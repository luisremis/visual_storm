#!/bin/bash
nthreads=56
niter=10
ntags=10

result_folder=perf_results
outfile=${result_folder}/perf_ntags${ntags}_nthread${nthreads}_niter${niter}.csv
result_log=${result_folder}/perf_results.log
result_pdf=${result_folder}/plots/perf_results_plot.pdf

# Force remove temporary storage for images
rm -rf $result_folder
mkdir -p $result_folder
append=-out # The first need to be create and not append

for db in vdms mysql
do
    for size in 100k 500k 1M 5M
    do
        # Run VDMS Queries
        echo "Running $db ${size}..."
        python3 performance.py \
                -db_type=$db \
                -db_name=$size \
                -numtags=$ntags \
                -numthreads=$nthreads \
                -numiters=$niter \
                ${append}=$outfile \
                > $result_folder/${db}_${size}.log
                2> $result_folder/${db}_${size}_error.log

        append=-append_out
    done
done

# Read number of images returned from logs
python3 parse_logs.py \
        -dir=$result_folder \
        -perf_csv=$outfile \
        -db_sizes="100k,500k,1M,5M" \
        -out=${result_folder}/perf_run_summary.csv \
        -dbs='vdms,mysql'

# Convert performance results to format for plotting
python3 convert_perf_results.py \
        -cols="100k,500k,1M,5M" \
        -numtags=$ntags \
        -numthreads=$nthreads \
        -numiters=$niter \
        -results=${result_folder}/perf_run_summary.csv \
        -out=$result_log

# Plot results
python3 plot_performance.py \
        -log=True \
        -infile=$result_log \
        -outfile=${result_pdf}

cp -r ${result_folder} perf_results-${ntags}-${nthreads}-${niter}