//
// KITTI query 1 : Find the titles of all videos that have objects of type "abc"
//

#define __STDC_FORMAT_MACROS

#include <string>
#include <vector>
#include <list>
#include "jarvis.h"

using namespace Jarvis;

struct Query1ResultItem {
    std::string title;

    Query1ResultItem(const std::string title)
    : title(title) {
    }

    bool operator<(const Query1ResultItem &) const;
    bool operator==(const Query1ResultItem &) const;

    std::string toString() {
        return title;
    }
};


typedef std::vector<Query1ResultItem> Query1Result;

Query1Result query1(Graph &db, std::string type);
