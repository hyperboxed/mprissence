#!/bin/bash

APP_NAME="elisa-discord-rpc"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
SERVICE_FILE="$HOME/.config/systemd/user/$APP_NAME.service"

echo "Stopping service..."
systemctl --user stop $APP_NAME.service
systemctl --user disable $APP_NAME.service

if [ -f "$SERVICE_FILE" ]; then
    echo "Removing service file..."
    rm "$SERVICE_FILE"
    systemctl --user daemon-reload
fi

if [ -d "$INSTALL_DIR" ]; then
    echo "Removing program files..."
    rm -rf "$INSTALL_DIR"
fi

echo "Elisa Discord RPC successfully uninstalled."