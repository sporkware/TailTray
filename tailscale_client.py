#!/usr/bin/env python3
"""
Tailscale client module - Core business logic
Separated from GUI for better testability
"""

import subprocess
import json
import time
from typing import Optional, List, Dict, Any, Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)


class TailscaleClient:
    """Client for interacting with Tailscale via CLI"""

    def __init__(self):
        self.status_cache: Optional[Dict] = None
        self.devices_cache: List[Dict] = []
        self._last_update = 0
        self._cache_timeout = 30  # seconds
        logger.info("Initialized Tailscale CLI client")

    def get_status(self, force_refresh: bool = False) -> Optional[Dict]:
        """Get current Tailscale status with caching"""
        current_time = time.time()

        # Return cached status if still valid
        if (not force_refresh and
            self.status_cache and
            current_time - self._last_update < self._cache_timeout):
            return self.status_cache

        try:
            logger.debug("Fetching Tailscale status")
            result = subprocess.run(
                ["tailscale", "status", "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                try:
                    self.status_cache = json.loads(result.stdout.strip())
                    self._last_update = current_time
                    logger.debug("Successfully updated status cache")
                    return self.status_cache
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse status JSON: {e}")
                    return None
            else:
                logger.error(f"Tailscale status command failed: {result.stderr.strip()}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("Tailscale status command timed out")
            return None
        except FileNotFoundError:
            logger.error("Tailscale CLI not found. Is Tailscale installed?")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting status: {e}")
            return None

    def get_devices(self) -> List[Dict]:
        """Get list of devices"""
        status = self.get_status()
        if not status:
            return []

        devices = []
        if status.get('Self'):
            devices.append(status['Self'])

        for peer in status.get('Peers', {}).values():
            devices.append(peer)

        self.devices_cache = devices
        return devices

    def get_exit_nodes(self) -> List[Dict]:
        """Get devices that can be exit nodes"""
        devices = self.get_devices()
        return [d for d in devices if d.get('ExitNodeOption', False)]

    def set_exit_node(self, ip: Optional[str]) -> Tuple[bool, str]:
        """Set exit node

        Returns:
            Tuple of (success, error_message)
        """
        action = f"set exit node to {ip}" if ip else "disable exit node"

        try:
            if ip:
                cmd = ["tailscale", "set", f"--exit-node={ip}"]
            else:
                cmd = ["tailscale", "set", "--exit-node="]

            logger.info(f"Attempting to {action}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

            if result.returncode == 0:
                logger.info(f"Successfully {action}")
                self.clear_cache()  # Clear cache to force refresh
                return True, ""
            else:
                error_msg = result.stderr.strip() or f"Command failed with return code {result.returncode}"
                logger.error(f"Failed to {action}: {error_msg}")
                return False, error_msg

        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out while trying to {action}"
            logger.error(error_msg)
            return False, error_msg
        except FileNotFoundError:
            error_msg = "Tailscale CLI not found. Is Tailscale installed?"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error setting exit node: {e}"
            logger.error(error_msg)
            return False, str(e)

    def ping_device(self, hostname: str) -> bool:
        """Ping a device"""
        try:
            logger.debug(f"Pinging device: {hostname}")
            result = subprocess.run(["tailscale", "ping", hostname],
                                  capture_output=True, timeout=10)
            success = result.returncode == 0
            logger.debug(f"Ping {'successful' if success else 'failed'} for {hostname}")
            return success
        except subprocess.TimeoutExpired:
            logger.error(f"Ping timed out for {hostname}")
            return False
        except FileNotFoundError:
            logger.error("Tailscale CLI not found")
            return False
        except Exception as e:
            logger.error(f"Error pinging device {hostname}: {e}")
            return False

    def taildrop_send(self, target: str, file_path: str) -> Tuple[bool, str]:
        """Send file via taildrop"""
        try:
            logger.info(f"Sending file {file_path} to {target}")
            result = subprocess.run(["tailscale", "file", "cp", file_path, f"{target}:"],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.info(f"Successfully sent file to {target}")
                return True, ""
            else:
                error_msg = result.stderr.strip() or f"Command failed with return code {result.returncode}"
                logger.error(f"Failed to send file: {error_msg}")
                return False, error_msg

        except subprocess.TimeoutExpired:
            error_msg = "File transfer timed out"
            logger.error(error_msg)
            return False, error_msg
        except FileNotFoundError:
            error_msg = "Tailscale CLI not found"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error sending file: {e}"
            logger.error(error_msg)
            return False, str(e)

    def is_connected(self) -> bool:
        """Check if connected"""
        status = self.get_status()
        return status is not None and status.get('BackendState') == 'Running'

    def clear_cache(self):
        """Clear cached data"""
        self.status_cache = None
        self.devices_cache = []
        self._last_update = 0
        logger.debug("Cache cleared")