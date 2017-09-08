/*
 * This test checks Jarvis iterator filters
 */

#define __STDC_FORMAT_MACROS
#include <inttypes.h>
#include "jarvis.h"
#include "util.h"
#include "tracklets.h"
#include "oxts_data.h"
#include "frame.h"
#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stdlib.h>     /* system, NULL, EXIT_FAILURE */

using namespace Jarvis;

int loadAllVideosMetadata(std::string file, Graph& db) {

    std::cout << "Loading videos' metadata from file: \n" << file << "\n";
    std::string line;
    std::string token;

    int videosCounter = 0;
    int videoRepCounter = 0;

    std::ifstream filein(file);
    std::vector<std::string> tokens;

    Transaction tx(db, Transaction::ReadWrite);
    db.create_index(Graph::NodeIndex, "video", "id", PropertyType::Integer);
    db.create_index(Graph::NodeIndex, "video", "title", PropertyType::String);
    tx.commit();

    while (std::getline(filein, line)) {

        std::istringstream iss(line);

        tokens.clear();
        while (std::getline(iss, token, ' ')) {
            tokens.push_back(token);
        }

        Transaction tx1(db, Transaction::ReadWrite);

        PropertyPredicate pps1("id", PropertyPredicate::Eq, atoi(tokens[0].c_str()));
        NodeIterator vi = db.get_nodes("video", pps1);

        if (!vi) {
            // adding a new video metadata
            videosCounter++;

            Node &nvideo = db.add_node("video");
            nvideo.set_property("id", atoi(tokens[0].c_str()));
            nvideo.set_property("title", tokens[1].c_str());
            nvideo.set_property("date", tokens[2].c_str());
            nvideo.set_property("sequence", tokens[3].c_str());
            nvideo.set_property("size", atof(tokens[4].c_str()));
            nvideo.set_property("numFrames", atoi(tokens[5].c_str()));
            nvideo.set_property("duration", tokens[6].c_str());
            nvideo.set_property("resolution", tokens[7].c_str());
        } else {
            //the video already exists
            videoRepCounter++;
        }

        tx1.commit();
    }

    std::cout << std::endl;

    std::cout << "Videos added: " << videosCounter << std::endl;
    std::cout << "Videos repeated: " << videoRepCounter << std::endl;

    int numVideos = 0;

    Transaction tx2(db, Transaction::ReadWrite);
    for (NodeIterator i = db.get_nodes("video"); i; i.next()) // should be only 0 or 1 though
    {
        numVideos++;
    }
    tx2.commit();

    std::cout << "Total videos in db: " << numVideos << std::endl;

    return 0;
}

int insertFrame(Frame frame, Graph & db) {

    Transaction tx0(db, Transaction::ReadWrite);
    db.create_index(Graph::NodeIndex, "frame", "id", PropertyType::String);
    tx0.commit();

    Transaction tx(db, Transaction::ReadWrite);

    PropertyPredicate pps1("id", PropertyPredicate::Eq, frame.id.c_str());
    NodeIterator fi = db.get_nodes("frame", pps1);

    if (!fi) {
        // adding new frame
        Node &nframe = db.add_node("frame");
        nframe.set_property("id", frame.id.c_str());
        nframe.set_property("sequenceNumber", frame.sequence.c_str());
        nframe.set_property("timestamp", frame.timestamp.c_str());
        nframe.set_property("latitude", frame.oxts->geoCoordinates.lat);
        nframe.set_property("longitude", frame.oxts->geoCoordinates.lon);
        nframe.set_property("altitude", frame.oxts->geoCoordinates.alt);
        nframe.set_property("rotationPitch", frame.oxts->rotation.pitch);
        nframe.set_property("rotationRoll", frame.oxts->rotation.roll);
        nframe.set_property("rotationYaw", frame.oxts->rotation.yaw);
        nframe.set_property("accelerationAf", frame.oxts->acceleration.af);
        nframe.set_property("accelerationAl", frame.oxts->acceleration.al);
        nframe.set_property("accelerationAu", frame.oxts->acceleration.au);
        nframe.set_property("accelerationAx", frame.oxts->acceleration.ax);
        nframe.set_property("accelerationAy", frame.oxts->acceleration.ay);
        nframe.set_property("accelerationAz", frame.oxts->acceleration.az);
        nframe.set_property("anglRateAwl", frame.oxts->angularRateAround.wf);
        nframe.set_property("anglRateAwl", frame.oxts->angularRateAround.wl);
        nframe.set_property("anglRateAwu", frame.oxts->angularRateAround.wu);
        nframe.set_property("anglRateAwx", frame.oxts->angularRateAround.wx);
        nframe.set_property("anglRateAwy", frame.oxts->angularRateAround.wy);
        nframe.set_property("anglRateAwz", frame.oxts->angularRateAround.wz);
        nframe.set_property("gpsModeOrimode", frame.oxts->gpsMode.orimode);
        nframe.set_property("gpsModePosmode", frame.oxts->gpsMode.posmode);
        nframe.set_property("gpsModeVelmode", frame.oxts->gpsMode.velmode);
        nframe.set_property("navigationStatus", frame.oxts->navigationStatus);
        nframe.set_property("numSatelites", frame.oxts->numSatelites);
        nframe.set_property("velocityVe", frame.oxts->velocity.ve);
        nframe.set_property("velocityVf", frame.oxts->velocity.vf);
        nframe.set_property("velocityVl", frame.oxts->velocity.vl);
        nframe.set_property("velocityVn", frame.oxts->velocity.vn);
        nframe.set_property("velocityVu", frame.oxts->velocity.vu);
        nframe.set_property("velAccPosAcc", frame.oxts->velocityAccuracy.pos_accuracy);
        nframe.set_property("velAccVelAcc", frame.oxts->velocityAccuracy.vel_accuracy);

    } else {
        //the frame already exists
        //        std::cout << "The frame with this id already exists!\n";

    }

    tx.commit();

    return 0;
}

