#from cycler import cycler
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import csv
import os
import re

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

color = ['red', 'red', 'blue', 'blue', 'orange', 'orange', 'g', 'g']

plot = "all" # "ops"

filename = "sumary_times.txt"
with open(filename) as f:
    data = []
    for line in f:
        line = line.replace('\n','')
        line = line.split(',') # to deal with blank

        if not isfloat(line[0]): # skip lines with text, probably headers
            labels = line
            continue

        if line:            # lines (ie skip them)
            line = [float(i) for i in line]
            data.append(line)

lines = np.array(data)
if plot == "all":
    columns_used = [1,3,5,7]
    error_used   = [2,4,6,8]
else:
    columns_used = [3,5,7]
    error_used   = [4,6,8]

n_threads = list(range(lines.shape[0]))
n_threads = [1,2,4,8,16,32,56,64]
# n_threads = [2,4,8,16,32,56,64]

lines = lines[n_threads, :]
yy    = lines[:, columns_used]
error = lines[:, error_used]

labels = np.array(labels)
labels = labels[columns_used]

plt.rc('lines', linewidth=1)
fig, ax0 = plt.subplots(nrows=1)

print(yy[:,1])
print(error[:,1])

for i in range(0,len(columns_used)):
    # ax0.plot(yy[:,i], label = labels[i], color=color[i])
    ax0.errorbar(lines[:,0]-1, yy[:,i], yerr=error[:,i],
                label = labels[i], color=color[columns_used[i]] ) #, fmt='-o')

if yy.shape[0] < 20:
    xticks = list(range(yy.shape[0]))
#     # # xticks = str(n_threads)
    plt.xticks(n_threads)
    # plt.xticks(xticks, n_threads)


plt.axvline(x=56)

ax0.set_title('VDMS - Video Transactions (Transactions per sec)')
plt.xlabel('# clients', fontsize=12)
plt.ylabel('Tx/sec', fontsize=12)

# yticks = list(xrange(yy.shape[0]))
# plt.yticks(yticks)
# ax0.set_yscale('log')
plt.ticklabel_format(axis='y')
if plot == "all":
    plt.yscale('log')
    plt.text(53, 5000, "hw-concurrency", rotation='vertical')
else:
    plt.text(53, 8, "hw-concurrency", rotation='vertical')

# plt.xscale('log')


plt.legend(loc="best", ncol=1, shadow=True, fancybox=True)

# plt.tight_layout()

newpath = 'plots'
if not os.path.exists(newpath):
    os.makedirs(newpath)

file_format = 'pdf' # 'png'

if plot == "all":
    prefix = "txsec_all_"
else:
    prefix = "txsec_ops_"

out_filename = 'plots/' + prefix + filename + '.' + file_format
plt.savefig(out_filename, format=file_format)

os.system("open " + out_filename)
