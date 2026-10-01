#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

"""Actual CPU/serial tests using tiny original programs, without commercial ROMs."""

import io
import json
import threading
from zipfile import ZipFile

import pytest

from pyboy import LinkCable, PyBoy
from pyboy.utils import PyBoyInvalidInputException, PyBoyInvalidOperationException, WindowEvent


def cartridge(title="LINK", program=b"\x18\xfe", cgb=True):
    rom = bytearray(32768)
    rom[0x100:0x104] = b"\x00\xc3\x50\x01"
    rom[0x134 : 0x134 + len(title)] = title.encode()
    rom[0x143] = 0x80 if cgb else 0
    rom[0x150 : 0x150 + len(program)] = program
    rom[0x14D] = (-sum(rom[0x134:0x14D]) - 25) & 255
    return io.BytesIO(rom)


def endpoint(title="LINK", program=b"\x18\xfe", cgb=True, no_input=True):
    machine = PyBoy(cartridge(title, program, cgb), window="null", no_input=no_input, cgb=cgb)
    machine.set_emulation_speed(0)
    machine.memory[0xFF50] = 1
    machine.register_file.PC = 0x150
    return machine


@pytest.fixture
def cable():
    machines = [endpoint("LEFT"), endpoint("RIGHT")]
    pair = LinkCable(*machines)
    yield pair
    pair.close()
    for machine in machines:
        machine.stop(save=False)


def start(pair, controls=(0x81, 0x80)):
    for machine, data, control in zip(pair.machines, (0xA5, 0x3C), controls):
        machine.memory[0xFF01] = data
        machine.memory[0xFF02] = control
        machine.memory[0xFF0F] = 0


def save(pair):
    stream = io.BytesIO()
    pair.save_state(stream)
    return stream.getvalue()


def contents(blob):
    with ZipFile(io.BytesIO(blob)) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def rewrite(blob, change):
    files = contents(blob)
    data = json.loads(files["cable.json"])
    change(data, files)
    files["cable.json"] = json.dumps(data).encode()
    stream = io.BytesIO()
    with ZipFile(stream, "w") as archive:
        for name, value in files.items():
            archive.writestr(name, value)
    return io.BytesIO(stream.getvalue())


def test_cpu_programs_exchange_bytes_and_observe_completion():
    def program(data, control):
        # DI; LD A,data; LDH(SB),A; LD A,control; LDH(SC),A;
        # poll SC.7; copy received byte to C000; signal completion at C001; loop.
        return bytes(
            [
                0xF3,
                0x3E,
                data,
                0xE0,
                0x01,
                0x3E,
                control,
                0xE0,
                0x02,
                0xF0,
                0x02,
                0xCB,
                0x7F,
                0x20,
                0xFA,
                0xF0,
                0x01,
                0xEA,
                0x00,
                0xC0,
                0x3E,
                1,
                0xEA,
                0x01,
                0xC0,
                0x18,
                0xFE,
            ]
        )

    machines = [endpoint("LEFT", program(0xA5, 0x81)), endpoint("RIGHT", program(0x3C, 0x80))]
    try:
        with LinkCable(*machines) as pair:
            pair.advance(5000)
            assert [m.memory[0xC000] for m in machines] == [0x3C, 0xA5]
            assert [m.memory[0xC001] for m in machines] == [1, 1]
            assert all(m.memory[0xFF0F] & 8 for m in machines)
            assert pair.transfers == (1, 1)
    finally:
        for machine in machines:
            machine.stop(save=False)


def test_two_external_clocks_wait(cable):
    start(cable, (0x80, 0x80))
    cable.advance(5000)
    assert cable.transfers == (0, 0)
    assert [m.memory[0xFF01] for m in cable.machines] == [0xA5, 0x3C]


