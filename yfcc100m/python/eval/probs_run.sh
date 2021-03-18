#!/bin/bash

rm probs.log

for size in 1M 5M 10M 50M 100M
do
    # Run VDMS Queries
    echo "Running $db ${size}..."
    python3 find_probs.py \
            -db_type=vdms \
            -db_name=$size >> probs.log 2>> probs.log
done
