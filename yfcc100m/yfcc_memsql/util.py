import os.path
import logging
import numpy as np
import math
import time
from memsql.common import database
import cv2
import requests
from pandas import isna
from urllib.parse import urlparse
import IPython


""" General functions """
property_names = ['Line number', 'ID', 'Hash', 'User NSID',
                  'User nickname', 'Date taken', 'Date uploaded',
                  'Capture device',
                  'Title', 'Description', 'User tags', 'Machine tags',
                  'Longitude', 'Latitude', 'Coord. Accuracy', 'Page URL',
                  'Download URL', 'License name', 'License URL',
                  'Server ID', 'Farm ID', 'Secret', 'Secret original',
                  'Extension', 'Marker']
property_names_sql = ['line_number','id', 'hash', 'user_nsid', 'user_nickname',
            'date_taken', 'date_uploaded', 'capture_device', 'title', 'description', 
            'user_tags', 'machine_tags', 'longitude', 'latitude', 'coord_accuracy', 
            'page_url', 'download_url', 'license_name', 'license_url', 'server_id', 
            'farm_id', 'secret', 'secret_original', 'extension', 'marker',
            'imgPath', 'imgBlob', 'format']
tag_property_names=['ID', 'autotags']

num_imgs_per_data_dir = 8400000
folder_choices = ['/mnt/data/set_0/data_0/images', '/mnt/data/set_0/data_1/images', '/mnt/data/set_0/data_2/images', '/mnt/data/set_0/data_3/images',
                  '/mnt/data/set_1/data_0/images', '/mnt/data/set_1/data_1/images', '/mnt/data/set_1/data_2/images', '/mnt/data/set_1/data_3/images']


def get_connection(params, db=None):
    if not db:
        db = params.db_name
        
    """ Returns a new connection to the database. """
    return database.connect(host=params.db_host, port=params.db_port, user=params.db_user, password=params.db_pswd, database=db)
   

def read_blob(file):
    # with open(file, 'rb') as f:
        # blob = f.read()
        
    img = requests.get(file)
    blob = np.frombuffer(img.content, dtype='uint8')
    blob = cv2.imdecode(blob,1)
    return blob
    

def add_blob(params, id, file):    
    with get_connection(params) as conn:        
        #define query
        ed_file = 'db/images/jpg' + urlparse(file).path
        query = "UPDATE test_metadata SET imgPath='{}' WHERE id={}".format(ed_file,id)
        args = (file, id)
        conn.execute(query)  
        
        # Read image file
        file = '/usr/share/pixmaps/faces/sunset.jpg'
        
        data = read_blob(file)
        
        #define query
        query = "UPDATE test_metadata SET imgBlob='{}' WHERE id={}".format(data,id)
        conn.execute(query) 
        # args = (data, id)
        # conn.execute(query, args)    
    

def display_images(imgs):
    from IPython.display import Image, display
    for im in imgs:
        display(Image(im))

def display_image_from_path(imgPath, w=None, h=None):
    img = IPython.core.display.Image(imgPath, width=w, height=h)
    if img.data:
        IPython.core.display.display(img)

def query_autotags(interests, host=None, port=3306, user="root",
                          pswd="", db=None):
    start_t = time.time()
    with database.connect(host=host, port=port, user=user,
                          password=pswd, database=db) as conn:
        match_regex = ' AND '.join(['''{}":"$'''.format(key) for key in interests.keys()])
        val_regex = ' AND '.join(['''CONVERT(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(a.autotags,'{}":"',-1),',',1),':',-1),DECIMAL)>=CONVERT({},DECIMAL)'''.format(key, value) for key, value in interests.items()])
        query = '''select b.line_number, b.id, a.autotags, b.download_url from test_autotags a JOIN test_metadata b ON a.id = b.id WHERE match (a.autotags) against ('{}') AND {}'''.format(match_regex, val_regex)
        sql_response = conn.query(query)
        response = []
        for res in sql_response:
#             tags_str = [t for t in res['autotags'].split(',') if any(key in t for key, val in interests.items())]
            
            if all(key in res['autotags'] for key in interests.keys()):
                tags_str = []
                for t in res['autotags'].split(','):
