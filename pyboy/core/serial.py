#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import time
import socket
import pyboy
from pyboy.utils import MAX_CYCLES
import queue

logger = pyboy.logging.get_logger(__name__)

try:
    import cython
except ImportError:

    class _mock:
        def __enter__(self):
            pass

        def __exit__(self, *args):
            pass

    exec(
        """
class cython:
    gil = _mock()
    nogil = _mock()
""",
        globals(),
        locals(),
    )


CYCLES_8192HZ = 128

async_recv = queue.Queue()


def async_comms(socket):
    while True:
        item = socket.recv(1)
        async_recv.put(item)


SENDING, RECEIVING, PASSIVE = 0, 1, 2


class Serial:
    def __init__(self, serial_address, serial_bind, serial_interrupt_based):
        self.SB = 0xFF  # Always 0xFF for a disconnected link cable
        self.SC = 0
        self.transfer_enabled = 0
        self.is_master = False
        self.internal_clock = 0
        self._cycles_to_interrupt = 0
        self.last_cycles = 0
        self.clock = 0
        self.clock_target = MAX_CYCLES

        self.serial_connected = False
        self.connection = None
        self.sending_state = PASSIVE

        self.trans_bits = 0
        self.serial_interrupt_based = serial_interrupt_based

        self.all_data = {"send": [], "recv": []}

        logger.debug("Serial starts: %s, %d, %d", serial_address, serial_bind, serial_interrupt_based)

        if not serial_address:
            logger.debug("No serial address supplied. Link Cable emulated as disconnected.")
            return

        if not serial_address.count(".") == 3 and serial_address.count(":") == 1:
            logger.error("Only IP-addresses of the format x.y.z.w:abcd is supported")
            return

        address_ip, address_port = serial_address.split(":")
        address_tuple = (address_ip, int(address_port))

        self.binding_connection = None
        if serial_bind:
            self.binding_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.binding_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logger.debug(f"Binding to {serial_address}")
            self.binding_connection.bind(address_tuple)
            self.binding_connection.listen(1)
            self.connection, _ = self.binding_connection.accept()
            logger.debug("Client has connected!")
        else:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            for _ in range(10):
                logger.debug(f"Connecting to {serial_address}")
                try:
                    self.connection.connect(address_tuple)
                    break
                except ConnectionRefusedError:
                    time.sleep(1)
                except OSError:
                    time.sleep(1)

            logger.debug("Connection successful!")

        self.serial_connected = self.connection is not None
        # if self.serial_interrupt_based:
        #     logger.debug("Interrupt-based serial emulation active!")
        #     self.recv_thread = threading.Thread(target=async_comms, args=(self.connection,))
        #     self.recv_thread.start()

    def set_SB(self, value):
        # if not value == self.SB:
        #     logger.debug(("Master " if self.is_master else "Slave ") + "Write SB: %02x", value)
        # logger.debug("SB set %02x", value)
        if not self.serial_connected:
            # Always 0xFF when cable is disconnected. Connecting is not implemented yet.
            self.SB = 0xFF
        else:
            self.SB = value

    def set_SC(self, value):  # cgb, double_speed
        # logger.debug(("Master " if self.is_master else "Slave ") + "Write SC: %02x", value)
        self.SC = value
        self.transfer_enabled = self.SC & 0x80
        self.is_master = self.SC & 1
        if self.is_master:
            self.sending_state = SENDING
        else:
            self.sending_state = RECEIVING
        # logger.debug("SC set %02x, %s", value, self.transfer_enabled)
        # TODO:
        # if cgb and (self.SC & 0b10): # High speed transfer
        #     self.double_speed = ...
        self.internal_clock = self.SC & 1  # 0: external, 1: internal
        if not self.serial_connected:
            if self.internal_clock:
                self.clock_target = self.clock + 8 * CYCLES_8192HZ
            else:
                # Will never complete, as there is no connection
                self.transfer_enabled = 0  # Technically it is enabled, but no reason to track it.
                self.clock_target = MAX_CYCLES
        else:
            # If connected then immediate send data
            self.clock_target = self.clock
        self._cycles_to_interrupt = self.clock_target - self.clock

    def tick(self, _cycles):
        cycles = _cycles - self.last_cycles
        if cycles == 0:
            return False
        self.last_cycles = _cycles

        self.clock += cycles

        interrupt = False
        if self.transfer_enabled:
            if not self.serial_connected:
                if self.clock >= self.clock_target:
                    # Disconnected emulation
                    self.SC &= 0x80
                    self.transfer_enabled = 0
                    self.clock_target = MAX_CYCLES
                    interrupt = True
            elif self.serial_interrupt_based:  # Connected emulation
                self.clock_target = MAX_CYCLES  # interrupt-based serial has no timing, just asap
                # TODO: SB-read-write based transfers? Schedule interrupt, but don't transfer before SB is read. Transfer whatever is needed and resync both.
                with cython.gil:
                    try:
                        if self.is_master:
                            if self.SC & 0x80:
                                if self.sending_state == SENDING:
                                    # logger.debug("Master sending!")
                                    self.connection.send(bytes([self.SB]))
                                    self.all_data["send"].append(self.SB)
                                    self.sending_state = RECEIVING
                                    logger.debug("Master byte sent: %02x", self.SB)
                                    self.clock_target = 0
                                elif self.sending_state == RECEIVING:
                                    try:
                                        data = self.connection.recv(
                                            1, socket.MSG_DONTWAIT
                                        )  # TODO: Timeout if the other side disconnects
                                        if len(data) > 0:
                                            self.SB = data[0]
                                            self.all_data["recv"].append(self.SB)
                                            logger.debug("Master byte received: %02x", self.SB)
                                            self.SC &= 0b0111_1111
                                            interrupt = True
                                            self.sending_state = PASSIVE
                                            self.clock_target = MAX_CYCLES
                                        else:
                                            logger.error("Master disconnect!")
                                            self.disconnect()
                                    except BlockingIOError:
                                        pass
                            # else:
                            #     self.clock_target = self.clock + 8 * CYCLES_8192HZ
                        else:
                            if self.sending_state == SENDING:
                                self.connection.send(bytes([self.SB]))
                                self.all_data["send"].append(self.SB)
                                logger.debug("Slave byte sent: %02x", self.SB)
                                # data = self.connection.recv(1)
                                self.SB = self.SB_latched
                                self.SC &= 0b0111_1111
                                interrupt = True
                                self.sending_state = PASSIVE
                                self.clock_target = MAX_CYCLES
                            elif self.sending_state == RECEIVING:
                                try:
                                    data = self.connection.recv(1, socket.MSG_DONTWAIT)
                                    if len(data) > 0:
                                        self.SB_latched = data[0]
                                        logger.debug("Slave recv! %02x", self.SB_latched)
                                        self.all_data["recv"].append(self.SB_latched)
                                        self.sending_state = SENDING
                                        self.clock_target = 0
                                    else:
                                        logger.error("Slave disconnect!")
                                        self.disconnect()
                                except BlockingIOError:
                                    # logger.debug("Slave no data!")
                                    # self.clock_target = self.clock + 8 * CYCLES_8192HZ
                                    pass
                    except (ConnectionResetError, BrokenPipeError) as ex:
                        logger.error(("Master " if self.is_master else "Slave ") + "Exception in serial tick: %s", ex)
                        self.disconnect()
            else:
                raise Exception(("Master " if self.is_master else "Slave ") + "Invalid mode")

        self._cycles_to_interrupt = self.clock_target - self.clock
        return interrupt

        # Clock based serial:
        # else:
        #     exit(2)
        #     # if self.SC & 1: # Master
        #     send_bit = bytes([(self.SB >> 7) & 1])
        #     self.connection.send(send_bit)

        #     data = self.connection.recv(1)
        #     self.SB = ((self.SB << 1) & 0xFF) | data[0] & 1

        #     logger.debug(f"recv sb: {self.SB:08b}")
        #     self.trans_bits += 1

        #     if self.trans_bits == 8:
        #         self.trans_bits = 0
        #         self.SC &= 0b0111_1111
        #         interrupt = True

        #     self.clock_target = self.clock + CYCLES_8192HZ

    def save_state(self, f):
        f.write(self.SB)
        f.write(self.SC)
        f.write(self.transfer_enabled)
        f.write(self.is_master)
        f.write(self.internal_clock)
        f.write_64bit(self.last_cycles)
        f.write_64bit(self._cycles_to_interrupt)
        f.write_64bit(self.clock)
        f.write_64bit(self.clock_target)

    def load_state(self, f, state_version):
        self.SB = f.read()
        self.SC = f.read()
        self.transfer_enabled = f.read()
        self.is_master = f.read()
        self.internal_clock = f.read()
        self.last_cycles = f.read_64bit()
        self._cycles_to_interrupt = f.read_64bit()
        self.clock = f.read_64bit()
        self.clock_target = f.read_64bit()

    def disconnect(self):
        logger.debug("DISCONNECTING")
        with cython.gil:
            if self.serial_connected:
                if self.connection:
                    self.connection.close()
                if self.binding_connection:
                    self.binding_connection.close()
            # if self.serial_interrupt_based and self.recv_thread:
            #     self.recv_thread.kill()

        self.sending_state = PASSIVE
        self.serial_connected = False
        self.SB = 0xFF
        self.clock_target = MAX_CYCLES

    def stop(self):
        from pprint import pprint as pp

        pp(self.all_data)
        if hasattr(self, "binding_connection") and self.binding_connection is not None:
            with open("master_recv.bin", "wb") as f:
                f.write(bytes(self.all_data["recv"]))
            with open("master_send.bin", "wb") as f:
                f.write(bytes(self.all_data["send"]))
        else:
            with open("slave_recv.bin", "wb") as f:
                f.write(bytes(self.all_data["recv"]))
            with open("slave_send.bin", "wb") as f:
                f.write(bytes(self.all_data["send"]))
        self.disconnect()
