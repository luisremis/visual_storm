#!/bin/bash

# # Drop all the dbs
# for size in 100k 500k 1M 5M
# do
# python3 drop_all.py \
#     -db_name "yfcc_${size}" \
#     -db_host "sky3.local" \
#     -db_port 3306 \
#     -db_user "root" \
#     -db_pswd ""
# done

# Build dbs

for size in 100k 500k 1M 5M
do
python3 build_yfcc_db_memsql.py \
    -data_file \
    /mnt/yfcc100m/metadata/processed/yfcc100m_photo_dataset_${size} \
    -tag_file \
    /mnt/yfcc100m/metadata/processed/yfcc100m_photo_autotags_${size}_extended \
    -tag_list /mnt/yfcc100m/metadata/processed/autotag_list.txt \
    -db_name "yfcc_${size}" \
    -db_host "sky3.local" \
    -db_port 3306 \
    -db_user "root" \
    -db_pswd ""
done
