#!/usr/bin/env python3
"""
Dynamic Cava Color Updater for Omarchy Themes
Automatically updates Cava gradient colors based on current Omarchy theme.
"""

import json
import os
import sys
import re
from pathlib import Path

def get_current_theme_path():
    """Get the path to the current Omarchy theme."""
    current_theme_link = Path.home() / '.config' / 'omarchy' / 'current' / 'theme'
    if current_theme_link.exists() and current_theme_link.is_symlink():
        return Path(current_theme_link.readlink())
    return None

def parse_toml_colors(toml_path):
    """Parse colors from TOML file (simple parser for our needs)."""
    normal_colors = {}
    bright_colors = {}
    background = '#333333'
    current_section = None

    try:
        with open(toml_path, 'r') as f:
            content = f.read()

        # Parse line by line, tracking sections
        for line in content.split('\n'):
            line = line.strip()

            # Track TOML sections
            if line.startswith('[colors.normal]'):
                current_section = 'normal'
                continue
            elif line.startswith('[colors.bright]'):
                current_section = 'bright'
                continue
            elif line.startswith('[') and 'colors' not in line:
                current_section = None  # Other section
                continue
            elif line.startswith('[colors.'):
                current_section = 'other'  # Other color section
                continue

            # Skip commented lines
            if line.startswith('#'):
                continue

            if '=' in line and ('0x' in line or '#' in line):
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')

                # Extract hex color in either #xxxxxx or 0xxxxxxx format
                hex_match = re.search(r'(?:#|0x)([a-fA-F0-9]{6})', value)
                if hex_match:
                    # Convert to standard #xxxxxx format
                    clean_color = '#' + hex_match.group(1)

                    if 'background' in key:
                        background = clean_color
                    elif any(color in key for color in ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']):
                        # Extract just the color name
                        color_name = key.split('.')[-1] if '.' in key else key

                        # Store in appropriate section
                        if current_section == 'normal':
                            normal_colors[color_name] = clean_color
                        elif current_section == 'bright':
                            bright_colors[color_name] = clean_color

    except Exception as e:
        print(f"Error parsing TOML: {e}")

    # Prefer normal colors over bright colors for a more muted palette
    colors = normal_colors.copy()

    # Fill in missing colors with bright variants if needed
    for color_name in ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']:
        if color_name not in colors and color_name in bright_colors:
            colors[color_name] = bright_colors[color_name]

    # Debug output when both types are found
    if normal_colors and bright_colors:
        print(f"Found both normal and bright colors, prioritizing normal colors")

    return colors, background

def extract_theme_colors(theme_path):
    """Extract relevant colors from the Omarchy theme."""
    # First try to read from custom_theme.json
    theme_json_path = theme_path / 'custom_theme.json'
    if theme_json_path.exists():
        try:
            with open(theme_json_path, 'r') as f:
                theme_data = json.load(f)

            # Get colors from different sections, prioritizing terminal colors
            colors = []

            # Try to get terminal colors first
            if 'colors' in theme_data and 'terminal' in theme_data['colors']:
                terminal_colors = theme_data['colors']['terminal']
                colors.extend([
                    terminal_colors.get('cyan', '#048ba8'),
                    terminal_colors.get('blue', '#38d6fa'),
                    terminal_colors.get('magenta', '#d35f5f'),
                    terminal_colors.get('yellow', '#9f87af'),
                    terminal_colors.get('red', '#9c528b'),
                    terminal_colors.get('green', '#a9fbd7'),
                ])

            # Fallback to alacritty normal colors
            elif 'apps' in theme_data and 'alacritty' in theme_data['apps']:
                alacritty_colors = theme_data['apps']['alacritty']['colors']['normal']
                colors.extend([
                    alacritty_colors.get('cyan', '#048ba8'),
                    alacritty_colors.get('blue', '#38d6fa'),
                    alacritty_colors.get('magenta', '#d35f5f'),
                    alacritty_colors.get('yellow', '#9f87af'),
                    alacritty_colors.get('red', '#9c528b'),
                    alacritty_colors.get('green', '#a9fbd7'),
                ])

            # Get background color
            background = '#333333'  # default
            if 'colors' in theme_data and 'primary' in theme_data['colors']:
                background = theme_data['colors']['primary'].get('background', background)
            elif 'apps' in theme_data and 'alacritty' in theme_data['apps']:
                background = theme_data['apps']['alacritty']['colors']['primary'].get('background', background)

            return colors, background

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error reading JSON theme: {e}")

    # Fallback: try to read from alacritty.toml
    alacritty_toml = theme_path / 'alacritty.toml'
    if alacritty_toml.exists():
        try:
            toml_colors, background = parse_toml_colors(alacritty_toml)

            # Build color array from parsed TOML
            # Check if we actually found any colors, if not, create a monochrome scheme
            if not toml_colors:
                # Try to extract foreground color from the file
                foreground = '#EFEFEF'  # default
                try:
                    with open(alacritty_toml, 'r') as f:
                        content = f.read()
                    fg_match = re.search(r'foreground\s*=\s*"(?:#|0x)([a-fA-F0-9]{6})"', content)
                    if fg_match:
                        foreground = '#' + fg_match.group(1)
                except:
                    pass

                # Create gradient from dark to light variations based on midnight theme
                colors = [
                    '#333333',  # Dark gray
                    '#555555',  # Medium dark gray
                    '#777777',  # Medium gray
                    '#999999',  # Light gray
                    '#BBBBBB',  # Lighter gray
                    foreground,  # Foreground color
                ]
                print(f"Theme has no color palette, using monochrome midnight scheme with foreground: {foreground}")
            else:
                colors = [
                    toml_colors.get('cyan', '#8be9fd'),
                    toml_colors.get('blue', '#bd93f9'),
                    toml_colors.get('magenta', '#ff79c6'),
                    toml_colors.get('yellow', '#f1fa8c'),
                    toml_colors.get('red', '#ff5555'),
                    toml_colors.get('green', '#50fa7b'),
                ]

            return colors, background

        except Exception as e:
            print(f"Error reading TOML theme: {e}")

    return None


def update_cava_config(colors, background):
    """Update the Cava configuration with new gradient colors."""
    config_path = Path.home() / '.config' / 'cava' / 'config'

    if not config_path.exists():
        print(f"Cava config not found at {config_path}")
        return False

    try:
        # Read current config
        with open(config_path, 'r') as f:
            config_content = f.read()

        # Update gradient colors - limit to 8 colors max
        colors_to_use = colors[:8]  # Cava supports max 8 gradient colors

        # Find and replace gradient colors
        new_config = config_content

        # Enable gradient mode
        new_config = re.sub(r'gradient\s*=.*', 'gradient = 1', new_config)

        # Keep background as default (terminal color)
        # Remove any background color setting to use terminal default
        new_config = re.sub(r'background\s*=\s*[\'"]?#[a-fA-F0-9]{6}[\'"]?', 'background = default', new_config)

        # Update gradient colors
        for i, color in enumerate(colors_to_use, 1):
            # Clean the color value to ensure it's just #xxxxxx
            clean_color = color.strip().split()[0]  # Remove any comments or extra text
            if not clean_color.startswith('#') or len(clean_color) != 7:
                print(f"Warning: Invalid color format '{color}', skipping")
                continue

            pattern = f'gradient_color_{i}\\s*=.*'
            replacement = f"gradient_color_{i} = '{clean_color}'"
            if re.search(pattern, new_config):
                new_config = re.sub(pattern, replacement, new_config)
            else:
                # Add the color if it doesn't exist, find the last gradient color and add after it
                last_gradient_match = None
                for j in range(8, 0, -1):  # Check from 8 down to 1
                    match = re.search(f'gradient_color_{j}\\s*=.*', new_config)
                    if match:
                        last_gradient_match = match
                        break

                if last_gradient_match:
                    # Insert after the last gradient color
                    insert_pos = last_gradient_match.end()
                    new_config = new_config[:insert_pos] + f"\n{replacement}" + new_config[insert_pos:]
                else:
                    # Find [color] section and add after gradient = 1
                    gradient_match = re.search(r'gradient\s*=\s*1', new_config)
                    if gradient_match:
                        insert_pos = gradient_match.end()
                        new_config = new_config[:insert_pos] + f"\n{replacement}" + new_config[insert_pos:]

        # Remove any gradient colors beyond what we have (clean up any malformed lines too)
        for i in range(len(colors_to_use) + 1, 9):
            pattern = f'gradient_color_{i}\\s*=.*(?:\n|$)'
            new_config = re.sub(pattern, '', new_config)

        # Write the updated config
        with open(config_path, 'w') as f:
            f.write(new_config)

        return True

    except Exception as e:
        print(f"Error updating Cava config: {e}")
        return False

def main():
    """Main function to update Cava colors from current Omarchy theme."""
    print("Updating Cava colors from current Omarchy theme...")

    # Get current theme path
    theme_path = get_current_theme_path()
    if not theme_path:
        print("Could not find current Omarchy theme")
        sys.exit(1)

    theme_name = theme_path.name
    print(f"Current theme: {theme_name}")

    # Extract colors from theme
    color_data = extract_theme_colors(theme_path)
    if not color_data:
        print("Could not extract colors from theme")
        sys.exit(1)

    colors, background = color_data
    print(f"Extracted {len(colors)} colors (background kept as terminal default)")

    # Update Cava config
    if update_cava_config(colors, background):
        print("✅ Cava colors updated successfully!")
        print(f"Applied gradient colors: {', '.join(colors[:8])}")
    else:
        print("❌ Failed to update Cava config")
        sys.exit(1)

if __name__ == '__main__':
    main()