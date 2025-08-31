#include "simple_test_framework.h"
#include "HabaParser.h"
#include "HabaData.h"

bool HabaParserTest_BasicParsing() {
    HabaParser parser;
    std::string raw_text = "content: Hello\npresentation: div { color: 'blue' }\nscript: console.log('test');";
    HabaData data = parser.parse(raw_text);

    ASSERT_EQ(data.content, "Hello");
    ASSERT_EQ(data.presentation_items.size(), 1);
    ASSERT_EQ(data.presentation_items[0].first, "div");
    ASSERT_EQ(data.presentation_items[0].second, "{ color: 'blue' }");
    ASSERT_EQ(data.script, "console.log('test');");
    return true;
}

// Register tests
struct TestRegistrar {
    TestRegistrar() {
        add_test_case("HabaParserTest_BasicParsing", HabaParserTest_BasicParsing);
    }
};

static TestRegistrar registrar_instance;

int main(int argc, char **argv) {
    return run_all_tests();
}