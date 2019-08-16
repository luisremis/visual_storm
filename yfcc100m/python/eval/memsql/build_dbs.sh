#!/bin/bash

for size in 100k 1M
do
python3 build_yfcc_db_memsql.py \
    -data_file \
    /mnt/yfcc100m/metadata/processed/yfcc100m_photo_dataset_${size} \
    -tag_file \
    /mnt/yfcc100m/metadata/processed/yfcc100m_photo_autotags_${size}_extended \
    -tag_list /mnt/yfcc100m/metadata/processed/autotag_list.txt \
    -db_name "yfcc_${size}" \
    -db_host "sky3.jf.intel.com" \
    -db_port 3306 \
    -db_user "root" \
    -db_pswd ""
done
