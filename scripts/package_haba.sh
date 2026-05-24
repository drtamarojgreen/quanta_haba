#!/bin/bash
set -e
VERSION="1.0.0"
PACKAGE_NAME="quanta-haba-${VERSION}"
DIST_DIR="dist"
BUILD_DIR="build/package"
echo "📦 Packaging QuantaHaba v${VERSION}..."
rm -rf "${DIST_DIR}" "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}" "${DIST_DIR}"
echo "  > Copying Python source..."
cp -r src/p/* "${BUILD_DIR}/"
echo "  > Copying C++ binaries..."
if [ -f "src/c/build/haba-converter" ]; then
    cp "src/c/build/haba-converter" "${BUILD_DIR}/"
fi
echo "  > Copying assets and docs..."
if [ -d "configuration" ]; then
    cp -r configuration "${BUILD_DIR}/"
fi
cp README.md "${BUILD_DIR}/"
if [ -f "LICENSE" ]; then
    cp LICENSE "${BUILD_DIR}/"
fi
echo "  > Creating distribution archive..."
# Use absolute path for tar to avoid relative path confusion
ABS_DIST_DIR="$(pwd)/${DIST_DIR}"
cd build
tar -czf "${ABS_DIST_DIR}/${PACKAGE_NAME}.tar.gz" package/
cd ..
echo "✅ Packaging complete: ${DIST_DIR}/${PACKAGE_NAME}.tar.gz"
