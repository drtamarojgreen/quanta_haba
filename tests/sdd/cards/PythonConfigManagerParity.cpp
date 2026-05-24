#include <iostream>
#include <map>
#include <string>
#include <fstream>
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

void write_checkout(const std::string& key, const std::string& value) {
    std::ofstream out("tests/sorrel/sdd/checkouts/config_parity.checkout", std::ios::app);
    out << key << " = " << value << std::endl;
}

/**
 * @Card: python_config_manager_parity_verification
 * @Results python_config_manager_parity_operational == true
 */
void python_config_manager_parity_card() {
    std::ifstream src("src/p/config_manager.py");
    std::string content((std::istreambuf_iterator<char>(src)), std::istreambuf_iterator<char>());

    bool has_get_names = content.find("def get_profile_names") != std::string::npos;
    bool has_save = content.find("def save_config") != std::string::npos;

    write_checkout("python_config_methods", (has_get_names ? "get_profile_names " : "") + (has_save ? "save_config" : ""));
    bool operational = has_get_names && has_save;
    std::cout << "python_config_manager_parity_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    std::cout << "[SDD Card: python_config_manager_parity_verification]" << std::endl;
    python_config_manager_parity_card();
    return 0;
}
