#from cycler import cycler
import numpy as np
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import csv
import os
import re
import argparse
from pathlib import Path

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False
    
obj = argparse.ArgumentParser()
obj.add_argument('-infile', type=lambda s: Path(s), default="perf_results/results.log",
                     help='File containing plot data')
obj.add_argument('-outfile', type=lambda s: Path(s), default="perf_results/plots/results_plot.pdf",
                     help='PDF path for file containing plots')
params = obj.parse_args()

plotfilename = str(params.outfile)

newpath = str(params.outfile.parents[0])
if not os.path.exists(newpath):
    os.makedirs(newpath)

color = ['red', 'blue', 'orange', 'g', 'brown', 'black']
linestyles = ['-', '--', '-.', ':', '-', '--',]

plot = "all" 
line_counter = 0

with open(str(params.infile)) as f:
    data = []
    for line in f:
        line = line.replace('\n','')

        if line_counter == 0:
            title = line
            line_counter =+ 1
            continue

        line = line.split(',') # to deal with blank

        if line:            # lines (ie skip them)
            # line = [float(i) for i in line]
            data.append(line)

print(title)

indexes_name = []
for i in range(len(data)-1):
    indexes_name.append(data[i+1][0])

# print(indexes_name)

xlabels = []
for i in range(len(data[0])-1):
    xlabels.append(data[0][i+1])

val = []

for i in range(len(data)-1):
    new = []
    for j in range(len(data[1])-1):
        new.append(float(data[i+1][j+1]))
    val.append(new)

for i in range(len(val)):
    val[i] = [float(j) for j in val[i]]

val = np.array(val)

columns_Tx = [i for i in range(0,len(data[0][1:]) * 2,2)]  # [0,2,4,6] Tx/sec
yy = val[:, columns_Tx]
yy = yy.transpose()

columns_imgs = [i for i in range(1,len(data[0][1:]) * 2,2)]  # [1,3,5,7]
accuracy = val[:, columns_imgs]
accuracy = accuracy.transpose()

# print(yy)

fig = plt.figure(figsize=(8,10))
plt.rc('lines', linewidth=1)

"""
Plot Tx/sec
"""
ax0 = plt.subplot(2,1,1)

for i in range(0,len(yy[0,:])):
    ax0.plot(yy[:,i], label = indexes_name[i],
                color=color[i], linestyle=linestyles[i], marker='o')

xticks = list(range(len(xlabels)))
plt.xticks(xticks)
ax0.set_xticklabels(xlabels, fontsize=14)

ax0.set_yscale('log')
ax0.set_title(title)
plt.xlabel('Size', fontsize=12)
plt.ylabel('Tx/sec', fontsize=12)

plt.legend(loc="best", ncol=1, shadow=True, fancybox=True)

"""
Plot Images/sec
"""

ax0 = plt.subplot(2,1,2)

for i in range(0,len(yy[0,:])):
    ax0.plot(accuracy[:,i], label = indexes_name[i],
             color=color[i], linestyle=linestyles[i], marker='o')

xticks = list(range(len(xlabels)))
plt.xticks(xticks)
ax0.set_xticklabels(xlabels, fontsize=14)

plt.xlabel('Size', fontsize=12)
plt.ylabel('images/sec', fontsize=12)

"""
Write to pdf
"""
plt.savefig(plotfilename, format="pdf")
