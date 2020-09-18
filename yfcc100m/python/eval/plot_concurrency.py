# from cycler import cycler
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

def instr2bool(in_value):
    if in_value.lower() in ['true', 't']:
        return True
    else:
        return False

def value_to_float(x):
    if type(x) == float or type(x) == int:
        return x
    if 'k' in x:
        if len(x) > 1:
            return float(x.replace('k', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 1000000
        return 1000000.0
    else:
        return float(x)
    return 0.0


obj = argparse.ArgumentParser()
obj.add_argument('-infile', type=lambda s: Path(s),
                 default="./perf_results.log",
                 help='File containing plot data')
obj.add_argument('-outfile', type=lambda s: Path(s),
                 default="./plots/res",
                 help='PDF path for file containing plots')
obj.add_argument('-log', type=instr2bool, default=True, const=True, nargs='?',
                 help='Use log scale for Tx/sec')
obj.add_argument('-single_page_plot', type=instr2bool,
                 default=True, const=True, nargs='?',
                 help='Use log scale for Tx/sec')

params = obj.parse_args()

plotfilename = str(params.outfile)

newpath = str(params.outfile.parents[0])
if not os.path.exists(newpath):
    os.makedirs(newpath)

# color = ['red', 'blue', 'red', 'blue', 'orange', 'orange']
# linestyles = ['-', '-', '--', '--', '-', '--', ]
# markers = ['o', 'o', '*', '*', 'o', '*']
plot = "all"
line_counter = 0

with open(str(params.infile)) as f:

    title = f.readline().replace('\n', '')
    db_sizes = f.readline().replace('\n', '').split(',')[1:]

    data = []
    for line in f:
        line = line.replace('\n', '').split(',')

        if line:  # lines (ie skip them)
            data.append(line)

# print(title)
# print(db_sizes)
# print(data)

query_name = []
for i in range(len(data)):
    query_name.append(data[i][0])

val = []

for i in range(len(data)):
    new = []
    for j in range(len(data[0]) - 1):
        new.append(float(data[i][j + 1]))
    val.append(new)

for i in range(len(val)):
    val[i] = [float(j) for j in val[i]]

val = np.array(val)

# print(data[0][1:])

columns_Tx = [i for i in range(0, len(val[0]), 6)]
tx_sec = val[:, columns_Tx]
tx_sec = tx_sec.transpose()

# print(tx_sec)

columns_Tx_std = [i for i in range(1, len(val[0]), 6)]
tx_sec_std = val[:, columns_Tx_std]
tx_sec_std = tx_sec_std.transpose()

# print(tx_sec_std)

columns_imgs = [i for i in range(2, len(val[0]), 6)]
imgs_sec = val[:, columns_imgs]
imgs_sec = imgs_sec.transpose()

# print(imgs_sec)

columns_imgs_std = [i for i in range(3, len(val[0]), 6)]
imgs_sec_std = val[:, columns_imgs_std]
imgs_sec_std = imgs_sec_std.transpose()

# print(imgs_sec_std)

columns_imgs = [i for i in range(4, len(val[0]), 6)]
imgs_ = val[:, columns_imgs]
imgs_ = imgs_.transpose()

# print(imgs_)

columns_imgs_std = [i for i in range(5, len(val[0]), 6)]
imgs_std = val[:, columns_imgs_std]
imgs_std = imgs_std.transpose()

# print(imgs_std)

x_pos = [int(value_to_float(i)) for i in db_sizes]

linestyles = ['-', '--']
markers = 'o'
color = ['red', 'blue', 'orange', 'black', 'pink']
# if len(imgs_[0, :]) == 2:
#     color = ['red', 'blue']
# elif len(imgs_[0, :]) == 4:
#     color = ['red', 'blue', 'red', 'blue']
# elif len(imgs_[0, :]) == 6:
#     color = ['red', 'blue', 'orange', 'red', 'blue', 'orange']
# elif len(imgs_[0, :]) == 8:

"""
Plot Tx/sec
"""

if params.single_page_plot:
    fig = plt.figure(figsize=(8,10))
    ax0 = plt.subplot(2,1,1)
else:
    fig = plt.figure()
    ax0 = plt.subplot()

plt.rc('lines', linewidth=1)

for i in range(0, len(tx_sec[0, :])):
    ax0.errorbar(x_pos, tx_sec[:, i],
                 yerr=tx_sec_std[:, i],
                 label=query_name[i],
                 color=color[i % len(color)],
                 linestyle=linestyles[int(i / int(len(color)))],
                 marker=markers)

plt.axvline(x=56)
# plt.text(53, 2*10**2, "hw-concurrency", rotation='vertical')
# ax0.set_xscale('log')
if params.log:
    ax0.set_yscale('log')

plt.xticks(x_pos, db_sizes)

ax0.set_title(title)
plt.xlabel('# of Concurrent Clients', fontsize=12)
plt.ylabel('Transactions/s', fontsize=12)

# plt.legend(loc="best", ncol=2, shadow=True, fancybox=True)

if not params.single_page_plot:
    plt.savefig(plotfilename + "_metadata.pdf", format="pdf", bbox_inches='tight')

"""
Plot Images/sec
"""

if params.single_page_plot:
    ax0 = plt.subplot(2,1,2)
else:
    fig = plt.figure()
    ax0 = plt.subplot()

plt.rc('lines', linewidth=1)

for i in range(0, len(imgs_sec[0, :])):
    ax0.errorbar(x_pos, imgs_sec[:, i],
                 yerr=imgs_sec_std[:, i],
                 label=query_name[i],
                 color=color[i % len(color)],
                 linestyle=linestyles[int(i / int(len(color)))],
                 marker=markers)

plt.axvline(x=56)
plt.text(53, 9*10**2, "hw-concurrency", rotation='vertical')

plt.legend(loc="best", ncol=2, shadow=True, fancybox=True, fontsize='small')
# ax0.set_xscale('log')
if params.log:
    ax0.set_yscale('log')

plt.xticks(x_pos, db_sizes)

plt.xlabel('# of Concurrent Clients', fontsize=12)
plt.ylabel('Images/s', fontsize=12)

if not params.single_page_plot:
    ax0.set_title(title)
    plt.savefig(plotfilename + "_images.pdf", format="pdf", bbox_inches='tight')
else:
    plt.savefig(plotfilename + "_all.pdf", format="pdf", bbox_inches='tight')

# """
# Plot # Images
# This plot if for sanity check only, no need to be displayed.
# """

# fig = plt.figure()
# plt.rc('lines', linewidth=1)
# ax0 = plt.subplot()

# for i in range(0, len(imgs_[0, :])):
#     ax0.errorbar(x_pos, imgs_[:, i],
#                  yerr=imgs_std[:, i],
#                  label=query_name[i],
#                  color=color[i], linestyle=linestyles, marker=markers)

# plt.axvline(x=56)

# # ax0.set_xscale('log')
# if params.log:
#     ax0.set_yscale('log')

# plt.xticks(x_pos, db_sizes)

# plt.xlabel('# of Concurrent Clients', fontsize=12)
# plt.ylabel('Avg. # images', fontsize=12)

# plt.savefig(plotfilename + "_numimages.pdf", format="pdf", bbox_inches='tight')
