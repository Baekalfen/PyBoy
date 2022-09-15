import logging
import os
import queue
import socket
import sys
import threading

logger = logging.getLogger(__name__)

SERIAL_FREQ = 8192 # Hz
CPU_FREQ = 4213440 # Hz

async_recv = queue.Queue()


def async_comms(socket):
    while True:
        item = socket.recv(1)
        async_recv.put(item)


class Serial:
    def __init__(self, serial_address, serial_bind, serial_interrupt_based):
        self.SB = 0
        self.SC = 0
        self.connection = None

        self.trans_bits = 0
        self.cycles_count = 0
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

        # if self.serial_interrupt_based:
        #     logger.info("Interrupt-based serial emulation active!")
        #     self.recv_thread = threading.Thread(target=async_comms, args=(self.connection,))
        #     self.recv_thread.start()

    def tick(self, cycles):
        if self.connection is None:
            return

        # self.cycles_count += 1

        if self.serial_interrupt_based:
            if self.SC & 0x80 == 0: # Performance optimization. Games might not set this on slave
                return False

            self.cycles_count += 1

            if (self.cycles_to_transmit() == 0):
                if self.SC & 1: # Master
                    if self.SC & 0x80:
                        logger.info(f"Master sending!")
                        self.connection.send(bytes([self.SB]))
                        data = self.connection.recv(1)
                        self.SB = data[0]
                        self.SC &= 0b0111_1111
                        self.cycles_count = 0
                        return True
                else:
                    # try:
                    #     data = async_recv.get(block=False)
                    # except queue.Empty:
                    #     return False
                    try:
                        data = self.connection.recv(1, socket.MSG_DONTWAIT)
                    except BlockingIOError:
                        return False

                    logger.info(f"Slave recv!")
                    self.connection.send(bytes([self.SB]))
                    # data = self.connection.recv(1)
                    self.SB = data[0]
                    self.SC &= 0b0111_1111
                    self.cycles_count = 0
                    return True
            return False
        else:
            # Check if serial is in progress
            if self.SC & 0x80 == 0:
                return False

            self.cycles_count += 1

            if (self.cycles_to_transmit() == 0):
                # if self.SC & 1: # Master
                send_bit = bytes([(self.SB >> 7) & 1])
                self.connection.send(send_bit)

                data = self.connection.recv(1)
                self.SB = ((self.SB << 1) & 0xFF) | data[0] & 1

                logger.info(f"recv sb: {self.SB:08b}")
                self.trans_bits += 1

                self.cycles_count = 0

                if self.trans_bits == 8:
                    self.trans_bits = 0
                    self.SC &= 0b0111_1111
                    return True
                return False
            return False

    def cycles_to_transmit(self):
        if self.connection:
            if self.SC & 0x80:
                return max(self.cycles_target - self.cycles_count, 0)
                # return CPU_FREQ // SERIAL_FREQ
            else:
                return 1 << 16
        else:
            return 1 << 16

    def stop(self):
        if self.connection:
            self.connection.close()
            # if self.serial_interrupt_based and self.recv_thread:
            #     self.recv_thread.kill()
