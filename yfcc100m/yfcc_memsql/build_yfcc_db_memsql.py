"""
SOURCE: https://github.com/memsql/memsql-python/blob/master/examples/multi_threaded_inserts.py

MODIFIED BY: Chaunte W. Lacewell

"""

from pathlib import Path
import pandas as pd
import numpy as np
import time
import math
import logging
import argparse
import threading
import util
from memsql.common import database
import sys, os
import csv

connection_batch_limit = 100
log_name = sys.argv[0].split('/')[-1].replace('.py','.log')

# Pre-generate the workload query
# QUERY_TEXT = "INSERT INTO %s VALUES %s" % (
    # TABLE, ",".join(["()"] * BATCH_SIZE))

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

def get_args():
    parserobj = argparse.ArgumentParser()
    # parserobj.add_argument('-process_first_n', type=int, default=None,
                           # help='Process only the first N lines of image/connection data [default: None-> all data]')
    parserobj.add_argument('-num_threads', type=int, default=100,
                           help='Number of threads to use [default: 100]')
    parserobj.add_argument('-batch_size', type=int, default=100,
                           help='Number of entries per thread for autotags and images [default: 100; connections: max {}]'.format(connection_batch_limit))
    parserobj.add_argument('-data_file', type=lambda s: Path(s),
                           default='yfcc100m_dataset_short',
                           help='YFCC metadata [default: ' +
                                '/mnt/data/metadata/yfcc100m_short/yfcc100m_dataset_short')
    parserobj.add_argument('-tag_list', type=lambda s: Path(s), default='../yfcc_parse_labels/autotag_list.txt',
                           help='List of expected tags [default: ../yfcc_parse_labels/autotag_list.txt]')
    parserobj.add_argument('-tag_file', type=lambda s: Path(s),
                           default='/mnt/data/metadata/yfcc100m_short/yfcc100m_autotags_short',
                           help='YFCC file of autotags [default: ' +
                                '/mnt/data/metadata/yfcc100m_short/yfcc100m_autotags_short]')
    parserobj.add_argument('-db_name', type=str, default='test',
                           help='Name of database [default: test]')
    parserobj.add_argument('-db_host', type=str, default='sky3.jf.intel.com',
                           help='Name of memsql host [default: sky3.jf.intel.com]')
    parserobj.add_argument('-db_port', type=int, default=3306,
                           help='Port of memsql [default: 3306]')
    parserobj.add_argument('-db_user', type=str, default='root',
                           help='Username of database [default: root]')
    parserobj.add_argument('-db_pswd', type=str, default='',
                           help='Password of database [default: ""]')
                                

    params = parserobj.parse_args()
    return params

def get_parameters(params, all_data, num_entries_per_thread=None):
    if num_entries_per_thread is None:
        num_entries_per_thread = params.batch_size
    
    num_entries = len(all_data)    
    # if params.process_first_n is not None and params.process_first_n < num_entries:
        # num_entries = params.process_first_n
        
    blocks = int(np.ceil(num_entries / (params.num_threads * num_entries_per_thread)))
    return num_entries_per_thread, num_entries, blocks, [None] * num_entries

