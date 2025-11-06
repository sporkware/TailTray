#!/usr/bin/env python3
"""
Integration tests for TailTray GUI
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from tailtray import MainWindow, DeviceDialog, ExitNodeDialog, TaildropDialog, SSHDialog, TroubleshootingDialog
from tailscale_client import TailscaleClient

class TestGUI(unittest.TestCase):
    """Test cases for the GTK GUI"""

    @classmethod
    def setUpClass(cls):
        """Set up the GTK application"""
        cls.app = Gtk.Application()

    def test_main_window_creation(self):
        """Test that the main window can be created"""
        client = MagicMock(spec=TailscaleClient)
        window = MainWindow(self.app, client)
        self.assertIsInstance(window, MainWindow)
        window.destroy()

    def test_device_dialog_creation(self):
        """Test that the device dialog can be created"""
        client = MagicMock(spec=TailscaleClient)
        device = {"HostName": "test-device", "Addresses": ["100.64.0.1"], "OS": "Linux"}
        parent = Gtk.Window()
        dialog = DeviceDialog(parent, device, client)
        self.assertIsInstance(dialog, DeviceDialog)
        dialog.destroy()

    def test_exit_node_dialog_creation(self):
        """Test that the exit node dialog can be created"""
        client = MagicMock(spec=TailscaleClient)
        client.get_exit_nodes.return_value = []
        parent = Gtk.Window()
        dialog = ExitNodeDialog(parent, client)
        self.assertIsInstance(dialog, ExitNodeDialog)
        dialog.destroy()

    def test_taildrop_dialog_creation(self):
        """Test that the taildrop dialog can be created"""
        client = MagicMock(spec=TailscaleClient)
        client.get_devices.return_value = []
        parent = Gtk.Window()
        dialog = TaildropDialog(parent, client)
        self.assertIsInstance(dialog, TaildropDialog)
        dialog.destroy()

    def test_ssh_dialog_creation(self):
        """Test that the SSH dialog can be created"""
        client = MagicMock(spec=TailscaleClient)
        client.get_devices.return_value = []
        parent = Gtk.Window()
        dialog = SSHDialog(parent, client)
        self.assertIsInstance(dialog, SSHDialog)
        dialog.destroy()

    def test_troubleshooting_dialog_creation(self):
        """Test that the troubleshooting dialog can be created"""
        client = MagicMock(spec=TailscaleClient)
        client.get_status.return_value = {}
        parent = Gtk.Window()
        dialog = TroubleshootingDialog(parent, client)
        self.assertIsInstance(dialog, TroubleshootingDialog)
        dialog.destroy()

if __name__ == '__main__':
    unittest.main()