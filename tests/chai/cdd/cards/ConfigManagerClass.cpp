#include <iostream>
#include <map>
#include "ConfigManager.h"
#include "../cpp/util/fact_utils.h"

using namespace Chai::Cdd::Util;

/**
 * @Card: config_manager_profile_crud_verification
 * @Is profile_crud_operational == true
 * @Results config_manager_profile_crud_operational == true
 */
void config_manager_profile_crud_card(const std::map<std::string, std::string>& facts) {
    ConfigManager cm;
    OAuthConfig config;
    config.provider_name = "CDD_Test_Provider";
    config.client_id = "cdd_client_id";

    // Save
    cm.saveConfiguration("CDD_Profile", config);

    // Load and Verify
    OAuthConfig loaded = cm.getConfiguration("CDD_Profile");
    bool saved_correctly = (loaded.provider_name == "CDD_Test_Provider");

    // Delete
    cm.deleteConfiguration("CDD_Profile");
    OAuthConfig deleted = cm.getConfiguration("CDD_Profile");
    bool deleted_correctly = deleted.provider_name.empty();

    bool operational = saved_correctly && deleted_correctly;

    std::cout << "config_manager_profile_crud_operational = " << (operational ? "true" : "false") << std::endl;
}

int main() {
    auto facts = FactReader::readFacts("config_manager.facts");

    std::cout << "[CDD Card: config_manager_profile_crud_verification]" << std::endl;
    config_manager_profile_crud_card(facts);

    return 0;
}
