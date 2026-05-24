CXX = g++
CXXFLAGS = -std=c++17 -I../../src/c/include -I./cpp/util
BIN_DIR = bin

CARDS = $(wildcard cards/*.cpp)
BINS = $(patsubst cards/%.cpp, $(BIN_DIR)/%, $(CARDS))

all: $(BINS)

$(BIN_DIR)/%: cards/%.cpp
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $< -o $@

test: all
	@for bin in $(BINS); do 		if [[ $$bin == *"PackagingAudit"* ]]; then 			SORREL_FACTS_DIR=facts ./$$bin packaging_audit; 		else 			SORREL_FACTS_DIR=facts ./$$bin; 		fi 	done

clean:
	rm -rf $(BIN_DIR)

.PHONY: all test clean
