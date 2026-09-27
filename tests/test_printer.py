#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import os.path
import tempfile
from pathlib import Path

import PIL

from pyboy.plugins.game_boy_printer import GameBoyPrinter

OVERWRITE_PNGS = False


def _send_packet(printer, magic, command, compression, data):
    """Send a complete printer packet and return the responses.

    responses[i] is the byte_to_send after processing byte i.
    With 1-byte delay, responses[i] is what the GB reads during byte i+1's transfer.
    The alive response (0x81) is at responses[-3] (from checksum_msb processing).
    The status response is at responses[-2] (from alive processing, before command executes).
    """
    length = len(data)
    checksum = command + compression + (length & 0xFF) + ((length >> 8) & 0xFF) + sum(data)
    checksum_lsb = checksum & 0xFF
    checksum_msb = (checksum >> 8) & 0xFF

    packet = list(magic) + [command, compression, length & 0xFF, (length >> 8) & 0xFF]
    packet += list(data)
    packet += [checksum_lsb, checksum_msb, 0x00, 0x00]

    responses = []
    for byte in packet:
        printer.process_byte(byte)
        responses.append(printer.byte_to_send)

    return responses


def test_printer_init():
    printer = GameBoyPrinter(output_dir=tempfile.gettempdir())

    responses = _send_packet(printer, [0x88, 0x33], 0x01, 0x00, [])

    # responses[-3] = alive response (0x81), responses[-2] = INIT returns 0 at ALIVE
    assert responses[-3] == 0x81, f"Alive byte should be 0x81, got {responses[-3]:#x}"
    assert responses[-2] == 0x00, f"INIT alive should return 0, got {responses[-2]:#x}"
    assert printer.status == 0
    assert printer.image_offset == 0


def test_printer_status_command():
    printer = GameBoyPrinter(output_dir=tempfile.gettempdir())

    responses = _send_packet(printer, [0x88, 0x33], 0x0F, 0x00, [])

    assert responses[-3] == 0x81, "Alive byte should be 0x81"
    # Status at alive time is 0x00 (idle, before STATUS command executes as NOP)
    assert responses[-2] == 0x00, "Status should be 0x00 (idle)"


def test_printer_data_command():
    printer = GameBoyPrinter(output_dir=tempfile.gettempdir())

    data = [0x00] * 640
    responses = _send_packet(printer, [0x88, 0x33], 0x04, 0x00, data)

    assert responses[-3] == 0x81, "Alive byte should be 0x81"
    # Status at alive time is 0x00 (handle_command hasn't run yet, 1-byte delay)
    assert responses[-2] == 0x00, f"Status at alive should be 0x00, got {responses[-2]:#x}"
    # After command execution, status is 0x08 (unprocessed data)
    assert printer.status == 0x08
    assert printer.image_offset == 160 * 16, f"Image offset should be 2560, got {printer.image_offset}"


def test_printer_data_partial():
    printer = GameBoyPrinter(output_dir=tempfile.gettempdir())

    data = [0xFF] * 320
    responses = _send_packet(printer, [0x88, 0x33], 0x04, 0x00, data)

    assert responses[-3] == 0x81, "Alive byte should be 0x81"
    # Partial data doesn't set status to 0x08 (only full 0x280 segments do)
    assert printer.status == 0x00


def test_printer_checksum_error():
    printer = GameBoyPrinter(output_dir=tempfile.gettempdir())

    # Manually construct a packet with wrong checksum
    packet = [0x88, 0x33, 0x0F, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00]

    responses = []
    for byte in packet:
        printer.process_byte(byte)
        responses.append(printer.byte_to_send)

    # Checksum mismatch should set checksum error bit in status
    assert printer.status & 1, "Checksum error bit should be set"
    # State should reset to MAGIC1
    assert printer.command_state == 0, "State should reset to MAGIC1 after checksum error"


def test_printer_magic_reset():
    printer = GameBoyPrinter(output_dir=tempfile.gettempdir())

    # Send a non-magic byte — should be ignored
    printer.process_byte(0x00)
    assert printer.command_state == 0, "Should stay in MAGIC1 state"

    # Send first magic byte
    printer.process_byte(0x88)
    assert printer.command_state == 1, "Should advance to MAGIC2"

    # Send wrong second byte (not 0x33)
    printer.process_byte(0x00)
    assert printer.command_state == 0, "Should reset to MAGIC1 on wrong magic2"

    # Send 0x88 again as second byte — should stay in MAGIC2
    printer.process_byte(0x88)
    assert printer.command_state == 1, "Should stay in MAGIC2 if 0x88 received"


