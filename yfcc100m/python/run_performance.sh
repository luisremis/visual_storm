#!/bin/bash
ntags=10
nthreads=10
niter=10
outfile=perf_nq10_nthread10_niter10.csv

mkdir -p perf_results

# Run VDMS Queries
python3 performance.py -db_name=100k -numtags=$ntags -numthreads=$nthreads -numiters=$niter -out=perf_results/$outfile > perf_results/vdms_100k.log
python3 performance.py -db_name=1M -numtags=$ntags -numthreads=$nthreads -numiters=$niter -append_out=perf_results/$outfile > perf_results/vdms_1M.log

# Run MemSQL Queries
cd memsql
python3 performance.py -db_name=yfcc_100k -numtags=$ntags -numthreads=$nthreads -numiters=$niter -append_out=../perf_results/$outfile > ../perf_results/memsql_100k.log
python3 performance.py -db_name=yfcc_1M -numtags=$ntags -numthreads=$nthreads -numiters=$niter -append_out=../perf_results/$outfile > ../perf_results/memsql_1M.log

# Force remove temporary storage for images
rm -rf tmp

# Convert performance results to format for plotting
cd ..
python3 convert_perf_results.py -results=perf_results/$outfile -out=perf_results/perf_results.log

# Plot results
python3 plot_performance.py -infile=perf_results/perf_results.log -outfile=perf_results/plots/perf_results_plot.pdf

