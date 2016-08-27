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

int insertSynonyms(std::string file, Jarvis::Graph& db)
{
    std::string line;
    std::string token;

    std::ifstream filein(file);
    std::vector<std::string> tokens;
    int labelCounter = 0;

    Jarvis::Transaction txi(db, Jarvis::Transaction::ReadWrite);
    db.create_index(Jarvis::Graph::NodeIndex, "label", "name", Jarvis::PropertyType::String);
    txi.commit();

    while(std::getline(filein, line)) 
    {     // '\n' is the default delimiter

        Jarvis::Transaction tx(db, Jarvis::Transaction::ReadWrite);

        std::istringstream iss(line);
        tokens.clear();

        while(std::getline(iss, token, '\t'))
        {
            tokens.push_back(token);
        } 

        if (tokens.size() != 2)
        {
            std::cout << "Tokens different from 2, something went wrong... " << std::endl;
            continue;
        }

        for (size_t i = 0; i < tokens.size(); ++i)
        {
            Jarvis::PropertyPredicate pps1("name", Jarvis::PropertyPredicate::Eq, tokens[i].c_str() );
            Jarvis::NodeIterator nodeit = db.get_nodes("label", pps1);

            if (!nodeit)
            {
                Jarvis::Node &nlabel = db.add_node("label");
                nlabel.set_property("name", tokens[i].c_str());
            }
        }

        Jarvis::PropertyPredicate pps1("name", Jarvis::PropertyPredicate::Eq, tokens[0].c_str() );
        Jarvis::NodeIterator i_first = db.get_nodes("label", pps1);

        Jarvis::PropertyPredicate pps2("name", Jarvis::PropertyPredicate::Eq, tokens[1].c_str() );
        Jarvis::NodeIterator i_second = db.get_nodes("label", pps2);

        if (!i_first || !i_second)
        {
            std::cout << "Label not found, what?" << std::endl;
        }

        Jarvis::Edge &e = db.add_edge(*i_first, *i_second, "synonym");
        e.set_property("testprop", "empy test prop");

        tx.commit();
    }

    Jarvis::Transaction tx(db, Jarvis::Transaction::ReadWrite);
    for (Jarvis::NodeIterator i = db.get_nodes("label"); i; i.next()) // should be only 0 or 1 though
    {
        labelCounter++;
    }
    tx.commit();
    std::cout << "Total Labels and synonyms: " << labelCounter << std::endl;

    return 0;
}
