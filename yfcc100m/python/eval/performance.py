import argparse
import time
from threading import Thread

import pandas as pd
import numpy as np

from postgresql_eval  import PostgreSQLQuery
from mysql_eval  import MySQLQuery
from memsql_eval import MemSQLQuery
from vdms_eval   import VDMSQuery

from DBEvalFramework import EvalFramework

VDMS_PORT_MAPPING = {'100k': 55500, '500k': 55405,
                     '1M':   55501, '5M':   55450,
                     '10M':  55510, '50M':  55000,
                     '100M': 50000}

# These are pre-computed probabilities so that queries returned
# a controlled number of results, to prevent the throughput to be
# affected by higher number of results
PROB_MAPPING = {
            '1M': {
              "1tag":           0.735,
              "1tag_loc20":     0.0625,
              "2tag_loc20_or":  0.059375,
              "2tag_or":        0.975,
              "2tag_loc20_and": 0.06875,
              "2tag_and":       0.059375,
            },
            '5M': {
              "1tag":           0.949375,
              "1tag_loc20":     0.0625,
              "2tag_or":        0.984375,
              "2tag_and":       0.59375,
              "2tag_loc20_or":  0.71249,
              "2tag_loc20_and": 0.06875,
            },
            '10M': {
              "2tag_loc20_or":  0.8312499,
              "2tag_and":       0.653125,
              "1tag_loc20":     0.0625,
              "2tag_or":        0.9875,
              "2tag_loc20_and": 0.06875,
              "1tag":           0.96468749
            },
            '50M':  {
              "1tag":           0.995,
              "2tag_and":       0.74218749,
              "1tag_loc20":     0.0625,
              "2tag_loc20_or":  0.95,
              "2tag_loc20_and": 0.06875,
              "2tag_or":        0.9953125
            },
            '100M': {
              "1tag":           0.9975,
              "1tag_loc20":     0.75,
              "2tag_and":       0.8015625,
              "2tag_loc20_or":  0.9781249,
              "2tag_loc20_and": 0.06875,
              "2tag_or":        0.997656249
            }
        }

# These are operations using VDMS API format / params.
OP_RESIZE_DOWN = {"type": "resize", "width": 224,  "height": 224}
OP_ROTATE      = {"type": "rotate", "angle": 45.0, "resize": False}

# Different queries, each with its own parameters.
# Database object must implement each of these queries

QUERY_PARAMS = [
            # {'key': '1tag',
            #  'tags': ["alligator"], 'probs': [0.99],
            #  'operations': [],
            #  'comptype': "and" },
            # {'key': '1tag_loc20',
            #  'tags': ["alligator"], 'probs': [0.4],
            #  'lat': -14.354356, 'long': -39.002567,
            #  'range_dist': 20,
            #  'operations': [],
            #  'comptype': "and"},
            # {'key': '2tag_and',
            #  'tags': ["alligator", "lake"], 'probs': [0.75, 0.75],
            #  'comptype': "and" },
            # {'key': '2tag_or',
            #  'tags': ["alligator", "lake"], 'probs': [0.8, 0.8],
            #  'comptype': "or" },
            # {'key': '2tag_loc20_and',
            #  'tags': ["alligator", "lake"], 'probs': [0.35, 0.35],
            #  'lat': -14.354356, 'long': -39.002567,
            #  'range_dist': 20,
            #  'comptype': "and" },
            # {'key': '2tag_loc20_or',
            #  'tags': ["alligator", "lake"], 'probs': [0.90, 0.95],
            #  'lat': -14.354356, 'long': -39.002567,
            #  'range_dist': 20,
            #  'comptype': "or" },

            {'key': '1tag_resize',
             'tags': ["alligator"], 'probs': [1.1],
             'operations': [OP_RESIZE_DOWN],
             'comptype': "or" },
            {'key': '1tag_loc20_resize',
             'tags': ["alligator"], 'probs': [0.4],
             'lat': -14.354356, 'long': -39.002567,
             'range_dist': 20,
             'operations': [OP_RESIZE_DOWN],
             'comptype': "or" },
            {'key': '2tag_resize_and',
             'tags': ["alligator", "lake"], 'probs': [0.95, 0.95],
             'operations': [OP_RESIZE_DOWN],
             'comptype': "and" },
            {'key': '2tag_resize_or',
             'tags': ["alligator", "lake"], 'probs': [0.95, 0.95],
             'operations': [OP_RESIZE_DOWN],
             'comptype': "or" },
            {'key': '2tag_loc20_resize_and',
             'tags': ["alligator", "lake"], 'probs': [0.95, 0.95],
             'lat': -14.354356, 'long': -39.002567,
             'range_dist': 20,
             'operations': [OP_RESIZE_DOWN],
             'comptype': "and" },
            {'key': '2tag_loc20_resize_or',
             'tags': ["alligator", "lake"], 'probs': [0.95, 0.95],
             'lat': -14.354356, 'long': -39.002567,
             'range_dist': 20,
             'operations': [OP_RESIZE_DOWN],
             'comptype': "or" },
              ]

def reject_outliers(data, m = 2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m]

