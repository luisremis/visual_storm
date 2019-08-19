import os
import struct
import numpy as np
import itertools
import time
import random

import vdms

def create_dir(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

# Returns index of x in arr if present, else -1
def binarySearch (arr, l, r, x):

    # Check base case
    if r >= l:

        mid = l + int((r - l)/2)

        # If element is present at the middle itself
        if arr[mid] == x:
            return mid

        # If element is smaller than mid, then it
        # can only be present in left subarray
        elif arr[mid] > x:
            return binarySearch(arr, l, mid-1, x)

        # Else the element can only be present
        # in right subarray
        else:
            return binarySearch(arr, mid + 1, r, x)

    else:
        # Element is not present in the array
        return -1


class VDMSQuery(object):

    def __init__(self, host="localhost", port=55555):
        self.db = vdms.vdms()
        self.db.connect(host, port)

    def __del__(self):
        self.db.disconnect()

    def get_image_fv(self, image_id):

        fI = {
            "FindImage": {
                "_ref": 34,
                "constraints": {
                    "ID": ["==", image_id]
                },
                "results": {
                    "list": ["ID"]
                }
            }
        }

        fD = {
            "FindDescriptor": {
                "set": "hybridNet",
                "link": {
                    "ref": 34,
                },
                "results": {
                    "blob": True,
                    "list": ["_distance"]
                }
            }
        }

        responses, blobs = self.db.query([fI, fD])

        print(self.db.get_last_response_str())

        return blobs[0], blobs[1]


    def get_image(self, image_id):

        fI = {
            "FindImage": {
                "constraints": {
                    "ID": ["==", image_id]
                },
                "results": {
                    "list": ["ID"]
                }
            }
        }

        responses, blobs = self.db.query([fI])

        print(self.db.get_last_response_str())

        return blobs[0]


    def get_similar_images(self, fv, n):

        fD = {
            "FindDescriptor": {
                "k_neighbors": n,
                "set": "hybridNet",
                "_ref": 34
            }
        }

        fI = {
            "FindImage": {
                "link": {
                    "ref": 34,
                },
                "results": {
                    "list": ["ID"]
                }
            }
        }

        response, imgs = self.db.query([fD, fI], [[fv]])

        print(self.db.get_last_response_str())

        return imgs


    def intersect_by_key(self, responses, key):

        for i in range (int(len(responses) / 2)):
            curr = len(responses[i*2 + 1]["FindImage"]["entities"])
            # print("curr:", curr)
            if i == 0:
                smallest = curr
                idx = 0
            else:
                if (curr < smallest):
                    smallest = curr
                    idx = i

        # build the initial set based on the smallest
        set = []
        for ent in responses[idx*2 + 1]["FindImage"]["entities"]:
            set.append(int(ent[key]))

        results = []
        for i in range (int(len(responses) / 2)):
            # if(i == idx): # this can be done to save one pass, but a corner
                            # case must be handled
            #     continue

            set.sort()
            aux_set = []

            for ent in responses[i*2 + 1]["FindImage"]["entities"]:
                id_to_check = int(ent[key])
                pos = binarySearch(set, 0, len(set) - 1, id_to_check)

                if (pos != -1):
                    aux_set.append(id_to_check)

                    if (i == int(len(responses)/2) - 1): # last findImage
                        results.append(ent)

            set = aux_set

        return results

    def get_metadata_by_tags(self, tags, probs, lat=-1, long=-1, range_dist=0, return_response=True):

        all_cmds = []

        ref = 1
        for (tag, prob) in zip(tags,probs):
            fE = {
                "FindEntity": {
                    "_ref": ref,
                    "class": "autotags",
                    "constraints": {
                        "name": ["==", tag]
                    }
                }
            }

            fI = {
                "FindImage": {
                    "link": {
                        "ref": ref,
                        "constraints": {
                            "tag_prob": [">=", prob]
                        }
                    },
                    "results": {
                        "list": ["ID", "Latitude", "Longitude", "License name"],
                        "blob": False
                    }
                }
            }

            if (lat != -1):
                fI["FindImage"]["constraints"] = {
                    "Latitude": [">=", lat-range_dist*1.0,
                                 "<=", lat + range_dist*1.0  ],
                    "Longitude": [">=", long-range_dist*1.0,
                                 "<=", long + range_dist*1.0  ]
                }

            all_cmds.append(fE)
            all_cmds.append(fI)

            ref += 1

        start = time.time()
        responses, blobs = self.db.query(all_cmds)
        # print("Time for metadata (ms):", endtime * 1000.0)
        # print(self.db.get_last_response_str())

        # Find intersections by ID
        try:
            if (len(tags) > 1):
                results = self.intersect_by_key(responses, "ID")
            else:
                results = responses[1]["FindImage"]["entities"]
        except:
                results = []
        endtime = time.time() - start

        print("Total results:", len(results))

        # print(results)
        if return_response:
            return results

        out_dict = {'response_len':len(results),'response_time':endtime}
        return out_dict


    def get_images_by_tags(self, tags, probs, operations = [],
                           lat=-1, long=-1, range_dist=0, return_images=True):
        start = time.time()
        results = self.get_metadata_by_tags(tags, probs, lat, long, range_dist)

        all_cmds = []

        for ele in results:
            fI = {
                "FindImage": {
                    "constraints": {
                        "ID":  ["==", ele['ID']]
                    },
                    "results": {
                        "list": ["ID", "Latitude", "Longitude", "License name"]
                    }
                }
            }

            if len(operations) >= 0:
                fI["FindImage"]["operations"] = operations

            all_cmds.append(fI)

        # start = time.time()
        responses, blobs = self.db.query(all_cmds)
        end_time = time.time() - start
        # print("Time for images (ms):", end_time * 1000.0)
        # print(self.db.get_last_response_str())

        # create_dir('tmp')
        # create_dir('tmp/vdms')
        # for im in blobs:
        #         name = random.randint(0,90000000)
        #         tmp_file = 'tmp/vdms/img_' + str(name) + ".jpg"
        #         f = open(tmp_file, 'wb')
        #         f.write(im)

        vblobs = [img for img in blobs if img]
        print("Total valid images:", len(vblobs))

        if return_images:
            return blobs

        out_dict = {'images_len':len(vblobs),'images_time':end_time}

        return out_dict
