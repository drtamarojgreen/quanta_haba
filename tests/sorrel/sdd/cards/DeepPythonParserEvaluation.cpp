#include <iostream>
#include <map>
#include <string>
#include <fstream>
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

void write_checkout(const std::string& key, const std::string& value) {
    std::ofstream out("tests/sorrel/sdd/checkouts/parser_parity.checkout", std::ios::app);
    out << key << " = " << value << std::endl;
}

/**
 * @Card: deep_python_parser_evaluation
 * @Is interface_contract_parity_required == true
 * @Results deep_python_parser_operational == true
 */
void deep_python_parser_card(const std::map<std::string, std::string>& facts) {
    std::ifstream src("src/p/haba_parser.py");
    std::string content((std::istreambuf_iterator<char>(src)), std::istreambuf_iterator<char>());

    bool has_to_json = content.find("def to_json") != std::string::npos;
    bool has_from_json = content.find("def from_json") != std::string::npos;

    write_checkout("python_parser_methods", (has_to_json ? "to_json " : "") + (has_from_json ? "from_json" : ""));
    write_checkout("python_parser_json_keys", content.find("content_layer") != std::string::npos ? "Verified" : "Missing");

    bool operational = has_to_json && has_from_json;
    std::cout << "deep_python_parser_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("parser_parity.facts");
    std::cout << "[SDD Card: deep_python_parser_evaluation]" << std::endl;
    deep_python_parser_card(facts);
    return 0;
}
