CXX = g++
CXXFLAGS = -std=c++17 -I../../src/c/include -I./cpp/util
BIN_DIR = bin

CARDS = cards/PackageIntegrity.cpp
BINS = $(patsubst cards/%.cpp, $(BIN_DIR)/%, $(CARDS))

all: $(BINS)

$(BIN_DIR)/%: cards/%.cpp
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $< -o $@

test: all
	@for bin in $(BINS); do SORREL_FACTS_DIR=facts ./$$bin; done

clean:
	rm -rf $(BIN_DIR)

.PHONY: all test clean
