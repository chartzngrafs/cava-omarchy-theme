#!/bin/bash
# Automatic Cava Theme Monitor using inotifywait
# Watches for Omarchy theme changes and automatically updates Cava colors.

OMARCHY_DIR="$HOME/.config/omarchy"
CAVA_DIR="$HOME/.config/cava"
LOG_FILE="$CAVA_DIR/theme-monitor.log"
UPDATE_SCRIPT="$CAVA_DIR/update-colors.py"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to update cava colors
update_cava() {
    log "Theme change detected, updating Cava colors..."
    cd "$CAVA_DIR"

    if python3 "$UPDATE_SCRIPT" >> "$LOG_FILE" 2>&1; then
        log "Cava colors updated successfully"

        # Cava requires manual reload (press 'c') or restart to pick up color changes
        # Try signal first, fall back to gentle restart if user prefers automatic updates
        if pgrep -x "cava" > /dev/null; then
            # Try SIGUSR1 signal (may not work on all versions)
            pkill -SIGUSR1 cava 2>/dev/null || true
            log "Config updated - press 'c' in cava to reload colors, or restart cava to see changes"
        fi
    else
        log "Failed to update Cava colors"
    fi
}

# Check if required files exist
if [ ! -d "$OMARCHY_DIR" ]; then
    log "ERROR: Omarchy config directory not found: $OMARCHY_DIR"
    exit 1
fi

if [ ! -f "$UPDATE_SCRIPT" ]; then
    log "ERROR: Update script not found: $UPDATE_SCRIPT"
    exit 1
fi

# Create log file if it doesn't exist
touch "$LOG_FILE"

log "Starting Cava theme monitor..."
log "Watching: $OMARCHY_DIR/current/"

# Run initial update
update_cava

# Monitor for changes to the current theme
inotifywait -m -e modify,create,delete,move "$OMARCHY_DIR/current/" --format '%w%f %e' 2>/dev/null | while read file event; do
    # Check if the theme symlink changed
    if [[ "$file" == *"theme"* ]] || [[ "$event" == *"CREATE"* ]] || [[ "$event" == *"MODIFY"* ]]; then
        # Add a small delay to avoid rapid successive updates
        sleep 0.5
        update_cava
    fi
done