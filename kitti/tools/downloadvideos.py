import os
import sys
import urllib

kitti_url = "http://kitti.is.tue.mpg.de/kitti/raw_data/"


#kitti.is.tue.mpg.de/kitti/raw_data/2011_09_26_drive_0001/2011_09_26_drive_0001_sync.zip
#kitti.is.tue.mpg.de/kitti/raw_data/2011_09_26_drive_0001/2011_09_26_drive_0001_tracklets.zip

dates = []
drives = []


if(len(sys.argv) == 3):
    download_folder = sys.argv[2] # e.g. /home/kspirovs/datasets/KITTI/videos

    titles_fname = sys.argv[1] # e.g. /home/kspirovs/datasets/KITTI/tools/kitti_titles.txt

    f_titles = open(titles_fname, 'r')

    for title in f_titles:
        print title
        title = title.rstrip()
        date = title[0:10]
        temp = title.split('_')
        drive = temp[len(temp)-1]
#       file_name = '{0}{1}_drive_{2}/{3}_drive_{4}_tracklets.zip'.format(kitti_url, date, drive, date, drive)
        file_name = '{0}{1}_drive_{2}/{3}_drive_{4}_sync.zip'.format(kitti_url, date, drive, date, drive)
        print "Downloading {0} ...".format(file_name)
        
#       name = "/home/kspirovs/local-dev/visual_storm/data/videos/{0}_drive_{1}_tracklets.zip".format(date, drive)
#       name = "{0}/{1}_drive_{2}_tracklets.zip".format(download_folder, date, drive)
        name = "{0}/{1}_drive_{2}_sync.zip".format(download_folder, date, drive)
        urllib.URLopener().retrieve(file_name, name)
else:
    print ("Wrong number of arguments!");