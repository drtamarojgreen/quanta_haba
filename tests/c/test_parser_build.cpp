#include "simple_test_framework.h"
#include "HabaParser.h"
#include "HabaData.h"

bool HabaParserTest_BuildRoundtrip() {
    HabaParser parser;
    HabaData data;
    data.content = "Roundtrip Test";
    data.presentation_items.push_back({"<div>", "{ color: 'red' }"});
    data.script = "console.log('roundtrip');";

    std::string rebuilt = parser.build(data);
    HabaData reparsed = parser.parse(rebuilt);

    ASSERT_EQ(data.content, reparsed.content);
    ASSERT_EQ(data.presentation_items.size(), reparsed.presentation_items.size());
    ASSERT_EQ(data.presentation_items[0].first, reparsed.presentation_items[0].first);
    ASSERT_EQ(data.presentation_items[0].second, reparsed.presentation_items[0].second);
    ASSERT_EQ(data.script, reparsed.script);
    return true;
}

// Register tests
struct ParserBuildRegistrar {
    ParserBuildRegistrar() {
        add_test_case("HabaParserTest_BuildRoundtrip", HabaParserTest_BuildRoundtrip);
    }
};

static ParserBuildRegistrar parser_build_registrar;
