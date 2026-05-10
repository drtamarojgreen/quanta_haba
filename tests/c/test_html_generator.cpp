#include "simple_test_framework.h"
#include "HabaData.h"
#include <string>
#include <vector>

// Forward declaration of the function to be tested
std::string generateHtml(const HabaData& data);

bool HtmlGeneratorTest_BasicConversion() {
    HabaData data;
    data.content = "Greenhouse Growth";
    data.presentation_items.push_back({"<div>", "{ color: 'green' }"});
    data.script = "console.log('Sprout');";

    std::string html = generateHtml(data);

    ASSERT_TRUE(html.find("<!DOCTYPE html>") != std::string::npos);
    ASSERT_TRUE(html.find("Greenhouse Growth") != std::string::npos);
    ASSERT_TRUE(html.find(".haba-container-0 { color: 'green' }") != std::string::npos);
    ASSERT_TRUE(html.find("<div class=\"haba-container-0\">") != std::string::npos);
    ASSERT_TRUE(html.find("console.log('Sprout');") != std::string::npos);
    return true;
}

bool HtmlGeneratorTest_MultipleContainers() {
    HabaData data;
    data.content = "Nested Content";
    data.presentation_items.push_back({"<section>", "{ padding: '10px' }"});
    data.presentation_items.push_back({"<article>", "{ margin: '5px' }"});

    std::string html = generateHtml(data);

    ASSERT_TRUE(html.find("<section class=\"haba-container-0\">") != std::string::npos);
    ASSERT_TRUE(html.find("<article class=\"haba-container-1\">") != std::string::npos);
    // Check nesting order: article should be inside section
    size_t section_pos = html.find("<section");
    size_t article_pos = html.find("<article");
    ASSERT_TRUE(section_pos < article_pos);
    return true;
}

// Register tests
struct HtmlGeneratorRegistrar {
    HtmlGeneratorRegistrar() {
        add_test_case("HtmlGeneratorTest_BasicConversion", HtmlGeneratorTest_BasicConversion);
        add_test_case("HtmlGeneratorTest_MultipleContainers", HtmlGeneratorTest_MultipleContainers);
    }
};

static HtmlGeneratorRegistrar html_gen_registrar;
