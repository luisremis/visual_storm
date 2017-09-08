#This script copies data from ucluster locally to create a sample of the dataset

mkdir ../data
rsync -r forest-app.jf.intel.com:/srv/data/yfcc100m/set_0/metadata/yfcc100m_short ../data/yfcc100m
rsync -r forest-app.jf.intel.com:/srv/data/yfcc100m/set_0/metadata/extras ../data/


# This is the entire dataset, will take a while
rsync -r forest-app.jf.intel.com:/srv/data/yfcc100m/metadata/original/* ../data/

bzip2 -dk ../data/yfcc100m_dataset.bz2
bzip2 -dk ../data/yfcc100m_autotags.bz2
