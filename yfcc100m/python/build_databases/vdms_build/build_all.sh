#!/bin/bash

# rm error_*.log screen_*.log

# python3 build_yfcc_db.py \
#           -data_file=/mnt/yfcc100m/metadata/processed/splitted/yfcc100m_dataset_000 \
#           -tag_file=/mnt/yfcc100m/metadata/processed/splitted/yfcc100m_dataset_autotags_000 \
#           -add_tags > screen_000.log 2> error_000.log

#sync
# (cd ../vdms/debug && bash check_graph.sh >> done.log && bsdtar cvfz /mnt/nvme1/vdms_archive_000.tar.gz db)
#(cd /mnt/nvme1/vdms/ && bsdtar cvfz /mnt/nvme1/vdms_archive_000.tar.gz db)

for i in $(seq -f "%03g" 51 100)
do
    echo "Building: "
    echo /mnt/yfcc100m/metadata/processed/splitted/yfcc100m_dataset_$i

    python3 build_yfcc_db.py \
        -data_file=/mnt/yfcc100m/metadata/processed/splitted/yfcc100m_dataset_$i \
        -tag_file=/mnt/yfcc100m/metadata/processed/splitted/yfcc100m_dataset_autotags_$i \
        > screen_$i.log 2> error_$i.log

    if [ "$i" -eq 10 ] || [ "$i" -eq 20 ] || [ "$i" -eq 50 ] || [ "$i" -eq 70 ] || [ "$i" -eq 90 ]
    then
        sync
        echo "checkpointing..."
        (cd /mnt/nvme1/vdms/ && \
         bsdtar cvfz /mnt/nvme1/vdms_archive_$i.tar.gz db)
    fi

    # (cd ../vdms/debug/ && bash check_graph.sh >> done.log && bsdtar cvfz /mnt/nvme1/vdms_archive_$i.tar.gz db)

 done
