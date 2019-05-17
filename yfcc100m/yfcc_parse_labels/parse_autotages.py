import json
import os.path
import subprocess

def split_str(s, n):
    length = len(s)
    return [ s[i:i+n] for i in range(0, length, n) ]

def extract_metadata(elems):
    if len(elems)<2: return None
    text = elems[1]
    text_split = text.split(',')
    d = dict()
    for elem in text_split:
        key = elem.split(':')[0]
        val = elem.split(':')[1]
        d[key] = val
    return d

def extract_metadata_d(elems):
    if len(elems)<25: return None
    d = dict()
    d['photo_hash'] = elems[2]
    d['user_id'] = elems[3]
    d['user_nickname'] = elems[4]
    d['date_taken'] = elems[5]
    d['date_uploaded'] = elems[6]
    d['capture_device'] = elems[7]
    d['title'] = elems[8]
    d['description'] = elems[9]
    d['user_tags'] = elems[10]
    d['machine_tags'] = elems[11]
    d['longitude'] = elems[12]
    d['latitude'] = elems[13]
    d['pos_accuracy'] = elems[14]
    d['url_show'] = elems[15]
    d['url_get'] = elems[16]
    d['license_name'] = elems[17]
    d['license_url'] = elems[18]
    d['server_id'] = elems[19]
    d['farm_id'] = elems[20]
    d['photo_secret'] = elems[21]
    d['photo_secret_orig'] = elems[22]
    d['photo_ext'] = elems[23]
    d['photo_or_video'] = elems[24]
    return d

fin_autotag = open('/data/yfcc100m/set_0/data_0/metadata/original/yfcc100m_autotags')

tags_dicc = {}
flag_done = False

while True:
    # read lines
    line_a = fin_autotag.readline()
    if (not line_a):
        break
    line_a_split = line_a.strip().split('\t')

    # extract metadata
    autotags = extract_metadata(line_a_split)

    if autotags != None:
    	for tag in autotags:
		if not tags_dicc.has_key(tag):
			tags_dicc[tag] = 1
			print(len(tags_dicc))
			if (len(tags_dicc) == 1570):
				flag_done = True
				break

    if (flag_done == True):
	break

print("Done :)")

output = open("autotag_list.txt", "w+")

for tag in tags_dicc:
    output.write(tag)
    output.write("\n")


