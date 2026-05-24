#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <regex>

void discover(const std::string& target) {
    if (target == "sdd") {
        std::cout << "tests/sdd" << std::endl;
    } else if (target == "facts") {
        std::cout << "tests/sdd/facts" << std::endl;
    }
}

void parse_rules(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) return;
    std::string line;
    std::regex artifact_re("<Artifact path=\"([^\"]+)\" />");
    std::smatch match;
    while (std::getline(file, line)) {
        if (std::regex_search(line, match, artifact_re)) {
            std::cout << "Rule Artifact: " << match[1] << std::endl;
        }
    }
}

int main(int argc, char** argv) {
    if (argc < 2) return 1;
    std::string cmd = argv[1];
    if (cmd == "discover" && argc > 2) {
        discover(argv[2]);
    } else if (cmd == "rules" && argc > 2) {
        parse_rules(argv[2]);
    }
    return 0;
}
