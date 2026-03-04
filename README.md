<div align="center">

# ⚡ ROM Manager Pro

<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-0D1117?style=for-the-badge&logo=windows&logoColor=white"/>
<img src="https://img.shields.io/badge/ADB-Auto_Setup-4ADE80?style=for-the-badge&logo=android&logoColor=white"/>
<img src="https://img.shields.io/badge/Zero_Config-Ready_to_Run-0F2A1A?style=for-the-badge"/>
<img src="https://img.shields.io/badge/License-MIT-4ADE80?style=for-the-badge"/>

Cross-platform Android ROM management tool built with **Python + PySide6**

Developed by [@alysonsb](https://github.com/alysonsb)

</div>

---

## 📌 Overview

**RomManagerPro** is a modern desktop application designed to simplify Android ROM management.

It allows you to:

- Extract partitions from `payload.bin`
- Flash images via Fastboot
- Manage apps using ADB
- Execute advanced commands
- Perform ROM operations safely through a clean graphical interface

No complex setup required.

---

## ✨ Features

### 📱 Device Information
- Model
- Android Version
- Serial Number
- IMEI
- RAM
- Storage
- Battery status

### 📦 App Management
- Install APK files
- List installed packages
- Disable / Re-enable system apps (debloat)

### ⌨ ADB Shell
- Execute custom ADB commands directly from the interface

### ⚡ Fastboot Tools
- Flash individual partitions
- Reboot system / bootloader / recovery
- Quick device actions

### 🗜 AOSP ROM Flashing
- Extract `payload.bin`
- Automatically flash extracted partitions

### 🔥 HyperOS Flash Support
- Extract official packages
- Execute built-in flash scripts

### 🌍 Multi-language Support
- English
- Português
- Español
- Русский

---

## 🚀 Installation

Download the latest version:

https://github.com/alysonsb/RomManagerPro-/releases/latest

| Platform | File |
|----------|------|
| 🐧 Linux | `RomManagerPro.sh` |
| 🪟 Windows | `RomManagerPro-Setup.exe` |

### Linux
```bash
chmod +x RomManagerPro.sh
./RomManagerPro.sh
```

### Windows
Run `RomManagerPro-Setup.exe` and follow the installer steps.

---

## 🔧 First Launch

On first startup, RomManagerPro will automatically offer to install:

- Android Platform Tools (ADB / Fastboot)
- payload-dumper-go

No manual configuration required.

---

## 📂 Project Structure

```
RomManagerPro/
├── main.py          # Entry point
├── config.py        # Constants and translations
├── threads.py       # Background operations
├── dialogs.py       # Dialog windows
├── ui_helpers.py    # UI components
└── utils.py         # ADB / Fastboot utilities
```

---

## 🙏 Credits

### payload-dumper-go

Used for extracting partitions from `payload.bin`.

Repository:
https://github.com/ssut/payload-dumper-go

License:
Apache License 2.0

RomManagerPro downloads the original binary directly from official releases without modification.

---

### Android Platform Tools

Official ADB and Fastboot tools provided by Google.

https://developer.android.com/tools/releases/platform-tools

---

## ☕ Support

If this project helps you, consider supporting its development.

---

## 📄 License

This project is licensed under the MIT License.  
See the `LICENSE` file for details.