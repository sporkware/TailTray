#!/usr/bin/env python3
"""
TailTray - Tailscale GUI for Linux
Provides the same features as the Windows Tailscale GUI

Copyright (c) 2025 TailTray Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the MIT License as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
MIT License for more details.

You should have received a copy of the MIT License
along with this program. If not, see <https://opensource.org/licenses/MIT>.
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, Gdk, GLib, AppIndicator3
import subprocess
import threading
import os
import sys
import logging

# Import the core client logic
from tailscale_client import TailscaleClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tailtray.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Note: Tailscale SDK is for cloud API, not local daemon
# Using CLI for local Tailscale daemon interaction
API_AVAILABLE = False




class DeviceDialog(Gtk.Dialog):
    """Dialog for device details and actions"""

    def __init__(self, parent, device, ts_client):
        super().__init__(title=f"Device: {device['HostName']}", parent=parent, flags=0)
        self.device = device
        self.ts_client = ts_client

        self.set_default_size(400, 300)
        self.set_modal(True)

        box = self.get_content_area()
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)

        # Device info
        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(12)

        labels = [
            ("Hostname:", device.get('HostName', 'Unknown')),
            ("DNS Name:", device.get('DNSName', 'N/A')),
            ("IP Address:", device.get('Addresses', ['N/A'])[0] if device.get('Addresses') else 'N/A'),
            ("OS:", device.get('OS', 'Unknown')),
            ("Online:", "Yes" if device.get('Online', False) else "No"),
            ("Exit Node:", "Yes" if device.get('ExitNodeOption', False) else "No"),
        ]

        for i, (label_text, value) in enumerate(labels):
            label = Gtk.Label(label_text)
            label.set_halign(Gtk.Align.START)
            grid.attach(label, 0, i, 1, 1)

            value_label = Gtk.Label(value)
            value_label.set_halign(Gtk.Align.START)
            grid.attach(value_label, 1, i, 1, 1)

        box.pack_start(grid, True, True, 0)

        # Action buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_margin_top(12)

        if device.get('Online', False):
            ping_btn = Gtk.Button(label="Ping")
            ping_btn.connect("clicked", self.on_ping)
            button_box.pack_start(ping_btn, False, False, 0)

            if device.get('ExitNodeOption', False):
                exit_btn = Gtk.Button(label="Set as Exit Node")
                exit_btn.connect("clicked", self.on_set_exit_node)
                button_box.pack_start(exit_btn, False, False, 0)

        close_btn = Gtk.Button(label="Close")
        close_btn.connect("clicked", lambda w: self.destroy())
        button_box.pack_end(close_btn, False, False, 0)

        box.pack_start(button_box, False, False, 0)

        self.show_all()

    def on_ping(self, button):
        success, stdout, stderr = self.ts_client.ping_device(self.device['HostName'])
        if success:
            dialog = Gtk.MessageDialog(
                self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                f"Ping successful:\n{stdout}"
            )
        else:
            dialog = Gtk.MessageDialog(
                self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                f"Ping failed:\n{stderr}"
            )
        dialog.run()
        dialog.destroy()

    def on_set_exit_node(self, button):
        ip = self.device.get('Addresses', [''])[0] if self.device.get('Addresses') else ''
        if self.ts_client.set_exit_node(ip):
            dialog = Gtk.MessageDialog(
                self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                "Exit node set successfully"
            )
            dialog.run()
            dialog.destroy()
        else:
            dialog = Gtk.MessageDialog(
                self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                "Failed to set exit node"
            )
            dialog.run()
            dialog.destroy()


class ExitNodeDialog(Gtk.Dialog):
    """Dialog for selecting exit node"""

    def __init__(self, parent, ts_client):
        super().__init__(title="Select Exit Node", parent=parent, flags=0)
        self.ts_client = ts_client

        self.set_default_size(400, 200)
        self.set_modal(True)

        box = self.get_content_area()
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)

        # Exit node list
        scrolled = Gtk.ScrolledWindow()
        self.liststore = Gtk.ListStore(str, str, bool)  # hostname, ip, selected

        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview.set_headers_visible(True)

        # Columns
        renderer_text = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Device", renderer_text, text=0)
        self.treeview.append_column(column)

        column = Gtk.TreeViewColumn("IP Address", renderer_text, text=1)
        self.treeview.append_column(column)

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_toggle)
        column = Gtk.TreeViewColumn("Use as Exit Node", renderer_toggle, active=2)
        self.treeview.append_column(column)

        scrolled.add(self.treeview)
        box.pack_start(scrolled, True, True, 0)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_margin_top(12)

        set_btn = Gtk.Button(label="Set")
        set_btn.connect("clicked", self.on_set)
        button_box.pack_start(set_btn, False, False, 0)

        disable_btn = Gtk.Button(label="Disable")
        disable_btn.connect("clicked", self.on_disable)
        button_box.pack_start(disable_btn, False, False, 0)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda w: self.destroy())
        button_box.pack_end(cancel_btn, False, False, 0)

        box.pack_start(button_box, False, False, 0)

        self.load_exit_nodes()
        self.show_all()

    def load_exit_nodes(self):
        self.liststore.clear()

        # Add "None" option
        self.liststore.append(["None (Direct connection)", "", False])

        # Add exit nodes
        exit_nodes = self.ts_client.get_exit_nodes()
        for node in exit_nodes:
            ip = node.get('Addresses', [''])[0] if node.get('Addresses') else ''
            self.liststore.append([node['HostName'], ip, node.get('ExitNode', False)])

    def on_toggle(self, widget, path):
        # Clear all selections
        for row in self.liststore:
            row[2] = False

        # Set selected
        self.liststore[path][2] = True

    def on_set(self, button):
        for row in self.liststore:
            if row[2]:
                if row[0] == "None (Direct connection)":
                    self.ts_client.set_exit_node("")
                else:
                    self.ts_client.set_exit_node(row[1])
                break
        self.destroy()

    def on_disable(self, button):
        self.ts_client.set_exit_node("")
        self.destroy()


class TaildropDialog(Gtk.Dialog):
    """Dialog for sending files via Taildrop"""

    def __init__(self, parent, ts_client):
        super().__init__(title="Send File with Taildrop", parent=parent, flags=0)
        self.ts_client = ts_client

        self.set_default_size(400, 150)
        self.set_modal(True)

        box = self.get_content_area()
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)

        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(12)

        # Device selection
        device_label = Gtk.Label("Send to device:")
        device_label.set_halign(Gtk.Align.START)
        grid.attach(device_label, 0, 0, 1, 1)

        self.device_combo = Gtk.ComboBoxText()
        self.populate_devices()
        grid.attach(self.device_combo, 1, 0, 1, 1)

        # File selection
        file_label = Gtk.Label("Select file:")
        file_label.set_halign(Gtk.Align.START)
        grid.attach(file_label, 0, 1, 1, 1)

        self.file_chooser = Gtk.FileChooserButton(title="Select File")
        grid.attach(self.file_chooser, 1, 1, 1, 1)

        box.pack_start(grid, True, True, 0)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_margin_top(12)

        send_btn = Gtk.Button(label="Send")
        send_btn.connect("clicked", self.on_send)
        button_box.pack_start(send_btn, False, False, 0)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda w: self.destroy())
        button_box.pack_end(cancel_btn, False, False, 0)

        box.pack_start(button_box, False, False, 0)

        self.show_all()

    def populate_devices(self):
        devices = self.ts_client.get_devices()
        for device in devices:
            if device.get('Online', False):
                display_name = device['HostName']
                if device.get('DNSName') and device['DNSName'] != device['HostName']:
                    display_name += f" ({device['DNSName']})"
                self.device_combo.append_text(display_name)

        if len(devices) > 0:
            self.device_combo.set_active(0)

    def on_send(self, button):
        device_text = self.device_combo.get_active_text()
        if not device_text:
            return

        # Extract hostname
        hostname = device_text.split(' (')[0]

        file_path = self.file_chooser.get_filename()
        if not file_path:
            return

        if self.ts_client.taildrop_send(hostname, file_path):
            dialog = Gtk.MessageDialog(
                self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                f"File sent successfully to {hostname}"
            )
            dialog.run()
            dialog.destroy()
            self.destroy()
        else:
            dialog = Gtk.MessageDialog(
                self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                "Failed to send file"
            )
            dialog.run()
            dialog.destroy()


class SSHDialog(Gtk.Dialog):
    """Dialog for SSH connections"""

    def __init__(self, parent, ts_client):
        super().__init__(title="Connect via Tailscale SSH", parent=parent, flags=0)
        self.ts_client = ts_client

        self.set_default_size(400, 150)
        self.set_modal(True)

        box = self.get_content_area()
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)

        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(12)

        # Device selection
        device_label = Gtk.Label("Connect to device:")
        device_label.set_halign(Gtk.Align.START)
        grid.attach(device_label, 0, 0, 1, 1)

        self.device_combo = Gtk.ComboBoxText()
        self.populate_devices()
        grid.attach(self.device_combo, 1, 0, 1, 1)

        # User
        user_label = Gtk.Label("Username:")
        user_label.set_halign(Gtk.Align.START)
        grid.attach(user_label, 0, 1, 1, 1)

        self.user_entry = Gtk.Entry()
        self.user_entry.set_text("root")
        grid.attach(self.user_entry, 1, 1, 1, 1)

        box.pack_start(grid, True, True, 0)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_margin_top(12)

        connect_btn = Gtk.Button(label="Connect")
        connect_btn.connect("clicked", self.on_connect)
        button_box.pack_start(connect_btn, False, False, 0)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda w: self.destroy())
        button_box.pack_end(cancel_btn, False, False, 0)

        box.pack_start(button_box, False, False, 0)

        self.show_all()

    def populate_devices(self):
        devices = self.ts_client.get_devices()
        for device in devices:
            if device.get('Online', False):
                display_name = device['HostName']
                if device.get('DNSName') and device['DNSName'] != device['HostName']:
                    display_name += f" ({device['DNSName']})"
                self.device_combo.append_text(display_name)

        if len(devices) > 0:
            self.device_combo.set_active(0)

    def on_connect(self, button):
        device_text = self.device_combo.get_active_text()
        if not device_text:
            return

        hostname = device_text.split(' (')[0]
        username = self.user_entry.get_text() or "root"

        # Try to launch SSH in a terminal
        terminals = ["gnome-terminal", "konsole", "xfce4-terminal", "xterm"]
        cmd = None

        for terminal in terminals:
            if self.check_command_exists(terminal):
                cmd = [terminal, "-e", f"tailscale ssh {username}@{hostname}"]
                break

        if not cmd:
            cmd = ["tailscale", "ssh", f"{username}@{hostname}"]

        try:
            subprocess.Popen(cmd)
            self.destroy()
        except Exception as e:
            dialog = Gtk.MessageDialog(
                self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                f"Failed to start SSH: {e}"
            )
            dialog.run()
            dialog.destroy()

    def check_command_exists(self, cmd):
        return subprocess.run(["which", cmd], capture_output=True).returncode == 0


class TroubleshootingDialog(Gtk.Dialog):
    """Dialog for troubleshooting"""

    def __init__(self, parent, ts_client):
        super().__init__(title="Troubleshooting", parent=parent, flags=0)
        self.ts_client = ts_client

        self.set_default_size(600, 400)
        self.set_modal(True)

        box = self.get_content_area()
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_margin_bottom(12)

        ping_btn = Gtk.Button(label="Test Connectivity")
        ping_btn.connect("clicked", self.test_connectivity)
        button_box.pack_start(ping_btn, False, False, 0)

        status_btn = Gtk.Button(label="Get Status")
        status_btn.connect("clicked", self.show_status)
        button_box.pack_start(status_btn, False, False, 0)

        logs_btn = Gtk.Button(label="Show Logs")
        logs_btn.connect("clicked", self.show_logs)
        button_box.pack_start(logs_btn, False, False, 0)

        close_btn = Gtk.Button(label="Close")
        close_btn.connect("clicked", lambda w: self.destroy())
        button_box.pack_end(close_btn, False, False, 0)

        box.pack_start(button_box, False, False, 0)

        # Text view
        scrolled = Gtk.ScrolledWindow()
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled.add(self.textview)
        box.pack_start(scrolled, True, True, 0)

        self.show_status()
        self.show_all()

    def append_text(self, text):
        buffer = self.textview.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, text)

    def clear_text(self):
        buffer = self.textview.get_buffer()
        buffer.set_text("")

    def show_status(self, button=None):
        self.clear_text()
        self.append_text("=== Tailscale Status ===\n\n")

        status = self.ts_client.get_status()
        if status:
            self.append_text(f"Backend State: {status.get('BackendState', 'Unknown')}\n")
            self.append_text(f"Tailnet: {status.get('TailnetName', 'Unknown')}\n\n")

            if status.get('Health'):
                self.append_text("Health Issues:\n")
                for issue in status['Health']:
                    self.append_text(f"  - {issue}\n")
            else:
                self.append_text("Health: Good\n")

            if status.get('Self'):
                self.append_text("\nSelf:\n")
                self_ = status['Self']
                self.append_text(f"  HostName: {self_.get('HostName', 'Unknown')}\n")
                self.append_text(f"  DNS Name: {self_.get('DNSName', 'N/A')}\n")
                if self_.get('Addresses'):
                    self.append_text(f"  IP Addresses: {self_['Addresses'][0]}\n")
                self.append_text(f"  Online: {'Yes' if self_.get('Online', False) else 'No'}\n")

            peers = status.get('Peers', {})
            self.append_text(f"\nPeers: {len(peers)}\n")
            for peer in peers.values():
                online = "Online" if peer.get('Online', False) else "Offline"
                self.append_text(f"  {peer.get('HostName', 'Unknown')} ({peer.get('DNSName', 'N/A')}) - {online}\n")
        else:
            self.append_text("Failed to get status\n")

    def test_connectivity(self, button=None):
        self.append_text("\n=== Connectivity Test ===\n")

        devices = self.ts_client.get_devices()
        for device in devices:
            if device.get('Online', False) and device.get('HostName'):
                self.append_text(f"Pinging {device['HostName']}... ")
                success, stdout, stderr = self.ts_client.ping_device(device['HostName'])
                if success:
                    self.append_text(f"OK - {stdout}\n")
                else:
                    self.append_text(f"Error: {stderr}\n")

        self.append_text("Connectivity test completed.\n")

    def show_logs(self, button=None):
        self.clear_text()
        self.append_text("=== Recent Tailscale Logs ===\n\n")

        # Try journalctl first
        success, stdout, stderr = self.ts_client.run_command("journalctl -u tailscaled --since '1 hour ago' --no-pager -n 50")
        if not success:
            # Fallback to tailscale debug logs
            success, stdout, stderr = self.ts_client.run_command("tailscale debug logs -n 50")

        if success:
            self.append_text(stdout)
        else:
            self.append_text(f"Failed to get logs: {stderr}\n")


class MainWindow(Gtk.ApplicationWindow):
    """Main application window"""

    def __init__(self, app, ts_client):
        super().__init__(application=app, title="Tailscale")
        self.ts_client = ts_client

        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)

        # Header with status
        self.create_header(main_box)

        # Device list
        self.create_device_list(main_box)

        # Action buttons
        self.create_action_buttons(main_box)

        self.add(main_box)
        self.refresh_devices()

        # Connect delete event to hide window instead of closing
        self.connect("delete-event", self.on_delete_event)

    def create_header(self, parent_box):
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.status_label = Gtk.Label("Checking status...")
        self.status_label.set_halign(Gtk.Align.START)
        header_box.pack_start(self.status_label, True, True, 0)

        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.connect("clicked", self.refresh_devices)
        header_box.pack_end(refresh_btn, False, False, 0)

        parent_box.pack_start(header_box, False, False, 0)

    def create_device_list(self, parent_box):
        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search devices...")
        self.search_entry.connect("search-changed", self.on_search_changed)
        parent_box.pack_start(self.search_entry, False, False, 0)

        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        # Tree view
        self.liststore = Gtk.ListStore(str, str, bool, bool, str)  # hostname, ip, online, exit_node, os
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview.set_headers_visible(True)

        # Columns
        columns = [
            ("Device", 0),
            ("IP Address", 1),
            ("Online", 2),
            ("Exit Node", 3),
            ("OS", 4),
        ]

        for title, col_id in columns:
            if col_id in [2, 3]:  # Boolean columns
                renderer = Gtk.CellRendererToggle()
                renderer.set_activatable(False)
                column = Gtk.TreeViewColumn(title, renderer, active=col_id)
            else:
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(title, renderer, text=col_id)
            self.treeview.append_column(column)

        self.treeview.connect("row-activated", self.on_device_activated)

        scrolled.add(self.treeview)
        parent_box.pack_start(scrolled, True, True, 0)

    def create_action_buttons(self, parent_box):
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_margin_top(12)

        exit_node_btn = Gtk.Button(label="Set Exit Node")
        exit_node_btn.connect("clicked", self.show_exit_node_dialog)
        button_box.pack_start(exit_node_btn, False, False, 0)

        taildrop_btn = Gtk.Button(label="Send File")
        taildrop_btn.connect("clicked", self.show_taildrop_dialog)
        button_box.pack_start(taildrop_btn, False, False, 0)

        ssh_btn = Gtk.Button(label="SSH")
        ssh_btn.connect("clicked", self.show_ssh_dialog)
        button_box.pack_start(ssh_btn, False, False, 0)

        troubleshoot_btn = Gtk.Button(label="Troubleshoot")
        troubleshoot_btn.connect("clicked", self.show_troubleshooting_dialog)
        button_box.pack_end(troubleshoot_btn, False, False, 0)

        parent_box.pack_start(button_box, False, False, 0)

    def refresh_devices(self, button=None):
        self.liststore.clear()
        self.ts_client.clear_cache()

        status = self.ts_client.get_status()
        if status:
            if self.ts_client.is_connected():
                self.status_label.set_text(f"Connected to {status.get('TailnetName', 'Unknown')}")
            else:
                self.status_label.set_text("Disconnected")
        else:
            self.status_label.set_text("Failed to get status")

        devices = self.ts_client.get_devices()
        for device in devices:
            hostname = device.get('HostName', 'Unknown')
            ip = device.get('Addresses', [''])[0] if device.get('Addresses') else ''
            online = device.get('Online', False)
            exit_node = device.get('ExitNodeOption', False)
            os_name = device.get('OS', 'Unknown')

            self.liststore.append([hostname, ip, online, exit_node, os_name])

    def on_search_changed(self, entry):
        search_text = entry.get_text().lower()
        self.liststore.clear()

        devices = self.ts_client.get_devices()
        for device in devices:
            hostname = device.get('HostName', '').lower()
            dns_name = device.get('DNSName', '').lower()

            if not search_text or search_text in hostname or search_text in dns_name:
                ip = device.get('Addresses', [''])[0] if device.get('Addresses') else ''
                online = device.get('Online', False)
                exit_node = device.get('ExitNodeOption', False)
                os_name = device.get('OS', 'Unknown')

                self.liststore.append([device['HostName'], ip, online, exit_node, os_name])

    def on_device_activated(self, treeview, path, column):
        model = treeview.get_model()
        iter_ = model.get_iter(path)
        hostname = model.get_value(iter_, 0)

        # Find device
        devices = self.ts_client.get_devices()
        for device in devices:
            if device['HostName'] == hostname:
                DeviceDialog(self, device, self.ts_client)
                break

    def show_exit_node_dialog(self, button=None):
        ExitNodeDialog(self, self.ts_client)

    def show_taildrop_dialog(self, button=None):
        TaildropDialog(self, self.ts_client)

    def show_ssh_dialog(self, button=None):
        SSHDialog(self, self.ts_client)

    def show_troubleshooting_dialog(self, button=None):
        TroubleshootingDialog(self, self.ts_client)


class TailscaleGUI(Gtk.Application):
    """Main application class"""

    def __init__(self):
        super().__init__(application_id="com.tailscale.gui")
        self.ts_client = TailscaleClient()
        self.main_window = None
        self.indicator = None

    def do_activate(self):
        if not self.main_window:
            self.main_window = MainWindow(self, self.ts_client)
            self.main_window.show_all()

        # Create system tray indicator
        self.create_indicator()

    def create_indicator(self):
        try:
            self.indicator = AppIndicator3.Indicator.new(
                "tailscale-gui",
                "network-vpn",
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_title("Tailscale")

            # Create menu
            menu = Gtk.Menu()

            show_item = Gtk.MenuItem(label="Show Tailscale")
            show_item.connect("activate", self.show_window)
            menu.append(show_item)

            sep = Gtk.SeparatorMenuItem()
            menu.append(sep)

            quit_item = Gtk.MenuItem(label="Quit")
            quit_item.connect("activate", self.quit_app)
            menu.append(quit_item)

            menu.show_all()
            self.indicator.set_menu(menu)

        except Exception as e:
            print(f"Failed to create system tray indicator: {e}")

    def show_window(self, item=None):
        if self.main_window:
            if self.main_window.is_visible():
                self.main_window.hide()
            else:
                self.main_window.present()

    def on_delete_event(self, widget, event):
        """Hide the window instead of closing when X is clicked"""
        self.hide()
        return True  # Prevent the window from being destroyed

    def quit_app(self, item=None):
        if self.main_window:
            self.main_window.destroy()
        self.quit()


def main():
    app = TailscaleGUI()
    return app.run(sys.argv)


if __name__ == "__main__":
    main()