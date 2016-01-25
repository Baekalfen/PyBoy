
RAM = None
CPU = None
windowHandle = None

class CoreDump(Exception):
    def __init__(self, message):
        super(CoreDump, self).__init__(message)

        from CPU.registers import A, F, B, C, D, E, H, L, SP, PC
        from opcodeToName import CPU_COMMANDS, CPU_COMMANDS_EXT

        dump = ""
        dump += "Error message: " + str(message) + "\n\n"
        dump += "CPU.interruptMasterEnable: " + str(CPU.interruptMasterEnable) + "\n"
        dump += "CPU.interruptMasterEnableLatch: " + str(CPU.interruptMasterEnableLatch) + "\n"
        dump += "CPU.halted: " + str(CPU.halted) + "\n"
        dump += "CPU.stopped: " + str(CPU.stopped) + "\n"
        dump += "CPU.breakOn: " + str(CPU.breakOn) + "\n"
        dump += "CPU.debugCallStack: " + str(CPU.debugCallStack) + "\n"

        instruction = CPU.fetchInstruction(CPU.reg[PC])
        if (CPU.ram[CPU.reg[PC]]) != 0xCB:
            l = CPU.opcodes[CPU.ram[CPU.reg[PC]]][0]
            dump += "Op:" + " " + "0x%0.2X" % CPU.ram[CPU.reg[PC]] + " " + "Name:" + " " + CPU_COMMANDS[CPU.ram[CPU.reg[PC]]] + " " + "Len:" + " " + str(l) + " " + ("val:" + " " + "0x%0.2X" % instruction[2][1]) if not l == 1 else ""
        else:
            dump += "CB op:" + " " + "0x%0.2X" % CPU.ram[CPU.reg[PC]+1] + " " + "CB name:" + " " + CPU_COMMANDS_EXT[CPU.ram[CPU.reg[PC]+1]]

        dump += "\n"

        for r, v in zip([A, F, B, C, D, E, H, L, PC, SP], ["A", "F", "B", "C", "D", "E", "H", "L", "PC", "SP"]):
            dump += str(v) + ": " + hex(CPU.reg[r]) + "\n"

        dump += RAM.dump() + "\n"

        import datetime
        fname = ("Core Dump " + str(RAM.cartridge.filename.split('/')[-1]) + " " + str(datetime.datetime.now()) + ".dump"). replace(" ", "_")
        with open(fname, "wb") as dumpfile:
            dumpfile.write(dump)

        windowHandle.dump(fname)
