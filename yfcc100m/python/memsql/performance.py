import argparse
import random
from pathlib import Path
import time
from memsql.common import database
import subprocess
from threading import Thread
import random

import pandas as pd
import cv2
import numpy as np
import build_yfcc_db_memsql
# import util
from urllib.parse import urlparse
from PIL import Image as PImage
import matplotlib.pyplot as plt
import MemSQLQuery

RANDOM_SEED_VALUE = 12
NUM_TRANSACTIONS = 10
NUM_ITERATIONS = 10
NUM_THREADS = 10


def get_args():
    obj = argparse.ArgumentParser()

    # Pool of autotags
    obj.add_argument('-autotag_pool', type=str, default='autotags_100k_GT_80',
                     help='File containing a pool of autotags for measurements which are chosen at random')

    # Database Info
    obj.add_argument('-db_name', type=str, default='yfcc_100k', #required=True,
                     help='Comma separated list of database names')
    obj.add_argument('-db_host', type=str, default='sky3.jf.intel.com', #required=True,
                     help='Name of memsql host')
    obj.add_argument('-db_port', type=int, default=3306,
                     help='Port of memsql [default: 3306]')
    obj.add_argument('-db_user', type=str, default='root',
                     help='Username of database [default: root]')
    obj.add_argument('-db_pswd', type=str, default='',
                     help='Password of database [default: ""]')

    # Output CSV
    obj.add_argument('-out', type=str, default='memsql_measurements_100trans.csv', 
                     help='CSV Filename for measurements [default: memsql_measurements_100trans.csv]')
    params = obj.parse_args()

    params.db_name = params.db_name.split(',')

    return params
    
    
def rebuild_db(db, params):
    db_size = db.split('_')[-1]
    cmd = "python3 build_yfcc_db_memsql.py -data_file '/mnt/data/metadata/yfcc100m_short/yfcc100m_photo_dataset_{}' -tag_file '/mnt/data/metadata/yfcc100m_short/yfcc100m_photo_autotags_{}' -db_name '{}' -db_host '{}' -db_port {} -db_user '{}' -db_pswd '{}'".format(db_size,
    db_size, db, params.db_host, params.db_port,
    params.db_user, params.db_pswd)
    subprocess.run(cmd, shell=True)

    
def get_metadata(memsql_obj, taglist, thresh):
    def get_thread_metadata(memsql_obj, idx, metadata_results, list_of_tags, prob_thresh): 
        random_tags = random.sample(list_of_tags, NUM_TRANSACTIONS)

        for ix, tag in enumerate(random_tags):
            metadata = memsql_obj.get_metadata_by_tag( [tag], [prob_thresh])#conn,
            print('\t\t\tTAG:{} ({} entries returned)'.format(tag,len(metadata)))
            metadata_results[idx + ix] = metadata
        # return metadata_results
    
    thread_arr = []            
    metadata_results = [None] * (NUM_THREADS * NUM_TRANSACTIONS)
    random.seed(RANDOM_SEED_VALUE)
    for thread in range(NUM_THREADS): # Number of threads processing at once
        print('\t\tMETADATA THREAD: {}'.format(thread))
        idx = (thread * NUM_TRANSACTIONS)
        # Get NUM_TRANSACTIONS random autotags for measurements 
        # metadata_results = get_thread_metadata(memsql_obj, idx, metadata_results, taglist, thresh)
        thread_add = Thread(target=get_thread_metadata, args=(memsql_obj, idx, metadata_results, taglist, thresh))
        thread_add.start()
        thread_arr.append(thread_add)
    for thread in thread_arr:
        thread.join()  
    return metadata_results
   
    