int insertObject(int count, tTracklet* t, std::string videoTitle, Graph & db) {

    int newObjectInserted = 0;

    Transaction tx0(db, Transaction::ReadWrite);
    db.create_index(Graph::NodeIndex, "object", "id", PropertyType::String);
    tx0.commit();

    int firstFrame = t->first_frame;
    int lastFrame = t->lastFrame();

    std::string objId = videoTitle + "_obj_" + std::to_string(count);

    Transaction tx(db, Transaction::ReadWrite);
    PropertyPredicate pps("id", PropertyPredicate::Eq, objId.c_str());
    NodeIterator oi = db.get_nodes("object", pps);

    if (!oi) {
        // adding new object
        newObjectInserted++;
        Node &nobject = db.add_node("object");
        nobject.set_property("id", objId.c_str());
        nobject.set_property("type", t->objectType.c_str()); // type of the obj for e.g. Van, Car, etc.
        nobject.set_property("height", t->h); // height of the bounding box around the object
        nobject.set_property("width", t->w); // width of the bounding box around the object
        nobject.set_property("length", t->l); // length of the bounding box around the object
        nobject.set_property("finished", t->finished); //info whether this object is fully labeled
        nobject.set_property("first_frame", t->first_frame);
        nobject.set_property("last_frame", t->lastFrame());

        for (int i = firstFrame; i <= lastFrame; i++) {

            std::string fseq = std::to_string(i);
            fseq.insert(0, 10 - (std::to_string(i).length()), '0');

            std::string frameId = videoTitle + "_" + fseq;

            PropertyPredicate pps1("id", PropertyPredicate::Eq, frameId.c_str());
            NodeIterator fi = db.get_nodes("frame", pps1);

            if (fi) {
                tPose objPose = t->poses[i];

                Edge &e = db.add_edge(*fi, nobject, "contains");
                e.set_property("amt_border_kf", objPose.amt_border_kf); //mechanical Turk border keyframe
                e.set_property("amt_border_l", objPose.amt_border_l); //mechanical Turk left boundary label (relative)
                e.set_property("amt_border_r", objPose.amt_border_r); //mechanical Turk right boundary label (relative)
                e.set_property("amt_occlusion", objPose.amt_occlusion); //mechanical Turk occlusion label
                e.set_property("amt_occlusion_kf", objPose.amt_occlusion_kf); //mechanical Turk occlusion keyframe
                e.set_property("occlusion", objPose.occlusion); //occlusion state
                e.set_property("occlusion_kf", objPose.occlusion_kf); //occlusion keyframe
                e.set_property("rx", objPose.rx); //rotation wrt. Velodyne coordinates
                e.set_property("ry", objPose.ry); //rotation wrt. Velodyne coordinates
                e.set_property("rz", objPose.rz); //rotation wrt. Velodyne coordinates
                e.set_property("rz", objPose.rz); //rotation wrt. Velodyne coordinates
                e.set_property("state", objPose.state); //pose state
                e.set_property("truncation", objPose.truncation); //truncation state
                e.set_property("tx", objPose.tx); //translation wrt. Velodyne coordinates
                e.set_property("ty", objPose.ty); //translation wrt. Velodyne coordinates
                e.set_property("tz", objPose.tz); //translation wrt. Velodyne coordinates

            } else {
                std::cout << "Error! Frame with id " << frameId << " does not exists!\n";
                return 1;
            }

        }
    } else {
        //the object already exists
        std::cout << "Error! Object with id " << objId << "already exists!\n";
        return 1;
    }
    tx.commit();


    return newObjectInserted;

}

