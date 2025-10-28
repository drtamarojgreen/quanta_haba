#include "simple_test_framework.h"
#include "HabaParser.h"
#include "HabaData.h"

bool HabaParserTest_FullFile() {
    HabaParser parser;
    std::string raw_text =
        "<content_layer>\n"
        "    Hello World\n"
        "</content_layer>\n"
        "<presentation_layer>\n"
        "    <containers>\n"
        "        div\n"
        "        p\n"
        "    </containers>\n"
        "    <styles>\n"
        "        { color: 'blue' }\n"
        "        { font-size: 16px }\n"
        "    </styles>\n"
        "</presentation_layer>\n"
        "<script_layer>\n"
        "    console.log('init');\n"
        "</script_layer>";
    HabaData data = parser.parse(raw_text);

    ASSERT_EQ(std::string("Hello World"), data.content);
    ASSERT_EQ(size_t(2), data.presentation_items.size());
    ASSERT_EQ(std::string("div"), data.presentation_items[0].first);
    ASSERT_EQ(std::string("{ color: 'blue' }"), data.presentation_items[0].second);
    ASSERT_EQ(std::string("p"), data.presentation_items[1].first);
    ASSERT_EQ(std::string("{ font-size: 16px }"), data.presentation_items[1].second);
    ASSERT_EQ(std::string("console.log('init');"), data.script);
    return true;
}

bool HabaParserTest_MissingScriptLayer() {
    HabaParser parser;
    std::string raw_text =
        "<content_layer>Just content</content_layer>\n"
        "<presentation_layer></presentation_layer>";
    HabaData data = parser.parse(raw_text);
    ASSERT_EQ(std::string("Just content"), data.content);
    ASSERT_EQ(size_t(0), data.presentation_items.size());
    ASSERT_EQ(std::string(""), data.script);
    return true;
}

bool HabaParserTest_MissingContentLayer() {
    HabaParser parser;
    std::string raw_text = "<presentation_layer></presentation_layer>";
    HabaData data = parser.parse(raw_text);
    ASSERT_EQ(std::string(""), data.content);
    return true;
}

bool HabaParserTest_EmptyInput() {
    HabaParser parser;
    HabaData data = parser.parse("");
    ASSERT_EQ(std::string(""), data.content);
    ASSERT_EQ(size_t(0), data.presentation_items.size());
    ASSERT_EQ(std::string(""), data.script);
    return true;
}

// Register tests
struct TestRegistrar {
    TestRegistrar() {
        add_test_case("HabaParserTest_FullFile", HabaParserTest_FullFile);
        add_test_case("HabaParserTest_MissingScriptLayer", HabaParserTest_MissingScriptLayer);
        add_test_case("HabaParserTest_MissingContentLayer", HabaParserTest_MissingContentLayer);
        add_test_case("HabaParserTest_EmptyInput", HabaParserTest_EmptyInput);
    }
};

static TestRegistrar registrar_instance;

int main(int argc, char **argv) {
    return run_all_tests();
}
