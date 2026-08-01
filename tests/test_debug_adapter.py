"""End-to-end test: spawns PyBoy's own CLI (`python -m pyboy ... --debug-adapter`) as a real
subprocess, speaks the Debug Adapter Protocol (DAP) over its stdio, and drives it through a full
launch -> breakpoint -> continue -> stop -> step -> registers session, against `default_rom.gb`.
"""

import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time

import pytest

import pyboy
import pyboy.plugins.debug_adapter

DEFAULT_ROM = os.path.join(os.path.dirname(pyboy.__file__), "default_rom.gb")
DEFAULT_ROM_SRC = os.path.join(os.path.dirname(pyboy.__file__), "..", "extras", "default_rom")


class DAPClient:
    """A tiny DAP client used purely for testing the debug_adapter plugin."""

    def __init__(self, proc):
        self.proc = proc
        self._seq = 0
        self._events = queue.Queue()
        self._responses = {}
        self._responses_lock = threading.Lock()
        self._responses_cond = threading.Condition(self._responses_lock)
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()

    def _read_loop(self):
        stream = self.proc.stdout
        while True:
            headers = {}
            while True:
                line = stream.readline()
                if not line:
                    return
                line = line.decode("utf-8").strip("\r\n")
                if line == "":
                    break
                key, _, value = line.partition(":")
                headers[key.strip().lower()] = value.strip()
            length = int(headers["content-length"])
            body = stream.read(length)
            message = json.loads(body.decode("utf-8"))
            if message["type"] == "event":
                self._events.put(message)
            elif message["type"] == "response":
                with self._responses_cond:
                    self._responses[message["request_seq"]] = message
                    self._responses_cond.notify_all()

    def send_request(self, command, arguments=None, timeout=10):
        self._seq += 1
        seq = self._seq
        message = {"seq": seq, "type": "request", "command": command}
        if arguments is not None:
            message["arguments"] = arguments
        body = json.dumps(message).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
        self.proc.stdin.write(header + body)
        self.proc.stdin.flush()

        with self._responses_cond:
            deadline = time.time() + timeout
            while seq not in self._responses:
                remaining = deadline - time.time()
                if remaining <= 0:
                    raise TimeoutError(f"No response to {command!r} after {timeout}s")
                self._responses_cond.wait(remaining)
            return self._responses.pop(seq)

    def wait_for_event(self, event_name, timeout=10):
        deadline = time.time() + timeout
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                raise TimeoutError(f"No {event_name!r} event after {timeout}s")
            message = self._events.get(timeout=remaining)
            if message["event"] == event_name:
                return message
            # Not the event we wanted; drop it (this test doesn't need it).


