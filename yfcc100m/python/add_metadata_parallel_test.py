import pandas as pd
from urllib.parse import urlparse
import numpy as np
import os
import datetime
import util
import time
import vdms
import multiprocessing as mp


tag_file = '/data/yfcc100m/set_0/data_0/metadata/yfcc100m_short/yfcc100m_autotags_short'
data_file = '/data/yfcc100m/set_0/data_0/metadata/yfcc100m_short/yfcc100m_dataset_short'
property_names = ['Line number', 'ID', 'Hash', 'User NSID',
                  'User nickname', 'Date taken', 'Date uploaded', 'Capture device',
                  'Title', 'Description', 'User tags', 'Machine tags',
                  'Longitude', 'Latitude', 'Coord. Accuracy', 'Page URL',
                  'Download URL', 'License name', 'License URL',
                  'Server ID', 'Farm ID', 'Secret', 'Secret original',
                  'Extension', 'Marker']


def add_queries(row_ix, row_data, current_tags):  # all_tags):  #, database):
    ex_start_t = time.time()  
    
    database = vdms.vdms()
    database.connect("localhost")
    parentref = 10
    
    # Get query
    all_queries = []

    # Set Metadata as properties
    props = {}
    for key in property_names:
        if not pd.isna(row_data[key]):
            props[key] = str(row_data[key])

    # Add entity for image and set properties to mimic AddImage
    query = {}
    addEntity = {}
    addEntity["class"] = "VD:IMG"
    addEntity["_ref"] = parentref
    props["VD:imgPath"] = 'db/images/jpg' + urlparse(props['Download URL']).path
    props["format"] = props['Extension']
    addEntity["properties"] = props
    addEntity["constraints"] = {'ID': ["==", props['ID']]}
    query["AddEntity"] = addEntity  
    all_queries.append(query)
    
    try:        
        if len(current_tags) > 0:  # Add auto tags
            for ix, t in enumerate(str(current_tags['autotags'].values[0]).split(',')):
                val = t.split(':')
                this_ref = parentref + ix + 1

                # Add 
                query = {}
                addEntity = {}
                addEntity["class"] = 'autotags'
                addEntity["_ref"] = this_ref
                addEntity["constraints"] = {'name': ["==", val[0]]}
                addEntity["properties"] = {"name": val[0]}
                query["AddEntity"] = addEntity  
                all_queries.append(query)

                query = {}
                addConnection = {}
                addConnection["class"] = 'tag' # less than 16
                addConnection["ref1"] = parentref
                addConnection["ref2"] = this_ref
                addConnection["properties"] = {"tag_name": val[0], 'tag_prob': float(val[1]), "MetaDataID": str(row_data['ID'])}
                query["AddConnection"] = addConnection  
                all_queries.append(query)

            res = database.query(all_queries)
            # print(database.get_last_response_str())
            print('[!] Finished autotags for ID == {}'.format(row_data['ID']))
        else:  # No tags to add
            print('[!] No autotags for ID == {}'.format(row_data['ID']))
            
    except:
        print('[!] Skipping autotags for ID == {}'.format(row_data['ID']))
        
    print('Elapsed time for index {} (ID: {}): {}'.format(row_ix, row_data['ID'], time.time() - ex_start_t))

def main():
    num_proc = mp.cpu_count()

    # Import YFCC 100m data
    data = pd.read_csv(data_file, sep='\t', names=property_names)
    tags = pd.read_csv(tag_file, sep='\t', names=['ID', 'autotags'])
    tags.dropna(subset=['autotags'], inplace=True)
    
    # arr = []
    # for i in range(num_proc):
        # db = vdms.vdms()
        # db.connect("localhost")
        # arr.append(db)

    start_t = time.time()
    
    # Serial
    # for ex_ix, example_data in data.iterrows():
        # if ex_ix < 10:
            # add_queries(ex_ix, example_data, tags) #, arr[ex_ix % num_proc])
            
    # with mp.Pool(num_proc) as pool:
        # # result_objects = [pool.apply_async(add_queries, args=(ex_ix,example_data, tags)) for ex_ix, example_data in data.iterrows()]
        # result_objects = [pool.apply_async(add_queries, args=(ex_ix,example_data, tags, arr[ex_ix % num_proc])) for ex_ix, example_data in data.iterrows()]
    # pool.join()
    
    # from joblib import Parallel, delayed
    # res = Parallel(n_jobs=num_proc)(delayed(add_queries)(ex_ix,example_data, tags) for ex_ix, example_data in data.iterrows())
    jobs = []
    p = 1
    for ex_ix, example_data in data.iterrows():
        curr_tags = tags.loc[tags['ID'] == example_data['ID']]
        process = mp.Process(target=add_queries, args=(ex_ix,example_data, curr_tags))
        jobs.append(process)
        p+=1
        if p == num_proc:
            for j in jobs:
                j.start()
            for j in jobs:
                j.join()
            jobs = []
            p = 1
            
    print('Total elapsed time: {}'.format(time.time() - start_t))


if __name__ == "__main__":
    main()
    