def test_disconnect_and_reconnect(cable):
    start(cable)
    cable.disconnect()
    cable.advance(5000)
    assert [m.memory[0xFF01] for m in cable.machines] == [255, 0x3C]
    assert cable.transfers == (1, 0)
    cable.connect()
    start(cable)
    cable.advance(5000)
    assert [m.memory[0xFF01] for m in cable.machines] == [0x3C, 0xA5]
    assert cable.transfers == (2, 1)


def test_partial_byte_and_pending_input_resume_identically(cable):
    start(cable)
    cable.advance(1600)
    cable.machines[0].button("a", delay=3)
    cable.machines[1].button_press("start")
    checkpoint = save(cable)
    cable.tick(5)
    expected = contents(save(cable))
    cable.load_state(io.BytesIO(checkpoint))
    cable.tick(5)
    assert contents(save(cable)) == expected
    assert cable.transfers == (1, 1)


def test_restart_requires_eight_fresh_edges(cable):
    start(cable)
    cable.advance(1600)
    start(cable)
    cable.advance(3000)
    assert cable.transfers == (0, 0)
    cable.advance(1200)
    assert cable.transfers == (1, 1)


def test_internal_clocks_do_not_shift_on_peer_edges(cable):
    start(cable, (0x81, 0x81))
    cable.advance(3000)
    assert cable.transfers == (0, 0)
    cable.advance(1200)
    assert cable.transfers == (1, 1)


def test_fast_serial_rejected_and_halted_before_cpu_progress(cable):
    start(cable, (0x83, 0x80))
    with pytest.raises(PyBoyInvalidOperationException, match="Fast CGB"):
        cable.tick()
    assert cable.halted
    assert cable.cycles == (0, 0)


def test_dmg_read_only_fast_bit_is_not_fast_serial():
    machines = [endpoint(cgb=False), endpoint(cgb=False)]
    try:
        with LinkCable(*machines) as pair:
            start(pair)
            pair.advance(5000)
            assert pair.transfers == (1, 1)
    finally:
        for machine in machines:
            machine.stop(save=False)


def test_halt_resume_and_halted_save(cable):
    start(cable)
    cable.advance(1600)
    cable.halt()
    checkpoint = save(cable)
    before = cable.cycles
    assert cable.tick() is False
    assert cable.step() is False
    assert cable.cycles == before
    cable.resume()
    cable.advance(5000)
    assert cable.transfers == (1, 1)
    cable.load_state(io.BytesIO(checkpoint))
    assert cable.halted and cable.cycles == before
    cable.resume()
    cable.advance(5000)
    assert cable.transfers == (1, 1)


def test_halt_can_interrupt_compiled_execution_from_another_thread(cable):
    timer = threading.Timer(0.02, cable.halt)
    timer.start()
    try:
        assert cable.tick(600) is False
        assert min(cable.cycles) < 600 * 70224
    finally:
        timer.cancel()
        timer.join()


def test_individual_tick_and_state_operations_are_blocked(cable):
    machine = cable.machines[0]
    for action in (machine.tick, lambda: machine.save_state(io.BytesIO()), lambda: machine.load_state(io.BytesIO())):
        with pytest.raises(PyBoyInvalidOperationException, match="LinkCable"):
            action()
    with pytest.raises(PyBoyInvalidOperationException, match="Hooks"):
        machine.hook_register(0, 0x150, lambda _: None, None)
    with pytest.raises(PyBoyInvalidOperationException, match="joypad"):
        machine.send_input(WindowEvent.STATE_LOAD)


def test_owned_endpoint_cannot_join_another_pair(cable):
    third = endpoint("THIRD")
    try:
        with pytest.raises(PyBoyInvalidOperationException, match="belongs"):
            LinkCable(third, cable.machines[0])
        third.tick()  # Failed construction must not attach the free endpoint.
    finally:
        third.stop(save=False)


def test_close_releases_individual_execution(cable):
    cable.close()
    cable.close()
    assert all(m.tick() for m in cable.machines)
    with pytest.raises(PyBoyInvalidOperationException, match="closed"):
        cable.tick()


@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_invalid_tick_counts_are_rejected(cable, value):
    with pytest.raises(ValueError):
        cable.tick(value)


