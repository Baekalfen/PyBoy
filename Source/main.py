#! /usr/local/bin/python2
# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import sys

try:
    import __pypy__
except ImportError:
    __pypy__ = None

if __pypy__ is not None:
    sys.path.insert(0, "/usr/local/Cellar/pypy/4.0.1/libexec/site-packages")

from MB import Motherboard
from WindowEvent import WindowEvent
from Debugger import Debugger
import time
import os.path
from multiprocessing import Process

if len(sys.argv) < 2:
    from Window_SDL2 import Window
elif sys.argv[1] == "SDL2":
    from Window_SDL2 import Window
elif sys.argv[1] == "pygame":
    from Window_pygame import Window
else:
    exit(1)

window = None
mb = None

SPF = 1/60. # inverse FPS (frame-per-second)

def start(ROM, bootROM = None):
    global window, mb

    window = Window(scale=1, debug=False)
    if bootROM is not None and os.path.isfile(bootROM):
        print "Starting with boot ROM"
        mb = Motherboard(ROM, bootROM, window)
    else:
        mb = Motherboard(ROM, None, window)

    # if __debug__:
        # debugger = Debugger(mb)

    done = False
    stepOnce = False
    exp_avg_cpu = 0
    exp_avg_gpu = 0
    counter = 0
    while not done:
        # GPCPUman.pdf p. 6
        # Nintendo documents describe the CPU&instructions speed i n machi ne cycl es whi l e t hi s document descri bes them in clock cycles. Here is the translation:
        # 1 machine cycle = 4 clock cycles

        #                  GB CPU Speed  NOP Instruction
        # Machine Cycles   1.05MHz       1 cycle
        # Clock Cycles     4.19MHz       4 cycles

        for event in window.getEvents():
            if event == WindowEvent.Quit:
                window.stop()
                done = True
            elif event == WindowEvent.DebugNext:
                stepOnce = True
            else:  # Right now, everything else is a button press
                mb.buttonEvent(event)
        
        t = time.time()
        mb.tickFrame()
        mb.tickVblank()

        tt = time.time()

        mb.lcd.tick()
        window.updateDisplay()
        tt2 = time.time()
        
        if __debug__ and counter % 16 == 0:
            exp_avg_cpu = 0.9 * exp_avg_cpu + 0.1 * (tt-t)
            exp_avg_gpu = 0.9 * exp_avg_gpu + 0.1 * (tt2-tt)
            window._window.title = "C" + str(int((exp_avg_cpu/SPF)*100)) + "%" + " G" + str(int((exp_avg_gpu/SPF)*100))+ "%"
            counter = 0
        counter += 1

if __name__ == "__main__":
    bootROM = "ROMs/DMG_ROM.bin"
    # try:
        # start("TestROMs/instr_timing/instr_timing.gb")
    # start("ROMs/pokemon_blue.gb")
    # start("ROMs/Tetris.gb")
    # start("ROMs/Mr. Do!.gb", bootROM)
    start("ROMs/SuperMarioLand.gb", bootROM)


    # filename = raw_input("Write the name of a ROM:\n")
    # start(filename)

        # start("TestROMs/instr_timing/instr_timing.gb")
        # start("TestROMs/mem_timing/mem_timing.gb")
        # start("Tetris.gb")
    # except Exception as ex:
    #     print ""
    #     print ex
    #     print ""
    #     mb.cpu.getDump()
    #     if raw_input() != "":
    #         window.dump("dump",True)

    # SPF = 0
    # for rom in [
    #             "TestROMs/cpu_instrs/individual/01-special.gb",
    #             "TestROMs/cpu_instrs/individual/02-interrupts.gb",
    #             "TestROMs/cpu_instrs/individual/03-op sp,hl.gb",
    #             "TestROMs/cpu_instrs/individual/04-op r,imm.gb",
    #             "TestROMs/cpu_instrs/individual/05-op rp.gb",
    #             "TestROMs/cpu_instrs/individual/06-ld r,r.gb",
    #             "TestROMs/cpu_instrs/individual/07-jr,jp,call,ret,rst.gb",
    #             # "TestROMs/cpu_instrs/individual/08-misc instrs.gb", #Generates Seg. fault
    #             "TestROMs/cpu_instrs/individual/09-op r,r.gb",
    #             "TestROMs/cpu_instrs/individual/10-bit ops.gb",
    #             "TestROMs/cpu_instrs/individual/11-op a,(hl).gb"
    #             ]:
    #     try:
    #         print rom
    #         start(rom)
    #     except:
    #         time.sleep(1)
    #         window.stop()
    #         time.sleep(1)
