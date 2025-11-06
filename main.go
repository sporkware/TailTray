package main

import (
	"log"
	"os"

	"github.com/gotk3/gotk3/gtk"
	"tailscale-gui/internal/gui"
	"tailscale-gui/internal/tailscale"
)

func main() {
	// Initialize GTK
	gtk.Init(&os.Args)

	// Create Tailscale client
	tsClient := tailscale.NewClient()

	// Create application
	app, err := gtk.ApplicationNew("com.tailscale.gui", 0)
	if err != nil {
		log.Fatal("Failed to create GTK application:", err)
	}

	app.Connect("activate", func() {
		createMainWindow(app, tsClient)
	})

	// Run the application
	app.Run(os.Args)
}

func createMainWindow(app *gtk.Application, tsClient *tailscale.Client) {
	// Create main window
	mainWindow := gui.NewMainWindow(app, tsClient)

	// Create system tray
	createSystemTray(mainWindow.GetWindow())
}

func createSystemTray(win *gtk.ApplicationWindow) {
	// Create status icon for system tray
	statusIcon, err := gtk.StatusIconNew()
	if err != nil {
		log.Printf("Failed to create status icon: %v", err)
		return
	}

	// Set icon (you might want to use a proper Tailscale icon)
	statusIcon.SetFromIconName("network-vpn")

	// Set tooltip
	statusIcon.SetTooltipText("Tailscale")

	// Connect popup menu
	statusIcon.Connect("popup-menu", func(statusIcon *gtk.StatusIcon, button uint, activateTime uint32) {
		menu, _ := gtk.MenuNew()

		// Show window item
		showItem, _ := gtk.MenuItemNewWithLabel("Show Tailscale")
		showItem.Connect("activate", func() {
			win.Present()
		})
		menu.Append(showItem)

		// Separator
		sep, _ := gtk.SeparatorMenuItemNew()
		menu.Append(sep)

		// Quit item
		quitItem, _ := gtk.MenuItemNewWithLabel("Quit")
		quitItem.Connect("activate", func() {
			gtk.MainQuit()
		})
		menu.Append(quitItem)

		menu.ShowAll()
		menu.PopupAtPointer(nil)
	})

	// Connect left click to show window
	statusIcon.Connect("activate", func() {
		if win.IsVisible() {
			win.Hide()
		} else {
			win.Present()
		}
	})
}
