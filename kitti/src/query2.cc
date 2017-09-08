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
#include "query2.h"
#include "strings.h"
#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stdlib.h>     /* system, NULL, EXIT_FAILURE */


using namespace Jarvis;

class ResultQ2 {
    static const int MAX_RESULTS = 20;

    Query2Result results;

public:

    Query2Result get_results() {
        return results;
    }

    void add(std::string title) {

        Query2ResultItem qri(title);

        if (std::find(results.begin(), results.end(), qri) == results.end()) {

            if (results.size() < MAX_RESULTS || qri < results.back()) {
                Query2Result::iterator pos = results.begin();
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

Query2Result query2(Graph &db, const std::string type1, const std::string type2) {
    std::cout << "Find the id of all the frames where there are objects of type Car and/or Pedestrian." << std::endl;

    Transaction tx(db, Transaction::ReadWrite);

    ResultQ2 result;

    auto type_filter = [type1, type2](const Node & n) {
        std::string type = n.get_property("type").string_value();
        return Disposition(type != type1 && type != type2);
    };

    auto p = [type1, type2, &result](Node & frame) {
        int count1 = 0, count2 = 0;
        NodeIterator objects = get_neighbors(frame, Outgoing, "contains", false)
                .filter([type1, type2](const Node & n) {
                    std::string type = n.get_property("type").string_value();
                    return Disposition(type != type1 && type != type2);
                });

        for (; objects; objects.next()) {
            std::string type = objects->get_property("type").string_value();
            if (type == type1)
                count1++;
            if (type == type2)
                count2++;
        }
        if (count1 > 0 && count2 > 0)
            result.add(frame.get_property("id").string_value());
    };

    *db.get_nodes("object").process(p);

    tx.commit();

    result.print_results();

    return result.get_results();
}

bool Query2ResultItem::operator<(const Query1ResultItem &a) const {
    return title < a.title;
}

bool Query2ResultItem::operator==(const Query1ResultItem &a) const {
    return (title.compare(a.title) == 0);
}
