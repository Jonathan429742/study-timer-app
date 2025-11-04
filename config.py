# Application configuration
import os
import json

# Path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DATA_DIR = os.path.join(BASE_DIR, 'data')
SESSION_FILE = os.path.join(DATA_DIR, 'sessions.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')

# Default timer settings (in minutes)
DEFAULT_SETTINGS = {
    'work_duration': 25,
    'short_break_duration': 5,
    'long_break_duration': 15,
    'sessions_before_long_break': 4
}

# Colors
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'danger': '#F44336',
    'light': '#F8F9FA',
    'dark': '#212529',
    'work': '#2E86AB',
    'short_break': '#4CAF50',
    'long_break': '#A23B72'
}

# Ensure directories exist
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def load_settings():
    """Load settings from JSON file or return defaults"""
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            # Ensure all settings are present
            for key, value in DEFAULT_SETTINGS.items():
                if key not in settings:
                    settings[key] = value
            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to JSON file"""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)