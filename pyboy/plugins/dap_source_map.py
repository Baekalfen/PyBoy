#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""Best-effort mapping between ROM addresses and lines in an RGBDS-style assembly disassembly
project (e.g. https://github.com/pret/pokered), so the Debug Adapter can report a source
location for the current PC and VSCode can step *inline in the original source* -- falling back
to the Disassembly View for any address this can't confidently resolve (e.g. inside data tables,
macro invocations, or conditionally-assembled code for a different game version).

This deliberately does *not* implement a real RGBDS preprocessor/assembler. It's a lightweight,
line-oriented walker that:

  - Follows `INCLUDE "file"` the same way `rgbasm` would, so files are visited in the same
    (recursive) order they'd actually be assembled in.
  - Tracks `SECTION "name", ...` boundaries, and anchors the current address using the actual
    linked (bank, address) for that section name, read from the linker's `.map` file (RGBDS
    doesn't put ROMX section addresses in the source -- those are only decided at link time).
  - Anchors (or re-anchors) the current address whenever a label is defined, by looking it up in
    the `.sym` file's symbol table (already loaded by PyBoy as `rom_symbols_inverse`).
  - Advances the current address across plain instruction lines using PyBoy's own disassembler
    (to get the real instruction length) and across simple `db`/`dw`/`dl`/`ds` data lines (by
    counting operands), double-checking instruction lines by mnemonic so a wrong guess can't
    quietly corrupt every subsequent mapping in the file.
  - Understands `IF`/`ELIF`/`ELSE`/`ENDC` well enough to only walk the taken branch, using a
    caller-supplied set of defined symbols (e.g. `{"_RED"}`), and skips `MACRO`/`ENDM` bodies
    entirely (those only become real code at their *call* site, which this doesn't attempt to
    resolve).

