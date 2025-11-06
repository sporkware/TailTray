# Maintainer: TailTray Contributors
pkgname=tailtray
pkgver=0.1.0
pkgrel=1
pkgdesc="Tailscale GUI for Linux - System tray application for KDE Plasma"
arch=('x86_64')
url="https://github.com/yourusername/tailtray"
license=('MIT')
depends=(
    'python-gobject'
    'python-requests'
    'gtk3'
    'libappindicator-gtk3'
    'tailscale'
    'plasma-desktop'
    'kdeplasma-addons'
)
makedepends=('python-setuptools')
optdepends=(
    'python-tailscale: For alternative API integration'
    'konsole: Default terminal for SSH connections'
    'dolphin: Default file manager for file operations'
)
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
    cd "$srcdir/$pkgname-$pkgver"

    # Install Python modules
    python setup.py install --root="$pkgdir" --optimize=1

    # Install main application
    install -Dm755 tailtray.py "$pkgdir/usr/bin/tailtray"

    # Install modules
    install -Dm644 tailscale_client.py "$pkgdir/usr/lib/python3.11/site-packages/tailscale_client.py"
    install -Dm644 tailtray_config.py "$pkgdir/usr/lib/python3.11/site-packages/tailtray_config.py"

    # Install desktop file
    install -Dm644 tailtray.desktop "$pkgdir/usr/share/applications/tailtray.desktop"

    # Install icons
    install -Dm644 tailtray.svg "$pkgdir/usr/share/icons/hicolor/scalable/apps/tailtray.svg"

    # Install systemd user service
    install -Dm644 tailtray.service "$pkgdir/usr/lib/systemd/user/tailtray.service"

    # Install documentation
    install -Dm644 README.md "$pkgdir/usr/share/doc/tailtray/README.md"
    install -Dm644 CHANGELOG.md "$pkgdir/usr/share/doc/tailtray/CHANGELOG.md"
    install -Dm644 STATUS.md "$pkgdir/usr/share/doc/tailtray/STATUS.md"

    # Install license
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/tailtray/LICENSE"

    # Install man page
    install -Dm644 tailtray.1 "$pkgdir/usr/share/man/man1/tailtray.1"
}