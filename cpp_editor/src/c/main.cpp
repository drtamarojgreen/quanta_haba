#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include "HabaParser.h"
#include "HabaData.h"
#include <string>
#include <vector>
#include <sstream>
#include "HabaParser.h"

void print_usage() {
    std::cout << "Usage: haba_editor <file_path>" << std::endl;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        print_usage();
        return 1;
    }

    std::string file_path = argv[1];
    std::ifstream file(file_path);

    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << file_path << std::endl;
        return 1;
    }

    std::string raw_text((std::istreambuf_iterator<char>(file)),
                         std::istreambuf_iterator<char>());

    HabaParser parser;
    HabaData data = parser.parse(raw_text);

    std::cout << "--- Parsed Haba Data ---" << std::endl;
    std::cout << "Content: " << data.content << std::endl;
    std::cout << "Presentation Items:" << std::endl;
    for (const auto& item : data.presentation_items) {
        std::cout << "  " << item.first << ": " << item.second << std::endl;
    }
    std::cout << "Script: " << data.script << std::endl;
}

// Function to generate the HTML from HabaData
std::string generateHtml(const HabaData& data) {
    std::stringstream html;

    // --- Start HTML structure ---
    html << "<!DOCTYPE html>\n";
    html << "<html lang=\"en\">\n";
    html << "<head>\n";
    html << "    <meta charset=\"UTF-8\">\n";
    html << "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n";
    html << "    <title>Haba Output</title>\n";

    // --- Add Styles ---
    // A simple approach: create a style tag and define styles for the containers.
    // This is a basic interpretation. A more robust solution might use classes.
    html << "    <style>\n";
    for (size_t i = 0; i < data.presentation_items.size(); ++i) {
        // This assumes container tags are simple element selectors like 'div', 'p', etc.
        // It might not work for complex container definitions with attributes.
        html << "        .haba-container-" << i << " " << data.presentation_items[i].second << "\n";
    }
    html << "    </style>\n";

    html << "</head>\n";
    html << "<body>\n\n";

    // --- Add Content ---
    // Wrap the content in the specified containers.
    // We'll nest the containers around the content.
    std::string content_with_containers = data.content;
    for (int i = data.presentation_items.size() - 1; i >= 0; --i) {
        std::stringstream temp_stream;
        // This is a naive way to inject a class. It assumes the container is a simple tag.
        // e.g., "<div>" becomes "<div class='haba-container-0'>"
        std::string container_tag = data.presentation_items[i].first;
        size_t first_space = container_tag.find('>');
        if (first_space != std::string::npos) {
            container_tag.insert(first_space, " class=\"haba-container-" + std::to_string(i) + "\"");
        }

        temp_stream << container_tag << "\n" << content_with_containers << "\n";

        // Generate closing tag, e.g., from "<div>" get "</div>"
        size_t tag_name_start = container_tag.find('<') + 1;
        size_t tag_name_end = container_tag.find_first_of(" >");
        std::string tag_name = container_tag.substr(tag_name_start, tag_name_end - tag_name_start);
        temp_stream << "</" << tag_name << ">";

        content_with_containers = temp_stream.str();
    }
    html << content_with_containers << "\n\n";

    // --- Add Script ---
    if (!data.script.empty()) {
        html << "<script>\n" << data.script << "\n</script>\n";
    }

    html << "</body>\n";
    html << "</html>\n";

    return html.str();
}


int main(int argc, char *argv[]) {
    // 1. Check arguments
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <input_file.haba>" << std::endl;
        return 1;
    }

    // 2. Read input file
    std::string input_path = argv[1];
    std::ifstream input_file(input_path);
    if (!input_file) {
        std::cerr << "Error: Cannot open input file '" << input_path << "'" << std::endl;
        return 1;
    }
    std::stringstream buffer;
    buffer << input_file.rdbuf();
    std::string file_content = buffer.str();
    input_file.close();

    // 3. Parse the content
    HabaParser parser;
    HabaData data = parser.parse(file_content);

    // 4. Generate HTML
    std::string html_content = generateHtml(data);

    // 5. Determine output path and write file
    std::string output_path = input_path;
    size_t dot_pos = output_path.rfind('.');
    if (dot_pos != std::string::npos) {
        output_path.replace(dot_pos, std::string::npos, ".html");
    } else {
        output_path += ".html";
    }

    std::ofstream output_file(output_path);
    if (!output_file) {
        std::cerr << "Error: Cannot open output file '" << output_path << "'" << std::endl;
        return 1;
    }
    output_file << html_content;
    output_file.close();

    // 6. Print success message
    std::cout << "Successfully converted '" << input_path << "' to '" << output_path << "'" << std::endl;

    return 0;
}
