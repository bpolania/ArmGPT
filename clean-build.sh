#!/bin/bash

# Clean build script - remove logs, clean, and rebuild with logging
echo "🗑️  Removing old build log..."
rm -f build.log

echo "🧹 Cleaning build artifacts..."
make clean

echo "🔨 Building with logging..."
make build-log

echo "✅ Clean build completed!"

if [ -f build.log ]; then
    echo "📋 Build log created:"
    echo "   - Check 'build.log' for details"
    if grep -q "Error:" build.log; then
        echo "❌ Build errors found in log"
    else
        echo "✅ Build appears successful"
    fi
fi