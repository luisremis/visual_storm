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
#include "neighbor.h"


#include "yfcc_csv_reader.h"
#include "geocities.h"
#include "synonyms.h"
// #include "ChronoCpu.h"

using namespace Jarvis;

int query(Graph& db, std::string key)
{
    int sanitycounter = 0;
    int edgecounter = 0;
    int extendedCounter = 0;
    int synCounter = 0;


    std::ofstream fileurls("urls.txt");
    std::ofstream fileurls_ext("urls_extended.txt");

    Transaction tx1(db, Transaction::ReadWrite);
    PropertyPredicate pps1("name", PropertyPredicate::Eq, key.c_str() );
    for (NodeIterator i = db.get_nodes("label", pps1); i; i.next()) // should be only 0 or 1 though
    {
        for (EdgeIterator ed = i->get_edges("has object"); ed; ed.next()) // should be only 0 or 1 though
        {
            fileurls << ed->get_source().get_property("link").string_value() << std::endl;
            edgecounter++;
        }
        // for (EdgeIterator ed = i->get_edges("synonym"); ed; ed.next()) // should be only 0 or 1 though
        // {
        //     std::cout << ed->get_source().get_property("name").string_value() << " - " << ed->get_destination().get_property("name").string_value() << std::endl;
        // }
        sanitycounter++;
            
    }
    tx1.commit();

    // std::cout << "Sanity Counter: " << sanitycounter << std::endl;
    std::cout << "Number of Results: " << edgecounter << std::endl;


    Transaction tx2(db, Transaction::ReadWrite);
    for (NodeIterator i = db.get_nodes("label", pps1); i; i.next()) // should be only 0 or 1 though
    {

        for (EdgeIterator ed = i->get_edges("synonym"); ed; ed.next()) // should be only 0 or 1 though
        {

            Node* it;
            if ( ed->get_source().get_property("name").string_value() == i->get_property("name").string_value() )
            {
                it = &ed->get_destination();
            }
            else
            {
                it = &ed->get_source();
            }

            std::cout << it->get_property("name").string_value() << std::endl;

            for (EdgeIterator ed = it->get_edges("has object"); ed; ed.next()) // should be only 0 or 1 though
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



    // std::cout << "Downloading images..." << std::endl;

    // int i =0;
    // i = system("rm images/*");
    // i = system("python downloadimages.py");
    // printf("%d\n", i);

    return 0;
}

int queryLocation(Graph& db, std::string key)
{

    int sanitycounter = 0;
    int edgecounter = 0;

    std::ofstream fileurls("urls.txt");

    Transaction tx2(db, Transaction::ReadWrite);
    PropertyPredicate pps1("name", PropertyPredicate::Eq, key.c_str() );
    for (NodeIterator i = db.get_nodes("place", pps1); i; i.next()) // should be only 0 or 1 though
    {
        std::cout << key << " is at " << i->get_property("latitude").float_value() << " , " 
                  << i->get_property("longitude").float_value() << std::endl;
        for (EdgeIterator ed = i->get_edges("was taken"); ed; ed.next()) // should be only 0 or 1 though
        {
            fileurls << ed->get_source().get_property("link").string_value() << std::endl;
            edgecounter++;
        }
        sanitycounter++;
            
    }
    tx2.commit();

    // std::cout << "Sanity Counter: " << sanitycounter << std::endl;
    std::cout << "Number of Results: " << edgecounter << std::endl;

    // std::cout << "Downloading images..." << std::endl;

    // int i =0;
    // i = system("rm images/*");
    // i = system("python downloadimages.py");
    // printf("%d\n", i);

    return 0;
    
}

int main(int argc, char **argv)
{
    int create = atoi(argv[1]);

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

        if (create == 1){
            insertNewMedia(argv[2], *db);
        }
        if (create == 2)
        {
            insertCountriesTree(argv[2], *db);
        }
        if (create == 3)
        {
            insertCities(argv[2], *db);
        }
        if (create == 4)
        {
            insertSynonyms(argv[2], *db);
        }

        if (create == 10)
        {
            int i = query(*db, argv[2]);
            printf("%d\n", i);
        }

        if (create == 11)
        {
            int i = queryLocation(*db, argv[2]);
            printf("%d\n", i);
        }

    }
    catch (Exception e) {
        print_exception(e);
        return 1;
    }


    return 0;
}
