"""
Create Databases in PostgreSQL
"""

from pathlib import Path
import pandas as pd
import numpy as np
import time
import math
import logging
import argparse
import threading
import psycopg2
import sys, os
import csv
import PostgreSQLQuery

connection_batch_limit = 100
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

def get_args():
    parserobj = argparse.ArgumentParser()
    parserobj.add_argument('-num_threads', type=int, default=100,
                           help='Number of threads to use [default: 100]')
    parserobj.add_argument('-batch_size', type=int, default=100,
                           help='Number of entries per thread for autotags and images [default: 100; connections: max {}]'.format(connection_batch_limit))
    parserobj.add_argument('-data_file', type=lambda s: Path(s),
                           default='/mnt/yfcc100m/metadata/processed/yfcc100m_photo_dataset',
                           help='YFCC metadata [default: ' +
                           '/mnt/yfcc100m/metadata/processed/yfcc100m_photo_dataset')
    parserobj.add_argument('-tag_list', type=lambda s: Path(s),
                            default='../yfcc_parse_labels/autotag_list.txt',
                           help='List of expected tags [default: ../../yfcc_parse_labels/autotag_list.txt]')
    parserobj.add_argument('-tag_file', type=lambda s: Path(s),
                           default='/mnt/yfcc100m/metadata/processed/yfcc100m_photo_autotags',
                           help='YFCC file of autotags [default: ' +
                                '/mnt/yfcc100m/metadata/processed/yfcc100m_photo_autotags]')

    # Database Info
    parserobj.add_argument('-db_name', type=str, default='test',
                           help='Name of database [default: test]')
    parserobj.add_argument('-db_host', type=str, required=True,
                           help='Name of postgresql host')
    parserobj.add_argument('-db_port', type=int, default=5432,
                           help='Port of postgresql [default: 5432]')
    parserobj.add_argument('-db_user', type=str, default='root',
                           help='Username of database [default: root]')
    parserobj.add_argument('-db_pswd', type=str, default='',
                           help='Password of database [default: ""]')

    params = parserobj.parse_args()
    return params

def make_logger(name, log_file, level=logging.INFO):
    logger = logging.getLogger(name)
    format = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(format)

    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(format)

    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(streamhandler)

    return logger


def get_parameters(params, all_data, num_entries_per_thread=None):
    if num_entries_per_thread is None:
        num_entries_per_thread = params.batch_size

    num_entries = len(all_data)

    blocks = int(np.ceil(num_entries / (params.num_threads * num_entries_per_thread)))
    return num_entries_per_thread, num_entries, blocks, [None] * num_entries


def setup_test_db(params):
    """ Create a database and table for this benchmark to use. """
    qh = PostgreSQLQuery.PostgreSQL(params)

    print('Creating table test_taglist')
    qh.db_cursor.execute('DROP TABLE IF EXISTS test_taglist')
    qh.db_cursor.execute("""\
        CREATE TABLE test_taglist(
        tagid SERIAL PRIMARY KEY,
        tag VARCHAR NOT NULL)""")

    print('Creating table test_autotags')
    qh.db_cursor.execute('DROP TABLE IF EXISTS test_autotags')
    qh.db_cursor.execute("""\
        CREATE TABLE test_autotags(
        metadataid BIGINT NOT NULL,
        tagname VARCHAR NOT NULL,
        probability NUMERIC(5,4) NOT NULL DEFAULT 0.000)""")

    print('Creating table test_metadata')
    qh.db_cursor.execute('DROP TABLE IF EXISTS test_metadata')
    qh.db_cursor.execute("""\
        CREATE TABLE test_metadata(
        line_number varchar(255) DEFAULT NULL,
        id BIGINT NOT NULL PRIMARY KEY,
        hash varchar(255) DEFAULT NULL,
        user_nsid varchar(255) DEFAULT NULL,
        user_nickname varchar(255) DEFAULT NULL,
        date_taken varchar(255) DEFAULT NULL,
        date_uploaded varchar(255) DEFAULT NULL,
        capture_device varchar DEFAULT NULL,
        title varchar DEFAULT NULL,
        description varchar DEFAULT NULL,
        user_tags varchar DEFAULT NULL,
        machine_tags varchar DEFAULT NULL,
        longitude NUMERIC(10,7) DEFAULT 999.9999999,
        latitude NUMERIC(10,7) DEFAULT 999.9999999,
        coord_accuracy varchar(255) DEFAULT NULL,
        page_url varchar DEFAULT NULL,
        download_url varchar DEFAULT NULL,
        license_name varchar(255) DEFAULT NULL,
        license_url varchar DEFAULT NULL,
        server_id varchar(255) DEFAULT NULL,
        farm_id varchar(255) DEFAULT NULL,
        secret varchar(255) DEFAULT NULL,
        secret_original varchar(255) DEFAULT NULL,
        extension varchar(255) DEFAULT NULL,
        marker varchar(255) DEFAULT NULL)""")
    qh.db.commit()
    qh.close_connection()


