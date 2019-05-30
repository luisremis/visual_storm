import pandas as pd
import numpy as np
import time
import logging
import argparse
from threading import Thread

import util
import vdms


def get_args():
    parserobj = argparse.ArgumentParser()
    parserobj.add_argument('-num_threads', type=int, default=64,
                           help='Number of threads to use [default: 64]')
    parserobj.add_argument('-batch_size', type=int, default=1,
                           help='Number of entries per thread [default: 1]')
    parserobj.add_argument('-data_file', type=str,
                           default='/data/yfcc100m/set_0/data_0/metadata/yfcc100m_short/yfcc100m_dataset_short',
                           help='YFCC metadata [default: ' +
                                '/data/yfcc100m/set_0/data_0/metadata/yfcc100m_short/yfcc100m_dataset_short')
    parserobj.add_argument('-tag_list', type=str, default='../yfcc_parse_labels/autotag_list.txt',
                           help='List of expected tags [default: ../yfcc_parse_labels/autotag_list.txt]')
    parserobj.add_argument('-tag_file', type=str,
                           default='/data/yfcc100m/set_0/data_0/metadata/yfcc100m_short/yfcc100m_autotags_short',
                           help='YFCC file of autotags [default: ' +
                                '/data/yfcc100m/set_0/data_0/metadata/yfcc100m_short/yfcc100m_autotags_short]')

    params = parserobj.parse_args()
    return params


def get_data(params):
    yfcc_tags = []
    with open(params.tag_list, 'r') as f:
        for tix, this_tag in enumerate(f):
            yfcc_tags.append(this_tag.strip())

    yfcc_data = pd.read_csv(params.data_file, sep='\t', names=util.property_names)
    tags = pd.read_csv(params.tag_file, sep='\t', names=['ID', 'autotags'])
    yfcc_data = pd.merge(yfcc_data, tags, on='ID')
    return yfcc_data, yfcc_tags


def get_db_list(num):
    dbs = []
    for i in range(0, num):
        db = vdms.vdms()
        db.connect("localhost")
        dbs.append(db)
    return dbs


def disconnect_db_list(dbs):
    for db in dbs:
        db.disconnect()


def make_logger(name, log_file, level=logging.INFO):
    logger = logging.getLogger(name)
    # format = logging.Formatter(logging.BASIC_FORMAT)
    format = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file, mode='w')        
    handler.setFormatter(format)
    
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(format)

    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(streamhandler)

    return logger
    
    
def process_tag_entities(params, dbs, tags):
    batch = params.batch_size
    num_lines = len(tags)
    blocks = int(np.ceil(num_lines / (params.num_threads * batch)))
    results = [None] * num_lines

    for block in range(0, blocks):
        thread_arr = []
        
        for i in range(0, params.num_threads):
            idx = params.num_threads * block + i * batch
            
            if idx < num_lines:
                thread_add = Thread(target=util.add_autotags_entity_batch, args=(idx, dbs[i], tags[idx:min([idx+batch, num_lines])], results))
                thread_add.start()
                thread_arr.append(thread_add)
            else:
                break
        
        idx = params.num_threads * block
        error_counter = 0
        for th in thread_arr:
            th.join()
            error_counter += results[idx:min([idx+batch, num_lines])].count(-1)
            idx += batch
    # return results, error_counter
    return error_counter


def process_image_entities(params, dbs, yfcc_data):
    batch = params.batch_size
    num_lines = len(yfcc_data)
    blocks = int(np.ceil(num_lines / (params.num_threads * batch)))
    results = [None] * num_lines

    for block in range(0, blocks):
        thread_arr = []
        
        for i in range(0, params.num_threads):
            idx = params.num_threads * block + i * batch
            
            if idx < num_lines:
                thread_add = Thread(target=util.add_image_entity_batch, args=(idx, min([idx+batch, num_lines]), dbs[i], yfcc_data.iloc[idx:min([idx+batch, num_lines]), :], results))
                thread_add.start()
                thread_arr.append(thread_add)
            else:
                break
        
        idx = params.num_threads * block
        error_counter = 0
        for th in thread_arr:
            th.join()
            error_counter += results[idx:min([idx+batch, num_lines])].count(-1)
            idx += batch
    return error_counter


def process_connections(params, dbs, yfcc_data):
    batch = 10
    # batch = params.batch_size
    num_lines = len(yfcc_data)
    blocks = int(np.ceil(num_lines / (params.num_threads * batch)))
    results = [None] * num_lines

    for block in range(0, blocks):
        thread_arr = []
        
        for i in range(0, params.num_threads):
            idx = params.num_threads * block + i * batch
            
            if idx < num_lines:
                thread_add = Thread(target=util.add_autotag_connection_batch,
                                    args=(idx, dbs[i], yfcc_data.iloc[idx:min([idx+batch, num_lines]), :], results))
                thread_add.start()
                thread_arr.append(thread_add)
            else:
                break
                
        idx = params.num_threads * block
        error_counter = 0
        for th in thread_arr:
            th.join()
            error_counter += results[idx:min([idx+batch, num_lines])].count(-1)
            idx += batch
    return error_counter


def main(in_args):
    main_logger.info('[!] Building database')
    start = time.time()

    # Get data
    data, all_tags = get_data(in_args)
    e_time = time.time() - start
    main_logger.info('\t[!] [get_data] Total elapsed time: {:0.4f} secs ({:0.4f} mins)'.format(e_time, e_time / 60.))

    db_list = get_db_list(in_args.num_threads)

    # Add Entities for Tags
    start_t = time.time()
    tag_num_errors = process_tag_entities(in_args, db_list, all_tags)
    e_time = time.time() - start_t
    main_logger.info('\t[!] [process_tag_entities] Total Errors: {}\tTotal elapsed time: {:0.4f} secs ({:0.4f} mins)'.format(tag_num_errors, e_time, e_time / 60.))

    # Add Entities for Metadata
    start_t = time.time()
    image_num_errors = process_image_entities(in_args, db_list, data)
    e_time = time.time() - start_t
    main_logger.info('\t[!] [process_image_entities] Total Errors: {}\tTotal elapsed time: {:0.4f} secs ({:0.4f} mins)'.format(image_num_errors, e_time, e_time / 60.))

    # Add Connections between Tags and Metadata
    start_t = time.time()
    connection_num_errors = process_connections(in_args, db_list, data)
    e_time = time.time() - start_t
    main_logger.info('\t[!] [process_connections] Total Errors: {}\tTotal elapsed time: {:0.4f} secs ({:0.4f} mins)'.format(connection_num_errors, e_time, e_time / 60.))

    disconnect_db_list(db_list)
    e_time = time.time() - start
    main_logger.info('[!] Total elapsed time: {:0.4f} secs ({:0.4f} mins)'.format(e_time, e_time / 60.))


if __name__ == "__main__":
    main_logger = make_logger('main_logger', "build_yfcc_db_batching.log")

    args = get_args()
    main(args)
