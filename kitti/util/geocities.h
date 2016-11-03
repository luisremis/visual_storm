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
#include <unordered_map>

using namespace Jarvis;

int insertCountriesTree(std::string file, Graph& db)
{
    std::string line;
    std::string token;

    std::ifstream filein(file);
    std::vector<std::string> tokens;
    int placesCounter = 0;

    Transaction txrem(db, Transaction::ReadWrite);
    for (NodeIterator i = db.get_nodes("place"); i; i.next()) // remove all places
    {
        db.remove(*i);
    }
    txrem.commit();

    Transaction txi(db, Transaction::ReadWrite);
    db.create_index(Graph::NodeIndex, "place", "name", PropertyType::String);
    db.create_index(Graph::NodeIndex, "place", "type", PropertyType::String);
    db.create_index(Graph::NodeIndex, "place", "code", PropertyType::String);
    db.create_index(Graph::NodeIndex, "place", "latitude" , PropertyType::Float);
    db.create_index(Graph::NodeIndex, "place", "longitude", PropertyType::Float);
    txi.commit();

    std::unordered_map<std::string, std::unordered_map<std::string,int > > continents; //List of countries by continent. 
    std::unordered_map<std::string, std::string> continents_code; // Continent Code map 
    std::unordered_map<std::string, std::string> countries_code;  // Country Code map 

    while(std::getline(filein, line)) 
    {     // '\n' is the default delimiter

        std::istringstream iss(line);
        tokens.clear();
        while(std::getline(iss, token, ','))
        {
            tokens.push_back(token);
        } 

        continents[tokens[3]][tokens[5]] = 1;
        continents_code[tokens[3]] = tokens[2];
        countries_code [tokens[5]] = tokens[4];

        //std::cout << tokens[2] << " " << tokens[3] << " " << tokens[4] << " " << tokens[5] << std::endl; 
    }


    for ( auto it = continents.begin(); it != continents.end(); ++it )
    {

        Transaction tx(db, Transaction::ReadWrite);

        Node &continent = db.add_node("place");
        continent.set_property("type", "continent");
        continent.set_property("name", it->first.c_str());
        continent.set_property("code", continents_code[it->first].c_str());

        for ( auto it_c = it->second.begin(); it_c != it->second.end(); ++it_c )
        {
            Node &country = db.add_node("place");
            country.set_property("type", "country");
            country.set_property("name", it_c->first.c_str());
            country.set_property("code", countries_code[it_c->first].c_str());
            Edge &e = db.add_edge(country, continent, "belongs to");
            e.set_property("testprop", "empy test prop");

            // std::cout << continents_code[it->first].c_str() << " " << it->first.c_str() << " " << countries_code[it_c->first].c_str() << " " << it_c->first.c_str() << std::endl; 

        }

        tx.commit();

    }

    Transaction tx(db, Transaction::ReadWrite);
    for (NodeIterator i = db.get_nodes("place"); i; i.next()) // should be only 0 or 1 though
    {
        placesCounter++;
        std::cout << i->get_property("type").string_value() << " " << i->get_property("code").string_value() << " " << i->get_property("name").string_value() << std::endl;
    }
    tx.commit();
    std::cout << "Total Places: " << placesCounter << std::endl;

    return 0;
}

int insertCities(std::string file, Graph& db)
{
    std::string line;
    std::string token;

    std::ifstream filein(file);
    std::vector<std::string> tokens;
    int placesCounter = 0;

    while(std::getline(filein, line)) 
    {     // '\n' is the default delimiter

        Transaction tx(db, Transaction::ReadWrite);

        std::istringstream iss(line);
        tokens.clear();

        while(std::getline(iss, token, ','))
        {
            tokens.push_back(token);
        } 

        PropertyPredicate pps1("code", PropertyPredicate::Eq, tokens[1].c_str() );
        NodeIterator i = db.get_nodes("place", pps1);

        if (i)
        {
            if (tokens[3].empty()) // No city name, assigning lat and long to the country
            {
                i->set_property("latitude",  atof(tokens[5].c_str()));
                i->set_property("longitude", atof(tokens[6].c_str()));
            }
            else // New city in that country
            {
                PropertyPredicate pps2("name", PropertyPredicate::Eq, tokens[3].c_str() );
                NodeIterator i_city = db.get_nodes("place", pps2);

                if (!i_city) // City does not exist already
                {
                    Node &city = db.add_node("place");
                    city.set_property("type", "city");
                    city.set_property("name", (tokens[3].c_str()));
                    city.set_property("code", "nocitycode");
                    city.set_property("latitude",  atof(tokens[5].c_str()));
                    city.set_property("longitude", atof(tokens[6].c_str()));
                    
                    Edge &e = db.add_edge(city, *i, "belongs to");
                    e.set_property("testprop", "empy test prop");
                }
                
            }
        }
        else
        {
            std::cout << "Non-existent Country code: " << tokens[1] << std::endl;
        }

        tx.commit();
    }

    Transaction tx(db, Transaction::ReadWrite);
    for (NodeIterator i = db.get_nodes("place"); i; i.next()) // should be only 0 or 1 though
    {
        placesCounter++;
        // std::cout << i->get_property("type").string_value() << " " << i->get_property("code").string_value() << " " << i->get_property("name").string_value() << std::endl;
    }
    tx.commit();

    std::cout << "Total Places: " << placesCounter << std::endl;


    return 0;
}
