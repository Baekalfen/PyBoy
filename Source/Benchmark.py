# -*- encoding: utf-8 -*-
#
# Authors: Asger Anders Lund Hansen, Mads Ynddal and Troels Ynddal
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

# Search for prints
# egrep -r "^[^#]*?print.*?$" .

from CPU import CPU
from Interaction import Interaction
from Cartridge import Cartridge
from RAM import RAM
from time import time


interactionTime = float("inf")
cartridgeTime = float("inf")
ramTime = float("inf")
cpuTime = float("inf")
benchmarkTime = float("inf")

for n in xrange(10):
    
    t = time()
    interaction = Interaction()
    t2 = time()
    if t2-t<interactionTime:
        interactionTime = t2-t

    t = time()
    cartridge = Cartridge("pokemon_blue.gb")
    t2 = time()
    if t2-t<cartridgeTime:
        cartridgeTime = t2-t

    t = time()
    ram = RAM(cartridge, interaction, random=False)
    t2 = time()
    if t2-t<ramTime:
        ramTime = t2-t
    
    t = time()
    cpu = CPU("DMG_ROM.bin", ram)
    t2 = time()
    if t2-t<cpuTime:
        cpuTime = t2-t
    
    t = time()
    i = 0
    while i<86285: #About 5 frames
        cpu.tick()
        i += 1
    t2 = time()
    if t2-t<benchmarkTime:
        benchmarkTime = t2-t
    
    

print "-- Init --"
print "Interaction:\t",str(interactionTime).replace(".",",")
print "Cartridge:  \t",str(cartridgeTime).replace(".",",")
print "RAM:        \t",str(ramTime).replace(".",",")
print "CPU:        \t",str(cpuTime).replace(".",",")
print ""
print "-- Benchmark --"
print "Total time:        \t",str(benchmarkTime).replace(".",",")
print "Average time/frame:\t",str(benchmarkTime/(i/17476)).replace(".",",")