"""Settings management for Gravity Control game."""

import json
import os
from pathlib import Path


class Settings:
    """Manages game settings with persistence to JSON file."""

    DEFAULT_SETTINGS = {
        "audio": {
            "master_volume": 100,
            "sfx_volume": 100,
            "music_volume": 100,
            "muted": False
        },
        "graphics": {
            "particle_quality": "high",  # low, medium, high
            "screen_shake": True,
            "background_speed": "normal",  # slow, normal, fast
            "vsync": True,
            "fullscreen": False
        },
        "controls": {
            "gravity_up": "up",
            "gravity_down": "down",
            "gravity_left": "left",
            "gravity_right": "right",
            "restart": "r",
            "pause": "escape",
            "continue": "space"
        },
        "game": {
            "show_timer": True,
            "show_fps": False,
            "show_hints": True
        }
    }

    def __init__(self, settings_file="settings.json"):
        """Initialize settings manager.

        Args:
            settings_file: Path to settings JSON file
        """
        self.settings_file = settings_file
        self.settings = self._deep_copy(self.DEFAULT_SETTINGS)
        self.load()

    def _deep_copy(self, obj):
        """Create a deep copy of a dictionary."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        return obj

    def load(self):
        """Load settings from JSON file, or create with defaults if not found."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self._merge_with_defaults(loaded)
                print(f"Settings loaded from {self.settings_file}")
            else:
                print(f"Settings file not found, created with defaults at {self.settings_file}")
                self.save()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading settings: {e}. Using defaults.")
            self.settings = self._deep_copy(self.DEFAULT_SETTINGS)

    def _merge_with_defaults(self, loaded):
        """Merge loaded settings with defaults to ensure all keys exist.

        Args:
            loaded: Loaded settings dictionary
        """
        for category, defaults in self.DEFAULT_SETTINGS.items():
            if category in loaded:
                for key, default_value in defaults.items():
                    if key in loaded[category]:
                        # Validate type matches
                        if isinstance(default_value, type(loaded[category][key])):
                            self.settings[category][key] = loaded[category][key]
                        else:
                            print(f"Warning: Invalid type for {category}.{key}, using default")
                            self.settings[category][key] = default_value
                    else:
                        self.settings[category][key] = default_value
            else:
                self.settings[category] = self._deep_copy(defaults)

    def save(self):
        """Save settings to JSON file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print(f"Settings saved to {self.settings_file}")
        except IOError as e:
            print(f"Error saving settings: {e}")

    def get(self, category, key):
        """Get a setting value.

        Args:
            category: Settings category (audio, graphics, controls, game)
            key: Setting key

        Returns:
            Setting value or None if not found
        """
        if category in self.settings:
            return self.settings[category].get(key)
        return None

    def set(self, category, key, value):
        """Set a setting value and save to file.

        Args:
            category: Settings category
            key: Setting key
            value: New value
        """
        if category in self.settings:
            self.settings[category][key] = value
            self.save()

    def reset_to_defaults(self):
        """Reset all settings to defaults and save."""
        self.settings = self._deep_copy(self.DEFAULT_SETTINGS)
        self.save()

    def reset_category(self, category):
        """Reset a specific category to defaults.

        Args:
            category: Category to reset
        """
        if category in self.DEFAULT_SETTINGS:
            self.settings[category] = self._deep_copy(self.DEFAULT_SETTINGS[category])
            self.save()

    def get_particle_limit(self):
        """Get maximum particle count based on quality setting.

        Returns:
            Maximum number of active particles
        """
        quality = self.get("graphics", "particle_quality")
        if quality == "low":
            return 20
        elif quality == "medium":
            return 50
        else:  # high
            return 100

    def get_background_speed_multiplier(self):
        """Get background animation speed multiplier.

        Returns:
            Speed multiplier (0.5, 1.0, or 1.5)
        """
        speed = self.get("graphics", "background_speed")
        if speed == "slow":
            return 0.5
        elif speed == "fast":
            return 1.5
        return 1.0


class GameState:
    """Manages game progress and statistics."""

    DEFAULT_STATE = {
        "current_level": 1,
        "best_times": {},
        "levels_completed": [],
        "total_deaths": 0,
        "total_playtime": 0.0
    }

    def __init__(self, state_file="game_state.json"):
        """Initialize game state manager.

        Args:
            state_file: Path to game state JSON file
        """
        self.state_file = state_file
        self.state = self.DEFAULT_STATE.copy()
        self.load()

    def load(self):
        """Load game state from JSON file."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for key in self.DEFAULT_STATE:
                        if key in loaded:
                            self.state[key] = loaded[key]
                print(f"Game state loaded from {self.state_file}")
            else:
                print(f"Game state file not found, created new state")
                self.save()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading game state: {e}. Using defaults.")
            self.state = self.DEFAULT_STATE.copy()

    def save(self):
        """Save game state to JSON file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except IOError as e:
            print(f"Error saving game state: {e}")

    def set_best_time(self, level, time):
        """Set best time for a level if it's better than existing.

        Args:
            level: Level number
            time: Completion time in seconds

        Returns:
            True if this is a new best, False otherwise
        """
        level_str = str(level)
        if level_str not in self.state["best_times"] or time < self.state["best_times"][level_str]:
            self.state["best_times"][level_str] = round(time, 3)
            self.save()
            return True
        return False

    def get_best_time(self, level):
        """Get best time for a level.

        Args:
            level: Level number

        Returns:
            Best time in seconds, or None if level not completed
        """
        return self.state["best_times"].get(str(level))

    def mark_level_complete(self, level):
        """Mark a level as completed.

        Args:
            level: Level number
        """
        if level not in self.state["levels_completed"]:
            self.state["levels_completed"].append(level)
            self.state["levels_completed"].sort()
            self.save()

    def increment_deaths(self):
        """Increment total death counter."""
        self.state["total_deaths"] += 1
        self.save()

    def add_playtime(self, seconds):
        """Add to total playtime.

        Args:
            seconds: Time to add in seconds
        """
        self.state["total_playtime"] += seconds
        self.save()
