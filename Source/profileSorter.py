import pstats
import os.path

i = 0
while os.path.isfile('profile'+str(i)):
    p = pstats.Stats('profile'+str(i))
    p.sort_stats('tottime')
    p.print_stats()
    i += 1
