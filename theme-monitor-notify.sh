#!/bin/bash
# Cava Theme Monitor with Notification (No Restart)
# This version updates colors and notifies user instead of restarting

OMARCHY_DIR="$HOME/.config/omarchy"
CAVA_DIR="$HOME/.config/cava"
LOG_FILE="$CAVA_DIR/theme-monitor.log"
UPDATE_SCRIPT="$CAVA_DIR/update-colors.py"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to send notification
notify_user() {
    local message="$1"

    # Try different notification methods
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "Cava Theme Sync" "$message" --icon=audio-visualizer 2>/dev/null
    elif command -v dunstify >/dev/null 2>&1; then
        dunstify "Cava Theme Sync" "$message" 2>/dev/null
    fi
}

# Track last update time for debouncing
LAST_UPDATE=0
DEBOUNCE_SECONDS=2

# Function to update cava colors without restart
update_cava() {
    # Debounce rapid successive updates
    current_time=$(date +%s)
    if [ $((current_time - LAST_UPDATE)) -lt $DEBOUNCE_SECONDS ]; then
        log "Skipping update due to debouncing (too soon)"
        return
    fi
    LAST_UPDATE=$current_time

    log "Theme change detected, updating Cava colors..."
    cd "$CAVA_DIR"

    if python3 "$UPDATE_SCRIPT" >> "$LOG_FILE" 2>&1; then
        log "Cava colors updated successfully"

        if pgrep -x "cava" > /dev/null; then
            # Get current theme name
            THEME_NAME=$(basename "$(readlink ~/.config/omarchy/current/theme)" 2>/dev/null || echo "unknown")

            message="Colors updated for '$THEME_NAME' theme. Press 'c' in cava to reload colors."
            log "$message"
            notify_user "$message"
        else
            log "No cava instances running"
        fi
    else
        log "Failed to update Cava colors"
        notify_user "Failed to update cava colors"
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

log "Starting Cava theme monitor (notification version)..."
log "Watching: $OMARCHY_DIR/current/"

# Run initial update
update_cava

# Monitor for changes to the current theme
inotifywait -m -e modify,create,delete,move "$OMARCHY_DIR/current/" --format '%w%f %e' 2>/dev/null | while read file event; do
    # Check if the theme symlink changed
    if [[ "$file" == *"theme"* ]] || [[ "$event" == *"CREATE"* ]] || [[ "$event" == *"MODIFY"* ]]; then
        # Let the debouncing in update_cava handle timing
        update_cava
    fi
done