# Changelog

All notable changes to Service Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Service search/filter by name
- Service details panel with full information
- Export service list to CSV/JSON
- Dark mode support
- Custom service groups/categories
- Service startup type configuration
- Log viewer for each service

## [1.1.0] - 2024-01-XX

### Added
- Desktop file for application menu integration
- Unix-style icons for all buttons
- CONTRIBUTING.md for community contributions
- CHANGELOG.md for version tracking
- LICENSE file (MIT)

### Changed
- Improved bulk operation to require single authentication
- Replaced emoji characters with system icons
- Simplified CSS styling for better compatibility

### Fixed
- Text visibility issues on colored buttons
- GTK markup parsing errors
- TreeViewColumn sizing compatibility

## [1.0.0] - 2024-01-XX

### Added
- Initial release
- Service monitoring with real-time status
- Multi-select checkbox functionality
- Bulk start/stop/restart operations
- Service filtering (All/Running/Custom/Custom Running)
- Quick selection tools (Select All/Deselect All/Select Running/Select Stopped)
- Auto-refresh every 30 seconds
- Right-click context menu
- Single service operations
- Default vs custom service distinction
- Status bar with operation feedback
- Error handling and dialogs
- Background threading for non-blocking operations

---

## Version Meanings

- **MAJOR.MINOR.PATCH**
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Release Notes

### Version 1.0.0 - Initial Release

The first stable release includes:

- Full GTK3 GUI application
- Systemd service management
- Multi-select operations
- Smart filtering
- Desktop integration

### Getting Started

```bash
git clone https://github.com/yourusername/service-manager.git
cd service-manager
./run_service_manager.sh
```

---

*For more information, see [README.md](README.md)*
