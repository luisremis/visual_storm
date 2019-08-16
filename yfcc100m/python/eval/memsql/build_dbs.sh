
# Build 100k version

python3 build_yfcc_db_memsql.py \
    -data_file \
    /mnt/data/metadata/yfcc100m_short/yfcc100m_photo_dataset_100k \
    -tag_file \
    /mnt/data/metadata/yfcc100m_short/yfcc100m_photo_autotags_100k_extended \
    -db_name "yfcc_100k" \
    -db_host "sky3.jf.intel.com" \
    -db_port 3306 \
    -db_user "root" \
    -db_pswd ""

# Build 1M version

python3 build_yfcc_db_memsql.py \
    -data_file \
    /mnt/data/metadata/yfcc100m_short/yfcc100m_photo_dataset_1M \
    -tag_file \
    /mnt/data/metadata/yfcc100m_short/yfcc100m_photo_autotags_1M_extended \
    -db_name "yfcc_1M" \
    -db_host "sky3.jf.intel.com" \
    -db_port 3306 \
    -db_user "root" \
    -db_pswd ""
