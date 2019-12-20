import mysql.connector
from urllib.parse import urlparse
import time
import os
import cv2
import random
import numpy as np
import requests

# These are no longer needed
# NUM_IMGS_PER_DATA_DIR = 8400000
# FOLDER_CHOICES = ['/set_0/data_0/images',
#                   '/set_0/data_1/images',
#                   '/set_0/data_2/images',
#                   '/set_0/data_3/images',
#                   '/set_1/data_0/images',
#                   '/set_1/data_1/images',
#                   '/set_1/data_2/images',
#                   '/set_1/data_3/images']

IMG_HOST = 'sky4.local'

def create_dir(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

class MySQL(object):
    def __init__(self, params):
        self.db = self.get_connection(params)
        # creating database_cursor to perform SQL operation
        self.db_cursor = self.db.cursor()
        
    def close_connection(self):
        self.db.close()
        self.db_cursor.close()         

    def get_connection(self, params):
        return mysql.connector.connect(host=params.db_host, user=params.db_user, passwd=params.db_pswd, port=params.db_port, database="yfcc_" + params.db_name)

    def get_metadata_by_tags(self, tags, probs, lat=-1, long=-1, range_dist=0, return_response=True):
        
        if lat != -1:
            location_qstr = '''(latitude >= {} AND latitude <= {} ) AND (longitude >= {} AND longitude <= {})'''.format(lat-range_dist*1.0,lat+range_dist*1.0,long-range_dist*1.0,long+range_dist*1.0)
            qstr = ['''id IN (select id from (test_metadata INNER JOIN test_autotags a on test_metadata.id=a.metadataid and a.probability >={} AND {} and a.tagid=(select test_taglist.tagid from test_taglist where test_taglist.tag='{}' limit 1)))'''.format(prob, location_qstr, tag) for prob,tag in zip(probs, tags)]
        else:
            qstr = ['''id IN (select id from (test_metadata INNER JOIN test_autotags a on test_metadata.id=a.metadataid and a.probability >={} and a.tagid=(select test_taglist.tagid from test_taglist where test_taglist.tag='{}' limit 1)))'''.format(prob, tag) for prob,tag in zip(probs, tags)]
        
        query = '''SELECT line_number, download_url, id, latitude, longitude, license_name FROM test_metadata WHERE {}'''.format(''' AND '''.join(qstr))

        start_t = time.time()
        self.db_cursor.execute(query)
        response = self.db_cursor.fetchall()
        endtime = time.time() - start_t

        # if response:
            # print(response)
        # print("Time for metadata (ms):", endtime * 1000.0)
        # print("Total results:", len(response))

        # if len(probs) == 1:
        #     out_file = open("perf_results/mysql_img_list.txt", 'w')
        #     cols = ['line_number', 'download_url', 'id', 'latitude', 'longitude', 'license_name']
        #     for res in response:
        #         out_file.write(str(res[cols.index('id')]))
        #         out_file.write("\n")

        if return_response:
            return response

        out_dict = {'response_len':len(response),'response_time':endtime}

        return out_dict

    def get_images_by_tags(self, tags, probs, operations = [],
                           lat=-1, long=-1, range_dist=0, return_images=True):
        start = time.time()
        metadata = self.get_metadata_by_tags(tags, probs, lat, long, range_dist)

        height = operations[0]["height"]
        width = operations[0]["width"]

        img_array = []
        cols = ['line_number', 'download_url', 'id', 'latitude', 'longitude', 'license_name']

        for res in metadata:

            # quotient = int(res[cols.index('line_number')]) // NUM_IMGS_PER_DATA_DIR
            # # imgPath = FOLDER_CHOICES[quotient] + urlparse(res[cols.index('download_url')]).path
            # imgPath = "http://"+IMG_HOST+FOLDER_CHOICES[quotient] + urlparse(res[cols.index('download_url')]).path

            # print(imgPath)
            # print(res[cols.index('id')])

            imgPath = "http://"+IMG_HOST+"/images/" + urlparse(res[cols.index('download_url')]).path

            try:
                # img = np.frombuffer(open(imgPath, 'rb').read(), dtype='uint8')
                imgdata = requests.get(imgPath)
                img = np.frombuffer(imgdata.content, dtype='uint8')

                ## -> cv2.imdecode returns None for some images
                dec_img = cv2.imdecode(img, cv2.IMREAD_COLOR)
                dec_img = dec_img if dec_img is not None else img
                if height and width:
                    resizedimg = cv2.resize(dec_img, dsize=(width, height))
                else:
                    resizedimg = dec_img

                # enc_img = resizedimg
                # enc_img = cv2.imencode(".jpg", img)-> cv2.error: OpenCV(4.1.0) /io/opencv/modules/imgcodecs/src/grfmt_base.cpp:145: error: (-10:Unknown error code -10) Raw image encoder error: Maximum supported image dimension is 65500 pixels in function 'throwOnEror'

                create_dir('/tmp/mysql')
                name = random.randint(0,90000000)
                tmp_file = '/tmp/mysql/img_' + str(name) + ".jpg"
                cv2.imwrite(tmp_file, resizedimg)

                enc_img = open(tmp_file, 'rb').read()

                if os.path.exists(tmp_file):
                    os.remove(tmp_file)

            except:
                print("Error processing image:", imgPath)
                enc_img = None

            img_array.append(enc_img)

        end_time = time.time() - start
        # print("Time for images (ms):", end_time * 1000.0)

        blobs = [img for img in img_array if img]
        # print("Total valid images:", len(blobs))

        if return_images:
            return blobs

        out_dict = {'images_len':len(blobs),'images_time':end_time}

        return out_dict
