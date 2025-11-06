package gui

import (
	"log"
	"path/filepath"

	"github.com/gotk3/gotk3/gdk"
	"github.com/gotk3/gotk3/gtk"
	"tailscale-gui/internal/tailscale"
)

// TaildropDialog represents the file sending dialog
type TaildropDialog struct {
	dialog      *gtk.Dialog
	deviceCombo *gtk.ComboBoxText
	fileChooser *gtk.FileChooserButton
	tsClient    *tailscale.Client
	parent      *MainWindow
}

// NewTaildropDialog creates a new file sending dialog
func NewTaildropDialog(parent *MainWindow) *TaildropDialog {
	td := &TaildropDialog{
		tsClient: parent.tailscaleClient,
		parent:   parent,
	}

	// Create dialog
	dialog, err := gtk.DialogNewWithButtons(
		"Send File with Taildrop",
		parent.window,
		gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
		[]interface{}{"Send", gtk.RESPONSE_OK},
		[]interface{}{"Cancel", gtk.RESPONSE_CANCEL},
	)
	if err != nil {
		log.Fatal("Failed to create dialog:", err)
	}
	td.dialog = dialog

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
	deviceLabel, _ := gtk.LabelNew("Send to device:")
	deviceLabel.SetHAlign(gtk.ALIGN_START)
	grid.Attach(deviceLabel, 0, 0, 1, 1)

	td.deviceCombo, _ = gtk.ComboBoxTextNew()
	td.populateDeviceList()
	grid.Attach(td.deviceCombo, 1, 0, 1, 1)

	// File selection
	fileLabel, _ := gtk.LabelNew("Select file:")
	fileLabel.SetHAlign(gtk.ALIGN_START)
	grid.Attach(fileLabel, 0, 1, 1, 1)

	td.fileChooser, _ = gtk.FileChooserButtonNew("Select File", gtk.FILE_CHOOSER_ACTION_OPEN)
	grid.Attach(td.fileChooser, 1, 1, 1, 1)

	contentArea.PackStart(grid, true, true, 0)

	// Connect response handler
	dialog.Connect("response", td.onResponse)

	return td
}

func (td *TaildropDialog) populateDeviceList() {
	// Get devices
	devices, err := td.tsClient.GetDevices()
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
			td.deviceCombo.AppendText(displayName)
		}
	}

	// Set first device as default if available
	if td.deviceCombo.GetActiveText() == "" && len(devices) > 0 {
		td.deviceCombo.SetActive(0)
	}
}

func (td *TaildropDialog) onResponse(dialog *gtk.Dialog, response gtk.ResponseType) {
	if response == gtk.RESPONSE_OK {
		td.sendFile()
	}
	td.dialog.Destroy()
}

func (td *TaildropDialog) sendFile() {
	// Get selected device
	deviceText := td.deviceCombo.GetActiveText()
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

	// Get selected file
	filename := td.fileChooser.GetFilename()
	if filename == "" {
		log.Println("No file selected")
		return
	}

	// Send file
	log.Printf("Sending file %s to %s", filename, hostname)
	if err := td.tsClient.TaildropSend(hostname, filename); err != nil {
		log.Printf("Failed to send file: %v", err)
		errorDialog := gtk.MessageDialogNew(
			td.parent.window,
			gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_ERROR,
			gtk.BUTTONS_OK,
			"Failed to send file: %v", err,
		)
		errorDialog.Run()
		errorDialog.Destroy()
		return
	}

	// Show success message
	successDialog := gtk.MessageDialogNew(
		td.parent.window,
		gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
		gtk.MESSAGE_INFO,
		gtk.BUTTONS_OK,
		"File sent successfully to %s", hostname,
	)
	successDialog.Run()
	successDialog.Destroy()
}

// Show displays the dialog
func (td *TaildropDialog) Show() {
	td.dialog.ShowAll()
}
