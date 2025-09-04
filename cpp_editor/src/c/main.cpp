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
#include "html_generator.h"


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
