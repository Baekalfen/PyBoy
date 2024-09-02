import logging
import os
import platform
import queue
import socket
import sys
import threading
import time

import select
from colorama import Fore

import pyboy

logger = pyboy.logging.get_logger(__name__)

INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW = [1 << x for x in range(5)]
SERIAL_FREQ = 8192  # Hz
CPU_FREQ = 4194304  # Hz  # Corrected CPU Frequency

async_recv = queue.Queue()


class Serial:
    """Gameboy Link Cable Emulation"""

    def __init__(self, mb, serial_address, serial_bind, serial_interrupt_based):
        self.mb = mb
        self.SC = 0  # Serial transfer control
        self.SB = 0xFF  # Serial transfer data
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
        self.transfer_enabled = False

        if serial_bind:
            self.binding_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.binding_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logger.info(f"Binding to {serial_address}")
            self.binding_connection.bind(address_tuple)
            self.binding_connection.listen(1)
            self.connection, _ = self.binding_connection.accept()
            logger.info(f"Client has connected!")
            # Set as master
        else:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.info(f"Connecting to {serial_address}")
            self.connection.connect(address_tuple)
            logger.info(f"Connection successful!")
            self.is_master = False

    def send_bit(self):
        send_bit = bytes([(self.SB >> 7) & 1])
        print(f"send bit: {send_bit}")
        print("ST", self.connection.send(send_bit))

    def recv_bit(self):
        print("waiting for data")
        try:
            data = self.connection.recv(1)
            print(f"{Fore.YELLOW}{data}{Fore.RESET}")
            self.SB = ((self.SB << 1) & 0xFF) | data[0]
            return True
        except BlockingIOError:  # Currently unused
            print("Skipped")
            return False

    def tick(self):
        if self.connection is None:
            return False

        while True:
            if self.SC & 0x80 == 0:  # Check if transfer is enabled
                if self.transfer_enabled:
                    print(f"{Fore.RED}Transfer disabled{Fore.RESET}")
                    self.transfer_enabled = False
                continue

            if not self.transfer_enabled:
                print(f"{Fore.GREEN}Transfer enabled{Fore.RESET}")
                self.transfer_enabled = True

            self.cycles_count += 16  # Accumulate cycles

            if self.cycles_to_transmit() == 0:
                self.send_bit()
                time.sleep(1 / SERIAL_FREQ)

                rb = self.recv_bit()
                if not rb:
                    continue

                # logger.info(f"recv sb: {self.SB:08b}")
                self.trans_bits += 1

                self.cycles_count = 0  # Reset cycle count after transmission

                if self.trans_bits == 8:
                    self.trans_bits = 0
                    # Clear transfer start flag
                    self.SC = ((self.SC << 1) & 0xFF) | 0
                    logger.info(f"*SET SC: {self.SC:08b} ({hex(self.SC)})")
                    # time.sleep(1 / SERIAL_FREQ)
                    self.mb.cpu.set_interruptflag(INTR_SERIAL)
                    if self.is_master:
                        time.sleep(1 / SERIAL_FREQ)

    def cycles_to_transmit(self):
        if self.connection:
            if self.SC & 0x80:
                return max(self.cycles_target - self.cycles_count, 0)
            else:
                return 1 << 16
        else:
            return 1 << 16

    def stop(self):
        if self.connection:
            self.connection.close()
