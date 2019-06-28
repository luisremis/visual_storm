import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import csv
import os
import re
from random import *
import fnmatch

color = ['red', 'blue', 'gray', '#000099', '#3333ff', 'g',
         '#ff6600', '#cc0000',
         'purple', 'pink', '#000000']

patterns = [ "/" ,"+" , "x", "o", "O", ".", "*",  "\\" , "|" , "-" ]

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

logs_dir = "timelogs_std_drop"
n_files = len(fnmatch.filter(os.listdir(logs_dir), '*.log'))

txsec_f   = []
txsec_fr  = []
txsec_ft  = []
txsec_frt = []
txsec_f_std   = []
txsec_fr_std  = []
txsec_ft_std  = []
txsec_frt_std = []

for i in range(1,n_files):
    f = open(os.path.join(logs_dir,"times_" + str(i) + ".log"))
    lines = f.readlines()

    # print (lines[3])
    txsec_f      .append(1 / (1e-3 * float(lines[1].split(',')[0]) ) * i )
    txsec_fr     .append(1 / (1e-3 * float(lines[3].split(',')[0]) ) * i )
    txsec_ft     .append(1 / (1e-3 * float(lines[5].split(',')[0]) ) * i )
    txsec_frt    .append(1 / (1e-3 * float(lines[7].split(',')[0]) ) * i )
    txsec_f_std  .append(float(lines[1].split(',')[3])/
                         float(lines[1].split(',')[0]) )
    txsec_fr_std .append(float(lines[3].split(',')[3])/
                         float(lines[3].split(',')[0]) )
    txsec_ft_std .append(float(lines[5].split(',')[3])/
                         float(lines[5].split(',')[0]) )
    txsec_frt_std.append(float(lines[7].split(',')[3])/
                         float(lines[7].split(',')[0]) )

f_sumary = open("sumary_times.txt", "w+")

f_sumary.write("threads,findVideo,std,findVideo+Resize,std,findVideo+Transcode,std,findVideo+Resize+Transcode,std\n")

for i in range(0,len(txsec_f)):
    f_sumary.write( "%i,%f,%f,%f,%f,%f,%f,%f,%f\n" %
                    (i+1,
                    txsec_f[i],   (txsec_f[i]   * txsec_f_std[i]),
                    txsec_fr[i],  (txsec_fr[i]  * txsec_fr_std[i]),
                    txsec_ft[i],  (txsec_ft[i]  * txsec_ft_std[i]),
                    txsec_frt[i], (txsec_frt[i] * txsec_frt_std[i])
                    ))

f_sumary.close()

plt.plot(txsec_fr,  label="findVideo+Resize")
plt.plot(txsec_ft,  label="findVideo+Transcode")
plt.plot(txsec_frt, label="findVideo+Resize+Transcode")
plt.ylabel('tx/s')
plt.xlabel("# threads")
plt.legend(loc="best", ncol=1, shadow=True, fancybox=True)


newpath = 'plots'
if not os.path.exists(newpath):
    os.makedirs(newpath)

out_filename = 'plots/sumary_times.pdf'
plt.savefig(out_filename , format="pdf")
os.system("open " + out_filename)
