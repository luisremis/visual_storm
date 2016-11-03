#pragma once

#include <fstream>
#include <sstream>
#include <iostream>
#include <string>
#include <vector>
#include <stdlib.h>     /* system, NULL, EXIT_FAILURE */
#include <oxts_data.h>

class Frame {
public:
    std::string id;
    std::string sequence;
    std::string timestamp;
    OxtsData *oxts;

    Frame() {
        oxts = new OxtsData();
    }

    Frame(std::string id, std::string seq, std::string ts, std::string
    oxts_line) : id(id), sequence(seq), timestamp(ts) {
        oxts = new OxtsData(oxts_line);
    }

    ~Frame() {
        //                delete oxts;
    }


};

