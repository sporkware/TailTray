#!/usr/bin/env python3
"""
Basic test for TailTray functionality without GUI
"""

import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tailscale_cli():
    """Test basic Tailscale CLI functionality"""
    print("Testing Tailscale CLI...")
    
    # Test status
    try:
        result = subprocess.run(["tailscale", "status", "--json"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            status = json.loads(result.stdout.strip())
            print(f"✓ Connected: {status.get('BackendState') == 'Running'}")
            print(f"✓ Self: {status.get('Self', {}).get('HostName', 'Unknown')}")
            print(f"✓ Peers: {len(status.get('Peers', {}))}")
        else:
            print(f"✗ Status failed: {result.stderr}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test if tailscale is available
    try:
        result = subprocess.run(["which", "tailscale"], capture_output=True)
        if result.returncode == 0:
            print("✓ Tailscale CLI found")
        else:
            print("✗ Tailscale CLI not found")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_gui_imports():
    """Test if GUI imports would work"""
    print("\nTesting GUI imports...")

    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, Gdk, GLib
        print("✓ GTK imports successful")

        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3
        print("✓ AppIndicator imports successful")

    except ImportError as e:
        print(f"✗ Import error: {e}")
    except ValueError as e:
        print(f"✗ GTK version error: {e}")

def test_kde_plasma_environment():
    """Test KDE Plasma and Wayland environment"""
    print("\nTesting KDE Plasma environment...")

    import os

    # Check desktop environment
    desktop = os.environ.get('XDG_SESSION_DESKTOP', '')
    if desktop in ['KDE', 'plasma']:
        print("✓ KDE Plasma desktop environment detected")
    else:
        print(f"⚠️ Desktop environment: {desktop} (KDE Plasma recommended)")

    # Check session type
    session_type = os.environ.get('XDG_SESSION_TYPE', '')
    if session_type == 'wayland':
        print("✓ Wayland session detected")
    else:
        print(f"⚠️ Session type: {session_type} (Wayland recommended)")

    # Check for KDE specific environment variables
    kde_session = os.environ.get('KDE_SESSION_VERSION', '')
    if kde_session:
        print(f"✓ KDE session version: {kde_session}")
    else:
        print("⚠️ KDE session version not detected")

    # Check for system tray support
    try:
        # Try to create a basic AppIndicator
        import gi
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3
        indicator = AppIndicator3.Indicator.new("test", "network-vpn", AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        print("✓ AppIndicator creation successful")
    except Exception as e:
        print(f"⚠️ AppIndicator test failed: {e}")

if __name__ == "__main__":
    test_tailscale_cli()
    test_gui_imports()
    test_kde_plasma_environment()