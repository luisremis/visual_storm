import MySQLQuery
from collections import namedtuple
import os
import time

import mysql.connector

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

def build_db(params):
    """
    Build database
    """
    import subprocess
    db_size = PORT_MAPPING[params.db_name]
    cmd = "python3 build_yfcc_db_mysql.py -data_file '/mnt/yfcc100m/metadata/processed/yfcc100m_photo_" + \
          "dataset_{}' -tag_file '/mnt/yfcc100m/metadata/processed/yfcc100m_photo_autotags_{}_extended' ".format(db_size, db_size) + \
          "-db_name '{}' -db_host '{}' -db_port {} -db_user '{}' -db_pswd '{}'".format(params.db_name, params.db_host,
              params.db_port, params.db_user, params.db_pswd)
    subprocess.run(cmd, shell=True)

def drop_database(params):
    conn = util.get_connection(params)
    db_cursor = conn.cursor()
    db_cursor.execute('DROP DATABASE %s' % params.db_name)
    db_cursor.close()
    conn.close()

args = {'db_name':'1M',
        'db_host':"127.0.0.1", #'sky3.jf.intel.com',
        'db_port': 3360,
        'db_user': 'root',
        'db_pswd': '',
        'build_db': False,
        'cleanup': False,
        'get_imgs': True}

resize = {
    "type": "resize",
    "width": 224,
    "height": 224
}
PORT_MAPPING = {'yfcc_100k': '100k', 'yfcc_1M': '1M', 'yfcc_10M': '10M'}
params = namedtuple("Arguments", args.keys())(*args.values())

# Build database
if args['build_db']:
    build_db(params)
    print('\n')

try:
    qh = MySQLQuery.MySQL(params)
except:
    build_db(params)
    print('\n')
    qh = MySQLQuery.MySQL(params)

probability = 0.9
latitude  = -14.354356
longitude = -39.002567

print('\nQuery metadata with autotags: alligator>=', probability, 'OR lake>=', probability)
print('Num IDs: ',len(qh.get_metadata_by_tags(["alligator", "lake"], [probability, probability], comptype='or')))
if args['get_imgs']:
    print('Query images with autotags: alligator>=', probability, 'OR lake>=', probability)
    res = qh.get_images_by_tags(["alligator", "lake"], [probability, probability], [resize], comptype='or')
    print(len(res))

print('\nQuery metadata with autotags: alligator>=', probability, 'AND lake>=', probability)
print('Num IDs: ',len(qh.get_metadata_by_tags(["alligator", "lake"], [probability, probability])))
if args['get_imgs']:
    print('Query images with autotags: alligator>=', probability, 'AND lake>=', probability)
    qh.get_images_by_tags(["alligator", "lake"], [probability, probability], [resize])

print('\nQuery metadata with autotags: alligator>=', probability, 'AND lake>=', probability, 'within 20 of lat',  latitude, ', long',  longitude)
print('Num IDs: ',len(qh.get_metadata_by_tags(["alligator", "lake"], [probability, probability], latitude, longitude, 20)))
if args['get_imgs']:
    print('Query images with autotags: alligator>=', probability, 'AND lake>=', probability, 'within 20 of lat',  latitude, ', long',  longitude)
    qh.get_images_by_tags(["alligator", "lake"], [probability, probability], [resize], latitude, longitude, 20)

print('\nQuery metadata with autotags: alligator>=', probability)
print('Num IDs: ',len(qh.get_metadata_by_tags(["alligator"], [probability] )))
if args['get_imgs']:
    print('Query images with autotags: alligator>=', probability)
    qh.get_images_by_tags(["alligator"], [probability], [resize])
    # display_images([img for img in blobs if img])

probability = 0.5

print('\nQuery metadata with autotags: pizza>=', probability , 'AND wine>=', probability)
print('Num IDs: ', len(qh.get_metadata_by_tags(["pizza", "wine"], [probability, probability] )))
if args['get_imgs']:
    print('Query images with autotags: pizza>=', probability , 'AND wine>=', probability)
    qh.get_images_by_tags(["pizza", "wine"], [probability, probability], [resize])


qh.close_connection()

# DROP Database
if args['cleanup']:
    drop_database(params)
    print('Removed database')

# display_images(imgs)
