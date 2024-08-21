import logging
import os
import platform
import queue
import socket
import sys
import threading
import time

import pyboy

logger = pyboy.logging.get_logger(__name__)

SERIAL_FREQ = 8192  # Hz
CPU_FREQ = 4194304  # Hz  # Corrected CPU Frequency

async_recv = queue.Queue()


def async_comms(socket):
    while True:
        item = socket.recv(1)
        async_recv.put(item)


class Serial:
    """Gameboy Link Cable Emulation"""

    def __init__(self, mb, serial_address, serial_bind, serial_interrupt_based):
        self.SB = 0  # Serial transfer data
        self.SC = 0  # Serial transfer control
        self.connection = None

        self.trans_bits = 0  # Number of bits transferred
        self.cycles_count = 0  # Number of cycles since last transfer
        self.cycles_target = CPU_FREQ // SERIAL_FREQ
        self.serial_interrupt_based = serial_interrupt_based

        if not serial_address:
            logger.info("No serial address supplied. Link Cable emulation disabled.")
            return

        if not serial_address.count(".") == 3 and serial_address.count(":") == 1:
            logger.info("Only IP-addresses of the format x.y.z.w:abcd is supported")
            return

        address_ip, address_port = serial_address.split(":")
        address_tuple = (address_ip, int(address_port))

        self.is_master = True

        if serial_bind:
            self.binding_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.binding_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logger.info(f"Binding to {serial_address}")
            self.binding_connection.bind(address_tuple)
            self.binding_connection.listen(1)
            self.connection, _ = self.binding_connection.accept()
            logger.info(f"Client has connected!")
            # Set as master
            self.SC = 1
        else:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.info(f"Connecting to {serial_address}")
            self.connection.connect(address_tuple)
            logger.info(f"Connection successful!")
            self.is_master = False
            self.SC = 0

        # self.connection.setblocking(False)
        # self.t = threading.Thread(target=async_comms, args=(self.connection,))
        # self.t.start()

    def tick(self, cycles):
        if self.connection is None:
            return False

        if self.SC & 0x80 == 0:  # Check if transfer is enabled
            return False

        self.cycles_count += cycles  # Accumulate cycles

        if self.cycles_to_transmit() == 0:
            send_bit = bytes([(self.SB >> 7) & 1])
            self.connection.send(send_bit)
            # time.sleep(1 / SERIAL_FREQ)  # Remove unnecessary sleep

            try:
                data = self.connection.recv(1)  # Receive data without timeout
                if data:
                    self.SB = ((self.SB << 1) & 0xFF) | data[0] & 1
                else:
                    return False  # Handle disconnection
            except BlockingIOError:
                return False  # No data available yet

            logger.info(f"recv sb: {self.SB:08b}")
            self.trans_bits += 1

            self.cycles_count = 0  # Reset cycle count after transmission

            if self.trans_bits == 8:
                self.trans_bits = 0
                self.SC &= 0b0111_1111  # Clear transfer start flag
                return True  # Indicate transfer complete
            return False
        return False

    def cycles_to_transmit(self):
        if self.connection:
            if self.SC & 0x80:
                return max(self.cycles_target - self.cycles_count, 0)
            else:
                return 1 << 16  # Large value to prevent transmission
        else:
            return 1 << 16

    def stop(self):
        if self.connection:
            self.connection.close()