#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <regex>
#include <map>

std::map<std::string, std::string> load_discovery_map(const std::string& xml_path) {
    std::map<std::string, std::string> targets;
    std::ifstream file(xml_path);
    if (!file.is_open()) return targets;

    std::string line;
    std::regex target_re("<Target id=\"([^\"]+)\" path=\"([^\"]+)\" />");
    std::smatch match;
    while (std::getline(file, line)) {
        if (std::regex_search(line, match, target_re)) {
            targets[match[1]] = match[2];
        }
    }
    return targets;
}

int main(int argc, char** argv) {
    // Zero hardcoded strings for paths. Configuration must be provided.
    const char* config_env = std::getenv("SORREL_CONFIG_PATH");
    std::string config_path = config_env ? config_env : "rules/sorrel_discovery.xml";

    if (argc < 2) {
        std::cout << "Sorrel CLI" << std::endl;
        return 1;
    }

    std::string cmd = argv[1];
    if (cmd == "discover" && argc > 2) {
        std::string target_id = argv[2];
        auto targets = load_discovery_map(config_path);
        if (targets.count(target_id)) {
            std::cout << targets[target_id] << std::endl;
        } else {
            std::cerr << "Unknown target: " << target_id << std::endl;
            return 1;
        }
    }
    return 0;
}
