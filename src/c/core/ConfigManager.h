#ifndef CONFIG_MANAGER_H
#define CONFIG_MANAGER_H

#include <string>
#include <vector>
#include <map>
#include "OAuthClient.h" // Assuming OAuthConfig is defined here

class ConfigManager {
public:
    ConfigManager();
    bool loadConfigurations();
    bool saveConfigurations();
    OAuthConfig getConfiguration(const std::string& profileName);
    std::vector<std::string> getProfileNames();
    bool saveConfiguration(const std::string& profileName, const OAuthConfig& config);
    bool deleteConfiguration(const std::string& profileName);

private:
    std::string getConfigFilePath();
    std::map<std::string, OAuthConfig> configurations;
};

#endif // CONFIG_MANAGER_H