Whenever the current address can't be established or confidently advanced (an unrecognized
directive, a macro call, an unresolvable condition, ...), mapping simply stops for that stretch
of the file until the next label or `SECTION` re-anchors it -- so gaps degrade gracefully instead
of producing wrong line numbers.
"""

import os
import re

import pyboy

logger = pyboy.logging.get_logger(__name__)

MNEMONICS = {
    "nop", "ld", "ldh", "inc", "dec", "add", "adc", "sub", "sbc", "and", "or", "xor", "cp",
    "jp", "jr", "call", "ret", "reti", "rst", "push", "pop", "halt", "stop", "di", "ei",
    "rlca", "rla", "rrca", "rra", "daa", "cpl", "scf", "ccf",
    "rlc", "rl", "rrc", "rr", "sla", "sra", "swap", "srl", "bit", "set", "res",
}  # yapf: disable

_INCLUDE_RE = re.compile(r'^INCLUDE\s+"([^"]+)"', re.IGNORECASE)
_SECTION_RE = re.compile(r'^SECTION\s+"((?:[^"\\]|\\.)*)"\s*,\s*(.*)$', re.IGNORECASE)
_SECTION_ROM0_ADDR_RE = re.compile(r"ROM0\s*\[\s*\$?([0-9A-Fa-f]+)\s*\]", re.IGNORECASE)
_SECTION_ROMX_ADDR_RE = re.compile(
    r"ROMX\s*\[\s*\$?([0-9A-Fa-f]+)\s*\](?:\s*,\s*BANK\s*\[\s*\$?([0-9A-Fa-f]+)\s*\])?", re.IGNORECASE
)
_IF_RE = re.compile(r"^IF\s+(.+)$", re.IGNORECASE)
_ELIF_RE = re.compile(r"^ELIF\s+(.+)$", re.IGNORECASE)
_ELSE_RE = re.compile(r"^ELSE\b", re.IGNORECASE)
_ENDC_RE = re.compile(r"^ENDC\b", re.IGNORECASE)
_MACRO_DEF_RE = re.compile(r"^MACRO\b", re.IGNORECASE)
_ENDM_RE = re.compile(r"^ENDM\b", re.IGNORECASE)
_DATA_RE = re.compile(r"^(db|dw|dl|ds)\b(.*)$", re.IGNORECASE)
_LABEL_RE = re.compile(r"^(?:([A-Za-z_][A-Za-z0-9_#@]*)(::?)|(\.[A-Za-z_][A-Za-z0-9_#@]*)(::?)?)\s*(.*)$")
_DEF_RE = re.compile(r"(?:!\s*)?DEF\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)", re.IGNORECASE)
_SYM_LABEL_RE = re.compile(r"^([0-9a-fA-F]+):([0-9a-fA-F]+)\s+(\S+)$")
_MAP_BANK_RE = re.compile(r"^(ROM0|ROMX) bank #(\d+):")
_MAP_SECTION_RE = re.compile(r'^\tSECTION:\s*\$([0-9a-fA-F]+)(?:-\$[0-9a-fA-F]+)?\s.*\["(.*)"\]\s*$')

_DATA_LENGTHS = {"db": 1, "dw": 2, "dl": 4}


def parse_map_file(path):
    """Parses an RGBDS linker `.map` file into `{section_name: (bank, start_addr)}`, used to
    resolve `SECTION "name", ROMX` directives to an actual linked address (RGBDS only assigns
    ROMX sections a bank/address at link time; it isn't in the source)."""
    sections = {}
    bank = None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                m = _MAP_BANK_RE.match(line)
                if m:
                    bank = int(m.group(2)) if m.group(1) == "ROMX" else 0
                    continue
                m = _MAP_SECTION_RE.match(line)
                if m and bank is not None:
                    sections[m.group(2)] = (bank, int(m.group(1), 16))
    except OSError:
        logger.warning(f"Could not read map file: {path}")
    return sections


def parse_sym_file(path, bank_override=None):
    """Parses RGBDS `bank:address label` symbol lines into `{label: (bank, address)}`.

    Boot-ROM symbol files use bank zero even though PyBoy addresses the active boot ROM as bank
    `-1`; callers can pass `bank_override=-1` to normalize those symbols to the debugger's
    address space.
    """
    symbols = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for raw_line in f:
                line = raw_line.strip()
                match = _SYM_LABEL_RE.match(line)
                if match:
                    bank = bank_override if bank_override is not None else int(match.group(1), 16)
                    symbols[match.group(3)] = (bank, int(match.group(2), 16))
    except OSError:
        logger.warning(f"Could not read symbol file: {path}")
    return symbols


def _strip_comment(line):
    """Removes a trailing `; comment`, respecting (naively) that a `;` inside a quoted string
    isn't a comment."""
    in_string = False
    i = 0
    while i < len(line):
        c = line[i]
        if c == '"' and (i == 0 or line[i - 1] != "\\"):
            in_string = not in_string
        elif c == ";" and not in_string:
            return line[:i]
        i += 1
    return line


def _split_top_level_commas(text):
    """Splits `text` on commas that aren't nested inside quotes/parens/brackets."""
    parts = []
    depth = 0
    in_string = False
    current = []
    for i, c in enumerate(text):
        if c == '"' and (i == 0 or text[i - 1] != "\\"):
            in_string = not in_string
        elif not in_string and c in "([":
            depth += 1
        elif not in_string and c in ")]":
            depth -= 1
        elif c == "," and depth == 0 and not in_string:
            parts.append("".join(current))
            current = []
            continue
        current.append(c)
    tail = "".join(current).strip()
    if tail or parts:
        parts.append(tail)
    return [p.strip() for p in parts if p.strip()]


def _data_length(directive, operands):
    """Best-effort byte length of a `db`/`dw`/`dl`/`ds` line. Returns `None` if it can't be
    confidently computed (e.g. an expression this doesn't understand), in which case the caller
    should stop advancing rather than guess."""
    directive = directive.lower()
    operands = operands.strip()
    if directive == "ds":
        # `ds N` or `ds N, fill` -- only the count matters for byte length.
        count_expr = _split_top_level_commas(operands)
        if not count_expr:
            return None
        try:
            return _parse_int(count_expr[0])
        except ValueError:
            return None

    items = _split_top_level_commas(operands)
    if not items:
        return None
    total = 0
    per_item = _DATA_LENGTHS[directive]
    for item in items:
        if item.startswith('"') and item.endswith('"') and len(item) >= 2:
            # A string literal in a `db` list contributes one byte per character (an
            # approximation -- custom charmaps could in principle map a character to more or
            # fewer than one byte, but this holds for the overwhelming majority of cases).
            total += len(item) - 2
        else:
            total += per_item
    return total


def _parse_int(expr):
    expr = expr.strip()
    if expr.startswith("$"):
        return int(expr[1:], 16)
    if expr.startswith("%"):
        return int(expr[1:], 2)
    return int(expr, 0)


def _eval_condition(expr, defines):
    """Evaluates a (small) subset of RGBDS `IF`/`ELIF` conditions: `DEF(SYM)`, `!DEF(SYM)`, and
    `&&`/`||` combinations of those. Anything else is unresolvable, and treated as false --
    conservatively skipping the branch rather than risking mis-mapping it."""
    expr = expr.strip()
    if not expr:
        return False

    for op, combine in ((r"\|\|", any), ("&&", all)):
        parts = re.split(op, expr)
        if len(parts) > 1:
            results = [_eval_condition(p, defines) for p in parts]
            if all(r is not None for r in results):
                return combine(results)
            return None

    m = re.match(r"^!?\s*DEF\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)$", expr, re.IGNORECASE)
    if m:
        defined = m.group(1) in defines
        return not defined if expr.strip().startswith("!") else defined
    return None


class _FileWalker:
    """Walks one already-open list of source lines, following `INCLUDE`s and tracking the
    current address, defers most bookkeeping (sections/labels/conditions/macros) covered above.
    Shared across the whole recursive include tree so `current_addr` persists across file
    boundaries within the same section, matching how `rgbasm` actually assembles it."""

    def __init__(self, root_dir, sections, symbols_inverse, read_byte, disassemble_one, defines, mapping, visited):
        self.root_dir = root_dir
        self.sections = sections
        self.symbols_inverse = symbols_inverse
        self.read_byte = read_byte
        self.disassemble_one = disassemble_one
        self.defines = defines
        self.mapping = mapping
        self.visited = visited
        self.current_bank = None
        self.current_addr = None
        self.current_label = None  # Most recent global (non-local) label, for scoping `.sub` labels.

    def _lose_sync(self):
        self.current_bank = None
        self.current_addr = None

    def _advance(self, n):
        if self.current_addr is None:
            return
        self.current_addr = (self.current_addr + n) & 0xFFFF

    def _record(self, path, lineno):
        if self.current_bank is None or self.current_addr is None:
            return
        self.mapping.setdefault((self.current_bank, self.current_addr), (path, lineno))

    def walk_file(self, rel_path):
        abs_path = os.path.normpath(os.path.join(self.root_dir, rel_path))
        if abs_path in self.visited:
            return  # Already processed (or currently being processed -- avoid infinite recursion).
        self.visited.add(abs_path)
        try:
            with open(abs_path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError:
            logger.warning(f"Could not read included source file: {abs_path}")
            return

        # `IF`/`ELIF`/`ELSE`/`ENDC` nesting: each entry is True if this level's branch is
        # currently being taken (lines processed normally), False if skipped.
        cond_stack = []
        macro_depth = 0

        def taking():
            return all(cond_stack)

        for i, raw_line in enumerate(lines):
            lineno = i + 1
            line = _strip_comment(raw_line).strip()
            if not line:
                continue

            if macro_depth:
                if _MACRO_DEF_RE.match(line):
                    macro_depth += 1
                elif _ENDM_RE.match(line):
                    macro_depth -= 1
                continue

            m = _IF_RE.match(line)
            if m:
                cond_stack.append(bool(_eval_condition(m.group(1), self.defines)))
                continue
            m = _ELIF_RE.match(line)
            if m and cond_stack:
                # Only take this branch if every earlier branch at this level was skipped.
                already_taken = cond_stack[-1]
                cond_stack[-1] = (not already_taken) and bool(_eval_condition(m.group(1), self.defines))
                continue
            if _ELSE_RE.match(line) and cond_stack:
                cond_stack[-1] = not cond_stack[-1]
                continue
            if _ENDC_RE.match(line) and cond_stack:
                cond_stack.pop()
                continue
            if cond_stack and not taking():
                continue

            if _MACRO_DEF_RE.match(line):
                macro_depth = 1
                continue

            m = _INCLUDE_RE.match(line)
            if m:
                self.walk_file(m.group(1))
                continue

            m = _SECTION_RE.match(line)
            if m:
                name, attrs = m.groups()
                section = self.sections.get(name)
                if section is None:
                    # Not in the linker's `.map` file (or none was supplied) -- fall back to an
                    # explicit inline address, if the source specifies one directly, e.g.
                    # `SECTION "Header", ROM0[$100]` or `SECTION "X", ROMX[$4010], BANK[$05]`.
                    rom0 = _SECTION_ROM0_ADDR_RE.search(attrs)
                    romx = _SECTION_ROMX_ADDR_RE.search(attrs)
                    if rom0:
                        section = (0, int(rom0.group(1), 16))
                    elif romx and romx.group(2):
                        section = (int(romx.group(2), 16), int(romx.group(1), 16))
                if section is None:
                    logger.debug(f"No linked address found for SECTION {name!r}")
                    self._lose_sync()
                else:
                    self.current_bank, self.current_addr = section
                continue

            m = _LABEL_RE.match(line)
            if m:
                global_name, _global_colons, local_name, _local_colons, rest = m.groups()
                if local_name is not None:
                    qualified = f"{self.current_label}{local_name}" if self.current_label else None
                else:
                    self.current_label = global_name
                    qualified = global_name
                if qualified is not None:
                    resolved = self.symbols_inverse.get(qualified)
                    if resolved is not None:
                        self.current_bank, self.current_addr = resolved
                # Deliberately don't `_record` the label line itself: it shares its address with
                # whatever code/data follows it (labels are zero-width), and highlighting the
                # first real instruction/data line there (recorded below, on this same iteration
                # if `rest` is non-empty, or on a later one otherwise) is more useful when
                # stepping than highlighting the label declaration.
                if rest and not rest.strip().startswith(";"):
                    line = rest.strip()
                else:
                    continue

            m = _DATA_RE.match(line)
            if m:
                length = _data_length(m.group(1), m.group(2))
                if length is None:
                    self._lose_sync()
                else:
                    self._record(abs_path, lineno)
                    self._advance(length)
                continue

            first_token = re.split(r"[\s,]", line, maxsplit=1)[0].lower()
            if first_token in MNEMONICS and self.current_addr is not None:
                bank = self.current_bank

                def _bank_read_byte(addr, _bank=bank):
                    return self.read_byte(_bank, addr)

                try:
                    length, text, _target = self.disassemble_one(_bank_read_byte, self.current_addr)
                except Exception:
                    self._lose_sync()
                    continue
                decoded_mnemonic = text.split(" ", 1)[0].split(",", 1)[0].lower()
                if decoded_mnemonic != first_token:
                    # Our line-oriented walker lost sync with the real byte stream (e.g. it
                    # mis-evaluated a condition, or walked into a data blob it didn't recognize)
                    # -- stop trusting it until the next label/SECTION re-anchors.
                    self._lose_sync()
                    continue
                self._record(abs_path, lineno)
                self._advance(length)
                continue

            # Anything else recognized as a no-op for address-tracking purposes (doesn't consume
            # bytes and doesn't need special handling): EXPORT, ASSERT, charmap directives, etc.
            # Anything truly unrecognized (typically a macro invocation) can't be sized, so stop
            # trusting the current address until it's re-anchored.
            if first_token not in (
                "export",
                "assert",
                "purge",
                "printt",
                "println",
                "print",
                "shift",
                "charmap",
                "newcharmap",
                "setcharmap",
                "opt",
                "pushs",
                "pops",
                "pusho",
                "popo",
                "rsreset",
                "rsset",
                "union",
                "nextu",
                "endu",
                "rept",
                "endr",
                "fail",
                "warn",
            ):
                self._lose_sync()


def build_source_map(
    root_dir, entry_files, symbols_inverse, sections, memory, disassemble_one, defines=frozenset({"_RED"})
):
    """Builds `{(bank, addr): (abs_path, line)}` by walking `entry_files` (and everything they
    transitively `INCLUDE`) under `root_dir`. See the module docstring for the approach and its
    limitations."""
    mapping = {}
    visited = set()

    def read_byte(bank, addr):
        return memory[bank, addr & 0xFFFF]

    for entry in entry_files:
        walker = _FileWalker(root_dir, sections, symbols_inverse, read_byte, disassemble_one, defines, mapping, visited)
        walker.walk_file(entry)
    return mapping


def find_entry_files(root_dir):
    """Auto-detects the top-level source files to start walking from: every `.asm` file under
    `root_dir` that no *other* `.asm` file `INCLUDE`s (an `.asm` project's "driver" files, e.g.
    `main.asm`/`home.asm`/`audio.asm` in pokered) -- generically, without hardcoding any
    particular project's layout."""
    all_files = []
    for dirpath, _dirnames, filenames in os.walk(root_dir):
        for name in filenames:
            if name.lower().endswith((".asm", ".inc")):
                all_files.append(os.path.relpath(os.path.join(dirpath, name), root_dir))

    included = set()
    for rel_path in all_files:
        abs_path = os.path.join(root_dir, rel_path)
        try:
            with open(abs_path, encoding="utf-8", errors="replace") as f:
                for raw_line in f:
                    m = _INCLUDE_RE.match(_strip_comment(raw_line).strip())
                    if m:
                        # `INCLUDE` paths in RGBDS projects are relative to the project root
                        # (the assembler's working directory), not to the including file.
                        included.add(os.path.normpath(m.group(1)))
        except OSError:
            continue

    return [f for f in all_files if os.path.normpath(f) not in included and f.lower().endswith(".asm")]
