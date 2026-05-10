#include "StringUtils.h"
#include <sstream>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#else
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace StringUtils {

std::string escapeJson(const std::string& input) {
    std::ostringstream ss;
    for (char c : input) {
        switch (c) {
            case '\"': ss << "\\\""; break;
            case '\\': ss << "\\\\"; break;
            case '\b': ss << "\\b"; break;
            case '\f': ss << "\\f"; break;
            case '\n': ss << "\\n"; break;
            case '\r': ss << "\\r"; break;
            case '\t': ss << "\\t"; break;
            default:
                if ('\x00' <= c && c <= '\x1f') {
                    ss << "\\u" << std::hex << (int)c;
                } else {
                    ss << c;
                }
        }
    }
    return ss.str();
}

std::string unescapeJson(const std::string& input) {
    std::string out;
    for (size_t i = 0; i < input.length(); ++i) {
        if (input[i] == '\\' && i + 1 < input.length()) {
            switch (input[++i]) {
                case '\"': out += '\"'; break;
                case '\\': out += '\\'; break;
                case 'b':  out += '\b'; break;
                case 'f':  out += '\f'; break;
                case 'n':  out += '\n'; break;
                case 'r':  out += '\r'; break;
                case 't':  out += '\t'; break;
                default:   out += input[i]; break;
            }
        } else {
            out += input[i];
        }
    }
    return out;
}

bool ensureDirectoryExists(const std::string& path) {
#ifdef _WIN32
    return CreateDirectoryA(path.c_str(), NULL) || ERROR_ALREADY_EXISTS == GetLastError();
#else
    return mkdir(path.c_str(), 0755) == 0 || errno == EEXIST;
#endif
}

}
