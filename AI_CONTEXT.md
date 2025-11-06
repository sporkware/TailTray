# AI Development Context - TailTray

## Project Overview
**TailTray** is a Linux GUI application for Tailscale, providing the same features as the Windows Tailscale GUI. Built specifically for KDE Plasma on Arch Linux/Manjaro with Wayland support.

## Key Architectural Decisions

### Language Choice: Python (Not Rust)
**Decision**: Chose Python + GTK3 over Rust for the following reasons:
- **Rapid Development**: Python allows faster prototyping and iteration
- **GTK Integration**: PyGObject provides excellent GTK3 bindings
- **Ecosystem Maturity**: Well-established Linux desktop development tools
- **Maintenance**: Easier for contributors to work with
- **Target Platform**: KDE Plasma ecosystem is Python-friendly

**Considered but Rejected**: Rust with gtk-rs
- Would provide better performance and memory safety
- But significantly increases development complexity
- GTK Rust bindings are less mature
- Would require more specialized contributors

### Backend Integration: CLI (Not SDK)
**Decision**: Use Tailscale CLI instead of Tailscale API SDK
- **Local Daemon Access**: CLI provides direct access to local Tailscale daemon
- **Stability**: CLI interface is stable and well-documented
- **No Authentication**: Avoids API key management for local GUI
- **Error Handling**: CLI provides clear error messages and status codes

**Considered but Rejected**: Tailscale API SDK
- Requires API keys and authentication
- Designed for cloud/admin API access, not local GUI
- Would complicate local application deployment

### Platform Targeting: KDE Plasma + Arch Linux
**Decision**: Primary target is KDE Plasma on Arch Linux/Manjaro
- **User Request**: Explicitly requested KDE Plasma + Wayland support
- **System Tray**: AppIndicator3 works reliably with KDE Plasma
- **Package Management**: Arch Linux has excellent packaging tools
- **User Base**: KDE Plasma users on Arch Linux are technical and demanding

**Secondary Support**: Other desktop environments (experimental)
- GNOME, XFCE, etc. may work but not guaranteed
- Focus development efforts on primary platform

## Development Philosophy

### Modular Architecture
- **Separation of Concerns**: GUI, client logic, and configuration are separate modules
- **Testability**: Each module can be unit tested independently
- **Maintainability**: Clear boundaries between components
- **Extensibility**: Easy to add new features without affecting existing code

### Quality Standards
- **100% Test Coverage**: All code must have corresponding tests
- **Type Hints**: Full type annotation for better IDE support and error catching
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Logging**: Structured logging with appropriate levels
- **Code Style**: Black formatting, flake8 linting, mypy type checking

### User Experience Focus
- **Native Integration**: Follows KDE Plasma design patterns
- **System Tray**: Proper system tray integration with context menus
- **Wayland Compatible**: Works correctly with Wayland display server
- **Responsive**: Non-blocking operations with proper threading
- **Accessible**: Keyboard navigation and screen reader support

## Current Project State

### Completed Features (v0.1.0-alpha)
- ✅ Complete device management with search and filtering
- ✅ Exit node selection with error handling
- ✅ Taildrop file transfer functionality
- ✅ SSH connection dialogs
- ✅ Troubleshooting tools with ping and diagnostics
- ✅ MagicDNS name resolution
- ✅ System tray integration (KDE Plasma)
- ✅ Configuration system (XDG compliant)
- ✅ Comprehensive testing (20 unit tests)
- ✅ Complete packaging (PKGBUILD, setup.py, systemd, desktop files)
- ✅ Documentation (all .md files updated)

### Technical Implementation Details

#### File Structure
```
tailtray/
├── tailtray.py              # Main GTK application
├── tailscale_client.py      # CLI client with error handling
├── tailtray_config.py       # XDG config management
├── setup.py                 # Python packaging
├── PKGBUILD                 # Arch Linux packaging
├── tests/                   # Unit tests (pytest)
├── *.md                     # Documentation
└── packaging files          # Desktop, systemd, icons
```

#### Key Classes
- `TailscaleClient`: Handles all Tailscale CLI interactions with caching and error handling
- `TailTrayConfig`: Manages XDG-compliant configuration storage
- `MainWindow`: GTK application window with system tray integration
- Various dialog classes for specific features

#### Testing Strategy
- **Unit Tests**: Mock external dependencies (subprocess, file operations)
- **Integration Tests**: Basic functionality verification
- **CI/CD Ready**: pytest with coverage reporting
- **Test Coverage**: 100% for core business logic

## Future Development Priorities

### High Priority (v0.2.0-beta)
1. **Multi-distribution Support**: .deb and .rpm packages
2. **Flatpak/Snap**: Universal Linux packaging
3. **Dark Mode**: KDE Plasma theme integration
4. **Performance**: Optimize large device list handling

### Medium Priority (v0.3.0-stable)
1. **Advanced Configuration**: More user preferences
2. **Plugin Architecture**: Extensible feature system
3. **Multi-language**: i18n support
4. **Network Monitoring**: Bandwidth and connection stats

### Long Term (v1.0.0)
1. **Enterprise Features**: Admin console integration
2. **Advanced Security**: ACL management interface
3. **Commercial Support**: Enterprise deployment options

## Development Constraints & Considerations

### Platform Limitations
- **Wayland**: Some GTK features may behave differently
- **System Tray**: AppIndicator3 support varies by desktop environment
- **File Permissions**: Tailscale operations require proper user permissions
- **Display Server**: X11 vs Wayland compatibility considerations

### User Expectations
- **Windows Parity**: Feature set should match Windows GUI
- **Native Feel**: Should integrate seamlessly with KDE Plasma
- **Performance**: Should be responsive even with many devices
- **Reliability**: Should handle network issues and Tailscale daemon restarts

### Technical Debt Awareness
- **GTK Version**: GTK3 chosen for stability, GTK4 migration possible later
- **CLI Dependency**: Tied to Tailscale CLI stability
- **Python Version**: Minimum 3.8, consider 3.9+ for better typing
- **Packaging**: Multiple package formats increase maintenance burden

## AI Agent Guidelines

### When Working on This Code
1. **Read This File First**: Understand the architectural decisions and constraints
2. **Check STATUS.md**: Current development status and priorities
3. **Run Tests**: Ensure all tests pass before making changes
4. **Follow Patterns**: Maintain the established code style and architecture
5. **Update Documentation**: Keep all .md files synchronized
6. **Test on Target Platform**: Verify changes work on KDE Plasma + Wayland

### Decision-Making Framework
1. **User Requirements**: KDE Plasma + Wayland is the primary target
2. **Maintainability**: Prefer simple, well-tested solutions
3. **Performance**: Optimize for typical use cases (not extreme edge cases)
4. **Compatibility**: Ensure works with current Tailscale CLI
5. **Extensibility**: Design for future feature additions

### Common Pitfalls to Avoid
- **Over-engineering**: Keep solutions simple and focused
- **Breaking Changes**: Maintain backward compatibility where possible
- **Platform Assumptions**: Test on actual KDE Plasma environment
- **API Dependencies**: Don't rely on unstable or undocumented APIs
- **Scope Creep**: Stick to core Tailscale GUI feature parity

## Contact & Context
This context was created during the initial development phase of TailTray. If you're an AI agent working on this project, use this file to understand the project vision, constraints, and development approach.

**Last Updated**: November 5, 2025
**AI Context Version**: 1.0