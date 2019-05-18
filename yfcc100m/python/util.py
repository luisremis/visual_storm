import os.path

property_names = ['Line number', 'ID', 'Hash', 'User NSID',
                  'User nickname', 'Date taken', 'Date uploaded', 'Capture device',
                  'Title', 'Description', 'User tags', 'Machine tags',
                  'Longitude', 'Latitude', 'Coord. Accuracy', 'Page URL',
                  'Download URL', 'License name', 'License URL',
                  'Server ID', 'Farm ID', 'Secret', 'Secret original',
                  'Extension', 'Marker']


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
            props[key] = int(row_data[key]) if key == 'ID' else str(row_data[key])
    props["VD:imgPath"] = 'db/images/jpg' + urlparse(props['Download URL']).path
    props["format"] = props['Extension']

    query = {}
    add_entity = {"class": "VD:IMG", "properties": props}
    query["AddEntity"] = add_entity
    res = database.query([query])
    results[index] = res[0][0]['AddEntity']["status"]


def add_autotag_connection(index, database, row_data, results):
    import pandas as pd
    all_queries = []

    # Find Image
    parentref = 10
    query = {}
    find_image = {'constraints': {'ID': ["==", row_data['ID']]}, "_ref": parentref}
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
    except:
        results[index] = -1

    results[index] = 0


def display_images(imgs):
    from IPython.display import Image, display
    for im in imgs:
        display(Image(im))
