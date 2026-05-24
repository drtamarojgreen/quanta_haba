.PHONY: all build-cpp test-cpp test-p package clean

all: build-cpp test-cpp test-p

build-cpp:
	mkdir -p src/c/build
	cd src/c/build && cmake .. && cmake --build .

test-cpp: build-cpp
	cd src/c/build && ctest

test-p:
	python3 -m unittest discover -s tests/p

package: build-cpp
	bash scripts/package_haba.sh

clean:
	rm -rf src/c/build
	rm -rf dist/
	rm -rf build/
	rm -f src/p/*.egg-info
