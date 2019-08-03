import argparse
import time

import pandas as pd
import util


def get_args():
    obj = argparse.ArgumentParser()
    # Database Info
    obj.add_argument('-db_name', type=str, required=True,
                     help='Comma separated list of database names')
    obj.add_argument('-db_host', type=str, required=True,
                     help='Name of memsql host')
    obj.add_argument('-db_port', type=int, default=3306,
                     help='Port of memsql [default: 3306]')
    obj.add_argument('-db_user', type=str, default='root',
                     help='Username of database [default: root]')
    obj.add_argument('-db_pswd', type=str, default='',
                     help='Password of database [default: ""]')
    obj.add_argument('-perf_out', type=str, default=None,  #'memsql_performance.csv',
                     help='CSV Filename for query measurements [default: memsql_performance.csv]')
    params = obj.parse_args()

    params.db_name = params.db_name.split(',')
    return params


def add_performance_row(perf_df, database, groupname, statname, statvalue):
    perf_df.at[statname + '_' + groupname, database] = statvalue
    perf_df.at[statname + '_' + groupname, 'Query'] = groupname
    perf_df.at[statname + '_' + groupname, 'Stat'] = statname
    return perf_df
    
    
def main(in_args):
    # Queries 
    # queries: list of dictionaries
    # dictionary = {'type': <query type>, 'query':{<key>:<condition>}}
    # type: autotags
    #   dict['query'] = {<autotag>: <autotag prob>}
    #     <autotag>: autotag constraint
    #     <autotag prob>: probability constraint (>=)
    #     RETURNS: entries >= prob
    queries = [{'type': 'autotags',
                'query':{'alligator': 0.8}},
               {'type': 'autotags',
                'query':{'pizza': 0.5, 'wine': 0.5}}]
    groups = [' AND '.join(['{} >= {}'.format(k, v) for k, v in q['query'].items()]) for q in queries]

    # Prepare table of measurements
    performance = pd.DataFrame(columns=['Query', 'Stat'] + in_args.db_name)

    for db in in_args.db_name:
        for tag_interests, group in zip(queries, groups):
            start_time = time.time()

            # Get line_number, id, autotags, and download_url for autotags
            query_fn = getattr(util, 'query_{}'.format(tag_interests['type']))
            sql_response, end_time_metadata = query_fn(tag_interests['query'], host=in_args.db_host, port=in_args.db_port,
                               user=in_args.db_user, pswd=in_args.db_pswd, db=db)

            num_transactions = len(sql_response)

            # Use line_number to get image path and display image
            end_time_img = util.get_query_images(sql_response)

            # Resize image to 224x224, and display image
            end_time_resize = util.get_query_images(sql_response, width=224, height=224)

            # Total time
            end_time_total = time.time() - start_time
            # end_time_total = end_time_metadata + end_time_img + end_time_resize

            # Print Stats
            print('[!] Find all images/autotags with {}'.format(group))
            print('\t[!] Elapsed time ({} entries returned): {:0.4f} secs ({:0.4f} mins)'.
                  format(num_transactions, end_time_metadata, end_time_metadata / 60.))
            print('\tElapsed time (display image from path): {:0.4f} secs ({:0.4f} mins)'.
                  format(end_time_img, end_time_img / 60.))
            print('\tElapsed time (display resized image from path): {:0.4f} secs ({:0.4f} mins)'.
                  format(end_time_resize, end_time_resize / 60.))
            print('\t[!] Total Elapsed time: {:0.4f} secs ({:0.4f} mins)'.format(end_time_total, end_time_total / 60.))

            # Log Measurements                                  
            performance = add_performance_row(performance, db, group, '# Entries Returned', num_transactions)
            performance = add_performance_row(performance, db, group, '[secs] Metadata', round(end_time_metadata, 4))
            performance = add_performance_row(performance, db, group, '[Tx/sec] Metadata', round(num_transactions / end_time_metadata, 4))
            performance = add_performance_row(performance, db, group, '[secs] Display Image', round(end_time_img, 4))
            performance = add_performance_row(performance, db, group, '[Tx/sec] Display Image', round(num_transactions / end_time_img, 4))
            performance = add_performance_row(performance, db, group, '[secs] Display Resized Image', round(end_time_resize, 4))
            performance = add_performance_row(performance, db, group, '[Tx/sec] Display Resized Image', round(num_transactions / end_time_resize, 4))
            performance = add_performance_row(performance, db, group, '[secs] Total', round(end_time_total, 4))
            performance = add_performance_row(performance, db, group, '[Tx/sec] Total', round(num_transactions / end_time_total, 4))
    if in_args.perf_out:
        performance.to_csv(in_args.perf_out)


if __name__ == '__main__':
    args = get_args()
    main(args)
