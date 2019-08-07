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


qh = VDMSQuery.VDMSQuery("sky3.jf.intel.com", 55500)

qh.get_image_by_tags(["alligator", "lake"], [0.2, 0.2])

qh.get_image_by_tags(["alligator", "lake"], [0.2, 0.2], -14.354356, -39.002567, 20)
# qh.get_image_by_tags(["alligator"], [0.9])

# print("Query Images:")
# display_images(imgs)

# img, fv = get_image_fv(3063512791)
# img     = get_image(3063512791)

# print("Query BImage:")
# display_images([img])

# arr = np.frombuffer(fv, dtype='float32')
# print("Result fv:", arr)

# imgs = get_similar_images(fv, 8)
