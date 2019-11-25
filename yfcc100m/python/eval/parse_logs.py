import argparse
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt


def get_args():
    obj = argparse.ArgumentParser()
    obj.add_argument('-dir', type=str, default='perf_results',
                     help='Directory where performance logs are located')
    obj.add_argument('-out', type=str, default='perf_results/time summary/perf_run_summary.csv',
                     help='Path to write summary of logs [default: perf_results/time summary/perf_run_summary.csv]')
    obj.add_argument('-dbs', type=str, default='vdms,mysql',
                     help='Comma-separated string of dbs compared. [default:vdms,mysql]')
    params = obj.parse_args()
    params.dbs = params.dbs.split(',')
    return params


def main(params):
    queries = ['_1tag_resize', '_2tag_resize', '_2tag_loc20_resize']
    outfile = params.out
    subs = ['Avg query metadata time [secs] ', 'Std query metadata time [secs] ',
            'Avg query images time [secs] ', 'Std query images time [secs] ',
            'Avg # responses ', 'Std # responses ', 'Avg # images ', 'Std # images ']
    xlabels = ['100k', '500k', '1M', '5M']
    cols = []
    for cstr in subs:
        for sz in xlabels:
            cols.append(cstr + sz)
    summary = pd.DataFrame(columns=cols)
    query_name = []

    # Get summary data
    for db in params.dbs:
        for sz in xlabels:
            path = os.path.join(params.dir, '{}_{}.log'.format(db, sz))
            with open(path, 'r') as file:
                query_idx = -1
                for line in file:
                    if line.startswith('Query:{'):
                        query_idx += 1
                        avg_meta_time = []
                        avg_img_time = []
                        avg_num_resp = []
                        avg_num_imgs = []
                    if line.startswith('Queries metadata TIME:'):
                        # start_idx = line.find('(') + 1
                        # end_idx = line.find(' mins)')
                        start_idx = line.find('Queries metadata TIME:') + len('Queries metadata TIME:')
                        end_idx = line.find('s (')
                        tmp = float(line[start_idx:end_idx])
                        avg_meta_time.append(tmp)
                    if line.startswith('Queries images TIME:'):
                        # start_idx = line.find('(') + 1
                        # end_idx = line.find(' mins)')
                        start_idx = line.find('Queries images TIME:') + len('Queries images TIME:')
                        end_idx = line.find('s (')
                        tmp = float(line[start_idx:end_idx])
                        avg_img_time.append(tmp)
                    if line.startswith('# responses: '):
                        start_idx = line.find('responses: ') + len('responses: ')
                        end_idx = line.find('\n')
                        tmp = float(line[start_idx:end_idx])
                        avg_num_resp.append(tmp)
                    if line.startswith('# images: '):
                        start_idx = line.find('# images: ') + len('# images: ')
                        end_idx = line.find('\n')
                        tmp = float(line[start_idx:end_idx])
                        avg_num_imgs.append(tmp)
                    if line.startswith('[!] Avg. Images'):
                        query = db + queries[query_idx % 3]
                        summary.at[query, 'Avg query metadata time [secs] ' + sz] = np.mean(avg_meta_time)
                        summary.at[query,  'Avg query images time [secs] ' + sz] = np.mean(avg_img_time)
                        summary.at[query,  'Avg # responses ' + sz] = np.mean(avg_num_resp)
                        summary.at[query,  'Avg # images ' + sz] = np.mean(avg_num_imgs)
                        summary.at[query,  'Std query metadata time [secs] ' + sz] = np.std(avg_meta_time)
                        summary.at[query,  'Std query images time [secs] ' + sz] = np.std(avg_img_time)
                        summary.at[query,  'Std # responses ' + sz] = np.std(avg_num_resp)
                        summary.at[query,  'Std # images ' + sz] = np.std(avg_num_imgs)
                        if query not in query_name:
                            query_name.append(query)
    summary.to_csv(outfile)

    # Reformat data
    qry_avg_meta_time_per_sz = []
    qry_std_meta_time_per_sz = []
    qry_avg_img_time_per_sz = []
    qry_std_img_time_per_sz = []
    qry_avg_num_resp_per_sz = []
    qry_std_num_resp_per_sz = []
    qry_avg_num_imgs_per_sz = []
    qry_std_num_imgs_per_sz = []
    for qidx, query in enumerate(query_name):
        avg_meta_time_per_sz = []
        std_meta_time_per_sz = []
        avg_img_time_per_sz = []
        std_img_time_per_sz = []
        avg_num_resp_per_sz = []
        std_num_resp_per_sz = []
        avg_num_imgs_per_sz = []
        std_num_imgs_per_sz = []
        for sz in xlabels:
            avg_meta_time_per_sz.append(summary.at[query, 'Avg query metadata time [secs] ' + sz])
            std_meta_time_per_sz.append(summary.at[query,  'Std query metadata time [secs] ' + sz])
            avg_img_time_per_sz.append(summary.at[query,  'Avg query images time [secs] ' + sz])
            std_img_time_per_sz.append(summary.at[query,  'Std query images time [secs] ' + sz])
            avg_num_resp_per_sz.append(summary.at[query,  'Avg # responses ' + sz])
            std_num_resp_per_sz.append(summary.at[query,  'Std # responses ' + sz])
            avg_num_imgs_per_sz.append(summary.at[query,  'Avg # images ' + sz])
            std_num_imgs_per_sz.append(summary.at[query,  'Std # images ' + sz])
        qry_avg_meta_time_per_sz.append(avg_meta_time_per_sz)
        qry_std_meta_time_per_sz.append(std_meta_time_per_sz)
        qry_avg_img_time_per_sz.append(avg_img_time_per_sz)
        qry_std_img_time_per_sz.append(std_img_time_per_sz)
        qry_avg_num_resp_per_sz.append(avg_num_resp_per_sz)
        qry_std_num_resp_per_sz.append(std_num_resp_per_sz)
        qry_avg_num_imgs_per_sz.append(avg_num_imgs_per_sz)
        qry_std_num_imgs_per_sz.append(std_num_imgs_per_sz)

    # Plot data
    color = ['red', 'blue', 'orange', 'red', 'blue', 'orange']
    linestyles = ['-', '-', '-', '--', '--', '--', ]
    markers = ['o', 'o', 'o', '*', '*', '*']
    plot = "all"
    x_pos = [1e5, 5e5, 1e6, 5e6]
    tick_labels = xlabels
    plotfilename = '.'.join(outfile.split('.')[:-1])

    # Plot Avg query metadata time [secs]
    fig = plt.figure()
    plt.rc('lines', linewidth=1)
    ax0 = plt.subplot()
    for qidx, query in enumerate(query_name):
        ax0.errorbar(x_pos, qry_avg_meta_time_per_sz[qidx], yerr=qry_std_meta_time_per_sz[qidx],
                     label=query, color=color[qidx], linestyle=linestyles[qidx],
                     marker=markers[qidx])
    ax0.set_yscale('log')
    ax0.set_xscale('log')
    plt.xticks(x_pos, tick_labels)
    plt.xlabel('Number of Images', fontsize=12)
    plt.ylabel('Avg query metadata time [secs]', fontsize=12)
    plt.legend(loc="best", ncol=1, shadow=True, fancybox=True)
    plt.savefig(plotfilename + "_metadata_time.pdf", format="pdf", bbox_inches='tight')

    # Plot Avg query images time [secs]
    fig = plt.figure()
    plt.rc('lines', linewidth=1)
    ax0 = plt.subplot()
    for qidx, query in enumerate(query_name):
        ax0.errorbar(x_pos, qry_avg_img_time_per_sz[qidx], yerr=qry_std_img_time_per_sz[qidx],
                     label=query, color=color[qidx], linestyle=linestyles[qidx],
                     marker=markers[qidx])
    ax0.set_yscale('log')
    ax0.set_xscale('log')
    plt.xticks(x_pos, tick_labels)
    plt.xlabel('Number of Images', fontsize=12)
    plt.ylabel('Avg query images time [secs]', fontsize=12)
    plt.savefig(plotfilename + "_img_time.pdf", format="pdf", bbox_inches='tight')

    # Plot Avg # responses
    fig = plt.figure()
    plt.rc('lines', linewidth=1)
    ax0 = plt.subplot()
    for qidx, query in enumerate(query_name):
        ax0.errorbar(x_pos, qry_avg_num_resp_per_sz[qidx], yerr=qry_std_num_resp_per_sz[qidx],
                     label=query, color=color[qidx], linestyle=linestyles[qidx],
                     marker=markers[qidx])
    ax0.set_yscale('log')
    ax0.set_xscale('log')
    plt.xticks(x_pos, tick_labels)
    plt.xlabel('Number of Images', fontsize=12)
    plt.ylabel('Avg # responses', fontsize=12)
    plt.savefig(plotfilename + "_num_resp.pdf", format="pdf", bbox_inches='tight')

    # Plot Avg # images
    fig = plt.figure()
    plt.rc('lines', linewidth=1)
    ax0 = plt.subplot()
    for qidx, query in enumerate(query_name):
        ax0.errorbar(x_pos, qry_avg_num_imgs_per_sz[qidx], yerr=qry_std_num_imgs_per_sz[qidx],
                     label=query, color=color[qidx], linestyle=linestyles[qidx],
                     marker=markers[qidx])
    ax0.set_yscale('log')
    ax0.set_xscale('log')
    plt.xticks(x_pos, tick_labels)
    plt.xlabel('Number of Images', fontsize=12)
    plt.ylabel('Avg # images returned', fontsize=12)
    plt.savefig(plotfilename + "_num_imgs.pdf", format="pdf", bbox_inches='tight')


if __name__ == '__main__':
    args = get_args()
    main(args)
