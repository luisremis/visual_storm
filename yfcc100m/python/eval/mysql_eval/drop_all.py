"""
Drop Databases in MSQyL
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
import sys, os
import csv

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

    # Database Info
    parserobj.add_argument('-db_name', type=str, default='test',
                           help='Name of database [default: test]')
    parserobj.add_argument('-db_host', type=str, required=True,
                           help='Name of mysql host')
    parserobj.add_argument('-db_port', type=int, default=3360,
                           help='Port of mysql [default: 3360]')
    parserobj.add_argument('-db_user', type=str, default='root',
                           help='Username of database [default: root]')
    parserobj.add_argument('-db_pswd', type=str, default='',
                           help='Password of database [default: ""]')

    params = parserobj.parse_args()
    return params

def drop_dbs(params):
    """ Create a database and table for this benchmark to use. """
    conn = util.get_connection(params, db="information_schema")
    db_cursor = conn.cursor() 
    db_cursor.execute('DROP DATABASE %s' % params.db_name)
    conn.commit()
    db_cursor.close()
    conn.close()

def main(in_args):
    main_logger.info('[!] Dropping database')
    start = time.time()

    # Setup database and tables
    drop_dbs(in_args)

    # cleanup(in_args)
    e_time = time.time() - start
    main_logger.info('[!] Total elapsed time: {:0.4f} secs ({:0.4f} mins)'.format(e_time, e_time / 60.))

if __name__ == '__main__':
    args = get_args()

    log_name = sys.argv[0].split('/')[-1].replace('.py','{}.log'.format(args.db_name))
    main_logger = make_logger('main_logger', log_name)

    main(args)


