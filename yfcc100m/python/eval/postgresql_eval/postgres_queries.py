import PostgreSQLQuery
from collections import namedtuple
import os
import time

import psycopg2

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


args = {'db_name':'1M',
        'db_host':"127.0.0.1",
        'db_port': 5432,
        'db_user': 'root',
        'db_pswd': 'password',
        'get_imgs': True}

resize = {
    "type": "resize",
    "width": 224,
    "height": 224
}
PORT_MAPPING = {'yfcc_100k': '100k', 'yfcc_1M': '1M', 'yfcc_10M': '10M'}
params = namedtuple("Arguments", args.keys())(*args.values())
qh = PostgreSQLQuery.PostgreSQL(params)

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

