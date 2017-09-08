rm -rf kittigraph
cd ..
make
cd src/
#./kitti 1 1 ../data/kitti/csvs/0001.txt
./kitti 0 /home/kspirovs/datasets/KITTI/kitti_videos.csv
#./kitti 1 /home/kspirovs/datasets/KITTI 2011_09_26 0048
