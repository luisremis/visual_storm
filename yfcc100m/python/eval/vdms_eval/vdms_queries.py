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

qh = VDMSQuery.VDMSQuery("sky4.jf.intel.com", 55500)

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

# print("Query Images:")
# display_images(imgs)

# img, fv = get_image_fv(3063512791)
# img     = get_image(3063512791)

# print("Query BImage:")
# display_images([img])

# arr = np.frombuffer(fv, dtype='float32')
# print("Result fv:", arr)

# imgs = get_similar_images(fv, 8)