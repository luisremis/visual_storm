Welcome to Visual Storm

Visual Storm is a collection of Datasets aiming to understand and test 
different visual worksets and use cases.

The datasets included initially are:

	Yahoo Flickr Creative Commons 100 Million (YFCC100m) dataset

	KITTI Vision Benchmark Suite


Basic info about organization:
-----------------------------

Each dataset will have its own directory tree, with the following folders

/src - source code files (*.cc, *.cpp)

/include - header files (*.h, *.hpp)

/test (optional) - Folder for tests

/tools (optional) - additional tools for handling data sets, downloaders, etc
        /data folder will be created when using downloaders, 
        retieving data from uCluster

/util (optional) - other file readers (such us .csv, .txt, etc) as helpers, 
        as well as any other useful helpers.


Let's calm down.