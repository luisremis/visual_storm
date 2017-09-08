#define __STDC_FORMAT_MACROS
#include <string>

#include "jarvis.h"
#include "util.h"

int insertSynonyms(std::string file, Jarvis::Graph& db, std::string tag, std::string prop);

int insertCountriesTree(std::string file, Jarvis::Graph& db, std::string tag);

int insertCities(std::string file, Jarvis::Graph& db, std::string tag);

