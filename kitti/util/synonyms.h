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

int insertSynonyms(std::string file, Graph& db)
{
    std::string line;
    std::string token;

    std::ifstream filein(file);
    std::vector<std::string> tokens;
    int labelCounter = 0;

    std::ofstream filesyn("syn.txt");

    Transaction txi(db, Transaction::ReadWrite);
    db.create_index(Graph::NodeIndex, "label", "name", PropertyType::String);
    txi.commit();

    while(std::getline(filein, line)) 
    {     // '\n' is the default delimiter

        Transaction tx(db, Transaction::ReadWrite);

        std::istringstream iss(line);
        tokens.clear();

        while(std::getline(iss, token, '\t'))
        {
            tokens.push_back(token);
        } 

        if (tokens.size() != 2)
        {
            std::cout << "Tokens different from 2, what? " << std::endl;
            continue;
        }

        for (size_t i = 0; i < tokens.size(); ++i)
        {
            PropertyPredicate pps1("name", PropertyPredicate::Eq, tokens[i].c_str() );
            NodeIterator nodeit = db.get_nodes("label", pps1);

            if (!nodeit)
            {
                Node &nlabel = db.add_node("label");
                nlabel.set_property("name", tokens[i].c_str());
            }
        }

        PropertyPredicate pps1("name", PropertyPredicate::Eq, tokens[0].c_str() );
        NodeIterator i_first = db.get_nodes("label", pps1);

        PropertyPredicate pps2("name", PropertyPredicate::Eq, tokens[1].c_str() );
        NodeIterator i_second = db.get_nodes("label", pps2);

        if (!i_first || !i_second)
        {
            std::cout << "Label not found, what?" << std::endl;
        }

        Edge &e = db.add_edge(*i_first, *i_second, "synonym");
        e.set_property("testprop", "empy test prop");

        filesyn << i_first->get_property("name").string_value() << " - " << i_second->get_property("name").string_value() << std::endl;

        tx.commit();
    }

    Transaction tx(db, Transaction::ReadWrite);
    for (NodeIterator i = db.get_nodes("label"); i; i.next()) // should be only 0 or 1 though
    {
        labelCounter++;
    }
    tx.commit();
    std::cout << "Total Labels and synonyms: " << labelCounter << std::endl;

    return 0;
}
