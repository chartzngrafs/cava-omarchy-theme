#!/bin/bash
# Alternative Cava Theme Monitor with automatic restart
# This version will restart cava automatically to apply color changes

OMARCHY_DIR="$HOME/.config/omarchy"
CAVA_DIR="$HOME/.config/cava"
LOG_FILE="$CAVA_DIR/theme-monitor.log"
UPDATE_SCRIPT="$CAVA_DIR/update-colors.py"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to update cava colors with restart
update_cava() {
    log "Theme change detected, updating Cava colors..."
    cd "$CAVA_DIR"

    if python3 "$UPDATE_SCRIPT" >> "$LOG_FILE" 2>&1; then
        log "Cava colors updated successfully"

        # If cava is running, restart it more gracefully
        if pgrep -x "cava" > /dev/null; then
            log "Restarting cava to apply new colors..."

            # Store information about running cava instances
            CAVA_PIDS=$(pgrep -x "cava")
            CAVA_INFO=""

            for pid in $CAVA_PIDS; do
                # Get the terminal and working directory
                CAVA_ARGS=$(ps -o args= -p "$pid" 2>/dev/null | sed 's/^cava//' | xargs)
                CAVA_PWD=$(pwdx "$pid" 2>/dev/null | cut -d: -f2 | xargs)
                CAVA_TTY=$(ps -o tty= -p "$pid" 2>/dev/null | tr -d ' ')

                if [ -n "$CAVA_TTY" ] && [ "$CAVA_TTY" != "?" ]; then
                    CAVA_INFO="$CAVA_ARGS|$CAVA_PWD|$CAVA_TTY"
                    break
                fi
            done

            # Gracefully terminate cava first with SIGTERM
            pkill -TERM cava
            sleep 0.3

            # If still running, force kill
            if pgrep -x "cava" > /dev/null; then
                pkill -KILL cava
                sleep 0.1
            fi

            # Wait a bit longer before restart
            sleep 0.5

            # Restart cava
            if [ -n "$CAVA_INFO" ]; then
                IFS='|' read -r ARGS PWD TTY <<< "$CAVA_INFO"

                # Try to restart in the same directory
                if [ -n "$PWD" ] && [ -d "$PWD" ]; then
                    cd "$PWD"
                fi

                nohup cava $ARGS > /dev/null 2>&1 &
                log "Cava restarted with new colors (PID: $!)"
            else
                # Fallback: simple restart
                nohup cava > /dev/null 2>&1 &
                log "Cava restarted with new colors (PID: $!)"
            fi
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

log "Starting Cava theme monitor (auto-restart version)..."
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