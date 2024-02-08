#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import fcntl
import os
import re
import socket

import pyboy
from pyboy.plugins.base_plugin import PyBoyPlugin
from pyboy.utils import WindowEvent

logger = pyboy.logging.get_logger(__name__)

####################################################
#
# A big Thank You to "chciken" for the extraordinary work of writing
# a blog post on exactly this topic:
#
# https://www.chciken.com/tlmboy/2022/04/03/gdb-z80.html
#
####################################################


class GdbServer(PyBoyPlugin):
    argv = [(
        "--gdbserver", {
            "nargs": "?",
            "default": None,
            "const": "127.0.0.1:1234",
            "type": str,
            "help": "Spawn GDB Server for debugging"
        }
    )]

    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TODO: Argv ip, port
        address, port = pyboy_argv.get("gdbserver").split(":", 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # fcntl.fcntl(self.sock, fcntl.F_SETFL, os.O_NONBLOCK)
        self.sock.bind((address, int(port)))
        self.sock.listen(1)
        logger.critical("Waiting for GDB client to connect on %s...", self.pyboy_argv.get("gdbserver"))
        (self.client_socket, self.client_address) = self.sock.accept()
        self.buffer = b""
        # self.pyboy._pause()
        self.freeze = True
        self.client_socket.setblocking(False)
        self._message_handler()

    def enabled(self):
        return self.pyboy_argv.get("gdbserver")

    def _gdb_checksum(self, data):
        return sum(data) & 0xff

    def _gdb_send(self, data):
        msg = b"$" + data + b"#" + f"{self._gdb_checksum(data):02x}".encode()
        logger.debug("Sending message: %s", msg)
        self.client_socket.send(msg)

    def _gdb_ack(self):
        logger.debug("Sending ack")
        self.client_socket.send(b"+")

    re_ack = b"([\+\-])"
    re_command = b"\$(.*?)#([0-9a-fA-F]+)"
    re_signal = b"([\x01\x02\x03\x04\x05\x06\x07\x08\x09])"

    def _gdb_recv_packages(self):
        logger.debug("Receiving data...")
        try:
            data = self.client_socket.recv(4096)
        except BlockingIOError:
            return []

        if data:
            logger.debug("Received data: %s", data)

        self.buffer += data

        matches = []
        while True:
            for t, r in [("ack", self.re_ack), ("cmd", self.re_command), ("sig", self.re_signal)]:
                m = re.match(b"^" + r, self.buffer)

                if not m:
                    continue

                matches.append((t, m.groups()))

                # Consume used part of buffer
                self.buffer = self.buffer[m.span()[1]:]
            else:
                # No more matches to make, break out of while
                break

        return matches

    def _format_little_endian(self, _in):
        return b"".join(f"{x:02X}".encode() for x in bytearray.fromhex(f"{_in:04X}")[::-1])

    def post_tick(self):
        self._message_handler()

    def _message_handler(self):
        while True:
            for _type, contents in self._gdb_recv_packages():
                if _type == "ack":
                    logger.debug("Received Ack: %s", contents)
                elif _type == "sig":
                    logger.info("Sig: %s", contents)
                    self._gdb_ack()
                    # self.pyboy._pause()
                    self.freeze = True
                    # self._gdb_send(b"OK")
                    self._gdb_send(b"S05")
                elif _type == "cmd":
                    logger.debug("Command: %s", contents)
                    body, checksum = contents
                    logger.info("Received message: %s", body.decode())
                    if not self._gdb_checksum(body) == int(checksum, 16):
                        logger.critical("Checksum on package failed: %s", contents)
                        exit(1)

                    self._gdb_ack()

                    # Command...
                    # \$(.*?)#([0-9a-fA-F]+)

                    if body.startswith(b"qSupported"):
                        # _, _sub_bodies = body.split(b':', 1)
                        # sub_bodies = _sub_bodies.split(b';')
                        # self._gdb_send(b"swbreak+;") # vContSupported+;
                        self._gdb_send(b"hwbreak+;")
                    elif body == b"vMustReplyEmpty":
                        self._gdb_send(b"")
                    elif body.startswith(b"Hg"):
                        self._gdb_send(b"")
                    elif body == b"qTStatus":
                        self._gdb_send(b"")
                    elif body == b"qfThreadInfo":
                        self._gdb_send(b"")
                    elif body == b"qL1160000000000000000":
                        self._gdb_send(b"")
                    elif body == b"qL1200000000000000000":
                        self._gdb_send(b"")
                    elif body == b"Hc-1" or body == b"Hc0":
                        self._gdb_send(b"")
                    elif body == b"qC":
                        self._gdb_send(b"")
                    elif body == b"?":
                        # Reason for pausing
                        self._gdb_send(b"S05")
                    elif body == b"qAttached":
                        # Keep alive after GDB closes?
                        self._gdb_send(b"0")
                    elif body == b"c":
                        self.freeze = False
                        # self.pyboy._unpause()
                    elif body == b"g":
                        # Registers as 16-bit little endian padded with x to number of registers in Z80
                        # AF, BC, DE, HL, SP, PC
                        msg = (
                            f"{self.pyboy.mb.cpu.F:02x}"
                            f"{self.pyboy.mb.cpu.A:02x}"
                            f"{self.pyboy.mb.cpu.C:02x}"
                            f"{self.pyboy.mb.cpu.B:02x}"
                            f"{self.pyboy.mb.cpu.E:02x}"
                            f"{self.pyboy.mb.cpu.D:02x}"
                        ).encode()

                        msg += ( \
                            self._format_little_endian(self.pyboy.mb.cpu.HL) + \
                            self._format_little_endian(self.pyboy.mb.cpu.SP) + \
                            self._format_little_endian(self.pyboy.mb.cpu.PC) \
                        )

                        msg += b"xx" * 14

                        self._gdb_send(msg)
                    elif body.startswith(b"m"):
                        # Memory
                        _addr, _length = body[1:].split(b",", 1)
                        addr = int(_addr, 16)
                        length = int(_length, 16)
                        if addr > 0xFFFF:
                            self._gdb_send(b"E 01")
                        else:
                            # From GDB docs:
                            # "The reply may contain fewer addressable memory units than requested if the server was able
                            # to read only part of the region of memory."
                            self._gdb_send(
                                "".join(
                                    f"{self.pyboy.get_memory_value(a):02x}"
                                    for a in range(addr, min(addr + length, 0x10000))
                                ).encode()
                            )
                    elif body.startswith(b"Z"):
                        # Add breakpoint
                        _type, _addr, kind = body.split(b",", 2)
                        addr = int(_addr, 16)
                        bank = -1
                        self.pyboy.mb.breakpoint_add(bank, addr)
                        self._gdb_send(b"OK")
                    elif body.startswith(b"z"):
                        # Remove breakpoint
                        _type, _addr, kind = body.split(b",", 2)
                        addr = int(_addr, 16)
                        bank = -1
                        brk_index = self.pyboy.mb.breakpoint_find(bank, addr)
                        if brk_index < 0:
                            breakpoint()
                            self._gdb_send(b"E 01")
                        else:
                            self.pyboy.mb.breakpoint_remove(brk_index)
                            self._gdb_send(b"OK")
                    elif body.startswith(b"vCont?"):
                        # self.pyboy._unpause()
                        # self.pyboy.mb.breakpoint_singlestep = 0
                        # self.freeze = False
                        # self.pyboy.mb.breakpoint_singlestep_latch = 0
                        self._gdb_send(b"vCont;c;s;t")
                        # return True
                    elif body.startswith(b"vCont"):
                        # self.pyboy._unpause()
                        # self.pyboy.mb.breakpoint_singlestep = 0
                        self.freeze = False
                        self.pyboy.mb.breakpoint_singlestep_latch = 0
                        self._gdb_send(b"OK")
                        # return True
                    # elif body == b"vContC":
                    #     # self.pyboy._pause()
                    #     self.freeze = True
                    #     self._gdb_send(b"OK")
                    elif body.startswith(b"vKill"):
                        self.pyboy.stop()
                        self._gdb_send(b"OK")
                    elif body == b"qSymbol::":
                        self._gdb_send(b"OK")
                        # return True
                    else:
                        breakpoint()
                else:
                    breakpoint()

            if not self.freeze:
                break

    def handle_breakpoint(self):
        # if not self.pyboy.paused:
        logger.critical(
            f"GDB server handle_breakpoint HL: {self.pyboy.mb.cpu.HL:04X}, SP: {self.pyboy.mb.cpu.SP:04X}, PC: {self.pyboy.mb.cpu.PC:04X}"
        )
        # self.pyboy._pause()
        self._gdb_send(b"S05")

        # self.client_socket.setblocking(True)
        self.freeze = True
        self._message_handler()

        # breakpoint()
        pass
