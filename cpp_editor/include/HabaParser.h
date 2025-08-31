#ifndef HABA_PARSER_H
#define HABA_PARSER_H

#include "HabaData.h"
#include <string>

/**
 * @class HabaParser
 * @brief A parser for the .haba file format.
 */
class HabaParser {
public:
    /**
     * @brief Parses the raw text of a .haba file into a HabaData object.
     * @param raw_text The raw text of the .haba file.
     * @return A HabaData object containing the parsed data.
     */
    HabaData parse(const std::string& raw_text);

    /**
     * @brief Builds a .haba file string from a HabaData object.
     * @param haba_data The HabaData object.
     * @return A string representing the content of a .haba file.
     */
    std::string build(const HabaData& haba_data);
};

#endif // HABA_PARSER_H
