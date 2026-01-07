# Cava Omarchy Theme Sync

Automatically synchronize [Cava](https://github.com/karlstav/cava) audio visualizer colors with your current [Omarchy](https://github.com/aredl/omarchy) theme in real-time.

![Demo of cava colors changing with theme](demo.gif)

## Features

- ✅ **Real-time theme synchronization** - Colors update automatically when you switch themes
- ✅ **Universal theme support** - Works with JSON and TOML theme formats
- ✅ **Smart color parsing** - Handles multiple hex formats and TOML sections
- ✅ **Crash-free operation** - Never interrupts running cava instances
- ✅ **Desktop notifications** - Get notified when colors update
- ✅ **Terminal background preserved** - Never overrides your terminal colors

## Installation

```bash
git clone https://github.com/yourusername/cava-omarchy-theme
cd cava-omarchy-theme

# Copy scripts to your cava config directory
cp *.sh *.py ~/.config/cava/
```

## Quick Start

### Manual Sync
```bash
# Update cava colors to match current theme
./sync-theme.sh
```

### Automatic Sync (Recommended)
Set up a systemd service for automatic theme monitoring:

```bash
# Copy the service script to cava config
cp theme-monitor-notify.sh ~/.config/cava/

# Create systemd service (you'll need to create the service file)
systemctl --user enable cava-theme-monitor.service
systemctl --user start cava-theme-monitor.service
```

## How It Works

1. **Monitors** `~/.config/omarchy/current/` directory for theme changes
2. **Extracts** colors from theme files in `~/.config/omarchy/current/theme/` (`custom_theme.json` or `alacritty.toml`)
3. **Updates** cava config with new gradient colors
4. **Notifies** you to reload cava (press `c` or `r` in cava)

## Supported Themes

- **JSON themes** (chartzngrafs, etc.)
- **TOML themes** (Dracula, Catppuccin, Blue Ridge Dark, etc.)
- **Monochrome themes** (Felix, Midnight)
- **All standard Omarchy themes**

## Requirements

- [Cava](https://github.com/karlstav/cava) audio visualizer
- [Omarchy](https://github.com/aredl/omarchy) theme manager
- Python 3.6+
- `inotify-tools` (for file monitoring)

## Usage

When you change your Omarchy theme:
1. Theme change is detected automatically
2. Cava config is updated with new colors
3. You receive a desktop notification
4. Press `c` (reload colors) or `r` (reload all) in cava
5. Enjoy your new synchronized colors!

## Documentation

See [README-theme-sync.md](README-theme-sync.md) for detailed technical documentation.

## License

MIT License - feel free to use and modify as needed.