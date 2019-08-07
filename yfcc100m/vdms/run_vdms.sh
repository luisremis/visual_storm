rm -rf db
mkdir -p db/images
# ln -s /data/yfcc100m/set_0/data_0/images db/images/jpg

/home/luisremi/vcs/pmgd/tools/mkgraph db/graph -c 32 \
	node VD:IMG imgPath string \
	node VD:IMG ID integer \
	node VD:IMG Latitude float \
	node VD:IMG Longitude float \
	node autotags name string

vdms 2> log.log
