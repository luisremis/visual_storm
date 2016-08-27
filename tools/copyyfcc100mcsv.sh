#This script copies data from ucluster locally to create a sample of the dataset

mkdir ../data
scp -r 10.54.81.111:/srv/datasets/YFCC100M/yfcc100m_short ../data/yfcc100m
scp -r 10.54.81.111:/srv/datasets/YFCC100M/extras/dictionary-seed ../data/
scp -r 10.54.81.111:/srv/datasets/YFCC100M/extras/geolite2 ../data/
