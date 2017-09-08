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
#include <math.h>

using namespace Jarvis;

int notFound = 0;
float rad_distance_miles = 30;
float lng_equivalent = rad_distance_miles/55.8f;

#define PI (3.141592653589793f)

inline float radians(float a)
{
    return a * PI / 180.0f;
}

void map2Location(Node &nmedia , Graph& db)
{

    float media_lat = nmedia.get_property("latitude").float_value();
    float media_lng = nmedia.get_property("longitude").float_value();
    
    PropertyPredicate pps2("type", PropertyPredicate::Eq, "city" );
    PropertyPredicate pp2("longitude", PropertyPredicate::GeLe, media_lng-lng_equivalent, media_lng+lng_equivalent);

    // printf("Longitude Range:  %f - %f \n", media_lng-lng_equivalent, media_lng+lng_equivalent);

    for (NodeIterator i = db.get_nodes("place", pp2); i; i.next())
    {
        float city_lat  = i->get_property("latitude").float_value();
        float city_lng  = i->get_property("longitude").float_value();

        float distance_miles = 3959 * acos( cos( radians(city_lat) ) * cos( radians( media_lat ) ) * 
                cos( radians( media_lng ) - radians(city_lng) ) + sin( radians(city_lat) ) * sin( radians( media_lat ) ) );

        if ( distance_miles < rad_distance_miles) 
        {
            Edge &e = db.add_edge(nmedia, *i, "was taken");
            e.set_property("testprop", "empy test prop");
            // printf("city found: \n");
            // printf("%s\n", i->get_property("name").string_value().c_str());
            // printf("%f %f - %f %f\n", city_lat, city_lng, media_lat, media_lng);
            // printf("end city------------\n");
            return;
        }
    }


    notFound++;
    // printf("Not found\n");



}

int insertNewMedia(std::string file, Graph& db)
{

    std::string line;
    std::string token;

    std::ifstream filein(file);
    std::vector<std::string> tokens;
    size_t counter = 0;
    size_t counterRep = 0;
    int mediaCounter = 0;

    Transaction txi(db, Transaction::ReadWrite);
    db.create_index(Graph::NodeIndex, "label", "name", PropertyType::String);
    db.create_index(Graph::NodeIndex, "media", "id", PropertyType::Integer  );
    txi.commit();

    while(std::getline(filein, line)) 
    {     // '\n' is the default delimiter

        Transaction tx(db, Transaction::ReadWrite);

        std::istringstream iss(line);
        counter++;
        if (counter % 500 == 0)
        {
            std::cout << "\r" << counter;
            std::cout << std::flush;
        }
        tokens.clear();
        while(std::getline(iss, token, '\t'))
        {
            tokens.push_back(token);
        } 

        PropertyPredicate pps1("id", PropertyPredicate::Eq, atoi(tokens[0].c_str()) );
        NodeIterator i = db.get_nodes("media", pps1);

        if (!i)
        {
            Node &nmedia = db.add_node("media");
            nmedia.set_property("id", atoi(tokens[0].c_str()));
            nmedia.set_property("user", tokens[2].c_str());
            nmedia.set_property("date", tokens[3].c_str());
            nmedia.set_property("camera", tokens[4].c_str());
            nmedia.set_property("latitude", atof(tokens[11].c_str()));
            nmedia.set_property("longitude", atof(tokens[10].c_str()));
            nmedia.set_property("link", tokens[14].c_str());
            nmedia.set_property("city", "gotham");

            
            if (!tokens[10].empty())
            {
                // printf("%s %s \n",tokens[10].c_str(), tokens[11].c_str() );
                map2Location(nmedia, db);
            }  

            std::stringstream labels(tokens[8]);

            while(std::getline(labels, line)) 
            {     // '\n' is the default delimiter

                std::istringstream iss(line);
                while(std::getline(iss, token, ',')){
                    // boost::erase_all(token, "\token");

                    PropertyPredicate pps1("name", PropertyPredicate::Eq, token.c_str() );
                    NodeIterator i = db.get_nodes("label", pps1);

                    if (!i){
                        Node &nlabel = db.add_node("label");
                        nlabel.set_property("name", token);

                        Edge &e = db.add_edge(nmedia, nlabel, "has object");
                        e.set_property("testprop", "empy test prop");
                    }
                    else
                    {
                        Edge &e = db.add_edge(nmedia, *i, "has object");
                        e.set_property("testprop", "empy test prop");
                    }


                }   // but we can specify a different one
            }
        }
        else
        {
            counterRep++;
        }

        

        tx.commit();

    }

    std::cout << std::endl;

    // for (size_t i = 0; i < tokens.size(); ++i)
    // {
    //     std::cout << tokens[i] << std::endl; 
    // }

    std::cout << "Elements added: " << counter - counterRep << std::endl;
    std::cout << "Elements Repeted: " << counterRep << std::endl;

    Transaction tx(db, Transaction::ReadWrite);
    for (NodeIterator i = db.get_nodes("media"); i; i.next()) // should be only 0 or 1 though
    {
        mediaCounter++;
    }
    tx.commit();
    std::cout << "Total Media files: " << mediaCounter << std::endl;
    std::cout << "Not found files: " << notFound << std::endl;


    return 0;
}
