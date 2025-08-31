#include "HabaParser.h"
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
    std::regex content_regex("<content_layer>(.*?)</content_layer>", std::regex::ECMAScript | std::regex::multiline);
    if (std::regex_search(raw_text, match, content_regex) && match.size() > 1) {
        data.content = trim(match[1].str());
    }

    // Extract presentation layer
    std::regex presentation_regex("<presentation_layer>(.*?)</presentation_layer>", std::regex::ECMAScript | std::regex::multiline);
    if (std::regex_search(raw_text, match, presentation_regex) && match.size() > 1) {
        std::string presentation_text = match[1].str();

        // Extract containers
        std::smatch containers_match;
        std::regex containers_regex("<containers>(.*?)</containers>", std::regex::ECMAScript | std::regex::multiline);
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
        std::regex styles_regex("<styles>(.*?)</styles>", std::regex::ECMAScript | std::regex::multiline);
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
    std::regex script_regex("<script_layer>(.*?)</script_layer>", std::regex::ECMAScript | std::regex::multiline);
    if (std::regex_search(raw_text, match, script_regex) && match.size() > 1) {
        data.script = trim(match[1].str());
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

    return ss.str();
}
