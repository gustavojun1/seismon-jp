from obspy import read
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
import numpy as np
import time
import os
import shutil

#sac_file = input("which file?\n")
source = "N"
station = "AAKH"
direction = "E"
sac_file = "data/" + source + "." + station + "." + direction + ".SAC"

station = read((sac_file), debug_headers=True)
#print(station)

x = []
y = []

count = 0
for i in station[0]:
    count += 1
    #print(f"{i} {count}")
    x.append(round(count / 30, 3))
    y.append(i)

plt.xlabel("Timestamp (in milliseconds)")
plt.ylabel("Earth motion magnitude on " + direction + " axis")
plt.title("Graph plotted at " + str(time.ctime(time.time())))
plt.plot(x, y)

#plt.show()
plot_file = "plot.png"
prev_file = "prev.png"
if os.path.exists(plot_file):
    shutil.copy(plot_file, prev_file)
plt.savefig("plot.png")