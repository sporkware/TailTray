package gui

import (
	"log"

	"github.com/gotk3/gotk3/gdk"
	"github.com/gotk3/gotk3/gtk"
	"tailscale-gui/internal/tailscale"
)

// ExitNodeDialog represents the exit node selection dialog
type ExitNodeDialog struct {
	dialog    *gtk.Dialog
	treeView  *gtk.TreeView
	listStore *gtk.ListStore
	tsClient  *tailscale.Client
	parent    *MainWindow
}

// NewExitNodeDialog creates a new exit node selection dialog
func NewExitNodeDialog(parent *MainWindow) *ExitNodeDialog {
	ed := &ExitNodeDialog{
		tsClient: parent.tailscaleClient,
		parent:   parent,
	}

	// Create dialog
	dialog, err := gtk.DialogNewWithButtons(
		"Select Exit Node",
		parent.window,
		gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
		[]interface{}{"Set", gtk.RESPONSE_OK},
		[]interface{}{"Disable", gtk.RESPONSE_APPLY},
		[]interface{}{"Cancel", gtk.RESPONSE_CANCEL},
	)
	if err != nil {
		log.Fatal("Failed to create dialog:", err)
	}
	ed.dialog = dialog

	// Get content area
	contentArea, _ := dialog.GetContentArea()
	contentArea.SetMarginStart(12)
	contentArea.SetMarginEnd(12)
	contentArea.SetMarginTop(12)
	contentArea.SetMarginBottom(12)

	// Create scrolled window
	scrolled, _ := gtk.ScrolledWindowNew(nil, nil)
	scrolled.SetSizeRequest(400, 300)

	// Create tree view
	ed.createExitNodeList()
	scrolled.Add(ed.treeView)

	contentArea.PackStart(scrolled, true, true, 0)

	// Connect response handler
	dialog.Connect("response", ed.onResponse)

	// Load exit nodes
	ed.loadExitNodes()

	return ed
}

func (ed *ExitNodeDialog) createExitNodeList() {
	// Create list store (columns: hostname, ip, selected)
	ed.listStore, _ = gtk.ListStoreNew(
		gdk.TYPE_STRING,  // hostname
		gdk.TYPE_STRING,  // ip
		gdk.TYPE_BOOLEAN, // selected
	)

	// Create tree view
	ed.treeView, _ = gtk.TreeViewNewWithModel(ed.listStore)
	ed.treeView.SetHeadersVisible(true)

	// Add columns
	ed.addColumn("Device", 0)
	ed.addColumn("IP Address", 1)

	// Add toggle column for selection
	renderer, _ := gtk.CellRendererToggleNew()
	renderer.Connect("toggled", ed.onToggle)
	column, _ := gtk.TreeViewColumnNewWithAttribute("Use as Exit Node", renderer, "active", 2)
	ed.treeView.AppendColumn(column)
}

func (ed *ExitNodeDialog) addColumn(title string, colID int) {
	renderer, _ := gtk.CellRendererTextNew()
	column, _ := gtk.TreeViewColumnNewWithAttribute(title, renderer, "text", colID)
	ed.treeView.AppendColumn(column)
}

func (ed *ExitNodeDialog) loadExitNodes() {
	// Clear existing data
	ed.listStore.Clear()

	// Get exit nodes
	exitNodes, err := ed.tsClient.GetExitNodes()
	if err != nil {
		log.Printf("Failed to get exit nodes: %v", err)
		return
	}

	// Get current status to check which exit node is active
	status, err := ed.tsClient.GetStatus()
	if err != nil {
		log.Printf("Failed to get status: %v", err)
		return
	}

	// Add "None" option first
	iter := ed.listStore.Append()
	ed.listStore.SetValue(iter, 0, "None (Direct connection)")
	ed.listStore.SetValue(iter, 1, "")
	ed.listStore.SetValue(iter, 2, status.Self != nil && !status.Self.ExitNode)

	// Add exit nodes
	for _, node := range exitNodes {
		iter := ed.listStore.Append()
		ip := ""
		if len(node.Addresses) > 0 {
			ip = node.Addresses[0]
		}

		ed.listStore.SetValue(iter, 0, node.HostName)
		ed.listStore.SetValue(iter, 1, ip)
		ed.listStore.SetValue(iter, 2, node.ExitNode)
	}
}

func (ed *ExitNodeDialog) onToggle(renderer *gtk.CellRendererToggle, path string) {
	// Clear all selections first
	ed.listStore.ForEach(func(model *gtk.TreeModel, path *gtk.TreePath, iter *gtk.TreeIter) bool {
		ed.listStore.SetValue(iter, 2, false)
		return false
	})

	// Set the selected one
	iter, err := ed.listStore.GetIterFromString(path)
	if err != nil {
		log.Printf("Failed to get iter: %v", err)
		return
	}

	ed.listStore.SetValue(iter, 2, true)
}

func (ed *ExitNodeDialog) onResponse(dialog *gtk.Dialog, response gtk.ResponseType) {
	switch response {
	case gtk.RESPONSE_OK:
		// Set selected exit node
		ed.setSelectedExitNode()
	case gtk.RESPONSE_APPLY:
		// Disable exit node
		if err := ed.tsClient.SetExitNode(""); err != nil {
			log.Printf("Failed to disable exit node: %v", err)
		}
		ed.parent.refreshDevices()
	}

	ed.dialog.Destroy()
}

func (ed *ExitNodeDialog) setSelectedExitNode() {
	ed.listStore.ForEach(func(model *gtk.TreeModel, path *gtk.TreePath, iter *gtk.TreeIter) bool {
		value, err := ed.listStore.GetValue(iter, 2)
		if err != nil {
			return false
		}

		selected, _ := value.GoValue()
		if selected.(bool) {
			// Get hostname
			hostValue, _ := ed.listStore.GetValue(iter, 0)
			hostname, _ := hostValue.GoValue()

			if hostname.(string) == "None (Direct connection)" {
				// Disable exit node
				if err := ed.tsClient.SetExitNode(""); err != nil {
					log.Printf("Failed to disable exit node: %v", err)
				}
			} else {
				// Get IP address
				ipValue, _ := ed.listStore.GetValue(iter, 1)
				ip, _ := ipValue.GoValue()

				if err := ed.tsClient.SetExitNode(ip.(string)); err != nil {
					log.Printf("Failed to set exit node: %v", err)
				}
			}

			ed.parent.refreshDevices()
			return true // Stop iteration
		}

		return false
	})
}

// Show displays the dialog
func (ed *ExitNodeDialog) Show() {
	ed.dialog.ShowAll()
}
