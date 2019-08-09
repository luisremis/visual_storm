import pandas as pd
import argparse


def get_args():
    obj = argparse.ArgumentParser()

    # File Information
    obj.add_argument('-results', type=str, default='test_results.csv',
                     help='Results CSV file')
    obj.add_argument('-out', type=str, default='perf_results/perf_results.log',
                     help='Filename to save results table [default: perf_results/perf_results.log]')
                     
    # Configs from performance run
    obj.add_argument('-cols', type=str, default='100k,1M,10M',
                     choices=['100k','1M','10M'],
                     help='Column names: 100k,1M,10M')
    obj.add_argument('-numtags', type=int, default=10,
                     help='Number of queries to process per thread [default: 10]')
    obj.add_argument('-numthreads', type=int, default=10,
                     help='Number of workers [default: 10]')
    obj.add_argument('-numiters', type=int, default=10,
                     help='Number of times to process all threads [default: 10]')
    params = obj.parse_args()
    return params


def main(params):
    data = pd.read_csv(params.results, index_col=0)
    cols = list(set([c.split(' ')[0] for c in data.columns if c.split(' ')[0] in params.cols]))
    
    with open(params.out, 'w') as log:
        print('YFCC100M - Queries - nq: {} nt: {} ni: {}'.format(params.numtags, params.numthreads, params.numiters), file=log)
        print('idx,{}'.format(','.join(cols)), file=log)
        for descriptor in data.index:
            line = descriptor
            for c in cols:
                line += ',{},{}'.format(data.at[descriptor, c + ' Tx/sec'],data.at[descriptor, c + ' imgs/sec'])
            print(line, file=log)


if __name__ == '__main__':
    args = get_args()
    main(args)

