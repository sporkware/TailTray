#!/usr/bin/env python3
"""
Unit tests for TailTray configuration
"""

import unittest
import tempfile
import os
import json
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tailtray_config import TailTrayConfig


class TestTailTrayConfig(unittest.TestCase):
    """Test cases for TailTrayConfig"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = TailTrayConfig(self.temp_dir)

    def tearDown(self):
        """Clean up after tests"""
        # Remove temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_config(self):
        """Test default configuration values"""
        self.assertEqual(self.config.get('ui.theme'), 'system')
        self.assertEqual(self.config.get('ui.show_notifications'), True)
        self.assertEqual(self.config.get('network.cache_timeout'), 30)
        self.assertEqual(self.config.get('logging.level'), 'INFO')

    def test_get_set_config(self):
        """Test getting and setting configuration values"""
        # Test setting a value
        self.config.set('ui.theme', 'dark')
        self.assertEqual(self.config.get('ui.theme'), 'dark')

        # Test getting nested values
        self.config.set('network.ping_timeout', 20)
        self.assertEqual(self.config.get('network.ping_timeout'), 20)

        # Test getting non-existent value
        self.assertIsNone(self.config.get('nonexistent.key'))
        self.assertEqual(self.config.get('nonexistent.key', 'default'), 'default')

    def test_config_persistence(self):
        """Test configuration persistence across instances"""
        # Set some values
        self.config.set('ui.theme', 'light')
        self.config.set('network.cache_timeout', 60)

        # Create new instance
        config2 = TailTrayConfig(self.temp_dir)

        # Check values are persisted
        self.assertEqual(config2.get('ui.theme'), 'light')
        self.assertEqual(config2.get('network.cache_timeout'), 60)

    def test_config_file_creation(self):
        """Test configuration file is created"""
        config_file = Path(self.temp_dir) / 'config.json'
        self.assertTrue(config_file.exists())

        # Verify it's valid JSON
        with open(config_file, 'r') as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        self.assertIn('ui', data)
        self.assertIn('network', data)

    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults"""
        # Modify some values
        self.config.set('ui.theme', 'dark')
        self.config.set('network.cache_timeout', 60)

        # Reset to defaults
        self.config.reset_to_defaults()

        # Check values are back to defaults
        self.assertEqual(self.config.get('ui.theme'), 'system')
        self.assertEqual(self.config.get('network.cache_timeout'), 30)

    def test_get_all(self):
        """Test getting all configuration"""
        all_config = self.config.get_all()
        self.assertIsInstance(all_config, dict)
        self.assertIn('ui', all_config)
        self.assertIn('network', all_config)
        self.assertIn('tailscale', all_config)
        self.assertIn('logging', all_config)

    def test_nested_keys(self):
        """Test nested key access"""
        # Test deep nesting
        self.config.set('deep.nested.value', 'test')
        self.assertEqual(self.config.get('deep.nested.value'), 'test')

        # Test partial access
        deep_config = self.config.get('deep')
        self.assertIsInstance(deep_config, dict)
        self.assertIn('nested', deep_config)


if __name__ == '__main__':
    unittest.main()