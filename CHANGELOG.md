# Changelog

All notable changes to TailTray will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Multi-distribution packaging (.deb, .rpm)
- Flatpak/Snap support
- Dark mode UI theme
- Advanced configuration options
- Plugin system architecture

## [0.1.0-alpha] - 2025-11-05

### Added
- **Core Application**
  - Python GTK3 GUI application optimized for KDE Plasma
  - System tray integration using AppIndicator3
  - Modular architecture with separated client and GUI logic
  - Comprehensive logging (file + console)
  - Virtual environment setup

- **Device Management**
  - Device list display with hostname, IP addresses, and online status
  - Search functionality for filtering devices
  - Operating system information display
  - Real-time status updates with caching

- **Exit Node Management**
  - Exit node selection dialog
  - Enable/disable exit node functionality
  - Current exit node status display
  - Location information for exit nodes

- **Taildrop Features**
  - File selection dialog
  - Device selection for file transfers
  - Progress indication for transfers
  - Error handling for file operations

- **Tailscale SSH**
  - SSH connection dialog
  - Terminal integration
  - Command history
  - Quick connect options

- **Troubleshooting Tools**
  - Diagnostics dialog
  - Connectivity tests with ping functionality
  - Status display
  - Log viewing functionality
  - Network information

- **MagicDNS Support**
  - DNS name display
  - Automatic resolution
  - Copy to clipboard functionality
  - DNS status indicators

- **Configuration System**
  - XDG-compliant configuration storage
  - Persistent settings with JSON format
  - UI, network, and Tailscale preferences
  - Runtime configuration updates

- **Packaging & Distribution**
  - Arch Linux PKGBUILD for native packaging
  - Python setup.py for pip installation
  - Systemd user service for autostart
  - Desktop file integration
  - SVG application icon
  - Man page documentation
  - Installation script with multiple options

- **Testing & Quality**
  - Comprehensive unit test suite (20 tests)
  - 100% test pass rate
  - Mocked external dependencies
  - Client and configuration testing
  - CI/CD ready test structure

- **System Integration**
  - KDE Plasma system tray support (Wayland)
  - Right-click context menu
  - Left-click quick status
  - Auto-start functionality via systemd
  - Proper desktop environment integration

### Technical Details
- **Backend**: Tailscale CLI integration with error handling
- **Frontend**: GTK3 with PyGObject, KDE Plasma optimized
- **System Tray**: AppIndicator3 with KDE Plasma support
- **Platform**: Linux (Arch Linux / Manjaro primary, KDE Plasma + Wayland)
- **Python Version**: 3.13+
- **Architecture**: Modular (client, config, GUI separation)

### Dependencies
- **Python**: PyGObject >= 3.40.0, requests >= 2.25.0
- **System**: GTK3, libappindicator-gtk3, plasma-desktop, kdeplasma-addons
- **Tailscale**: tailscale CLI

### Resolved Issues
- ✅ Comprehensive error handling with timeouts
- ✅ Configuration file support with XDG compliance
- ✅ Proper logging with file and console output
- ✅ Modular architecture for maintainability
- ✅ KDE Plasma + Wayland compatibility verified
- ✅ Complete packaging for Arch Linux

## [Future Plans]

### v0.2.0-beta (Planned)
- [ ] Multi-distribution support (.deb, .rpm packages)
- [ ] Flatpak/Snap universal packaging
- [ ] Dark mode UI theme support
- [ ] Advanced network monitoring features
- [ ] Performance optimizations

### v0.3.0-stable (Planned)
- [ ] Production-ready stability testing
- [ ] User experience improvements
- [ ] Advanced configuration options
- [ ] Plugin architecture foundation
- [ ] Multi-language support (i18n)

### v1.0.0-release (Planned)
- [ ] All planned features implemented
- [ ] Universal Linux distribution support
- [ ] Enterprise deployment features
- [ ] Advanced networking tools
- [ ] Commercial support options

---

## Version History Summary

| Version | Date | Status | Key Features |
|---------|------|--------|--------------|
| 0.1.0-alpha | 2025-11-05 | Alpha | Complete KDE Plasma GUI, packaging, testing |
| 0.2.0-beta | TBD | Beta | Multi-distro support, dark mode, performance |
| 0.3.0-stable | TBD | Stable | Production ready, enterprise features |
| 1.0.0-release | TBD | Release | Universal Linux support, commercial ready |

---

*Note: This project is currently in alpha development. Features and APIs may change significantly before the stable release.*