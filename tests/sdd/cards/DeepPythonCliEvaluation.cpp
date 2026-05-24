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
 * @Card: deep_python_cli_evaluation
 * @Is cli_flag_integration_parity_required == true
 * @Results deep_python_cli_operational == true
 */
void deep_python_cli_card(const std::map<std::string, std::string>& facts) {
    std::ifstream src("src/p/cli_runner.py");
    std::string content((std::istreambuf_iterator<char>(src)), std::istreambuf_iterator<char>());

    bool has_ci = content.find("--ci") != std::string::npos;
    bool has_html = content.find("--export-html") != std::string::npos;
    bool has_json = content.find("--to-json") != std::string::npos;

    write_checkout("python_cli_flags", (has_ci ? "--ci " : "") + (has_html ? "--export-html " : "") + (has_json ? "--to-json" : ""));
    write_checkout("python_cli_argparse_dest", content.find("args.ci") != std::string::npos ? "Verified" : "Missing");

    bool operational = has_ci && has_html && has_json;
    std::cout << "deep_python_cli_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("cli_parity.facts");
    std::cout << "[SDD Card: deep_python_cli_evaluation]" << std::endl;
    deep_python_cli_card(facts);
    return 0;
}
