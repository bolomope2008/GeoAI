"""
Settings Manager for GeoAI Backend

This module handles configuration settings storage and retrieval using JSON files
instead of modifying the configuration.py file directly. This is essential for
Electron apps where the configuration.py file is bundled and read-only.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SettingsManager:
    def __init__(self, config_dir: str = None):
        """
        Initialize the settings manager.
        
        Args:
            config_dir: Directory to store settings. If None, uses CONFIG_DIR env var
                       or falls back to current directory.
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path(os.getenv('CONFIG_DIR', '.'))
        
        self.settings_file = self.config_dir / 'settings.json'
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Default settings (matching configuration.py defaults)
        self.default_settings = {
            "ollama_base_url": "http://localhost:11434",
            "embedding_model": "nomic-embed-text", 
            "llm_model": "phi4:14b-fp16",
            "chunk_size": 1500,
            "chunk_overlap": 150,
            "top_k_chunks": 10
        }
        
        # Load existing settings or create default file
        self._initialize_settings()
    
    def _initialize_settings(self):
        """Initialize settings file if it doesn't exist."""
        if not self.settings_file.exists():
            logger.info(f"Creating default settings file at {self.settings_file}")
            self.save_settings(self.default_settings)
        else:
            # Validate existing settings and add missing keys
            current_settings = self.load_settings()
            updated = False
            for key, value in self.default_settings.items():
                if key not in current_settings:
                    current_settings[key] = value
                    updated = True
            
            if updated:
                logger.info("Updating settings file with new default values")
                self.save_settings(current_settings)
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from JSON file.
        
        Returns:
            Dictionary containing all settings
        """
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
            return settings
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load settings: {e}. Using defaults.")
            return self.default_settings.copy()
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save settings to JSON file.
        
        Args:
            settings: Dictionary of settings to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate settings keys
            valid_keys = set(self.default_settings.keys())
            filtered_settings = {k: v for k, v in settings.items() if k in valid_keys}
            
            # Merge with existing settings to preserve any we didn't update
            current_settings = self.load_settings()
            current_settings.update(filtered_settings)
            
            with open(self.settings_file, 'w') as f:
                json.dump(current_settings, f, indent=2)
            
            logger.info(f"Settings saved successfully to {self.settings_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
    
    def get_setting(self, key: str, default=None):
        """
        Get a specific setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        settings = self.load_settings()
        return settings.get(key, default)
    
    def update_setting(self, key: str, value: Any) -> bool:
        """
        Update a single setting.
        
        Args:
            key: Setting key
            value: New value
            
        Returns:
            True if successful, False otherwise
        """
        if key not in self.default_settings:
            logger.warning(f"Unknown setting key: {key}")
            return False
        
        settings = self.load_settings()
        settings[key] = value
        return self.save_settings(settings)
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all settings to default values.
        
        Returns:
            True if successful, False otherwise
        """
        return self.save_settings(self.default_settings)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all current settings.
        
        Returns:
            Dictionary of all settings
        """
        return self.load_settings()