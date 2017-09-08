/*
 * This test checks Jarvis iterator filters
 */

#define __STDC_FORMAT_MACROS
#include <inttypes.h>
#include "jarvis.h"
#include "util.h"
#include "neighbor.h"
#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stdlib.h>     /* system, NULL, EXIT_FAILURE */
#include <boost/serialization/nvp.hpp>

#include "kitti_csv_reader.h"
#include "kitti_data_reader.h"
//#include "query1.h"
#include "query1.cc"
//#include "query2.cc"

using namespace Jarvis;

int query(Graph& db, std::string frameId) {

    int edgecounter = 0;

    std::ofstream resultIds("objectIds.txt");

    Transaction tx2(db, Transaction::ReadWrite);
    PropertyPredicate pps1("id", PropertyPredicate::Eq, atoi(frameId.c_str()));
    for (NodeIterator fi = db.get_nodes("frame", pps1); fi; fi.next()) {
        EdgeIterator ei = fi->get_edges(Direction::Outgoing);

        for (EdgeIterator ei = fi->get_edges("contains"); ei; ei.next()) {
            if (!strcmp(ei->get_property(StringID("type"))
                    .string_value().c_str(), "Car")) {
                resultIds << ei->get_destination().get_id() << " " <<
                        ei->get_destination().get_property(StringID("id"))
                        .int_value() << std::endl;
                edgecounter++;
            }
        }
    }

    tx2.commit();

    std::cout << "Number of Results: " << edgecounter << std::endl;

    return 0;

}

void showUsage() {

    std::cout << "\nUsage:\n";
    std::cout << "./kitti 0 <path_to_kitti_dataset_csv_file>" << std::endl;
    std::cout << "./kitti 1 <path_to_root_kitti_dataset_directory> <date>"
            " <drive_seq>" << std::endl;
    std::cout << "./kitti 2 <search_term> <path_to_media_data>" << std::endl;
    std::cout << "./kitti 3 <object type>" << std::endl;
    std::cout << "./kitti 4 <object type1> <object type2>" << std::endl;
}

int main(int argc, char **argv) {
    if (argc > 5) {
        showUsage();
        return 0;
    }

    int create = atoi(argv[1]);

    Graph* db;

    try {

        db = new Graph("kittigraph", Graph::ReadWrite);
        printf("\nOpened existing kittigraph db.\n");

    } catch (Exception e) {
        //        print_exception(e);
        printf("Opening a not existent database, creating a new one.\n");

        try {
            db = new Graph("kittigraph", Graph::Create);
            printf("DB created.\n");

        } catch (Exception e) {
            print_exception(e);
            return 1;
        }
    }

    try {

        switch (create) {
            case 0:
                loadAllVideosMetadata(argv[2], *db);
                break;
            case 1:
                loadVideo(argv[2], argv[3], argv[4], *db);
                break;
            case 2:
                //for videos from object or tracking datasets
                uploadVideosFromCSV(argv[3], *db);
            case 3:
                query1(*db, argv[2]);
                break;
            case 4:
//                query2(*db, argv[2], argv[3]);
                break;
            default:
                break;
        }

        dbState(*db);

    } catch (Exception e) {
        print_exception(e);
        return 1;
    }


    return 0;
}