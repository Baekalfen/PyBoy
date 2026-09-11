#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from array import array

import pyboy
from pyboy.plugins.base_plugin import PyBoyPlugin
from pyboy.core import serial
from pyboy.core.serial_printer import SerialPrinter


logger = pyboy.logging.get_logger(__name__)


# Printer commands
PRINTER_DATA = 0x04
PRINTER_INIT = 0x01
PRINTER_PRINT = 0x02
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

    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)
        self.output_dir = pyboy_argv.get("printer_output") or "."

        self.__set_mb_serial()

    def __set_mb_serial(self):
        self._enabled = bool(self.pyboy_argv.get("printer")) and type(self.mb.serial) is serial.Serial
        if self._enabled:
            self.mb.serial = SerialPrinter(self.mb.cgb_mode, self)
            self._initialize()

    def _initialize(self):
        # State machine
        self.command_state = MAGIC1
        self.command_id = 0
        self.compression_enabled = 0
        self.bytes_remaining = 0
        self.data_length = 0
        self.checksum = 0
        self.status = 0
        self.response_byte = 0

        # Command data buffer
        self.command_data = array("B", [0] * PRINTER_MAX_DATA)
        self.command_data_view = self.command_data

        # Image buffer (1 byte per pixel, value 0-3)
        self.image = array("B", [0] * PRINTER_BUFFER_SIZE)
        self.image_view = self.image
        self.image_offset = 0

        # Compression state
        self.run_length = 0
        self.run_compressed = 0

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
        self.image_pending = 0

    def enabled(self):
        return self._enabled

    def post_tick(self):
        if self.image_pending:
            self._flush_pending_image()
            self.image_pending = 0

    def process_byte(self, value):
        self.process_byte_nogil(value)
        if self.image_pending:
            self._flush_pending_image()
            self.image_pending = 0

    def process_byte_nogil(self, value):
        self.response_byte = 0

        if self.command_state <= LENGTH_MSB:
            if self._consume_header(value):
                return
        elif self.command_state == DATA:
            self._consume_data(value)
        elif self.command_state <= CHECKSUM_MSB:
            if self._consume_checksum(value):
                return
        elif self.command_state == ALIVE:
            self._consume_alive()
        elif self.command_state == STATUS:
            self.command_state = MAGIC1
            self._apply_command_nogil()
            return

        # Accumulate checksum for bytes from COMMAND through DATA
        if self.command_state >= COMMAND and self.command_state < CHECKSUM_LSB:
            self.checksum = (self.checksum + value) & 0xFFFF

        # Advance state
        if self.command_state != DATA:
            self.command_state += 1

        # Skip DATA state if no data
        if self.command_state == DATA:
            if self.bytes_remaining == 0:
                self.command_state += 1

    def _consume_header(self, value):
        if self.command_state == MAGIC1:
            if value != 0x88:
                return 1
            self.status &= ~1
            self.data_length = 0
            self.checksum = 0
        elif self.command_state == MAGIC2:
            if value == 0x33:
                pass
            elif value == 0x88:
                return 1
            else:
                self.command_state = MAGIC1
                return 1
        elif self.command_state == COMMAND:
            self.command_id = value & 0xF
        elif self.command_state == COMPRESSION:
            self.compression_enabled = value & 1
        elif self.command_state == LENGTH_LSB:
            self.bytes_remaining = value
        else:
            self.bytes_remaining |= (value & 0x3) << 8
        return 0

    def _consume_data(self, value):
        if self.data_length < PRINTER_MAX_DATA:
            if self.compression_enabled:
                self._decompress_byte(value)
            else:
                self.command_data_view[self.data_length] = value
                self.data_length += 1
        self.bytes_remaining -= 1

    def _consume_checksum(self, value):
        if self.command_state == CHECKSUM_LSB:
            self.checksum ^= value
            return 0

        self.checksum ^= value << 8
        if self.checksum:
            self.status |= 1
            self.command_state = MAGIC1
            return 1
        self.response_byte = 0x81
        return 0

    def _consume_alive(self):
        if self.command_id == PRINTER_INIT:
            self.response_byte = 0
            return
        if self.status == 6 and self.time_remaining == 0:
            self.status = 4
        self.response_byte = self.status

    def _decompress_byte(self, value):
        if self.run_length == 0:
            self.run_compressed = value & 0x80
            self.run_length = (value & 0x7F) + 1 + self.run_compressed
        elif self.run_compressed:
            while self.run_length:
                if self.data_length < PRINTER_MAX_DATA:
                    self.command_data_view[self.data_length] = value
                    self.data_length += 1
                self.run_length -= 1
                if self.data_length >= PRINTER_MAX_DATA:
                    self.run_length = 0
                    break
        else:
            if self.data_length < PRINTER_MAX_DATA:
                self.command_data_view[self.data_length] = value
                self.data_length += 1
            self.run_length -= 1

    def _apply_command_nogil(self):
        if self.command_id == PRINTER_DATA:
            if self.data_length == PRINTER_MAX_DATA:
                self.image_offset %= PRINTER_BUFFER_SIZE
                self.status = 8  # Unprocessed data

                data_index = 0
                for row_group in range(2):  # 2 rows of 8 pixels
                    for tile_x in range(PRINTER_WIDTH // 8):
                        for y in range(8):
                            low_byte = self.command_data_view[data_index]
                            high_byte = self.command_data_view[data_index + 1]
                            data_index += 2
                            for pixel_x in range(8):
                                pixel = ((low_byte >> 7) & 1) | (((high_byte >> 7) & 1) << 1)
                                low_byte <<= 1
                                high_byte <<= 1
                                image_index = self.image_offset + tile_x * 8 + pixel_x + y * PRINTER_WIDTH
                                if image_index < PRINTER_BUFFER_SIZE:
                                    self.image_view[image_index] = pixel

                    self.image_offset += 8 * PRINTER_WIDTH
        elif self.command_id == PRINTER_INIT:
            self.status = 0
            self.image_offset = 0
        elif self.command_id == PRINTER_PRINT:
            if self.data_length == 4:
                self.status = 6  # Printing
                self.print_margins = self.command_data_view[1]
                self.print_palette = self.command_data_view[2]
                self.print_exposure = self.command_data_view[3] & 0x7F

                # Instant printing: time_remaining set to 0 so status transitions
                # to 4 (done) on the next status poll. Real hardware takes time,
                # but games poll until done and instant works in practice.
                self.time_remaining = 0
                self.image_pending = 1
        # STATUS (0x0F) is a NOP, just returns status

    def _flush_pending_image(self):
        if self.image_pending:
            try:
                self._decode_image()
            except Exception:
                logger.exception("Failed to save printer image")
            self.image_offset = 0

    def _decode_image(self):
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
        for pixel_index in range(self.image_offset):
            shade = (self.print_palette >> (self.image_view[pixel_index] * 2)) & 3
            r, g, b = colors[shade]
            pixels[pixel_index * 3] = r
            pixels[pixel_index * 3 + 1] = g
            pixels[pixel_index * 3 + 2] = b

        image = Image.frombytes("RGB", (PRINTER_WIDTH, height), bytes(pixels))

        # Continuous printing: stitch when no margin rows are requested
        margin_flags = self.print_margins
        leading_blank_rows = (margin_flags >> 4) & 0xF
        trailing_blank_rows = margin_flags & 0xF

        if leading_blank_rows == 0 and trailing_blank_rows == 0 and self._stitch_image is not None:
            # Append to existing stitched image
            new_height = self._stitch_image.height + height
            stitched = Image.new("RGB", (PRINTER_WIDTH, new_height))
            stitched.paste(self._stitch_image, (0, 0))
            stitched.paste(image, (0, self._stitch_image.height))
            self._stitch_image = stitched
        elif leading_blank_rows == 0 and trailing_blank_rows == 0:
            # Start new stitched image
            self._stitch_image = image.copy()
        else:
            # Flush any pending stitch before saving an image with margin rows
            self._flush_stitch()
            self._stitch_image = image.copy()

        self._last_image = image

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
