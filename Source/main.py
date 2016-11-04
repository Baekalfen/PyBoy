#! /usr/local/bin/python2
# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import traceback
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
import os
import sys
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
    window = Window(scale=1)
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
    limitEmulationSpeed = True
    while not done:
        exp_avg_emu = 0.9 * exp_avg_emu + 0.1 * (t_VSynced-t_start)

        t_start = time.clock()
        for event in window.getEvents():
            if event == WindowEvent.Quit:
                window.stop()
                done = True

                mb.cpu.getDump()
            elif event == WindowEvent.ReleaseSpeedUp:
                limitEmulationSpeed ^= limitEmulationSpeed
            # elif event == WindowEvent.PressSpeedUp:
            #     limitEmulationSpeed = False
            elif event == WindowEvent.SaveState:
                mb.saveState(mb.ram.cartridge.gameName+".state")
            elif event == WindowEvent.LoadState:
                mb.loadState(mb.ram.cartridge.gameName+".state")
            elif event == WindowEvent.DebugNext:
                mb.cpu.breakAllow = True
            else:  # Right now, everything else is a button press
                mb.buttonEvent(event)

        mb.tickFrame()
        mb.tickVblank()

        mb.lcd.tick()
        window.updateDisplay()


        # Trying to avoid VSync'ing on a frame, if we are out of time
        if limitEmulationSpeed or (time.clock()-t_start < SPF):
            # This one makes time and frame syncing work, but messes with time.clock()
            window.VSync()

        t_VSynced = time.clock()

        if counter % 60 == 0:
            text = str(int(((exp_avg_emu)/SPF*100))) + "%"
            window._window.title = text
            # print text
            counter = 0
        counter += 1

    print "###########################"
    print "# Emulator is turning off #"
    print "###########################"


def runBlarggsTest():
    for rom in [
                "TestROMs/instr_timing/instr_timing.gb",
                ## "TestROMs/mem_timing/mem_timing.gb",
                "TestROMs/oam_bug/rom_singles/1-lcd_sync.gb",
                "TestROMs/cpu_instrs/individual/01-special.gb",
                "TestROMs/cpu_instrs/individual/02-interrupts.gb",
                "TestROMs/cpu_instrs/individual/03-op sp,hl.gb",
                "TestROMs/cpu_instrs/individual/04-op r,imm.gb",
                "TestROMs/cpu_instrs/individual/05-op rp.gb",
                "TestROMs/cpu_instrs/individual/06-ld r,r.gb",
                "TestROMs/cpu_instrs/individual/07-jr,jp,call,ret,rst.gb",
                "TestROMs/cpu_instrs/individual/08-misc instrs.gb", #Generates Seg. fault
                "TestROMs/cpu_instrs/individual/09-op r,r.gb",
                "TestROMs/cpu_instrs/individual/10-bit ops.gb",
                "TestROMs/cpu_instrs/individual/11-op a,(hl).gb",
                ]:
        try:
            print rom
            start(rom)
        except Exception as ex:
            print ex
            time.sleep(1)
            window.stop()
            time.sleep(2)

if __name__ == "__main__":
    bootROM = "ROMs/DMG_ROM.bin"


    directory = "ROMs/"
    try:
        # Verify directories
        if not bootROM is None and not os.path.exists(bootROM):
            print "Boot-ROM not found. Please copy the Boot-ROM to '%s'. Using replacement in the meanwhile..." % bootROM
            bootROM = None
        if not os.path.exists(directory) and len(sys.argv) < 2:
            print "ROM folder not found. Please copy the Game-ROM to '%s'" % directory
            exit()

        # Check if the ROM is given through argv
        if len(sys.argv) > 2: # First arg is SDL2/PyGame
            if sys.argv[2] == "blargg":
                runBlarggsTest()
                exit(0)
            start(sys.argv[2], bootROM)
            exit(0)
        # else:
        #Give a list of ROMs to start
        found_files = filter(lambda f: f.lower().endswith(".gb") or f.lower().endswith(".gbc"), os.listdir(directory))
        for i, f in enumerate(found_files):
            print "%s\t%s" % (i+1, f)
        filename = raw_input("Write the name or number of the ROM file:\n")

        try:
            filename = directory + found_files[int(filename)-1]
        except:
            filename = directory + filename

        start(filename, bootROM)
    except KeyboardInterrupt:
        if mb is not None:
            mb.cpu.getDump()
        print "Interrupted by keyboard"
    except Exception as ex:
        if mb is not None:
            mb.cpu.getDump()
        # print ex
        traceback.print_exc()

