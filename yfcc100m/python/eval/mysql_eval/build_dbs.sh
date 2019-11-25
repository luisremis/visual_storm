#!/bin/bash

# Build dbs

# for size in 100k
for size in 100k 500k 1M 5M
do
python3 build_yfcc_db_mysql.py \
    -data_file \
    /mnt/yfcc100m/metadata/processed/yfcc100m_photo_dataset_${size} \
    -tag_file \
    /mnt/yfcc100m/metadata/processed/yfcc100m_photo_autotags_${size}_extended \
    -tag_list /mnt/yfcc100m/metadata/processed/autotag_list.txt \
    -db_name "yfcc_${size}" \
    -db_host "127.0.0.1" \
    -db_port 3360 \
    -db_user "root" \
    -db_pswd ""
done
