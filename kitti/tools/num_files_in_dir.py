#!/usr/bin/env python
import os.path
import sys
path = sys.argv[1]
num_files = len([f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))])
print num_files

