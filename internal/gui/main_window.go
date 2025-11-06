package gui

import (
	"log"
	"sort"
	"strings"

	"github.com/gotk3/gotk3/gdk"
	"github.com/gotk3/gotk3/gtk"
	"tailscale-gui/internal/tailscale"
)

// MainWindow represents the main application window
type MainWindow struct {
	window          *gtk.ApplicationWindow
	tailscaleClient *tailscale.Client
	deviceList      *gtk.TreeView
	deviceStore     *gtk.ListStore
	searchEntry     *gtk.SearchEntry
	statusLabel     *gtk.Label
}

// NewMainWindow creates a new main window
func NewMainWindow(app *gtk.Application, tsClient *tailscale.Client) *MainWindow {
	mw := &MainWindow{
		tailscaleClient: tsClient,
	}

	// Create main window
	win, err := gtk.ApplicationWindowNew(app)
	if err != nil {
		log.Fatal("Failed to create window:", err)
	}
	mw.window = win

	mw.window.SetTitle("Tailscale")
	mw.window.SetDefaultSize(800, 600)
	mw.window.SetPosition(gtk.WIN_POS_CENTER)

	// Create main layout
	box, err := gtk.BoxNew(gtk.ORIENTATION_VERTICAL, 6)
	if err != nil {
		log.Fatal("Failed to create box:", err)
	}

	// Create header with status
	mw.createHeader(box)

	// Create device management section
	mw.createDeviceSection(box)

	// Create action buttons
	mw.createActionButtons(box)

	// Set window content
	mw.window.Add(box)
	mw.window.ShowAll()

	// Load initial data
	mw.refreshDevices()

	return mw
}

func (mw *MainWindow) createHeader(box *gtk.Box) {
	headerBox, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	headerBox.SetMarginStart(12)
	headerBox.SetMarginEnd(12)
	headerBox.SetMarginTop(12)

	// Status label
	mw.statusLabel, _ = gtk.LabelNew("Checking status...")
	mw.statusLabel.SetHAlign(gtk.ALIGN_START)
	headerBox.PackStart(mw.statusLabel, true, true, 0)

	// Refresh button
	refreshBtn, _ := gtk.ButtonNewWithLabel("Refresh")
	refreshBtn.Connect("clicked", mw.refreshDevices)
	headerBox.PackEnd(refreshBtn, false, false, 0)

	box.PackStart(headerBox, false, false, 0)
}

func (mw *MainWindow) createDeviceSection(box *gtk.Box) {
	// Search entry
	mw.searchEntry, _ = gtk.SearchEntryNew()
	mw.searchEntry.SetPlaceholderText("Search devices...")
	mw.searchEntry.SetMarginStart(12)
	mw.searchEntry.SetMarginEnd(12)
	mw.searchEntry.Connect("search-changed", mw.onSearchChanged)
	box.PackStart(mw.searchEntry, false, false, 0)

	// Scrolled window for device list
	scrolled, _ := gtk.ScrolledWindowNew(nil, nil)
	scrolled.SetMarginStart(12)
	scrolled.SetMarginEnd(12)
	scrolled.SetVExpand(true)

	// Create device list
	mw.createDeviceList()
	scrolled.Add(mw.deviceList)

	box.PackStart(scrolled, true, true, 0)
}

func (mw *MainWindow) createDeviceList() {
	// Create list store (columns: hostname, ip, online, exit_node)
	mw.deviceStore, _ = gtk.ListStoreNew(
		gdk.TYPE_STRING,  // hostname
		gdk.TYPE_STRING,  // ip
		gdk.TYPE_BOOLEAN, // online
		gdk.TYPE_BOOLEAN, // exit_node
		gdk.TYPE_STRING,  // os
	)

	// Create tree view
	mw.deviceList, _ = gtk.TreeViewNewWithModel(mw.deviceStore)
	mw.deviceList.SetHeadersVisible(true)

	// Add columns
	mw.addColumn("Device", 0)
	mw.addColumn("IP Address", 1)
	mw.addColumn("Online", 2)
	mw.addColumn("Exit Node", 3)
	mw.addColumn("OS", 4)

	// Connect double-click handler
	mw.deviceList.Connect("row-activated", mw.onDeviceActivated)
}

func (mw *MainWindow) addColumn(title string, colID int) {
	renderer, _ := gtk.CellRendererTextNew()
	column, _ := gtk.TreeViewColumnNewWithAttribute(title, renderer, "text", colID)
	mw.deviceList.AppendColumn(column)
}

