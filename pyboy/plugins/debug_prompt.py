#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import os
import re

import pyboy
from pyboy.plugins.base_plugin import PyBoyPlugin
from pyboy.utils import WindowEvent

logger = pyboy.logging.get_logger(__name__)


class DebugPrompt(PyBoyPlugin):
    argv = [("--breakpoints", {"type": str, "help": "Add breakpoints on start-up (internal use)"})]

    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        self.rom_symbols = {}
        if pyboy_argv.get("ROM"):
            gamerom_file_no_ext, rom_ext = os.path.splitext(pyboy_argv.get("ROM"))
            for sym_ext in [".sym", rom_ext + ".sym"]:
                sym_path = gamerom_file_no_ext + sym_ext
                if os.path.isfile(sym_path):
                    with open(sym_path) as f:
                        for _line in f.readlines():
                            line = _line.strip()
                            if line == "":
                                continue
                            elif line.startswith(";"):
                                continue
                            elif line.startswith("["):
                                # Start of key group
                                # [labels]
                                # [definitions]
                                continue

                            try:
                                bank, addr, sym_label = re.split(":| ", line.strip())
                                bank = int(bank, 16)
                                addr = int(addr, 16)
                                if not bank in self.rom_symbols:
                                    self.rom_symbols[bank] = {}

                                self.rom_symbols[bank][addr] = sym_label
                            except ValueError as ex:
                                logger.warning("Skipping .sym line: %s", line.strip())

        for _b in (self.pyboy_argv.get("breakpoints") or "").split(","):
            b = _b.strip()
            if b == "":
                continue

            bank, addr = self.parse_bank_addr_sym_label(b)
            if bank is None or addr is None:
                logger.error("Couldn't parse address or label: %s", b)
                pass
            else:
                self.mb.breakpoint_add(bank, addr)
                logger.info("Added breakpoint for address or label: %s", b)

    def enabled(self):
        return self.pyboy_argv.get("breakpoints")

    def parse_bank_addr_sym_label(self, command):
        if ":" in command:
            bank, addr = command.split(":")
            bank = int(bank, 16)
            addr = int(addr, 16)
            return bank, addr
        else:
            for bank, addresses in self.rom_symbols.items():
                for addr, label in addresses.items():
                    if label == command:
                        return bank, addr
        return None, None

    def handle_breakpoint(self):
        while True:
            self.pyboy.plugin_manager.post_tick()

            # Get symbol
            if self.mb.cpu.PC < 0x4000:
                bank = 0
            else:
                bank = self.mb.cartridge.rombank_selected
            sym_label = self.rom_symbols.get(bank, {}).get(self.mb.cpu.PC, "")

            # Print state
            print(self.mb.cpu.dump_state(sym_label))

            # REPL
            cmd = input()
            # breakpoint()
            if cmd == "c" or cmd.startswith("c "):
                # continue
                if cmd.startswith("c "):
                    _, command = cmd.split(" ", 1)
                    bank, addr = self.parse_bank_addr_sym_label(command)
                    if bank is None or addr is None:
                        print("Couldn't parse address or label!")
                    else:
                        # TODO: Possibly add a counter of 1, and remove the breakpoint after hitting it the first time
                        self.mb.breakpoint_add(bank, addr)
                        break
                else:
                    self.mb.breakpoint_singlestep_latch = 0
                    break
            elif cmd == "sl":
                for bank, addresses in self.rom_symbols.items():
                    for addr, label in addresses.items():
                        print(f"{bank:02X}:{addr:04X} {label}")
            elif cmd == "bl":
                for bank, addr in self.mb.breakpoints_list:
                    print(f"{bank:02X}:{addr:04X} {self.rom_symbols.get(bank, {}).get(addr, '')}")
            elif cmd == "b" or cmd.startswith("b "):
                if cmd.startswith("b "):
                    _, command = cmd.split(" ", 1)
                else:
                    command = input(
                        'Write address in the format of "00:0150" or search for a symbol label like "Main"\n'
                    )

                bank, addr = self.parse_bank_addr_sym_label(command)
                if bank is None or addr is None:
                    print("Couldn't parse address or label!")
                else:
                    self.mb.breakpoint_add(bank, addr)

            elif cmd == "d":
                print(f"Removing breakpoint at current PC")
                self.mb.breakpoint_reached() # NOTE: This removes the breakpoint we are currently at
            elif cmd == "pdb":
                # Start pdb
                import pdb
                pdb.set_trace()
                break
            else:
                # Step once
                self.mb.breakpoint_singlestep_latch = 1
                break
