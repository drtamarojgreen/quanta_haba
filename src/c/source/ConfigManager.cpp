#include "../include/ConfigManager.h"
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <sys/stat.h>

#ifdef _WIN32
#include <shlobj.h>
#endif

// Anonymous namespace for helper functions
namespace {
    // Helper to extract a string value for a given key from a JSON object block.
    // Assumes the value is on the same line and enclosed in quotes.
    std::string extractJsonString(const std::string& block, const std::string& key) {
        std::string search_key = "\"" + key + "\": \"";
        size_t start_pos = block.find(search_key);
        if (start_pos == std::string::npos) return "";
        start_pos += search_key.length();
        size_t end_pos = block.find("\"", start_pos);
        if (end_pos == std::string::npos) return "";
        return block.substr(start_pos, end_pos - start_pos);
    }

    // Helper to extract a boolean value.
    bool extractJsonBool(const std::string& block, const std::string& key) {
        std::string search_key = "\"" + key + "\": ";
        size_t start_pos = block.find(search_key);
        if (start_pos == std::string::npos) return false;
        start_pos += search_key.length();
        return block.substr(start_pos, 4) == "true";
    }

    // Helper to extract a string array for scopes.
    std::vector<std::string> extractJsonScopes(const std::string& block) {
        std::vector<std::string> scopes;
        std::string search_key = "\"scopes\": [";
        size_t start_pos = block.find(search_key);
        if (start_pos == std::string::npos) return scopes;
        start_pos += search_key.length();
        size_t end_pos = block.find("]", start_pos);
        if (end_pos == std::string::npos) return scopes;

        std::string scope_block = block.substr(start_pos, end_pos - start_pos);
        size_t current_pos = 0;
        while(current_pos < scope_block.length()) {
            size_t scope_start = scope_block.find('"', current_pos);
            if (scope_start == std::string::npos) break;
            scope_start++;
            size_t scope_end = scope_block.find('"', scope_start);
            if (scope_end == std::string::npos) break;
            scopes.push_back(scope_block.substr(scope_start, scope_end - scope_start));
            current_pos = scope_end + 1;
        }
        return scopes;
    }
}

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
        return false;
    }

    std::string content((std::istreambuf_iterator<char>(configFile)), std::istreambuf_iterator<char>());
    configurations.clear();

    size_t current_pos = 0;
    while(true) {
        size_t profile_key_start = content.find('"', current_pos);
        if (profile_key_start == std::string::npos) break;
        profile_key_start++;
        size_t profile_key_end = content.find('"', profile_key_start);
        if (profile_key_end == std::string::npos) break;

        std::string profileName = content.substr(profile_key_start, profile_key_end - profile_key_start);

        size_t block_start = content.find('{', profile_key_end);
        if (block_start == std::string::npos) break;

        // Find the matching closing brace for this profile
        int brace_level = 1;
        size_t block_end = block_start + 1;
        while(block_end < content.length() && brace_level > 0) {
            if (content[block_end] == '{') brace_level++;
            if (content[block_end] == '}') brace_level--;
            block_end++;
        }
        if (brace_level != 0) break; // Malformed JSON

        std::string profile_block = content.substr(block_start, block_end - block_start);

        OAuthConfig config;
        config.provider_name = extractJsonString(profile_block, "provider_name");
        config.client_id = extractJsonString(profile_block, "client_id");
        config.client_secret = extractJsonString(profile_block, "client_secret");
        config.authorization_url = extractJsonString(profile_block, "authorization_url");
        config.token_url = extractJsonString(profile_block, "token_url");
        config.api_base_url = extractJsonString(profile_block, "api_base_url");
        config.redirect_uri = extractJsonString(profile_block, "redirect_uri");
        config.use_pkce = extractJsonBool(profile_block, "use_pkce");
        config.scopes = extractJsonScopes(profile_block);

        configurations[profileName] = config;
        current_pos = block_end;
    }
    return true;
}

bool ConfigManager::saveConfigurations() {
    std::string filePath = getConfigFilePath();
    std::ofstream configFile(filePath);
    if (!configFile.is_open()) {
        return false;
    }

    configFile << "{\n";
    bool firstProfile = true;
    for (const auto& pair : configurations) {
        if (!firstProfile) {
            configFile << ",\n";
        }
        configFile << "  \"" << pair.first << "\": {\n";
        configFile << "    \"provider_name\": \"" << pair.second.provider_name << "\",\n";
        configFile << "    \"client_id\": \"" << pair.second.client_id << "\",\n";
        configFile << "    \"client_secret\": \"" << pair.second.client_secret << "\",\n";
        configFile << "    \"authorization_url\": \"" << pair.second.authorization_url << "\",\n";
        configFile << "    \"token_url\": \"" << pair.second.token_url << "\",\n";
        configFile << "    \"api_base_url\": \"" << pair.second.api_base_url << "\",\n";
        configFile << "    \"redirect_uri\": \"" << pair.second.redirect_uri << "\",\n";
        configFile << "    \"use_pkce\": " << (pair.second.use_pkce ? "true" : "false") << ",\n";
        configFile << "    \"scopes\": [";
        bool firstScope = true;
        for (const auto& scope : pair.second.scopes) {
            if (!firstScope) {
                configFile << ", ";
            }
            configFile << "\"" << scope << "\"";
            firstScope = false;
        }
        configFile << "]\n";
        configFile << "  }";
        firstProfile = false;
    }
    configFile << "\n}\n";
    return true;
}

OAuthConfig ConfigManager::getConfiguration(const std::string& profileName) {
    if (configurations.count(profileName)) {
        return configurations[profileName];
    }
    return OAuthConfig{};
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
