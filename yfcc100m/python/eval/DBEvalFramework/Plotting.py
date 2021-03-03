import csv
import os
import re
import argparse
from pathlib import Path

# from cycler import cycler
import numpy as np
import matplotlib

matplotlib.use('pdf')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


color      = ['red', 'blue', 'orange', 'black', 'pink', 'brown', 'violet', 'green']
linestyles = ['-', '--', '-.']
markers    = ['o', '*', 'd']
patterns = [ "" ,"" , "", "", "\\", ".", "*",  "\\" , "|" , "-" ]

class Plotting(object):

    def __init__(self):

        return

    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def instr2bool(self, in_value):
        if in_value.lower() in ['true', 't']:
            return True
        else:
            return False

    def value_to_float(self, x):
        if type(x) == float or type(x) == int or type(x) == np.int64:
            return x

        if 'k' in x:
            if len(x) > 1:
                return float(x.replace('k', '')) * 1000
            return 1000.0
        if 'M' in x:
            if len(x) > 1:
                return float(x.replace('M', '')) * 1000000
            return 1000000.0
        return 0.0


    # This will plot query time (in seconds) as a function of
    # database size for all the queries.
    # This will name que queries using engine_query for all the queries.
    # values is in the format:
    #   query0_dbsize0_time,query0_dbsize0_std, ... , query0_dbsizeN_time,query0_dbsizeN_std
    def plot_lines_all(self, queries, db_sizes, engines, values,
                        log="y",
                        title="Query Time",
                        filename="plot_unnamed.pdf",
                        xlabel="Database Size",
                        ylabel="None"):

        # print(len(values))
        # print(len(values[1:]))
        # print(values)
        if (len(db_sizes) * 2) != len(values[1,:]):
            print("Error input size")
            print("db_sizes:", db_sizes)
            print("values:", values)
            return

        if len(queries) * len(engines) != len(values[:,1]):
            print("Error input size")
            print("queries:", queries)
            print("values:", values)
            return

        n_queries = len(queries)

        # local_markers = []
        # local_linesty = []
        # local_color   = []

        # aux = int(n_queries / len(engines))

        # for i in range(len(engines)):
        #     local_markers += [markers[i]    for j in range(aux)]
        #     local_linesty += [linestyles[i] for j in range(aux)]
        #     local_color   += [color[j]      for j in range(aux)]

        fig = plt.figure()
        plt.rc('lines', linewidth=1)
        ax0 = plt.subplot()

        x_pos = [self.value_to_float(i) for i in db_sizes]

        for j in range(len(engines)):
            for i in range(n_queries):
                ax0.errorbar(x_pos,
                             values[j*len(engines) + i,0:len(db_sizes)],
                             yerr=values[j*len(engines) + i,len(db_sizes):],
                             label=engines[j] + "_" + queries[i],
                             color=color[i],
                             linestyle=linestyles[j],
                             marker=markers[j],
                             )

        if log == "x" or log == "both":
            ax0.set_xscale('log')
        if log == "y" or log == "both":
            ax0.set_yscale('log')
        # ax0.set_ylim(1,10**4)

        plt.xticks(x_pos, db_sizes)

        ax0.set_title(title)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)

        if len(engines) > 2 or n_queries > 2:
            plt.legend(bbox_to_anchor=(0, -0.15),
                       loc="upper left",
                       # mode="expand",
                       borderaxespad=0,
                       ncol=len(engines),
                       fancybox=True,
                       )
        else:
            plt.legend(loc="best",
                       ncol=len(engines),
                       shadow=True, fancybox=True)

        plt.savefig(filename, format="pdf", bbox_inches='tight')
        plt.close()

    def plot_lines_all_mosaic(self, queries, db_sizes, engines, values,
                        log="y",
                        title="",
                        filename="plot_unnamed.pdf",
                        xlabel="",
                        ylabel=""):

        # print(len(values))
        # print(len(values[1:]))
        # print(values)
        if (len(db_sizes) * 2) != len(values[1,:]):
            print("Error input size")
            print("db_sizes:", db_sizes)
            print("values:", values)
            return

        if len(queries) * len(engines) != len(values[:,1]):
            print("Error input size")
            print("queries:", queries)
            print("values:", values)
            return

        n_queries = len(queries)

        local_markers = []
        local_linesty = []
        local_color   = []

        aux = int(n_queries / len(engines))

        for i in range(len(engines)):
            local_markers += [markers[i]    for j in range(aux)]
            local_linesty += [linestyles[i] for j in range(aux)]
            local_color   += [color[j]      for j in range(aux)]

        import math
        side = math.ceil(math.sqrt(n_queries))

        # fig = plt.figure()
        fig = plt.figure(figsize=(12,12))

        if title != "":
            fig.suptitle(title, fontsize=16)

        for i in range(len(queries)):

            ax0 = plt.subplot(side,side,i+1)

            ax0.set_title(queries[i])

            x_pos = [self.value_to_float(i) for i in db_sizes]

            for j in range(len(engines)):
                ax0.errorbar(x_pos,
                             values[n_queries*j + i,0:len(db_sizes)],
                             yerr=values[n_queries*j + i,len(db_sizes):],
                             label=engines[j],
                             color=color[j],
                             linestyle=linestyles[j % len(linestyles)],
                             marker=markers[j % len(markers)],
                             )

            if log == "x" or log == "both":
                ax0.set_xscale('log')
            if log == "y" or log == "both":
                ax0.set_yscale('log')
            # ax0.set_ylim(1,10**4)

            plt.xticks(x_pos, db_sizes, fontsize=10)

            if i == 0:
                plt.legend(loc="best", ncol=1, shadow=True, fancybox=True)

            if i % side == 0:
                plt.ylabel(ylabel, fontsize=12)

            if i >= (n_queries - side):
                plt.xlabel(xlabel, fontsize=12)

        plt.savefig(filename, format="pdf", bbox_inches='tight')
        plt.close()

    def plot_bars(self, queries, db_sizes, values,
                  title="Generic (but Awesome) Bar Plot",
                  filename="plot_summary.pdf",
                  xlabel="Database Size",
                  ylabel="Speedup ?",
                  log="none"):

        fig, ax0 = plt.subplots(nrows=1)
        fig.set_size_inches(12, 3)

        bar_width = 1 / (len(queries) + 1) # 0.15
        n_groups = len(db_sizes)
        index = np.arange(n_groups)
        opacity = 0.7

        for i in range(len(queries)):

            vals = values[i,0:len(db_sizes)]

            if queries[i] == "avg":
                local_color = "cyan"
                local_pattern = "\\"
            else:
                local_color = color[i]
                local_pattern = ""

            plt.bar(index + i*bar_width,
                    vals,
                    bar_width,
                    alpha=opacity,
                    color=local_color,
                    hatch=local_pattern,
                    # yerr=err,
                    # error_kw=error_config,
                    label=queries[i])

        ax0.set_title(title)

        ax0.set_xticks(index + (len(db_sizes) / 2 + 1) * bar_width)
        ax0.set_xticklabels(db_sizes, fontsize=10)
        ax0.tick_params(axis='y', labelsize=10)

        limit = values[:,0:len(db_sizes)].max() * 1.5

        # ax0.set_ylim(0.1, limit)

        plt.ylabel('Speedup', fontsize=12)

        if log == "x" or log == "both":
            ax0.set_xscale('log')
        if log == "y" or log == "both":
            ax0.set_yscale('log')

        plt.axhline(y=1)

        if len(queries) > 4:
            plt.legend(bbox_to_anchor=(0, -0.15),
                       loc="upper left",
                       # mode="expand",
                       borderaxespad=0,
                       ncol=4,
                       fancybox=True,
                       fontsize=9.5,
                       )
        else:
            plt.legend(ncol=7, shadow=True, fancybox=True,
                       fontsize=9.5, loc="upper left")

        plt.savefig(filename, format="pdf", bbox_inches='tight')
        plt.close()
