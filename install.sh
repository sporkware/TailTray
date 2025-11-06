#!/bin/bash

# TailTray Installation Script
# Installs dependencies for TailTray on Linux

set -e

echo "🦎 TailTray Installation Script"
echo "================================"

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VER=$VERSION_ID
else
    echo "❌ Cannot detect Linux distribution"
    exit 1
fi

echo "📦 Detected distribution: $DISTRO $VER"

# Check for KDE Plasma and Wayland
if [ "$XDG_SESSION_DESKTOP" != "KDE" ] && [ "$XDG_SESSION_DESKTOP" != "plasma" ]; then
    echo "⚠️ Warning: TailTray is designed for KDE Plasma. Current desktop: $XDG_SESSION_DESKTOP"
fi

if [ "$XDG_SESSION_TYPE" != "wayland" ]; then
    echo "⚠️ Warning: TailTray is designed for Wayland. Current session: $XDG_SESSION_TYPE"
fi

# Install system packages based on distribution
case $DISTRO in
    arch|manjaro)
        echo "🔧 Installing packages for Arch Linux / Manjaro..."
        sudo pacman -S --noconfirm python-gobject python-requests gtk3 \
            libappindicator-gtk3 python-pip tailscale plasma-desktop \
            kdeplasma-addons
        ;;

    ubuntu|debian)
        echo "⚠️ Installing packages for Ubuntu/Debian (experimental support)..."
        sudo apt update
        sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
            gir1.2-appindicator3-0.1 python3-requests python3-pip \
            tailscale kde-plasma-desktop
        echo "⚠️ Note: KDE Plasma integration may not work perfectly on Ubuntu/Debian"
        ;;

    fedora)
        echo "⚠️ Installing packages for Fedora (experimental support)..."
        sudo dnf install -y python3-gobject python3-requests gtk3 \
            libappindicator-gtk3 python3-pip tailscale plasma-desktop
        echo "⚠️ Note: KDE Plasma integration may not work perfectly on Fedora"
        ;;

    opensuse*)
        echo "⚠️ Installing packages for openSUSE (experimental support)..."
        sudo zypper install -y python3-gobject python3-requests gtk3 \
            libappindicator3-1 python3-pip tailscale plasma5-desktop
        echo "⚠️ Note: KDE Plasma integration may not work perfectly on openSUSE"
        ;;

    *)
        echo "❌ Unsupported distribution: $DISTRO"
        echo "TailTray is designed for Arch Linux / Manjaro with KDE Plasma."
        echo "Please install the following packages manually:"
        echo "- python3-gobject (or python-gobject)"
        echo "- python3-requests (or python-requests)"
        echo "- gtk3"
        echo "- libappindicator-gtk3 (or equivalent)"
        echo "- python3-pip"
        echo "- tailscale"
        echo "- plasma-desktop (for KDE Plasma)"
        echo "- kdeplasma-addons (for KDE Plasma)"
        exit 1
        ;;
esac

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies if requested
if [ "$1" = "--dev" ]; then
    echo "🛠️ Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Enable and start Tailscale service
echo "🚀 Enabling Tailscale service..."
sudo systemctl enable tailscaled
sudo systemctl start tailscaled

# Check if Tailscale is running
echo "🔍 Checking Tailscale status..."
if systemctl is-active --quiet tailscaled; then
    echo "✅ Tailscale daemon is running"
else
    echo "⚠️ Tailscale daemon is not running. Please start it manually:"
    echo "   sudo systemctl start tailscaled"
fi

# Test GUI imports
echo "🧪 Testing GUI imports..."
python3 -c "
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3
print('✅ GUI imports successful')
" 2>/dev/null || echo "⚠️ GUI imports failed - check installation"

# Create desktop entry
echo "🖥️ Creating KDE Plasma desktop entry..."
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/tailtray.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=TailTray
Comment=Tailscale GUI for KDE Plasma
Exec=$(pwd)/venv/bin/python $(pwd)/tailtray.py
Icon=network-vpn
Terminal=false
Categories=Network;Qt;KDE;
StartupNotify=true
X-KDE-StartupNotify=true
X-KDE-SubstituteUID=false
EOF

echo "✅ Desktop entry created"

# Create autostart entry if requested
if [ "$1" = "--autostart" ] || [ "$2" = "--autostart" ]; then
    echo "🔄 Creating autostart entry..."
    mkdir -p ~/.config/autostart
    cp ~/.local/share/applications/tailtray.desktop ~/.config/autostart/
    echo "✅ Autostart entry created"
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Authenticate with Tailscale: tailscale up"
echo "2. Run TailTray: ./venv/bin/python tailtray.py"
echo "3. Or use the desktop entry from your KDE Plasma application menu"
echo ""
echo "🔧 Options:"
echo "   --dev      : Install development dependencies"
echo "   --autostart: Create autostart entry for KDE Plasma"
echo ""
echo "🎯 System Requirements:"
echo "   - Desktop Environment: KDE Plasma"
echo "   - Session Type: Wayland"
echo "   - Distribution: Arch Linux / Manjaro (recommended)"
echo ""
echo "📚 For more information, see README.md"