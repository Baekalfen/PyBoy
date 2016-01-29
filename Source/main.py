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
    print "Invalid arguments!"
    exit(1)

window = None
mb = None

SPF = 1/60. # inverse FPS (frame-per-second)

def start(ROM, bootROM = None):
    global window, mb

    print bootROM
    window = Window(scale=1, debug=False)
    if bootROM is not None:
        print "Starting with boot ROM"
        mb = Motherboard(ROM, bootROM, window)
    else:
        mb = Motherboard(ROM, None, window)

    done = False
    exp_avg_cpu = 0
    exp_avg_gpu = 0
    counter = 0
    t = time.time()
    while not done:
        for event in window.getEvents():
            if event == WindowEvent.Quit:
                window.stop()
                done = True
            # elif event == WindowEvent.DebugNext:
            #     pass
            else:  # Right now, everything else is a button press
                mb.buttonEvent(event)
        
        # t = time.time()
        # if mb.cpu.ram[0xFF40] >> 7 == 1: # Check if LCD is on
        #     if mb.cpu.ram.updateVRAMCache:
        #         mb.lcd.refreshTileData()
        #         mb.cpu.ram.updateVRAMCache = False
        mb.tickFrame()
        mb.tickVblank()

        # tt = time.time()

        mb.lcd.tick()
        window.updateDisplay()
        # tt2 = time.time()
        
        if counter % 60 == 0:
            text = str(int(((time.time()-t)/SPF*100)/60)) + "%"
            t=time.time()
            # exp_avg_cpu = 0.5 * exp_avg_cpu + 0.5 * (tt-t)
            # exp_avg_gpu = 0.5 * exp_avg_gpu + 0.5 * (tt2-tt)
            # text = "C" + str(int((exp_avg_cpu/SPF)*100)) + "%" + " G" + str(int((exp_avg_gpu/SPF)*100))+ "%"
            window._window.title = text
            # print text
            counter = 0
        counter += 1

        # if tt2-t < SPF:
            # Trying to avoid VSync'ing on a frame, if we are out of time
        # window.VSync()

    print "###########################"
    print "# Emulator is turning off #"
    print "###########################"

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

    # start("TestROMs/instr_timing/instr_timing.gb", bootROM)
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
