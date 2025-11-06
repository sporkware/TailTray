package tailscale

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"strings"
)

// Client represents a Tailscale client
type Client struct{}

// NewClient creates a new Tailscale client
func NewClient() *Client {
	return &Client{}
}

// Status represents the current Tailscale status
type Status struct {
	Version      string             `json:"Version"`
	TailnetName  string             `json:"TailnetName"`
	Health       []string           `json:"Health"`
	BackendState string             `json:"BackendState"`
	Self         *Device            `json:"Self"`
	Peers        map[string]*Device `json:"Peers"`
	User         map[string]*User   `json:"User"`
}

// Device represents a Tailscale device
type Device struct {
	ID               int      `json:"ID"`
	PublicKey        string   `json:"PublicKey"`
	HostName         string   `json:"HostName"`
	DNSName          string   `json:"DNSName"`
	OS               string   `json:"OS"`
	UserID           int      `json:"UserID"`
	TailnetLockKey   string   `json:"TailnetLockKey"`
	NodeKey          string   `json:"NodeKey"`
	Addresses        []string `json:"Addresses"`
	AllowedIPs       []string `json:"AllowedIPs"`
	Endpoints        []string `json:"Endpoints"`
	Created          string   `json:"Created"`
	LastSeen         string   `json:"LastSeen"`
	Online           bool     `json:"Online"`
	KeepAlive        bool     `json:"KeepAlive"`
	ExitNode         bool     `json:"ExitNode"`
	ExitNodeOption   bool     `json:"ExitNodeOption"`
	TailnetLockError string   `json:"TailnetLockError"`
}

// User represents a Tailscale user
type User struct {
	ID             int    `json:"ID"`
	LoginName      string `json:"LoginName"`
	DisplayName    string `json:"DisplayName"`
	Domain         string `json:"Domain"`
	TailnetLockKey string `json:"TailnetLockKey"`
}

// GetStatus retrieves the current Tailscale status
func (c *Client) GetStatus() (*Status, error) {
	cmd := exec.Command("tailscale", "status", "--json")
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to get tailscale status: %w", err)
	}

	var status Status
	if err := json.Unmarshal(output, &status); err != nil {
		return nil, fmt.Errorf("failed to parse status: %w", err)
	}

	return &status, nil
}

// GetDevices returns a list of all devices
func (c *Client) GetDevices() ([]*Device, error) {
	status, err := c.GetStatus()
	if err != nil {
		return nil, err
	}

	devices := make([]*Device, 0, len(status.Peers)+1)
	if status.Self != nil {
		devices = append(devices, status.Self)
	}

	for _, peer := range status.Peers {
		devices = append(devices, peer)
	}

	return devices, nil
}

// GetExitNodes returns devices that can be used as exit nodes
func (c *Client) GetExitNodes() ([]*Device, error) {
	devices, err := c.GetDevices()
	if err != nil {
		return nil, err
	}

	var exitNodes []*Device
	for _, device := range devices {
		if device.ExitNodeOption {
			exitNodes = append(exitNodes, device)
		}
	}

	return exitNodes, nil
}

// SetExitNode sets the current exit node
func (c *Client) SetExitNode(ip string) error {
	var cmd *exec.Cmd
	if ip == "" {
		cmd = exec.Command("tailscale", "set", "--exit-node=")
	} else {
		cmd = exec.Command("tailscale", "set", fmt.Sprintf("--exit-node=%s", ip))
	}

	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to set exit node: %w", err)
	}

	return nil
}

// PingDevice pings a device and returns latency
func (c *Client) PingDevice(hostname string) (string, error) {
	cmd := exec.Command("tailscale", "ping", hostname)
	output, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("failed to ping device: %w", err)
	}

	return strings.TrimSpace(string(output)), nil
}

// TaildropSend sends a file to a device
func (c *Client) TaildropSend(target, filePath string) error {
	cmd := exec.Command("tailscale", "file", "cp", filePath, target+":")
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to send file: %w", err)
	}
	return nil
}

// GetTailnetName returns the current tailnet name
func (c *Client) GetTailnetName() (string, error) {
	status, err := c.GetStatus()
	if err != nil {
		return "", err
	}
	return status.TailnetName, nil
}

// IsConnected checks if Tailscale is connected
func (c *Client) IsConnected() bool {
	status, err := c.GetStatus()
	if err != nil {
		return false
	}
	return status.BackendState == "Running"
}
