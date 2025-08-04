#!/bin/bash

# Improved development server for Pantheon Agents documentation
# with better file watching and automatic rebuilding

echo "🚀 Starting Improved Pantheon Docs Dev Server..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the docs directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: Please run this script from the docs directory${NC}"
    exit 1
fi

# Install watchdog if not already installed
echo "📦 Checking dependencies..."
pip install -q watchdog sphinx-autobuild

# Configuration
HOST="${DOC_HOST:-127.0.0.1}"
PORT="${DOC_PORT:-8080}"

echo -e "${BLUE}Configuration:${NC}"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo ""

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build 2>/dev/null || true

# Initial build
echo "🔨 Initial build..."
sphinx-build -b html source build/html

echo -e "${GREEN}✨ Documentation server starting...${NC}"
echo -e "${GREEN}📍 URL: http://$HOST:$PORT${NC}"
echo ""
echo "Features:"
echo "  • Live reload on file changes"
echo "  • Watches all .rst, .md, .py files"
echo "  • Minimal rebuild delay"
echo "  • Better error handling"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run sphinx-autobuild with improved options
sphinx-autobuild \
    --host "$HOST" \
    --port "$PORT" \
    --delay 0 \
    --watch source \
    --watch ../pantheon \
    --ignore "*.pyc" \
    --ignore "*.pyo" \
    --ignore "__pycache__" \
    --ignore ".git" \
    --ignore "build" \
    --ignore "*.swp" \
    --ignore "*~" \
    --ignore ".DS_Store" \
    --re-ignore ".*\.#.*" \
    --re-ignore ".*~$" \
    --open-browser \
    source build/html