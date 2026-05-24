#include <iostream>
#include <map>
#include <string>
#include <fstream>
#include <vector>
#include <algorithm>
#include "ConfigManager.h"
#include "../cpp/util/fact_utils.h"

using namespace Sorrel::Sdd::Util;

void write_checkout(const std::string& key, const std::string& value) {
    std::ofstream out("tests/sorrel/sdd/checkouts/config_parity.checkout", std::ios::app);
    out << key << " = " << value << std::endl;
}

/**
 * @Card: config_manager_profile_crud_verification
 * @Is profile_crud_operational == true
 * @Results config_manager_profile_crud_operational == true
 */
void config_manager_profile_crud_card(const std::map<std::string, std::string>& facts) {
    ConfigManager cm;
    OAuthConfig config;
    config.provider_name = "CRUD_TEST";
    cm.saveConfiguration("CRUD_Profile", config);
    OAuthConfig loaded = cm.getConfiguration("CRUD_Profile");
    bool ok = (loaded.provider_name == "CRUD_TEST");
    cm.deleteConfiguration("CRUD_Profile");

    write_checkout("cpp_config_crud", ok ? "Verified" : "Failed");
    std::cout << "config_manager_profile_crud_operational = " << (ok ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("config_manager.facts");
    std::cout << "[SDD Card: config_manager_profile_crud_verification]" << std::endl;
    config_manager_profile_crud_card(facts);
    return 0;
}
