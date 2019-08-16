import urllib
import time
import os
import time
import re
from util import tag_property_names, property_names
import argparse

def get_args():
    parserobj = argparse.ArgumentParser()
    parserobj.add_argument('-tag_file', type=str, required=True,
                           help='YFCC file of autotags [Ex: /mnt/yfcc100m/metadata/original/yfcc100m_photo_autotags]')
    params = parserobj.parse_args()
    return params


def main(params):
    photoautotags = params.tag_file
    photoautotagsex = params.tag_file + "_extended"
    print('Separating autotags string to individual rows')
    start = time.time()
    with open(photoautotags, 'r') as f, open(photoautotagsex, 'w') as f_out:
        for line in f:
            tokens = line.strip().split('\t')
            if len(tokens) > 1:
                for tagstr in tokens[1].split(','):
                    tag_val = tagstr.split(':')
                    if len(tag_val) == 2:
                        newline = '\t'.join([tokens[0],tag_val[0],tag_val[1]]) + '\n'
                        f_out.write(newline)
    print('\tTime(s): {:0.4f}'.format(time.time() - start))
    print('New extended file location: ', photoautotagsex)


if __name__ == '__main__':
    args = get_args()
    main(args)

