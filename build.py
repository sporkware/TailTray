#!/usr/bin/env python3
"""
Build script for creating a standalone executable of TailTray using PyInstaller.
This creates a single executable file for faster loading and easier distribution.
"""

import os
import subprocess
import sys
from pathlib import Path

def build_executable():
    """Build the TailTray executable using PyInstaller."""
    print("Building TailTray executable...")

    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # PyInstaller command (Nuitka requires patchelf for better optimization)
    cmd = [
        "pyinstaller",
        "--onefile",  # Create a single executable
        "--windowed",  # Don't show console window (for GUI app)
        "--name", "tailtray",
        "--hidden-import", "gi.repository.Gtk",
        "--hidden-import", "gi.repository.Gdk",
        "--hidden-import", "gi.repository.GLib",
        "--hidden-import", "gi.repository.GObject",
        "--hidden-import", "gi.repository.AppIndicator3",
        "--hidden-import", "gi.repository.Gio",
        "--add-data", "tailtray.svg:.",  # Include icon in bundle
        "tailtray.py"
    ]

    try:
        subprocess.run(cmd, check=True)
        print("Build completed successfully!")
        print("Executable created: dist/tailtray")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()