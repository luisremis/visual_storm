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
BASEURL = 'https://multimedia-commons.s3-us-west-2.amazonaws.com/data/videos/mp4/'
SEARCH1 = "people"

def main():
    print("Starting dataset processing")
    npgpdf, mdpdf = getMetaData()

    ''' Get a subset that has appropriate license type '''
    goodlpdf = mdpdf[mdpdf['License name'] == LICENSETYPE]

    ''' Get a subset containing user tag SEARCH1 '''
    searchpdf = goodlpdf[goodlpdf['Machine tags'].str.contains(SEARCH1)==True]

    ''' Fetch those videos '''
    getVideos(searchpdf)

    ''' For the specific videos NPG requested '''
    # vidpdf = videoSlice(mdpdf,npgpdf)
    # getVideos(vidpdf)

    print("Finished downloading")
    sys.exit(0)

def getMetaData():
    ''' PDF of videos to download '''
    ''' NOTE: PDF = Pandas Dataframe '''

    npgfile = getPath("npg-videos.tsv")
    npgheader = ["Purpose","Description","URL","Finder","ID"]
    npgpdf = pd.read_csv(npgfile,"\t", header = 1, names = npgheader)

    ''' PDF for yf100m metadata '''
    mdfile = getPath("yfcc100m_videos_metadata.tsv")
    mdheaderfile = getPath("yfcc100m_videos_metadata_headers.csv")
    mdheader = [x.strip() for x in open(mdheaderfile)]
    mdpdf = pd.read_csv(mdfile, "\t", header = None)
    mdpdf.columns = mdheader
    return npgpdf, mdpdf

def videoSlice(pdf,vididpdf):
    ''' Shrink the metadata to just select data '''
    slicelst = ["Identifier", "Title", "Description_x","Description_y", "Download URL","License name","User tags","Machine tags","Extension","Hash"]
    vidpdf = pd.merge(pdf, vididpdf,left_on='Identifier',right_on='ID',how='inner')
    vidpdf = vidpdf[slicelst]
    return vidpdf

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
#    print("Downloading %s" % idf)
    print(rowd)
    hashd = rowd['Hash']
    sub1 = hashd[0:3]
    sub2 = hashd[3:6]
    hashf = hashd + ".mp4"
    fullurl = os.path.join(baseurl,*[sub1,sub2,hashf])
    print(fullurl)
    return
    try:
        urllib.request.urlretrieve(fullurl,idf)
    except Exception as e:
        print("Failed to download %s; Error: %s" % (fullurl,str(e)))


if __name__ == '__main__': main()

