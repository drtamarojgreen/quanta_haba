#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include "HabaParser.h"
#include "HabaData.h"

void print_usage() {
    std::cout << "Usage: haba_editor <file_path>" << std::endl;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        print_usage();
        return 1;
    }

    std::string file_path = argv[1];
    std::ifstream file(file_path);

    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << file_path << std::endl;
        return 1;
    }

    std::string raw_text((std::istreambuf_iterator<char>(file)),
                         std::istreambuf_iterator<char>());

    HabaParser parser;
    HabaData data = parser.parse(raw_text);

    std::cout << "--- Parsed Haba Data ---" << std::endl;
    std::cout << "Content: " << data.content << std::endl;
    std::cout << "Presentation Items:" << std::endl;
    for (const auto& item : data.presentation_items) {
        std::cout << "  " << item.first << ": " << item.second << std::endl;
    }
    std::cout << "Script: " << data.script << std::endl;

    return 0;
}
