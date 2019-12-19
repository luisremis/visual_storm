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

class TestVideos(TestCommand.TestCommand):

    #Methos to insert one image
    def insertVideo(self, db, props=None):

        video_arr = []
        all_queries = []

        fd = open("test_videos/Megamind.avi", 'rb')
        video_arr.append(fd.read())
        fd.close()

        video_parms = {}

        # adds some prop
        if not props is None:
            props["test_case"] = "test_case_prop"
            video_parms["properties"] = props

        video_parms["codec"]     = "h264"
        video_parms["container"] = "mp4"

        query = {}
        query["AddVideo"] = video_parms

        all_queries.append(query)

        response, res_arr = db.query(all_queries, [video_arr])

        self.assertEqual(len(response), 1 + 1)
        self.assertEqual(response[0]["AddVideo"]["status"], 0)

    def addMetadataVideos(self):

        db = self.create_connection()

        for x in xrange(1,200):

            start = time.time()

            all_queries = []
            number_of_inserts = 500

            for i in range(0,number_of_inserts):

                props = {}
                props["name"] = "video_" + str(i)
                props["doctor"] = "Dr. Strange Love"

                video_parms = {}
                video_parms["properties"] = props
                video_parms["class"] = "VD:VID"

                query = {}
                query["AddEntity"] = video_parms

                all_queries.append(query)

            response, obj_array = db.query(all_queries)
            self.assertEqual(len(response), number_of_inserts + 1)
            for i in range(0, number_of_inserts):
                self.assertEqual(response[i]["AddEntity"]["status"], 0)

            end = time.time()

    def test_addVideo(self):

        db = self.create_connection()

        all_queries = []
        video_arr = []

        self.addMetadataVideos()

        number_of_inserts = 1

        for i in range(0,number_of_inserts):
            #Read Brain Image
            fd = open("test_videos/Megamind.avi", 'rb')
            video_arr.append(fd.read())
            fd.close()

            op_params_resize = {}
            op_params_resize["height"] = 512
            op_params_resize["width"]  = 512
            op_params_resize["type"] = "resize"

            props = {}
            props["name"] = "video_" + str(i)
            props["doctor"] = "Dr. Strange Love"

            video_parms = {}
            video_parms["properties"] = props
            video_parms["codec"] = "h264"

            query = {}
            query["AddVideo"] = video_parms

            all_queries.append(query)

        response, obj_array = db.query(all_queries, [video_arr])
        self.assertEqual(len(response), number_of_inserts + 1)
        for i in range(0, number_of_inserts):
            self.assertEqual(response[i]["AddVideo"]["status"], 0)

    def test_findVideo(self):

        db = self.create_connection()

        prefix_name = "video_1_"

        number_of_inserts = 1

        for i in range(0,number_of_inserts):
            props = {}
            props["name"] = prefix_name + str(i)
            self.insertVideo(db, props=props)

        all_queries = []

        for i in range(0,number_of_inserts):
            constraints = {}
            constraints["name"] = ["==", prefix_name + str(i)]

            video_parms = {}
            video_parms["constraints"] = constraints

            query = {}
            query["FindVideo"] = video_parms

            all_queries.append(query)

        start = time.time()
        response, vid_array = db.query(all_queries)
        end = time.time()
        print(end - start)

        self.assertEqual(len(response), number_of_inserts + 1)
        self.assertEqual(len(vid_array), number_of_inserts)
        for i in range(0, number_of_inserts):
            self.assertEqual(response[i]["FindVideo"]["status"], 0)

        print("cpuutil: " + str(psutil.cpu_percent()))

        # fd = open("findVideo_Megamind.mp4", 'wb')
        # fd.write(vid_array[0])
        # fd.close()

    def test_findVideoAndTranscode(self):

        db = self.create_connection()

        prefix_name = "video_trans_"

        number_of_inserts = 1

        for i in range(0,number_of_inserts):
            props = {}
            props["name"] = prefix_name + str(i)
            self.insertVideo(db, props=props)

        all_queries = []

        for i in range(0,number_of_inserts):
            constraints = {}
            constraints["name"] = ["==", prefix_name + str(i)]

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
        print(end - start)

        self.assertEqual(len(response), number_of_inserts + 1)
        self.assertEqual(len(vid_array), number_of_inserts)
        for i in range(0, number_of_inserts):
            self.assertEqual(response[i]["FindVideo"]["status"], 0)

        # fd = open("findVideoTrans_Megamind.avi", 'wb')
        # fd.write(vid_array[0])
        # fd.close()

    def test_findVideoAndResize(self):

        db = self.create_connection()

        prefix_name = "video_resize_"

        number_of_inserts = 1

        for i in range(0,number_of_inserts):
            props = {}
            props["name"] = prefix_name + str(i)
            self.insertVideo(db, props=props)

        all_queries = []

        for i in range(0,number_of_inserts):
            constraints = {}
            constraints["name"] = ["==", prefix_name + str(i)]

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
        print(end - start)

        self.assertEqual(len(response), number_of_inserts + 1)
        self.assertEqual(len(vid_array), number_of_inserts)
        for i in range(0, number_of_inserts):
            self.assertEqual(response[i]["FindVideo"]["status"], 0)

        print("cpuutil: " + str(psutil.cpu_percent()))

        # fd = open("findVideoResize_Megamind.mp4", 'wb')
        # fd.write(vid_array[0])
        # fd.close()

    def test_findVideoResizeAndTranscode(self):

        db = self.create_connection()

        prefix_name = "video_resize_trans_"

        number_of_inserts = 1

        for i in range(0,number_of_inserts):
            props = {}
            props["name"] = prefix_name + str(i)
            self.insertVideo(db, props=props)

        all_queries = []

        for i in range(0,number_of_inserts):
            constraints = {}
            constraints["name"] = ["==", prefix_name + str(i)]

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
        print(end - start)
        print("cpuutil: " + str(psutil.cpu_percent()))

        self.assertEqual(len(response), number_of_inserts + 1)
        self.assertEqual(len(vid_array), number_of_inserts)
        for i in range(0, number_of_inserts):
            self.assertEqual(response[i]["FindVideo"]["status"], 0)


        # fd = open("findVideoResizeTrans_Megamind.avi", 'wb')
        # fd.write(vid_array[0])
        # fd.close()
