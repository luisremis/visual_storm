#!/bin/bash
nthreads=1
niter=1
ntags=1

result_folder=perf_results
outfile=${result_folder}/perf_ntags${ntags}_nthread${nthreads}_niter${niter}.csv
result_log=${result_folder}/perf_results.log
result_pdf=${result_folder}/plots/perf_results_plot.pdf

# Force remove temporary storage for images
rm -rf tmp
rm -rf $result_folder
mkdir -p $result_folder
append=-out # The first need to be create and not append

for db in vdms memsql
do
    for size in 100k 1M
    do
        # Run VDMS Queries
        echo "Running $db ${size}..."
        python3 $db/performance.py \
                -db_name=$size \
                -numtags=$ntags \
                -numthreads=$nthreads \
                -numiters=$niter \
                ${append}=$outfile > $result_folder/${db}_${size}.log

        append=-append_out
    done
done

# Convert performance results to format for plotting
python3 convert_perf_results.py \
        -cols="100k,1M" \
        -numtags=$ntags \
        -numthreads=$nthreads \
        -numiters=$niter \
        -results=$outfile \
        -out=$result_log

# Plot results
python3 plot_performance.py \
        -log=True \
        -infile=$result_log \
        -outfile=${result_pdf}
