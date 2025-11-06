# TailTray - Development Guidelines

## Build Commands

### Python Version (Primary)
```bash
# Virtual environment setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run application
python tailtray.py
```

### Arch Linux Package Build
```bash
# Build from PKGBUILD
makepkg -si

# Or install from AUR (when available)
yay -S tailtray
```

### Python Package Installation
```bash
# Install via pip
pip install .

# Or install in development mode
pip install -e .
```

## Test Commands

### Python Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=tailtray tests/

# Run specific test file
python -m pytest tests/test_client.py -v

# Run with verbose output
python -m pytest tests/ -v
```

### Integration Testing
```bash
# Test GUI application
python tailtray.py --help

# Test basic functionality
python test_basic.py
```

## Lint Commands

### Python
```bash
# Install linting tools
pip install -r requirements-dev.txt

# Check code style
black --check tailtray.py tailscale_client.py tailtray_config.py tests/

# Fix code style
black tailtray.py tailscale_client.py tailtray_config.py tests/

# Check for issues
flake8 tailtray.py tailscale_client.py tailtray_config.py tests/

# Type checking
mypy tailtray.py tailscale_client.py tailtray_config.py
```

## Code Style Guidelines

### Python
- **Imports**: Group by standard library, third-party, local
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Docstrings**: Use triple quotes for module/class/function docs
- **Line length**: 88 characters (Black default)
- **Error handling**: Use try/except with specific exceptions and proper logging
- **GTK**: Use gi.repository imports, handle widget creation properly
- **Type hints**: Use for all function parameters and return values
- **Logging**: Use the logging module, not print statements

```python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class MainWindow(Gtk.ApplicationWindow):
    """Main application window for TailTray."""

    def __init__(self, app, ts_client) -> None:
        super().__init__(application=app, title="TailTray")
        self.ts_client = ts_client
        logger.info("Main window initialized")
        # implementation...
```

### Common Guidelines

### Error Handling
**Python:**
```python
try:
    result = self.ts_client.get_status()
    if not result:
        raise ValueError("Failed to get status")
except Exception as e:
    logging.error(f"Status error: {e}")
    return False
```

**Go:**
```go
status, err := client.GetStatus()
if err != nil {
    log.Printf("Failed to get status: %v", err)
    return err
}
```

### Code Structure
- Keep functions focused on single responsibility
- Use classes/structs for related data
- Document public APIs
- Separate GUI logic from business logic

### GTK/GUI Code
- Initialize GTK properly in main
- Handle widget creation errors
- Connect signals appropriately
- Clean up resources when done
- Use consistent spacing/margins

### Logging
- Include context in log messages
- Use appropriate log levels
- Don't log sensitive information

### Comments
- Document exported functions/types
- Explain complex logic
- Keep comments current

### File Organization
**Python:**
- `tailtray.py`: Main GTK application
- `tailscale_client.py`: Tailscale CLI client logic
- `tailtray_config.py`: Configuration management
- `tests/`: Unit test suite
- `setup.py`: Python packaging
- `PKGBUILD`: Arch Linux packaging

### Dependencies
**Python:**
- Use requirements.txt
- Keep dependencies minimal
- Pin versions for reproducibility

**Go:**
- Use go.mod for dependency management
- Keep dependencies minimal
- Update regularly for security

### Security
- No secrets in code
- Validate user input
- Use secure defaults
- Follow principle of least privilege
- Sanitize shell commands