func (mw *MainWindow) createActionButtons(box *gtk.Box) {
	buttonBox, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	buttonBox.SetMarginStart(12)
	buttonBox.SetMarginEnd(12)
	buttonBox.SetMarginBottom(12)

	// Exit node button
	exitNodeBtn, _ := gtk.ButtonNewWithLabel("Set Exit Node")
	exitNodeBtn.Connect("clicked", mw.showExitNodeDialog)
	buttonBox.PackStart(exitNodeBtn, false, false, 0)

	// Taildrop button
	taildropBtn, _ := gtk.ButtonNewWithLabel("Send File")
	taildropBtn.Connect("clicked", mw.showTaildropDialog)
	buttonBox.PackStart(taildropBtn, false, false, 0)

	// SSH button
	sshBtn, _ := gtk.ButtonNewWithLabel("SSH")
	sshBtn.Connect("clicked", mw.showSSHDialog)
	buttonBox.PackStart(sshBtn, false, false, 0)

	// Troubleshooting button
	troubleshootBtn, _ := gtk.ButtonNewWithLabel("Troubleshoot")
	troubleshootBtn.Connect("clicked", mw.showTroubleshootingDialog)
	buttonBox.PackEnd(troubleshootBtn, false, false, 0)

	box.PackStart(buttonBox, false, false, 0)
}

func (mw *MainWindow) refreshDevices() {
	// Clear existing data
	mw.deviceStore.Clear()

	// Get status
	status, err := mw.tailscaleClient.GetStatus()
	if err != nil {
		mw.statusLabel.SetText("Error: " + err.Error())
		return
	}

	// Update status
	if mw.tailscaleClient.IsConnected() {
		mw.statusLabel.SetText("Connected to " + status.TailnetName)
	} else {
		mw.statusLabel.SetText("Disconnected")
	}

	// Get devices
	devices, err := mw.tailscaleClient.GetDevices()
	if err != nil {
		log.Printf("Failed to get devices: %v", err)
		return
	}

	// Sort devices by hostname
	sort.Slice(devices, func(i, j int) bool {
		return devices[i].HostName < devices[j].HostName
	})

	// Add devices to list
	for _, device := range devices {
		iter := mw.deviceStore.Append()
		ip := ""
		if len(device.Addresses) > 0 {
			ip = device.Addresses[0]
		}

		mw.deviceStore.SetValue(iter, 0, device.HostName)
		mw.deviceStore.SetValue(iter, 1, ip)
		mw.deviceStore.SetValue(iter, 2, device.Online)
		mw.deviceStore.SetValue(iter, 3, device.ExitNodeOption)
		mw.deviceStore.SetValue(iter, 4, device.OS)
	}
}

func (mw *MainWindow) onSearchChanged() {
	text, _ := mw.searchEntry.GetText()
	mw.filterDevices(text)
}

func (mw *MainWindow) filterDevices(filterText string) {
	// Clear current display
	mw.deviceStore.Clear()

	// Get all devices
	devices, err := mw.tailscaleClient.GetDevices()
	if err != nil {
		log.Printf("Failed to get devices: %v", err)
		return
	}

	// Filter and sort devices
	var filteredDevices []*tailscale.Device
	for _, device := range devices {
		if filterText == "" ||
			strings.Contains(strings.ToLower(device.HostName), strings.ToLower(filterText)) ||
			strings.Contains(strings.ToLower(device.DNSName), strings.ToLower(filterText)) {
			filteredDevices = append(filteredDevices, device)
		}
	}

	// Sort filtered devices
	sort.Slice(filteredDevices, func(i, j int) bool {
		return filteredDevices[i].HostName < filteredDevices[j].HostName
	})

	// Add filtered devices to list
	for _, device := range filteredDevices {
		iter := mw.deviceStore.Append()
		ip := ""
		if len(device.Addresses) > 0 {
			ip = device.Addresses[0]
		}

		mw.deviceStore.SetValue(iter, 0, device.HostName)
		mw.deviceStore.SetValue(iter, 1, ip)
		mw.deviceStore.SetValue(iter, 2, device.Online)
		mw.deviceStore.SetValue(iter, 3, device.ExitNodeOption)
		mw.deviceStore.SetValue(iter, 4, device.OS)
	}
}

func (mw *MainWindow) onDeviceActivated(treeView *gtk.TreeView, path *gtk.TreePath, column *gtk.TreeViewColumn) {
	// TODO: Show device details dialog
	log.Printf("Device activated: %s", path.String())
}

func (mw *MainWindow) showExitNodeDialog() {
	dialog := NewExitNodeDialog(mw)
	dialog.Show()
}

func (mw *MainWindow) showTaildropDialog() {
	dialog := NewTaildropDialog(mw)
	dialog.Show()
}

func (mw *MainWindow) showSSHDialog() {
	dialog := NewSSHDialog(mw)
	dialog.Show()
}

func (mw *MainWindow) showTroubleshootingDialog() {
	dialog := NewTroubleshootingDialog(mw)
	dialog.Show()
}

// GetWindow returns the GTK window
func (mw *MainWindow) GetWindow() *gtk.ApplicationWindow {
	return mw.window
}
