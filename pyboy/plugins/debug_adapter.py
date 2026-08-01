#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""Exposes a Debug Adapter Protocol (DAP) server over stdio, so IDEs (e.g. VSCode, via the
PyBoyVSCode extension: https://github.com/Baekalfen/PyBoyVSCode) can set source and instruction
breakpoints, step through Game Boy assembly one instruction at a time, and inspect CPU
registers/flags/memory.

Enable with `pyboy game.gb --debug-adapter`, or `PyBoy("game.gb", debug_adapter=True)`.

The adapter speaks DAP (https://microsoft.github.io/debug-adapter-protocol/specification) over
stdin/stdout, so nothing else should write to stdout while this plugin is enabled -- this is why
`--debug-adapter` should always be combined with a non-interactive window backend
(e.g. `--window null` or `--window SDL2`, but not the interactive splash/help text PyBoy prints
on start-up when run standalone; the PyBoyVSCode extension takes care of this).

If the DAP `launch` request includes `sourceRoot`, the adapter also performs best-effort
assembly-source mapping for an RGBDS project. It reports `source` and `line` in `stackTrace` for
addresses it can prove, and omits them elsewhere so clients can fall back to disassembly.
`sourceMapFile` optionally selects the linked RGBDS `.map` file; otherwise a `.map` beside the ROM
is used when present. `bootromSourceRoot` does the same for boot-ROM assembly; when PyBoy uses its
built-in boot ROM, the bundled `extras/bootrom` source directory is discovered automatically.
"""

import base64
import os
import sys
import threading
import traceback

import pyboy
import pyboy.logging
from pyboy.plugins.base_plugin import PyBoyPlugin
from pyboy.plugins.dap_disassembler import disassemble_one
from pyboy.plugins.dap_io import DAPReader, DAPWriter
from pyboy.plugins.dap_source_map import (
    build_source_map,
    find_entry_files,
    parse_map_file,
    parse_sym_file,
)
from pyboy.utils import WindowEvent

logger = pyboy.logging.get_logger(__name__)

THREAD_ID = 1
REGISTERS_VAR_REF = 1
FLAGS_VAR_REF = 2


def _addr_ref(bank, addr):
    """Encodes a (bank, addr) pair as the string used for `instructionReference` /
    `memoryReference` values, the disassembled `address` field, and the format expected back for
    breakpoints.

    This *must* be a plain hex/decimal integer string, parseable by JavaScript's `BigInt()` --
    VSCode's Disassembly View does exactly that for every single instruction it receives
    (`BigInt(instruction.address)` in disassemblyView.ts), and silently *drops* (with only a
    `console.error`, invisible to the user) any row where that throws. An earlier "bank:addr"
    string format (e.g. "0:0100") is *not* valid BigInt syntax, so every row was being silently
    dropped, resulting in a completely blank Disassembly View despite otherwise-correct DAP
    responses. Encode (bank, addr) as a single integer instead: `bank` is offset by +1 so the
    boot ROM's sentinel bank (-1) still encodes to a non-negative value.
    """
    return hex(((bank + 1) << 16) | (addr & 0xFFFF))


def _parse_addr_ref(ref):
    value = int(ref, 16)
    return (value >> 16) - 1, value & 0xFFFF


class DebugAdapter(PyBoyPlugin):
    argv = [(
        "--debug-adapter",
        {
            "action": "store_true",
            "help": (
                "Expose a Debug Adapter Protocol (DAP) server over stdio, for IDE debugging "
                "(e.g. the PyBoyVSCode extension). Nothing else should write to stdout while "
                "this is enabled."
            ),
        },
    )]  # yapf: disable

    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        self.reader = DAPReader(sys.stdin.buffer)
        self.writer = DAPWriter(sys.stdout.buffer)
        self._seq = 0
        self._seq_lock = threading.Lock()
        self._breakpoint_refs = set()
        self._instruction_breakpoint_refs = set()
        self._source_breakpoint_refs = {}
        self._stop_on_entry = False

        # Best-effort address -> (source file, line number) map, built at launch time from a
        # user-supplied `sourceRoot` (an RGBDS-style disassembly project, e.g. a "pokered"
        # checkout). Empty unless/until `_req_launch` successfully builds one; frames simply omit
        # `source`/fall back to a real `line` number when there's no entry for the current PC, in
        # which case VSCode falls back to its own Disassembly View automatically.
        self._source_map = {}

        # Coordinates pausing/resuming/stepping the emulator thread, using PyBoy's public
        # `hook_register` (permanent, address-based breakpoints -- fires *before* the triggering
        # instruction executes, PC unchanged) and `singlestep`/`register_singlestep_handler`
        # (instruction-level stepping -- fires *after* the just-executed instruction, PC already
        # advanced) APIs. `_on_break` blocks the firing callback (via `threading.Event`) until
        # the DAP client asks to continue, step, or pause.
        self._resume = threading.Event()
        self._pending_action = "continue"  # "continue" | "step"
        self._hooks = {}  # (bank, addr) -> True, for tracking currently registered breakpoints
        # (bank, addr) -> original opcode byte, captured *before* `hook_register` patches memory
        # with its special "trap" opcode (`0xDB`). Used to hide that trap from the disassembly
        # view, which otherwise reads live memory and shows a bogus "0xDB ..." instruction for
        # any address that currently has a breakpoint set.
        self._hook_original_bytes = {}
        self._stopped_lock = threading.Lock()
        self.is_stopped = False

        # PyBoy starts ticking frames as soon as the surrounding process's main loop begins
        # (e.g. `pyboy/__main__.py`'s `while pyboy.tick(): pass`), which can race ahead of the
        # DAP handshake (initialize/launch/setInstructionBreakpoints/configurationDone) since
        # that happens concurrently, over stdio. To avoid silently skipping past the ROM's very
        # first instruction before the client has had a chance to set breakpoints, freeze
        # execution immediately by queuing a `PAUSE` input: `PyBoy._tick` checks
        # `if not self.paused:` *before* ever calling into `mb.tick()`, so no instruction -- not
        # even the first one -- runs until we explicitly unpause once the handshake completes.
        # (`send_input` is used here, rather than setting `self.pyboy.paused` directly, because
        # that attribute is read-only from outside `PyBoy` itself, and calling the `_pause()`
        # helper directly would crash here: it's still mid-construction at this point, before
        # `PyBoy.__init__` has assigned `self._plugin_manager`, which `_pause()` needs. Queuing
        # the input instead defers the actual pausing to the first real `tick()` call, by which
        # point construction has fully finished -- while still guaranteed to happen before any
        # instruction executes.)
        #
        # This intentionally bypasses `register_singlestep_handler`, whose callback only fires
        # *after* a full instruction has already run (the underlying tick loop always executes
        # exactly one real instruction before it gets a chance to bail when single-stepping is
        # enabled) -- using it here would report the PC *after* the ROM's first instruction
        # instead of its true entry point.
        self._configured = threading.Event()
        self._entry_paused = True
        self.pyboy.send_input(WindowEvent.PAUSE)
        self.pyboy.register_singlestep_handler(self._on_break)

        self._protocol_thread = threading.Thread(target=self._run_protocol, name="pyboy-dap", daemon=True)
        self._protocol_thread.start()

    def enabled(self):
        return self.pyboy_argv.get("debug_adapter")

    def stop(self):
        self._configured.set()  # Unblock the emulator thread, in case configurationDone never arrived
        self._resume.set()  # Unblock the emulator thread, in case it's currently stopped
        self._leave_entry_pause()  # Unfreeze, in case we're still paused at the entry point
        self._send_event("terminated")

    # -- DAP message plumbing (runs on its own background thread) -----------------------------

    def _run_protocol(self):
        while True:
            try:
                message = self.reader.read_message()
            except EOFError:
                break
            if message is None:
                break
            if not message:
                continue
            try:
                self._dispatch(message)
            except Exception as exc:
                logger.error(f"Error handling DAP message: {message}\n{traceback.format_exc()}")
                if message.get("type") == "request":
                    self._send_response(message, success=False, message=str(exc))

    def _next_seq(self):
        with self._seq_lock:
            self._seq += 1
            return self._seq

    def _send_response(self, request, success=True, body=None, message=None):
        self.writer.write_message(
            {
                "type": "response",
                "seq": self._next_seq(),
                "request_seq": request["seq"],
                "command": request["command"],
                "success": success,
                "body": body or {},
                **({"message": message} if message else {}),
            }
        )

    def _send_event(self, event, body=None):
        self.writer.write_message(
            {
                "type": "event",
                "seq": self._next_seq(),
                "event": event,
                "body": body or {},
            }
        )

    def _dispatch(self, message):
        if message.get("type") != "request":
            return
        command = message["command"]
        handler = getattr(self, f"_req_{command}", None)
        if handler is None:
            logger.warning(f"Unhandled DAP command: {command}")
            self._send_response(message, success=False, message=f"Unsupported command: {command}")
            return
        handler(message)

    # -- Breakpoint/stepping coordination (called from the emulator thread) -------------------

    def _on_break(self, reason="step"):
        with self._stopped_lock:
            self.is_stopped = True
        self._resume.clear()
        self._send_event("stopped", {"reason": reason, "threadId": THREAD_ID, "allThreadsStopped": True})
        self._resume.wait()
        with self._stopped_lock:
            self.is_stopped = False

        if self._pending_action == "step":
            self.pyboy.singlestep = True
        elif self.mb.breakpoint_waiting >= 0:
            # A breakpoint trap is removed before its callback runs. Keep the CPU's one-shot
            # single-step flag set while clearing the latch so the restored instruction executes;
            # PyBoy then reinjects the trap before resuming normal execution.
            self.mb.breakpoint_singlestep_latch = 0
        else:
            self.pyboy.singlestep = False

    def _leave_entry_pause(self):
        """Unfreezes execution after the initial handshake, transitioning out of the
        `__init__`-installed `paused` freeze (see there for why entry gating uses `paused`
        instead of a hook/breakpoint). No-op once already left. Must be called before the first
        `continue`/`next`/`stepIn`/`pause` request is allowed to take effect, and before the
        `configurationDone` response if the client didn't ask to stop on entry."""
        if not self._entry_paused:
            return
        self._entry_paused = False
        with self._stopped_lock:
            self.is_stopped = False
        self.pyboy.send_input(WindowEvent.UNPAUSE)

    def _hook_callback(self, _context):
        pc = self._registers()["PC"]
        bank = self.pyboy.bank(pc)
        reason = (
            "breakpoint"
            if any((bank, pc) in refs for refs in self._source_breakpoint_refs.values())
            else "instruction breakpoint"
        )
        self._on_break(reason)

    def _register_hook(self, bank, addr, callback):
        if (bank, addr) in self._hooks:
            return
        # Capture the real opcode *before* `hook_register` overwrites it in memory with its
        # special trap opcode (`0xDB`), so it can be substituted back in when disassembling.
        original_opcode = self.pyboy.memory[bank, addr]
        self.pyboy.hook_register(bank, addr, callback, None)
        self._hooks[(bank, addr)] = True
        self._hook_original_bytes[(bank, addr)] = original_opcode

    def _deregister_hook(self, bank, addr):
        if (bank, addr) not in self._hooks:
            return
        self.pyboy.hook_deregister(bank, addr)
        del self._hooks[(bank, addr)]
        del self._hook_original_bytes[(bank, addr)]

    def _add_breakpoint(self, bank, addr):
        self._register_hook(bank, addr, self._hook_callback)

    def _remove_breakpoint(self, bank, addr):
        self._deregister_hook(bank, addr)

    def _reconcile_breakpoints(self):
        wanted = set(self._instruction_breakpoint_refs)
        for refs in self._source_breakpoint_refs.values():
            wanted.update(refs)

        for bank, addr in self._breakpoint_refs - wanted:
            self._remove_breakpoint(bank, addr)
        for bank, addr in wanted - self._breakpoint_refs:
            self._add_breakpoint(bank, addr)
        self._breakpoint_refs = wanted

    def _request_step_out(self):
        """Best-effort "step out of the current subroutine": peeks the return address off the
        stack (assuming we're currently inside a routine reached via `CALL`/`RST`) and runs
        until that address is reached, similar to a temporary breakpoint.

        This is a heuristic: if the stack doesn't currently hold a real return address (e.g. we
        aren't inside a call), this will behave unpredictably. There's no reliable, general way
        to detect this on the SM83, so this matches what most Game Boy-focused debuggers do.
        """
        sp = self.pyboy.register_file.SP
        lo = self.pyboy.memory[sp & 0xFFFF]
        hi = self.pyboy.memory[(sp + 1) & 0xFFFF]
        return_addr = (hi << 8) | lo
        bank = self.pyboy.bank(return_addr)

        def _one_shot(_context):
            self._remove_breakpoint(bank, return_addr)
            self._on_break("step")

        self._register_hook(bank, return_addr, _one_shot)

        self._pending_action = "continue"
        if self._entry_paused:
            self._leave_entry_pause()
        else:
            self._resume.set()

    # -- Registers/memory/disassembly helpers --------------------------------------------------

    def _registers(self):
        rf = self.pyboy.register_file
        h = (rf.HL >> 8) & 0xFF
        l = rf.HL & 0xFF
        return {
            "A": rf.A, "F": rf.F, "B": rf.B, "C": rf.C, "D": rf.D, "E": rf.E, "H": h, "L": l,
            "AF": (rf.A << 8) | rf.F, "BC": (rf.B << 8) | rf.C, "DE": (rf.D << 8) | rf.E, "HL": rf.HL,
            "SP": rf.SP, "PC": rf.PC,
        }  # yapf: disable

    def _flags(self):
        f = self.pyboy.register_file.F
        return {"Z": bool(f & 0x80), "N": bool(f & 0x40), "H": bool(f & 0x20), "C": bool(f & 0x10)}

    def _set_register(self, name, value):
        rf = self.pyboy.register_file
        if name == "H":
            rf.HL = (value << 8) | (rf.HL & 0xFF)
        elif name == "L":
            rf.HL = (rf.HL & 0xFF00) | value
        else:
            setattr(rf, name, value)

    def _read_byte(self, addr):
        return self.pyboy.memory[addr & 0xFFFF]

    def _disasm_read_byte(self, addr):
        """Like `_read_byte`, but substitutes back the real opcode for any address that
        currently has an active breakpoint hook: `hook_register` installs breakpoints by
        overwriting the byte in memory with a special trap opcode (`0xDB`), so disassembling
        straight from live memory would otherwise show a bogus "0xDB ..." instruction at every
        breakpoint address for as long as it's set."""
        addr &= 0xFFFF
        bank = self.pyboy.bank(addr)
        original = self._hook_original_bytes.get((bank, addr))
        if original is not None:
            return original
        return self._read_byte(addr)

    def _symbol_for(self, bank, addr):
        """Returns the closest known symbol label at (bank, addr), or None."""
        labels = self.pyboy.rom_symbols.get(bank, {}).get(addr)
        return labels[0] if labels else None

    def _build_source_map(self, source_root, source_map_file):
        """Best-effort: if the client points `sourceRoot` at an RGBDS-style disassembly project
        checkout (e.g. a "pokered" checkout) matching the running ROM, build an address -> (file,
        line) map so `_req_stackTrace` can report real source locations instead of only raw
        disassembly. A missing source directory is treated as an empty map; source projects that
        contain unsupported constructs simply produce gaps and fall back to the Disassembly View."""
        self._source_map = {}
        if not source_root:
            return

        source_root = os.path.abspath(os.path.expanduser(os.fspath(source_root)))
        if not os.path.isdir(source_root):
            logger.warning(f"Source root does not exist or is not a directory: {source_root}")
            return

        if source_map_file:
            source_map_file = os.path.abspath(os.path.expanduser(os.fspath(source_map_file)))
        else:
            # Auto-discover an RGBDS linker `.map` file next to the ROM, the same way PyBoy
            # itself already auto-discovers `.sym` files (needed for ROMX section addresses,
            # which the source only gets to pick after linking).
            gamerom = getattr(self.pyboy, "gamerom", None)
            if gamerom:
                no_ext, ext = os.path.splitext(gamerom)
                for candidate in (no_ext + ".map", no_ext + ext + ".map"):
                    if os.path.isfile(candidate):
                        source_map_file = candidate
                        break

        sections = parse_map_file(source_map_file) if source_map_file else {}
        entries = find_entry_files(source_root)
        self._source_map = build_source_map(
            source_root,
            entries,
            self.pyboy.rom_symbols_inverse,
            sections,
            self.pyboy.memory,
            disassemble_one,
        )
        logger.debug(f"Built source map from {source_root!r}: {len(self._source_map)} addresses mapped")

    def _build_bootrom_source_map(self, source_root):
        """Builds a source map for the active boot ROM. If no explicit root is supplied and
        PyBoy is using its built-in boot ROM, use the matching source tree from this checkout."""
        if source_root:
            source_root = os.path.abspath(os.path.expanduser(os.fspath(source_root)))
        elif getattr(self.pyboy, "bootrom_file", None) is None:
            source_root = os.path.abspath(
                os.path.join(os.path.dirname(os.path.realpath(pyboy.__file__)), "..", "extras", "bootrom")
            )
        else:
            return

        if not os.path.isdir(source_root):
            logger.warning(f"Boot-ROM source root does not exist or is not a directory: {source_root}")
            return

        cgb_flag = self.pyboy.memory[0x143]
        variant = "cgb" if cgb_flag & 0x80 else "dmg"
        preferred_entry = f"bootrom_{variant}.asm"
        entries = (
            [preferred_entry]
            if os.path.isfile(os.path.join(source_root, preferred_entry))
            else find_entry_files(source_root)
        )
        if not entries:
            logger.warning(f"No boot-ROM assembly entry file found under: {source_root}")
            return

        symbols = {}
        symbol_candidates = [f"{os.path.splitext(entry)[0]}.sym" for entry in entries]
        symbol_candidates.append(f"bootrom_{variant}.sym")
        for candidate in symbol_candidates:
            symbol_path = os.path.join(source_root, candidate)
            if os.path.isfile(symbol_path):
                symbols = parse_sym_file(symbol_path, bank_override=-1)
                break

        bootrom_map = build_source_map(
            source_root,
            entries,
            symbols,
            {},
            self.pyboy.memory,
            disassemble_one,
        )
        bootrom_map = {(-1, addr): entry for (_bank, addr), entry in bootrom_map.items()}
        self._source_map.update(bootrom_map)
        logger.debug(f"Built boot-ROM source map from {source_root!r}: {len(bootrom_map)} addresses mapped")

    def _source_path_key(self, path):
        return os.path.normcase(os.path.normpath(os.path.abspath(os.path.expanduser(path))))

    def _source_breakpoint_locations(self, path, requested_line):
        """Returns `(line, addresses)` for the first executable source line at or after
        `requested_line`, or None when the source map has no matching location."""
        path_key = self._source_path_key(path)
        lines = {}
        for (bank, addr), (mapped_path, mapped_line) in self._source_map.items():
            if self._source_path_key(mapped_path) == path_key and mapped_line >= requested_line:
                lines.setdefault(mapped_line, set()).add((bank, addr))
        if not lines:
            return None
        line = min(lines)
        return line, sorted(lines[line])

    def _annotate_target(self, text, target):
        """If `target` is the absolute address referenced by a `CALL`/`JP`/`JR`/`LD`/`LDH`-style
        operand (as returned by `disassemble_one`) and it has a known symbol label, replaces the
        raw hex operand in `text` with that label, e.g. `"CALL $0150"` becomes `"CALL Init"`.
        Returns `text` unchanged if `target` is `None` or has no known symbol."""
        if target is None:
            return text
        symbol = self._symbol_for(self.pyboy.bank(target), target)
        if not symbol:
            return text
        return text.replace("${:04X}".format(target), symbol)

    def _disassemble(self, addr, count):
        result = []
        cur = addr & 0xFFFF
        for _ in range(count):
            length, text, target = disassemble_one(self._disasm_read_byte, cur)
            text = self._annotate_target(text, target)
            raw = bytes(self._disasm_read_byte((cur + i) & 0xFFFF) for i in range(length))
            result.append({"address": cur, "length": length, "text": text, "bytes": raw.hex()})
            cur = (cur + length) & 0xFFFF
        return result

    def _disassemble_backwards(self, addr, count):
        """Best-effort disassembly of `count` instructions ending *before* `addr`. See
        `pyboy_dap.session.PyBoySession.disassemble_backwards` (predecessor implementation) for
        the reasoning behind this heuristic."""
        max_len = 3
        for start in range(max(0, addr - count * max_len), addr):
            cur = start
            instructions = []
            while cur < addr:
                length, text, target = disassemble_one(self._disasm_read_byte, cur)
                text = self._annotate_target(text, target)
                instructions.append((cur, length, text))
                cur += length
            if cur == addr:
                trimmed = instructions[-count:]
                return [
                    {
                        "address": a,
                        "length": length,
                        "text": text,
                        "bytes": bytes(self._disasm_read_byte((a + i) & 0xFFFF) for i in range(length)).hex(),
                    }
                    for (a, length, text) in trimmed
                ]
        return []

    # -- Requests -------------------------------------------------------------------------------

    def _req_initialize(self, request):
        self._send_response(
            request,
            body={
                "supportsConfigurationDoneRequest": True,
                "supportsDisassembleRequest": True,
                "supportsSteppingGranularity": True,
                "supportsInstructionBreakpoints": True,
                "supportsReadMemoryRequest": True,
                "supportsWriteMemoryRequest": True,
                "supportsTerminateRequest": True,
                "supportsSingleThreadExecutionRequests": False,
                "supportsValueFormattingOptions": True,
            },
        )
        self._send_event("initialized")

    def _req_launch(self, request):
        # Unlike a typical DAP adapter, the ROM is already loaded -- PyBoy started this plugin
        # from the command line (or from Python), so there's nothing left to configure here
        # besides `stopOnEntry` and (optionally) `sourceRoot`.
        args = request.get("arguments", {})
        self._stop_on_entry = bool(args.get("stopOnEntry", False))
        self._build_source_map(args.get("sourceRoot"), args.get("sourceMapFile"))
        self._build_bootrom_source_map(args.get("bootromSourceRoot"))
        self._send_response(request)

    _req_attach = _req_launch

    def _req_configurationDone(self, request):
        self._configured.set()
        self._send_response(request)
        if self._entry_paused:
            if self._stop_on_entry:
                # Still frozen at the ROM's true entry point (see `__init__`/`_leave_entry_pause`)
                # -- report it now that the handshake is done, and stay paused until the client
                # asks to continue/step.
                with self._stopped_lock:
                    self.is_stopped = True
                self._send_event("stopped", {"reason": "entry", "threadId": THREAD_ID, "allThreadsStopped": True})
            else:
                # The client doesn't care about stopping at the entry point; resume immediately.
                # Single-stepping stays off until/unless the client later requests a step; any
                # breakpoints set in the meantime (via `hook_register`) remain active regardless.
                self._leave_entry_pause()

    def _req_setInstructionBreakpoints(self, request):
        args = request.get("arguments", {})
        wanted = args.get("breakpoints", [])

        wanted_refs = set()
        results = []
        for bp in wanted:
            ref = bp["instructionReference"]
            offset = bp.get("offset", 0)
            try:
                bank, addr = _parse_addr_ref(ref)
                addr = (addr + offset) & 0xFFFF
            except ValueError:
                results.append({"verified": False, "message": "Invalid instructionReference"})
                continue
            wanted_refs.add((bank, addr))
            results.append({"verified": True, "instructionReference": _addr_ref(bank, addr)})

        self._instruction_breakpoint_refs = wanted_refs
        self._reconcile_breakpoints()

        self._send_response(request, body={"breakpoints": results})

    def _req_setBreakpoints(self, request):
        args = request.get("arguments", {})
        source = args.get("source") or {}
        source_path = source.get("path")
        requested = args.get("breakpoints")
        if requested is None:
            requested = [{"line": line} for line in args.get("lines", [])]

        if not isinstance(source_path, str):
            results = [{"verified": False, "message": "Source breakpoint is missing source.path"} for _ in requested]
            self._send_response(request, body={"breakpoints": results})
            return

        source_key = self._source_path_key(source_path)
        source_descriptor = {"name": os.path.basename(source_path), "path": source_path}
        source_refs = set()
        results = []
        for bp in requested:
            line = bp.get("line")
            if not isinstance(line, int) or line < 1:
                results.append({"verified": False, "line": line, "message": "Invalid source line"})
                continue
            if bp.get("condition") or bp.get("hitCondition") or bp.get("logMessage"):
                results.append(
                    {
                        "verified": False,
                        "source": source_descriptor,
                        "line": line,
                        "message": "Conditional, hit-count, and log breakpoints are not supported",
                    }
                )
                continue

            locations = self._source_breakpoint_locations(source_path, line)
            if locations is None:
                results.append(
                    {
                        "verified": False,
                        "source": source_descriptor,
                        "line": line,
                        "message": "No executable instruction is mapped to this source line",
                    }
                )
                continue

            resolved_line, addresses = locations
            source_refs.update(addresses)
            result = {
                "verified": True,
                "source": source_descriptor,
                "line": resolved_line,
                "instructionReference": _addr_ref(*addresses[0]),
            }
            if bp.get("column") is not None:
                result["column"] = bp["column"]
            results.append(result)

        if source_refs:
            self._source_breakpoint_refs[source_key] = source_refs
        else:
            self._source_breakpoint_refs.pop(source_key, None)
        self._reconcile_breakpoints()
        self._send_response(request, body={"breakpoints": results})

    def _req_threads(self, request):
        self._send_response(request, body={"threads": [{"id": THREAD_ID, "name": "CPU"}]})

    def _req_stackTrace(self, request):
        pc = self._registers()["PC"]
        bank = self.pyboy.bank(pc)
        symbol = self._symbol_for(bank, pc)
        name = symbol if symbol else f"{bank}:{pc:04x}"
        frame = {
            "id": 1,
            "name": name,
            "line": 0,
            "column": 0,
            "instructionPointerReference": _addr_ref(bank, pc),
        }
        source_entry = self._source_map.get((bank, pc))
        if source_entry:
            path, line = source_entry
            # Presence of `source` makes VSCode show/highlight this real source file instead of
            # the Disassembly View; omitting it (whenever there's no mapping for this address)
            # makes VSCode fall back to the Disassembly View automatically.
            frame["source"] = {"name": os.path.basename(path), "path": path}
            frame["line"] = line
        self._send_response(request, body={"stackFrames": [frame], "totalFrames": 1})

    def _req_scopes(self, request):
        self._send_response(
            request,
            body={
                "scopes": [
                    {"name": "Registers", "variablesReference": REGISTERS_VAR_REF, "expensive": False},
                    {"name": "Flags", "variablesReference": FLAGS_VAR_REF, "expensive": False},
                ]
            },
        )

    def _req_variables(self, request):
        ref = request["arguments"]["variablesReference"]
        variables = []
        if ref == REGISTERS_VAR_REF:
            regs = self._registers()
            for name in ["A", "F", "B", "C", "D", "E", "H", "L", "AF", "BC", "DE", "HL", "SP", "PC"]:
                width = 4 if name in ("AF", "BC", "DE", "HL", "SP", "PC") else 2
                variables.append(
                    {
                        "name": name,
                        "value": f"0x{regs[name]:0{width}x}",
                        "variablesReference": 0,
                        "evaluateName": name,
                    }
                )
        elif ref == FLAGS_VAR_REF:
            for name, value in self._flags().items():
                variables.append({"name": name, "value": str(value), "variablesReference": 0})
        self._send_response(request, body={"variables": variables})

    def _req_setVariable(self, request):
        args = request["arguments"]
        if args["variablesReference"] == REGISTERS_VAR_REF:
            name = args["name"]
            value = int(args["value"], 0)
            self._set_register(name, value)
            self._send_response(request, body={"value": args["value"]})
        else:
            self._send_response(request, success=False, message="Variable is read-only")

    def _req_continue(self, request):
        self._pending_action = "continue"
        if self._entry_paused:
            self.pyboy.singlestep = False
            self._leave_entry_pause()
        else:
            self._resume.set()
        self._send_response(request, body={"allThreadsContinued": True})

    def _req_next(self, request):
        self._pending_action = "step"
        if self._entry_paused:
            self.pyboy.singlestep = True
            self._leave_entry_pause()
        else:
            self._resume.set()
        self._send_response(request)

    _req_stepIn = _req_next

    def _req_stepOut(self, request):
        self._request_step_out()
        self._send_response(request)

    def _req_pause(self, request):
        with self._stopped_lock:
            stopped = self.is_stopped
        if not stopped:
            self.pyboy.singlestep = True
        self._send_response(request)

    def _req_disassemble(self, request):
        args = request["arguments"]
        _, addr = _parse_addr_ref(args["memoryReference"])
        addr = (addr + args.get("offset", 0)) & 0xFFFF
        instruction_offset = args.get("instructionOffset", 0)
        count = args["instructionCount"]

        if instruction_offset < 0:
            before = self._disassemble_backwards(addr, -instruction_offset)
            # `before` can (and near the start of a bank -- e.g. address 0 during early boot --
            # routinely does) contain *fewer* than `-instruction_offset` entries: disassembling
            # backwards is inherently ambiguous/best-effort, and there may simply not be enough
            # addressable bytes before `addr` to find a valid decode. The DAP spec requires the
            # response to contain *exactly* `instructionCount` entries: VSCode's Disassembly View
            # locates "the instruction at offset 0" (i.e. the current PC, for the initial
            # highlight/scroll) purely by *position* in the returned array
            # (`instructionOffset + i == 0`), not by matching addresses -- so returning a
            # shorter-than-requested `before` shifts every later row left by the shortfall,
            # making VSCode misidentify some other (arbitrary, further-into-memory) instruction
            # as "the current one". This is exactly what caused the Disassembly View to highlight
            # the wrong, stuck address during early boot. Pad the front with placeholder
            # "invalid instruction" rows (address `-1`, which VSCode explicitly recognizes and
            # ignores) to preserve positional alignment.
            padding = -instruction_offset - len(before)
            remaining = count + instruction_offset  # count - (-instruction_offset)
            after = self._disassemble(addr, remaining) if remaining > 0 else []
            instructions = [None] * padding + before + after
        else:
            # Skip `instruction_offset` instructions forward first, then disassemble `count`.
            skipped = self._disassemble(addr, instruction_offset + count)
            instructions = skipped[instruction_offset:]

        body_instructions = []
        for instr in instructions:
            if instr is None:
                # Placeholder for an instruction that couldn't be decoded (see above). `-1` is
                # recognized by VSCode's Disassembly View as an explicitly invalid address and
                # silently skipped, while still preserving positional alignment for later rows.
                body_instructions.append({"address": "-1", "instructionBytes": "", "instruction": "??"})
                continue
            # Compute the bank *per instruction*, not once for the whole window: a wide window
            # (VSCode routinely requests hundreds of instructions either side of the current PC)
            # can span a bank boundary -- most notably the boot ROM -> cartridge ROM transition at
            # 0x100, which happens right in the middle of early-boot disassembly. Reusing a single
            # bank for the whole window mislabels every row past that boundary, producing wrong
            # `address` references that don't match the live PC's `instructionPointerReference`
            # (from `_req_stackTrace`), so the current-instruction highlight in VSCode either
            # doesn't move or lands on the wrong row.
            bank = self.pyboy.bank(instr["address"])
            symbol = self._symbol_for(bank, instr["address"])
            text = instr["text"]
            if symbol:
                # VSCode's Disassembly View doesn't currently render the `symbol` field (each row
                # is always exactly one instruction), so the only reliable way to show "this is
                # the start of a routine" is to append it to the instruction text itself.
                text = f"{text} [{symbol}]"
            body_instructions.append(
                {
                    "address": _addr_ref(bank, instr["address"]),
                    "instructionBytes": instr["bytes"],
                    "instruction": text,
                    **({"symbol": symbol} if symbol else {}),
                }
            )
        self._send_response(request, body={"instructions": body_instructions})

    def _req_readMemory(self, request):
        args = request["arguments"]
        _, addr = _parse_addr_ref(args["memoryReference"])
        addr = (addr + args.get("offset", 0)) & 0xFFFF
        count = args["count"]
        data = bytes(self._read_byte((addr + i) & 0xFFFF) for i in range(count))
        self._send_response(
            request,
            body={
                "address": _addr_ref(self.pyboy.bank(addr), addr),
                "data": base64.b64encode(data).decode("ascii"),
            },
        )

    def _req_writeMemory(self, request):
        args = request["arguments"]
        _, addr = _parse_addr_ref(args["memoryReference"])
        addr = (addr + args.get("offset", 0)) & 0xFFFF
        data = base64.b64decode(args["data"])
        for i, b in enumerate(data):
            self.pyboy.memory[(addr + i) & 0xFFFF] = b
        self._send_response(request, body={"bytesWritten": len(data)})

    def _req_disconnect(self, request):
        self._configured.set()  # Unblock the emulator thread, in case configurationDone never arrived
        self._resume.set()  # Unblock the emulator thread, in case it's currently stopped
        self.pyboy._quit()
        self._send_response(request)

    def _req_terminate(self, request):
        self._configured.set()
        self._resume.set()
        self.pyboy._quit()
        self._send_response(request)
        self._send_event("terminated")
