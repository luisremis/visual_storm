#!/bin/bash
niter=20
ntags=2

result_folder=concurreny_results
result_log=${result_folder}/conc_results.log
result_pdf_prefix=${result_folder}/plots/res

# Force remove temporary storage for images
rm -rf $result_folder
mkdir -p $result_folder


flag="first"
thread_list=""

db=mysql
# for size in 100k 500k 1M 5M 10M 50M 100M

for nthreads in 1 2 4 8 16 32 56 64
do
    outfile=${result_folder}/conc_ntags${ntags}_nthread${nthreads}_niter${niter}.csv
    append=-out # The first need to be create and not append
    for size in 1M 5M 10M 50M
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
                > $result_folder/${db}_${size}_${nthreads}.log
                2> $result_folder/${db}_${size}_${nthreads}_error.log

        append=-append_out
    done

    # This will automaticalle create the thread_list string.
    if [ "$flag" = "first" ]; then
        flag="no"
    else
        thread_list=${thread_list},
    fi
    thread_list=${thread_list}${size}

done

# # Read number of images returned from logs
# python3 parse_logs.py \
#         -dir=$result_folder \
#         -perf_csv=$outfile \
#         -db_sizes=$thread_list \
#         -out=${result_folder}/conc_run_summary.csv \
#         -dbs='vdms'

# # Convert performance results to format for plotting
# python3 convert_perf_results.py \
#         -cols=$thread_list \
#         -numtags=$ntags \
#         -numthreads=$nthreads \
#         -numiters=$niter \
#         -results=${result_folder}/conc_run_summary.csv \
#         -out=$result_log

# Plot results
# python3 plot_performance.py \
#         -infile=$result_log \
#         -outfile=${result_pdf_prefix}

results_folder_copy=conc_results-${ntags}-${niter}-${db}

rm -r $results_folder_copy
cp -r $result_folder $results_folder_copy
