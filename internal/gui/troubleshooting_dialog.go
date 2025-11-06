package gui

import (
	"bytes"
	"log"
	"os/exec"

	"github.com/gotk3/gotk3/gtk"
	"tailscale-gui/internal/tailscale"
)

// TroubleshootingDialog represents the troubleshooting dialog
type TroubleshootingDialog struct {
	dialog   *gtk.Dialog
	textView *gtk.TextView
	tsClient *tailscale.Client
	parent   *MainWindow
}

// NewTroubleshootingDialog creates a new troubleshooting dialog
func NewTroubleshootingDialog(parent *MainWindow) *TroubleshootingDialog {
	td := &TroubleshootingDialog{
		tsClient: parent.tailscaleClient,
		parent:   parent,
	}

	// Create dialog
	dialog, err := gtk.DialogNewWithButtons(
		"Troubleshooting",
		parent.window,
		gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
		[]interface{}{"Close", gtk.RESPONSE_CLOSE},
	)
	if err != nil {
		log.Fatal("Failed to create dialog:", err)
	}
	td.dialog = dialog

	// Set dialog size
	dialog.SetDefaultSize(600, 400)

	// Get content area
	contentArea, _ := dialog.GetContentArea()
	contentArea.SetMarginStart(12)
	contentArea.SetMarginEnd(12)
	contentArea.SetMarginTop(12)
	contentArea.SetMarginBottom(12)

	// Create button box
	buttonBox, _ := gtk.BoxNew(gtk.ORIENTATION_HORIZONTAL, 6)
	buttonBox.SetMarginBottom(12)

	// Add buttons
	pingBtn, _ := gtk.ButtonNewWithLabel("Test Connectivity")
	pingBtn.Connect("clicked", td.runConnectivityTest)
	buttonBox.PackStart(pingBtn, false, false, 0)

	statusBtn, _ := gtk.ButtonNewWithLabel("Get Status")
	statusBtn.Connect("clicked", td.showStatus)
	buttonBox.PackStart(statusBtn, false, false, 0)

	logsBtn, _ := gtk.ButtonNewWithLabel("Show Logs")
	logsBtn.Connect("clicked", td.showLogs)
	buttonBox.PackStart(logsBtn, false, false, 0)

	resetBtn, _ := gtk.ButtonNewWithLabel("Reset Connection")
	resetBtn.Connect("clicked", td.resetConnection)
	buttonBox.PackEnd(resetBtn, false, false, 0)

	contentArea.PackStart(buttonBox, false, false, 0)

	// Create scrolled text view
	scrolled, _ := gtk.ScrolledWindowNew(nil, nil)
	scrolled.SetVExpand(true)

	td.textView, _ = gtk.TextViewNew()
	td.textView.SetEditable(false)
	td.textView.SetWrapMode(gtk.WRAP_WORD)
	scrolled.Add(td.textView)

	contentArea.PackStart(scrolled, true, true, 0)

	// Connect response handler
	dialog.Connect("response", func(dialog *gtk.Dialog, response gtk.ResponseType) {
		td.dialog.Destroy()
	})

	// Show initial status
	td.showStatus()

	return td
}

func (td *TroubleshootingDialog) runConnectivityTest() {
	td.appendText("Running connectivity test...\n")

	// Get devices
	devices, err := td.tsClient.GetDevices()
	if err != nil {
		td.appendText("Error getting devices: " + err.Error() + "\n")
		return
	}

	// Test ping to each online device
	for _, device := range devices {
		if device.Online && device.HostName != "" {
			td.appendText("Pinging " + device.HostName + "... ")
			result, err := td.tsClient.PingDevice(device.HostName)
			if err != nil {
				td.appendText("Error: " + err.Error() + "\n")
			} else {
				td.appendText("OK - " + result + "\n")
			}
		}
	}

	td.appendText("Connectivity test completed.\n")
}

func (td *TroubleshootingDialog) showStatus() {
	td.clearText()
	td.appendText("=== Tailscale Status ===\n\n")

	// Get status
	status, err := td.tsClient.GetStatus()
	if err != nil {
		td.appendText("Error getting status: " + err.Error() + "\n")
		return
	}

	td.appendText("Backend State: " + status.BackendState + "\n")
	td.appendText("Tailnet: " + status.TailnetName + "\n")

	if len(status.Health) > 0 {
		td.appendText("Health Issues:\n")
		for _, issue := range status.Health {
			td.appendText("  - " + issue + "\n")
		}
	} else {
		td.appendText("Health: Good\n")
	}

	if status.Self != nil {
		td.appendText("\nSelf:\n")
		td.appendText("  HostName: " + status.Self.HostName + "\n")
		td.appendText("  DNS Name: " + status.Self.DNSName + "\n")
		if len(status.Self.Addresses) > 0 {
			td.appendText("  IP Addresses: " + status.Self.Addresses[0] + "\n")
		}
		td.appendText("  Online: " + boolToString(status.Self.Online) + "\n")
	}

	peerCount := len(status.Peers)
	td.appendText("\nPeers: " + string(rune(peerCount+'0')) + "\n")

	for _, peer := range status.Peers {
		td.appendText("  " + peer.HostName + " (" + peer.DNSName + ") - " + boolToString(peer.Online) + "\n")
	}
}

func (td *TroubleshootingDialog) showLogs() {
	td.clearText()
	td.appendText("=== Recent Tailscale Logs ===\n\n")

	// Get logs using journalctl if available, otherwise tailscale debug logs
	cmd := exec.Command("journalctl", "-u", "tailscaled", "--since", "1 hour ago", "--no-pager", "-n", "50")
	output, err := cmd.Output()
	if err != nil {
		// Fallback to tailscale debug logs
		cmd = exec.Command("tailscale", "debug", "logs", "-n", "50")
		output, err = cmd.Output()
		if err != nil {
			td.appendText("Error getting logs: " + err.Error() + "\n")
			return
		}
	}

	td.appendText(string(output))
}

func (td *TroubleshootingDialog) resetConnection() {
	td.appendText("Resetting Tailscale connection...\n")

	// Stop and start tailscale
	cmd := exec.Command("sudo", "systemctl", "restart", "tailscaled")
	if err := cmd.Run(); err != nil {
		td.appendText("Error resetting connection: " + err.Error() + "\n")
		td.appendText("You may need to run: sudo systemctl restart tailscaled\n")
		return
	}

	td.appendText("Connection reset successfully. Please wait a moment for reconnection.\n")
}

func (td *TroubleshootingDialog) appendText(text string) {
	buffer, _ := td.textView.GetBuffer()
	endIter := buffer.GetEndIter()
	buffer.Insert(endIter, text)
}

func (td *TroubleshootingDialog) clearText() {
	buffer, _ := td.textView.GetBuffer()
	buffer.SetText("")
}

func boolToString(b bool) string {
	if b {
		return "Online"
	}
	return "Offline"
}

// Show displays the dialog
func (td *TroubleshootingDialog) Show() {
	td.dialog.ShowAll()
}