def test_printer_full_flow():
    printer = GameBoyPrinter(output_dir=tempfile.gettempdir())

    # INIT
    _send_packet(printer, [0x88, 0x33], 0x01, 0x00, [])
    assert printer.status == 0

    # DATA — fill with a simple pattern (640 bytes = one 160x16 segment)
    data = [0xFF] * 640
    _send_packet(printer, [0x88, 0x33], 0x04, 0x00, data)
    assert printer.status == 0x08
    assert printer.image_offset == 160 * 16

    # Empty DATA (required before PRINT per Pan Docs)
    _send_packet(printer, [0x88, 0x33], 0x04, 0x00, [])

    # PRINT — margins=0x13, palette=0xE4, exposure=0x40
    print_data = [0x01, 0x13, 0xE4, 0x40]
    _send_packet(printer, [0x88, 0x33], 0x02, 0x00, print_data)
    assert printer.status == 6, f"Status should be 6 (printing), got {printer.status:#x}"

    # STATUS poll — should show 4 (done) since time_remaining is 0
    _send_packet(printer, [0x88, 0x33], 0x0F, 0x00, [])
    assert printer.status == 4, f"Status should be 4 (done), got {printer.status:#x}"


def test_printer_rle_decompression():
    printer = GameBoyPrinter(output_dir=tempfile.gettempdir())

    # Construct RLE-compressed data that expands to 640 bytes:
    # Control byte 0x82 = compressed run, length = 2 + 2 = 4, repeat 0xFF
    # Each: 0x82 0xFF -> 4 bytes of 0xFF
    # 160 runs * 4 bytes = 640 bytes
    compressed = []
    for _ in range(160):
        compressed.extend([0x82, 0xFF])
    assert len(compressed) == 320

    _send_packet(printer, [0x88, 0x33], 0x04, 0x01, compressed)
    assert printer.status == 0x08, f"Status should be 0x08 after RLE data, got {printer.status:#x}"
    assert printer.image_offset == 160 * 16

    # All pixels should be 3 (0xFF in 2BPP = both bits set = value 3)
    for i in range(160 * 16):
        assert printer.image[i] == 3, f"Pixel {i} should be 3, got {printer.image[i]}"


def test_printer_image_output():
    printer = GameBoyPrinter(output_dir=tempfile.gettempdir())

    # INIT
    _send_packet(printer, [0x88, 0x33], 0x01, 0x00, [])

    # DATA — all zeros (white image)
    data = [0x00] * 640
    _send_packet(printer, [0x88, 0x33], 0x04, 0x00, data)

    # PRINT
    _send_packet(printer, [0x88, 0x33], 0x02, 0x00, [0x01, 0x13, 0xE4, 0x40])

    # Check that an image was produced
    img = printer.get_image()
    assert img is not None, "Should have a printed image"
    assert img.width == 160
    assert img.height == 16

    # All-white image (all zeros in 2BPP = shade 0 = white)
    pixel = img.getpixel((0, 0))
    assert pixel == (0xFF, 0xFF, 0xFF), f"Pixel should be white, got {pixel}"

    # Flush and check file was saved
    printer.stop()
    files = [f for f in os.listdir(tempfile.gettempdir()) if f.startswith("print_") and f.endswith(".png")]
    assert len(files) > 0, "Should have saved at least one PNG file"

    # Cleanup
    for f in files:
        os.remove(os.path.join(tempfile.gettempdir(), f))


