#!/usr/bin/env python3
"""
Service Manager - GUI application for monitoring and controlling systemd services
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject
import subprocess
import threading

# Default Ubuntu Desktop services (to filter out)
DEFAULT_SERVICES = {
    'accounts-daemon', 'auditd', 'avahi-daemon', 'bluetooth', 'bolt',
    'colord', 'cron', 'cups', 'cups-browsed', 'dbus', 'fwupd',
    'gdm', 'gnome-remote-desktop', 'kerneloops', 'ModemManager',
    'NetworkManager', 'open-fprintd', 'polkit', 'power-profiles-daemon',
    'python3-validity', 'rsyslog', 'rtkit-daemon', 'snapd',
    'switcheroo-control', 'systemd-journald', 'systemd-logind',
    'systemd-machined', 'systemd-oomd', 'systemd-resolved',
    'systemd-timesyncd', 'systemd-udevd', 'thermald', 'udisks2',
    'unattended-upgrades', 'upower', 'wpa_supplicant', 'user'
}

# Custom services (non-default)
CUSTOM_SERVICES = {
    'anydesk', 'caddy', 'containerd', 'docker', 'ollama',
    'ovs-vswitchd', 'ovsdb-server', 'virtlockd', 'virtlogd'
}


class ServiceInfo:
    def __init__(self, name, load, active, sub, description):
        self.name = name
        self.load = load
        self.active = active
        self.sub = sub
        self.description = description
        self.is_custom = name.split('.')[0] in CUSTOM_SERVICES


class ServiceManagerWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Service Manager")
        self.set_default_size(1000, 650)
        self.set_border_width(10)
        
        # Add custom CSS
        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_data(b"""
            .custom-service {
                background-color: #e3f2fd;
            }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)
        
        # Header with icon
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(header_box, False, False, 5)
        
        # Application icon
        icon_image = Gtk.Image.new_from_icon_name("system-run", Gtk.IconSize.DIALOG)
        header_box.pack_start(icon_image, False, False, 0)
        
        header = Gtk.Label()
        header.set_markup("<b><span size='large'>Systemd Service Manager</span></b>")
        header_box.pack_start(header, False, False, 0)
        
        # Filter options
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(filter_box, False, False, 5)
        
        filter_label = Gtk.Label(label="Filter:")
        filter_box.pack_start(filter_label, False, False, 0)
        
        self.filter_combo = Gtk.ComboBoxText()
        self.filter_combo.append_text("All Services")
        self.filter_combo.append_text("Running Only")
        self.filter_combo.append_text("Custom Services Only")
        self.filter_combo.append_text("Custom Running Only")
        self.filter_combo.set_active(2)  # Default to Custom Services Only
        self.filter_combo.connect("changed", self.on_filter_changed)
        filter_box.pack_start(self.filter_combo, False, False, 0)
        
        # Selection count label
        self.selection_count_label = Gtk.Label(label="Selected: 0")
        self.selection_count_label.set_halign(Gtk.Align.START)
        filter_box.pack_start(self.selection_count_label, False, False, 10)
        
        # Refresh button
        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.set_image(Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON))
        refresh_btn.set_always_show_image(True)
        refresh_btn.connect("clicked", self.on_refresh)
        filter_box.pack_end(refresh_btn, False, False, 0)
        
        self.status_label = Gtk.Label(label="")
        self.status_label.set_halign(Gtk.Align.END)
        filter_box.pack_end(self.status_label, False, False, 0)
        
        # Create list store (added 'selected' boolean column at index 0)
        self.list_store = Gtk.ListStore(bool, str, str, str, str, bool)
        
        # Tree view
        self.tree_view = Gtk.TreeView(model=self.list_store)
        self.tree_view.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        
        # Checkbox column for multi-select
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_cell_toggled)
        column_select = Gtk.TreeViewColumn("Select", renderer_toggle)
        column_select.set_cell_data_func(renderer_toggle, self.cell_data_func)
        column_select.set_resizable(False)
        column_select.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.tree_view.append_column(column_select)
        
        # Columns
        columns = [
            ("Service Name", 1),
            ("Status", 2),
            ("State", 3),
            ("Description", 4)
        ]
        
        for title, col_idx in columns:
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=col_idx)
            column.set_resizable(True)
            column.set_expand(col_idx == 4)  # Description column expands
            self.tree_view.append_column(column)
        
        # Selection (for single operations via right-click)
        self.selection = self.tree_view.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.selection.connect("changed", self.on_selection_changed)
        
        # Scrollable area
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_window.add(self.tree_view)
        main_box.pack_start(scroll_window, True, True, 0)
        
        # Selection buttons
        select_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(select_box, False, False, 0)

        select_all_btn = Gtk.Button(label="Select All")
        select_all_btn.set_image(Gtk.Image.new_from_icon_name("object-select", Gtk.IconSize.BUTTON))
        select_all_btn.set_always_show_image(True)
        select_all_btn.connect("clicked", self.on_select_all)
        select_box.pack_start(select_all_btn, False, False, 0)

        deselect_all_btn = Gtk.Button(label="Deselect All")
        deselect_all_btn.set_image(Gtk.Image.new_from_icon_name("object-select", Gtk.IconSize.BUTTON))
        deselect_all_btn.set_always_show_image(True)
        deselect_all_btn.connect("clicked", self.on_deselect_all)
        select_box.pack_start(deselect_all_btn, False, False, 0)

        select_running_btn = Gtk.Button(label="Select Running")
        select_running_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON))
        select_running_btn.set_always_show_image(True)
        select_running_btn.connect("clicked", self.on_select_running)
        select_box.pack_start(select_running_btn, False, False, 0)

        select_stopped_btn = Gtk.Button(label="Select Stopped")
        select_stopped_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-pause", Gtk.IconSize.BUTTON))
        select_stopped_btn.set_always_show_image(True)
        select_stopped_btn.connect("clicked", self.on_select_stopped)
        select_box.pack_start(select_stopped_btn, False, False, 0)

        # Control buttons
        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(control_box, False, False, 5)

        self.start_btn = Gtk.Button(label="Start Selected")
        self.start_btn.set_image(Gtk.Image.new_from_icon_name("system-run", Gtk.IconSize.BUTTON))
        self.start_btn.set_always_show_image(True)
        self.start_btn.connect("clicked", self.on_start)
        self.start_btn.set_sensitive(False)
        control_box.pack_start(self.start_btn, False, False, 0)

        self.stop_btn = Gtk.Button(label="Stop Selected")
        self.stop_btn.set_image(Gtk.Image.new_from_icon_name("process-stop", Gtk.IconSize.BUTTON))
        self.stop_btn.set_always_show_image(True)
        self.stop_btn.connect("clicked", self.on_stop)
        self.stop_btn.set_sensitive(False)
        control_box.pack_start(self.stop_btn, False, False, 0)

        self.restart_btn = Gtk.Button(label="Restart Selected")
        self.restart_btn.set_image(Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON))
        self.restart_btn.set_always_show_image(True)
        self.restart_btn.connect("clicked", self.on_restart)
        self.restart_btn.set_sensitive(False)
        control_box.pack_start(self.restart_btn, False, False, 0)

        # Single service buttons (for right-click context menu)
        single_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(single_box, False, False, 0)

        single_label = Gtk.Label(label="Single Service (via selection):")
        single_label.set_halign(Gtk.Align.END)
        single_box.pack_start(single_label, True, True, 0)

        self.single_start_btn = Gtk.Button(label="Start")
        self.single_start_btn.set_image(Gtk.Image.new_from_icon_name("system-run", Gtk.IconSize.BUTTON))
        self.single_start_btn.set_always_show_image(True)
        self.single_start_btn.connect("clicked", self.on_single_start)
        self.single_start_btn.set_sensitive(False)
        single_box.pack_start(self.single_start_btn, False, False, 0)

        self.single_stop_btn = Gtk.Button(label="Stop")
        self.single_stop_btn.set_image(Gtk.Image.new_from_icon_name("process-stop", Gtk.IconSize.BUTTON))
        self.single_stop_btn.set_always_show_image(True)
        self.single_stop_btn.connect("clicked", self.on_single_stop)
        single_box.pack_start(self.single_stop_btn, False, False, 0)

        self.single_restart_btn = Gtk.Button(label="Restart")
        self.single_restart_btn.set_image(Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON))
        self.single_restart_btn.set_always_show_image(True)
        self.single_restart_btn.connect("clicked", self.on_single_restart)
        single_box.pack_start(self.single_restart_btn, False, False, 0)
        
        # Status bar
        self.status_bar = Gtk.Statusbar()
        self.status_bar.set_halign(Gtk.Align.FILL)
        main_box.pack_start(self.status_bar, False, False, 0)
        
        # Context menu
        self.tree_view.connect("button-press-event", self.on_treeview_button_press)
        
        # Load services
        self.services_data = []
        self.load_services()
        
        # Auto-refresh every 30 seconds
        GObject.timeout_add(30000, self.auto_refresh)
    
    def cell_data_func(self, column, cell, model, tree_iter, data):
        """Set checkbox state based on model data"""
        cell.set_active(model[tree_iter][0])  # Column 0 is 'selected'
    
    def on_cell_toggled(self, renderer, path):
        """Handle checkbox toggle"""
        tree_iter = self.list_store.get_iter(path)
        current_value = self.list_store[tree_iter][0]
        self.list_store[tree_iter][0] = not current_value
        self.update_selection_count()
        self.update_button_states()
    
    def update_selection_count(self):
        """Update the selection count label"""
        count = sum(1 for row in self.list_store if row[0])
        self.selection_count_label.set_label(f"Selected: {count}")
    
    def update_button_states(self):
        """Update button states based on selection"""
        selected_count = sum(1 for row in self.list_store if row[0])
        selected_running = sum(1 for row in self.list_store if row[0] and row[2] == "Running")
        selected_stopped = sum(1 for row in self.list_store if row[0] and row[2] == "Stopped")
        
        # Bulk action buttons
        self.start_btn.set_sensitive(selected_stopped > 0)
        self.stop_btn.set_sensitive(selected_running > 0)
        self.restart_btn.set_sensitive(selected_running > 0)
        
        # Single service buttons
        model, tree_iter = self.selection.get_selected()
        if tree_iter:
            status = model[tree_iter][2]
            self.single_start_btn.set_sensitive(status == "Stopped")
            self.single_stop_btn.set_sensitive(status == "Running")
        else:
            self.single_start_btn.set_sensitive(False)
            self.single_stop_btn.set_sensitive(False)
    
    def get_selected_services(self):
        """Get list of selected service names"""
        selected = []
        for row in self.list_store:
            if row[0]:  # If checkbox is checked
                selected.append(row[1])  # Service name
        return selected
    
    def get_selected_services_with_status(self):
        """Get list of selected services with their status"""
        selected = []
        for row in self.list_store:
            if row[0]:  # If checkbox is checked
                selected.append((row[1], row[2]))  # (name, status)
        return selected
    
    def load_services(self):
        """Load services in a background thread"""
        self.set_status("Loading services...")
        thread = threading.Thread(target=self._load_services_thread)
        thread.daemon = True
        thread.start()
    
    def _load_services_thread(self):
        """Background thread to load services"""
        try:
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--all', '--no-pager', '--no-legend'],
                capture_output=True, text=True, timeout=30
            )
            
            services = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 5:
                    name = parts[0]
                    load = parts[1]
                    active = parts[2]
                    sub = parts[3]
                    description = ' '.join(parts[4:])
                    
                    service = ServiceInfo(name, load, active, sub, description)
                    services.append(service)
            
            GLib.idle_add(self._update_list_store, services)
        except Exception as e:
            GLib.idle_add(self.set_status, f"Error: {str(e)}")
    
    def _update_list_store(self, services):
        """Update the list store with services data"""
        self.services_data = services
        self.list_store.clear()
        
        for service in services:
            status = "Running" if service.sub == "running" else "Stopped"
            self.list_store.append([
                False,  # Selected (checkbox) - default unchecked
                service.name,
                status,
                service.sub,
                service.description,
                service.is_custom
            ])
        
        self.apply_filter()
        self.set_status(f"Loaded {len(services)} services")
    
    def apply_filter(self):
        """Apply the selected filter"""
        filter_type = self.filter_combo.get_active()
        
        # Preserve current selections by service name
        preserved_selections = set(self.get_selected_services())
        
        # Clear and repopulate based on filter
        self.list_store.clear()
        
        for service in self.services_data:
            show = True
            
            if filter_type == 1:  # Running Only
                show = service.sub == "running"
            elif filter_type == 2:  # Custom Services Only
                show = service.is_custom
            elif filter_type == 3:  # Custom Running Only
                show = service.is_custom and service.sub == "running"
            
            if show:
                status = "Running" if service.sub == "running" else "Stopped"
                # Preserve selection if service was previously selected
                is_selected = service.name in preserved_selections
                self.list_store.append([
                    is_selected,
                    service.name,
                    status,
                    service.sub,
                    service.description,
                    service.is_custom
                ])
        
        self.update_selection_count()
        self.update_button_states()
    
    def on_filter_changed(self, widget):
        """Handle filter change"""
        self.apply_filter()
    
    def on_select_all(self, widget):
        """Select all visible services"""
        for row in self.list_store:
            row[0] = True
        self.update_selection_count()
        self.update_button_states()
    
    def on_deselect_all(self, widget):
        """Deselect all services"""
        for row in self.list_store:
            row[0] = False
        self.update_selection_count()
        self.update_button_states()
    
    def on_select_running(self, widget):
        """Select all running services"""
        for row in self.list_store:
            row[0] = (row[2] == "Running")
        self.update_selection_count()
        self.update_button_states()
    
    def on_select_stopped(self, widget):
        """Select all stopped services"""
        for row in self.list_store:
            row[0] = (row[2] == "Stopped")
        self.update_selection_count()
        self.update_button_states()
    
    def on_selection_changed(self, selection):
        """Handle selection change"""
        self.update_button_states()

    def on_refresh(self, widget):
        """Refresh button clicked"""
        self.load_services()

    def auto_refresh(self):
        """Auto-refresh services"""
        self.load_services()
        return True  # Continue timeout

    def on_start(self, widget):
        """Start selected services"""
        selected = self.get_selected_services_with_status()
        to_start = [name for name, status in selected if status == "Stopped"]
        if to_start:
            self.execute_bulk_service_command("start", to_start)
    
    def on_stop(self, widget):
        """Stop selected services"""
        selected = self.get_selected_services_with_status()
        to_stop = [name for name, status in selected if status == "Running"]
        if to_stop:
            self.execute_bulk_service_command("stop", to_stop)
    
    def on_restart(self, widget):
        """Restart selected services"""
        selected = self.get_selected_services_with_status()
        to_restart = [name for name, status in selected if status == "Running"]
        if to_restart:
            self.execute_bulk_service_command("restart", to_restart)
    
    def on_single_start(self, widget):
        """Start single selected service"""
        model, tree_iter = self.selection.get_selected()
        if tree_iter:
            service_name = model[tree_iter][1]
            self.execute_service_command("start", service_name)
    
    def on_single_stop(self, widget):
        """Stop single selected service"""
        model, tree_iter = self.selection.get_selected()
        if tree_iter:
            service_name = model[tree_iter][1]
            self.execute_service_command("stop", service_name)
    
    def on_single_restart(self, widget):
        """Restart single selected service"""
        model, tree_iter = self.selection.get_selected()
        if tree_iter:
            service_name = model[tree_iter][1]
            self.execute_service_command("restart", service_name)
    
    def execute_service_command(self, action, service_name):
        """Execute systemctl command for a single service"""
        self.set_status(f"{action.capitalize()}ing {service_name}...")
        thread = threading.Thread(target=self._execute_command_thread, args=(action, service_name))
        thread.daemon = True
        thread.start()
    
    def execute_bulk_service_command(self, action, service_names):
        """Execute systemctl command for multiple services"""
        count = len(service_names)
        self.set_status(f"{action.capitalize()}ing {count} service(s)...")
        thread = threading.Thread(target=self._execute_bulk_command_thread, args=(action, service_names))
        thread.daemon = True
        thread.start()
    
    def _execute_command_thread(self, action, service_name):
        """Background thread to execute systemctl command for single service"""
        try:
            result = subprocess.run(
                ['pkexec', 'systemctl', action, service_name],
                capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                GLib.idle_add(self.set_status, f"Successfully {action}ed {service_name}")
                GLib.idle_add(self.load_services)
            else:
                error_msg = result.stderr.strip() or "Failed to execute command"
                GLib.idle_add(self.set_status, f"Error: {error_msg}")
                GLib.idle_add(self.show_error_dialog, f"Failed to {action} {service_name}\n\n{error_msg}")
        except Exception as e:
            GLib.idle_add(self.set_status, f"Error: {str(e)}")
            GLib.idle_add(self.show_error_dialog, f"Failed to {action} service\n\n{str(e)}")
    
    def _execute_bulk_command_thread(self, action, service_names):
        """Background thread to execute systemctl command for multiple services"""
        try:
            # Execute all services in a single pkexec/systemctl call
            result = subprocess.run(
                ['pkexec', 'systemctl', action] + service_names,
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                success_count = len(service_names)
                GLib.idle_add(self.set_status, f"Completed: {success_count} service(s) {action}ed successfully")
                GLib.idle_add(self.load_services)
            else:
                error_msg = result.stderr.strip() or "Failed to execute command"
                # Try to parse which services failed
                GLib.idle_add(self.set_status, f"Error: {error_msg}")
                GLib.idle_add(self.show_error_dialog, f"Failed to {action} services:\n\n{error_msg}")
        except Exception as e:
            GLib.idle_add(self.set_status, f"Error: {str(e)}")
            GLib.idle_add(self.show_error_dialog, f"Failed to {action} services\n\n{str(e)}")
    
    def show_error_dialog(self, message):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def set_status(self, message):
        """Set status bar message"""
        self.status_bar.push(0, message)
    
    def on_treeview_button_press(self, widget, event):
        """Handle right-click context menu"""
        if event.button == 3:  # Right click
            path = self.tree_view.get_path_at_pos(int(event.x), int(event.y))
            if path:
                self.tree_view.grab_focus()
                self.tree_view.set_cursor(path[0], path[1], False)

                menu = Gtk.Menu()

                start_item = Gtk.MenuItem(label="Start")
                start_item.connect("activate", self.on_single_start)
                menu.append(start_item)

                stop_item = Gtk.MenuItem(label="Stop")
                stop_item.connect("activate", self.on_single_stop)
                menu.append(stop_item)

                restart_item = Gtk.MenuItem(label="Restart")
                restart_item.connect("activate", self.on_single_restart)
                menu.append(restart_item)

                menu.append(Gtk.SeparatorMenuItem())
                
                # Bulk actions
                bulk_start_item = Gtk.MenuItem(label="Start Selected")
                bulk_start_item.connect("activate", self.on_start)
                menu.append(bulk_start_item)
                
                bulk_stop_item = Gtk.MenuItem(label="Stop Selected")
                bulk_stop_item.connect("activate", self.on_stop)
                menu.append(bulk_stop_item)
                
                bulk_restart_item = Gtk.MenuItem(label="Restart Selected")
                bulk_restart_item.connect("activate", self.on_restart)
                menu.append(bulk_restart_item)

                menu.append(Gtk.SeparatorMenuItem())

                refresh_item = Gtk.MenuItem(label="Refresh")
                refresh_item.connect("activate", self.on_refresh)
                menu.append(refresh_item)

                menu.show_all()
                menu.popup_at_pointer(event)
                return True


def main():
    win = ServiceManagerWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
