#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import socket
import logging
from pyboy.utils import MAX_CYCLES

logger = logging.getLogger(__name__)

CYCLES_8192HZ = 128


class Serial:
    def __init__(self, serial_address, serial_bind, serial_interrupt_based=True):
        self.SB = 0xFF  # Always 0xFF for a disconnected link cable
        self.SC = 0
        self.transfer_enabled = 0
        self.internal_clock = 0
        self._cycles_to_interrupt = 0
        self.last_cycles = 0
        self.clock = 0
        self.clock_target = MAX_CYCLES

        self.connection = None

        self.trans_bits = 0
        self.serial_interrupt_based = serial_interrupt_based

        if not serial_address:
            logger.info("No serial address supplied. Link Cable emulated as disconnected.")
            return

        if not serial_address.count(".") == 3 and serial_address.count(":") == 1:
            logger.info("Only IP-addresses of the format x.y.z.w:abcd is supported")
            return

        address_ip, address_port = serial_address.split(":")
        address_tuple = (address_ip, int(address_port))

        if serial_bind:
            self.binding_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.binding_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logger.info(f"Binding to {serial_address}")
            self.binding_connection.bind(address_tuple)
            self.binding_connection.listen(1)
            self.connection, _ = self.binding_connection.accept()
            logger.info(f"Client has connected!")
        else:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.info(f"Connecting to {serial_address}")
            self.connection.connect(address_tuple)
            logger.info(f"Connection successful!")
        # self.connection.setblocking(False)

    def set_SB(self, value):
        # Always 0xFF when cable is disconnected. Connecting is not implemented yet.
        self.SB = 0xFF

    def set_SC(self, value):  # cgb, double_speed
        self.SC = value
        self.transfer_enabled = self.SC & 0x80
        # TODO:
        # if cgb and (self.SC & 0b10): # High speed transfer
        #     self.double_speed = ...
        self.internal_clock = self.SC & 1  # 0: external, 1: internal
        if self.internal_clock:
            self.clock_target = self.clock + 8 * CYCLES_8192HZ
        else:
            # Will never complete, as there is no connection
            self.transfer_enabled = 0  # Technically it is enabled, but no reason to track it.
            self.clock_target = MAX_CYCLES
        self._cycles_to_interrupt = self.clock_target - self.clock

    def tick(self, _cycles):
        cycles = _cycles - self.last_cycles
        if cycles == 0:
            return False
        self.last_cycles = _cycles

        self.clock += cycles

        interrupt = False
        if self.transfer_enabled:
            if self.connection is None:
                # Disconnected emulation
                if self.clock >= self.clock_target:
                    self.SC &= 0x80
                    self.transfer_enabled = 0
                    # self._cycles_to_interrupt = MAX_CYCLES
                    self.clock_target = MAX_CYCLES
                    interrupt = True
            else:
                # Connected emulation
                if self.clock >= self.clock_target:
                    # if self.SC & 1: # Master
                    send_bit = bytes([(self.SB >> 7) & 1])
                    self.connection.send(send_bit)

                    data = self.connection.recv(1)
                    self.SB = ((self.SB << 1) & 0xFF) | data[0] & 1

                    logger.info(f"recv sb: {self.SB:08b}")
                    self.trans_bits += 1

                    if self.trans_bits == 8:
                        self.trans_bits = 0
                        self.SC &= 0b0111_1111
                        return True
                    return False

        self._cycles_to_interrupt = self.clock_target - self.clock
        return interrupt

    # if self.serial_interrupt_based:
        #     if self.SC & 1: # Master
        #         if self.SC & 0x80:
        #             logger.info(f'Master sending!')
        #             self.connection.send(bytes([self.SB]))
        #             # self.connection.setblocking(True)
        #             data = self.connection.recv(1)
        #             self.SB = data[0]
        #             self.SC &= 0b0111_1111
        #             return True
        #     else:
        #         try:
        #             if self.SC & 0x80:
        #                 # self.connection.setblocking(False)
        #                 logger.info(f'Slave recv!')
        #                 self.connection.send(bytes([self.SB]))
        #                 data = self.connection.recv(1)
        #                 self.SB = data[0]
        #                 self.SC &= 0b0111_1111
        #                 return True
        #         except BlockingIOError:
        #             pass
        #     return False
        # return False
        # else:
        # Check if serial is in progress

    def save_state(self, f):
        f.write(self.SB)
        f.write(self.SC)
        f.write(self.transfer_enabled)
        f.write(self.internal_clock)
        f.write_64bit(self.last_cycles)
        f.write_64bit(self._cycles_to_interrupt)
        f.write_64bit(self.clock)
        f.write_64bit(self.clock_target)

    def load_state(self, f, state_version):
        self.SB = f.read()
        self.SC = f.read()
        self.transfer_enabled = f.read()
        self.internal_clock = f.read()
        self.last_cycles = f.read_64bit()
        self._cycles_to_interrupt = f.read_64bit()
        self.clock = f.read_64bit()
        self.clock_target = f.read_64bit()


    def stop(self):
        if self.connection:
            self.connection.close()
