#!/bin/bash
set -e

# Build dbs on 127.0.0.1 or sky4.local

# for size in 100k
#for size in 1M 5M 10M 50M 100M
for size in 100M
#for size in 1M 5M 10M
do
case "$size" in
  50M)
    host=sky4.local
    ;;
  *)
    host=127.0.0.1
    ;;
esac
echo "HOST: ${host}"
echo "Processing yfcc_${size} Database"
sudo -u root psql -h $host -c "drop database if exists \"yfcc_${size}\";"
sudo -u root psql -h $host -c "create database \"yfcc_${size}\" OWNER root;"
python3 build_yfcc_db_postgres.py \
    -data_file \
    /mnt/yfcc100m/metadata/processed/yfcc100m_photo_dataset_${size} \
    -tag_file \
    /mnt/yfcc100m/metadata/processed/yfcc100m_photo_autotags_${size}_extended \
    -tag_list /mnt/yfcc100m/metadata/processed/autotag_list.txt \
    -db_name "${size}" \
    -db_host "${host}" \
    -db_port 5432 \
    -db_user "root" \
    -db_pswd "password"
done
