#!/usr/bin/env python3
"""
Configuration management for TailTray
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class TailTrayConfig:
    """Configuration manager for TailTray"""

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            # Use XDG config directory
            xdg_config = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            config_dir = os.path.join(xdg_config, 'tailtray')

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / 'config.json'
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
            else:
                self._config = self._get_defaults()
                self._save_config()
                logger.info(f"Created default configuration at {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._config = self._get_defaults()

    def _save_config(self):
        """Save configuration to file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.debug(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            'ui': {
                'theme': 'system',  # system, light, dark
                'show_notifications': True,
                'auto_refresh_interval': 30,  # seconds
                'max_log_lines': 1000
            },
            'network': {
                'cache_timeout': 30,  # seconds
                'ping_timeout': 10,    # seconds
                'command_timeout': 15  # seconds
            },
            'tailscale': {
                'auto_connect': False,
                'preferred_exit_node': None
            },
            'logging': {
                'level': 'INFO',
                'file_enabled': True,
                'max_file_size': 10485760  # 10MB
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self._config

        # Navigate to the parent of the final key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the final value
        config[keys[-1]] = value
        self._save_config()
        logger.debug(f"Set configuration {key} = {value}")

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config = self._get_defaults()
        self._save_config()
        logger.info("Reset configuration to defaults")