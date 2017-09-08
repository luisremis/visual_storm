//
// KITTI query 1 : Find the titles of all videos that have objects of type "abc"
//

#include <string>
#include <vector>
#include <map>
#include <unordered_set>
#include <algorithm>
#include "jarvis.h"
#include "util.h"
#include "neighbor.h"
#include "query1.h"
#include "strings.h"
#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stdlib.h>     /* system, NULL, EXIT_FAILURE */


using namespace Jarvis;

class Result {
    static const int MAX_RESULTS = 20;

    Query1Result results;

public:

    Query1Result get_results() {
        return results;
    }

    void add(std::string title) {

        Query1ResultItem qri(title);

        if (std::find(results.begin(), results.end(), qri) == results.end()) {

            if (results.size() < MAX_RESULTS || qri < results.back()) {
                Query1Result::iterator pos = results.begin();
                while (pos != results.end() && *pos < qri)
                    pos++;
                results.insert(pos, qri);

                if (results.size() > MAX_RESULTS)
                    results.pop_back();
            }
        }
    }

    void print_results() {
        std::cout << "Video titles:\n";
        for (auto &r : results)
            std::cout << r.toString() << "\n";
    }

};

Query1Result query1(Graph &db, const std::string type) {
    std::cout << "Find the titles of all the videos which have objects of type"
            " \"" << type << "\"." << std::endl;

    Result result;
    Transaction tx(db, Transaction::ReadWrite);

    PropertyPredicate pps1("type", PropertyPredicate::Eq, type.c_str());

    for (NodeIterator oi = db.get_nodes("object", pps1); oi; oi.next()) {
        for (EdgeIterator ei = oi->get_edges("contains"); ei; ei.next()) {
            Node &frame = ei->get_source();

            for (EdgeIterator ei2 = frame.get_edges("has"); ei2; ei2.next()) {
                Node &video = ei2->get_source();
                result.add(video.get_property("title").string_value());
            }
        }
    }

    tx.commit();
    result.print_results();

    return result.get_results();
}

bool Query1ResultItem::operator<(const Query1ResultItem &a) const {
    return title < a.title;
}

bool Query1ResultItem::operator==(const Query1ResultItem &a) const {
    return (title.compare(a.title) == 0);
}
