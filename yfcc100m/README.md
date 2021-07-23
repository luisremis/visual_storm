YFCC100M Evaluation
===================

This folder contains all the necessary implementation to replicate studies presented on our
47th International Conference on Very Large Data Bases (VLDB 2021) paper.

Motivation
----------

Data scientists spend most of their time dealing with data preparation,
rather than doing what they know best:
build machine learning models and algorithms to solve previously unsolvable problems.
In this paper, we describe the Visual Data Management System (VDMS),
and demonstrate how it can be used to simplify the data preparation process
and consequently gain in efficiency simply because
we are using a system designed for the job.
To demonstrate this, we use one of the largest available
public datasets (YFCC100M),
with 100 million images and videos, plus additional data including
machine-generated tags, for a total of about ~12TB of data.
VDMS differs from existing data management systems
due to its focus on supporting machine learning and
data analytics pipelines that rely on images, videos, and feature vectors,
treating these as first class citizens.
We demonstrate how VDMS outperforms well-known and widely used
systems for data management by up to ~364x, with
an average improvement of about 85x for our use-cases, and particularly at scale,
for a **image search** engine implementation.
At the same time, VDMS simplifies the process of data preparation and data access,
and provides functionalities non-existent in alternative options.

Dataset
-------

The Yahoo! Flickr Creative Commons 100m ([YFCC100M](https://arxiv.org/pdf/1503.01817.pdf)) 
dataset is a large collection of 100 million public Flickr media objects 
created to provide free, shareable multimedia data for research.
This dataset contains approximately 99.2 million images and 0.8 million videos
with metadata characterized by 25 fields such as the unique identifier, userid,
date the media was taken/uploaded, location in longitude/latitude coordinates,
device type the media was captured, URL to download the media object,
and the Creative Commons license type information.
The YFCC100M dataset also contains **autotags**
provided as a set of comma-separated concepts such as people, scenery, objects,
and animals from 1,570 trained machine learning classifiers.
Together with each **autotags**, there is a probability associated with
each tag to indicate certainty of the classification.
This is, an image can have the **autotags** "people", "person", "party",
"outdoor", and each **autotag** assigned will be accompanied by a
probability of that **autotags** being present in that image/frame.
Given that there is no standard benchmark oriented towards visual data queries,
we have built a series of queries to filter this dataset that is modeled after
our internal use cases for many of the mentioned applications we have worked
with.

### Download Dataset

Instructions on how to download the dataset can be found 
[here](https://multimediacommons.wordpress.com/yfcc100m-core-dataset/).

For this experiment, we downloaded the dataset to a local storage. 
Datasets creators offer links to every image, that can be used to
download directly, as well as AWS S3 buckets.

We provide simple [tools](https://github.com/luisremis/visual_storm/tree/master/yfcc100m/tools) 
to download image once the original metadata has been downloaded from once
of the sources above.

Evaluation Implementation
-------------------------

We provide all the scripts and implementation needed for building 
all the baselines 
([mysql](https://github.com/luisremis/visual_storm/tree/master/yfcc100m/python/eval/mysql_eval),
 [postgresql](https://github.com/luisremis/visual_storm/tree/master/yfcc100m/python/eval/postgresql_eval)) 
and [VDMS](https://github.com/luisremis/visual_storm/tree/master/yfcc100m/python/vdms_eval) databases.

Instructions on how to install and deploy each database can be found 
on each project github pages.

The implementation and instructions to run evaluationcan be found 
[here](https://github.com/luisremis/visual_storm/tree/master/yfcc100m/python/eval).

Get in Touch!
-------------

For any questions, concerns, or comments for improvements, etc, please create an issue 
on the [issues page](https://github.com/luisremis/visual_storm/issues) for this project, 
or email the authors directly. 
