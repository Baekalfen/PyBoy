#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from array import array

import pyboy
from pyboy.core import serial
from pyboy.plugins.base_plugin import PyBoyPlugin

logger = pyboy.logging.get_logger(__name__)


# Printer commands
PRINTER_INIT = 0x01
PRINTER_PRINT = 0x02
PRINTER_DATA = 0x04
PRINTER_STATUS = 0x0F

# State machine states
MAGIC1 = 0
MAGIC2 = 1
COMMAND = 2
COMPRESSION = 3
LENGTH_LSB = 4
LENGTH_MSB = 5
DATA = 6
CHECKSUM_LSB = 7
CHECKSUM_MSB = 8
ALIVE = 9
STATUS = 10

# Buffer dimensions
PRINTER_WIDTH = 160
PRINTER_MAX_HEIGHT = 200
PRINTER_BUFFER_SIZE = PRINTER_WIDTH * PRINTER_MAX_HEIGHT
PRINTER_MAX_DATA = 0x280  # 640 bytes per DATA command (160x16 pixels in 2BPP)


class GameBoyPrinter(PyBoyPlugin):
    argv = [
        ("--printer", {"action": "store_true", "help": "Enable Game Boy Printer emulation"}),
        (
            "--printer-output",
            {"type": str, "help": "Output directory for printed images (default: current directory)"},
        ),
    ]

    def __init__(self, pyboy=None, mb=None, pyboy_argv=None, output_dir="."):
        if mb is None:
            self.output_dir = output_dir
            self._enabled = True
        else:
            super().__init__(pyboy, mb, pyboy_argv)
            self.output_dir = pyboy_argv.get("printer_output") or "."
            self._enabled = bool(pyboy_argv.get("printer")) and type(mb.serial) is serial.Serial
            if self._enabled:
                mb.serial = serial.SerialPrinter(mb.cgb_mode, self)

        if not self._enabled:
            return

        self._initialize()

    def _initialize(self):
        # State machine
        self.command_state = MAGIC1
        self.command_id = 0
        self.compression = 0
        self.length_left = 0
        self.command_length = 0
        self.checksum = 0
        self.status = 0
        self.byte_to_send = 0

        # Command data buffer
        self.command_data = array("B", [0] * PRINTER_MAX_DATA)

        # Image buffer (1 byte per pixel, value 0-3)
        self.image = array("B", [0] * PRINTER_BUFFER_SIZE)
        self.image_offset = 0

        # Compression state
        self.compression_run_length = 0
        self.compression_run_is_compressed = 0

        # Print parameters
        self.print_margins = 0
        self.print_palette = 0xE4
        self.print_exposure = 0x40

        # Continuous printing (stitching)
        self._stitch_image = None  # PIL Image for stitching
        self._print_count = 0

        # Printing delay
        self.time_remaining = 0

        # Last decoded image (for API access)
        self._last_image = None

    def enabled(self):
        return self._enabled

    def process_byte(self, byte_received):
        self.byte_to_send = 0

        if self.command_state == MAGIC1:
            if byte_received != 0x88:
                return
            self.status &= ~1  # Clear checksum error bit
            self.command_length = 0
            self.checksum = 0
        elif self.command_state == MAGIC2:
            if byte_received != 0x33:
                if byte_received != 0x88:
                    self.command_state = MAGIC1
                return
        elif self.command_state == COMMAND:
            self.command_id = byte_received & 0xF
        elif self.command_state == COMPRESSION:
            self.compression = byte_received & 1
        elif self.command_state == LENGTH_LSB:
            self.length_left = byte_received
        elif self.command_state == LENGTH_MSB:
            self.length_left |= (byte_received & 0x3) << 8
        elif self.command_state == DATA:
            if self.command_length < PRINTER_MAX_DATA:
                if self.compression:
                    self._decompress_byte(byte_received)
                else:
                    self.command_data[self.command_length] = byte_received
                    self.command_length += 1
            self.length_left -= 1
        elif self.command_state == CHECKSUM_LSB:
            self.checksum ^= byte_received
        elif self.command_state == CHECKSUM_MSB:
            self.checksum ^= byte_received << 8
            if self.checksum:
                self.status |= 1  # Checksum error
                self.command_state = MAGIC1
                return
            self.byte_to_send = 0x81
        elif self.command_state == ALIVE:
            if self.command_id == PRINTER_INIT:
                self.byte_to_send = 0
            else:
                if self.status == 6 and self.time_remaining == 0:
                    self.status = 4  # Printing done
                self.byte_to_send = self.status
        elif self.command_state == STATUS:
            self.command_state = MAGIC1
            self._handle_command()
            return

        # Accumulate checksum for bytes from COMMAND through DATA
        if self.command_state >= COMMAND and self.command_state < CHECKSUM_LSB:
            self.checksum = (self.checksum + byte_received) & 0xFFFF

        # Advance state
        if self.command_state != DATA:
            self.command_state += 1

        # Skip DATA state if no data
        if self.command_state == DATA:
            if self.length_left == 0:
                self.command_state += 1

    def _decompress_byte(self, byte_received):
        if self.compression_run_length == 0:
            self.compression_run_is_compressed = byte_received & 0x80
            self.compression_run_length = (byte_received & 0x7F) + 1 + self.compression_run_is_compressed
        elif self.compression_run_is_compressed:
            while self.compression_run_length:
                if self.command_length < PRINTER_MAX_DATA:
                    self.command_data[self.command_length] = byte_received
                    self.command_length += 1
                self.compression_run_length -= 1
                if self.command_length >= PRINTER_MAX_DATA:
                    self.compression_run_length = 0
                    break
        else:
            if self.command_length < PRINTER_MAX_DATA:
                self.command_data[self.command_length] = byte_received
                self.command_length += 1
            self.compression_run_length -= 1

    def _handle_command(self):
        if self.command_id == PRINTER_INIT:
            self.status = 0
            self.image_offset = 0
        elif self.command_id == PRINTER_PRINT:
            if self.command_length == 4:
                self.status = 6  # Printing
                self.print_margins = self.command_data[1]
                self.print_palette = self.command_data[2]
                self.print_exposure = self.command_data[3] & 0x7F

                # Instant printing: time_remaining set to 0 so status transitions
                # to 4 (done) on the next status poll. Real hardware takes time,
                # but games poll until done and instant works in practice.
                self.time_remaining = 0

                try:
                    self._decode_and_save_image()
                except Exception:
                    logger.exception("Failed to save printer image")
                self.image_offset = 0
        elif self.command_id == PRINTER_DATA:
            if self.command_length == PRINTER_MAX_DATA:
                self.image_offset %= PRINTER_BUFFER_SIZE
                self.status = 8  # Unprocessed data

                byte_idx = 0
                for _ in range(2):  # 2 rows of 8 pixels
                    for tile_x in range(PRINTER_WIDTH // 8):
                        for y in range(8):
                            byte_lo = self.command_data[byte_idx]
                            byte_hi = self.command_data[byte_idx + 1]
                            byte_idx += 2
                            for x_pixel in range(8):
                                pixel = ((byte_lo >> 7) & 1) | (((byte_hi >> 7) & 1) << 1)
                                byte_lo <<= 1
                                byte_hi <<= 1
                                idx = self.image_offset + tile_x * 8 + x_pixel + y * PRINTER_WIDTH
                                if idx < PRINTER_BUFFER_SIZE:
                                    self.image[idx] = pixel

                    self.image_offset += 8 * PRINTER_WIDTH
        # STATUS (0x0F) is a NOP, just returns status

    def _decode_and_save_image(self):
        if self.image_offset == 0:
            return

        try:
            from PIL import Image
        except ImportError:
            logger.error("PIL/Pillow is required for GB Printer image output")
            return

        height = self.image_offset // PRINTER_WIDTH
        if height == 0:
            return

        # Decode 2BPP pixel values to RGB using palette
        colors = [
            (0xFF, 0xFF, 0xFF),  # Shade 0 - white
            (0xAA, 0xAA, 0xAA),  # Shade 1 - light gray
            (0x55, 0x55, 0x55),  # Shade 2 - dark gray
            (0x00, 0x00, 0x00),  # Shade 3 - black
        ]

        pixels = bytearray(self.image_offset * 3)
        for i in range(self.image_offset):
            shade = (self.print_palette >> (self.image[i] * 2)) & 3
            r, g, b = colors[shade]
            pixels[i * 3] = r
            pixels[i * 3 + 1] = g
            pixels[i * 3 + 2] = b

        img = Image.frombytes("RGB", (PRINTER_WIDTH, height), bytes(pixels))

        # Continuous printing: stitch when margins are zero
        margins = self.print_margins
        top_margin = (margins >> 4) & 0xF
        bottom_margin = margins & 0xF

        if top_margin == 0 and bottom_margin == 0 and self._stitch_image is not None:
            # Append to existing stitched image
            new_height = self._stitch_image.height + height
            stitched = Image.new("RGB", (PRINTER_WIDTH, new_height))
            stitched.paste(self._stitch_image, (0, 0))
            stitched.paste(img, (0, self._stitch_image.height))
            self._stitch_image = stitched
        elif top_margin == 0 and bottom_margin == 0:
            # Start new stitched image
            self._stitch_image = img.copy()
        else:
            # Non-zero margins: flush any pending stitch, then save this image
            self._flush_stitch()
            self._stitch_image = img.copy()

        self._last_image = img

    def _flush_stitch(self):
        if self._stitch_image is None:
            return

        import os

        filename = os.path.join(self.output_dir, f"print_{self._print_count:04d}.png")
        self._stitch_image.save(filename)
        logger.info(f"Saved printer output: {filename} ({self._stitch_image.width}x{self._stitch_image.height})")
        self._print_count += 1
        self._stitch_image = None

    def tick(self, frames):
        if self.time_remaining > 0:
            self.time_remaining -= frames
            if self.time_remaining <= 0:
                self.time_remaining = 0

    def get_image(self):
        return self._last_image

    def stop(self):
        self._flush_stitch()

    # def save_state(self, f):
    #     f.write(self.command_state)
    #     f.write(self.command_id)
    #     f.write(self.compression)
    #     f.write_16bit(self.length_left)
    #     f.write_16bit(self.command_length)
    #     f.write_16bit(self.checksum)
    #     f.write(self.status)
    #     f.write(self.byte_to_send)
    #     f.write_16bit(self.image_offset)
    #     f.write(self.print_margins)
    #     f.write(self.print_palette)
    #     f.write(self.print_exposure)
    #     f.write(self.compression_run_length)
    #     f.write(self.compression_run_is_compressed)
    #     for i in range(PRINTER_BUFFER_SIZE):
    #         f.write(self.image[i])
    #     for i in range(PRINTER_MAX_DATA):
    #         f.write(self.command_data[i])
    #     f.write_32bit(self.time_remaining)
    #     f.write_32bit(self._print_count)

    # def load_state(self, f, state_version):
    #     self.command_state = f.read()
    #     self.command_id = f.read()
    #     self.compression = f.read()
    #     self.length_left = f.read_16bit()
    #     self.command_length = f.read_16bit()
    #     self.checksum = f.read_16bit()
    #     self.status = f.read()
    #     self.byte_to_send = f.read()
    #     self.image_offset = f.read_16bit()
    #     self.print_margins = f.read()
    #     self.print_palette = f.read()
    #     self.print_exposure = f.read()
    #     self.compression_run_length = f.read()
    #     self.compression_run_is_compressed = f.read()
    #     for i in range(PRINTER_BUFFER_SIZE):
    #         self.image[i] = f.read()
    #     for i in range(PRINTER_MAX_DATA):
    #         self.command_data[i] = f.read()
    #     self.time_remaining = f.read_32bit()
    #     self._print_count = f.read_32bit()