def setup_test_db(params):
    """ Create a database and table for this benchmark to use. """

    with util.get_connection(params, db="information_schema") as conn:
        print('Creating database %s' % params.db_name)
        conn.query('DROP DATABASE IF EXISTS %s' % params.db_name)
        conn.query('CREATE DATABASE %s' % params.db_name)
        conn.query('USE %s' % params.db_name)
        
        print('Creating table test_taglist')
        conn.query('DROP TABLE IF EXISTS test_taglist')
        conn.query("""\
            CREATE TABLE test_taglist(
            idx INT AUTO_INCREMENT PRIMARY KEY,
            tag varchar(255) NOT NULL DEFAULT '')""")
        
        print('Creating table test_autotags')
        conn.query('DROP TABLE IF EXISTS test_autotags')
        conn.query("""\
            CREATE TABLE test_autotags(
            id BIGINT UNSIGNED NOT NULL, 
            autotags varchar(255) NOT NULL DEFAULT '',
            key (id) USING CLUSTERED COLUMNSTORE,
            FULLTEXT (autotags))""")
        
        # print('Creating table test_autotags')  # JSON Test
        # conn.query('DROP TABLE IF EXISTS test_autotags')
        # conn.query("""\
            # CREATE TABLE test_autotags(
            # id BIGINT UNSIGNED NOT NULL, 
            # autotags varchar(255) NOT NULL DEFAULT '',
            # probability DOUBLE NOT NULL DEFAULT 0,
            # key (id, autotags))""")

        print('Creating table test_metadata')
        conn.query('DROP TABLE IF EXISTS test_metadata')
        
        t_query = ''
        conn.query("""\
            CREATE TABLE test_metadata(
            line_number varchar(255) DEFAULT NULL,
            id BIGINT NOT NULL PRIMARY KEY, 
            hash varchar(255) DEFAULT NULL, 
            user_nsid varchar(255) DEFAULT NULL,
            user_nickname varchar(255) DEFAULT NULL,
            date_taken varchar(255) DEFAULT NULL,
            date_uploaded varchar(255) DEFAULT NULL,
            capture_device varchar(255) DEFAULT NULL,
            title varchar(255) DEFAULT NULL, 
            description varchar(255) DEFAULT NULL, 
            user_tags varchar(255) DEFAULT NULL, 
            machine_tags varchar(255) DEFAULT NULL,
            longitude varchar(255) DEFAULT NULL, 
            latitude varchar(255) DEFAULT NULL, 
            coord_accuracy varchar(255) DEFAULT NULL, 
            page_url varchar(255) DEFAULT NULL,
            download_url varchar(255) DEFAULT NULL, 
            license_name varchar(255) DEFAULT NULL, 
            license_url varchar(255) DEFAULT NULL,
            server_id varchar(255) DEFAULT NULL, 
            farm_id varchar(255) DEFAULT NULL, 
            secret varchar(255) DEFAULT NULL, 
            secret_original varchar(255) DEFAULT NULL,
            extension varchar(255) DEFAULT NULL,
            marker varchar(255) DEFAULT NULL,
            imgPath varchar(255) DEFAULT NULL,
            imgBlob blob DEFAULT NULL,
            format varchar(255) DEFAULT 'jpg')""")

def cleanup():
    """ Cleanup the database this benchmark is using. """

    with util.get_connection(params) as conn:
        conn.query('DROP DATABASE %s' % params.db_name)

def process_tag_entities(params):
    num_lines = len([line.strip() for line in open(str(params.tag_list), 'r')])
    query = "LOAD DATA INFILE '{}' INTO TABLE test_taglist (tag)".format(str(params.tag_list.absolute()))
    with util.get_connection(params) as conn:
        conn.execute(query)
        count = conn.get("SELECT COUNT(*) AS count FROM test_taglist").count
    return count, num_lines - count
    
def process_autotags_entities(params):
    # JSON
    # # tags = pd.read_csv(str(params.tag_file), sep='\t', names=['id', 'autotags'])
    # # for ix, row in tags.iterrows():
        # # if not pd.isna(row['autotags']):
            # # json_str = '['
            # # curr_tags = row['autotags'].split(',')
            # # arr = []
            # # for tag in curr_tags:
                # # name, prob = tag.split(':')
                # # arr.append("{'name':'" + name + "','probability':" + prob + "}" )
            
            # # json_str += ','.join(arr) + ']'        
        # # else:
            # # json_str = "[{'name':'','probability':0.0}]"
        # # # tags.set_value(ix, 'autotags', json_str)
        # # tags.at[ix, 'autotags'] = json_str
    # # num_lines = len(tags)
    # # tmp_file = str(Path().cwd() / 'tmp_tags')    
    # # tags.to_csv(tmp_file, index=False)
    # # query = "LOAD DATA INFILE '{}' INTO TABLE test_autotags (id,autotags)".format(tmp_file)
    
    # 2 cols -> 3 cols (id, name, prob)
    # tags = pd.DataFrame(columns=['id','autotags', 'probability'])
    # tmp_file = str(Path().cwd() / 'tmp_tags') 
    # # with open(tmp_file, 'w') as file:
        # # writer = csv.writer(file)
    # for line in open(str(params.tag_file), 'r'):
        # line = line.strip().split('\t')
        # if len(line) > 1:
            # name, taglist = line
            # taglist = taglist.split(',')
            # for t in taglist:
                # tag, val = t.split(':')
                # tags = tags.append({'id': name, 'autotags':tag, 'probability':val}, ignore_index=True) 
                # # writer.writerows('{}\t{}\t{}'.format(name,tag,val))
                # # new_data.append('{}\t{}\t{}'.format(name,tag,val))
    # tags.to_csv(tmp_file, index=False)
    # query = "LOAD DATA INFILE '{}' INTO TABLE test_autotags (id,autotags,probability)".format(tmp_file)
    # os.remove(tmp_file)
    
    num_lines = len([line.strip() for line in open(str(params.tag_file), 'r')])
    query = "LOAD DATA INFILE '{}' INTO TABLE test_autotags (id,autotags)".format(str(params.tag_file.absolute()))
    with util.get_connection(params) as conn:
        conn.execute(query)
        count = conn.get("SELECT COUNT(*) AS count FROM test_autotags").count
    return count, num_lines - count
    