@pytest.mark.parametrize(
    "change",
    [
        lambda data, files: data.update(identities=data["identities"][::-1]),
        lambda data, files: data.update(state_version=0),
        lambda data, files: data.update(bits=[9, 0]),
        lambda data, files: data.update(edges=[-1, None]),
        lambda data, files: data["runtime"][0].update(events=[WindowEvent.STATE_LOAD]),
        lambda data, files: files.update({"1.state": b"broken"}),
    ],
)
def test_bad_bundle_rejected_without_changing_either_endpoint(cable, change):
    start(cable)
    cable.advance(1600)
    checkpoint = save(cable)
    with pytest.raises(PyBoyInvalidInputException):
        cable.load_state(rewrite(checkpoint, change))
    assert contents(save(cable)) == contents(checkpoint)


def test_corrupt_archive_rejected(cable):
    with pytest.raises(PyBoyInvalidInputException):
        cable.load_state(io.BytesIO(b"not a state"))


def test_second_endpoint_load_failure_rolls_back_both(cable):
    class FailingEndpoint:
        def __init__(self, machine):
            self.machine = machine
            self.fail = True

        def __getattr__(self, name):
            return getattr(self.machine, name)

        def _link_restore(self, *args):
            if self.fail:
                self.fail = False
                raise ValueError("second endpoint failed")
            return self.machine._link_restore(*args)

    checkpoint = save(cable)
    cable.tick()
    before = contents(save(cable))
    cable.machines = (cable.machines[0], FailingEndpoint(cable.machines[1]))
    with pytest.raises(ValueError, match="second endpoint"):
        cable.load_state(io.BytesIO(checkpoint))
    assert contents(save(cable)) == before


def test_double_speed_clock_completes_in_half_the_base_cycles():
    # STOP performs the CGB speed switch requested through KEY1.
    machines = [endpoint("LEFT", b"\x10\x00\x18\xfe"), endpoint("RIGHT")]
    machines[0].memory[0xFF4D] = 1
    try:
        with LinkCable(*machines) as pair:
            pair.advance(100)
            assert machines[0].memory[0xFF4D] & 0x80
            start(pair)
            pair.advance(1900)
            assert pair.transfers == (0, 0)
            pair.advance(200)
            assert pair.transfers == (1, 1)
    finally:
        for machine in machines:
            machine.stop(save=False)


def test_frame_and_audio_buffers_advance(cable):
    before = [m.frame_count for m in cable.machines]
    cable.tick(3)
    assert all(m.frame_count >= frame + 2 for m, frame in zip(cable.machines, before))
    assert all(m.sound.ndarray.size > 0 for m in cable.machines)
    cable.halt()
    held = [m.frame_count for m in cable.machines]
    cable.tick()
    assert [m.frame_count for m in cable.machines] == held


def test_duplicate_endpoint_rejected(cable):
    with pytest.raises(PyBoyInvalidInputException, match="distinct"):
        LinkCable(cable.machines[0], cable.machines[0])


def test_interactive_input_rejected_before_attachment():
    machines = [endpoint("LEFT", no_input=False), endpoint("RIGHT")]
    try:
        with pytest.raises(PyBoyInvalidOperationException, match="no_input"):
            LinkCable(*machines)
        assert all(m.tick() for m in machines)
    finally:
        for machine in machines:
            machine.stop(save=False)


def test_rom_override_after_attachment_invalidates_old_state(cable):
    checkpoint = save(cable)
    cable.machines[0].memory[0, 0x200] = 0x42
    with pytest.raises(PyBoyInvalidInputException, match="Cartridge"):
        cable.load_state(io.BytesIO(checkpoint))


def test_detach_abandons_pending_transfer(cable):
    start(cable)
    cable.advance(1000)
    cable.close()
    for machine in cable.machines:
        assert not machine.memory[0xFF02] & 0x80
        assert machine.memory[0xFF01] == 255
        assert machine.tick(2)
