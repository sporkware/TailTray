# TailTray - Tailscale GUI for Linux

A system tray GUI application for Tailscale on Linux, providing the same features as the Windows Tailscale client.

## Features

- **Device Management**: View and search all devices in your Tailscale network
- **Exit Node Selection**: Enable/disable exit nodes with a full selection dialog
- **Taildrop**: Send files to devices on your network
- **Tailscale SSH**: SSH connections with terminal integration
- **Troubleshooting**: Diagnostics, connectivity tests, and log viewing
- **MagicDNS**: DNS name display and automatic resolution
- **System Tray**: KDE Plasma system tray with right-click menu
- **Configuration**: Persistent settings with XDG config directory support
- **Logging**: Comprehensive logging to file and console

## Installation

### Target Platform
TailTray is designed for **Arch Linux** and **Manjaro** with **KDE Plasma** desktop environment running on **Wayland**.

**✅ Verified Working**: KDE Plasma 6, Wayland session, AppIndicator3 system tray integration.

### Prerequisites

```bash
# Arch Linux / Manjaro
sudo pacman -S python-gobject python-requests gtk3 libappindicator-gtk3

# Install additional KDE/Plasma dependencies
sudo pacman -S plasma-desktop kdeplasma-addons
```

### Install Tailscale

```bash
# Arch Linux / Manjaro
sudo pacman -S tailscale

# Enable and start the service
sudo systemctl enable --now tailscaled
```

### Setup TailTray

```bash
# Clone the repository
git clone <repository-url>
cd tailtray

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python tailtray.py

# Optional: Build standalone executable for faster loading
pip install -r requirements-dev.txt
python build.py
```

### Automated Installation

For Arch Linux / Manjaro with KDE Plasma:

```bash
# Run the installation script
./install.sh

# Or with development dependencies
./install.sh --dev

# Or with autostart
./install.sh --autostart
```

### Arch Linux Package Installation

Build and install from PKGBUILD:

```bash
# Clone and build
makepkg -si

# Or install from AUR (when available)
yay -S tailtray
```

### Systemd User Service

Enable autostart with systemd:

```bash
# Copy service file
cp tailtray.service ~/.config/systemd/user/

# Enable and start
systemctl --user enable tailtray.service
systemctl --user start tailtray.service
```

### Manual Installation

For other distributions or manual setup:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy files to appropriate locations
sudo cp tailtray.py /usr/local/bin/tailtray
sudo cp tailtray.desktop /usr/share/applications/
sudo cp tailtray.svg /usr/share/icons/hicolor/scalable/apps/
sudo cp tailtray.1 /usr/share/man/man1/

# Make executable
sudo chmod +x /usr/local/bin/tailtray
```

## Usage

1. Start TailTray: `python tailtray.py`
2. The application will appear in your system tray
3. Right-click the tray icon to access all features
4. Left-click to quickly view device status

## Configuration

TailTray uses the Tailscale CLI for communication and stores its own configuration in XDG directories.

### Tailscale Setup
Ensure Tailscale is properly configured:
- Tailscale is running: `sudo systemctl enable --now tailscaled`
- You're authenticated: `tailscale up`

### TailTray Configuration
Configuration is stored in `~/.config/tailtray/config.json` and includes:
- UI preferences (theme, notifications)
- Network settings (cache timeouts, ping settings)
- Tailscale preferences (auto-connect, exit node)
- Logging configuration

Default configuration will be created automatically on first run.

## Development

### Project Structure

```
tailtray/
├── tailtray.py              # Main GTK application
├── tailscale_client.py      # Tailscale CLI client logic
├── tailtray_config.py       # Configuration management
├── setup.py                 # Python packaging
├── PKGBUILD                 # Arch Linux packaging
├── install.sh               # Installation script
├── tailtray.desktop         # Desktop file
├── tailtray.service         # Systemd user service
├── tailtray.svg             # Application icon
├── tailtray.1               # Man page
├── requirements.txt         # Runtime dependencies
├── requirements-dev.txt     # Development dependencies
├── tests/                   # Unit tests
│   ├── test_client.py      # Client tests
│   └── test_config.py      # Configuration tests
├── README.md               # This file
├── STATUS.md               # Development status
├── CHANGELOG.md            # Version history
├── CONTRIBUTING.md         # Contribution guidelines
└── LICENSE                 # MIT license
```

### Running in Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python tailtray.py

# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=tailtray tests/

# Check code style
black --check tailtray.py tailscale_client.py tailtray_config.py tests/
flake8 tailtray.py tailscale_client.py tailtray_config.py tests/
```

## Troubleshooting

### System Tray Not Appearing

TailTray is designed for **KDE Plasma** on **Wayland**. If the system tray icon doesn't appear:

- **Verify your desktop environment**: Ensure you're running KDE Plasma
- **Check Wayland**: Run `echo $XDG_SESSION_TYPE` - should show "wayland"
- **Install KDE Plasma components**:
  ```bash
  sudo pacman -S plasma-desktop kdeplasma-addons
  ```
- **Restart Plasma**: Log out and back in, or restart plasmashell:
  ```bash
  killall plasmashell && kstart5 plasmashell
  ```
- **Check AppIndicator support**: Ensure `libappindicator-gtk3` is installed

### Permission Issues

- Ensure your user is in the `tailscale` group: `sudo usermod -a -G tailscale $USER`
- Restart your session after group changes
- For Wayland, you may need additional permissions for system tray access

### API Connection Issues

- Check Tailscale status: `tailscale status`
- Verify Tailscale daemon is running: `systemctl status tailscaled`
- Ensure you're authenticated: `tailscale up`

### Wayland-Specific Issues

- **Screen sharing**: If TailTray windows don't appear, check Wayland permissions
- **System tray**: KDE Plasma's system tray should automatically show AppIndicator icons
- **Notifications**: Ensure KDE Plasma notifications are enabled

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and feature requests, please use the GitHub issue tracker.