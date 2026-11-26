<div align="center">

# چابک‌نویس | ChabokNevis

### A Persian/Dari and English Typing Tutor for Windows

Improve your typing speed, accuracy, and keyboard skills with ChabokNevis.

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-6.6%2B-green?logo=qt&logoColor=white" alt="PySide6">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/Version-1.0.1-success" alt="Version">
</p>

<p>
  <a href="https://github.com/Mujtaba4444/ChabokNevis/releases/latest/download/ChabokNevis_Setup.exe">
    <img src="https://img.shields.io/badge/Download-ChabokNevis-brightgreen?style=for-the-badge&logo=windows" alt="Download ChabokNevis">
  </a>
</p>

<p>
  <a href="https://github.com/Mujtaba4444/ChabokNevis/releases">All Releases</a> •
  <a href="https://github.com/Mujtaba4444/ChabokNevis/issues">Report a Bug</a> •
  <a href="https://github.com/Mujtaba4444">GitHub Profile</a>
</p>

</div>

---

## Overview

**ChabokNevis (چابک‌نویس)** is a desktop typing tutor designed to help users improve their typing speed, accuracy, and keyboard skills.

It supports Persian/Dari and English typing, providing interactive lessons, real-time typing feedback, mechanical keyboard sound effects, and progress statistics.

The application works offline and stores user data locally.

## Download

The latest version is **v1.0.1**.

### Windows Installer

Download and run the installer:

**[Download ChabokNevis for Windows](https://github.com/Mujtaba4444/ChabokNevis/releases/latest/download/ChabokNevis_Setup.exe)**

No separate Python installation is required when using the Windows installer.

For previous versions, visit the [Releases page](https://github.com/Mujtaba4444/ChabokNevis/releases).

### System Requirements

| Requirement | Minimum |
|---|---|
| Operating System | Windows 10 or later |
| Architecture | 64-bit |
| Internet Connection | Not required |
| Python | Not required for the installer |

---

## Features

| Feature | Description |
|---|---|
| **Two Languages** | Supports Persian/Dari and English typing. |
| **Interactive Lessons** | Practice typing through structured lessons and exercises. |
| **Real-Time Feedback** | Instantly identifies correct and incorrect characters. |
| **Character Highlighting** | Displays correct characters in green and incorrect characters in red. |
| **Keyboard Sound Effects** | Provides mechanical keyboard sounds while typing. |
| **Adjustable Sound Volume** | Allows users to control keyboard sound volume. |
| **Typing Statistics** | Tracks typing performance and progress. |
| **Language Settings** | Switch between the supported application languages. |
| **Offline Functionality** | Works without an internet connection. |
| **Local Storage** | Stores application data locally using SQLite. |
| **Modern Interface** | Provides a clean desktop interface designed with PySide6. |

---

## Screenshots

<!-- Add your application screenshots here. -->

<!--
<p align="center">
  <img src="screenshots/dashboard.png" width="800" alt="ChabokNevis Dashboard">
</p>

<p align="center">
  <img src="screenshots/typing.png" width="800" alt="Typing Practice">
</p>

<p align="center">
  <img src="screenshots/settings.png" width="800" alt="Application Settings">
</p>
-->

---

## Technologies

ChabokNevis is built using the following technologies:

| Technology | Purpose |
|---|---|
| **Python** | Main programming language |
| **PySide6** | Desktop graphical user interface |
| **SQLite** | Local database |
| **PyInstaller** | Application packaging |
| **Inno Setup** | Windows installer creation |
| **pytest** | Automated testing |

---

## Installation

### Option 1: Windows Installer (Recommended)

1. Download `ChabokNevis_Setup.exe` from the [latest release](https://github.com/Mujtaba4444/ChabokNevis/releases/latest).
2. Run the installer.
3. Follow the installation instructions.
4. Launch ChabokNevis from the Start Menu or desktop shortcut.

### Option 2: Run from Source

If you want to run the application from its source code:

**1. Clone the repository**

```bash
git clone https://github.com/Mujtaba4444/ChabokNevis.git
```

**2. Navigate to the project directory**

```bash
cd ChabokNevis
```

**3. Create a virtual environment**

```bash
python -m venv .venv
```

**4. Activate the virtual environment**

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

**5. Install dependencies**

```bash
pip install -r requirements.txt
```

**6. Run the application**

```bash
python main.py
```

---

## Project Structure

```text
ChabokNevis/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── ChabokNevis_Setup.iss
│
├── app/
│   ├── core/
│   ├── database/
│   ├── engine/
│   ├── i18n/
│   │   └── locales/
│   ├── resources/
│   │   ├── fonts/
│   │   ├── icons/
│   │   ├── images/
│   │   └── sounds/
│   ├── services/
│   └── ui/
│
├── content/
│
└── tests/
```

---

## Usage

1. Launch ChabokNevis.
2. Choose your preferred application language.
3. Select a typing lesson or exercise.
4. Start typing the displayed text.
5. Observe the real-time character feedback.
6. Review your typing statistics and progress.
7. Customize application settings, including keyboard sound volume.

---

## Development

### Run Tests

To execute the automated test suite:

```bash
pytest tests --import-mode=importlib
```

### Build the Application

The application can be packaged using PyInstaller:

```bash
pyinstaller --noconfirm --clean --windowed --onedir --name ChabokNevis --icon "app/resources/icons/ChabokNevis.ico" --add-data "app/resources;app/resources" --add-data "app/i18n/locales;app/i18n/locales" --add-data "content;content" main.py
```

The generated application will be located in:

```text
dist/ChabokNevis/
```

### Create the Windows Installer

The Windows installer is configured using:

```text
ChabokNevis_Setup.iss
```

Open the script with Inno Setup Compiler to build the installer.

---

## Contact & Support

Have a question, found a bug, or want to suggest an improvement?

- **GitHub Profile:** [@Mujtaba4444](https://github.com/Mujtaba4444)
- **Bug Reports:** [Open an Issue](https://github.com/Mujtaba4444/ChabokNevis/issues)
- **Feature Requests:** [Submit a Feature Request](https://github.com/Mujtaba4444/ChabokNevis/issues/new)

For general questions and project-related discussions, feel free to use GitHub.

---

## Acknowledgments

Thank you to everyone who supports the development of ChabokNevis and helps improve the project through feedback and suggestions.

---

<div align="center">

**ChabokNevis | چابک‌نویس**

Made with Python and PySide6.

[GitHub Repository](https://github.com/Mujtaba4444/ChabokNevis) • [Releases](https://github.com/Mujtaba4444/ChabokNevis/releases) • [Support](https://github.com/Mujtaba4444/ChabokNevis/issues)

</div>
