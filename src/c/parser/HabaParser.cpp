#include "HabaParser.h"
#include "StringUtils.h"
#include <regex>
#include <sstream>
#include <vector>

namespace {
// Helper function to trim leading/trailing whitespace from a string
std::string trim(const std::string& str) {
    const std::string whitespace = " \t\n\r\f\v";
    size_t first = str.find_first_not_of(whitespace);
    if (std::string::npos == first) {
        return str;
    }
    size_t last = str.find_last_not_of(whitespace);
    return str.substr(first, (last - first + 1));
}

// Helper function to split a string by a delimiter
std::vector<std::string> split(const std::string& str, char delimiter) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(str);
    while (std::getline(tokenStream, token, delimiter)) {
        tokens.push_back(token);
    }
    return tokens;
}
}

HabaData HabaParser::parse(const std::string& raw_text) {
    HabaData data;
    std::smatch match;

    // Extract content layer
    std::regex content_regex("<content_layer>([\\s\\S]*?)</content_layer>", std::regex::ECMAScript | std::regex::multiline);
    if (std::regex_search(raw_text, match, content_regex) && match.size() > 1) {
        data.content = trim(match[1].str());
    }

    // Extract presentation layer
    std::regex presentation_regex("<presentation_layer>([\\s\\S]*?)</presentation_layer>", std::regex::ECMAScript | std::regex::multiline);
    if (std::regex_search(raw_text, match, presentation_regex) && match.size() > 1) {
        std::string presentation_text = match[1].str();

        // Extract containers
        std::smatch containers_match;
        std::regex containers_regex("<containers>([\\s\\S]*?)</containers>", std::regex::ECMAScript | std::regex::multiline);
        std::vector<std::string> containers;
        if (std::regex_search(presentation_text, containers_match, containers_regex) && containers_match.size() > 1) {
            std::string containers_block = trim(containers_match[1].str());
            auto lines = split(containers_block, '\n');
            for(const auto& line : lines) {
                std::string trimmed_line = trim(line);
                if (!trimmed_line.empty()) {
                    containers.push_back(trimmed_line);
                }
            }
        }

        // Extract styles
        std::smatch styles_match;
        std::regex styles_regex("<styles>([\\s\\S]*?)</styles>", std::regex::ECMAScript | std::regex::multiline);
        std::vector<std::string> styles;
        if (std::regex_search(presentation_text, styles_match, styles_regex) && styles_match.size() > 1) {
            std::string styles_block = trim(styles_match[1].str());
            auto lines = split(styles_block, '\n');
            for(const auto& line : lines) {
                std::string trimmed_line = trim(line);
                if (!trimmed_line.empty()) {
                    styles.push_back(trimmed_line);
                }
            }
        }

        // Match containers and styles by order
        for (size_t i = 0; i < containers.size(); ++i) {
            std::string style = (i < styles.size()) ? styles[i] : "";
            data.presentation_items.emplace_back(containers[i], style);
        }
    }

    // Extract script layer
    std::regex script_regex("<script_layer>([\\s\\S]*?)</script_layer>", std::regex::ECMAScript | std::regex::multiline);
    if (std::regex_search(raw_text, match, script_regex) && match.size() > 1) {
        data.script = trim(match[1].str());
    }

    // Extract to_do layer
    std::regex todo_regex("<to_do>([\\s\\S]*?)</to_do>", std::regex::ECMAScript | std::regex::multiline);
    if (std::regex_search(raw_text, match, todo_regex) && match.size() > 1) {
        data.to_do = trim(match[1].str());
    }

    return data;
}

