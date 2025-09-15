#!/bin/bash
# Sync Cava colors with current Omarchy theme

SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR"

# Run the Python script
python3 update-colors.py

# Cava will automatically pick up the config changes
echo "Colors updated - cava will refresh automatically"