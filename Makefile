# Makefile for building the 'linkgraph' application with PyInstaller on Windows

.PHONY: build

# Define variables for paths to simplify changes later
ICON_PATH="images\\img.ico"
CONFIG_PATH="config.json"
IMAGE_PATH="images\\icon_app.png"
OUTPUT_NAME=linkgraph

build:
	@echo "Building the application..."
	pyinstaller --onefile --windowed --name=$(OUTPUT_NAME) --icon=$(ICON_PATH) --add-data "$(CONFIG_PATH);." --add-data "$(IMAGE_PATH);images" main.py
