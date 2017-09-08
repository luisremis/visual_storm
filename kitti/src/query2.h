//
// KITTI query 1 : Find the titles of all videos that have objects of type "abc"
//

#define __STDC_FORMAT_MACROS

#include <string>
#include <vector>
#include <list>
#include "jarvis.h"

using namespace Jarvis;

struct Query2ResultItem {
    std::string title;

    Query2ResultItem(const std::string title)
    : title(title) {
    }

    bool operator<(const Query2ResultItem &) const;
    bool operator==(const Query2ResultItem &) const;

    std::string toString() {
        return title;
    }
};


typedef std::vector<Query2ResultItem> Query2Result;

Query2Result query2(Graph &db, std::string type);
