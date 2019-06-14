import os
import struct
import numpy

class descriptors_reader(object):

    def __init__(self, prefix):

        self.file = None
        self.prefix = prefix
        self.file_counter = 0

        self.dimensions = 4096

        self.desc_counter = 0

        self.read_next_file()

    def get_next_n(self, n):

        ids = []
        descriptors = []

        i = 0

        while i < n:

            id_bin = self.file.read(8)
            if id_bin == '':
                read_next_file()
                continue

            id_long = struct.unpack('@l', id_bin)[0]

            descriptor = self.file.read(4 * self.dimensions)

            ids.append(id_long)
            descriptors.append(descriptor)

            i += 1

        return ids, descriptors


    def read_next_file(self):

        filename = self.prefix + str(self.file_counter) + ".bin"

        print("Reading", filename, "...")

        self.file = open(filename, 'rb')
        self.file_counter += 1


