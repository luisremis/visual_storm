import argparse
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt


def get_args():
    obj = argparse.ArgumentParser()
    obj.add_argument('-dir', type=str, default='perf_results',
                     help='Directory where performance logs are located')
    obj.add_argument('-perf_csv', type=str, required=True,
                     help='CSV with database performance')
    obj.add_argument('-db_sizes', type=str, default="100k,500k,1M,5M",
                     help='Sizes of database')
    obj.add_argument('-out', type=str, default='perf_results/time summary/perf_run_summary.csv',
                     help='Path to write summary of logs [default: perf_results/time summary/perf_run_summary.csv]')
    obj.add_argument('-dbs', type=str, default='vdms,mysql',
                     help='Comma-separated string of dbs compared. [default:vdms,mysql]')
    params = obj.parse_args()
    params.dbs = params.dbs.split(',')
    params.db_sizes = params.db_sizes.split(',')
    return params


def main(params):
    prev_results = pd.read_csv(params.perf_csv, index_col=0)
    subs = [' Tx/sec', ' Tx/sec_std', ' imgs/sec', ' imgs/sec_std', ' #imgs', ' #imgs_std']
    new_cols = [sz + c for sz in params.db_sizes for c in subs]
    for c in list(set(new_cols) - set(prev_results.columns)):
        prev_results[c] = np.nan
    summary = prev_results[new_cols]

    queries = [
                '_1tag',
                '_1tag_resize',
                '_1tag_loc20_resize',
                '_2tag_loc20_resize',
                '_2tag_resize_and',
                '_2tag_loc20_resize_and',
                '_2tag_resize_or',
                '_2tag_loc20_resize_or',
              ]

    outfile = params.out
    query_name = []

    # Get summary data
    for db in params.dbs:
        for sz in params.db_sizes:
            path = os.path.join(params.dir, '{}_{}.log'.format(db, sz))
            with open(path, 'r') as file:
                query_idx = -1
                for line in file:
                    if line.startswith('Query:{'):
                        query_idx += 1
                        avg_num_imgs = []
                    if line.startswith('# images: '):
                        start_idx = line.find('# images: ') + len('# images: ')
                        end_idx = line.find('\n')
                        tmp = float(line[start_idx:end_idx])
                        avg_num_imgs.append(tmp)
                    if line.startswith('[!] Avg. Images'):
                        query = db + queries[query_idx % 3]
                        summary.at[query, sz + ' #imgs'] = np.mean(avg_num_imgs)
                        summary.at[query, sz + ' #imgs_std'] = np.std(avg_num_imgs)
                        if query not in query_name:
                            query_name.append(query)
    summary.to_csv(outfile)


if __name__ == '__main__':
    args = get_args()
    main(args)
