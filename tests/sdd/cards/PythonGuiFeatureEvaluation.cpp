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
 * @Card: python_gui_feature_evaluation
 * @Is gui_feature_parity_required == true
 * @Results python_gui_features_operational == true
 */
void python_gui_eval_card(const std::map<std::string, std::string>& facts) {
    std::ifstream src("src/p/editor.py");
    std::string content((std::istreambuf_iterator<char>(src)), std::istreambuf_iterator<char>());

    bool has_demo = content.find("QuantaDemoWindow") != std::string::npos;
    bool has_config = content.find("ConfigDialog") != std::string::npos;

    write_checkout("python_gui_features_raw", (has_demo ? "ModelDemo " : "") + (has_config ? "ConfigDialog" : ""));

    bool operational = has_demo && has_config;
    std::cout << "python_gui_features_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("gui_parity.facts");
    std::cout << "[SDD Card: python_gui_feature_evaluation]" << std::endl;
    python_gui_eval_card(facts);
    return 0;
}
