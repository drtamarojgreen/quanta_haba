#ifndef FACT_UTILS_H
#define FACT_UTILS_H
#include <map>
#include <string>
#include <fstream>
#include <iostream>
#include <filesystem>
namespace fs = std::filesystem;
namespace Sorrel::Sdd::Util {
class FactReader {
public:
    static std::map<std::string, std::string> readFacts(const std::string& filename) {
        std::map<std::string, std::string> facts;
        std::string base = std::getenv("SORREL_FACTS_DIR") ? std::getenv("SORREL_FACTS_DIR") : ".";
        std::ifstream file(fs::path(base) / filename);
        std::string line;
        while (std::getline(file, line)) {
            if (line.find("Is ") == 0) {
                size_t eq = line.find('=');
                if (eq != std::string::npos) {
                    std::string k = line.substr(3, eq - 3);
                    std::string v = line.substr(eq + 1);
                    k.erase(0, k.find_first_not_of(" ")); k.erase(k.find_last_not_of(" ") + 1);
                    v.erase(0, v.find_first_not_of(" ")); v.erase(v.find_last_not_of(" ") + 1);
                    facts[k] = v;
                }
            }
        }
        return facts;
    }
};
}
#endif
