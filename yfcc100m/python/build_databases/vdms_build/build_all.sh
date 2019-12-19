#!/bin/bash

rm -rf logs
mkdir logs

input_root="/data/datasets/yfcc100m/metadata/processed/splitted/"
output_root="/data/datasets/yfcc100m/golden_building/"

python3 build_yfcc_db.py \
          -data_file=${input_root}/yfcc100m_dataset_000 \
          -tag_file=${input_root}/yfcc100m_dataset_autotags_000 \
          -add_tags > logs/screen_000.log 2> logs/error_000.log

sync
(cd ${output_root}/vdms/ && \
 bash check_graph.sh && \
 bsdtar cvfz ${output_root}/vdms_archive_000.tar.gz db )

for i in $(seq -f "%03g" 0 4)
do
    echo "Building: "
    echo yfcc100m_dataset_$i

    python3 build_yfcc_db.py \
        -data_file=${input_root}/yfcc100m_dataset_$i \
        -tag_file=${input_root}/yfcc100m_dataset_autotags_$i \
        > logs/screen_$i.log 2> logs/error_$i.log

    if [ "$i" -eq 0 ] || [ "$i" -eq 4 ] || [ "$i" -eq 9 ] || [ "$i" -eq 19 ] || [ "$i" -eq 49 ] || [ "$i" -eq 69 ] || [ "$i" -eq 89 ]
    then
        sync
        echo "checkpointing..."
        (cd ${output_root}/vdms/ && \
         bash check_graph.sh && \
         bsdtar cvfz ${output_root}/vdms_archive_$i.tar.gz db)
    fi

 done
