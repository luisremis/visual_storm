import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import csv
import os
import re
from random import *

color = ['red', 'blue', 'gray', 'b', 'b', 'g',
         '#ff6600', '#cc0000',
         'purple', 'pink', '#000000']

patterns = [ "/" ,"+" , "x", "o", "O", ".", "*",  "\\" , "|" , "-" ]

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

files = ["query1.txt"]
counter  = 1

queries = ['Video Operations in VDMS - 32 Clients']

# plt.subplots(figsize=(15, 10))

for file in files:

    with open(file) as f:
        data = []
        for line in f:
            line = line.split(',') # to deal with blank

            if line:            # lines (ie skip them)
                # line = [float(i) for i in line]
                data.append(line)

    labels = []
    for i in range(len(data)-1):
        labels.append(data[i+1][0])

#     print(labels)

    xlabels = []
    for i in range(len(data[0])-1):
        xlabels.append(data[0][i+1].rstrip())

#     print(xlabels)

    val = []

    for i in range(len(data)-1):
        # print data[i]
        new = []
        for j in range(len(data[0])-1):
            new.append(float(data[i+1][j+1]))
        val.append(new)

    for i in range(len(val)):
        val[i] = [float(j) for j in val[i]]

    val = np.array(val).transpose()
#     print(val)

    ind = np.arange(len(labels))
    width = 0.6       # the width of the bars: can also be len(x) sequence

    # plt.subplot(130+counter)

    p1 = plt.bar(ind, val[0,:], width)
    p3 = plt.bar(ind, val[2,:], width, bottom=val[0,:])
    p2 = plt.bar(ind, val[1,:], width, bottom=val[2,:])
#     p3 = plt.bar(ind, val[2,:], width,
#                  bottom=val[1,:] + val[0,:])

    plt.title(queries[counter-1])
    plt.xticks(ind, labels, fontsize=6)
#     plt.yticks(np.arange(0, 21, 5))

    if counter == 1:
        plt.ylabel('Time (ms) per query')

    if counter == 1:
        plt.legend((p1[0], p2[0] ,p3[0]), xlabels)

    counter +=1

filename = "findVideo"
form = ["png"]

for fo in form:
    outputfile = "res_"+ filename + '.' + fo
    plt.savefig(outputfile, format=fo, bbox_inches='tight')

newpath = 'plots'
if not os.path.exists(newpath):
    os.makedirs(newpath)

out_filename = 'plots/decomp.pdf'
plt.savefig(out_filename , format="pdf")
os.system("open " + out_filename)