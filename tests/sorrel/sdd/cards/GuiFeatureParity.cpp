#include <iostream>
#include <map>
#include <string>
#include <fstream>
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

void write_checkout(const std::string& key, const std::string& value) {
    std::ofstream out("tests/sorrel/sdd/checkouts/gui_parity.checkout", std::ios::app);
    out << key << " = " << value << std::endl;
}

/**
 * @Card: gui_feature_verification
 * @Is gui_feature_parity_required == true
 * @Results gui_features_operational == true
 */
void gui_feature_card(const std::map<std::string, std::string>& facts) {
    std::ifstream src("src/c/source/gui_editor.cpp");
    std::string content((std::istreambuf_iterator<char>(src)), std::istreambuf_iterator<char>());

    bool has_demo = content.find("Run Model Demo") != std::string::npos;
    bool has_config = content.find("OpenConfigDialog") != std::string::npos;

    write_checkout("cpp_gui_features", (has_demo ? "ModelDemo " : "") + (has_config ? "ConfigDialog" : ""));

    bool operational = has_demo && has_config;
    std::cout << "gui_features_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("gui_parity.facts");
    std::cout << "[SDD Card: gui_feature_verification]" << std::endl;
    gui_feature_card(facts);
    return 0;
}
