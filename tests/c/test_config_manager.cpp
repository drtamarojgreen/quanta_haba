#include "simple_test_framework.h"
#include "ConfigManager.h"
#include <fstream>

bool ConfigManagerTest_SaveAndLoadProfile() {
    ConfigManager cm;
    OAuthConfig config;
    config.provider_name = "TestProvider";
    config.client_id = "test_client_id";
    cm.saveConfiguration("TestProfile", config);

    ConfigManager cm2;
    OAuthConfig loaded_config = cm2.getConfiguration("TestProfile");
    ASSERT_EQ(config.provider_name, loaded_config.provider_name);
    ASSERT_EQ(config.client_id, loaded_config.client_id);
    return true;
}

bool ConfigManagerTest_DeleteProfile() {
    ConfigManager cm;
    OAuthConfig config;
    config.provider_name = "TestProvider";
    cm.saveConfiguration("TestProfileToDelete", config);
    cm.deleteConfiguration("TestProfileToDelete");

    ConfigManager cm2;
    OAuthConfig loaded_config = cm2.getConfiguration("TestProfileToDelete");
    ASSERT_EQ(std::string(""), loaded_config.provider_name);
    return true;
}

// Register tests
struct TestRegistrar_ConfigManager {
    TestRegistrar_ConfigManager() {
        add_test_case("ConfigManagerTest_SaveAndLoadProfile", ConfigManagerTest_SaveAndLoadProfile);
        add_test_case("ConfigManagerTest_DeleteProfile", ConfigManagerTest_DeleteProfile);
    }
};

static TestRegistrar_ConfigManager registrar_instance_config;
