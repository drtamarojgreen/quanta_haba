#include "../include/ConfigManager.h"
#include <fstream>
#include <iostream>
#include <json/json.h> // Assuming jsoncpp library is available
#include <sys/stat.h> // For checking file existence

#ifdef _WIN32
#include <shlobj.h>
#endif

ConfigManager::ConfigManager() {
    loadConfigurations();
}

std::string ConfigManager::getConfigFilePath() {
    std::string path;
#ifdef _WIN32
    char szPath[MAX_PATH];
    if (SUCCEEDED(SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, 0, szPath))) {
        path = std::string(szPath) + "\\QuantaHaba";
        CreateDirectoryA(path.c_str(), NULL);
        path += "\\oauth_profiles.json";
    }
#else
    // Linux/macOS implementation
    const char* homeDir = getenv("HOME");
    if (homeDir) {
        path = std::string(homeDir) + "/.config/QuantaHaba";
        mkdir(path.c_str(), 0700);
        path += "/oauth_profiles.json";
    }
#endif
    return path;
}

bool ConfigManager::loadConfigurations() {
    std::string filePath = getConfigFilePath();
    std::ifstream configFile(filePath);
    if (!configFile.is_open()) {
        return false; // File doesn't exist or couldn't be opened
    }

    Json::Value root;
    configFile >> root;

    for (auto const& profileName : root.getMemberNames()) {
        const Json::Value& profile = root[profileName];
        OAuthConfig config;
        config.provider_name = profile.get("provider_name", profileName).asString();
        config.client_id = profile.get("client_id", "").asString();
        config.client_secret = profile.get("client_secret", "").asString();
        config.authorization_url = profile.get("authorization_url", "").asString();
        config.token_url = profile.get("token_url", "").asString();
        config.api_base_url = profile.get("api_base_url", "").asString();
        config.redirect_uri = profile.get("redirect_uri", "http://localhost:8080/callback").asString();
        config.use_pkce = profile.get("use_pkce", true).asBool();

        const Json::Value& scopes = profile["scopes"];
        for (const auto& scope : scopes) {
            config.scopes.push_back(scope.asString());
        }
        configurations[profileName] = config;
    }
    return true;
}

bool ConfigManager::saveConfigurations() {
    std::string filePath = getConfigFilePath();
    std::ofstream configFile(filePath);
    if (!configFile.is_open()) {
        return false;
    }

    Json::Value root;
    for (const auto& pair : configurations) {
        Json::Value profile;
        profile["provider_name"] = pair.second.provider_name;
        profile["client_id"] = pair.second.client_id;
        profile["client_secret"] = pair.second.client_secret;
        profile["authorization_url"] = pair.second.authorization_url;
        profile["token_url"] = pair.second.token_url;
        profile["api_base_url"] = pair.second.api_base_url;
        profile["redirect_uri"] = pair.second.redirect_uri;
        profile["use_pkce"] = pair.second.use_pkce;

        Json::Value scopes(Json::arrayValue);
        for (const auto& scope : pair.second.scopes) {
            scopes.append(scope);
        }
        profile["scopes"] = scopes;
        root[pair.first] = profile;
    }

    configFile << root;
    return true;
}

OAuthConfig ConfigManager::getConfiguration(const std::string& profileName) {
    if (configurations.count(profileName)) {
        return configurations[profileName];
    }
    return OAuthConfig{}; // Return an empty config
}

std::vector<std::string> ConfigManager::getProfileNames() {
    std::vector<std::string> names;
    for (const auto& pair : configurations) {
        names.push_back(pair.first);
    }
    return names;
}

bool ConfigManager::saveConfiguration(const std::string& profileName, const OAuthConfig& config) {
    configurations[profileName] = config;
    return saveConfigurations();
}

bool ConfigManager::deleteConfiguration(const std::string& profileName) {
    if (configurations.erase(profileName) > 0) {
        return saveConfigurations();
    }
    return false;
}