#                     print(t.split(":"))
                    val = t.split(":")                    
                    try:
                        if len(val) == 2: 
                            val[1] = float(val[1]) if val[1] != '' else 0
                            if val[0] in interests and val[1] >= float(interests[val[0]]):
                                tags_str.append(val[0] + ":" + str(val[1]))   
                    except:
                        print(val[0], val[1])
                if tags_str:
                    print('\tID: {}'.format(res['id']))
                    print('\tAutotags: {}'.format(','.join(tags_str)))
                    print('\tdownload_url: {}\n'.format(res['download_url']))
                    response.append(res)
    return response, time.time() - start_t

def get_query_images(sql_response, width=None, height=None):
    start_t = time.time()
    for res in sql_response:
        quotient = int(res['line_number']) // num_imgs_per_data_dir
        imgPath = folder_choices[quotient] + urlparse(res['download_url']).path
        display_image_from_path(imgPath, w=width, h=height)
    return time.time() - start_t

""" Using multiple entries per thread """

def add_autotags_entity_batch(index, database, tag, results):

    def check_status(response):
        redo = False
        for ix, _ in enumerate(tag):
            try:
                results[index + ix] = response[0][ix]['AddEntity']["status"]
            except:
                results[index + ix] = -1
                redo = True
                break
        return redo

    for ix, row in enumerate(tag):
        query = "INSERT INTO test_taglist(idx,tag) VALUES ({},'{:%s}');".format(index + ix, row)
        try:
            database.execute(query)
            results[index + ix] = 0
        except:
            results[index + ix] = -1
    return results


def add_image_to_db(params, database, start, end, row_data, results):
    with get_connection(params, db=database) as conn:
        all_queries = []
        for ix, row in row_data.iterrows():
            # Set Metadata as properties
            props = {}
            file = str(row['Download URL'])
            # file = 'db/images/jpg' + urlparse(str(row['Download URL'])).path
            add_blob(str(row['ID']), file)
            
        for ix, row in row_data.iterrows():
            count = conn.get("SELECT COUNT(*) AS count FROM test_metadata WHERE id={} AND imgPath={}".format(row['ID'], 'db/images/jpg' + urlparse(str(row['Download URL'])).path)).count
            index = int(row['Line number'])
            if count > 0:
                results[index] = 0
            else:
                results[index] = -1
    return results


def add_image_batch_to_db(database, batch_size, start, end, row_data, results):

    rounds = math.ceil((end - start)/ batch_size)

    for i in range(rounds):

        start_r = start + batch_size * i
        if start_r < end:
            end_r   = min(start_r + batch_size , end)
            add_image_to_db(database, start_r, end_r,
                                   row_data.iloc[start_r:end_r, :], results)
        else:
            break
    return results


def add_image_batch_to_db2(database, batch_size, start, end, row_data, results):

    rounds = math.ceil((end - start)/ batch_size)

    for i in range(rounds):

        start_r = start + batch_size * i
        if start_r < end:
            end_r   = min(start_r + batch_size , end)
            add_image_to_db2(database, start_r, end_r,
                                   row_data.iloc[start_r:end_r, :], results)
        else:
            break
    return results
    
    
def add_image_to_db2(params, database, start, end, row_data, results):
    with get_connection(params, db=database) as conn:
        all_tag_count = []
        # all_vals = []
        for ix, row in row_data.iterrows():
            if not isna(row['autotags']):
                current_tags = row['autotags'].split(',')
                all_tag_count.append(len(current_tags))
                all_vals = []
                for ix, t in enumerate(current_tags):
                    val = t.split(':')
                    rowstr = "({},'{}',{})".format(int(row['id']), val[0], val[1])
                    print(rowstr)
                    all_vals.append(rowstr)
                query = "INSERT INTO test_autotags (id,tags,probability) VALUES {}".format(','.join(all_vals))
                try:
                    conn.execute(query)  
                except:
                    print('check query')
            else:
                all_tag_count.append(0)

            
        # query = "INSERT INTO test_autotags (id,autotags,probability) VALUES ({})".format(','.join(all_vals))
        # conn.execute(query)    
                        
        for (ix, row), rc in zip(row_data.iterrows(), all_tag_count):
            count = conn.get("SELECT COUNT(*) AS count FROM test_autotags WHERE id={}".format(row['ID'])).count
            index = start + ix  # int(row['Line number'])
            if count == rc:
                results[index] = 0
            else:
                results[index] = -1
    return results


