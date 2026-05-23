#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sys/stat.h>

bool fileExists(const std::string& name) {
    struct stat buffer;
    return (stat(name.c_str(), &buffer) == 0);
}

long getFileSize(const std::string& filename) {
    struct stat stat_buf;
    int rc = stat(filename.c_str(), &stat_buf);
    return rc == 0 ? stat_buf.st_size : -1;
}

/**
 * @Card: package_integrity_verification
 * @Results required_files_found (numeric), package_archive_size (numeric)
 */
int main(int argc, char** argv) {
    std::vector<std::string> required_files = {
        "build/package/editor.py",
        "build/package/haba_parser.py",
        "build/package/haba-converter",
        "build/package/configuration/model_config.json",
        "build/package/README.md"
    };

    int found_count = 0;
    for (const auto& file : required_files) {
        if (fileExists(file)) {
            found_count++;
        }
    }

    long archive_size = getFileSize("dist/quanta-haba-1.0.0.tar.gz");

    std::cout << "required_files_found = " << found_count << std::endl;
    std::cout << "package_archive_size = " << archive_size << std::endl;

    return 0;
}