def test_serial_printer_with_emulator(default_rom):
    from pyboy import PyBoy

    pyboy = PyBoy(default_rom, window="null", printer=True, printer_output=tempfile.gettempdir())
    pyboy.set_emulation_speed(0)

    # The printer should be enabled — check via the API
    assert pyboy.printer_image() is None, "No image should be printed yet"

    # A serial transfer should complete normally
    pyboy.tick(60, False)
    pyboy.memory[0xFF02] = 0x81
    assert pyboy.memory[0xFF02] & 0x80
    pyboy.tick(1, False)
    assert not pyboy.memory[0xFF02] & 0x80

    # The printer should respond with 0x00 for non-magic bytes
    assert pyboy.memory[0xFF01] == 0x00, f"Printer should respond 0x00, got {pyboy.memory[0xFF01]:#x}"

    pyboy.stop(save=False)

    # Cleanup any generated files
    files = [f for f in os.listdir(tempfile.gettempdir()) if f.startswith("print_") and f.endswith(".png")]
    for f in files:
        os.remove(os.path.join(tempfile.gettempdir(), f))


def test_serial_printer_detection(default_rom):
    """Test the Pan Docs printer detection sequence."""
    from pyboy import PyBoy

    pyboy = PyBoy(default_rom, window="null", printer=True, printer_output=tempfile.gettempdir())
    pyboy.set_emulation_speed(0)
    pyboy.tick(60, False)

    # Send the detection packet: 0x88, 0x33, 0x0F, 0x00, 0x00, 0x00, 0x0F, 0x00, 0x00, 0x00
    # (magic, command=STATUS, compression=0, length=0, checksum=0x000F, alive, status)
    detection_bytes = [0x88, 0x33, 0x0F, 0x00, 0x00, 0x00, 0x0F, 0x00, 0x00, 0x00]

    responses = []
    for byte in detection_bytes:
        pyboy.memory[0xFF01] = byte
        pyboy.memory[0xFF02] = 0x81  # Internal clock, start transfer
        pyboy.tick(1, False)  # Complete the transfer
        responses.append(pyboy.memory[0xFF01])

    # With 1-byte delay, the response to byte N is read during byte N+1's transfer.
    # Byte 8 (alive=0x00): GB reads response to byte 7 (checksum_msb) = 0x81
    # Byte 9 (status=0x00): GB reads response to byte 8 (alive) = status byte (0x00 idle)
    assert responses[8] == 0x81, f"Printer should be detected (0x81), got {responses[8]:#x}"
    assert responses[9] == 0x00, f"Status should be 0x00 (idle), got {responses[9]:#x}"

    pyboy.stop(save=False)

    # Cleanup
    files = [f for f in os.listdir(tempfile.gettempdir()) if f.startswith("print_") and f.endswith(".png")]
    for f in files:
        os.remove(os.path.join(tempfile.gettempdir(), f))


def test_printer_rom(print_file):
    """End-to-end test with the gbprinter test ROM.

    Boots the ROM, presses A to add characters, then Start to print,
    and verifies the printed image matches a saved baseline (acid-test style).
    """
    from pyboy import PyBoy

    pyboy = PyBoy(print_file, window="null", printer=True, printer_output=tempfile.gettempdir())
    pyboy.set_emulation_speed(0)

    # Let the ROM boot
    pyboy.tick(60, False)

    # Press A a bunch of times to add characters to the screen
    for _ in range(20):
        pyboy.button("a")
        pyboy.tick(5, False)

    # Press Start to initiate the print
    pyboy.button("start")

    # The printing process takes many serial transfers. Run enough frames
    # for the full INIT + DATA + PRINT + STATUS sequence to complete.
    for _ in range(600):
        pyboy.tick(1, False)
        if pyboy.printer_image() is not None:
            break

    image = pyboy.printer_image()
    assert image is not None, "Should have printed an image"

    pyboy.stop(save=False)

    png_path = Path("tests/test_results/print_gbprinter.png")
    if OVERWRITE_PNGS:
        png_path.parents[0].mkdir(parents=True, exist_ok=True)
        image.save(png_path)
    else:
        assert png_path.exists(), "Test result doesn't exist"
        old_image = PIL.Image.open(png_path).convert("RGB")
        diff = PIL.ImageChops.difference(image.convert("RGB"), old_image)
        if diff.getbbox() and os.environ.get("TEST_VERBOSE_IMAGES"):
            image.show()
            old_image.show()
            diff.show()
        assert not diff.getbbox(), "Images are different!"

    # Cleanup any generated files
    files = [f for f in os.listdir(tempfile.gettempdir()) if f.startswith("print_") and f.endswith(".png")]
    for f in files:
        os.remove(os.path.join(tempfile.gettempdir(), f))
