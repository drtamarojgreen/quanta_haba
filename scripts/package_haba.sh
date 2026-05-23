#!/bin/bash
set -e

# Configuration
VERSION="1.0.0"
PACKAGE_NAME="quanta-haba-${VERSION}"
DIST_DIR="dist"
BUILD_DIR="build/package"

echo "📦 Packaging QuantaHaba v${VERSION}..."

# 1. Clean up old build artifacts
rm -rf "${DIST_DIR}"
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
mkdir -p "${DIST_DIR}"

# 2. Copy Python source
echo "  > Copying Python source..."
cp -r src/p/* "${BUILD_DIR}/"

# 3. Copy C++ binaries
echo "  > Copying C++ binaries..."
if [ -f "src/c/build/haba-converter" ]; then
    cp "src/c/build/haba-converter" "${BUILD_DIR}/"
else
    echo "  ⚠️ Warning: haba-converter binary not found in src/c/build/. Make sure to build C++ components first."
fi

# 4. Copy configurations and documentation
echo "  > Copying assets and docs..."
cp -r configuration "${BUILD_DIR}/" || echo "  ⚠️ Warning: configuration directory not found."
cp README.md "${BUILD_DIR}/"
cp LICENSE "${BUILD_DIR}/" || echo "  ⚠️ Warning: LICENSE file not found."

# 5. Create archive
echo "  > Creating distribution archive..."
# Use absolute path for tar to avoid confusion with relative paths after cd
ABS_DIST_DIR="$(pwd)/${DIST_DIR}"
mkdir -p "${ABS_DIST_DIR}"
cd build
tar -czf "${ABS_DIST_DIR}/${PACKAGE_NAME}.tar.gz" package/
cd ..

echo "✅ Packaging complete: ${DIST_DIR}/${PACKAGE_NAME}.tar.gz"
