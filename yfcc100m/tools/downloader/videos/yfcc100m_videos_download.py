#!/usr/bin/env python3


# Some of these may not be necessary
import pandas as pd
import numpy as np
import copy
import urllib.request
import os
import sys
import csv
import logging

FROOT = "input_files"
LICENSETYPE = "Attribution License"

'''
License Options:
 * Attribution License
 * Attribution-ShareAlike License
 * Attribution-NoDerivs License
 * Attribution-NonCommercial License
 * Attribution-NonCommercial-ShareAlike License
 * Attribution-NonCommercial-NoDerivs License
'''

BASEURL = 'https://multimedia-commons.s3-us-west-2.amazonaws.com/data/videos/mp4/'
SEARCH1 = "backpack"

def main():
    print("Starting dataset processing")
    mdpdf = getMetaData()

    ''' Get a subset that has appropriate license type '''
    goodlpdf = mdpdf[mdpdf['License name'] == LICENSETYPE]

    ''' Get a subset containing user tag SEARCH1 '''
    # searchpdf = goodlpdf[goodlpdf['User tags'].str.contains(SEARCH1)==True]
    searchpdf = goodlpdf

    ''' Fetch those videos '''
    getVideos(searchpdf)

    print("Finished downloading")
    sys.exit(0)

def getMetaData():

    ''' PDF for yf100m metadata '''
    mdfile = getPath("yfcc100m_videos_metadata.tsv")
    mdheaderfile = getPath("yfcc100m_videos_metadata_headers.csv")
    mdheader = [x.strip() for x in open(mdheaderfile)]
    mdpdf = pd.read_csv(mdfile, "\t", header = None)
    mdpdf.columns = mdheader
    return mdpdf

def getPath(fname):
    return os.path.join(FROOT,fname)

def getVideos(pdf):
    baseurl = 'https://multimedia-commons.s3-us-west-2.amazonaws.com/data/videos/mp4/'
#     urlfname = getPath("s3vidurl.txt")    # If you'd rather read the URL from a file
#     with open(urlfname) as f:
#         baseurl = f.readlines()
#     baseurl = baseurl[0].strip()
    pdf.apply(lambda x: getVideo(x,baseurl), axis = 1)

def getVideo(rowd,baseurl):

    ''' Destination file '''
    idf = os.path.join(FROOT,*['vidcache',str(rowd['Identifier']) + '.mp4'])
    if os.path.isfile(idf):
        print("File %s already exists; Skip it to speed things up" % idf)
        return
    ''' License Check '''
    if rowd['License name'] != LICENSETYPE:
        print("Incorrect License: %s; Skipping %s" % (rowd['License name'],idf))
        return

    ''' All good -- get the video '''
    # print("Downloading %s" % idf)
    # print(rowd)
    hashd = rowd['Hash']
    sub1 = hashd[0:3]
    sub2 = hashd[3:6]
    hashf = hashd + ".mp4"
    fullurl = os.path.join(baseurl,*[sub1,sub2,hashf])
    print(fullurl)
    # return
    try:
        urllib.request.urlretrieve(fullurl,idf)
    except Exception as e:
        print("Failed to download %s; Error: %s" % (fullurl,str(e)))


if __name__ == '__main__': main()

