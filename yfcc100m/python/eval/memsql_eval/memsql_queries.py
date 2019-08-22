import MemSQLQuery
from collections import namedtuple
import os
import time

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

def build_db(params):
    """
    Build database
    """
    import subprocess
    db_size = PORT_MAPPING[params.db_name]
    cmd = "python3 build_yfcc_db_memsql.py -data_file '/mnt/yfcc100m/metadata/processed/yfcc100m_photo_" + \
          "dataset_{}' -tag_file '/mnt/yfcc100m/metadata/processed/yfcc100m_photo_autotags_{}_extended' ".format(db_size, db_size) + \
          "-db_name '{}' -db_host '{}' -db_port {} -db_user '{}' -db_pswd '{}'".format(params.db_name, params.db_host,
              params.db_port, params.db_user, params.db_pswd)
    subprocess.run(cmd, shell=True)

def drop_database(params):
    with database.connect(host=params.db_host, port=params.db_port,
                                  user=params.db_user, password=params.db_pswd,
                                  database=params.db_name) as conn:
                conn.query('DROP DATABASE %s' % params.db_name)

args = {'db_name':'yfcc_100k',
        'db_host':'sky3.jf.intel.com',
        'db_port': 3306,
        'db_user': 'root',
        'db_pswd': '',
        'build_db': False,
        'cleanup': False}

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
    qh = MemSQLQuery.MemSQL(params)
except:
    build_db(params)
    print('\n')
    qh = MemSQLQuery.MemSQL(params)

print('Query metadata with autotags: alligator>=0.2 AND lake>=0.2')
qh.get_metadata_by_tags(["alligator", "lake"], [0.2, 0.2])
print('Query images with autotags: alligator>=0.2 AND lake>=0.2')
qh.get_images_by_tags(["alligator", "lake"], [0.2, 0.2], [resize])

print('Query metadata with autotags: alligator>=0.2 AND lake>=0.2 within 20 of lat -14.354356, long -39.002567')
qh.get_metadata_by_tags(["alligator", "lake"], [0.2, 0.2], -14.354356, -39.002567, 20)
print('Query images with autotags: alligator>=0.2 AND lake>=0.2 within 20 of lat -14.354356, long -39.002567')
qh.get_images_by_tags(["alligator", "lake"], [0.2, 0.2], [resize], -14.354356, -39.002567, 20)

print('Query metadata with autotags: alligator>=0.2')
qh.get_metadata_by_tags(["alligator"], [0.2] )
print('Query images with autotags: alligator>=0.2')
qh.get_images_by_tags(["alligator"], [0.2], [resize])
# display_images([img for img in blobs if img])

print('Query metadata with autotags: pizza>=0.5 AND wine>=0.5')
qh.get_metadata_by_tags(["pizza", "wine"], [0.5, 0.5] )
print('Query images with autotags: pizza>=0.5 AND wine>=0.5')
qh.get_images_by_tags(["pizza", "wine"], [0.5, 0.5], [resize])

# DROP Database
if args['cleanup']:
    drop_database(params)
    print('Removed database')

# display_images(imgs)
