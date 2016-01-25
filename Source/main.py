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
        mb = Motherboard(ROM, bootROM, window)
    else:
        mb = Motherboard(ROM, None, window)

    if __debug__:
        debugger = Debugger(mb)

    done = False
    stepOnce = False
    exp_avg_cpu = 0
    exp_avg_gpu = 0
    while not done:
        # t = time.clock()
        t = time.time()
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
                mb.buttonPressed(event)

        mb.tick()
        tt = time.time()

        window.updateDisplay() 
        tt2 = time.time()
        # time.sleep(max(0, SPF-tt))
        # tt = time.clock()-t
        # while (time.clock()-t < SPF):
        #     pass

        
        if __debug__:
            exp_avg_cpu = int(0.9 * exp_avg_cpu + 0.1 * int((SPF/(tt-t))*100))
            exp_avg_gpu = int(0.9 * exp_avg_gpu + 0.1 * int((SPF/(tt2-tt))*100))
            window._window.title = "C" + str(exp_avg_cpu) + "%" + " G" + str(exp_avg_gpu)+ "%"

if __name__ == "__main__":
    bootROM = "DMG_ROM.bin"
    # try:
        # start("TestROMs/instr_timing/instr_timing.gb")
        # start("pokemon_blue.gb")
    start("SuperMarioLand.gb")
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
