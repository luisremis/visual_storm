rm -rf db
mkdir -p db/images
# ln -s /data/yfcc100m/set_0/data_0/images db/images/jpg

/home/luisremi/vcs/pmgd/tools/mkgraph db/graph \
	node VD:IMG imgPath string \
	node VD:IMG ID integer \
	node autotags name string

vdms 2> log.log
