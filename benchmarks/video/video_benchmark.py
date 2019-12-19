#
# The MIT License
#
# @copyright Copyright (c) 2017 Intel Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import TestCommand
import time
import psutil
import numpy as np

num_queries = 50

def reject_outliers(data, m=1):
    return data[abs(data - np.mean(data)) < m * np.std(data)]

class TestVideosRead(TestCommand.TestCommand):

    def test_findVideo(self):

        db = self.create_connection()

        prefix_name = "video_1_"

        total_sum    = []
        commands_sum = []
        metadata_sum = []

        for i in range(0,num_queries):

            all_queries = []

            constraints = {}
            constraints["name"] = ["==", prefix_name + "0"] # str(i)]

            video_parms = {}
            video_parms["constraints"] = constraints

            query = {}
            query["FindVideo"] = video_parms

            all_queries.append(query)

            start = time.time()
            response, vid_array = db.query(all_queries)
            end = time.time()

            commands_time = response[1]["Timers"]["commands"]
            metadata_time = response[1]["Timers"]["metadata_tx"]
            total_time    = response[1]["Timers"]["total"]

            commands_sum.append(commands_time)
            metadata_sum.append(metadata_time)
            total_sum   .append(total_time)
            # print(db.get_last_response_str())
            # print("cpuutil: " + str(psutil.cpu_percent()))

            self.assertEqual(len(response), 1 + 1)
            self.assertEqual(len(vid_array), 1)
            for i in range(0, 1):
                self.assertEqual(response[i]["FindVideo"]["status"], 0)



        total_sum    = reject_outliers( np.array(total_sum) )
        metadata_sum = reject_outliers( np.array(metadata_sum) )
        commands_sum = reject_outliers( np.array(commands_sum) )
        total_avg    = np.mean(total_sum)
        total_std    = np.std (total_sum)
        metadata_avg = np.mean(metadata_sum)
        metadata_std = np.std (metadata_sum)
        commands_avg = np.mean(commands_sum)
        commands_std = np.std (commands_sum)

        print("test_findVideo")
        print("%s,%s,%s,%s,%s,%s" % (total_avg, metadata_avg, commands_avg,
                                     total_std, metadata_std, commands_std))

        # fd = open("findVideo_Megamind.mp4", 'wb')
        # fd.write(vid_array[0])
        # fd.close()

    def test_findVideoAndTranscode(self):

        db = self.create_connection()

        prefix_name = "video_trans_"

        total_sum    = []
        commands_sum = []
        metadata_sum = []

        for i in range(0,num_queries):

            all_queries = []

            constraints = {}
            constraints["name"] = ["==", prefix_name + "0"] # str(i)]

            video_parms = {}
            video_parms["constraints"] = constraints
            video_parms["codec"]     = "xvid"
            video_parms["container"] = "avi"

            query = {}
            query["FindVideo"] = video_parms

            all_queries.append(query)

            start = time.time()
            response, vid_array = db.query(all_queries)
            end = time.time()

            commands_time = response[1]["Timers"]["commands"]
            metadata_time = response[1]["Timers"]["metadata_tx"]
            total_time    = response[1]["Timers"]["total"]

            commands_sum.append(commands_time)
            metadata_sum.append(metadata_time)
            total_sum   .append(total_time)
            # print(db.get_last_response_str())
            # print("cpuutil: " + str(psutil.cpu_percent()))

            self.assertEqual(len(response), 1 + 1)
            self.assertEqual(len(vid_array), 1)
            for i in range(0, 1):
                self.assertEqual(response[i]["FindVideo"]["status"], 0)


        total_sum    = reject_outliers( np.array(total_sum) )
        metadata_sum = reject_outliers( np.array(metadata_sum) )
        commands_sum = reject_outliers( np.array(commands_sum) )
        total_avg    = np.mean(total_sum)
        total_std    = np.std (total_sum)
        metadata_avg = np.mean(metadata_sum)
        metadata_std = np.std (metadata_sum)
        commands_avg = np.mean(commands_sum)
        commands_std = np.std (commands_sum)

        print("test_findVideoAndTranscode")
        print("%s,%s,%s,%s,%s,%s" % (total_avg, metadata_avg, commands_avg,
                                     total_std, metadata_std, commands_std))

        # fd = open("findVideoTrans_Megamind.avi", 'wb')
        # fd.write(vid_array[0])
        # fd.close()

    def test_findVideoAndResize(self):

        db = self.create_connection()

        prefix_name = "video_resize_"

        total_sum = []
        commands_sum = []
        metadata_sum = []

        for i in range(0,num_queries):

            all_queries = []

            constraints = {}
            constraints["name"] = ["==", prefix_name + "0"] # str(i)]

            video_parms = {}
            video_parms["constraints"] = constraints
            video_parms["operations"] = [
                {
                    "type": "resize",
                    "width": 200, "height": 200,
                }
            ]

            query = {}
            query["FindVideo"] = video_parms

            all_queries.append(query)

            start = time.time()
            response, vid_array = db.query(all_queries)
            end = time.time()

            commands_time = response[1]["Timers"]["commands"]
            metadata_time = response[1]["Timers"]["metadata_tx"]
            total_time    = response[1]["Timers"]["total"]

            commands_sum.append(commands_time)
            metadata_sum.append(metadata_time)
            total_sum   .append(total_time)
            # print(db.get_last_response_str())
            # print("cpuutil: " + str(psutil.cpu_percent()))

            self.assertEqual(len(response), 1 + 1)
            self.assertEqual(len(vid_array), 1)
            for i in range(0, 1):
                self.assertEqual(response[i]["FindVideo"]["status"], 0)


        total_sum    = reject_outliers( np.array(total_sum) )
        metadata_sum = reject_outliers( np.array(metadata_sum) )
        commands_sum = reject_outliers( np.array(commands_sum) )
        total_avg    = np.mean(total_sum)
        total_std    = np.std (total_sum)
        metadata_avg = np.mean(metadata_sum)
        metadata_std = np.std (metadata_sum)
        commands_avg = np.mean(commands_sum)
        commands_std = np.std (commands_sum)

        print("test_findVideoAndResize")
        print("%s,%s,%s,%s,%s,%s" % (total_avg, metadata_avg, commands_avg,
                                     total_std, metadata_std, commands_std))

        # fd = open("findVideoResize_Megamind.mp4", 'wb')
        # fd.write(vid_array[0])
        # fd.close()

    def test_findVideoResizeAndTranscode(self):

        db = self.create_connection()

        prefix_name = "video_resize_trans_"

        total_sum = []
        commands_sum = []
        metadata_sum = []

        for i in range(0,num_queries):

            all_queries = []

            constraints = {}
            constraints["name"] = ["==", prefix_name + "0"] # str(i)]

            video_parms = {}
            video_parms["constraints"] = constraints
            video_parms["codec"]     = "xvid"
            video_parms["container"] = "avi"
            video_parms["operations"] = [
                {
                    "type": "resize",
                    "width": 200, "height": 200,
                }
            ]

            query = {}
            query["FindVideo"] = video_parms

            all_queries.append(query)

            start = time.time()
            response, vid_array = db.query(all_queries)
            end = time.time()

            commands_time = response[1]["Timers"]["commands"]
            metadata_time = response[1]["Timers"]["metadata_tx"]
            total_time    = response[1]["Timers"]["total"]

            commands_sum.append(commands_time)
            metadata_sum.append(metadata_time)
            total_sum   .append(total_time)
            # print(db.get_last_response_str())
            # print("cpuutil: " + str(psutil.cpu_percent()))

            self.assertEqual(len(response), 1 + 1)
            self.assertEqual(len(vid_array), 1)
            for i in range(0, 1):
                self.assertEqual(response[i]["FindVideo"]["status"], 0)


        total_sum    = reject_outliers( np.array(total_sum) )
        metadata_sum = reject_outliers( np.array(metadata_sum) )
        commands_sum = reject_outliers( np.array(commands_sum) )
        total_avg    = np.mean(total_sum)
        total_std    = np.std (total_sum)
        metadata_avg = np.mean(metadata_sum)
        metadata_std = np.std (metadata_sum)
        commands_avg = np.mean(commands_sum)
        commands_std = np.std (commands_sum)

        print("test_findVideoResizeAndTranscode")
        print("%s,%s,%s,%s,%s,%s" % (total_avg, metadata_avg, commands_avg,
                                     total_std, metadata_std, commands_std))

        # fd = open("findVideoResizeTrans_Megamind.avi", 'wb')
        # fd.write(vid_array[0])
        # fd.close()
