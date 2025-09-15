#!/bin/bash
# Test script to manually trigger cava color reload

echo "Testing cava reload approaches..."

if ! pgrep -x "cava" > /dev/null; then
    echo "❌ No cava process found. Please start cava first."
    exit 1
fi

echo "Found cava running. Testing reload methods:"

echo "1. Trying SIGUSR1 signal..."
pkill -SIGUSR1 cava 2>/dev/null && echo "   ✅ Signal sent" || echo "   ❌ Signal failed"

echo "2. Trying SIGHUP signal..."
pkill -SIGHUP cava 2>/dev/null && echo "   ✅ Signal sent" || echo "   ❌ Signal failed"

echo ""
echo "If neither method works, cava may need to be restarted to see color changes."
echo "You can press 'c' manually in cava to reload colors."