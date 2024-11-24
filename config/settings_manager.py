# config/settings_manager.py
import json
import os
from typing import Dict, Any, Optional

class SettingsManager:
    def __init__(self):
        self.settings_file = os.path.expanduser('~/.music_player_sync/settings.json')
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or return defaults"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.get_default_settings()
        return self.get_default_settings()

    def save_settings(self) -> bool:
        """Save current settings to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def get_default_settings(self) -> Dict[str, Any]:
        """Return default settings"""
        return {
            'music_directory': os.path.expanduser('~/Music'),
            'view_hierarchy': 'Artist > Album > Song',
            'auto_organize': False,
            'watch_folder': False,
            'device_settings': {
                'auto_detect': True,
                'support_ipod': True,
                'auto_eject': False,
                'show_warnings': True
            },
            'sync_settings': {
                'sync_playlists': True,
                'sync_ratings': True,
                'sync_play_counts': True,
                'conflict_resolution': 'Ask Each Time',
                'manage_space': True
            },
            'advanced_settings': {
                'enable_logging': False,
                'cache_size': 1000
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        try:
            keys = key.split('.')
            value = self.settings
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set a setting value"""
        keys = key.split('.')
        settings = self.settings
        for k in keys[:-1]:
            settings = settings.setdefault(k, {})
        settings[keys[-1]] = value
        self.save_settings()

# Singleton instance
settings_manager = SettingsManager()