def add_image_entity_batch(params, database, start, end, row_data, results):
    from pandas import isna
    from urllib.parse import urlparse

    def check_status(connection):
        redo = False
        for ix, b in enumerate(range(start, end)):
            try:
                results[b] = response[0][ix]['AddEntity']["status"]
            except:
                results[b] = -1
                redo = True
                # print(response)
                break
        return redo

    with get_connection(params, db=database) as conn:
        all_queries = []
        for ix, row in row_data.iterrows():
            # Set Metadata as properties
            props = {}
            for key in property_names:
                if not isna(row[key]):
                    props[key] = int(row[key]) if key == 'ID' else str(row[key])
                else:
                    props[key] = ''
                if isinstance(props[key], str) and len(props[key]) > 255:
                    str_len_error = -1
                else:
                    str_len_error = 0
            props["imgPath"] = 'db/images/jpg' + urlparse(props['Download URL']).path
            props["format"] = "jpg"
            
            prop_arr = []
            prop_arr_col = []
            for p, ps in zip(property_names + ["imgPath", "format"], property_names_sql):
                if p in props:
                    prop_arr.append("'{}'".format(props[p]))
                    prop_arr_col.append(ps)
            rowstr = ','.join(prop_arr)
            colstr = ','.join(prop_arr_col)
            query = "INSERT INTO test_metadata ({}) VALUES ({})".format(colstr, rowstr)
            conn.execute(query)
        for ix, row in row_data.iterrows():
            count = conn.get("SELECT SUM(id='{}') AS count FROM test_metadata".format(row['ID'])).count
            index = int(row['Line number'])
            if count > 0 and str_len_error == 0:
                results[index] = 0
            else:
                results[index] = -1
    # return results


def add_image_all_batch(database, batch_size, start, end, row_data, results):

    rounds = math.ceil((end - start)/ batch_size)

    for i in range(rounds):

        start_r = start + batch_size * i
        if start_r < end:
            end_r   = min(start_r + batch_size , end)
            add_image_entity_batch(database, start_r, end_r,
                                   row_data.iloc[start_r:end_r, :], results)
        else:
            break
    # return results

def add_autotag_connection_all_batch(index, batch_size, db,
                                     start, end, row_data, results):

    rounds = math.ceil((end - start)/ batch_size)

    # print("rounds", rounds)
    for i in range(rounds):

        start_r = start + batch_size * i
        if start_r < end:
            end_r   = min(start_r + batch_size , end)
            add_autotag_connection_batch(start_r, db,
                                         row_data, start_r, end_r, results)
        else:
            break

