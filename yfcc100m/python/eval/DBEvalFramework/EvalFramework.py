import os

import numpy as np
from numpy import inf
from numpy import nan

import pandas as pd

from DBEvalFramework import Plotting

class EvalFramework(object):

    def __init__(self, experiment_name):

        self.experiment_name = experiment_name

        try:
            self.data = pd.read_csv(experiment_name + ".csv", index_col=0)
        except:
            print("File not found, creating a new onself...")
            self.data = pd.DataFrame(columns=[
                    "query", "engine", "db_size",
                    "n_threads",
                    "n_samples",
                    "query_time_avg", "query_time_std",
                    "n_results", "n_results_std",
                    ])

        self.export_to_csv()

    def add_row(self, query, engine, db_size,
            n_threads,
            n_samples,
            query_time_avg, query_time_std,
            n_results, n_results_std):

        self.data.loc[len(self.data)] = [
                query,
                engine,
                db_size,
                n_threads,
                n_samples,
                query_time_avg,
                query_time_std,
                n_results,
                n_results_std,
            ]

    def clear(self):

        self.data = pd.DataFrame(columns=[
                    "query", "engine", "db_size",
                    "n_threads",
                    "n_samples",
                    "query_time_avg", "query_time_std",
                    "n_results", "n_results_std",
                    ])

        self.export_to_csv()

    def export_to_csv(self):

        self.data.to_csv(self.experiment_name + ".csv")

    def get_unique(self, column):

        arr = []
        vals = self.data.loc[:,column]

        # arr = [v for v in vals if v not in arr]
        for val in vals:
            if val not in arr:
                arr.append(val)

        return arr

    def get_arr_for_eng_q_dbsize(self, engine, query, db_size, key):

        arr = self.data[self.data["query"] == query]
        arr = arr[self.data["engine"]      == engine]
        arr = arr[self.data["db_size"]     == db_size]
        arr = arr[key].to_numpy()

        return arr

    def get_arr_for_eng_q_threads(self, engine, query, threads, key):

        arr = self.data[self.data["query"] == query]
        arr = arr[self.data["engine"]      == engine]
        arr = arr[self.data["n_threads"]   == threads]
        arr = arr[key].to_numpy()

        return arr

    def get_arr_for_eng_q_threads(self, engine, query, threads, key):

        arr = self.data[self.data["query"] == query]
        arr = arr[self.data["engine"]      == engine]
        arr = arr[self.data["n_threads"]   == threads]
        arr = arr[key].to_numpy()

        return arr

    def plot_all(self, folder="plots"):
        self.plot_folder=folder
        self.plot_folder += "/"

        if not os.path.exists(self.plot_folder):
            os.makedirs(self.plot_folder)

        # print(self.data)
        self.plot_all_for_db_size()
        self.plot_all_for_n_clients()
        self.plot_all_for_all_queries()

    def plot_all_for_all_queries(self):

        threads  = self.get_unique("n_threads")
        queries  = self.get_unique("query")

        if len(queries) == 1:
            return

        print("Plotting plot_all_for_all_queries...")

        for q in queries:
            self.plot_results_throughput_parallelism_threads(q, result_type="Images")


    def plot_all_for_n_clients(self):

        threads  = self.get_unique("n_threads")
        queries  = self.get_unique("query")

        if len(threads) == 1:
            return

        db_sizes = self.get_unique("db_size")

        print("Plotting plot_all_for_n_clients...")

        for i in db_sizes:

            self.plot_results_throughput_parallelism_queries(i, result_type="Images")

        for i in queries:
            self.plot_results_throughput_parallelism_dbsizes(i, result_type="Images")

    def plot_all_for_db_size(self):

        db_sizes = self.get_unique("db_size")

        if len(db_sizes) == 1:
            return

        threads = self.get_unique("n_threads")

        print("Plotting plot_all_for_db_size...")

        for i in threads:

            self.plot_query_time(i)
            self.plot_query_throughput(i)
            self.plot_results_throughput(i, result_type="Images")
            self.plot_query_time_speedup(i)
            self.plot_n_results(i)

    def plot_results_throughput_parallelism_threads(self, q,
                                            result_type="results"):

        # Plot query times:
        threads  = self.get_unique("n_threads")
        queries  = self.get_unique("query")
        engines  = self.get_unique("engine")
        db_sizes = self.get_unique("db_size")

        # Todo make general for more db_sizes
        values = np.zeros(len(db_sizes) * 2)

        for eng in engines:
            for th in threads:

                times     = self.get_arr_for_eng_q_threads(eng, q, th,
                                                            "query_time_avg")
                times_std = self.get_arr_for_eng_q_threads(eng, q, th,
                                                            "query_time_std")
                n_results = self.get_arr_for_eng_q_threads(eng, q, th,
                                                            "n_results")

                # Compute Results per second
                rps   = 1/times * th * n_results
                rps[rps == inf] = 0

                stds  = rps * (times_std / times)

                # print("values:",len(values, len(values[0])))
                # print("rps:",len(rps))

                values = np.vstack((values, np.append(rps, stds)))

        values = values[1:,:] # remove initial row of zeros

        p = Plotting.Plotting()

        # filename  = self.plot_folder + "plot_conc_q_"
        # filename += str(q) + "_results_throughput_threads.pdf"

        # title = "Throughput as " + result_type + " per second Summary"
        # p.plot_lines_all(str(threads), db_sizes, engines, values,
        #                   title=title,
        #                   filename=filename,
        #                   log="both",
        #                   xlabel="Database Size",
        #                   ylabel=result_type + "/s")

        filename  = self.plot_folder + "plot_q_"
        filename += str(q) + "_mosaic_results_throughput_threads.pdf"

        threads = ["clients: " + str(a) for a in threads]
        # title = "Throughput for " + q
        # title += " as Database Size increases"
        p.plot_lines_all_mosaic(threads, db_sizes, engines, values,
                          filename=filename,
                          # title=title,
                          log="both",
                          xlabel="Database Size",
                          ylabel=result_type + "/s")



    def plot_results_throughput_parallelism_dbsizes(self, q,
                                            result_type="results"):

        # Plot query times:
        threads  = self.get_unique("n_threads")
        queries  = self.get_unique("query")
        engines  = self.get_unique("engine")
        db_sizes = self.get_unique("db_size")

        # Todo make general for more db_sizes
        values = np.zeros(len(threads) * 2)

        for eng in engines:
            for db_size in db_sizes:

                times     = self.get_arr_for_eng_q_dbsize(eng, q, db_size,
                                                            "query_time_avg")
                times_std = self.get_arr_for_eng_q_dbsize(eng, q, db_size,
                                                            "query_time_std")
                threads   = self.get_arr_for_eng_q_dbsize(eng, q, db_size,
                                                            "n_threads")
                n_results = self.get_arr_for_eng_q_dbsize(eng, q, db_size,
                                                            "n_results")

                # Compute Results per second
                rps   = 1/times * threads * n_results
                rps[rps == inf] = 0

                stds  = rps * (times_std / times)

                values = np.vstack((values, np.append(rps, stds)))

        values = values[1:,:] # remove initial row of zeros

        p = Plotting.Plotting()

        filename  = self.plot_folder + "plot_conc_q_"
        filename += str(q) + "_results_throughput_db_size.pdf"

        title = "Throughput as " + result_type + " per second - Summary"
        p.plot_lines_all(db_sizes, threads, engines, values,
                          title=title,
                          filename=filename,
                          xlabel="# of concurrent clients",
                          ylabel=result_type + "/s")

        filename  = self.plot_folder + "plot_conc_q_"
        filename += str(q) + "_mosaic_results_throughput_db_size.pdf"

        # title = "Throughput for " + q
        # title += " as number of concurrent clients increases"
        p.plot_lines_all_mosaic(db_sizes, threads, engines, values,
                          filename=filename,
                          # title=title,
                          xlabel="# of concurrent clients",
                          ylabel=result_type + "/s")


    def plot_results_throughput_parallelism_queries(self, db_size,
                                            result_type="results"):

        # Plot query times:
        threads  = self.get_unique("n_threads")
        queries  = self.get_unique("query")
        engines  = self.get_unique("engine")

        # Todo make general for more db_sizes
        values = np.zeros(len(threads) * 2)

        for eng in engines:
            for q in queries:

                times     = self.get_arr_for_eng_q_dbsize(eng, q, db_size,
                                                            "query_time_avg")
                times_std = self.get_arr_for_eng_q_dbsize(eng, q, db_size,
                                                            "query_time_std")
                threads   = self.get_arr_for_eng_q_dbsize(eng, q, db_size,
                                                            "n_threads")
                n_results = self.get_arr_for_eng_q_dbsize(eng, q, db_size,
                                                            "n_results")
                stds      = self.get_arr_for_eng_q_dbsize(eng, q, db_size,
                                                            "n_results_std")

                # Compute Results per second
                rps   = 1/times * threads * n_results
                rps[rps == inf] = 0

                stds  = rps * (times_std / times)

                values = np.vstack((values, np.append(rps, stds)))

        values = values[1:,:] # remove initial row of zeros

        p = Plotting.Plotting()

        filename  = self.plot_folder + "plot_conc_dbsize_"
        filename += str(db_size) + "_results_throughput.pdf"

        title = "Throughput as " + result_type + " per second - Summary"
        p.plot_lines_all(queries, threads, engines, values,
                          title=title,
                          filename=filename,
                          xlabel="# of concurrent clients",
                          ylabel=result_type + "/s")

        filename  = self.plot_folder + "plot_conc_dbsize_"
        filename += str(db_size) + "_mosaic_results_throughput.pdf"

        # title = "Throughput for " + db_size
        # title += " as number of concurrent clients increases"
        p.plot_lines_all_mosaic(queries, threads, engines, values,
                          filename=filename,
                          # title=title,
                          xlabel="# of concurrent clients",
                          ylabel=result_type + "/s")


    def plot_results_throughput(self, n_threads, result_type="results"):

        # Plot query times:
        db_sizes = self.get_unique("db_size")
        queries  = self.get_unique("query")
        engines  = self.get_unique("engine")

        # Todo make general for more db_sizes
        values = np.zeros(len(db_sizes) * 2)

        for eng in engines:
            for q in queries:

                times     = self.get_arr_for_eng_q_threads(eng, q, n_threads,
                                                            "query_time_avg")
                times_std = self.get_arr_for_eng_q_threads(eng, q, n_threads,
                                                            "query_time_std")
                n_results = self.get_arr_for_eng_q_threads(eng, q, n_threads,
                                                            "n_results")

                # Compute Results per second
                rps   = 1/times * n_threads * n_results
                rps[rps == inf] = 0

                stds  = rps * (times_std / times)

                values = np.vstack((values, np.append(rps, stds)))

        values = values[1:,:] # remove initial row of zeros

        p = Plotting.Plotting()

        filename  = self.plot_folder
        filename += "plot_th_" + str(n_threads) + "_results_throughput.pdf"

        title = "Throughput as " + result_type + " per second - Summary"
        p.plot_lines_all(queries, db_sizes, engines, values, log="both",
                          title=title,
                          filename=filename,
                          ylabel=result_type + "/s")

        filename  = self.plot_folder
        filename += "plot_th_" + str(n_threads) + "_mosaic_results_throughput.pdf"

        # title = "Throughput for different queries"
        p.plot_lines_all_mosaic(queries, db_sizes, engines, values, log="both",
                          # title=title,
                          filename=filename,
                          xlabel="Database Size",
                          ylabel=result_type + "/s")


    def plot_query_throughput(self, n_threads):

        # Plot query times:
        db_sizes = self.get_unique("db_size")
        queries  = self.get_unique("query")
        engines  = self.get_unique("engine")

        values = np.zeros(len(db_sizes) * 2)

        for eng in engines:
            for q in queries:

                times   = self.get_arr_for_eng_q_threads(eng, q, n_threads,
                                                            "query_time_avg")
                stds    = self.get_arr_for_eng_q_threads(eng, q, n_threads,
                                                            "query_time_std")

                qps = 1/times * n_threads
                qps[qps == inf] = 0

                stds  = qps * (stds / times)

                values = np.vstack((values, np.append(qps, stds)))

        values = values[1:,:] # remove initial row of zeros

        p = Plotting.Plotting()

        filename  = self.plot_folder
        filename += "plot_th_" + str(n_threads) + "_queries_throughput.pdf"

        title = "Query Throughput (q/s) Summary"
        p.plot_lines_all(queries, db_sizes, engines, values, log="both",
                          title=title,
                          filename=filename,
                          ylabel="Queries per second")

        filename  = self.plot_folder
        filename += "plot_th_" + str(n_threads) + "_mosaic_query_throughput.pdf"

        # title = "Query Throughput (q/s) for different queries"
        p.plot_lines_all_mosaic(queries, db_sizes, engines, values, log="both",
                          # title=title,
                          filename=filename,
                          xlabel="Database Size",
                          ylabel="Queries per second")


    def plot_query_time(self, n_threads):

        # Plot query times:
        db_sizes = self.get_unique("db_size")
        queries  = self.get_unique("query")
        engines  = self.get_unique("engine")

        values = np.zeros(len(db_sizes) * 2)

        for eng in engines:
            for q in queries:

                times = self.get_arr_for_eng_q_threads(eng,q, n_threads,
                                                            "query_time_avg")
                stds  = self.get_arr_for_eng_q_threads(eng, q, n_threads,
                                                            "query_time_std")

                values = np.vstack((values, np.append(times, stds)))

        values = values[1:,:] # remove initial row of zeros

        p = Plotting.Plotting()

        filename  = self.plot_folder
        filename += "plot_th_" + str(n_threads) + "_query_times.pdf"

        title = "Query Execution Time(s) Summary"
        p.plot_lines_all(queries, db_sizes, engines, values, log="both",
                          title=title,
                          filename=filename,
                          ylabel="Average Query Time(s)")

        filename  = self.plot_folder
        filename += "plot_th_" + str(n_threads) + "_mosaic_query_times.pdf"

        # title = "Query Execution Time(s) for different queries"
        p.plot_lines_all_mosaic(queries, db_sizes, engines, values, log="both",
                          # title=title,
                          filename=filename,
                          xlabel="Database Size",
                          ylabel="Average Query Time(s)")

        return


    def plot_n_results(self, n_threads):

        # Plot query times:
        db_sizes = self.get_unique("db_size")
        queries  = self.get_unique("query")
        engines  = self.get_unique("engine")

        values = np.zeros(len(db_sizes) * 2)

        for eng in engines:
            for q in queries:

                n_res = self.get_arr_for_eng_q_threads(eng,q, n_threads,
                                                            "n_results")
                stds  = self.get_arr_for_eng_q_threads(eng, q, n_threads,
                                                            "n_results_std")

                values = np.vstack((values, np.append(n_res, stds)))

        values = values[1:,:] # remove initial row of zeros

        p = Plotting.Plotting()

        filename  = self.plot_folder
        filename += "plot_th_" + str(n_threads) + "_n_results.pdf"

        title = "Returned Results Summary"
        p.plot_lines_all(queries, db_sizes, engines, values, log="both",
                          title=title,
                          filename=filename,
                          ylabel="Number of Results")

        filename  = self.plot_folder
        filename += "plot_th_" + str(n_threads) + "_mosaic_n_results.pdf"

        title = "Returned Results for different queries"
        p.plot_lines_all_mosaic(queries, db_sizes, engines, values, log="x",
                          title=title,
                          filename=filename,
                          xlabel="Database Size",
                          ylabel="Number of Results")

        return

    # Bar plot
    def plot_query_time_speedup(self, n_threads):

        # Plot query times:
        db_sizes = self.get_unique("db_size")
        engines  = self.get_unique("engine")

        if len(engines) < 2:
            print("Single engine, no speedup plot generated")
            return

        # This will only compute speedup of eng[0] vs eng[i > 0].

        for sub_eng in range(1,len(engines)):

            # We need to get queries every times because we append "avg"
            queries  = self.get_unique("query")

            s_engines = [engines[0], engines[sub_eng]]
            values = np.zeros(len(db_sizes) * 2)

            for eng in s_engines:
                for q in queries:

                    times = self.get_arr_for_eng_q_threads(eng, q, n_threads,
                                                            "query_time_avg")
                    stds  = self.get_arr_for_eng_q_threads(eng, q, n_threads,
                                                            "query_time_std")

                    values = np.vstack((values, np.append(times, stds)))

            values = values[1:,:] # remove initial row of zeros

            # Compute speedup
            for i in range(len(queries)):
                values[i,:] = values[len(queries)+i, :] / values[i, :]

            values = values[0:len(queries),:]

            # compute average and add "avg" row to queries
            avgs = np.mean(values, axis=0)
            values = np.vstack((values, avgs))
            queries.append("avg")

            p = Plotting.Plotting()

            filename  = self.plot_folder
            filename += "plot_th_" + str(n_threads) + "_query_times_speedup_"
            filename += s_engines[1] + ".pdf"

            title  = "Speedup of " + s_engines[0] + " over " + s_engines[1]
            title += " for all queries"
            p.plot_bars(queries, db_sizes, values,
                        filename=filename,
                        title=title,
                        log="y")

        return
