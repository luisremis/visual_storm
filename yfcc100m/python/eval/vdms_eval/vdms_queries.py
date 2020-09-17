import os.path

import VDMSQuery

def display_images(imgs):
    from IPython.display import Image, display
    counter = 0
    for im in imgs:
        img_file = 'images/results_' + str(counter) + '.jpg'
        counter = counter + 1
        fd = open(img_file, 'wb+')
        fd.write(im)
        fd.close()
        display(Image(img_file))

resize = {
    "type": "resize",
    "width": 224,
    "height": 224
}

get_imgs = False

qh = VDMSQuery.VDMSQuery("sky4.local", 55501)

probability = 0.9
latitude  = -14.354356
longitude = -39.002567

print('\nQuery metadata with autotags: alligator>=', probability, 'OR lake>=', probability)
print('Num IDs: ',len(qh.get_metadata_by_tags(["alligator", "lake"], [probability, probability], comptype='or')))
if get_imgs:
    print('Query images with autotags: alligator>=', probability, 'OR lake>=', probability)
    res = qh.get_images_by_tags(["alligator", "lake"], [probability, probability], [resize], comptype='or')
    print(len(res))

print('\nQuery metadata with autotags: alligator>=', probability, 'AND lake>=', probability)
print('Num IDs: ',len(qh.get_metadata_by_tags(["alligator", "lake"], [probability, probability])))
if get_imgs:
    print('Query images with autotags: alligator>=', probability, 'AND lake>=', probability)
    qh.get_images_by_tags(["alligator", "lake"], [probability, probability], [resize])

print('\nQuery metadata with autotags: alligator>=', probability, 'AND lake>=', probability, 'within 20 of lat',  latitude, ', long',  longitude)
print('Num IDs: ',len(qh.get_metadata_by_tags(["alligator", "lake"], [probability, probability], latitude, longitude, 20)))
if get_imgs:
    print('Query images with autotags: alligator>=', probability, 'AND lake>=', probability, 'within 20 of lat',  latitude, ', long',  longitude)
    qh.get_images_by_tags(["alligator", "lake"], [probability, probability], [resize], latitude, longitude, 20)

print('\nQuery metadata with autotags: alligator>=', probability)
print('Num IDs: ',len(qh.get_metadata_by_tags(["alligator"], [probability] )))
if get_imgs:
    print('Query images with autotags: alligator>=', probability)
    qh.get_images_by_tags(["alligator"], [probability], [resize])
    # display_images([img for img in blobs if img])

probability = 0.5

print('\nQuery metadata with autotags: pizza>=', probability , 'AND wine>=', probability)
print('Num IDs: ', len(qh.get_metadata_by_tags(["pizza", "wine"], [probability, probability] )))
if get_imgs:
    print('Query images with autotags: pizza>=', probability , 'AND wine>=', probability)
    qh.get_images_by_tags(["pizza", "wine"], [probability, probability], [resize])

# print("Query Images:")
# display_images(imgs)

# img, fv = get_image_fv(3063512791)
# img     = get_image(3063512791)

# print("Query BImage:")
# display_images([img])

# arr = np.frombuffer(fv, dtype='float32')
# print("Result fv:", arr)

# imgs = get_similar_images(fv, 8)
