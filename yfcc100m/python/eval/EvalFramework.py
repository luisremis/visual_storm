import numpy as np
import pandas as pd

import Plotting

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

        print(self.data)

    def export_to_csv(self):

        print(self.data)

        self.data.to_csv(self.experiment_name + ".csv")

    def get_unique(self, column):

        arr = []
        vals = self.data.loc[:,column]

        # arr = [v for v in vals if v not in arr]
        for val in vals:
            if val not in arr:
                arr.append(val)

        return arr

    def get_arr_for_end_and_q(self, engine, query, key):

        arr = self.data[self.data["query"] == query]
        arr = arr[self.data["engine"] == engine]
        arr = arr[key].to_numpy()

        return arr

    # For a given query and engine, it will return an array with all the times
    def get_times_for_eng_and_q(self, engine, query):

        return self.get_arr_for_end_and_q(engine, query, "query_time_avg")

    # For a given query and engine, it will return an array with all the stds
    def get_stds_for_eng_and_q(self, engine, query):

        return self.get_arr_for_end_and_q(engine, query, "query_time_std")

    # For a given query and engine, it will return an array with all the n_threads
    def get_threads_for_eng_and_q(self, engine, query):

        return self.get_arr_for_end_and_q(engine, query, "n_threads")

    # For a given query and engine, it will return an array with all the n_results
    def get_results_for_eng_and_q(self, engine, query):

        return self.get_arr_for_end_and_q(engine, query, "n_results")

    def plot_all(self):

        threads = self.get_unique("n_threads")

        for i in threads:

            self.plot_query_time(i)
            self.plot_query_throughput(i)
            self.plot_results_throughput(i, result_type="Images")

    def plot_results_throughput_parallelism(self, n_threads,
                                            result_type="results"):

        # Plot query times:
        db_sizes = self.get_unique("db_size")
        queries  = self.get_unique("query")
        engines  = self.get_unique("engine")

        # Todo make general for more db_sizes
        values = np.zeros(len(db_sizes) * 2)

        for eng in engines:
            for q in queries:

                times     = self.get_times_for_eng_and_q(eng,q)
                threads   = self.get_threads_for_eng_and_q(eng, q)
                n_results = self.get_results_for_eng_and_q(eng, q)
                stds      = self.get_arr_for_end_and_q(eng, q, "n_results_std")

                from numpy import inf
                from numpy import nan

                # Compute Results per second
                rps   = 1/times * threads * n_results
                rps[rps == inf] = 0
                where_are_NaNs = np.isnan(rps)
                rps[where_are_NaNs] = 0

                stds  = 1/stds  * threads * n_results
                stds[stds == inf] = 0
                where_are_NaNs = np.isnan(stds)
                stds[where_are_NaNs] = 0

                values = np.vstack((values, np.append(rps, stds)))

        values = values[1:,:]

        p = Plotting.Plotting()

        p.plot_lines_all(queries, db_sizes, engines, values, log=True,
                          title=result_type + " per second",
                          filename="plot_" + str(n_threads) + "_results_throughput.pdf",
                          ylabel=result_type + "/s")

        p.plot_lines_all_mosaic(queries, db_sizes, engines, values, log=True,
                          title=result_type + " per second",
                          filename="plot_" + str(n_threads) + "_results_throughput_mosaic.pdf",
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

                times     = self.get_times_for_eng_and_q(eng,q)
                threads   = self.get_threads_for_eng_and_q(eng, q)
                n_results = self.get_results_for_eng_and_q(eng, q)
                stds      = self.get_arr_for_end_and_q(eng, q, "n_results_std")

                from numpy import inf
                from numpy import nan

                # Compute Results per second
                rps   = 1/times * threads * n_results
                rps[rps == inf] = 0
                where_are_NaNs = np.isnan(rps)
                rps[where_are_NaNs] = 0

                stds  = 1/stds  * threads * n_results
                stds[stds == inf] = 0
                where_are_NaNs = np.isnan(stds)
                stds[where_are_NaNs] = 0

                values = np.vstack((values, np.append(rps, stds)))

        values = values[1:,:]

        p = Plotting.Plotting()

        p.plot_lines_all(queries, db_sizes, engines, values, log=True,
                          title=result_type + " per second",
                          filename="plot_" + str(n_threads) + "_results_throughput.pdf",
                          ylabel=result_type + "/s")

        p.plot_lines_all_mosaic(queries, db_sizes, engines, values, log=True,
                          title=result_type + " per second",
                          filename="plot_" + str(n_threads) + "_results_throughput_mosaic.pdf",
                          ylabel=result_type + "/s")

    def plot_query_throughput(self, n_threads):

        # Plot query times:
        db_sizes = self.get_unique("db_size")
        queries  = self.get_unique("query")
        engines  = self.get_unique("engine")

        values = np.zeros(len(db_sizes) * 2)

        for eng in engines:
            for q in queries:

                times   = self.get_times_for_eng_and_q(eng,q)
                threads = self.get_threads_for_eng_and_q(eng, q)
                stds    = self.get_stds_for_eng_and_q(eng, q)

                from numpy import inf
                qps = 1/times * threads
                qps[qps == inf] = 0

                stds  = 1/stds  * threads
                stds[stds == inf] = 0

                values = np.vstack((values, np.append(qps, stds)))

        values = values[1:,:]

        p = Plotting.Plotting()

        p.plot_lines_all(queries, db_sizes, engines, values, log=True,
                          title="Queries per second",
                          filename="plot_" + str(n_threads) + "_queries_throughput.pdf",
                          ylabel="Queries per second")

        p.plot_lines_all_mosaic(queries, db_sizes, engines, values, log=True,
                          title="Queries per second - Mosaic",
                          filename="plot_" + str(n_threads) + "_query_throughput_mosaic.pdf",
                          ylabel="Queries per second")

    def plot_query_time(self, n_threads):

        # Plot query times:
        db_sizes = self.get_unique("db_size")
        queries  = self.get_unique("query")
        engines  = self.get_unique("engine")

        values = np.zeros(len(db_sizes) * 2)

        for eng in engines:
            for q in queries:

                times = self.get_times_for_eng_and_q(eng, q)
                stds  = self.get_stds_for_eng_and_q(eng, q)

                values = np.vstack((values, np.append(times, stds)))

        values = values[1:,:]

        p = Plotting.Plotting()

        p.plot_lines_all(queries, db_sizes, engines, values,
                          title="Query Times",
                          filename="plot_" + str(n_threads) + "_query_times.pdf",
                          ylabel="Average Query Time(s)")

        p.plot_lines_all_mosaic(queries, db_sizes, engines, values,
                          title="Query Times - Mosaic",
                          filename="plot_" + str(n_threads) + "_query_times_mosaic.pdf",
                          ylabel="Average Query Time(s)")

        return
