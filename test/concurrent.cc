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
#include <thread>
#include <stdlib.h>     /* system, NULL, EXIT_FAILURE */
#include "neighbor.h"

#include "ChronoCpu.h"

using namespace Jarvis;


#define NUM_THREADS 1
#define TRANS_LOOP 500000

std::vector<std::string> cities;
std::vector<float> exe_time(NUM_THREADS);


void getCityNames(std::string file, Graph& db)
{
    std::string line;
    std::string token;

    std::ifstream filein(file);
    std::vector<std::string> tokens;
    std::vector<std::string> possibleCities;

    int edgecounter = 0;

    while(std::getline(filein, line)) 
    { 
        std::istringstream iss(line);
        tokens.clear();

        while(std::getline(iss, token, ','))
        {
            tokens.push_back(token);
        } 

        if (! tokens[3].empty())
        {
           possibleCities.push_back(tokens[3] );           
        }
    }

    std::cout << possibleCities.size() << " possibleCities found" << std::endl;

    for (size_t i = 0; i < possibleCities.size(); ++i)
    {

        std::string key = possibleCities[i];

        edgecounter = 0;
        Transaction tx2(db, Transaction::ReadWrite);
        PropertyPredicate pps1("name", PropertyPredicate::Eq, key.c_str() );
        for (NodeIterator i = db.get_nodes("place", pps1); i; i.next()) // should be only 0 or 1 though
        {
            for (EdgeIterator ed = i->get_edges("was taken"); ed; ed.next()) // should be only 0 or 1 though
            {
                edgecounter++;
            }
                
        }
        tx2.commit();

        if (edgecounter)
        {
            cities.push_back(key);
        }
    }

    std::cout << cities.size() << " cities found" << std::endl;
}

void queryLocation(Graph* db, int thread_id)
{
    int edgecounter = 0;

    srand(time(NULL));
    
    ChronoCpu chrono("chrono_tx");
    
    for (int i = 0; i < TRANS_LOOP; ++i)
    {
        std::string key = cities[size_t(rand()%cities.size())];

        chrono.tic();
        Transaction tx2(*db, Transaction::ReadOnly);
        PropertyPredicate pps1("name", PropertyPredicate::Eq, key.c_str() );
        for (NodeIterator i = db->get_nodes("place", pps1); i; i.next()) // should be only 0 or 1 though
        {
            for (EdgeIterator ed = i->get_edges("was taken"); ed; ed.next()) // should be only 0 or 1 though
            {
                //fileurls << ed->get_source().get_property("link").string_value() << std::endl;
                edgecounter++;
            }
                
        }
        tx2.commit();
        chrono.tac();
    }


    // std::cout << "Query time (AVG): " << chrono.getElapsedStats().averageTime_ms << std::endl;
    exe_time[thread_id] = chrono.getElapsedStats().averageTime_ms;    
}

int main(int argc, char **argv)
{
    // int create = atoi(argv[1]);

    Graph* db;

    try{
        db = new Graph("yfcc100m", Graph::ReadWrite);
    }
    catch(Exception e) {
        print_exception(e);
        printf("Not existent Database, creating a new one\n");

        try{
            db = new Graph("yfcc100m", Graph::Create);
        }
        catch(Exception e) {
            print_exception(e);
            return 1;
        }
    }


    try {

        getCityNames("data/geolite2/latlongcities.csv", *db);

        // if (create == 11)
        {
            std::vector<std::thread*> t(NUM_THREADS);
            for (int i = 0; i < NUM_THREADS; ++i)
            {
                t[i] =  new std::thread(queryLocation,db,i);
            }
            for (int i = 0; i < NUM_THREADS; ++i)
            {
                t[i]->join();
            }
            
            float sum = 0.0f;
            for (int i = 0; i < NUM_THREADS; ++i)
            {
                sum += exe_time[i];
            }

            std::cout << "Average Exe time = " << sum / NUM_THREADS << std::endl;
        }
    }
    catch (Exception e) {
        print_exception(e);
        return 1;
    }


    return 0;
}
