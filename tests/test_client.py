#!/usr/bin/env python3
"""
Unit tests for TailscaleClient
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tailscale_client import TailscaleClient


class TestTailscaleClient(unittest.TestCase):
    """Test cases for TailscaleClient"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = TailscaleClient()

    def tearDown(self):
        """Clean up after tests"""
        self.client.clear_cache()

    @patch('subprocess.run')
    def test_get_status_success(self, mock_run):
        """Test successful status retrieval"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"BackendState": "Running", "Self": {"HostName": "test"}}'
        mock_run.return_value = mock_result

        status = self.client.get_status()

        self.assertIsNotNone(status)
        self.assertEqual(status['BackendState'], 'Running')
        self.assertEqual(status['Self']['HostName'], 'test')
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_get_status_failure(self, mock_run):
        """Test status retrieval failure"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = 'Connection failed'
        mock_run.return_value = mock_result

        status = self.client.get_status()

        self.assertIsNone(status)
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_get_status_json_error(self, mock_run):
        """Test status retrieval with invalid JSON"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = 'invalid json'
        mock_run.return_value = mock_result

        status = self.client.get_status()

        self.assertIsNone(status)

    def test_get_status_caching(self):
        """Test status caching"""
        # First call should fetch
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"BackendState": "Running"}'
            mock_run.return_value = mock_result

            status1 = self.client.get_status()
            self.assertEqual(mock_run.call_count, 1)

        # Second call should use cache
        with patch('subprocess.run') as mock_run:
            status2 = self.client.get_status()
            mock_run.assert_not_called()

        self.assertEqual(status1, status2)

    @patch('subprocess.run')
    def test_set_exit_node_success(self, mock_run):
        """Test successful exit node setting"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ''
        mock_result.stderr = ''
        mock_run.return_value = mock_result

        success, error = self.client.set_exit_node('192.168.1.1')

        self.assertTrue(success)
        self.assertEqual(error, '')
        mock_run.assert_called_once_with(
            ['tailscale', 'set', '--exit-node=192.168.1.1'],
            capture_output=True, text=True, timeout=15
        )

    @patch('subprocess.run')
    def test_set_exit_node_disable(self, mock_run):
        """Test exit node disabling"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        success, error = self.client.set_exit_node(None)

        self.assertTrue(success)
        mock_run.assert_called_once_with(
            ['tailscale', 'set', '--exit-node='],
            capture_output=True, text=True, timeout=15
        )

    @patch('subprocess.run')
    def test_set_exit_node_failure(self, mock_run):
        """Test exit node setting failure"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = 'Permission denied'
        mock_run.return_value = mock_result

        success, error = self.client.set_exit_node('192.168.1.1')

        self.assertFalse(success)
        self.assertIn('Permission denied', error)

    @patch('subprocess.run')
    def test_ping_device_success(self, mock_run):
        """Test successful device ping"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "pong"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        success, stdout, stderr = self.client.ping_device('device.example.ts.net')

        self.assertTrue(success)
        self.assertEqual(stdout, "pong")
        self.assertEqual(stderr, "")
        mock_run.assert_called_once_with(
            ['tailscale', 'ping', 'device.example.ts.net'],
            capture_output=True, text=True, timeout=10
        )

    @patch('subprocess.run')
    def test_ping_device_failure(self, mock_run):
        """Test device ping failure"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "timeout"
        mock_run.return_value = mock_result

        success, stdout, stderr = self.client.ping_device('device.example.ts.net')

        self.assertFalse(success)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "timeout")

    @patch('subprocess.run')
    def test_taildrop_send_success(self, mock_run):
        """Test successful taildrop send"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        success, error = self.client.taildrop_send("target", "/tmp/file")

        self.assertTrue(success)
        self.assertEqual(error, "")
        mock_run.assert_called_once_with(
            ['tailscale', 'file', 'cp', '/tmp/file', 'target:'],
            capture_output=True, text=True, timeout=30
        )

    @patch('subprocess.run')
    def test_taildrop_send_failure(self, mock_run):
        """Test taildrop send failure"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "failed"
        mock_run.return_value = mock_result

        success, error = self.client.taildrop_send("target", "/tmp/file")

        self.assertFalse(success)
        self.assertEqual(error, "failed")

    @patch('subprocess.run', side_effect=FileNotFoundError)
    def test_file_not_found_error(self, mock_run):
        """Test FileNotFoundError"""
        status = self.client.get_status()
        self.assertIsNone(status)

    def test_get_devices_empty_status(self):
        """Test get_devices with no status"""
        with patch.object(self.client, 'get_status', return_value=None):
            devices = self.client.get_devices()
            self.assertEqual(devices, [])

    def test_get_devices_with_data(self):
        """Test get_devices with status data"""
        mock_status = {
            'Self': {'HostName': 'mydevice', 'TailscaleIPs': ['100.1.1.1']},
            'Peers': {
                'peer1': {'HostName': 'peer1', 'TailscaleIPs': ['100.1.1.2']},
                'peer2': {'HostName': 'peer2', 'TailscaleIPs': ['100.1.1.3']}
            }
        }

        with patch.object(self.client, 'get_status', return_value=mock_status):
            devices = self.client.get_devices()
            self.assertEqual(len(devices), 3)
            self.assertEqual(devices[0]['HostName'], 'mydevice')
            self.assertEqual(devices[1]['HostName'], 'peer1')
            self.assertEqual(devices[2]['HostName'], 'peer2')

    def test_get_exit_nodes(self):
        """Test get_exit_nodes filtering"""
        mock_devices = [
            {'HostName': 'device1', 'ExitNodeOption': True},
            {'HostName': 'device2', 'ExitNodeOption': False},
            {'HostName': 'device3', 'ExitNodeOption': True}
        ]

        with patch.object(self.client, 'get_devices', return_value=mock_devices):
            exit_nodes = self.client.get_exit_nodes()
            self.assertEqual(len(exit_nodes), 2)
            self.assertEqual(exit_nodes[0]['HostName'], 'device1')
            self.assertEqual(exit_nodes[1]['HostName'], 'device3')

    def test_is_connected(self):
        """Test connection status checking"""
        # Test connected
        with patch.object(self.client, 'get_status', return_value={'BackendState': 'Running'}):
            self.assertTrue(self.client.is_connected())

        # Test not connected
        with patch.object(self.client, 'get_status', return_value={'BackendState': 'Stopped'}):
            self.assertFalse(self.client.is_connected())

        # Test no status
        with patch.object(self.client, 'get_status', return_value=None):
            self.assertFalse(self.client.is_connected())


if __name__ == '__main__':
    unittest.main()