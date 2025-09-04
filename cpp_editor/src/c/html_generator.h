#ifndef HTML_GENERATOR_H
#define HTML_GENERATOR_H

#include "HabaData.h"
#include <string>

/**
 * @brief Generates an HTML string from a HabaData object.
 * @param data The HabaData object containing the parsed data.
 * @return A string containing the full HTML document.
 */
std::string generateHtml(const HabaData& data);

#endif // HTML_GENERATOR_H
