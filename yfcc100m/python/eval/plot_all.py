import argparse
import time

from DBEvalFramework import EvalFramework

def main(args):

    e = EvalFramework.EvalFramework(args.in_file)
    e.plot_all(folder=args.out_folder)

def get_args():
    obj = argparse.ArgumentParser()

    obj.add_argument('-in_file', type=str, default=None,
                     help='Input dataframe file (csv)')

    obj.add_argument('-out_folder', type=str, default=None,
                     help='Output folder where plots will go')

    params = obj.parse_args()

    if params.in_file == None:
        print("Need input file.")
        exit()

    if params.out_folder == None:
        print("Need output folder.")
        exit()

    return params

if __name__ == '__main__':
    args = get_args()
    main(args)