def process_metadata_entities(params):
    all_data = pd.read_csv(str(params.data_file), sep='\t', names=util.property_names)
    batch, num_lines, blocks, results = get_parameters(params, all_data)
    query = "LOAD DATA INFILE '{}' INTO TABLE test_metadata ({})".format(str(params.data_file.absolute()), ','.join(util.property_names_sql[:-3]))
    
    with util.get_connection(params) as conn:
        conn.execute(query)
        count = conn.get("SELECT COUNT(*) AS count FROM test_metadata").count    
    
    # thread_arr = []
    # per_thread = int(num_lines / params.num_threads)
    # for i in range(0, params.num_threads):
        # idx = i * per_thread

        # if idx < num_lines:
            # start = idx
            # end = min([idx+per_thread, num_lines])
            # print('thread: {}\tstart index: {}\tend index:{}'.format(i, start, end))
            # results = util.add_image_batch_to_db(params.db_name, batch, start, end, all_data, results)
            # # results = util.add_image_all_batch(params.db_name, batch, start, end, all_data, results)
            # # thread_add = threading.Thread(target=util.add_image_all_batch, args=(params.db_name, batch, start, end, all_data, results))
            # # thread_add.start()
            # # thread_arr.append(thread_add)
        # else:
            # break

    # # for th in thread_arr:
        # # th.join()
    # # return results.count(-1)
    
    return count, num_lines - count
    
# def str_to_json(val):
    # tags = []
    # if not pd.isna(val):
        # current_tags = val.split(',')
        # for x in current_tags:
            # data = x.split(':')
            # # tags[data[0]] = float(data[1])
            # tags.append({"tagname" : data[0], "probability" : float(data[1])})
    # else:
        # tags.append({"tagname" : "null", "probability" : float(0)})
    # return tags
        
        
# def process_autotags_entities(params):
    # tags = pd.read_csv(params.tag_file, sep='\t', names=['id', 'autotags'])
    # tags['autotags'] = tags['autotags'].apply(str_to_json)
    # tmp_file = Path().cwd() / 'tmp_autotags.csv'
    # tags.to_csv(str(tmp_file), index=False)
    # query = "LOAD DATA INFILE '{}' INTO TABLE test_autotags (id,autotags)".format(str(tmp_file))
    # num_lines = len([line.strip() for line in open(str(params.tag_file), 'r')])
    # # query = "LOAD DATA INFILE '{}' INTO TABLE test_autotags (id,autotags)".format(str(params.tag_file.absolute()))
    # with util.get_connection(params) as conn:
        # conn.execute(query)
        # count = conn.get("SELECT COUNT(*) AS count FROM test_autotags").count
    # os.remove(str(tmp_file))
    # return count, num_lines - count
    

def main(in_args):
    main_logger.info('[!] Building database')
    start = time.time()
    
    # Setup database and tables
    setup_test_db(in_args)        
    
    func_list = ['process_tag_entities', 'process_autotags_entities', 'process_metadata_entities']
    for fn in func_list:
        start_t = time.time()
        tag_num_success, tag_num_errors = eval('{}(in_args)'.format(fn))
        e_time = time.time() - start_t
        main_logger.info('[!] [{}]\n\tTotal Successes: {}\n\tTotal Errors: {}\n\tTotal elapsed time: {:0.4f} secs ({:0.4f} mins)'.format(fn, tag_num_success, tag_num_errors, e_time, e_time / 60.))
        
    # cleanup(in_args)    
    e_time = time.time() - start
    main_logger.info('[!] Total elapsed time: {:0.4f} secs ({:0.4f} mins)'.format(e_time, e_time / 60.))

if __name__ == '__main__':
    main_logger = make_logger('main_logger', log_name)
    args = get_args()
    main(args)
   
   
