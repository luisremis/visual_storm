from memsql.common import database
from urllib.parse import urlparse
import time
import os
import cv2
import numpy as np

NUM_IMGS_PER_DATA_DIR = 8400000
FOLDER_CHOICES = ['/mnt/data/set_0/data_0/images', '/mnt/data/set_0/data_1/images', '/mnt/data/set_0/data_2/images', '/mnt/data/set_0/data_3/images',
                  '/mnt/data/set_1/data_0/images', '/mnt/data/set_1/data_1/images', '/mnt/data/set_1/data_2/images', '/mnt/data/set_1/data_3/images']

def create_dir(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

class MemSQL(object):
    def __init__(self, params):
        self.db = self.get_connection(params)
 
    def get_connection(self, params):
        return database.connect(host=params.db_host, port=params.db_port, 
                            user=params.db_user, password=params.db_pswd,
                            database=params.db_name)
    
    def get_images_from_query(self, metadata, operations,return_images):
        height = operations[0]["height"]
        width = operations[0]["width"]
        
        start_t = time.time()
        img_array = []
        for res in metadata:
            quotient = int(res['line_number']) // NUM_IMGS_PER_DATA_DIR
            imgPath = FOLDER_CHOICES[quotient] + urlparse(res['download_url']).path
            try:
                img = np.frombuffer(open(imgPath, 'rb').read(), dtype='uint8')
                # dec_img = cv2.imdecode(img, cv2.IMREAD_COLOR) # -> returns None for some images
                # dec_img = dec_img if dec_img is not None else img
                if height and width:
                    # from PIL import Image
                    # image = Image.open(io.BytesIO(dec_img))
                    # resizedimg = cv2.resize(dec_img, dsize=(width, height))
                    resizedimg = cv2.resize(img, dsize=(width, height))
                else:
                    resizedimg = img
                
                # enc_img = cv2.imencode(".jpg", img)-> cv2.error: OpenCV(4.1.0) /io/opencv/modules/imgcodecs/src/grfmt_base.cpp:145: error: (-10:Unknown error code -10) Raw image encoder error: Maximum supported image dimension is 65500 pixels in function 'throwOnEror'
                create_dir('tmp')
                tmp_file = 'tmp/' + '_'.join(imgPath.split('/')[-2:])
                cv2.imwrite(tmp_file, resizedimg)
                
                enc_img = open(tmp_file, 'rb').read()
                
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
                    
                # with tempfile.TemporaryFile as tmp:
                    # cv2.imwrite(tmp, resizedimg)
                    # tmp.seek(0)
                    # enc_img = open(tmp, 'rb').read()
                    
            except:
                enc_img = None
            img_array.append(enc_img)
        end_time = time.time() - start_t
        print("Time for images (ms):", end_time * 1000.0)
        
        blobs = [img for img in img_array if img]
        print("Total valid images:", len(blobs))
        
        if return_images:
            return blobs
            
        out_dict = {'images_len':len(blobs),'images_time':end_time}
        
        return out_dict
    
    
    def get_images_by_tags(self, tags, probs, operations = [],
                           lat=-1, long=-1, range_dist=0, return_images=True):
        results = self.get_metadata_by_tags(tags, probs, lat, long, range_dist)        
        
        out_dict = self.get_images_from_query(results, operations, return_images)
        return out_dict       
        
    def get_metadata_by_tags(self, tags, probs, lat=-1, long=-1, range_dist=0, return_response=True):
        # Conversion help: https://stackoverflow.com/a/24372831                    
        # qstr = ['''select b.line_number, b.download_url, b.id, b.latitude, b.longitude, b.license_name from test_taglist c, test_autotags a JOIN test_metadata b ON a.metadataid = b.id WHERE a.tagid=c.idx AND c.tag = '{}' AND a.probability >= {} AND 69.0 * DEGREES(ACOS(LEAST(COS(RADIANS({}))
         # * COS(RADIANS(b.latitude))
         # * COS(RADIANS({} - b.longitude))
         # + SIN(RADIANS({}))
         # * SIN(RADIANS(b.latitude)), 1.0))) <= {}'''.format(tag,prob,lat, long, lat,miles) for tag, prob in zip(tags, probs)] 
        if lat != -1:
            qstr = ['''select b.line_number, b.download_url, b.id, b.latitude, b.longitude, b.license_name from test_taglist c, test_autotags a JOIN test_metadata b ON a.metadataid = b.id WHERE a.tagid=c.idx AND c.tag = '{}' AND a.probability >= {} AND (b.latitude >= {} AND b.latitude <= {}) AND (b.longitude >= {} AND b.longitude <= {})'''.format(tag,prob,-range_dist*1.0,lat+range_dist*1.0,long-range_dist*1.0,long+range_dist*1.0) for tag, prob in zip(tags, probs)]
        else:
            qstr = ['''select b.line_number, b.download_url, b.id, b.latitude, b.longitude, b.license_name from test_taglist c, test_autotags a JOIN test_metadata b ON a.metadataid = b.id WHERE a.tagid=c.idx AND c.tag = '{}' AND a.probability >= {}'''.format(tag,prob) for tag, prob in zip(tags, probs)]
        query = ''' intersect '''.join(qstr) 
        
        start_t = time.time()       
        response = self.db.query(query)    
        endtime = time.time() - start_t
        print("Time for metadata (ms):", endtime * 1000.0) 
        print("Total responses:", len(response))
        if return_response:
            return response
            
        out_dict = {'response_len':len(response),'response_time':endtime}
        return out_dict    
        