std::string HabaParser::build(const HabaData& haba_data) {
    std::stringstream ss;

    // Build content layer
    ss << "<content_layer>\n    " << haba_data.content << "\n</content_layer>\n";

    // Build presentation layer
    ss << "<presentation_layer>\n";
    ss << "    <containers>\n";
    for (const auto& item : haba_data.presentation_items) {
        ss << "        " << item.first << "\n";
    }
    ss << "    </containers>\n";
    ss << "    <styles>\n";
    for (const auto& item : haba_data.presentation_items) {
        ss << "        " << item.second << "\n";
    }
    ss << "    </styles>\n";
    ss << "</presentation_layer>";

    // Build script layer
    if (!haba_data.script.empty()) {
        ss << "\n<script_layer>\n    " << haba_data.script << "\n</script_layer>";
    }

    // Build to_do layer
    if (!haba_data.to_do.empty()) {
        ss << "\n<to_do>\n    " << haba_data.to_do << "\n</to_do>";
    }

    return ss.str();
}

std::string HabaParser::toJson(const HabaData& data) {
    std::stringstream ss;
    ss << "{\n";
    ss << "  \"content_layer\": \"" << StringUtils::escapeJson(data.content) << "\",\n";
    ss << "  \"presentation_layer\": {\n";
    ss << "    \"containers\": [";
    for (size_t i = 0; i < data.presentation_items.size(); ++i) {
        ss << "\"" << StringUtils::escapeJson(data.presentation_items[i].first) << "\"" << (i < data.presentation_items.size() - 1 ? ", " : "");
    }
    ss << "],\n";
    ss << "    \"styles\": [";
    for (size_t i = 0; i < data.presentation_items.size(); ++i) {
        ss << "\"" << StringUtils::escapeJson(data.presentation_items[i].second) << "\"" << (i < data.presentation_items.size() - 1 ? ", " : "");
    }
    ss << "]\n";
    ss << "  },\n";
    ss << "  \"script_layer\": \"" << StringUtils::escapeJson(data.script) << "\",\n";
    ss << "  \"to_do\": \"" << StringUtils::escapeJson(data.to_do) << "\"\n";
    ss << "}";
    return ss.str();
}

HabaData HabaParser::fromJson(const std::string& json_str) {
    HabaData data;
    auto extract = [&](const std::string& key) {
        std::string search = "\"" + key + "\": \"";
        size_t start = json_str.find(search);
        if (start == std::string::npos) return std::string("");
        start += search.length();
        // Finding the end quote while respecting escaped quotes
        size_t end = start;
        while (end < json_str.length()) {
            if (json_str[end] == '\"' && json_str[end-1] != '\\') break;
            end++;
        }
        return StringUtils::unescapeJson(json_str.substr(start, end - start));
    };

    data.content = extract("content_layer");
    data.script = extract("script_layer");
    data.to_do = extract("to_do");

    // Containers and Styles extraction
    size_t c_start = json_str.find("\"containers\": [");
    if (c_start != std::string::npos) {
        c_start += 15;
        size_t c_end = json_str.find("]", c_start);
        std::string c_block = json_str.substr(c_start, c_end - c_start);
        std::vector<std::string> containers;
        size_t pos = 0;
        while ((pos = c_block.find("\"", pos)) != std::string::npos) {
            size_t end = c_block.find("\"", pos + 1);
            containers.push_back(c_block.substr(pos + 1, end - pos - 1));
            pos = end + 1;
        }

        size_t s_start = json_str.find("\"styles\": [");
        if (s_start != std::string::npos) {
            s_start += 11;
            size_t s_end = json_str.find("]", s_start);
            std::string s_block = json_str.substr(s_start, s_end - s_start);
            std::vector<std::string> styles;
            pos = 0;
            while ((pos = s_block.find("\"", pos)) != std::string::npos) {
                size_t end = s_block.find("\"", pos + 1);
                styles.push_back(s_block.substr(pos + 1, end - pos - 1));
                pos = end + 1;
            }

            for (size_t i = 0; i < containers.size(); ++i) {
                data.presentation_items.push_back({containers[i], (i < styles.size() ? styles[i] : "")});
            }
        }
    }

    return data;
}
