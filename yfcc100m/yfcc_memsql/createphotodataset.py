import urllib
import time
import os
import time
import re

dataset = "/mnt/data/metadata/original/yfcc100m_dataset"
photodataset = "/mnt/data/metadata/original/yfcc100m_photo_dataset"
autotags = "/mnt/data/metadata/original/yfcc100m_autotags"
photoautotags = "/mnt/data/metadata/original/yfcc100m_photo_autotags"

property_names = ['Line number', 'ID', 'Hash', 'User NSID',
                  'User nickname', 'Date taken', 'Date uploaded',
                  'Capture device',
                  'Title', 'Description', 'User tags', 'Machine tags',
                  'Longitude', 'Latitude', 'Coord. Accuracy', 'Page URL',
                  'Download URL', 'License name', 'License URL',
                  'Server ID', 'Farm ID', 'Secret', 'Secret original',
                  'Extension', 'Marker']
tag_property_names=['ID', 'autotags']

# f=open(dataset, 'r')
# f_out=open(photodataset, 'w')
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

# Close files
# f.close()
# f_out.close()