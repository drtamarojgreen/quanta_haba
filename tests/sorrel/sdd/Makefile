CXX = g++
CXXFLAGS = -std=c++17 -I../../../src/c/include -I../cpp/util
LDFLAGS =

# Source files for C++ components
HABA_SRCS = ../../../src/c/source/HabaParser.cpp ../../../src/c/source/StringUtils.cpp
CONFIG_SRCS = ../../../src/c/source/ConfigManager.cpp ../../../src/c/source/StringUtils.cpp
ANALYZER_SRCS = ../../../src/c/source/ScriptAnalyzer.cpp
LOGIC_SRCS = ../../../src/c/source/EditorLogic.cpp

# SDD Cards
CARDS = cards/HabaParserClass.cpp \
        cards/ConfigManagerClass.cpp \
        cards/ScriptAnalyzerClass.cpp \
        cards/EditorLogicParity.cpp \
        cards/PythonHabaParserParity.cpp \
        cards/PythonConfigManagerParity.cpp \
        cards/PythonScriptAnalyzerParity.cpp \
        cards/PythonEditorLogicParity.cpp \
        cards/CliFeatureParity.cpp \
        cards/GuiFeatureParity.cpp \
        cards/PythonCliFeatureEvaluation.cpp \
        cards/PythonGuiFeatureEvaluation.cpp \
        cards/DeepCliFeatureParity.cpp \
        cards/DeepGuiFeatureParity.cpp \
        cards/DeepPythonCliEvaluation.cpp \
        cards/DeepPythonGuiEvaluation.cpp \
        cards/DeepPythonParserEvaluation.cpp

BIN_DIR = bin
BINS = $(patsubst cards/%.cpp, $(BIN_DIR)/%, $(CARDS))

# Optional facts directory
FACTS_DIR ?= facts

all: $(BINS)

$(BIN_DIR)/%: cards/%.cpp
	@mkdir -p $(BIN_DIR)
	@mkdir -p checkouts
	$(CXX) $(CXXFLAGS) $< $(filter-out $<, $(HABA_SRCS) $(CONFIG_SRCS) $(LOGIC_SRCS) $(ANALYZER_SRCS)) -o $@ $(LDFLAGS)

# Specific rules for cards with dependencies
$(BIN_DIR)/HabaParserClass: cards/HabaParserClass.cpp $(HABA_SRCS)
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) cards/HabaParserClass.cpp $(HABA_SRCS) -o $@ $(LDFLAGS)

$(BIN_DIR)/ConfigManagerClass: cards/ConfigManagerClass.cpp $(CONFIG_SRCS)
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) cards/ConfigManagerClass.cpp $(CONFIG_SRCS) -o $@ $(LDFLAGS)

$(BIN_DIR)/EditorLogicParity: cards/EditorLogicParity.cpp $(LOGIC_SRCS)
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) cards/EditorLogicParity.cpp $(LOGIC_SRCS) -o $@ $(LDFLAGS)

$(BIN_DIR)/ScriptAnalyzerClass: cards/ScriptAnalyzerClass.cpp $(ANALYZER_SRCS)
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) cards/ScriptAnalyzerClass.cpp $(ANALYZER_SRCS) -o $@ $(LDFLAGS)

clean:
	rm -rf $(BIN_DIR) checkouts

test: all
	@echo "Running Haba SDD Tests with SORREL_FACTS_DIR=$(FACTS_DIR)..."
	@rm -f checkouts/*.checkout
	@for bin in $(BINS); do \
		echo "Executing $$bin..."; \
		SORREL_FACTS_DIR=$(FACTS_DIR) ./$$bin; \
	done
	@echo "--- SDD Checkouts (Empirical Evidence) ---"
	@ls checkouts/*.checkout && cat checkouts/*.checkout

.PHONY: all clean test
