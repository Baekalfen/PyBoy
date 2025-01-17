#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#


import pyboy
from pyboy.plugins.base_plugin import PyBoyPlugin

logger = pyboy.logging.get_logger(__name__)


class DebugPrompt(PyBoyPlugin):
    argv = [("--breakpoints", {"type": str, "help": "Add breakpoints on start-up (internal use)"})]

    def __init__(self, pyboy, mb, pyboy_argv):
        super().__init__(pyboy, mb, pyboy_argv)

        if not self.enabled():
            return

        self.rom_symbols = pyboy._load_symbols()

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
            try:
                return self.pyboy._lookup_symbol(command)
            except ValueError:
                pass
        return None, None

    def handle_breakpoint(self):
        while True:
            self.pyboy._plugin_manager.post_tick()

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
                for bank, addr in self.mb.breakpoints.keys():
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
                print("Removing breakpoint at current PC")
                self.mb.breakpoint_reached()  # NOTE: This removes the breakpoint we are currently at
            elif cmd == "pdb":
                # Start pdb
                import pdb

                pdb.set_trace()
                break
            else:
                # Step once
                self.mb.breakpoint_singlestep_latch = 1
                break
