#!/bin/bash

# define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# configuration
APP_NAME="elisa-discord-rpc"
SCRIPT_NAME="elisa_rpc.py"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/$APP_NAME.service"

# 1. display ASCII Art
echo -e "${GREEN}"
cat << "EOF"
   __  __ ____  ____  ___ ____ 
  |  \/  |  _ \|  _ \|_ _/ ___|
  | |\/| | |_) | |_) || |\___ \
  | |  | |  __/|  _ < | | ___) |
  |_|  |_|_|   |_| \_\___|____/
            S E N C E
EOF
echo -e "${NC}"
echo "Installing MPRIS Discord Presence for Elisa..."
echo "----------------------------------------------"

# 2. function to install system dependencies
install_system_deps() {
    echo -e "${YELLOW}Missing Python 3 or build dependencies (headers) required for dbus-python.${NC}"
    
    # detect Linux Distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        ID=$ID
    else
        echo -e "${RED}Could not detect Linux distribution.${NC}"
        exit 1
    fi

    echo "Detected System: $OS"
    echo "We need to install: Python 3, pip, venv, and DBus development headers."

    CMD=""
    PACKAGES=""

    # determine package manager commands based on distro ID
    case "$ID" in
        ubuntu|debian|linuxmint|pop|neon)
            CMD="sudo apt update && sudo apt install -y"
            # Ubuntu separates venv and pip
            # dbus headers are needed for compilation
            PACKAGES="python3 python3-pip python3-venv libdbus-1-dev libglib2.0-dev gcc pkg-config"
            ;;
        fedora|rhel|centos)
            CMD="sudo dnf install -y"
            # Fedora uses dbus-devel instead of libdbus-1-dev
            PACKAGES="python3 python3-pip dbus-devel glib2-devel gcc"
            ;;
        arch|manjaro|endeavouros)
            CMD="sudo pacman -S --noconfirm"
            # Arch uses dbus-glib instead of libdbus-1-dev
            PACKAGES="python python-pip dbus-glib base-devel"
            ;;
        opensuse*|suse)
            CMD="sudo zypper install -y"
            # openSUSE uses dbus-1-devel instead of libdbus-1-dev
            PACKAGES="python3 python3-pip dbus-1-devel glib2-devel gcc"
            ;;
        *)
            echo -e "${RED}Your distribution ($ID) is not automatically supported.${NC}"
            echo "Please manually install Python 3 and DBus/GLib development headers."
            exit 1
            ;;
    esac

    # ask for user permission before running sudo
    echo -e "Command to run: ${GREEN}$CMD $PACKAGES${NC}"
    read -p "Do you want to proceed with system package installation (sudo password required)? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ -n $REPLY ]]; then
        echo "Installation cancelled."
        exit 1
    fi

    # exec command
    eval "$CMD $PACKAGES"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install system packages.${NC}"
        exit 1
    fi
}

# 3. check prerequisites
echo "Checking prerequisites..."

# check for Python 3, pip, and venv module
if ! command -v python3 &> /dev/null || \
   ! python3 -c "import venv" &> /dev/null || \
   ! command -v pip3 &> /dev/null; then
    install_system_deps
fi

# check for DBus headers (using pkg-config if available)
# this is a "soft" check. If pkg-config is missing, we proceed and let pip fail later if needed.
if command -v pkg-config &> /dev/null; then
    if ! pkg-config --exists dbus-1; then
        echo -e "${YELLOW}DBus headers seem missing.${NC}"
        install_system_deps
    fi
fi

# 4. prepare installation directory
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing previous installation..."
    rm -rf "$INSTALL_DIR"
fi

echo "Creating directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# check if source files exist in current directory
if [ ! -f "$SCRIPT_NAME" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: $SCRIPT_NAME or requirements.txt not found in current directory.${NC}"
    echo "Please run this script from the repository root."
    exit 1
fi

echo "Copying files..."
cp "$SCRIPT_NAME" "$INSTALL_DIR/"
cp "requirements.txt" "$INSTALL_DIR/"

# 5. set up python venv
echo "Creating Python Virtual Environment..."
python3 -m venv "$INSTALL_DIR/venv"

if [ ! -d "$INSTALL_DIR/venv" ]; then
    echo -e "${RED}Failed to create virtual environment.${NC}"
    exit 1
fi

echo "Installing Python dependencies (pypresence, dbus-python, requests)..."
# activate venv temporarily for this shell instance
source "$INSTALL_DIR/venv/bin/activate"

# upgrade pip to avoid warnings
pip install --upgrade pip > /dev/null 2>&1

# install requirements
if pip install -r "$INSTALL_DIR/requirements.txt"; then
    echo -e "${GREEN}Python dependencies installed successfully.${NC}"
else
    echo -e "${RED}Failed to install Python dependencies.${NC}"
    echo "This is usually caused by missing C compilers or DBus headers."
    echo "Try running the script again or install 'dbus-devel'/'libdbus-1-dev' manually."
    exit 1
fi

deactivate

# 6. create systemd service
echo "Configuring systemd user service..."
mkdir -p "$SERVICE_DIR"

# generate service file
# we use the absolute path to the venv python executable
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=Discord RPC for Elisa Music Player
After=network.target sound.target

[Service]
Type=simple
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/$SCRIPT_NAME
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

echo "Reloading systemd..."
systemctl --user daemon-reload

echo "Enabling and starting service..."
systemctl --user enable "$APP_NAME.service"
systemctl --user restart "$APP_NAME.service"

# 7. verification & done
echo "----------------------------------------------"
# check if service is active
if systemctl --user is-active --quiet "$APP_NAME.service"; then
    echo -e "${GREEN}Success! The RPC service is running.${NC}"
else
    echo -e "${YELLOW}Service installed, but currently not active.${NC}"
    echo "Check logs with: journalctl --user -u $APP_NAME -f"
fi

echo -e "You can verify status anytime with: ${YELLOW}systemctl --user status $APP_NAME${NC}"
echo "----------------------------------------------"