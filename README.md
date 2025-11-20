# 🎵 Elisa Music Player Discord RPC

A lightweight, feature-rich Discord Rich Presence (RPC) client for the Elisa Music Player (and other MPRIS-compatible players) on Linux.

![alt text](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)


![alt text](https://img.shields.io/badge/Linux-D--Bus-orange?style=for-the-badge&logo=linux)


![alt text](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

This daemon connects to Elisa via D-Bus/MPRIS and updates your Discord status with the current track, artist, elapsed time, and album art.

✨ Features

Rich Metadata: Displays Track Title, Artist, and Album.

Smart Cover Art System:

Remote URLs: If the player provides an HTTP URL, it uses it.

Local Files: If the cover is stored locally on your disk, it temporarily uploads it to Imgur so Discord can display it.

Fallback Search: If no cover is found, it searches iTunes API to find the correct artwork.

Seek Detection: Correctly updates the timestamp if you scrub/seek through the song.

Pause Handling: Shows a "Paused" status or clears the presence when stopped.

Systemd Integration: Runs silently in the background as a user service.

🚀 Installation

An automated installer is included to handle dependencies (Python venv, DBus headers) and service registration.

1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/elisa-discord-rpc.git
cd elisa-discord-rpc
```

2. Run the installer
```bash
chmod +x install.sh
./install.sh
```

The script will check for necessary system libraries (like libdbus-1-dev), set up a virtual environment, and register the systemd service.

🛠 Management

Since the script runs as a systemd user service, you can manage it using standard commands:

Check status:

code
Bash
download
content_copy
expand_less
systemctl --user status elisa-discord-rpc

View logs (useful for debugging):

code
Bash
download
content_copy
expand_less
journalctl --user -u elisa-discord-rpc -f

Restart the service:

code
Bash
download
content_copy
expand_less
systemctl --user restart elisa-discord-rpc

Stop the service:

code
Bash
download
content_copy
expand_less
systemctl --user stop elisa-discord-rpc
🗑 Uninstallation

If you want to remove the RPC client and clean up all files:

code
Bash
download
content_copy
expand_less
chmod +x uninstall.sh
./uninstall.sh
🧩 How it Works

This script uses dbus-python to listen to the org.mpris.MediaPlayer2.elisa interface.

Activity: It updates the Discord status every second only if the state has changed (track change, seek, pause).

Performance: It uses a persistent connection and caches cover art URLs to minimize API usage and CPU load.

Imgur: Local cover art uploads are anonymous and deleted from memory when the track changes (handled via Imgur delete hashes where possible).

📝 Requirements

Linux OS (Arch, Ubuntu, Fedora, etc.)

Python 3

dbus-python prerequisites (handled by install.sh):

Debian/Ubuntu: libdbus-1-dev libglib2.0-dev

Arch: dbus-glib

Fedora: dbus-devel

🤝 Contributing

Feel free to open issues or pull requests if you find bugs or want to add support for other MPRIS players!

Built with ❤️ for the Linux community.