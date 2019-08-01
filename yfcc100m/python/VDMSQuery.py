import os
import struct
import numpy as np
import itertools
import time

import vdms

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

        print("bye bye")

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

    def get_image_by_tags(self, tags, probs):

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

            all_cmds.append(fE)
            all_cmds.append(fI)

            ref += 1

        start = time.time()
        responses, blobs = self.db.query(all_cmds)
        print("Time (ms):", (time.time() - start) * 1000.0)
        # print(self.db.get_last_response_str())

        if (len(tags) > 1):
            results = self.intersect_by_key(responses, "ID")
        else:
            results = responses[1]["FindImage"]["entities"]

        print("Total results:", len(results))

        # print(results)

        return responses


    def get_image_by_tag(self, tag, prob):

        fE = {
            "FindEntity": {
                "_ref": 2,
                "class": "autotags",
                "constraints": {
                    "name": ["==", tag]
                }
            }
        }

        fI = {
            "FindImage": {
                "link": {
                    "ref": 2,
                    "constraints": {
                        "tag_prob": [">=", prob]
                    }
                },
                "results": {
                    "list": ["ID"],
                    "blob": True,
                    "limit": 20
                }
            }
        }

        responses, blobs = self.db.query([fE, fI])

    #     print(self.db.get_last_response_str())

        print("Images with", tag, "with prob >=", prob, ":", responses[1]["FindImage"]["returned"])

        return blobs
