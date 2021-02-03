#!/bin/bash
NITER=5
experiment_name=perf_all_threads_images

running_folder=running_experiment
info=${running_folder}/info.txt

# Force remove temporary storage for images
rm -rf $running_folder
mkdir -p $running_folder

echo "running" $experiment_name "..."
echo $experiment_name "started..." >> $info

date >> $info

for th in 2 4 8 16 32 56 64 112
# for th in 4 8 16
do
    # for size in 1M 5M 10M 50M
    for size in 1M 5M 10M 50M 100M
    do
        for db in vdms mysql
        do
            # Run VDMS Queries
            echo "Running $th $db ${size}..." >> $info
            python3 performance.py \
                    -db_type=$db \
                    -db_name=$size \
                    -numthreads=$th \
                    -numiters=$NITER \
                    -out_folder=$running_folder \
                    >> $running_folder/log.log
                    2>> $running_folder/log_error.log
        done
    done
done

date >> $info

data_file=${running_folder}/data
python3 plot_all.py -in_file=$data_file -out_folder=${running_folder}/plots

results_folder_copy=$experiment_name

rm -r $results_folder_copy
cp -r $running_folder $results_folder_copy

date >> $info

echo "Experiment Done" >> $info
