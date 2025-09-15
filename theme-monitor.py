#!/usr/bin/env python3
"""
Automatic Cava Theme Monitor
Watches for Omarchy theme changes and automatically updates Cava colors.
"""

import os
import time
import subprocess
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / '.config' / 'cava' / 'theme-monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ThemeChangeHandler(FileSystemEventHandler):
    """Handler for theme change events."""

    def __init__(self, update_script_path):
        self.update_script_path = update_script_path
        self.last_update = 0
        self.debounce_seconds = 1  # Prevent multiple rapid updates

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        # Check if the theme symlink was modified
        if event.src_path.endswith('/current/theme') or 'current' in event.src_path:
            self.update_cava_colors()

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return

        if event.src_path.endswith('/current/theme') or 'current' in event.src_path:
            self.update_cava_colors()

    def update_cava_colors(self):
        """Update Cava colors with debouncing."""
        current_time = time.time()
        if current_time - self.last_update < self.debounce_seconds:
            return

        self.last_update = current_time
        logger.info("Theme change detected, updating Cava colors...")

        try:
            # Run the update script
            result = subprocess.run(
                ['python3', str(self.update_script_path)],
                cwd=self.update_script_path.parent,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("Cava colors updated successfully")
                logger.info(result.stdout.strip())
            else:
                logger.error(f"Failed to update Cava colors: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error("Update script timed out")
        except Exception as e:
            logger.error(f"Error running update script: {e}")

def main():
    """Main monitoring function."""
    # Paths
    omarchy_config = Path.home() / '.config' / 'omarchy'
    update_script = Path.home() / '.config' / 'cava' / 'update-colors.py'

    if not omarchy_config.exists():
        logger.error(f"Omarchy config directory not found: {omarchy_config}")
        return 1

    if not update_script.exists():
        logger.error(f"Update script not found: {update_script}")
        return 1

    logger.info("Starting Cava theme monitor...")
    logger.info(f"Watching: {omarchy_config}")

    # Set up file system watcher
    event_handler = ThemeChangeHandler(update_script)
    observer = Observer()
    observer.schedule(event_handler, str(omarchy_config), recursive=True)

    # Start monitoring
    observer.start()
    logger.info("Theme monitor started successfully")

    try:
        # Run initial update
        event_handler.update_cava_colors()

        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down theme monitor...")
        observer.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        observer.stop()
        return 1

    observer.join()
    logger.info("Theme monitor stopped")
    return 0

if __name__ == '__main__':
    exit(main())