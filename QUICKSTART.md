# Service Manager - Quick Reference

## Installation

### Quick Start (No Install)
```bash
git clone https://github.com/yourusername/service-manager.git
cd service-manager
./run_service_manager.sh
```

### System-Wide Installation
```bash
sudo ./install.sh
```

### Uninstall
```bash
sudo ./uninstall.sh
```

## Usage

### Launch
```bash
# From directory
./run_service_manager.sh

# From anywhere (after install)
service-manager

# From Applications menu
Search "Service Manager"
```

### Keyboard Shortcuts
| Action | Shortcut |
|--------|----------|
| Refresh | F5 |
| Select All | Ctrl+A |
| Deselect All | Ctrl+Shift+A |
| Start Selected | Ctrl+S |
| Stop Selected | Ctrl+T |
| Restart Selected | Ctrl+R |

### Features Overview

#### Selection Tools
- **Checkboxes** - Select individual services
- **Select All** - Select all visible services
- **Deselect All** - Clear all selections
- **Select Running** - Select all running services
- **Select Stopped** - Select all stopped services

#### Filters
- **All Services** - Show everything
- **Running Only** - Show active services
- **Custom Services Only** - Show non-default services (default)
- **Custom Running Only** - Show active custom services

#### Actions
- **Start Selected** - Start all selected stopped services
- **Stop Selected** - Stop all selected running services
- **Restart Selected** - Restart all selected running services
- **Single Service** - Actions for individually selected service

#### Context Menu (Right-Click)
- Start/Stop/Restart (single service)
- Start/Stop/Restart Selected (bulk)
- Refresh

## Troubleshooting

### App won't start
```bash
# Check dependencies
python3 -c "import gi; gi.require_version('Gtk', '3.0'); print('OK')"

# Install if needed
sudo apt install python3-gi gir1.2-gtk-3.0
```

### Permission errors
```bash
# Ensure polkit is running
systemctl status polkit

# Install if missing
sudo apt install polkit
```

### Icons missing
The app uses standard GTK icons. If icons don't display, check your icon theme.

## Custom Services List

Default custom services detected:
- anydesk
- caddy
- containerd
- docker
- ollama
- ovs-vswitchd
- ovsdb-server
- virtlockd
- virtlogd

To add more, edit `CUSTOM_SERVICES` in `service_manager.py`.

## Configuration

### Auto-refresh Interval
Edit line in `service_manager.py`:
```python
GObject.timeout_add(30000, self.auto_refresh)  # 30000 = 30 seconds
```

### Default Filter
Edit line in `service_manager.py`:
```python
self.filter_combo.set_active(2)  # 0=All, 1=Running, 2=Custom, 3=Custom Running
```

## Support

- **Issues**: https://github.com/yourusername/service-manager/issues
- **Discussions**: https://github.com/yourusername/service-manager/discussions

## License

MIT License - See LICENSE file for details.