@pytest.fixture
def dap_client():
    proc = subprocess.Popen(
        [sys.executable, "-m", "pyboy", DEFAULT_ROM, "--window", "null", "--no-input", "--debug-adapter"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    client = DAPClient(proc)
    try:
        yield client
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            if stream is not None:
                stream.close()


def test_initialize(dap_client):
    resp = dap_client.send_request("initialize", {"adapterID": "pyboy"})
    assert resp["success"]
    assert resp["body"]["supportsDisassembleRequest"] is True
    dap_client.wait_for_event("initialized")


def test_launch_stop_on_entry_and_registers(dap_client):
    dap_client.send_request("initialize", {"adapterID": "pyboy"})
    dap_client.wait_for_event("initialized")

    resp = dap_client.send_request("launch", {"stopOnEntry": True})
    assert resp["success"], resp

    resp = dap_client.send_request("configurationDone")
    assert resp["success"], resp

    dap_client.wait_for_event("stopped")

    resp = dap_client.send_request("threads")
    assert resp["body"]["threads"][0]["name"] == "CPU"

    resp = dap_client.send_request("stackTrace", {"threadId": 1})
    frames = resp["body"]["stackFrames"]
    assert len(frames) == 1
    # The true reset vector (bank -1, addr 0) -- not after the boot ROM's first instruction has
    # already executed.
    assert frames[0]["instructionPointerReference"] == pyboy.plugins.debug_adapter._addr_ref(-1, 0)
    assert frames[0]["source"]["name"] == "bootrom_common.asm"
    assert frames[0]["source"]["path"].endswith(os.path.join("extras", "bootrom", "bootrom_common.asm"))
    assert frames[0]["line"] == 4

    resp = dap_client.send_request("scopes", {"frameId": 1})
    scope_refs = {s["name"]: s["variablesReference"] for s in resp["body"]["scopes"]}
    assert "Registers" in scope_refs
    assert "Flags" in scope_refs

    resp = dap_client.send_request("variables", {"variablesReference": scope_refs["Registers"]})
    reg_names = {v["name"] for v in resp["body"]["variables"]}
    assert reg_names == {"A", "F", "B", "C", "D", "E", "H", "L", "AF", "BC", "DE", "HL", "SP", "PC"}


def test_bootrom_source_root_override(dap_client, tmp_path):
    source = tmp_path / "bootrom.asm"
    source.write_text('SECTION "bootrom", ROM0[$0000]\nmain:\n    ld SP, $FFFE\n', encoding="utf-8")
    (tmp_path / "bootrom.sym").write_text("00:0000 main\n", encoding="utf-8")

    dap_client.send_request("initialize", {"adapterID": "pyboy"})
    dap_client.wait_for_event("initialized")
    resp = dap_client.send_request("launch", {"stopOnEntry": True, "bootromSourceRoot": str(tmp_path)})
    assert resp["success"], resp
    dap_client.send_request("configurationDone")
    dap_client.wait_for_event("stopped")

    frame = dap_client.send_request("stackTrace", {"threadId": 1})["body"]["stackFrames"][0]
    assert frame["source"]["name"] == "bootrom.asm"
    assert frame["source"]["path"] == str(source)
    assert frame["line"] == 3


def test_source_breakpoint_and_continue(dap_client):
    source_path = os.path.join(os.path.abspath(DEFAULT_ROM_SRC), "default_rom.asm")
    entrypoint_ref = pyboy.plugins.debug_adapter._addr_ref(0, 0x0150)

    dap_client.send_request("initialize", {"adapterID": "pyboy"})
    dap_client.wait_for_event("initialized")
    dap_client.send_request(
        "launch",
        {"stopOnEntry": True, "sourceRoot": os.path.abspath(DEFAULT_ROM_SRC)},
    )

    resp = dap_client.send_request(
        "setBreakpoints",
        {"source": {"path": source_path}, "breakpoints": [{"line": 32}]},
    )
    breakpoint = resp["body"]["breakpoints"][0]
    assert breakpoint["verified"]
    assert breakpoint["line"] == 32
    assert breakpoint["instructionReference"] == entrypoint_ref

    dap_client.send_request("configurationDone")
    dap_client.wait_for_event("stopped")
    dap_client.send_request("continue", {"threadId": 1})
    stopped = dap_client.wait_for_event("stopped")
    assert stopped["body"]["reason"] == "breakpoint"

    frame = dap_client.send_request("stackTrace", {"threadId": 1})["body"]["stackFrames"][0]
    assert frame["source"]["path"] == source_path
    assert frame["line"] == 32


def test_instruction_breakpoint_repeats_after_continue(dap_client):
    breakpoint_ref = pyboy.plugins.debug_adapter._addr_ref(0, 0x01AB)

    dap_client.send_request("initialize", {"adapterID": "pyboy"})
    dap_client.wait_for_event("initialized")
    dap_client.send_request("launch", {"stopOnEntry": True})
    response = dap_client.send_request(
        "setInstructionBreakpoints",
        {"breakpoints": [{"instructionReference": breakpoint_ref}]},
    )
    assert response["body"]["breakpoints"][0]["verified"]

    dap_client.send_request("configurationDone")
    dap_client.wait_for_event("stopped")
    for _ in range(2):
        dap_client.send_request("continue", {"threadId": 1})
        stopped = dap_client.wait_for_event("stopped", timeout=15)
        assert stopped["body"]["reason"] == "instruction breakpoint"


def test_remove_active_source_breakpoint(dap_client):
    source_path = os.path.join(os.path.abspath(DEFAULT_ROM_SRC), "default_rom.asm")

    dap_client.send_request("initialize", {"adapterID": "pyboy"})
    dap_client.wait_for_event("initialized")
    dap_client.send_request(
        "launch",
        {"stopOnEntry": True, "sourceRoot": os.path.abspath(DEFAULT_ROM_SRC)},
    )
    dap_client.send_request(
        "setBreakpoints",
        {"source": {"path": source_path}, "breakpoints": [{"line": 32}]},
    )
    dap_client.send_request("configurationDone")
    dap_client.wait_for_event("stopped")
    dap_client.send_request("continue", {"threadId": 1})
    assert dap_client.wait_for_event("stopped")["body"]["reason"] == "breakpoint"

    # The emulator has already removed the trap byte while its hook callback is paused. Removing
    # the source breakpoint must still succeed and must not leave a pending reinjection behind.
    response = dap_client.send_request("setBreakpoints", {"source": {"path": source_path}, "breakpoints": []})
    assert response["success"], response
    assert response["body"]["breakpoints"] == []

    dap_client.send_request("continue", {"threadId": 1})
    dap_client.send_request("pause", {"threadId": 1})
    assert dap_client.wait_for_event("stopped")["body"]["reason"] == "step"


def test_step_advances_pc(dap_client):
    dap_client.send_request("initialize", {"adapterID": "pyboy"})
    dap_client.wait_for_event("initialized")
    dap_client.send_request("launch", {"stopOnEntry": True})
    dap_client.send_request("configurationDone")
    dap_client.wait_for_event("stopped")

    def current_pc():
        resp = dap_client.send_request("stackTrace", {"threadId": 1})
        ref = resp["body"]["stackFrames"][0]["instructionPointerReference"]
        return ref

    pc1 = current_pc()

    resp = dap_client.send_request("next", {"threadId": 1, "granularity": "instruction"})
    assert resp["success"]
    dap_client.wait_for_event("stopped")

    pc2 = current_pc()
    assert pc1 != pc2


def test_instruction_breakpoint_and_continue(dap_client):
    dap_client.send_request("initialize", {"adapterID": "pyboy"})
    dap_client.wait_for_event("initialized")
    dap_client.send_request("launch", {"stopOnEntry": False})

    # Break right at the start of the cartridge header / entrypoint (0x100), a fixed address in
    # bank 0 that every Game Boy ROM must execute (a `NOP` followed by a `JP`, per Pan Docs).
    entrypoint_ref = pyboy.plugins.debug_adapter._addr_ref(0, 0x0100)
    resp = dap_client.send_request(
        "setInstructionBreakpoints", {"breakpoints": [{"instructionReference": entrypoint_ref}]}
    )
    assert resp["body"]["breakpoints"][0]["verified"]

    dap_client.send_request("configurationDone")
    stopped = dap_client.wait_for_event("stopped")
    # DAP-standard reason so IDEs (e.g. VSCode) auto-focus/reveal the Disassembly View --
    # https://microsoft.github.io/debug-adapter-protocol/specification#Events_Stopped, and see
    # `StackFrame.openInEditor` in VSCode's `debugModel.ts`.
    assert stopped["body"]["reason"] == "instruction breakpoint"

    resp = dap_client.send_request("stackTrace", {"threadId": 1})
    ref = resp["body"]["stackFrames"][0]["instructionPointerReference"]
    assert ref == entrypoint_ref

    # While the breakpoint is set, `hook_register` has patched live memory at 0x0100 with its
    # trap opcode (`0xDB`) -- disassembling that address must show the real, original
    # instruction (`NOP`), not the trap byte.
    resp = dap_client.send_request(
        "disassemble", {"memoryReference": entrypoint_ref, "instructionOffset": 0, "instructionCount": 1}
    )
    instructions = resp["body"]["instructions"]
    assert instructions[0]["instructionBytes"] != "db"
    assert "NOP" in instructions[0]["instruction"]


def test_disassemble(dap_client):
    dap_client.send_request("initialize", {"adapterID": "pyboy"})
    dap_client.wait_for_event("initialized")
    dap_client.send_request("launch", {"stopOnEntry": True})
    dap_client.send_request("configurationDone")
    dap_client.wait_for_event("stopped")

    resp = dap_client.send_request(
        "disassemble",
        {
            "memoryReference": pyboy.plugins.debug_adapter._addr_ref(-1, 0x0000),
            "instructionOffset": 0,
            "instructionCount": 4,
        },
    )
    instructions = resp["body"]["instructions"]
    assert len(instructions) == 4
    for instr in instructions:
        # Every address returned must be parseable as a BigInt by VSCode's Disassembly View
        # (disassemblyView.ts does `BigInt(instruction.address)` and silently drops any row where
        # that throws) -- i.e. a plain hex/decimal integer string, not e.g. "bank:addr".
        int(instr["address"], 16)
        assert pyboy.plugins.debug_adapter._parse_addr_ref(instr["address"])[0] == -1
        assert instr["instruction"]


def test_disassemble_pads_backwards_window_at_start_of_memory(dap_client):
    """A negative `instructionOffset` request whose backward window runs past the start of
    addressable memory (e.g. asking for 50 instructions *before* address 0x0000, which obviously
    don't exist) must still return exactly `instructionCount` rows, with placeholder rows at the
    front (rather than fewer rows overall).

    This matters because VSCode's Disassembly View locates "the instruction at offset 0" (used to
    seed the highlight/scroll position for the current PC) purely by *position* in the returned
    array -- `instructionOffset + i == 0` -- not by matching addresses. Returning a
    shorter-than-requested backward window shifts every later row left by the shortfall, so
    VSCode ends up treating some other, arbitrary, further-into-memory instruction as if it were
    the current one. This was the root cause of the Disassembly View getting stuck highlighting
    the wrong address during early boot (e.g. showing 0x56 while the real PC was 0x0)."""
    dap_client.send_request("initialize", {"adapterID": "pyboy"})
    dap_client.wait_for_event("initialized")
    dap_client.send_request("launch", {"stopOnEntry": True})
    dap_client.send_request("configurationDone")
    dap_client.wait_for_event("stopped")

    resp = dap_client.send_request(
        "disassemble",
        {
            "memoryReference": pyboy.plugins.debug_adapter._addr_ref(-1, 0x0000),
            "instructionOffset": -50,
            "instructionCount": 100,
        },
    )
    instructions = resp["body"]["instructions"]
    assert len(instructions) == 100

    # The row at position 50 (instructionOffset + 50 == 0) must be the actual instruction at the
    # requested address (0x0000), not some other, further-along instruction.
    bank, addr = pyboy.plugins.debug_adapter._parse_addr_ref(instructions[50]["address"])
    assert (bank, addr) == (-1, 0x0000)

    # Rows before it, which couldn't be decoded (nothing exists before address 0), must be
    # explicitly-invalid placeholders that VSCode recognizes and ignores, not silently omitted.
    for instr in instructions[:50]:
        assert instr["address"] == "-1"


def test_disassemble_computes_bank_per_instruction_across_bootrom_boundary(dap_client):
    """A single `disassemble` request that spans the boot ROM -> cartridge ROM transition (a
    real scenario: VSCode routinely requests a wide window, e.g. hundreds of instructions either
    side of the current PC, and during early boot the current PC is well within the first 0x100
    bytes) must label each row with the bank that was *actually* active at that row's own
    address, not just the bank of the window's starting address -- otherwise every row past the
    boundary is mislabeled, producing `address` references that don't match the live PC's
    `instructionPointerReference`, so VSCode's Disassembly View either doesn't highlight the
    current instruction or highlights the wrong row."""
    dap_client.send_request("initialize", {"adapterID": "pyboy"})
    dap_client.wait_for_event("initialized")
    dap_client.send_request("launch", {"stopOnEntry": True})
    dap_client.send_request("configurationDone")
    dap_client.wait_for_event("stopped")

    resp = dap_client.send_request(
        "disassemble",
        {
            "memoryReference": pyboy.plugins.debug_adapter._addr_ref(-1, 0x0000),
            "instructionOffset": 0,
            "instructionCount": 500,
        },
    )
    instructions = resp["body"]["instructions"]
    for instr in instructions:
        bank, addr = pyboy.plugins.debug_adapter._parse_addr_ref(instr["address"])
        # Below 0x100: still the boot ROM (bank -1). At/above 0x100: cartridge ROM (bank 0), even
        # though this is the *same* disassemble request whose window started inside the boot ROM.
        assert bank == (-1 if addr < 0x100 else 0), (hex(addr), bank)


def test_disassemble_annotates_symbols_for_targets_and_routine_starts(tmp_path):
    """CALL/JP (and similar) operands should show the symbol label from a loaded `.sym` file
    instead of a raw hex address, when one is known for the target address. The instruction
    actually at a labeled address should also show that label as a suffix, marking the start of
    a routine."""
    rom_path = tmp_path / "rom.gb"
    with open(DEFAULT_ROM, "rb") as f:
        rom_path.write_bytes(f.read())
    # default_rom.gb's entrypoint (0x100) is: NOP; JP $0150 (see Pan Docs cartridge header).
    (tmp_path / "rom.sym").write_text("00:0150 EntryPoint\n")

    proc = subprocess.Popen(
        [sys.executable, "-m", "pyboy", str(rom_path), "--window", "null", "--no-input", "--debug-adapter"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    client = DAPClient(proc)
    try:
        client.send_request("initialize", {"adapterID": "pyboy"})
        client.wait_for_event("initialized")
        client.send_request("launch", {"stopOnEntry": True})
        client.send_request("configurationDone")
        client.wait_for_event("stopped")

        resp = client.send_request(
            "disassemble",
            {
                "memoryReference": pyboy.plugins.debug_adapter._addr_ref(0, 0x0100),
                "instructionOffset": 0,
                "instructionCount": 2,
            },
        )
        instructions = resp["body"]["instructions"]
        assert instructions[0]["instruction"] == "NOP"
        # The label is substituted in place of the raw hex target, and (unlike LD's memory
        # operands) isn't wrapped in parens, since JP jumps directly to the address rather than
        # dereferencing it.
        assert instructions[1]["instruction"] == "JP EntryPoint"

        # The instruction actually located at a labeled address should show that label as a
        # suffix on its own row too, so the start of a routine is visible even when not jumped to
        # from elsewhere in the disassembly window (VSCode's Disassembly View doesn't render the
        # DAP `symbol` field itself, so it must be part of the `instruction` text to be visible).
        resp = client.send_request(
            "disassemble",
            {
                "memoryReference": pyboy.plugins.debug_adapter._addr_ref(0, 0x0150),
                "instructionOffset": 0,
                "instructionCount": 1,
            },
        )
        instructions = resp["body"]["instructions"]
        assert instructions[0]["instruction"] == "NOP [EntryPoint]"
        assert instructions[0]["symbol"] == "EntryPoint"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            if stream is not None:
                stream.close()


@pytest.mark.skipif(
    any(shutil.which(tool) is None for tool in ("rgbasm", "rgblink", "rgbfix")), reason="RGBDS tools not installed"
)
def test_source_root_reports_source_line_in_stack_trace(tmp_path):
    """When `launch`'s `sourceRoot` points at a matching RGBDS disassembly project checkout,
    `stackTrace` should report the real `.asm` source file/line for the current PC instead of
    only the raw disassembly -- letting VSCode step inline in source, falling back to the
    Disassembly View automatically wherever no mapping exists (e.g. mid-instruction, or over
    `INCBIN`-only data)."""
    obj = tmp_path / "default_rom.obj"
    sym = tmp_path / "default_rom.sym"
    map_file = tmp_path / "default_rom.map"
    gb = tmp_path / "default_rom.gb"
    subprocess.run(["rgbasm", "-o", str(obj), "default_rom.asm"], cwd=DEFAULT_ROM_SRC, check=True, capture_output=True)
    subprocess.run(
        ["rgblink", "-m", str(map_file), "-n", str(sym), "-o", str(gb), str(obj)], check=True, capture_output=True
    )
    subprocess.run(["rgbfix", "-p0", "-f", "hg", str(gb)], check=True, capture_output=True)

    proc = subprocess.Popen(
        [sys.executable, "-m", "pyboy", str(gb), "--window", "null", "--no-input", "--debug-adapter"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    client = DAPClient(proc)
    try:
        client.send_request("initialize", {"adapterID": "pyboy"})
        client.wait_for_event("initialized")
        resp = client.send_request("launch", {"stopOnEntry": True, "sourceRoot": os.path.abspath(DEFAULT_ROM_SRC)})
        assert resp["success"], resp

        client.send_request("configurationDone")
        client.wait_for_event("stopped")
        boot_frame = client.send_request("stackTrace", {"threadId": 1})["body"]["stackFrames"][0]
        assert boot_frame["source"]["name"] == "bootrom_common.asm"
        assert boot_frame["source"]["path"].endswith(os.path.join("extras", "bootrom", "bootrom_common.asm"))
        assert boot_frame["line"] == 4

        # Break at $150 (`Main:`, see `extras/default_rom/default_rom.asm`).
        client.send_request(
            "setInstructionBreakpoints",
            {"breakpoints": [{"instructionReference": pyboy.plugins.debug_adapter._addr_ref(0, 0x0150)}]},
        )
        client.send_request("continue", {"threadId": 1})
        stopped = client.wait_for_event("stopped")
        assert stopped["body"]["reason"] == "instruction breakpoint"

        resp = client.send_request("stackTrace", {"threadId": 1})
        frame = resp["body"]["stackFrames"][0]
        assert frame["source"]["name"] == "default_rom.asm"
        assert frame["source"]["path"] == os.path.join(os.path.abspath(DEFAULT_ROM_SRC), "default_rom.asm")
        assert frame["line"] == 32  # `nop` right after the `Main:` label
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            if stream is not None:
                stream.close()
