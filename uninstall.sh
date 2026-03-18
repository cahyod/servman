#!/bin/bash
# Service Manager - Uninstallation Script

set -e

INSTALL_DIR="${INSTALL_DIR:-/opt/service-manager}"
DESKTOP_FILE="/usr/share/applications/service-manager.desktop"

echo "==================================="
echo "  Service Manager Uninstaller"
echo "==================================="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo ./uninstall.sh"
    exit 1
fi

# Remove application
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
    echo "Application removed."
else
    echo "Application directory not found: $INSTALL_DIR"
fi

# Remove desktop file
if [ -f "$DESKTOP_FILE" ]; then
    echo "Removing desktop file..."
    rm -f "$DESKTOP_FILE"
    update-desktop-database 2>/dev/null || true
    echo "Desktop file removed."
else
    echo "Desktop file not found: $DESKTOP_FILE"
fi

echo
echo "==================================="
echo "  Uninstallation Complete!"
echo "==================================="
echo
