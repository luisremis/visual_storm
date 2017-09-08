/*
 * This test checks Jarvis iterator filters
 */

#define __STDC_FORMAT_MACROS
#include <inttypes.h>
#include "jarvis.h"
#include "util.h"
#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stdlib.h>     /* system, NULL, EXIT_FAILURE */

using namespace Jarvis;

bool setSensorDataEdgeProperies(Edge &e, std::vector<std::string> tokens) {
    e.set_property("type", tokens[2].c_str());
    e.set_property("truncated", atof(tokens[3].c_str()));
    e.set_property("occluded", atof(tokens[4].c_str()));
    e.set_property("yawangle", atof(tokens[5].c_str()));
    e.set_property("x1", atof(tokens[6].c_str()));
    e.set_property("y1", atof(tokens[7].c_str()));
    e.set_property("x2", atof(tokens[8].c_str()));
    e.set_property("y2", atof(tokens[9].c_str()));
    e.set_property("height", atof(tokens[10].c_str()));
    e.set_property("width", atof(tokens[11].c_str()));
    e.set_property("length", atof(tokens[12].c_str()));
    e.set_property("X", atof(tokens[13].c_str()));
    e.set_property("Y", atof(tokens[14].c_str()));
    e.set_property("Z", atof(tokens[15].c_str()));
    e.set_property("rotation_y", atof(tokens[16].c_str()));
    if (tokens.size() == 18)
        e.set_property("score", atof(tokens[17].c_str()));

    return true;
}

int uploadVideosFromCSV(std::string file, Graph& db) {

    std::string line;
    std::string token;

    std::ifstream filein(file);
    std::vector<std::string> tokens;
    size_t counter = 0;
    size_t counterRep = 0;
    int frameCounter = 0;
    int objectCounter = 0;

    Transaction txi(db, Transaction::ReadWrite);
    db.create_index(Graph::NodeIndex, "label", "name", PropertyType::String);
    db.create_index(Graph::NodeIndex, "frame", "id", PropertyType::Integer);
    db.create_index(Graph::NodeIndex, "object", "id", PropertyType::Integer);
    db.create_index(Graph::NodeIndex, "object", "type", PropertyType::String);
    txi.commit();

    Transaction tx1(db, Transaction::ReadWrite);
    Node &nvideo = db.add_node("video");
    nvideo.set_property("title", file);
    tx1.commit();

    while (std::getline(filein, line)) { // '\n' is the default delimiter

        std::istringstream iss(line);
        counter++;
        if (counter % 100 == 0) {
            std::cout << "\r" << counter;
            std::cout << std::flush;
            /* code */
        }
        tokens.clear();
        while (std::getline(iss, token, ' ')) {
            tokens.push_back(token);

        }

        Transaction tx(db, Transaction::ReadWrite);

        PropertyPredicate pps1("id", PropertyPredicate::Eq,
                atoi(tokens[0].c_str()));
        NodeIterator fi = db.get_nodes("frame", pps1);

        if (!fi) {
            //a new frame
            frameCounter++;

            Node &nframe = db.add_node("frame");
            nframe.set_property("id", atoi(tokens[0].c_str()));

            db.add_edge(nvideo, nframe, "has");

            PropertyPredicate pps2("id", PropertyPredicate::Eq,
                    atoi(tokens[1].c_str()));
            NodeIterator oi = db.get_nodes("object", pps2);
            if (!oi) {
                //new object found
                objectCounter++;

                Node &nobject = db.add_node("object");
                nobject.set_property("id", atoi(tokens[1].c_str()));
                nobject.set_property("type", tokens[2].c_str());

                Edge &e = db.add_edge(nframe, nobject, "contains");
                setSensorDataEdgeProperies(e, tokens);

            } else {
                //an existing object that appears on a new frame
                Edge &e = db.add_edge(nframe, *oi, "contains");
                setSensorDataEdgeProperies(e, tokens);
            }

        } else {
            //an existing frame
            //count the times this frame has been referenced
            counterRep++;
            PropertyPredicate pps2("id", PropertyPredicate::Eq,
                    atoi(tokens[1].c_str()));
            NodeIterator oi = db.get_nodes("object", pps2);

            if (!oi) {
                // a new object on an existing frame
                objectCounter++;

                Node &nobject = db.add_node("object");
                nobject.set_property("id", atoi(tokens[1].c_str()));
                nobject.set_property("type", tokens[2].c_str());

                Edge &e = db.add_edge(*fi, nobject, "contains");
                setSensorDataEdgeProperies(e, tokens);

            } else {
                // an existing object that appears on an existing frame
                Edge &e = db.add_edge(*fi, *oi, "contains");
                setSensorDataEdgeProperies(e, tokens);
            }
        }

        tx.commit();

    }

    std::cout << std::endl;

    std::cout << "Frames added: " << frameCounter << std::endl;
    std::cout << "Objects added " << objectCounter << std::endl;

    int numFrames = 0;
    Transaction tx(db, Transaction::ReadWrite);
    for (NodeIterator i = db.get_nodes("frame"); i; i.next()) 
    {
        numFrames++;
    }
    tx.commit();
    std::cout << "Total number of frames: " << numFrames << std::endl;

    return 0;
}