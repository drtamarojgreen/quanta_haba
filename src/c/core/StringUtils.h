#ifndef STRING_UTILS_H
#define STRING_UTILS_H

#include <string>

namespace StringUtils {
    std::string escapeJson(const std::string& input);
    std::string unescapeJson(const std::string& input);
    bool ensureDirectoryExists(const std::string& path);
}

#endif
