package gui

import (
	"fmt"
	"log"
	"os/exec"

	"github.com/gotk3/gotk3/gtk"
	"tailscale-gui/internal/tailscale"
)

// SSHDialog represents the SSH connection dialog
type SSHDialog struct {
	dialog      *gtk.Dialog
	deviceCombo *gtk.ComboBoxText
	userEntry   *gtk.Entry
	tsClient    *tailscale.Client
	parent      *MainWindow
}

// NewSSHDialog creates a new SSH connection dialog
func NewSSHDialog(parent *MainWindow) *SSHDialog {
	sd := &SSHDialog{
		tsClient: parent.tailscaleClient,
		parent:   parent,
	}

	// Create dialog
	dialog, err := gtk.DialogNewWithButtons(
		"Connect via Tailscale SSH",
		parent.window,
		gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
		[]interface{}{"Connect", gtk.RESPONSE_OK},
		[]interface{}{"Cancel", gtk.RESPONSE_CANCEL},
	)
	if err != nil {
		log.Fatal("Failed to create dialog:", err)
	}
	sd.dialog = dialog

	// Get content area
	contentArea, _ := dialog.GetContentArea()
	contentArea.SetMarginStart(12)
	contentArea.SetMarginEnd(12)
	contentArea.SetMarginTop(12)
	contentArea.SetMarginBottom(12)

	// Create form layout
	grid, _ := gtk.GridNew()
	grid.SetRowSpacing(6)
	grid.SetColumnSpacing(12)

	// Device selection
	deviceLabel, _ := gtk.LabelNew("Connect to device:")
	deviceLabel.SetHAlign(gtk.ALIGN_START)
	grid.Attach(deviceLabel, 0, 0, 1, 1)

	sd.deviceCombo, _ = gtk.ComboBoxTextNew()
	sd.populateDeviceList()
	grid.Attach(sd.deviceCombo, 1, 0, 1, 1)

	// User selection
	userLabel, _ := gtk.LabelNew("Username:")
	userLabel.SetHAlign(gtk.ALIGN_START)
	grid.Attach(userLabel, 0, 1, 1, 1)

	sd.userEntry, _ = gtk.EntryNew()
	sd.userEntry.SetText("root") // Default to root
	grid.Attach(sd.userEntry, 1, 1, 1, 1)

	// Info label
	infoLabel, _ := gtk.LabelNew("Note: This will open a terminal with the SSH connection")
	infoLabel.SetHAlign(gtk.ALIGN_START)
	infoLabel.SetMarginTop(12)
	grid.Attach(infoLabel, 0, 2, 2, 1)

	contentArea.PackStart(grid, true, true, 0)

	// Connect response handler
	dialog.Connect("response", sd.onResponse)

	return sd
}

func (sd *SSHDialog) populateDeviceList() {
	// Get devices
	devices, err := sd.tsClient.GetDevices()
	if err != nil {
		log.Printf("Failed to get devices: %v", err)
		return
	}

	// Add devices to combo box
	for _, device := range devices {
		if device.Online {
			displayName := device.HostName
			if device.DNSName != "" && device.DNSName != device.HostName {
				displayName = device.HostName + " (" + device.DNSName + ")"
			}
			sd.deviceCombo.AppendText(displayName)
		}
	}

	// Set first device as default if available
	if sd.deviceCombo.GetActiveText() == "" && len(devices) > 0 {
		sd.deviceCombo.SetActive(0)
	}
}

func (sd *SSHDialog) onResponse(dialog *gtk.Dialog, response gtk.ResponseType) {
	if response == gtk.RESPONSE_OK {
		sd.connectSSH()
	}
	sd.dialog.Destroy()
}

func (sd *SSHDialog) connectSSH() {
	// Get selected device
	deviceText := sd.deviceCombo.GetActiveText()
	if deviceText == "" {
		log.Println("No device selected")
		return
	}

	// Extract hostname from display text
	hostname := deviceText
	if idx := len(hostname) - 1; idx > 0 {
		for i := idx; i >= 0; i-- {
			if hostname[i] == '(' {
				hostname = hostname[:i-1] // Remove space and parenthesis part
				break
			}
		}
	}

	// Get username
	username, _ := sd.userEntry.GetText()
	if username == "" {
		username = "root"
	}

	// Construct SSH command
	sshTarget := fmt.Sprintf("%s@%s", username, hostname)

	log.Printf("Connecting to %s via SSH", sshTarget)

	// Launch SSH in terminal
	// Try different terminal commands
	terminals := []string{"gnome-terminal", "konsole", "xfce4-terminal", "xterm", "terminator"}
	var cmd *exec.Cmd

	for _, terminal := range terminals {
		if _, err := exec.LookPath(terminal); err == nil {
			cmd = exec.Command(terminal, "-e", "tailscale", "ssh", sshTarget)
			break
		}
	}

	if cmd == nil {
		// Fallback to xterm or just run directly
		if _, err := exec.LookPath("xterm"); err == nil {
			cmd = exec.Command("xterm", "-e", "tailscale", "ssh", sshTarget)
		} else {
			cmd = exec.Command("tailscale", "ssh", sshTarget)
		}
	}

	if err := cmd.Start(); err != nil {
		log.Printf("Failed to start SSH: %v", err)
		errorDialog := gtk.MessageDialogNew(
			sd.parent.window,
			gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_ERROR,
			gtk.BUTTONS_OK,
			"Failed to start SSH connection: %v", err,
		)
		errorDialog.Run()
		errorDialog.Destroy()
	}
}

// Show displays the dialog
func (sd *SSHDialog) Show() {
	sd.dialog.ShowAll()
}
