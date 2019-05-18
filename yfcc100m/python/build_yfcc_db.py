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
                           help='Number of threads to use [default: 100]')
    parserobj.add_argument('-data_file', type=str,
                           default='/data/yfcc100m/set_0/data_0/metadata/yfcc100m_short/yfcc100m_dataset_short',
                           help='YFCC metadata [default: ' +
                                '/data/yfcc100m/set_0/data_0/metadata/yfcc100m_short/yfcc100m_dataset_short')
    parserobj.add_argument('-tag_list', type=str, default='autotag_list.txt',
                           help='List of expected tags [default: autotag_list.txt]')
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


def process_tag_entities(params, dbs, tags):
    num_tags = len(tags)
    retries = int(np.ceil(num_tags / params.num_threads))
    results = [None] * num_tags

    for ret in range(0, retries):
        thread_arr = []
        for i in range(0, params.num_threads):
            idx = params.num_threads * ret + i
            if idx < num_tags:
                thread_add = Thread(target=util.add_autotags_entity, args=(idx, dbs[i], tags[idx], results))
                thread_add.start()
                thread_arr.append(thread_add)
        idx = params.num_threads * ret
        error_counter = 0
        for th in thread_arr:
            th.join()
            if results[idx] == -1:
                error_counter += 1
                logging.debug('\t[!] [process_tag_entities] Index {} status: {}'.format(idx, results[idx]))
            idx += 1


def process_image_entities(params, dbs, yfcc_data):
    num_lines = len(yfcc_data)
    retries = int(np.ceil(num_lines / params.num_threads))
    results = [None] * num_lines

    for ret in range(0, retries):
        thread_arr = []
        for i in range(0, params.num_threads):
            idx = params.num_threads * ret + i
            if idx < num_lines:
                thread_add = Thread(target=util.add_image_entity, args=(idx, dbs[i], yfcc_data.iloc[idx, :], results))
                thread_add.start()
                thread_arr.append(thread_add)
        idx = params.num_threads * ret
        error_counter = 0
        for th in thread_arr:
            th.join()
            if results[idx] == -1:
                error_counter += 1
                logging.debug('\t[!] [process_image_entities] Index {} status: {}'.format(idx, results[idx]))
            idx += 1


def process_connections(params, dbs, yfcc_data):
    num_lines = len(yfcc_data)
    retries = int(np.ceil(num_lines / params.num_threads))
    results = [None] * num_lines

    for ret in range(0, retries):
        thread_arr = []
        for i in range(0, params.num_threads):
            idx = params.num_threads * ret + i
            if idx < num_lines:
                thread_add = Thread(target=util.add_autotag_connection,
                                    args=(idx, dbs[i], yfcc_data.iloc[idx, :], results))
                thread_add.start()
                thread_arr.append(thread_add)
        idx = params.num_threads * ret
        error_counter = 0
        for th in thread_arr:
            th.join()
            if results[idx] == -1:
                error_counter += 1
                logging.debug('\t[!] [process_connections] Index {} status: {}'.format(idx, results[idx]))
            idx += 1


def main(in_args):
    logging.debug('[!] Building database')
    start = time.time()

    # Get data
    data, all_tags = get_data(in_args)
    logging.debug('\t[!] [get_data] Total elapsed time: {:0.4f}'.format(time.time() - start))

    db_list = get_db_list(in_args.num_threads)

    # Add Entities for Tags
    start_t = time.time()
    process_tag_entities(in_args, db_list, all_tags)
    logging.debug('\t[!] [process_tag_entities] Total elapsed time: {:0.4f}'.format(time.time() - start_t))

    # Add Entities for Metadata
    start_t = time.time()
    process_image_entities(in_args, db_list, data)
    logging.debug('\t[!] [process_image_entities] Total elapsed time: {:0.4f}'.format(time.time() - start_t))

    # Add Connections between Tags and Metadata
    start_t = time.time()
    process_connections(in_args, db_list, data)
    logging.debug('\t[!] [process_connections] Total elapsed time: {:0.4f}'.format(time.time() - start_t))

    disconnect_db_list(db_list)
    logging.debug('[!] Total elapsed time: {:0.4f}'.format(time.time() - start))


if __name__ == "__main__":
    log_file = "build_yfcc_db.log"
    logging.basicConfig(filename=str(log_file), filemode='w', level=logging.DEBUG)
    stderrlogger = logging.StreamHandler()
    stderrlogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logging.getLogger().addHandler(stderrlogger)

    args = get_args()
    main(args)

    if stderrlogger:
        logging.getLogger().removeHandler(stderrlogger)
