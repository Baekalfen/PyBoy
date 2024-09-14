import os
import platform
import queue
import select
import socket
import threading
import time

import pyboy

logger = pyboy.logging.get_logger(__name__)

INTR_VBLANK, INTR_LCDC, INTR_TIMER, INTR_SERIAL, INTR_HIGHTOLOW = [1 << x for x in range(5)]
SERIAL_FREQ = 8192 # Hz
CPU_FREQ = 4194304 # Hz  # Corrected CPU Frequency

async_recv = queue.Queue()


class Serial:
    """Gameboy Link Cable Emulation"""
    def __init__(self, mb, serial_address, serial_bind, serial_interrupt_based):
        self.mb = mb
        self.SC = 0b00000000 # Serial transfer control
        self.SB = 0b00000000 # Serial transfer data
        self.connection = None

        self.trans_bits = 0 # Number of bits transferred
        self.cycles_count = 0 # Number of cycles since last transfer
        self.cycles_target = CPU_FREQ // SERIAL_FREQ
        self.serial_interrupt_based = serial_interrupt_based

        self.recv = queue.Queue()

        self.quitting = False

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
        self.waiting_for_byte = False
        self.byte_retry_count = 0

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
            self.is_master = False
        self.connection.setblocking(False)
        self.recv_t = threading.Thread(target=lambda: self.recv_thread())
        self.recv_t.daemon = True
        self.recv_t.start()

    def recv_thread(self):
        while not self.quitting:
            try:
                data = self.connection.recv(1)
                self.recv.put(data)
            except BlockingIOError as e:
                pass
            except ConnectionResetError as e:
                print(f"Connection reset by peer: {e}")
                break

    def send_bit(self):
        send_bit = bytes([(self.SB >> 7) & 1])
        try:
            self.connection.send(send_bit)
        except ConnectionResetError:
            self.SB = 0xFF

    def tick(self, cycles):
        if self.connection is None:
            # No connection, no serial
            self.SB = 0xFF
            return False

        if self.SC & 0x80 == 0: # Check if transfer is enabled
            return False

        self.cycles_count += cycles # Accumulate cycles

        if self.cycles_to_transmit() == 0:
            if not self.waiting_for_byte:
                self.send_bit()
            time.sleep(1 / SERIAL_FREQ)

            try:
                rb = self.recv.get_nowait()
                self.waiting_for_byte = False
                self.byte_retry_count = 0
                self.trans_bits += 1
            except queue.Empty as e:
                # This part prevents indefinite lockup
                # while waiting for bytes
                self.waiting_for_byte = True
                self.byte_retry_count += 1
                if self.byte_retry_count >= 8:
                    self.byte_retry_count = 0
                    self.cycles_count = 0 # Reset cycles
                return False
            self.SB = ((self.SB << 1) & 0xFF) | rb[0]

            self.cycles_count = 0 # Reset cycle count after transmission

            if self.trans_bits == 8:
                self.trans_bits = 0
                # Clear transfer start flag
                self.SC &= 0x7F
                return True
        return False

    def cycles_to_transmit(self):
        if self.connection:
            if self.SC & 0x80:
                return max(self.cycles_target - self.cycles_count, 0)
            else:
                return 1 << 16
        else:
            return 1 << 16

    def stop(self):
        self.quitting = True
        if self.connection:
            self.connection.close()
        if hasattr(self, "binding_connection"):
            self.binding_connection.close()
        self.connection = None
        self.binding_connection = None
        self.recv_t.join()
