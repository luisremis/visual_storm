import argparse
import time
from threading import Thread

import pandas as pd
import numpy as np

from mysql_eval  import MySQLQuery
from memsql_eval import MemSQLQuery
from vdms_eval   import VDMSQuery

VDMS_PORT_MAPPING = {'100k': 55500, '500k': 55405,
                     '1M':   55501, '5M':   55450,
                     '10M':  55510, '50M':  55000,
                     '100M': 50000}

# SIZE_PROB_MAPPING = {'100k': 0.21, '500k': 0.41,
#                      '1M':   0.55, '5M':   0.65,
#                      '10M':  0.70, '50M':  0.75,
#                      '100M': 0.82}

SIZE_PROB_MAPPING = {'100k': 0.81, '500k': 0.81,
                     '1M':   0.81, '5M':   0.81,
                     '10M':  0.81, '50M':  0.81,
                     '100M': 0.81}

RESIZE = {"type": "resize", "width": 224, "height": 224}
QUERY_PARAMS = [{'key': '_1tag_resize',
                 'tags': ["alligator"],
                 'probs': [0.9],
                 'operations': [RESIZE] },
                {'key': '_2tag_resize',
                 'tags': ["alligator", "lake"],
                 'probs': [0.4, 0.4],
                 'operations': [RESIZE] },
                {'key': '_2tag_loc20_resize',
                 'tags': ["alligator", "lake"],
                  'probs': [0.2, 0.2],
                  'lat': -14.354356, 'long': -39.002567,
                  'range_dist': 20,
                  'operations': [RESIZE] }
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
    obj.add_argument('-numtags', type=int, default=1,
                     help='Number of queries to process per thread [default: 10]')
    obj.add_argument('-numthreads', type=int, default=1,
                     help='Number of workers [default: 10]')
    obj.add_argument('-numiters', type=int, default=1,
                     help='Number of times to process all threads [default: 10]')

    # Output CSV
    obj.add_argument('-out', type=str, default=None,
                     help='CSV Filename for measurements [default: vdms_perf_nq{NUM_TRANSACTIONS}_nthread{NUM_THREADS}_niter{NUM_ITERATIONS}_db{db_name}.csv]')
    obj.add_argument('-append_out', type=str, default=None,
                     help='CSV Filename to update measurements')

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

    if params.out == params.append_out:
        params.out = params.db_type + '_perf_nq{}_nthread{}_niter{}_db{}.csv'.format(
                            params.numtags,
                            params.numthreads,
                            params.numiters,
                            params.db_name)
    return params


def get_thread_metadata(obj, params, index, results, query_arguments):

    for ix in range(params.numtags):
        # print('\nTAG:{}\tLAT:{}\tLON:{}'.format(query_arguments['tags'], query_arguments['lat'] if 'lat' in query_arguments else '', query_arguments['long'] if 'long' in query_arguments else ''))
        tag   = query_arguments['tags']
        probs = query_arguments['probs']
        lat   = query_arguments['lat']  if 'lat'  in query_arguments else -1
        long  = query_arguments['long'] if 'long' in query_arguments else -1
        range_dist = query_arguments['range_dist'] if 'range_dist' in query_arguments else 0
        operations = query_arguments['operations'] if 'operations' in query_arguments else []

        data_dict = obj.get_metadata_by_tags(tag, probs, lat,
                                             long, range_dist,
                                             return_response=False)
        results[index + ix].update(data_dict)

    if params.numthreads == 1:
        return results

def get_thread_images(obj, params, index, results, query_arguments):

    for ix in range(params.numtags):
        # print('\nTAG:{}\tLAT:{}\tLON:{}'.format(query_arguments['tags'], query_arguments['lat'] if 'lat' in query_arguments else '', query_arguments['long'] if 'long' in query_arguments else ''))
        tag   = query_arguments['tags']
        probs = query_arguments['probs']
        lat   = query_arguments['lat'] if 'lat' in query_arguments else -1
        long  = query_arguments['long'] if 'long' in query_arguments else -1
        range_dist = query_arguments['range_dist'] if 'range_dist' in query_arguments else 0
        operations = query_arguments['operations'] if 'operations' in query_arguments else []

        data_dict = obj.get_images_by_tags(tag, probs,
                                           operations, lat, long,
                                           range_dist,
                                           return_images=False)
        results[index + ix].update(data_dict)

    if params.numthreads == 1:
        return results

def get_metadata(params, query_arguments):
    thread_arr = []
    results = [{}] * (params.numthreads * params.numtags)
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

    # Metadata queries
    for thread in range(params.numthreads):  # Number of threads processing at once
        # print('== METADATA THREAD: {} =='.format(thread))
        idx = (thread * params.numtags)
        if idx < (params.numthreads * params.numtags):
            if params.numthreads == 1:
                results = get_thread_metadata(list_of_objs[thread], params,
                                              idx, results, query_arguments)
            else:
                thread_add = Thread(target=get_thread_metadata,
                                    args=(list_of_objs[thread], params, idx,
                                          results, query_arguments))
                thread_arr.append(thread_add)
        else:
            break

    if params.numthreads != 1:
        for thread in thread_arr:
            thread.start()

    if params.numthreads != 1:
        for thread in thread_arr:
            thread.join()

    thread_arr = []
    #Image queries
    for thread in range(params.numthreads):  # Number of threads processing at once
        # print('== IMAGES THREAD: {} =='.format(thread))
        idx = (thread * params.numtags)
        if idx < (params.numthreads * params.numtags):
            if params.numthreads == 1:
                results = get_thread_images(list_of_objs[thread], params, idx,
                                            results, query_arguments)
            else:
                thread_add = Thread(target=get_thread_images,
                                    args=(list_of_objs[thread], params, idx,
                                          results, query_arguments))
                thread_arr.append(thread_add)
        else:
            break

    if params.numthreads != 1:
        for thread in thread_arr:
            thread.start()

    if params.numthreads != 1:
        for thread in thread_arr:
            thread.join()

    return results

def add_performance_row(params, perf_df, database, descriptor,
                        avg_tx_per_sec, std_tx_per_sec,
                        avg_img_per_sec, std_img_per_sec):

    perf_df.at[descriptor, database + ' Tx/sec']       = avg_tx_per_sec
    perf_df.at[descriptor, database + ' Tx/sec_std']   = std_tx_per_sec
    perf_df.at[descriptor, database + ' imgs/sec']     = avg_img_per_sec
    perf_df.at[descriptor, database + ' imgs/sec_std'] = std_img_per_sec

    return perf_df


def main(params):
    # Prepare table of measurements
    if params.append_out:
        performance = pd.read_csv(params.append_out, index_col=0)
        outfile = params.append_out
    else:
        outfile = params.out
        performance = pd.DataFrame(columns=[
                    params.db_name + ' Tx/sec',
                    params.db_name + ' Tx/sec_std',
                    params.db_name + ' imgs/sec',
                    params.db_name + ' imgs/sec_std',
                    ])

    for query_args in QUERY_PARAMS:

        # For this query, we put a high probability.
        if query_args["key"] == "_1tag_resize":
            for i in range(len(query_args["probs"])):
                query_args["probs"][i] = 0.8

        # For this query, we put a medium probability.
        if query_args["key"] == "_2tag_resize":
            for i in range(len(query_args["probs"])):
                query_args["probs"][i] = 0.4

        # For this query, we put a low probability.
        if query_args["key"] == "_2tag_loc20_resize":
            for i in range(len(query_args["probs"])):
                query_args["probs"][i] = 0.2

        # print('Query:{}'.format(query_args))
        print('DATABASE: {}'.format(params.db_name))

        all_tx_per_sec = []
        all_img_per_sec = []

        desire_images = 200
        error = 0.5
        num_images = 0

        prob_max = 1.0
        prob_min = 0.0
        prob = query_args["probs"][0]

        while abs(num_images - desire_images) > desire_images * error :

            # Get Metadata
            start_t = time.time()
            # print('Query:{}'.format(query_args))
            results = get_metadata(params, query_args)
            end_time_metadata = time.time() - start_t

            print("Trying Prob:", prob)

            # # Metadata transactions per sec
            # all_times = [res['response_time'] for res in results if res]
            # tx_per_sec = (params.numthreads) / np.mean(all_times)
            # all_tx_per_sec.append(tx_per_sec)
            # print('Queries metadata TIME: {:0.4f}s ({:0.4f} mins)'.format(
            #                         np.sum(all_times),
            #                         np.sum(all_times) / 60.), flush=True)

            # Images per sec
            num_images = np.sum([res['images_len'] for res in results if res])
            print("desire: ", desire_images, "num_images:", num_images)

            if num_images < desire_images:
                prob_max = query_args["probs"][0]
            else:
                prob_min = query_args["probs"][0]

            prob = (prob_max + prob_min) / 2.0
            for i in range(len(query_args["probs"])):
                query_args["probs"][i] = prob

            if prob < 0.001:
                break

            # print("prob_min: ", prob_min, "prob_max:", prob_max)

        print("Prob:", prob, "Images:", num_images)


        #     all_times = [res['images_time'] for res in results if res]
        #     img_per_sec = num_images / (np.mean(all_times) * params.numtags)
        #     all_img_per_sec.append(img_per_sec)
        #     print('Queries images TIME: {:0.4f}s ({:0.4f} mins)'.format(
        #                             np.sum(all_times),
        #                             np.sum(all_times) / 60.))

        #     print('# responses: {}'.format(len(all_times)))
        #     print('# images: {}'.format(num_images))
        #     print('ITERATION TIME: {:0.4f}s ({:0.4f} mins)'.format(
        #                             end_time_metadata,
        #                             end_time_metadata / 60.), flush=True)

        # avg_tx_per_sec  = np.mean(all_tx_per_sec)
        # std_tx_per_sec  = np.std(all_tx_per_sec)
        # avg_img_per_sec = np.mean(all_img_per_sec)
        # std_img_per_sec = np.std(all_img_per_sec)

        # Print info
        # print('[!] Avg. Metadata Transactions per sec: {:0.4f} - std:{:0.4f}'.format(avg_tx_per_sec, std_tx_per_sec))
        # print('[!] Avg. Images per sec: {:0.4f} - std:{:0.4f}'.format(
        #                             avg_img_per_sec,
        #                             std_img_per_sec))
        # print("\n")

        # Log Measurements
    #     performance = add_performance_row(params, performance,
    #                                         params.db_name,
    #                                         params.db_type + query_args['key'],
    #                                         avg_tx_per_sec, std_tx_per_sec,
    #                                         avg_img_per_sec, std_img_per_sec)
    # performance.to_csv(outfile)


if __name__ == '__main__':
    args = get_args()
    main(args)
