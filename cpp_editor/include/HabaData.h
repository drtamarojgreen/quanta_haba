#ifndef HABA_DATA_H
#define HABA_DATA_H

#include <string>
#include <vector>
#include <utility> // for std::pair

/**
 * @class HabaData
 * @brief A simple data class to hold the parsed Haba file content.
 */
class HabaData {
public:
    std::string content;
    std::vector<std::pair<std::string, std::string>> presentation_items;
    std::string script;
};

#endif // HABA_DATA_H
