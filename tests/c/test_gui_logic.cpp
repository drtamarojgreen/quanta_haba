#include "simple_test_framework.h"
#include "HabaParser.h"
#include "html_generator.h"

bool GuiLogicTest_PreviewTrigger() {
    // Tests that the logic used to trigger previews (parsing + generation) works
    HabaParser parser;
    std::string input = "<content_layer>GUI Test</content_layer>";
    HabaData data = parser.parse(input);
    std::string html = generateHtml(data);

    ASSERT_TRUE(html.find("GUI Test") != std::string::npos);
    return true;
}

// Register tests
struct GuiLogicRegistrar {
    GuiLogicRegistrar() {
        add_test_case("GuiLogicTest_PreviewTrigger", GuiLogicTest_PreviewTrigger);
    }
};

static GuiLogicRegistrar gui_logic_registrar;
