import os
import struct
import numpy as np
import itertools
import time
import random
import cv2

import vdms

OR_OPERATION = True

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

        # Runs a query, described in the "query" object param
    def run_query(self, query):

        key   = query['key']
        tags  = query['tags']
        probs = query['probs']
        lat   = query['lat']  if 'lat'  in query else -1
        long  = query['long'] if 'long' in query else -1
        range_dist = query['range_dist'] if 'range_dist' in query else 0
        operations = query['operations'] if 'operations' in query else []
        comptype   = query["comptype"]   if 'comptype'   in query else "or"

        # Metadata only queries

        if key == "1tag":
            return self.get_metadata(tags, probs,
                                     comptype=comptype)

        if key == "1tag_loc20":
            return self.get_metadata(tags, probs,
                                     lat=lat,
                                     long=long,
                                     range_dist=range_dist,
                                     comptype=comptype,
                                     )

        if key == "2tag_and":
            return self.get_metadata(tags, probs, comptype=comptype, )

        if key == "2tag_or":
            return self.get_metadata(tags, probs, comptype=comptype, )

        if key == "2tag_loc20_and":
            return self.get_metadata(tags, probs,
                                     lat=lat,
                                     long=long,
                                     range_dist=range_dist,
                                     comptype=comptype,
                                     )

        if key == "2tag_loc20_or":
            return self.get_metadata(tags, probs,
                                     lat=lat,
                                     long=long,
                                     range_dist=range_dist,
                                     comptype=comptype,
                                     )

        # Image queries

        if key == "1tag_resize":
            return self.get_images(tags, probs,
                                     operations=operations,
                                     comptype=comptype,
                                     )

        if key == "1tag_loc20_resize":
            return self.get_images(tags, probs,
                                     lat=lat,
                                     long=long,
                                     range_dist=range_dist,
                                     operations=operations,
                                     comptype=comptype,
                                     )

        if key == "2tag_resize_and":
            return self.get_images(tags, probs,
                                     operations=operations,
                                     comptype=comptype,
                                     )

        if key == "2tag_resize_or":
            return self.get_images(tags, probs,
                                     operations=operations,
                                     comptype=comptype,
                                     )

        if key == "2tag_loc20_resize_and":
            return self.get_images(tags, probs,
                                     lat=lat,
                                     long=long,
                                     range_dist=range_dist,
                                     operations=operations,
                                     comptype=comptype,
                                     )

        if key == "2tag_loc20_resize_or":
            return self.get_images(tags, probs,
                                     lat=lat,
                                     long=long,
                                     range_dist=range_dist,
                                     operations=operations,
                                     comptype=comptype,
                                     )

        print("Error - MySQLQueries - Query nor found:", key)
        exit()


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


    def intersect_by_key(self, responses, key, comptype='and'):

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

                if (pos != -1 and comptype == 'and'):
                    aux_set.append(id_to_check)

                    if (i == int(len(responses)/2) - 1): # last findImage
                        results.append(ent)

                elif (pos == -1 and comptype == 'or'):
                    aux_set.append(id_to_check)
                    results.append(ent)

            set = aux_set

        return results

    def get_metadata(self, tags, probs, lat=-1, long=-1, range_dist=0, return_response=False, comptype='and'):

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
                        "list": ["ID"],
                        "blob": False
                    }
                }
            }

            if (lat != -1):
                fI["FindImage"]["constraints"] = {
                    "Latitude":  [">=", lat  - range_dist*1.0,
                                  "<=", lat  + range_dist*1.0  ],
                    "Longitude": [">=", long - range_dist*1.0,
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
	    #TODO: Add 'or'
            if (len(tags) > 1):
                results = self.intersect_by_key(responses, "ID",
                                                comptype=comptype)
            else:
                results = responses[1]["FindImage"]["entities"]
        except:
                results = []
                print("Error processing results in get_metadata")

        endtime = time.time() - start

        # print("GetMetadataVDMS Query:", endtime)

        # This is for the case of internal call from within this calss
        if return_response:
            return results

        # print("Total results:", len(results))
        # print("Time for metadata (ms):", endtime * 1000.0)

        out_dict = {'response_len':len(results),'response_time':endtime}
        return out_dict


    def get_images(self, tags, probs,
                           operations = [],
                           lat=-1, long=-1,
                           range_dist=0,
                           return_images=False,
                           comptype='and'):

        if len(tags) > 1:

            if comptype == 'or':
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
                            }
                        }
                    }

                    if (lat != -1):
                        fI["FindImage"]["constraints"] = {
                            "Latitude":  [">=", lat  - range_dist*1.0,
                                          "<=", lat  + range_dist*1.0  ],
                            "Longitude": [">=", long - range_dist*1.0,
                                          "<=", long + range_dist*1.0  ]
                        }

                    all_cmds.append(fE)
                    all_cmds.append(fI)

                    ref += 1

                start = time.time()
                responses, blobs = self.db.query(all_cmds)
                total_time = time.time() - start

            elif comptype == 'and':
                start = time.time()
                results = self.get_metadata(tags, probs, lat, long, range_dist, return_response=True)

                all_cmds = []

                for ele in results:
                    fI = {
                        "FindImage": {
                            "constraints": {
                                "ID":  ["==", ele['ID']]
                            },
                            # "results": {
                            #     "list": ["ID"]
                            # }
                        }
                    }

                    if len(operations) > 0:
                        fI["FindImage"]["operations"] = operations

                    all_cmds.append(fI)

                # start = time.time()
                responses, blobs = self.db.query(all_cmds)
                total_time = time.time() - start

                # if lat == -1:
                #     out_file = open("perf_results/vdms_img_list.txt", 'w')
                #     for ent in responses:
                #         out_file.write(str(ent["FindImage"]["entities"][0]["ID"]))
                #         out_file.write("\n")

        else:

            all_cmds = []

            fE = {
                "FindEntity": {
                    "_ref": 10,
                    "class": "autotags",
                    "constraints": {
                        "name": ["==", tags[0]]
                    }
                }
            }

            fI = {
                "FindImage": {
                    "link": {
                        "ref": 10,
                        "constraints": {
                            "tag_prob": [">=", probs[0]]
                        }
                    },
                    # "results": {
                    #     "list": ["ID"]
                    # }
                }
            }

            if (lat != -1):
                fI["FindImage"]["constraints"] = {
                    "Latitude":  [">=", lat  - range_dist*1.0,
                                  "<=", lat  + range_dist*1.0  ],
                    "Longitude": [">=", long - range_dist*1.0,
                                  "<=", long + range_dist*1.0  ]
                }

            if len(operations) > 0:
                fI["FindImage"]["operations"] = operations

            all_cmds.append(fE)
            all_cmds.append(fI)

            start = time.time()
            responses, blobs = self.db.query(all_cmds)
            total_time = time.time() - start

        decoded_images = []
        counter_bad_img = 0
        try:
            for im in blobs:
                if len(im) == 0:
                    # print("WARNING - Returned blob of size 0")
                    dec_img = None
                    counter_bad_img += 1
                else:
                    img = np.frombuffer(im, dtype='uint8')
                    dec_img = cv2.imdecode(img, cv2.IMREAD_COLOR)

                decoded_images.append(dec_img)
        except:
            print("ERROR: Error decoding image result from VDMS")
            raise
            decoded_images = []

        if counter_bad_img > 1:
            print("WARNING:", counter_bad_img * 100 / len(decoded_images),
                  "% of the images are empty")

        out_dict = {
            'response_len':  len(decoded_images),
            'response_time': total_time,
            'metadata_perc': 0,
        }

        if return_images:
            out_dict["decoded_images"] = decoded_images

        return out_dict
