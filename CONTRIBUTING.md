# Contributing to TailTray

Thank you for your interest in contributing to TailTray! This document provides guidelines and information for contributors.

## Getting Started

### Development Environment Setup

1. **Prerequisites** (Arch Linux / Manjaro with KDE Plasma recommended)
   ```bash
   # Arch Linux / Manjaro
   sudo pacman -S python-gobject python-requests gtk3 libappindicator-gtk3 tailscale git plasma-desktop kdeplasma-addons

   # For packaging development
   sudo pacman -S pacman-contrib python-setuptools
   ```

2. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd tailtray
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Install Tailscale**
   ```bash
   # If not already installed
   sudo systemctl enable --now tailscaled
   tailscale up
   ```

4. **Verify Environment**
   ```bash
   # Check desktop environment
   echo $XDG_SESSION_DESKTOP  # Should show "KDE" or "plasma"
   echo $XDG_SESSION_TYPE     # Should show "wayland"
   ```

### Running the Application

```bash
# Development mode
source venv/bin/activate
python tailtray.py --debug

# Test mode
python tailtray.py --test

# Production mode
python tailtray.py
```

## Development Guidelines

### Code Style

We follow these Python coding standards:

- **PEP 8** for Python code formatting
- **Type hints** for all new functions and methods
- **Docstrings** for all public functions and classes
- **Line length**: Maximum 88 characters (Black default)

#### Example Code Style

```python
from typing import Optional, List, Dict
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class DeviceManager:
    """Manages Tailscale device operations."""
    
    def __init__(self, client: TailscaleClient) -> None:
        self.client = client
        self.devices: List[Dict] = []
    
    def get_online_devices(self) -> List[Dict]:
        """Get list of currently online devices.
        
        Returns:
            List of device dictionaries with online status.
        """
        return [device for device in self.devices if device.get('online', False)]
```

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
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_client.py      # Client tests
│   └── test_config.py      # Configuration tests
│   ├── test_gui.py
│   └── fixtures/
├── docs/                    # Documentation
│   ├── api.md
│   ├── user-guide.md
│   └── development.md
├── scripts/                 # Utility scripts
│   ├── install.sh
│   ├── build.sh
│   └── test.sh
└── assets/                  # Icons, themes, etc.
    ├── icons/
    └── ui/
```

## Contributing Process

### 1. Fork and Branch

1. Fork the repository on GitHub
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

### 2. Make Changes

- Write clean, well-documented code
- Add tests for new functionality
- Update documentation as needed
- Follow the existing code style

### 3. Test Your Changes

```bash
# Run the test suite
python -m pytest tests/

# Run with coverage
python -m pytest --cov=tailtray tests/

# Check code style
black --check tailtray.py tests/
flake8 tailtray.py tests/

# Type checking
mypy tailtray.py
```

### 4. Commit Changes

Use clear, descriptive commit messages:

```
feat: add exit node selection dialog
fix: resolve system tray icon display issue
docs: update installation instructions
test: add unit tests for device manager
```

### 5. Submit Pull Request

1. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a pull request with:
   - Clear title and description
   - Reference any related issues
   - Describe testing performed
   - Include screenshots for UI changes

## Areas for Contribution

### High Priority

1. **Testing**
   - Unit tests for all components
   - Integration tests with Tailscale API
   - GUI testing with GTK test framework
   - Mock Tailscale API for testing

2. **API Integration**
   - Replace CLI calls with Tailscale SDK
   - Implement proper error handling
   - Add async operations
   - Connection retry logic

3. **Documentation**
   - User guide with screenshots
   - API documentation
   - Installation guides for different distributions
   - Troubleshooting guide

### Medium Priority

1. **UI/UX Improvements**
   - Dark mode support
   - Better error messages
   - Progress indicators
   - Keyboard shortcuts

2. **Features**
   - Configuration file support
   - Network profiles
   - Bandwidth monitoring
   - Auto-connect rules

3. **Platform Support**
   - Wayland compatibility
   - Different desktop environments
   - High DPI support
   - Multi-language support

### Low Priority

1. **Advanced Features**
   - Plugin system
   - Browser extension
   - Mobile app companion
   - Advanced networking tools

## Development Tools

### Recommended IDE Setup

- **VS Code** with Python extensions
- **PyCharm** Community Edition
- **Vim/Neovim** with Python plugins

### Useful Extensions

- Python (Microsoft)
- Pylance
- Black Formatter
- GitLens
- GTK Inspector

### Debugging

```bash
# Enable debug logging
export TAILTRAY_DEBUG=1
python tailtray.py

# GTK Inspector for UI debugging
GTK_DEBUG=interactive python tailtray.py

# Profile memory usage
python -m memory_profiler tailtray.py
```

## Reporting Issues

When reporting bugs, please include:

1. **System Information**
   - Linux distribution and version
   - Desktop environment
   - Python version
   - Tailscale version

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Any error messages

3. **Logs**
   - Application logs with debug enabled
   - Tailscale daemon logs
   - System logs if relevant

## Code Review Process

1. **Automated Checks**
   - All tests must pass
   - Code style compliance
   - Type checking
   - Security scanning

2. **Manual Review**
   - Code quality and maintainability
   - Feature correctness
   - Performance implications
   - Documentation updates

3. **Approval Requirements**
   - At least one maintainer approval
   - All discussions resolved
   - CI/CD pipeline passing

## Community

- **GitHub Discussions**: For questions and ideas
- **Issues**: For bug reports and feature requests
- **Wiki**: For additional documentation
- **Releases**: For announcements and changelogs

#### Packaging Guidelines
- Update `PKGBUILD` for Arch Linux packages
- Update `setup.py` for Python packaging
- Test systemd service integration
- Ensure desktop file follows XDG standards
- Update man page for new features
- Test package installation on clean system

## License

By contributing to TailTray, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to TailTray! Your help makes this project better for everyone.