def get_images(memsql_obj, height, width, metadata_results):
    def get_thread_images(memsql_obj, idx, metadata_results, height, width, imgdata_results): 
        for ix in range(NUM_TRANSACTIONS):
            if metadata_results[idx+ix] is not None:
                imgdata = memsql_obj.get_images_from_query(metadata_results[idx+ix], height, width)
                print('\t\t\tTx:{} ({} images returned)'.format(ix,len([img for img in imgdata if img is not None])))
            else:
                imgdata = None
            imgdata_results[idx + ix] = imgdata
        # return imgdata_results
    
    thread_arr = []            
    imgdata_results = [None] * (NUM_THREADS * NUM_TRANSACTIONS)
    # height, width = 224, 224
    random.seed(RANDOM_SEED_VALUE)
    for thread in range(NUM_THREADS): # Number of threads processing at once
        print('\t\tIMG THREAD: {}'.format(thread))
        idx = (thread * NUM_TRANSACTIONS)
        
        # imgdata_results = get_thread_images(memsql_obj, idx, metadata_results, height, width, imgdata_results)
        thread_add = Thread(target=get_thread_images, args=(memsql_obj, idx, metadata_results, height, width, imgdata_results))
        thread_add.start()
        thread_arr.append(thread_add)
    for thread in thread_arr:
        thread.join()    
    return imgdata_results
 

def add_performance_row(perf_df, database, groupname, statname, statvalue):
    perf_df.at[statname + '_' + groupname, database] = statvalue
    perf_df.at[statname + '_' + groupname, 'Query'] = groupname
    perf_df.at[statname + '_' + groupname, 'Stat'] = statname
    return perf_df
    
    
def main(params):    
    taglist = Path(params.autotag_pool).read_text().split('\n')
    thresh = 0.8
    
    # Prepare table of measurements
    performance = pd.DataFrame(columns=['Query', 'Stat'] + params.db_name)
    
    for db in params.db_name:  # Process each database separately
        print('DATABASE: {}'.format(db))
        all_tx_per_sec = []
        all_img_per_sec = []
        for iteration in range(NUM_ITERATIONS):  # Number of times to average
            print('\tITERATION: {}'.format(iteration))
            memsql_obj = MemSQLQuery.MemSQL(db, params)
            
            # Rebuild database
            # rebuild_start = time.time()
            # memsql_obj.rebuild_db()
            # rebuild_end = time.time() - rebuild_start
            # print('[!] Total elapsed time: {:0.4f} secs'.format(rebuild_end))            
            
            #Get Metadata
            start_t = time.time()   
            metadata_results = get_metadata(memsql_obj, taglist, thresh)            
            end_time_metadata = time.time() - start_t
            
            # Metadata transactions per sec
            tx_per_sec = (NUM_TRANSACTIONS * NUM_THREADS) / end_time_metadata
            all_tx_per_sec.append(tx_per_sec)
            
            # Use results to get Image data and resize
            start_t = time.time()
            height, width = 224, 224
            imgdata_results = get_images(memsql_obj, height, width, metadata_results)
            end_time_img = time.time() - start_t
                        
            # Images per sec
            num_images = np.sum([len([img for img in entry if img is not None]) for entry in imgdata_results if entry is not None])
            img_per_sec = num_images / end_time_img
            all_img_per_sec.append(img_per_sec)
            
        avg_tx_per_sec = np.mean(all_tx_per_sec)
        avg_img_per_sec = np.mean(all_img_per_sec)
        
        # Print info
        print('\t[!] Avg. Metadata Transactions per sec: {:0.4f}'.format(avg_tx_per_sec))
        print('\t[!] Avg. Images per sec: {:0.4f}'.format(avg_img_per_sec))
        
        # Log Measurements                                  
        performance = add_performance_row(performance, db, 'tagsGT0.8', 'Avg. Tx/sec', avg_tx_per_sec)                              
        performance = add_performance_row(performance, db, 'tagsGT0.8', 'Avg. Images/sec', avg_img_per_sec)
        performance.to_csv(params.out)    


if __name__ == '__main__':
    args = get_args()
    main(args)