def process_tag_entities(params):
    # File contains a list of all autotags
    num_lines = len([line.strip() for line in open(str(params.tag_list), 'r')])
    qh = PostgreSQLQuery.PostgreSQL(params)
    with open(str(params.tag_list.absolute()), 'r') as f:
        qh.db_cursor.copy_from(f, 'test_taglist', sep=',', columns=('tag',))
    qh.db_cursor.execute("SELECT COUNT(*) FROM test_taglist")
    (count,) = qh.db_cursor.fetchone()
    qh.db.commit()
    qh.close_connection()
    return count, num_lines - count

def process_autotags_entities(params):
    num_lines = len([line.strip() for line in open(str(params.tag_file), 'r')])
    qh = PostgreSQLQuery.PostgreSQL(params)
    with open(str(params.tag_file.absolute()), 'r') as f:
        qh.db_cursor.copy_from(f, 'test_autotags', sep='\t')

    # Add column (tagid) for index of autotag taken from test_taglist table
    query1 = \
        '''ALTER TABLE test_autotags ADD COLUMN tagid INT;'''
    query2 = \
        '''UPDATE test_autotags SET tagid = test_taglist.tagid
        FROM test_taglist WHERE test_taglist.tag=test_autotags.tagname'''
    qh.db_cursor.execute(query1)
    qh.db_cursor.execute(query2)

    # Drop column (tagname) from test_autotags and add tagid and metadataid as index
    query3 = \
        '''ALTER TABLE test_autotags DROP column tagname;''' #, ADD PRIMARY KEY(metadataid,tagid);'''
    query4 = \
        '''CREATE INDEX tagid ON test_autotags(tagid);'''
    query5 = \
        '''CREATE INDEX metadataid ON test_autotags(metadataid);'''
    qh.db_cursor.execute(query3)
    qh.db_cursor.execute(query4)
    qh.db_cursor.execute(query5)

    qh.db_cursor.execute("SELECT COUNT(*) FROM test_autotags")
    (count,) = qh.db_cursor.fetchone()
    qh.db.commit()
    qh.close_connection()
    return count, num_lines - count

def process_metadata_entities(params):
    all_data = pd.read_csv(str(params.data_file), sep='\t', names=property_names)
    batch, num_lines, blocks, results = get_parameters(params, all_data)
    qh = PostgreSQLQuery.PostgreSQL(params)
    with open(str(params.data_file.absolute()), 'r') as f:
        qh.db_cursor.copy_from(f, 'test_metadata', null="", sep='\t', columns=property_names_sql[:-3])
    qh.db_cursor.execute("SELECT COUNT(*) FROM test_metadata")
    (count,) = qh.db_cursor.fetchone()
    qh.db.commit()
    qh.close_connection()
    return count, num_lines - count


def main(in_args):
    main_logger.info('[!] Building database')
    start = time.time()

    # Setup database and tables
    setup_test_db(in_args)

    func_list = ['process_tag_entities', 'process_metadata_entities', 'process_autotags_entities']
    #func_list = ['process_autotags_entities']
    for fn in func_list:
        start_t = time.time()
        tag_num_success, tag_num_errors = eval('{}(in_args)'.format(fn))
        e_time = time.time() - start_t
        main_logger.info('[!] [{}]\n\tTotal Successes: {}\n\tTotal Errors: {}\n\tTotal elapsed time: {:0.4f} secs ({:0.4f} mins)'.format(fn, tag_num_success, tag_num_errors, e_time, e_time / 60.))

    # cleanup(in_args)
    e_time = time.time() - start
    main_logger.info('[!] Total elapsed time: {:0.4f} secs ({:0.4f} mins)'.format(e_time, e_time / 60.))

if __name__ == '__main__':
    args = get_args()

    log_name = sys.argv[0].split('/')[-1].replace('.py','yfcc_{}.log'.format(args.db_name))
    main_logger = make_logger('main_logger', log_name)

    main(args)


