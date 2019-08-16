import argparse
import vdms
from threading import Thread

import pandas as pd
import numpy as np

import VDMSQuery
import time

PORT_MAPPING = {'100k': 55500, '1M': 55501, '10M': 55510, 'None': 55555}

RESIZE = {"type": "resize", "width": 224, "height": 224}
QUERY_PARAMS = [{'key': 'vdms_1tag_resize', 'tags': ["alligator"], 'probs': [0.2], 'operations': [RESIZE]},
                {'key': 'vdms_2tag_resize', 'tags': ["alligator", "lake"], 'probs': [0.2, 0.2], 'operations': [RESIZE]},
                {'key': 'vdms_2tag_loc20_resize', 'tags': ["alligator", "lake"], 'probs': [0.2, 0.2],
                 'lat': -14.354356, 'long': -39.002567, 'range_dist': 20, 'operations': [RESIZE]}]


def get_args():
    obj = argparse.ArgumentParser()

    # Database Info
    obj.add_argument('-db_name', type=str, default='100k',
                     choices=PORT_MAPPING.keys(),
                     help='Database names: 100k, 1M, 10M')
    obj.add_argument('-db_host', type=str, default="sky3.jf.intel.com",
                     help='Name of vdms host')

    # Run Config
    obj.add_argument('-numtags', type=int, default=10,
                     help='Number of queries to process per thread [default: 10]')
    obj.add_argument('-numthreads', type=int, default=10,
                     help='Number of workers [default: 10]')
    obj.add_argument('-numiters', type=int, default=10,
                     help='Number of times to process all threads [default: 10]')

    # Output CSV
    obj.add_argument('-out', type=str, default=None,
                     help='CSV Filename for measurements [default: vdms_perf_nq{NUM_TRANSACTIONS}_nthread{NUM_THREADS}_niter{NUM_ITERATIONS}_db{db_name}.csv]')
    obj.add_argument('-append_out', type=str, default=None,
                     help='CSV Filename to update measurements')
    params = obj.parse_args()

    params.db_port = PORT_MAPPING[params.db_name]
    if params.out == params.append_out:
        params.out = 'vdms_perf_nq{}_nthread{}_niter{}_db{}.csv'.format(
                            params.numtags,
                            params.numthreads,
                            params.numiters,
                            params.db_name)
    return params


def get_thread_metadata(obj, params, index, results, query_arguments):
    for ix in range(params.numtags):
        # print('\nTAG:{}\tLAT:{}\tLON:{}'.format(query_arguments['tags'], query_arguments['lat'] if 'lat' in query_arguments else '', query_arguments['long'] if 'long' in query_arguments else ''))
        tag = query_arguments['tags']
        probs = query_arguments['probs']
        lat = query_arguments['lat'] if 'lat' in query_arguments else -1
        long = query_arguments['long'] if 'long' in query_arguments else -1
        range_dist = query_arguments['range_dist'] if 'range_dist' in query_arguments else 0
        operations = query_arguments['operations'] if 'operations' in query_arguments else []

        data_dict = obj.get_metadata_by_tags(tag, probs, lat, long, range_dist, return_response=False)
        dd2 = obj.get_images_by_tags(tag, probs, operations, lat, long, range_dist, return_images=False)
        data_dict.update(dd2)
        results[index + ix] = data_dict

    if params.numthreads == 1:
        return results


def get_metadata(params, query_arguments):
    thread_arr = []
    results = [None] * (params.numthreads * params.numtags)
    list_of_objs = []
    for i in range(params.numthreads):
        list_of_objs.append(VDMSQuery.VDMSQuery(params.db_host, params.db_port))

    for thread in range(params.numthreads):  # Number of threads processing at once
        print('== METADATA THREAD: {} =='.format(thread))
        idx = (thread * params.numtags)
        if idx < (params.numthreads * params.numtags):
            if params.numthreads == 1:
                results = get_thread_metadata(list_of_objs[thread], params, idx, results, query_arguments)
            else:
                thread_add = Thread(target=get_thread_metadata,
                                    args=(list_of_objs[thread], params, idx, results, query_arguments))
                thread_add.start()
                thread_arr.append(thread_add)
        else:
            break

    if params.numthreads != 1:
        for thread in thread_arr:
            thread.join()
    return results


def add_performance_row(perf_df, database, descriptor, tx_per_sec, img_per_sec):
    perf_df.at[descriptor, database + ' Tx/sec'] = tx_per_sec
    perf_df.at[descriptor, database + ' imgs/sec'] = img_per_sec
    return perf_df


def main(params):
    # Prepare table of measurements
    if params.append_out:
        performance = pd.read_csv(params.append_out, index_col=0)
        outfile = params.append_out
    else:
        outfile = params.out
        performance = pd.DataFrame(columns=[params.db_name + ' Tx/sec', params.db_name + ' imgs/sec'])

    for query_args in QUERY_PARAMS:
        print('Query:{}'.format(query_args))
        print('DATABASE: {}'.format(params.db_name))
        all_tx_per_sec = 0
        all_img_per_sec = 0
        for iteration in range(params.numiters):  # Number of times to average
            print('====== ITERATION: {} ======'.format(iteration))

            # Get Metadata
            start_t = time.time()
            results = get_metadata(params, query_args)
            end_time_metadata = time.time() - start_t

            # Metadata transactions per sec
            all_times = [res['response_time'] for res in results if res]
            tx_per_sec = (params.numtags * params.numthreads) / np.max(all_times)
            all_tx_per_sec += tx_per_sec

            # Images per sec
            num_images = np.sum([res['images_len'] for res in results if res])
            all_times = [res['images_time'] for res in results if res]
            img_per_sec = num_images / np.max(all_times)
            all_img_per_sec += img_per_sec

            print('# responses: {}'.format(len(all_times)))
            print('# images: {}'.format(num_images))
            print('ITERATION TIME: {:0.4f}s ({:0.4f} mins)'.format(end_time_metadata, end_time_metadata / 60.))

        avg_tx_per_sec = all_tx_per_sec / params.numiters
        avg_img_per_sec = all_img_per_sec / params.numiters

        # Print info
        print('\n[!] Avg. Metadata Transactions per sec: {:0.4f}'.format(avg_tx_per_sec))
        print('[!] Avg. Images per sec: {:0.4f}'.format(avg_img_per_sec))

        # Log Measurements
        performance = add_performance_row(performance, params.db_name, query_args['key'], avg_tx_per_sec,
                                          avg_img_per_sec)
    performance.to_csv(outfile)


if __name__ == '__main__':
    args = get_args()
    main(args)
