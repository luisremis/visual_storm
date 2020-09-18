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
    return 0.0


obj = argparse.ArgumentParser()
obj.add_argument('-infile', type=lambda s: Path(s),
                 default="./conc_ntags2_niter4.csv",
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

    data = []
    for line in f:
        line = line.replace('\n', '').split(',')

        if line:  # lines (ie skip them)
            data.append(line)

# print(title)
# print(db_sizes)
# print(data)

n_threads = []
for i in range(len(data)):
    n_threads.append(data[i][0])

data = np.array(data)
data = data[:,1:]

print(data)
data.reshape(4,40)

print(data)

for i in range(len(data)):
    new = []
    for j in range(1, len(data[0])):
        new.append(float(data[i][j - 1]))
        if j % 4 == 0:
            new.append(1.0)
            new.append(1.0)
    val.append(new)

for i in range(len(val)):
    val[i] = [float(j) for j in val[i]]

val = np.array(val)

print(val)

