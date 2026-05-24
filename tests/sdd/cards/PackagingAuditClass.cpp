#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sys/stat.h>
#include <map>
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

bool fileExists(const std::string& name) {
    struct stat buffer;
    return (stat(name.c_str(), &buffer) == 0);
}

long getFileSize(const std::string& filename) {
    struct stat stat_buf;
    int rc = stat(filename.c_str(), &stat_buf);
    return rc == 0 ? stat_buf.st_size : -1;
}

void packaging_audit_card(const std::map<std::string, std::string>& facts) {
    std::string build_dir = facts.count("build_directory") ? facts.at("build_directory") : "build/package";
    std::string dist_dir = facts.count("dist_directory") ? facts.at("dist_directory") : "dist";
    std::string version = facts.count("package_version") ? facts.at("package_version") : "1.0.0";

    std::vector<std::string> required = {
        build_dir + "/editor.py",
        build_dir + "/haba_parser.py",
        build_dir + "/haba-converter",
        build_dir + "/configuration/model_config.json",
        build_dir + "/README.md"
    };

    int found = 0;
    for (const auto& file : required) {
        if (fileExists(file)) found++;
    }

    std::string archive = dist_dir + "/quanta-haba-" + version + ".tar.gz";
    long size = getFileSize(archive);

    std::cout << "required_files_found = " << found << std::endl;
    std::cout << "package_archive_size_bytes = " << size << std::endl;
    std::cout << "package_integrity_operational = " << (found == 5 ? 1 : 0) << std::endl;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: PackagingAuditClass [LogicalCardName]" << std::endl;
        return 1;
    }

    std::string card_name = argv[1];
    auto facts = FactReader::readFacts("packaging.facts");

    if (card_name == "packaging_audit") {
        std::cout << "[SDD Card: packaging_audit]" << std::endl;
        packaging_audit_card(facts);
    } else {
        std::cerr << "Unknown logical card: " << card_name << std::endl;
        return 1;
    }

    return 0;
}
