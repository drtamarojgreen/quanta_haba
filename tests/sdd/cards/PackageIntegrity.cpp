#include <iostream>
#include <vector>
#include <sys/stat.h>
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

bool fileExists(const std::string& name) {
    struct stat buffer;
    return (stat(name.c_str(), &buffer) == 0);
}

int main(int argc, char** argv) {
    auto facts = FactReader::readFacts("packaging.facts");
    std::string build_dir = facts.count("build_directory") ? facts["build_directory"] : "build/package";

    std::vector<std::string> required = {
        build_dir + "/editor.py",
        build_dir + "/haba_parser.py",
        build_dir + "/haba-converter",
        build_dir + "/configuration/model_config.json",
        build_dir + "/README.md"
    };

    int found = 0;
    for (const auto& f : required) {
        if (fileExists("../../" + f)) found++;
    }

    std::cout << "required_files_found = " << found << std::endl;
    std::cout << "package_integrity_operational = " << (found == 5 ? 1 : 0) << std::endl;

    return 0;
}
