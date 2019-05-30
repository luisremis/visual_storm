import os.path
import logging
import numpy as np


""" General functions """
property_names = ['Line number', 'ID', 'Hash', 'User NSID',
                  'User nickname', 'Date taken', 'Date uploaded', 'Capture device',
                  'Title', 'Description', 'User tags', 'Machine tags',
                  'Longitude', 'Latitude', 'Coord. Accuracy', 'Page URL',
                  'Download URL', 'License name', 'License URL',
                  'Server ID', 'Farm ID', 'Secret', 'Secret original',
                  'Extension', 'Marker']


def display_images(imgs):
    from IPython.display import Image, display
    for im in imgs:
        display(Image(im))


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
        
    all_queries = []
    for ix, row in enumerate(tag):
        query = {}
        add_entity = {"class": 'autotags', "properties": {"name": row}}
        query["AddEntity"] = add_entity
        all_queries.append(query)
    
    redo_flag = True
    cnt = 0
    while redo_flag is True and cnt < 5:
        res = database.query(all_queries)
        redo_flag = check_status(res)
        cnt += 1


def add_image_entity_batch(index, index2, database, row_data, results):
    from pandas import isna
    from urllib.parse import urlparse
    
    def check_status(response):
        redo = False
        for ix, b in enumerate(range(index, index2)):
            try:
                results[b] = response[0][ix]['AddEntity']["status"]
            except:
                results[b] = -1
                redo = True
                break
        return redo
    
    all_queries = []
    for ix, row in row_data.iterrows():
        # Set Metadata as properties
        props = {}
        for key in property_names:
            if not isna(row[key]):
                props[key] = int(row[key]) if key == 'ID' else str(row[key])
        props["VD:imgPath"] = 'db/images/jpg' + urlparse(props['Download URL']).path
        props["format"] = "jpg"

        query = {}
        add_entity = {"class": "VD:IMG", "properties": props}
        query["AddEntity"] = add_entity
        all_queries.append(query)
    
    redo_flag = True
    cnt = 0
    while redo_flag is True and cnt < 5:
        res = database.query(all_queries)
        redo_flag = check_status(res)
        cnt += 1


def add_autotag_connection_batch(index, database, row_data, results):
    import pandas as pd
    
    def check_status(response, indices):
        redo = False
        for rix, n in enumerate(indices):
            tmp = response[n[0] : n[1]]
            try:
                for i in range(len(tmp)):
                    cmd = list(tmp[i][0].items())[0][0]
                    assert tmp[i][0][cmd]["status"] == 0
                results[index + rix] = 0        
            except:
                results[index + rix] = -1
                redo = True
                break
        return redo
    
    run_index = []
    num_queries = 0
    for rix, row in row_data.iterrows():
        # Find Tag
        if not pd.isna(row['autotags']):
            ind = [None, None]
            all_queries = []
            # Find Image
            parentref = 1000 * rix
            query = {}
            find_image = {'constraints': {'ID': ["==", int(row['ID'])]}, "_ref": parentref}
            query["FindImage"] = find_image
            all_queries.append(query)
            ind[0] = num_queries            
            num_queries +=1
            
            current_tags = row['autotags'].split(',')
            for ix, t in enumerate(current_tags):
                val = t.split(':')
                this_ref = parentref + ix + 1

                # Find Tag 
                query = {}
                find_entity = {"class": 'autotags', "_ref": this_ref, "constraints": {'name': ["==", val[0]]}}
                query["FindEntity"] = find_entity
                all_queries.append(query)
                num_queries +=1

                # Add Connection
                query = {}
                add_connection = {"class": 'tag', "ref1": parentref, "ref2": this_ref,
                                  "properties": {"tag_name": val[0], 'tag_prob': float(val[1]),
                                                 "MetaDataID": int(row['ID'])}}
                query["AddConnection"] = add_connection
                all_queries.append(query)
                ind[1] = num_queries
                num_queries +=1
            run_index.append(ind)
    
    redo_flag = True
    cnt = 0
    while redo_flag is True and cnt < 5:
        res = database.query(all_queries)
        redo_flag = check_status(res, run_index)
        cnt += 1


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
    find_image = {'constraints': {'ID': ["==", int(row_data['ID'])]}, "_ref": parentref}
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
            find_entity = {"class": 'autotags', "_ref": this_ref, "constraints": {'name': ["==", val[0]]}}
            query["FindEntity"] = find_entity
            all_queries.append(query)

            # Add Connection
            query = {}
            add_connection = {"class": 'tag', "ref1": parentref, "ref2": this_ref,
                              "properties": {"tag_name": val[0], 'tag_prob': float(val[1]),
                                             "MetaDataID": int(row_data['ID'])}}
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

