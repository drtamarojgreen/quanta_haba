#include "html_generator.h"
#include "HabaData.h"
#include <string>
#include <sstream>
#include <vector>

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