int loadVideo(std::string root_dir_path, std::string date, std::string drive_seq, Graph & db) {

    std::string videoTitle = date + "_drive_" + drive_seq;
    std::string path = root_dir_path + "/" + date + "/" + videoTitle + "_sync";
    std::string trackletFilePath = path + "/tracklet_labels.xml";
    std::string oxtsFileName = path + "/oxts/data/oxts.txt";
    std::string oxtsTimestampsFileName = path + "/oxts/timestamps.txt";
    int frameCounter = 0;

    //load all the frames of the video
    try {

        //load the frames' timestamps

        std::string line;
        std::vector<std::string> timestamps;
        std::ifstream fTimestamps(oxtsTimestampsFileName);


        while (std::getline(fTimestamps, line)) {
            timestamps.push_back(line);
        }

        //load the frames' oxts data

        int i = 0;
        std::ifstream oxtsFile(oxtsFileName);

        while (std::getline(oxtsFile, line)) {

            std::string fseq = std::to_string(i);
            fseq.insert(0, 10 - (std::to_string(i).length()), '0');

            std::string frameId = videoTitle + "_" + fseq;

            Frame f(frameId, fseq, timestamps[i], line);

            //insert frame into db
            insertFrame(f, db);
            frameCounter++;

            //connect frame with video
            Transaction tx(db, Transaction::ReadWrite);

            PropertyPredicate pps1("id", PropertyPredicate::Eq, f.id);
            NodeIterator fi = db.get_nodes("frame", pps1);

            PropertyPredicate pps2("title", PropertyPredicate::Eq, videoTitle);
            NodeIterator vi = db.get_nodes("video", pps2);

            if (vi) {
                if (fi) {

                    db.add_edge(*vi, *fi, "has");

                } else {
                    std::cout << "Error: The node with id " << f.id << " is not found!\n";
                    return 1;
                }

            } else {
                std::cout << "Error: The video with title " << videoTitle << " is not found!\n";
                return 1;
            }

            tx.commit();

            i++;

        }

        //loading objects on the frames

        Tracklets *tracklets = new Tracklets();
        tracklets->loadFromFile(trackletFilePath);
        int numObjects = tracklets->numberOfTracklets();
        int objCounter = 0;

        for (int i = 0; i < numObjects; i++) {

            tTracklet* t = tracklets->getTracklet(i);

            objCounter += insertObject(i, t, videoTitle, db);

        }

        std::cout << "Objects added: " << objCounter << std::endl;


    } catch (Exception e) {
        print_exception(e);
        return 1;
    }

    //    delete tracklets;

    return 0;

}

void dbState(Graph & db) {

    int numVideos = 0;
    int numFrames = 0;
    int numObjects = 0;

    Transaction tx2(db, Transaction::ReadWrite);
    for (NodeIterator i = db.get_nodes("video"); i; i.next()) // should be only 0 or 1 though
    {
        numVideos++;
    }

    for (NodeIterator i = db.get_nodes("frame"); i; i.next()) // should be only 0 or 1 though
    {
        numFrames++;
    }

    for (NodeIterator i = db.get_nodes("object"); i; i.next()) // should be only 0 or 1 though
    {
        numObjects++;
    }
    tx2.commit();

    std::cout << "\nTotal videos in db: " << numVideos << std::endl;
    std::cout << "Total frames in db: " << numFrames << std::endl;
    std::cout << "Total objects in db: " << numObjects << std::endl;


}

