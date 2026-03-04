<div align="center">

<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-0D1117?style=for-the-badge&logo=windows&logoColor=white"/>
<img src="https://img.shields.io/badge/ADB-Auto_Setup-4ADE80?style=for-the-badge&logo=android&logoColor=white"/>
<img src="https://img.shields.io/badge/Zero_Config-Ready_to_Run-0F2A1A?style=for-the-badge"/>
<img src="https://img.shields.io/badge/License-Proprietary-F87171?style=for-the-badge"/>

# ⚡ ROM Manager Pro


> Developed by [@alysonsb](https://github.com/alysonsb)

RomManagerPro is a cross-platform desktop tool for Android ROM management, built with Python and PySide6. It lets you extract partitions from `payload.bin` files, flash via fastboot, manage apps, run ADB/Fastboot commands and more — all through a modern graphical interface.

---

## ✨ Features

- 🖥 **Device Info** — Model, Android version, Serial, IMEI, RAM, Storage, Battery
- 📦 **App Manager** — Install APKs, list packages, debloat (disable/re-enable system apps)
- ⌨ **ADB Shell** — Run ADB commands directly from the UI
- ⚡ **Fastboot** — Flash individual partitions and quick actions (reboot, bootloader, recovery)
- 🗜 **Flash AOSP** — Extract `payload.bin` and flash partitions via fastboot
- 🔥 **Flash HyperOS** — Extract and run official flash scripts
- 🌐 **Multi-language** — English, Português, Español, Русский

---

## 🚀 Installation

Download the installer for your operating system from the [Releases](https://github.com/alysonsb/RomManagerPro-/releases/latest) page:

| Platform | File |
|----------|------|
| 🐧 Linux / macOS | `RomManagerPro.sh` |
| 🪟 Windows | `RomManagerPro-Setup.exe` |

**Linux / macOS:**
```bash
./RomManagerPro.sh
```

**Windows:** Run `RomManagerPro-Setup.exe` and follow the installer steps.

> The app will automatically offer to install **Android Platform Tools** and **payload-dumper-go** on first launch if they are not already present on your system.

---

## 📂 Project Structure

```
RomManagerPro/
├── main.py          # Entry point and main window
├── config.py        # Constants, URLs and translations
├── threads.py       # Background threads (flash, extraction, downloads)
├── dialogs.py       # Auxiliary dialogs and windows
├── ui_helpers.py    # Reusable UI components
└── utils.py         # Utility functions (ADB, versioning, permissions)
```

---

## 🙏 Credits & Third-Party Dependencies

### payload-dumper-go
This project uses **[payload-dumper-go](https://github.com/ssut/payload-dumper-go)**, developed by **[ssut](https://github.com/ssut)**, to extract partitions from `payload.bin` files found in Android ROM packages.

- 🔗 Repository: https://github.com/ssut/payload-dumper-go
- 📄 License: [Apache License 2.0](https://github.com/ssut/payload-dumper-go/blob/master/LICENSE)

RomManagerPro automatically downloads `payload-dumper-go` directly from its official GitHub releases and invokes it as an external process for partition extraction. No modifications are made to the original binary.

> Special thanks to **ssut** for the excellent open-source work that powers the core ROM extraction functionality of this project.

---

### Android Platform Tools (ADB / Fastboot)
Uses the **Android Platform Tools** distributed by Google for ADB communication and Fastboot operations.

- 🔗 https://developer.android.com/tools/releases/platform-tools

---

## ☕ Support the Project

If this project was helpful to you, consider buying me a coffee!

---

## 📄 License

Distributed under the MIT License. See the `LICENSE` file for more details.