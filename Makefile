# Makefile for TailTray

.PHONY: all build install clean test

# Default target
all: build

# Build the executable
build:
	@echo "Building TailTray executable..."
	python build.py

# Install dependencies
install-deps:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Install dev dependencies
install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements-dev.txt

# Run tests
test:
	@echo "Running tests..."
	python -m pytest tests/

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build dist *.spec

# Install system-wide (requires root)
install: build
	@echo "Installing TailTray system-wide..."
	sudo cp dist/tailtray /usr/local/bin/tailtray
	sudo cp tailtray.desktop /usr/share/applications/
	sudo cp tailtray.svg /usr/share/icons/hicolor/scalable/apps/
	sudo cp tailtray.1 /usr/share/man/man1/

# Uninstall
uninstall:
	@echo "Uninstalling TailTray..."
	sudo rm -f /usr/local/bin/tailtray
	sudo rm -f /usr/share/applications/tailtray.desktop
	sudo rm -f /usr/share/icons/hicolor/scalable/apps/tailtray.svg
	sudo rm -f /usr/share/man/man1/tailtray.1