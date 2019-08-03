import MemSQLQuery
from collections import namedtuple
import os

from memsql.common import database

def display_images(imgs):
    from IPython.display import Image, display
    img_dir = 'images/'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    counter = 0
    for im in imgs:
        img_file = img_dir + 'results_' + str(counter) + '.jpg'
        counter = counter + 1
        fd = open(img_file, 'wb+')
        fd.write(im)
        fd.close()
        display(Image(img_file))
        

def run_tag_query(list_of_tags, list_of_probabilities, height=None, width=None):
    sql_response = memsql_obj.get_metadata_by_tag(list_of_tags, list_of_probabilities)

    imgs = memsql_obj.get_images_from_query(sql_response, height, width)
    valid_images = [img for img in imgs if img]
    return valid_images


def run_location_query(latitude, longitude, miles, tag, probability, height=None, width=None):
    sql_response = memsql_obj.get_metadata_by_location_and_tag(latitude, longitude, miles, tag, probability)

    imgs = memsql_obj.get_images_from_query(sql_response, height, width)
    valid_images = [img for img in imgs if img]
    return valid_images
    
args = {'db_name':'yfcc_1M',
        'db_host':'sky3.jf.intel.com',
        'db_port': 3306,
        'db_user': 'root',
        'db_pswd': ''} 
        
height, width = 224, 224        
params = namedtuple("Arguments", args.keys())(*args.values())

memsql_obj = MemSQLQuery.MemSQL(params.db_name, params)

print('Query autotags: alligator>=0.8')
imgs = run_tag_query(["alligator"], [0.8], height=height, width=width)

print('Query autotags: alligator>=0.8 AND lake>=0.8')
imgs = run_tag_query(["alligator", "lake"], [0.8, 0.8], height=height, width=width)

print('Query autotags: pizza>=0.5 AND wine>=0.5')
imgs = run_tag_query(["pizza", "wine"], [0.5, 0.5], height=height, width=width)

print('Query location: alligator>=0.8 within 100 miles of 38.9072° N, 77.0369° W (Washington, DC)')
imgs = run_location_query(38.9072, -77.0369, 100, "alligator", 0.8, height=height, width=width)

# display_images(imgs)