def add_autotag_connection_batch(index, database, row_data, start, end, results):
    import pandas as pd

    def check_status(response, indices):
        redo = False
        for rix, n in enumerate(indices):
            tmp = response[n[0] : n[1]]
            try:
                status = 0
                for i in range(len(tmp)):
                    cmd = list(tmp[0][i].items())[0][0]
                    if tmp[0][i][cmd]["status"] != 0:
                        results[index + rix] = -1
                        break
                results[index + rix] = 0
            except:
                results[index + rix] = -1
                redo = True
                break
        return redo

    t0 = time.time()

    data = row_data.iloc[start:end, :]
    # print("start_r ", start, "end ", end)

    run_index = []
    all_queries = []
    num_queries = 0

    pre = time.time() - t0

    t0 = time.time()

    for rix, row in data.iterrows():
        # Find Tag
        if not pd.isna(row['autotags']):
            ind = [None, None]
            # Find Image
            parentref = (100 * rix) % 19000
            parentref +=1  #Max ref 20000
            query = {}
            findImage = {}
            findImage["_ref"] = parentref
            findImage['constraints'] = {'ID': ["==", int(row['ID'])]}
            findImage['results'] = {"blob": False}
            query["FindImage"] = findImage
            all_queries.append(query)
            ind[0] = num_queries
            num_queries +=1

            current_tags = row['autotags'].split(',')
            for ix, t in enumerate(current_tags):
                val = t.split(':')
                this_ref = parentref + ix + 1

                # Find Tag
                query = {}
                find_entity = {}
                find_entity["_ref"] = this_ref
                find_entity["class"] = 'autotags'
                find_entity["constraints"] = {'name': ["==", val[0]]}
                query["FindEntity"] = find_entity
                all_queries.append(query)
                num_queries +=1

                # Add Connection
                query = {}
                add_connection = {}
                add_connection["class"] = 'tag'
                add_connection["ref1"] = parentref
                add_connection["ref2"] = this_ref
                add_connection["properties"] = {"tag_name": val[0],
                                                "tag_prob": float(val[1]),
                                                "MetaDataID": int(row['ID'])}
                query["AddConnection"] = add_connection
                all_queries.append(query)
                ind[1] = num_queries
                num_queries +=1
            run_index.append(ind)

    make_query = time.time() - t0

    t0 = time.time()

    redo_flag = True
    cnt = 0
    while redo_flag is True and cnt < 40:
        try:
            res = database.query(all_queries)
        except:
            res = [None] * len(all_queries[0])
            print('\tERROR WITH QUERY')
        redo_flag = check_status(res, run_index)
        cnt += 1

    run_query = time.time() - t0


    total_time = pre + make_query + run_query

    # print("pre:", pre / total_time, "make:", make_query/total_time, "run:", run_query/total_time)

""" Using single entry per thread """

def add_autotags_entity(index, database, tag, results):
    query = {}
    add_entity = {"class": 'autotags', "properties": {"name": tag}}
    query["AddEntity"] = add_entity
    res = database.query([query])
    # print('res[0][0]', res[0][0])
    results[index] = res[0][0]['AddEntity']["status"]


def add_image_entity(index, database, row_data, results):
    from pandas import isna
    from urllib.parse import urlparse

    # Set Metadata as properties
    props = {}
    for key in property_names:
        if not isna(row_data[key]):
            # props[key] = str(row_data[key])
            props[key] = int(row_data[key]) if key == 'ID' else str(row_data[key])
    props["VD:imgPath"] = 'db/images/jpg' + urlparse(props['Download URL']).path
    props["format"] = "jpg"

    query = {}
    add_entity = {"class": "VD:IMG", "properties": props}

    query["AddEntity"] = add_entity
    res = database.query([query])
    results[index] = res[0][0]['AddEntity']["status"]


def add_autotag_connection(index, database, row_data, results):
    import pandas as pd
    all_queries = []
    success_counter = 0

    # Find Image
    parentref = 10
    query = {}
    find_image = {
        "_ref": parentref,
        'constraints': {
            'ID': ["==", int(row_data['ID'])]
        }
    }
    query["FindImage"] = find_image
    all_queries.append(query)

    # Find Tag
    if not pd.isna(row_data['autotags']):
        current_tags = row_data['autotags'].split(',')
        for ix, t in enumerate(current_tags):
            val = t.split(':')
            this_ref = parentref + ix + 1

            # Find Tag
            query = {}
            find_entity = {
                "class": 'autotags',
                "_ref": this_ref,
                "constraints": {
                    'name': ["==", val[0]]
                    }
                }

            query["FindEntity"] = find_entity
            all_queries.append(query)

            # Add Connection
            query = {}
            add_connection = {
                    "class": 'tag',
                    "ref1": parentref,
                    "ref2": this_ref,
                    "properties": {
                        "tag_name": val[0],
                        'tag_prob': float(val[1]),
                        "MetaDataID": int(row_data['ID'])
                        }
                    }

            query["AddConnection"] = add_connection
            all_queries.append(query)
    try:
        res = database.query(all_queries)
        for i in range(len(res)):
            cmd = list(res[i][0].items())[0][0]
            assert res[i][0][cmd]["status"] == 0, 0
            # success_counter +=1
        results[index] = 0
        # results[index] = success_counter

    except:
        results[index] = -1

