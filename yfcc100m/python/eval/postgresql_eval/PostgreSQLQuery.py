import psycopg2
from urllib.parse import urlparse
import time
import os
import cv2
import random
import numpy as np
import requests

IMG_HOST = 'sky4.local'

def create_dir(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

class PostgreSQL(object):
    def __init__(self, params):
        self.db = self.get_connection(params)
        self.db_cursor = self.db.cursor()

    def close_connection(self):
        self.db.close()
        self.db_cursor.close()

    def get_connection(self, params):
        return psycopg2.connect(host=params.db_host, user=params.db_user,
                            password=params.db_pswd, port=params.db_port,
                            dbname="yfcc_" + params.db_name)


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

        print("Error - PostgreSQLQueries - Query nor found:", key)
        exit()


    def get_metadata(self, tags, probs,
                             lat=-1, long=-1,
                             range_dist=0,
                             comptype='and',
                             return_responses=False):

        if lat not in [-1, 999.9999999]:
            location_qstr = '''(latitude >= {} AND latitude <= {}) AND (longitude >= {} AND longitude <= {})'''.format(lat-range_dist*1.0,lat+range_dist*1.0,long-range_dist*1.0,long+range_dist*1.0)

            qstr = ['''id IN (select id from (test_metadata INNER JOIN test_autotags a on test_metadata.id=a.metadataid and a.probability >={} AND a.tagid=(select test_taglist.tagid from test_taglist where test_taglist.tag='{}' limit 1)))'''.format(prob, tag) for prob,tag in zip(probs, tags)]

            query = '''SELECT line_number, download_url, id, latitude, longitude, license_name FROM test_metadata WHERE {} AND ({})'''.format(location_qstr, ''' {} '''.format(comptype.upper()).join(qstr))
        else:
            qstr = ['''id IN (select id from (test_metadata INNER JOIN test_autotags a on test_metadata.id=a.metadataid and a.probability >={} AND a.tagid=(select test_taglist.tagid from test_taglist where test_taglist.tag='{}' limit 1) ) )'''.format(prob, tag) for prob,tag in zip(probs, tags)]

            query = '''SELECT line_number, download_url, id, latitude, longitude, license_name FROM test_metadata WHERE {}'''.format(''' {} '''.format(comptype.upper()).join(qstr))

        start_t = time.time()
        self.db_cursor.execute(query)
        response = self.db_cursor.fetchall()
        endtime = time.time() - start_t

        if return_responses:
            return response

        out_dict = {'response_len':len(response),'response_time':endtime}

        return out_dict

    def rotate_image(self, image, angle):
      image_center = tuple(np.array(image.shape[1::-1]) / 2)
      rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
      result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
      return result

    def get_images(self, tags, probs, operations = [],
                           lat=-1, long=-1, range_dist=0, return_images=False, comptype='and'):
        start = time.time()
        metadata = self.get_metadata(tags, probs,
                                     lat, long, range_dist,
                                     comptype=comptype,
                                     return_responses=True)
        metadata_time = time.time() - start

        img_array = []
        cols = ['line_number', 'download_url', 'id',
                'latitude', 'longitude', 'license_name']

        for res in metadata:

            imgPath = "http://"+IMG_HOST+"/images/" + urlparse(res[cols.index('download_url')]).path

            try:
                imgdata = requests.get(imgPath)

                img = np.frombuffer(imgdata.content, dtype='uint8')

                # Warning -> cv2.imdecode returns None for some images
                # This seems to be fixed, but a possible source or error.
                decoded_img = cv2.imdecode(img, cv2.IMREAD_COLOR)

                # Check image is correct
                decoded_img = decoded_img if decoded_img is not None else img

                # Apply operations, if any
                for op in operations:
                    if op["type"] == "resize":

                        height = op["height"]
                        width  = op["width"]

                        if height and width:
                            decoded_img = cv2.resize(decoded_img, dsize=(width, height))
                        else:
                            print("ERROR - Resize parameters not defined!")

                    if op["type"] == "rotate":

                        angle = op["angle"]

                        if angle:
                            decoded_img = self.rotate_image(decoded_img, angle)
                        else:
                            print("ERROR - Resize parameters not defined!")

            except:
                print("Error processing image:", imgPath)
                decoded_img = None

            img_array.append(decoded_img)

        total_time = time.time() - start

        out_dict = {
            'response_len':  len(img_array),
            'response_time': total_time,
            'metadata_perc': metadata_time / total_time,
        }

        if return_images:
            out_dict["decoded_images"] = decoded_images

        return out_dict
