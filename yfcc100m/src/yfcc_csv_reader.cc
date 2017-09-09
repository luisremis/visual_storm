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
#include <math.h>

#include "yfcc_csv_reader.h"
// #include "Chrono.h"

#define IMAGE_TAG "AT:IMAGE"
#define PLACE_TAG "PLACE"
#define LABEL_TAG "LABEL"

float rad_distance_miles = 30;
float lng_equivalent = rad_distance_miles/55.8f;

#define PI (3.141592653589793f)

inline float radians(float a)
{
    return a * PI / 180.0f;
}

void map2Location(Jarvis::Node &nmedia , Jarvis::Graph& db)
{
    float media_lat = nmedia.get_property("latitude").float_value();
    float media_lng = nmedia.get_property("longitude").float_value();

    Jarvis::PropertyPredicate pp2("longitude", Jarvis::PropertyPredicate::GeLe,
                                    media_lng-lng_equivalent, media_lng+lng_equivalent);

    for (Jarvis::NodeIterator i = db.get_nodes(PLACE_TAG, pp2); i; i.next()) {
        float city_lat  = i->get_property("latitude").float_value();
        float city_lng  = i->get_property("longitude").float_value();

        float distance_miles = 3959 * acos( cos( radians(city_lat) ) * cos( radians( media_lat ) ) *
                cos( radians( media_lng ) - radians(city_lng) ) +
                sin( radians(city_lat) ) * sin( radians( media_lat ) ) );

        if ( distance_miles < rad_distance_miles) {
            Jarvis::Edge &e = db.add_edge(nmedia, *i, "was taken");
            e.set_property("testprop", "empy test prop");
            return;
        }
    }
}

int insertNewMedia(std::string file, Jarvis::Graph& db)
{
    std::string line;
    std::string token;

    std::ifstream filein(file);
    std::vector<std::string> tokens;
    size_t counter = 0;
    size_t counterRep = 0;
    int mediaCounter = 0;

    Jarvis::Transaction txi(db, Jarvis::Transaction::ReadWrite);
    db.create_index(Jarvis::Graph::NodeIndex, LABEL_TAG, "name", Jarvis::PropertyType::String);
    db.create_index(Jarvis::Graph::NodeIndex, IMAGE_TAG, "id", Jarvis::PropertyType::Integer  );
    txi.commit();

    // ChronoCpu chrono("chrono_tx");

    // '\n' is the default delimiter
    while(std::getline(filein, line)) {

        std::istringstream iss(line);
        counter++;
        if (counter % 500 == 0) {
            std::cout << "\r Elements loaded: " << counter;
                      // << " - Avg Trans Time: "
                      // << chrono.getElapsedStats().averageTime_ms << " ms";
            std::cout << std::flush;
        }
        tokens.clear();
        while(std::getline(iss, token, '\t')) {
            tokens.push_back(token);
        }

        // chrono.tic();
        Jarvis::Transaction tx(db, Jarvis::Transaction::ReadWrite);

        Jarvis::PropertyPredicate pps1("id", Jarvis::PropertyPredicate::Eq, atoi(tokens[0].c_str()) );
        Jarvis::NodeIterator i = db.get_nodes(IMAGE_TAG, pps1);

        if (!i) {
            Jarvis::Node &nmedia = db.add_node(IMAGE_TAG);

            // nmedia.set_property("lineNumber", atoi(tokens[0].c_str()));
            nmedia.set_property("id",  atoi(tokens[1].c_str()));
            nmedia.set_property("mediaHash", tokens[2].c_str());
            nmedia.set_property("userId" , tokens[3].c_str());
            nmedia.set_property("userNick" , tokens[4].c_str());
            nmedia.set_property("datetaken",  tokens[5].c_str());
            nmedia.set_property("dateUplo",  tokens[6].c_str());
            nmedia.set_property("captureDev" , tokens[7].c_str());
            nmedia.set_property("title",  tokens[8].c_str());
            nmedia.set_property("description",  tokens[9].c_str());
            // nmedia.set_property("User tags (comma-separated)",  tokens[10].c_str());
            // nmedia.set_property("Machine tags (comma-separated)",  tokens[11].c_str());
            nmedia.set_property("longitude",  atof(tokens[12].c_str()));
            nmedia.set_property("latitude",   atof(tokens[13].c_str()));
            nmedia.set_property("accuracyLoc",  tokens[14].c_str());
            nmedia.set_property("webUrl",  tokens[15].c_str());
            nmedia.set_property("link",  tokens[16].c_str());
            nmedia.set_property("licenseName",  tokens[17].c_str());
            nmedia.set_property("licenseURL",  tokens[18].c_str());
            nmedia.set_property("serverId",  tokens[19].c_str());
            nmedia.set_property("farmId",  tokens[20].c_str());
            nmedia.set_property("secret",  tokens[21].c_str());
            nmedia.set_property("secretOrig",  tokens[22].c_str());
            nmedia.set_property("extension",  tokens[23].c_str());
            nmedia.set_property("format",  tokens[24].c_str());


            if (!tokens[10].empty()) {
                map2Location(nmedia, db);
            }

            std::stringstream labels(tokens[10]);

            // '\n' is the default delimiter
            while(std::getline(labels, line)) {
                std::istringstream iss(line);

                while(std::getline(iss, token, ',')) {
                    Jarvis::PropertyPredicate pps1("name", Jarvis::PropertyPredicate::Eq, token.c_str() );
                    Jarvis::NodeIterator i = db.get_nodes(LABEL_TAG, pps1);

                    if (!i){
                        Jarvis::Node &nlabel = db.add_node(LABEL_TAG);
                        nlabel.set_property("name", token);

                        Jarvis::Edge &e = db.add_edge(nmedia, nlabel, "has object");
                        e.set_property("testprop", "empy test prop");
                    }
                    else {
                        Jarvis::Edge &e = db.add_edge(nmedia, *i, "has object");
                        e.set_property("testprop", "empy test prop");
                    }
                }
            }
        }
        else {
            counterRep++;
        }

        tx.commit();
    }

    std::cout << std::endl;

    std::cout << "Elements added: " << counter - counterRep << std::endl;
    std::cout << "Elements Repeted: " << counterRep << std::endl;

    Jarvis::Transaction tx(db, Jarvis::Transaction::ReadWrite);
    // should be only 0 or 1 though
    for (Jarvis::NodeIterator i = db.get_nodes(IMAGE_TAG); i; i.next()) {
        mediaCounter++;
    }
    tx.commit();

    std::cout << "Total Media files: " << mediaCounter << std::endl;

    return 0;
}
