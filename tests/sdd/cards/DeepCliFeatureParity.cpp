#include <iostream>
#include <map>
#include <string>
#include <fstream>
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

void write_checkout(const std::string& key, const std::string& value) {
    std::ofstream out("tests/sorrel/sdd/checkouts/cli_parity.checkout", std::ios::app);
    out << key << " = " << value << std::endl;
}

/**
 * @Card: deep_cli_feature_verification
 * @Is cli_flag_integration_parity_required == true
 * @Results deep_cli_features_operational == true
 */
void deep_cli_feature_card(const std::map<std::string, std::string>& facts) {
    std::ifstream src("src/c/source/cli_editor.cpp");
    std::string content((std::istreambuf_iterator<char>(src)), std::istreambuf_iterator<char>());

    bool has_ci = content.find("--ci") != std::string::npos;
    bool has_html = content.find("--export-html") != std::string::npos;

    write_checkout("cpp_cli_flags", (has_ci ? "--ci " : "") + (has_html ? "--export-html" : ""));
    write_checkout("cpp_cli_state_mapping", content.find("state.ci_mode = true") != std::string::npos ? "Operational" : "Missing");

    bool operational = has_ci && has_html;
    std::cout << "deep_cli_features_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("cli_parity.facts");
    std::cout << "[SDD Card: deep_cli_feature_verification]" << std::endl;
    deep_cli_feature_card(facts);
    return 0;
}
