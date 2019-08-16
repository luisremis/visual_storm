import urllib
import time
import os
import time
import re
from util import tag_property_names, property_names

dataset = "/mnt/data/metadata/original/yfcc100m_dataset"
photodataset = "/mnt/data/metadata/original/yfcc100m_photo_dataset"
autotags = "/mnt/data/metadata/original/yfcc100m_autotags"
photoautotags = "/mnt/data/metadata/original/yfcc100m_photo_autotags"

line_num = 0
id_index = property_names.index('ID')
photo_index = property_names.index('Marker')
line_num_index = property_names.index('Line number')

with open(dataset, 'r') as f, open(photodataset, 'w') as f_out, open(autotags, 'r') as ft, open(photoautotags, 'w') as ft_out:
    for i, (line, tagline) in enumerate(zip(f, ft)):
        tokens = line.strip().split('\t')
        if tokens[photo_index] == '0':
            print('Processing index: {} ({},{})'.format(i,tokens[id_index], tagline.split('\t')[0]))
            tokens[line_num_index] = str(line_num) # Update line number
            f_out.write('\t'.join(tokens) + '\n')
            ft_out.write(tagline)
            line_num += 1
