import urllib
import time
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time
import pylab
import re

dataset = "/home/luisremi/data/yfcc100m/yfcc100m_dataset"

f_out=open("urls.txt", 'w')

counter = 0

f=open(dataset, 'r')
for line in f:
    tokens = line.strip().split('\t')
    if tokens[24] == '0': # photo indicator

        if counter > 30000000:
            break
        url = tokens[16]  # url of the photo
        f_out.write(url + "\n")
        counter = counter + 1