#!/bin/bash

# Helper script to run auto_build.py with appropriate settings

echo "🔍 Detecting environment..."

# Check if we're in Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Docker environment detected"
    export USE_POLLING_OBSERVER=1
fi

# Check if we're in WSL
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "🪟 WSL environment detected"
    export USE_POLLING_OBSERVER=1
fi

# Check if we're on a network filesystem
if df . | grep -E '(nfs|cifs|smb)' >/dev/null 2>&1; then
    echo "🌐 Network filesystem detected"
    export USE_POLLING_OBSERVER=1
fi

# Check if user explicitly wants polling
if [ "$1" = "--polling" ] || [ "$1" = "-p" ]; then
    echo "✅ Forcing polling observer as requested"
    export FORCE_POLLING=1
fi

# Run the auto build script
echo "🚀 Starting auto-build..."
exec python auto_build.py