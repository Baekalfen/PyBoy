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
    exp_avg_emu = 0
    exp_avg_cpu = 0
    t_start = 0
    t_VSynced = 0
    t_frameDone = 0
    counter = 0
    while not done:
        exp_avg_emu = 0.9 * exp_avg_emu + 0.1 * (t_VSynced-t_start)
        exp_avg_cpu = 0.9 * exp_avg_cpu + 0.1 * (t_frameDone-t_start)

        t_start = time.clock()
        for event in window.getEvents():
            if event == WindowEvent.Quit:
                window.stop()
                done = True
            # elif event == WindowEvent.DebugNext:
            #     pass
            else:  # Right now, everything else is a button press
                mb.buttonEvent(event)
        
        mb.tickFrame()
        mb.tickVblank()

        mb.lcd.tick()
        window.updateDisplay()

        t_frameDone = time.clock()

        # Trying to avoid VSync'ing on a frame, if we are out of time
        if (time.clock()-t_start < SPF):
            # This one fixes the time.clock(), but uses much more CPU
            # while (time.clock()-t_start < SPF):
            #     pass

            # This one makes time and frame syncing work, but messes with time.clock()
            window.VSync()

        t_VSynced = time.clock()

        if counter % 60 == 0:
            text = "E:"+str(int(((exp_avg_emu)/SPF*100))) + "%"+ "C:"+ str(int(((exp_avg_cpu)/SPF*100))) + "%"
            # text = "C" + str(int((exp_avg_cpu/SPF)*100)) + "%" + " G" + str(int((exp_avg_gpu/SPF)*100))+ "%"
            window._window.title = text
            # print text
            counter = 0
        counter += 1



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
    # except KeyboardInterrupt as ex:
    #     print ""
    #     print ex
    #     print ""
    #     mb.cpu.getDump()
        # if raw_input() != "":
        #     window.dump("dump",True)

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
