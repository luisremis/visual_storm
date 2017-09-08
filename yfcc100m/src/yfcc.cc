#define __STDC_FORMAT_MACROS
#include <inttypes.h>
#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stdlib.h>     /* system, NULL, EXIT_FAILURE */

#include "jarvis.h"
#include "util.h"
#include "neighbor.h"

#include "yfcc_csv_reader.h"
#include "misc_loaders.h"
#include "Chrono.h"

int query(Jarvis::Graph& db, std::string key)
{
    int edgecounter = 0;
    int extendedCounter = 0;
    int synCounter = 0;

    std::ofstream fileurls("urls.txt");
    std::ofstream fileurls_ext("urls_extended.txt");

    Jarvis::Transaction tx1(db, Jarvis::Transaction::ReadWrite);
    Jarvis::PropertyPredicate pps1("name", Jarvis::PropertyPredicate::Eq, key.c_str() );
    for (Jarvis::NodeIterator i = db.get_nodes("label", pps1); i; i.next())
    {
        for (Jarvis::EdgeIterator ed = i->get_edges("has object"); ed; ed.next())
        {
            fileurls << ed->get_source().get_property("link").string_value() << std::endl;
            edgecounter++;
        }           
    }
    tx1.commit();

    std::cout << "Number of Results: " << edgecounter << std::endl;


    Jarvis::Transaction tx2(db, Jarvis::Transaction::ReadWrite);
    for (Jarvis::NodeIterator i = db.get_nodes("label", pps1); i; i.next()) 
    {

        for (Jarvis::EdgeIterator ed = i->get_edges("synonym"); ed; ed.next())
        {

            Jarvis::Node* it;
            if ( ed->get_source().get_property("name").string_value() == i->get_property("name").string_value() )
            {
                it = &ed->get_destination();
            }
            else
            {
                it = &ed->get_source();
            }

            for (Jarvis::EdgeIterator ed = it->get_edges("has object"); ed; ed.next())
            {
                fileurls_ext << ed->get_source().get_property("link").string_value() << std::endl;
                extendedCounter++;
            }
            synCounter++;
        }
            
    }
    tx2.commit();


    std::cout << "Sync Counter: " << synCounter << std::endl;
    std::cout << "Extended Search Results: " << extendedCounter << std::endl;

    return 0;
}

int queryLocation(Jarvis::Graph& db, std::string key)
{

    int edgecounter = 0;

    std::ofstream fileurls("urls.txt");

    Jarvis::Transaction tx2(db, Jarvis::Transaction::ReadWrite);
    Jarvis::PropertyPredicate pps1("name", Jarvis::PropertyPredicate::Eq, key.c_str() );
    for (Jarvis::NodeIterator i = db.get_nodes("place", pps1); i; i.next())
    {
        std::cout << key << " is at " << i->get_property("latitude").float_value() << " , " 
                  << i->get_property("longitude").float_value() << std::endl;
        for (Jarvis::EdgeIterator ed = i->get_edges("was taken"); ed; ed.next())
        {
            fileurls << ed->get_source().get_property("link").string_value() << std::endl;
            edgecounter++;
        }            
    }
    tx2.commit();

    std::cout << "Number of Results: " << edgecounter << std::endl;

    return 0;    
}

int main(int argc, char **argv)
{
    std::string create = argv[1];

    std::string jarvisDB("/mnt/pmfs/yfcc100m_jarvis"); // By default

    if (argc > 3){
        jarvisDB = argv[3];
    }

    Jarvis::Graph* db;
    Jarvis::Graph::Config config;
    config.default_region_size = 0x4000000000; // Set to 256 GB

    try{
        db = new Jarvis::Graph(jarvisDB.c_str(), Jarvis::Graph::ReadWrite, &config);
    }
    catch(Jarvis::Exception e) {
        print_exception(e);
        printf("Not existent Database, creating a new one\n");

        try{
            db = new Jarvis::Graph(jarvisDB.c_str(), Jarvis::Graph::Create, &config);
        }
        catch(Jarvis::Exception e) {
            print_exception(e);
            return 1;
        }
    }


    try {

        if (create == "--media"){
            insertNewMedia(argv[2], *db);
        }
        if (create == "--locationTree")
        {
            insertCountriesTree(argv[2], *db, "place");
        }
        if (create == "--cities")
        {
            insertCities(argv[2], *db, "place");
        }
        if (create == "--synonyms")
        {
            insertSynonyms(argv[2], *db, "label", "name");
        }

        if (create == "--queryLabel")
        {
            int i = query(*db, argv[2]);
            printf("%d\n", i);
        }

        if (create == "--queryLocation")
        {
            int i = queryLocation(*db, argv[2]);
            printf("%d\n", i);
        }

    }
    catch (Jarvis::Exception e) {
        print_exception(e);
        return 1;
    }


    return 0;
}
