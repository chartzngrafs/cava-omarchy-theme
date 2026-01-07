# Cava Omarchy Theme Sync

This project automatically synchronizes Cava's colors with your current Omarchy theme in **real-time with live updates**.

## Installation

```bash
git clone https://github.com/yourusername/cava-omarchy-theme
cd cava-omarchy-theme
# Copy scripts to your cava config directory
cp *.sh *.py ~/.config/cava/
```

## Files

- `update-colors.py` - Python script that reads current Omarchy theme and updates Cava config
- `sync-theme.sh` - Shell wrapper script for manual syncing
- `theme-monitor.sh` - Background monitor (manual reload version)
- `theme-monitor-restart.sh` - Background monitor with auto-restart (can cause crashes)
- `theme-monitor-notify.sh` - Background monitor with notifications (currently active)
- `theme-monitor.py` - Alternative Python-based monitor (requires watchdog package)

## Live Automatic Sync with Manual Reload (Currently Active) ✅

A systemd user service `cava-theme-monitor.service` is running in the background that:
- **Automatically detects when you change your Omarchy theme**
- **Instantly updates Cava config with new colors** when themes switch
- **Sends desktop notifications** when colors are updated
- **Requires pressing 'c' or 'r' in cava** to reload colors (prevents crashes, ensures stability)
- Logs activity to `~/.config/cava/theme-monitor.log` (when installed to cava config directory)

### Service Management
```bash
# Check status
systemctl --user status cava-theme-monitor.service

# View recent logs
tail -f ~/.config/cava/theme-monitor.log

# Stop service
systemctl --user stop cava-theme-monitor.service

# Start service
systemctl --user start cava-theme-monitor.service

# Disable auto-start
systemctl --user disable cava-theme-monitor.service
```

## Manual Sync (If Needed)
```bash
# If installed to ~/.config/cava/
~/.config/cava/sync-theme.sh

# Or run directly from this directory
./sync-theme.sh
```

## How it Works

1. **File monitoring**: Watches `~/.config/omarchy/current/` directory for theme changes using `inotifywait`
2. **Theme detection**: Reads theme name from `~/.config/omarchy/current/theme.name`
3. **Color extraction**: When theme changes, extracts colors from theme files in `~/.config/omarchy/current/theme/`:
   - `custom_theme.json` (for complex themes like chartzngrafs)
   - `alacritty.toml` (for standard themes like Dracula, Blue Ridge Dark, etc.)
4. **Smart parsing**: Handles multiple hex formats (`#xxxxxx`, `0xxxxxxx`), inline comments, TOML sections, and malformed color entries
5. **Color mapping**: Uses terminal colors (cyan, blue, magenta, yellow, red, green) for gradient
6. **Config update**: Updates Cava's config with extracted colors, keeping background as terminal default
7. **Notification**: Sends desktop notifications when colors update, prompting manual reload

The colors are applied as a gradient from bottom to top of the visualizer, creating a dynamic color scheme that matches your current theme.

## Color Features

- ✅ **Terminal background preserved** - Never overrides your terminal's background color
- ✅ **Universal hex format support** - Handles both `#xxxxxx` and `0xxxxxxx` hex formats
- ✅ **Intelligent color parsing** - Handles TOML sections, inline comments, and various formats
- ✅ **Smart color prioritization** - Prefers normal over bright colors for appropriate palettes
- ✅ **Gradient generation** - Creates smooth color transitions from theme palette
- ✅ **Real-time config updates** - Colors update automatically, manual reload required
- ✅ **Desktop notifications** - Get notified when theme colors change
- ✅ **Single notification per change** - Intelligent debouncing prevents notification spam
- ✅ **Crash-free operation** - Never interrupts running cava instances

## Supported Themes

- ✅ **JSON themes** with `custom_theme.json` (chartzngrafs, etc.)
- ✅ **TOML themes** with `alacritty.toml` (Dracula, Catppuccin, Blue Ridge Dark, Felix, Space Monkey, Solarized Osaka, etc.)
- ✅ **Section-aware parsing** - Correctly handles `[colors.normal]` and `[colors.bright]` sections
- ✅ **Multiple hex formats** - Supports both `#268bd2` and `0x268bd2` color formats
- ✅ **Themes with inline comments** - Properly parsed hex colors with comments
- ✅ **Monochrome themes** (Felix, Midnight) and colorful themes (Space Monkey, Ristretto)
- ✅ **Minimal themes** - Creates appropriate gradients for themes without color palettes
- ✅ **All standard Omarchy color schemes**

## Usage

When you change your Omarchy theme:
1. **Automatic detection** - The monitor service detects the theme change instantly
2. **Config update** - Cava's config is updated with new colors automatically
3. **Notification** - You receive a desktop notification like: *"Colors updated for 'ristretto' theme. Press 'c' in cava to reload colors."*
4. **Manual reload** - Press `c` (reload colors) or `r` (reload all) in your cava window
5. **Enjoy new colors** - Cava displays with the new theme's gradient colors

## Color Extraction Logic

The system intelligently handles different theme formats:

1. **JSON themes**: Extracts colors from structured JSON with priority on terminal colors
2. **TOML themes with sections**: Prefers `[colors.normal]` over `[colors.bright]` for muted, appropriate palettes
3. **TOML themes without sections**: Uses available colors as-is
4. **Multiple hex formats**: Automatically converts both `#xxxxxx` and `0xxxxxxx` formats to cava-compatible format
5. **Minimal themes**: Creates monochrome gradients based on foreground color
6. **Fallback handling**: Gracefully handles missing or malformed color definitions

## Version History

- **v1.0**: Basic color extraction and manual sync
- **v2.0**: Added automatic monitoring with cava restart (caused crashes)
- **v3.0**: Notification-based system with manual reload (crash-free)
- **v3.1**: Enhanced TOML parsing with section awareness and smart color prioritization
- **v3.2**: **Current** - Added universal hex format support (`#` and `0x`), improved notification debouncing, and robust error handling for all theme types