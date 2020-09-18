#!/bin/bash
db_sizes="100k,500k,1M,5M,10M,50M,100M"

for db in vdms
do
    for size in 1M 5M 10M 50M 100M
    do
        # Run VDMS Queries
        echo "Running $db ${size}..."
        python3 find_probs.py \
                -db_type=$db \
                -db_name=$size
    done
done
