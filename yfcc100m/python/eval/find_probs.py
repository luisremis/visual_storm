import argparse
import time
from threading import Thread
import json

import pandas as pd
import numpy as np

from mysql_eval  import MySQLQuery
from memsql_eval import MemSQLQuery
from vdms_eval   import VDMSQuery

from DBEvalFramework import EvalFramework

VDMS_PORT_MAPPING = {'100k': 55500, '500k': 55405,
                     '1M':   55501, '5M':   55450,
                     '10M':  55510, '50M':  55000,
                     '100M': 50000}

QUERY_PARAMS = [
            {'key': '1tag',
             'tags': ["alligator"], 'probs': [0.98],
             'operations': [],
             'comptype': "and" },
            {'key': '1tag_loc20',
             'tags': ["alligator"], 'probs': [0.5],
             'lat': -14.354356, 'long': -39.002567,
             'range_dist': 20,
             'operations': [],
             'comptype': "and"  },
            {'key': '2tag_and',
             'tags': ["alligator", "lake"], 'probs': [0.95, 0.95],
             'comptype': "and" },
            {'key': '2tag_or',
             'tags': ["alligator", "lake"], 'probs': [0.9, 0.9],
             'comptype': "or" },
            {'key': '2tag_loc20_and',
             'tags': ["alligator", "lake"], 'probs': [0.55, 0.55],
             'lat': -14.354356, 'long': -39.002567,
             'range_dist': 20,
             'comptype': "and" },
            {'key': '2tag_loc20_or',
             'tags': ["alligator", "lake"], 'probs': [0.95, 0.95],
             'lat': -14.354356, 'long': -39.002567,
             'range_dist': 20,
             'comptype': "or" },

              ]

def get_args():
    obj = argparse.ArgumentParser()

    # Database Info
    obj.add_argument('-db_type', type=str, default='vdms',
                     choices=["vdms", "memsql", "mysql"],
                     help='Database names: vdms, memsql, mysql')
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
    obj.add_argument('-numthreads', type=int, default=1,
                     help='Number of workers [default: 4]')
    obj.add_argument('-numiters', type=int, default=1,
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
    else:
        # VDMS needs port mapping
        params.db_host = "sky4.local"
        params.db_port = VDMS_PORT_MAPPING[params.db_name]

    return params


def run_query_thread(obj, params, index, results, query_arguments):

    # Here the object runs the query and returns time and len
    data_dict = obj.run_query(query_arguments)
    results[index].update(data_dict)

def run_query(params, query_arguments):

    thread_arr = []
    results = [{}] * (params.numthreads)
    list_of_objs = []

    if (params.db_type == "vdms"):
        for i in range(params.numthreads):
            list_of_objs.append(
                        VDMSQuery.VDMSQuery(params.db_host, params.db_port))
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

    # print('DB_SIZE: {}'.format(params.db_name))
    # print("============================\n")

    desire_results = 200
    error = 0.3

    result_dic = {}

    for query_args in QUERY_PARAMS:

        # print('Query: {}'.format(query_args["key"]))

        num_results = 0

        prob_max = 1.0
        prob_min = 0.0
        prob = query_args["probs"][0]

        while True :

            start_t = time.time()
            results = run_query(params, query_args)
            end_time_metadata = time.time() - start_t

            # print("Trying Prob:", prob)
            num_results = np.sum([res['response_len'] for res in results if res])
            # print("desire: ", desire_results, "num_results:", num_results)

            if abs(num_results - desire_results) < desire_results * error:
                # print("Found!")
                break

            if num_results < desire_results:
                prob_max = prob
            else:
                prob_min = prob

            prob = (prob_max + prob_min) / 2.0
            for i in range(len(query_args["probs"])):
                query_args["probs"][i] = prob

            if prob < 0.1:
                break

            # print("prob_min: ", prob_min, "prob_max:", prob_max)

        print('Query: {}, Prob: {}, Results: {}'.format(query_args["key"], prob, num_results))
        result_dic[query_args["key"]] = prob
        # print("Found Prob:", prob, "Results:", num_results)

    print(json.dumps(result_dic, indent=2))


if __name__ == '__main__':
    args = get_args()
    main(args)
