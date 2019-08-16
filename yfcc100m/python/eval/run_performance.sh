#!/bin/bash
ntags=2
nthreads=100
niter=100
outfile=perf_ntags${ntags}_nthread${nthreads}_niter${niter}.csv

mkdir -p perf_results

# Run VDMS Queries
echo "Running vdms_100k..."
python3 vdms/performance.py -db_name=100k -numtags=$ntags -numthreads=$nthreads -numiters=$niter -out=perf_results/$outfile > perf_results/vdms_100k.log
echo "Running vdms_1M..."
python3 vdms/performance.py -db_name=1M -numtags=$ntags -numthreads=$nthreads -numiters=$niter -append_out=perf_results/$outfile > perf_results/vdms_1M.log

# Run MemSQL Queries
echo "Running memsql_100k..."
python3 memsql/performance.py -db_name=yfcc_100k -numtags=$ntags -numthreads=$nthreads -numiters=$niter -append_out=perf_results/$outfile > perf_results/memsql_100k.log
echo "Running memsql_1M..."
python3 memsql/performance.py -db_name=yfcc_1M -numtags=$ntags -numthreads=$nthreads -numiters=$niter -append_out=perf_results/$outfile > perf_results/memsql_1M.log

# Force remove temporary storage for images
rm -rf tmp

# Convert performance results to format for plotting
python3 convert_perf_results.py -cols='100k,1M' -results=perf_results/$outfile -out=perf_results/perf_results.log

# Plot results
python3 plot_performance.py -infile=perf_results/perf_results.log -outfile=perf_results/plots/perf_results_plot.pdf
