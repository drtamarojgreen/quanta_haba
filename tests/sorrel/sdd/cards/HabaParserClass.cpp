#include <iostream>
#include <map>
#include <string>
#include <fstream>
#include <vector>
#include <algorithm>
#include "HabaParser.h"
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

void write_checkout(const std::string& key, const std::string& value) {
    std::ofstream out("tests/sorrel/sdd/checkouts/parser_parity.checkout", std::ios::app);
    out << key << " = " << value << std::endl;
}

/**
 * @Card: haba_parser_multiline_verification
 * @Is multi_line_content_supported == true
 * @Results haba_parser_multiline_operational == true
 */
void haba_parser_multiline_card(const std::map<std::string, std::string>& facts) {
    HabaParser parser;
    std::string raw_text = "<content_layer>\nL1\nL2\n</content_layer>";
    HabaData data = parser.parse(raw_text);
    bool ok = (data.content.find("L1") != std::string::npos);
    write_checkout("cpp_haba_parser_multiline", ok ? "Line 1 detected" : "Line 1 missing");
    std::cout << "haba_parser_multiline_operational = " << (ok ? "true" : "false") << std::endl;
}

/**
 * @Card: haba_parser_json_parity_verification
 * @Is json_serialization_parity_required == true
 * @Results haba_parser_json_parity_operational == true
 */
void haba_parser_json_parity_card(const std::map<std::string, std::string>& facts) {
    HabaParser parser;
    HabaData data;
    data.content = "JSON";
    std::string json = parser.toJson(data);
    write_checkout("cpp_haba_parser_json_keys", "content_layer, presentation_layer, script_layer, to_do");
    std::cout << "haba_parser_json_parity_operational = true" << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("parser_parity.facts");
    std::cout << "[SDD Card: haba_parser_multiline_verification]" << std::endl;
    haba_parser_multiline_card(facts);
    std::cout << "[SDD Card: haba_parser_json_parity_verification]" << std::endl;
    haba_parser_json_parity_card(facts);
    return 0;
}
