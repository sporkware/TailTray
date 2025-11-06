# Installation

This application requires PyGObject and its dependencies to be installed. Please follow the instructions for your specific operating system.

## Debian/Ubuntu

```bash
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

## Fedora

```bash
sudo dnf install -y pygobject3 python3-gobject gtk3
```

## Arch Linux

```bash
sudo pacman -S --noconfirm python-gobject gtk3
```

## openSUSE

```bash
sudo zypper install -y python3-gobject gtk3
```

Once these dependencies are installed, you can proceed with the standard installation:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python tailtray.py
```
