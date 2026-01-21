#!/bin/bash
# Installation script for smallstep CLI (step)
# This script downloads and installs the step CLI tool required for MFA with CINECA HPC

set -e

# Determine system architecture
ARCH=$(uname -m)
case "$ARCH" in
    x86_64)
        STEP_ARCH="amd64"
        ;;
    aarch64|arm64)
        STEP_ARCH="arm64"
        ;;
    armv7l)
        STEP_ARCH="armv7"
        ;;
    *)
        echo "Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

# Set version and download URL
STEP_VERSION="0.29.0"
STEP_URL="https://github.com/smallstep/cli/releases/download/v${STEP_VERSION}/step_linux_${STEP_VERSION}_${STEP_ARCH}.tar.gz"

echo "Installing smallstep CLI (step) version ${STEP_VERSION} for ${STEP_ARCH}..."

# Create temporary directory for download
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

# Download and extract
echo "Downloading from $STEP_URL..."
curl -L -o step.tar.gz "$STEP_URL"

echo "Extracting archive..."
tar -xzf step.tar.gz

# Install to /usr/local/bin (or ~/.local/bin if not root)
if [ -w /usr/local/bin ]; then
    INSTALL_DIR="/usr/local/bin"
else
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
fi

echo "Installing step to $INSTALL_DIR..."
cp "step_${STEP_VERSION}/bin/step" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/step"

# Clean up
cd /
rm -rf "$TMP_DIR"

# Verify installation
if command -v step &> /dev/null; then
    echo "✓ smallstep CLI installed successfully!"
    step version
else
    echo "Warning: step binary installed but not found in PATH"
    echo "You may need to add $INSTALL_DIR to your PATH"
fi
