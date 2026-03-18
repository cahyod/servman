#!/bin/bash
# Service Manager - Installation Script
# This script installs Service Manager to your system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${INSTALL_DIR:-/opt/service-manager}"
DESKTOP_FILE="/usr/share/applications/service-manager.desktop"

echo "==================================="
echo "  Service Manager Installer"
echo "==================================="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo ./install.sh"
    exit 1
fi

# Check dependencies
echo "Checking dependencies..."
MISSING_DEPS=()

if ! command -v python3 &> /dev/null; then
    MISSING_DEPS+=("python3")
fi

if ! python3 -c "import gi" &> /dev/null; then
    MISSING_DEPS+=("python3-gi")
fi

if ! python3 -c "gi.require_version('Gtk', '3.0')" &> /dev/null; then
    MISSING_DEPS+=("gir1.2-gtk-3.0")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "Missing dependencies: ${MISSING_DEPS[*]}"
    echo "Installing missing dependencies..."
    apt-get update
    apt-get install -y "${MISSING_DEPS[@]}"
fi

echo "Dependencies OK!"
echo

# Install application
echo "Installing Service Manager to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/service_manager.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/run_service_manager.sh" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/service_manager.py"
chmod +x "$INSTALL_DIR/run_service_manager.sh"

# Update desktop file path
echo "Updating desktop file..."
sed "s|Exec=.*|Exec=$INSTALL_DIR/run_service_manager.sh|" "$SCRIPT_DIR/service-manager.desktop" > "$DESKTOP_FILE"
chmod +x "$DESKTOP_FILE"

# Update desktop database
update-desktop-database 2>/dev/null || true

echo
echo "==================================="
echo "  Installation Complete!"
echo "==================================="
echo
echo "Service Manager has been installed to: $INSTALL_DIR"
echo "Desktop file installed to: $DESKTOP_FILE"
echo
echo "You can now:"
echo "  - Launch from Applications menu"
echo "  - Run: $INSTALL_DIR/run_service_manager.sh"
echo "  - Uninstall: sudo ./uninstall.sh"
echo
