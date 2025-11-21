```
███╗   ███╗██████╗ ██████╗ ██╗██████╗
████╗ ████║██╔══██╗██╔══██╗██║██╔════╝
██╔████╔██║██████╔╝██████╔╝██║███████╗
██║╚██╔╝██║██╔═══╝ ██╔══██╗██║╚════██║
██║ ╚═╝ ██║██║     ██║  ██║██║███████║
╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝
            S E N C E
```

# 🎵 **Elisa Music Player Discord RPC**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/Linux-D--Bus-orange?style=for-the-badge&logo=linux"/>
  <img src="https://img.shields.io/badge/MPRIS-Compatible-purple?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Discord-RPC-5865F2?style=for-the-badge&logo=discord&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

A lightweight, feature-rich Discord Rich Presence (RPC) client for the **Elisa Music Player** (for now) on Linux.

Technically, it should work on any MPRIS-compatible player, but it needs to be tested on other players, plus it needs some more customization (like icons for the corresponding players). So, only for **Elisa** for now.

It also features cover art fetching from iTunes.
If the cover isn't found on iTunes, it will be uploaded to Imgur and cached for future use, and then deleted from Imgur when the track is no longer playing!

✨ Automatically updates your Discord status with track title, artist, progress, playback state, and album art.

---

## 📚 **Table of Contents**

* [✨ Features](#-features)
* [🖼 Preview](#-preview)
* [🚀 Installation](#-installation)
* [🛠 Management](#-management)
* [🗑 Uninstallation](#-uninstallation)
* [🧩 How it Works](#-how-it-works)
* [📦 Requirements](#-requirements)
* [🤝 Contributing](#-contributing)

---

## ✨ **Features**

| Function               | Status | Description                                      |
| ---------------------- | ------ | ------------------------------------------------ |
| 🎵 Rich Metadata       | ✔      | Track name, artist, album                        |
| 🖼 Smart Cover Art     | ✔      |  iTunes search fallback + local file upload |
| ⏱️ Seek Detection       | ✔      | Correct timestamp calculation                    |
| 💤 Pause/Stop Logic    | ✔      | Smart status hiding/switching                    |
| 🔥 Systemd Integration | ✔      | Background service without interface             |
| 📦 Caching             | ✔      | Minimizes API requests to save traffic             |

---

## 🖼 **Preview**

<p align="center">
  <img src="https://github.com/hyperboxed/mprissence/blob/main/screenshots/preview.jpg" width="300" />
</p>

---

## 🚀 **Installation**

1. **Clone the repository**

```bash
git clone https://github.com/hyperboxed/mprissence.git
cd mprissence
```

2. **Run the installer**

```bash
chmod +x install.sh
./install.sh
```

‼️ Note that the "install.sh" script **DOES NOT** need root privileges!

The script automatically:

* Checks DBus development headers
* Creates Python virtual environment
* Installs Python dependencies
* Registers a systemd user service

---

## 🛠 **Management**

Check status:

```bash
systemctl --user status mprissence
```

View logs:

```bash
journalctl --user -u mprissence -f
```

Restart:

```bash
systemctl --user restart mprissence
```

Stop:

```bash
systemctl --user stop mprissence
```

---

## 🗑 **Uninstallation**

```bash
chmod +x uninstall.sh
./uninstall.sh
```

---

## 🧩 **How it Works**

### 🖧 Architecture

```mermaid
flowchart LR
    A[Elisa Player] --> B[MPRIS / DBus]
    B --> C[RPC Daemon]
    C --> D[Discord IPC]
```

### 🔍 Activity Logic

* Updates every second **only when state changes**
* Detects seek events and recalculates timestamps
* Clears presence when playback stops

### ⚙ Performance

* Persistent DBus session
* Cached artwork + delete-hashes
* Minimal CPU usage

---

## 📦 **Requirements**

* Linux OS (Arch, Ubuntu, Fedora, etc.)
* Python 3
* DBus/MPRIS
* Development headers:

  * Debian/Ubuntu: `libdbus-1-dev libglib2.0-dev`
  * Arch: `dbus-glib`
  * Fedora: `dbus-devel`

‼️ By the way, the installation script will automatically install the required dependencies

---

## 🤝 **Contributing**

Any PR's and issues are welcome, especially if you want to add even more features

---

<p align="center">
Made with ❤️ for the Linux community <3<br/>
If you like this project, please leave a ⭐ on GitHub!
</p>
