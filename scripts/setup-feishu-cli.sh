#!/usr/bin/env bash
# Install Feishu/Lark CLI for Claude Code web sessions.
# Called automatically by the SessionStart hook.
set -euo pipefail

BINARY="lark-cli"
INSTALL_DIR="/usr/local/bin"
REPO_URL="https://github.com/larksuite/cli.git"
CLONE_DIR="/tmp/lark-cli-src"

# Skip if already installed
if command -v "$BINARY" &>/dev/null; then
  echo "feishu-cli: already installed ($(lark-cli --version 2>&1 | tail -1))"
  exit 0
fi

echo "feishu-cli: installing from source..."

# Clone repo
rm -rf "$CLONE_DIR"
git clone --depth 1 "$REPO_URL" "$CLONE_DIR" 2>&1

# Create minimal meta_data.json (fetched at runtime instead)
mkdir -p "$CLONE_DIR/internal/registry"
echo '{}' > "$CLONE_DIR/internal/registry/meta_data.json"

# Build
cd "$CLONE_DIR"
VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo dev)
go build -trimpath \
  -ldflags "-s -w -X github.com/larksuite/cli/internal/build.Version=$VERSION -X github.com/larksuite/cli/internal/build.Date=$(date +%Y-%m-%d)" \
  -o "$BINARY" .

# Install binary
install -d "$INSTALL_DIR"
install -m755 "$BINARY" "$INSTALL_DIR/$BINARY"

echo "feishu-cli: installed $VERSION to $INSTALL_DIR/$BINARY"

# Install skills (non-blocking; if npx is available)
if command -v npx &>/dev/null; then
  echo "feishu-cli: installing skills..."
  npx skills add larksuite/cli -y -g 2>&1 || echo "feishu-cli: skills install failed (non-fatal)"
fi

# Cleanup
rm -rf "$CLONE_DIR"
echo "feishu-cli: setup complete"