def get_args():
    obj = argparse.ArgumentParser()

    # Database Info
    obj.add_argument('-db_type', type=str, default='vdms',
                     choices=["vdms", "memsql", "mysql", "postgresql"],
                     help='Database names: vdms, memsql, mysql, postgresql')
    obj.add_argument('-db_name', type=str, default='100k',
                     choices=VDMS_PORT_MAPPING.keys(),
                     help='Database names: 100k, 1M, 10M')

    obj.add_argument('-db_host', type=str, default="sky4.local",
                     help='Name of host')
    obj.add_argument('-db_port', type=int, default=3306,
                     help='Port of memsql [default: 3306]')
    obj.add_argument('-db_user', type=str, default='root',
                     help='Username of database [default: root]')
    obj.add_argument('-db_pswd', type=str, default='',
                     help='Password of database [default: ""]')

    # Run Config
    obj.add_argument('-numthreads', type=int, default=4,
                     help='Number of workers [default: 4]')
    obj.add_argument('-numiters', type=int, default=2,
                     help='Number of times to process all threads [default: 2]')

    # Output CSV
    obj.add_argument('-out_folder', type=str, default=None,
                     help='CSV Filename for measurements')

    params = obj.parse_args()

    if params.db_type == "memsql":
        params.db_host = "sky3.local"
    elif params.db_type == "mysql":
        params.db_host = "127.0.0.1" #TODO: Get to work with hostname
        params.db_port = 3360
    elif params.db_type == "postgresql":
        if params.db_name == '50M':
            params.db_host = "sky4.local"
        else:
            params.db_host = "127.0.0.1"
        params.db_port = 5432
        params.db_user = "root"
        params.db_pswd = "password"
    else:
        # VDMS needs port mapping
        params.db_host = "sky4.local"
        params.db_port = VDMS_PORT_MAPPING[params.db_name]

    return params

def run_query_thread(obj, params, index, results, query_arguments):

    start = time.time()
    # Here the object runs the query and returns time and len
    data_dict = obj.run_query(query_arguments)
    results[index].update(data_dict)

    endtime = time.time() - start
    print("query_thread took:", endtime) # Debugging

def run_query(params, query_arguments):

    thread_arr = []
    results = [{}] * (params.numthreads)
    list_of_objs = []

    if (params.db_type == "vdms"):
        for i in range(params.numthreads):
            list_of_objs.append(
                        VDMSQuery.VDMSQuery(params.db_host, params.db_port))
    elif (params.db_type == 'postgresql'):
        for i in range(params.numthreads):
            list_of_objs.append(PostgreSQLQuery.PostgreSQL(params))
    elif (params.db_type == "mysql"):
        for i in range(params.numthreads):
            list_of_objs.append(MySQLQuery.MySQL(params))
    else:
        for i in range(params.numthreads):
            list_of_objs.append(MemSQLQuery.MemSQL(params))

    for thread in range(params.numthreads):
        thread_add = Thread(target=run_query_thread,
                            args=(list_of_objs[thread], params, thread,
                                  results, query_arguments))
        thread_arr.append(thread_add)

    for thread in thread_arr:
        thread.start()

    for thread in thread_arr:
        thread.join()

    return results

def main(params):

    datafile = params.out_folder + "/data"
    evfw = EvalFramework.EvalFramework(datafile)

    print('ENGINE: {} - DB_SIZE: {} - N_THREADS: {}'.format(
                                                params.db_type,
                                                params.db_name,
                                                params.numthreads))
    print("============================\n")

    for query_args in QUERY_PARAMS:

        # Set probabilities so that results returned a controlled
        # number of results
        query = query_args["key"]
        q_key_prob = query.replace('_resize','')
        for i in range(len(query_args["probs"])):
            query_args["probs"][i] = PROB_MAPPING[params.db_name][q_key_prob]

        print('Query:{}'.format(query_args))

        all_times = []
        all_len = []

        for iteration in range(params.numiters):  # Number of times to average
            print('====== ITERATION: {} ======'.format(iteration), flush=True)

            start_t = time.time()
            results = run_query(params, query_args)
            end_time_iteration = time.time() - start_t

            all_times.append([res['response_time'] for res in results if res])
            all_len.append(  [res['response_len']  for res in results if res])

            print('ITERATION TIME: {:0.4f}s ({:0.4f} mins)'.format(
                                    end_time_iteration,
                                    end_time_iteration / 60.), flush=True)
            print('Query Time Avg: {:0.4f}s'.format(np.mean(all_times)),
                                                    flush=True)
            print('N Results Avg: {:0.4f} \n'.format(np.mean(all_len)),
                                                    flush=True)

        print("\n")

        len_all_times = len(all_times)
        len_all_len   = len(all_len)
        # Reject outliers outside 2 std on measurements.
        all_times = reject_outliers(np.array(all_times))
        all_len   = reject_outliers(np.array(all_len))

        if (len(all_times) / len_all_times) < 0.4:
            print("WARNING: Rejecting too many samples!")

        evfw.add_row(query_args["key"],
                     params.db_type,
                     params.db_name,
                     params.numthreads,
                     params.numiters,
                     np.mean(all_times),
                     np.std (all_times),
                     np.mean(all_len),
                     np.std (all_len),
                     )

    evfw.export_to_csv()

if __name__ == '__main__':
    args = get_args()
    main(args)
