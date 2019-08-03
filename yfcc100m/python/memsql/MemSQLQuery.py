from memsql.common import database
from urllib.parse import urlparse
from PIL import Image as PImage
import matplotlib.pyplot as plt
import cv2
import numpy as np
import subprocess
import geopy.distance

NUM_IMGS_PER_DATA_DIR = 8400000
FOLDER_CHOICES = ['/mnt/data/set_0/data_0/images', '/mnt/data/set_0/data_1/images', '/mnt/data/set_0/data_2/images', '/mnt/data/set_0/data_3/images',
                  '/mnt/data/set_1/data_0/images', '/mnt/data/set_1/data_1/images', '/mnt/data/set_1/data_2/images', '/mnt/data/set_1/data_3/images']

class MemSQL(object):
    def __init__(self, current_db, params):
        self.params = params
        self.db = current_db
        self.conn = None
        
    def rebuild_db(self):
        """
        Rebuilds database to clear cache
        """
        db_size = self.db.split('_')[-1]
        cmd = "python3 build_yfcc_db_memsql.py -data_file '/mnt/data/metadata/yfcc100m_short/yfcc100m_photo_dataset_{}' -tag_file '/mnt/data/metadata/yfcc100m_short/yfcc100m_photo_autotags_{}' -db_name '{}' -db_host '{}' -db_port {} -db_user '{}' -db_pswd '{}'".format(db_size,
        db_size, self.db, self.params.db_host, self.params.db_port,
        self.params.db_user, self.params.db_pswd)
        subprocess.run(cmd, shell=True)
 
    def connect_db(self):
        self.conn = database.connect(host=self.params.db_host, port=self.params.db_port, 
                            user=self.params.db_user, password=self.params.db_pswd,
                            database=self.db)
    
    def get_images_from_query(self, metadata, height, width):
        img_array = []
        for res in metadata:
            quotient = int(res['line_number']) // NUM_IMGS_PER_DATA_DIR
            imgPath = FOLDER_CHOICES[quotient] + urlparse(res['download_url']).path
            try:
                img = np.frombuffer(open(imgPath, 'rb').read(), dtype='uint8')
                dec_img = cv2.imdecode(img, 1) # -> returns None for some images
                dec_img = dec_img if dec_img is not None else img
                if height and width:
                    resizedimg = cv2.resize(dec_img, (width, height))
                else:
                    resizedimg = dec_img
                
                # enc_img = cv2.imencode(".jpg", img)-> cv2.error: OpenCV(4.1.0) /io/opencv/modules/imgcodecs/src/grfmt_base.cpp:145: error: (-10:Unknown error code -10) Raw image encoder error: Maximum supported image dimension is 65500 pixels in function 'throwOnEror'
                tmp_file = "/tmp/tmpimg.jpg"
                cv2.imwrite(tmp_file, resizedimg)
                enc_img = open(tmp_file, 'rb').read()
            except:
                enc_img = None
            img_array.append(enc_img)
        print("Total images:", len([img for img in img_array if img]))
        return img_array
    
    
    def get_metadata_by_tag(self, tag_name, threshold):#, conn
        conn = database.connect(host=self.params.db_host, port=self.params.db_port, 
                            user=self.params.db_user, password=self.params.db_pswd,
                            database=self.db)
                            
        match_regex = '''{}":"$'''.format(tag_name)
        # # val_regex = '''CONVERT(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(a.autotags,'{}":"',-1),',',1),':',-1),DECIMAL)>={}'''.format(tag_name, threshold)
        # # query = r'select b.line_number, b.id, a.autotags, b.longitude, b.latitude, b.download_url from test_autotags a JOIN test_metadata b ON a.id = b.id WHERE match (a.autotags) against ("{}") AND {}'.format(match_regex, val_regex)
        
        # val_regex = '''CONVERT(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(a.autotags,'{}":"',-1),',',1),':',-1),DECIMAL)>={}'''.format(tag_name, threshold)
        # query = '''select b.line_number, b.download_url, a.autotags, b.id, b.latitude, b.longitude, b.license_name from test_autotags a JOIN test_metadata b ON a.id = b.id WHERE match (a.autotags) against ('{}')'''.format(match_regex)
        
        match_regex = ' AND '.join(['''{}":"$'''.format(tag) for tag in tag_name])
        val_regex = ' AND '.join(['''CONVERT(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(a.autotags,'{}":"',-1),',',1),':',-1),DECIMAL)>=CONVERT({},DECIMAL)'''.format(tag, prob) for tag, prob in zip(tag_name, threshold)])
        query = '''select b.line_number, b.id, a.autotags, b.download_url from test_autotags a JOIN test_metadata b ON a.id = b.id WHERE match (a.autotags) against ('{}') AND {}'''.format(match_regex, val_regex)
        
        sql_response = conn.query(query)
        
        # Verify probabilities are >= threshold
        response = []
        for res in sql_response:
            if all(tag in res['autotags'] for tag in tag_name):
                # Extract tag_name and probability
                tags_str = []
                for t in res['autotags'].split(','):
                    val = t.split(":")
                    if len(val) == 2 and val[0] in tag_name:
                        val[1] = float(val[1]) if val[1] != '' else 0
                        tagidx = tag_name.index(val[0])
                        if val[1] >= threshold[tagidx]:
                            tags_str.append(val[0] + ":" + str(val[1]))
                if tags_str:
                    # print('\tID: {}'.format(res['id']))
                    # print('\tAutotags: {}'.format(','.join(tags_str)))
                    # print('\tdownload_url: {}\n'.format(res['download_url']))
                    response.append(res)
        conn.close()
        print("Total results:", len(response))
        return response       
        
    def get_metadata_by_location_and_tag(self, latitude, longitude, miles, tag_name, threshold):#, conn
        conn = database.connect(host=self.params.db_host, port=self.params.db_port, 
                            user=self.params.db_user, password=self.params.db_pswd,
                            database=self.db)
                            
        match_regex = '''{}":"$'''.format(tag_name)
        
        val_regex = '''CONVERT(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(a.autotags,'{}":"',-1),',',1),':',-1),DECIMAL)>={}'''.format(tag_name, threshold)
        
        query = '''select b.line_number, b.download_url, a.autotags, b.id, b.latitude, b.longitude, b.license_name from test_autotags a JOIN test_metadata b ON a.id = b.id WHERE match (a.autotags) against ('{}')'''.format(match_regex)
        
        sql_response = conn.query(query)
        
        # Verify probabilities are >= threshold
        response = []
        for res in sql_response:
            poi = (latitude, longitude)
            coord = (res['latitude'], res['longitude'])
            dist = geopy.distance.vincenty(poi, coord).miles
            if dist <= miles and tag_name in res['autotags']:
                # Extract tag_name and probability
                tags_str = []
                for t in res['autotags'].split(','):
                    val = t.split(":")
                    if len(val) == 2 and val[0] == tag_name:
                        val[1] = float(val[1]) if val[1] != '' else 0
                        
                        if val[1] >= threshold:
                            tags_str.append(val[0] + ":" + str(val[1]))
                if tags_str:
                    # print('\tID: {}'.format(res['id']))
                    # print('\tAutotags: {}'.format(','.join(tags_str)))
                    # print('\tdownload_url: {}\n'.format(res['download_url']))
                    response.append(res)
        conn.close()
        print("Total results:", len(response))
        return response       
        