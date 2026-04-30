CXX = g++
CXXFLAGS = -std=c++17 -I../../../src/c/include -I../cpp/util
LDFLAGS =

# Source files for HabaParser
HABA_SRCS = ../../../src/c/source/HabaParser.cpp

# CDD Cards
CARDS = cards/HabaParserClass.cpp

BIN_DIR = bin
BINS = $(patsubst cards/%.cpp, $(BIN_DIR)/%, $(CARDS))

# Optional facts directory
FACTS_DIR ?= facts

all: $(BINS)

$(BIN_DIR)/HabaParserClass: cards/HabaParserClass.cpp
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $< $(HABA_SRCS) -o $@ $(LDFLAGS)

clean:
	rm -rf $(BIN_DIR)

test: all
	@echo "Running Haba CDD Tests with CHAI_FACTS_DIR=$(FACTS_DIR)..."
	@for bin in $(BINS); do \
		echo "Executing $$bin..."; \
		CHAI_FACTS_DIR=$(FACTS_DIR) ./$$bin; \
	done

.PHONY: all clean test
