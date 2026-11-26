<div align="center">

# ChabokNevis (چابک‌نویس)

**Offline Persian (Dari & Iranian Farsi) Typing Tutor for Windows**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-6.6+-green.svg)](https://pypi.org/project/PySide6/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://microsoft.com/windows)
[![Version](https://img.shields.io/badge/Version-1.0.1-blue.svg)](https://github.com/Mujtaba4444/ChabokNevis/releases/latest)

</div>

---

## Overview

**ChabokNevis** (چابک‌نویس) is a complete, offline typing tutor designed for learning Persian (Dari & Iranian Farsi) keyboard layouts. Built with Python and PySide6, it provides a structured learning path from beginner to advanced, with interactive exercises, real-time feedback, and comprehensive progress tracking.

## Download

**Latest Release: v1.0.1**

Download ChabokNevis for Windows:

<div align="center">

### [Download ChabokNevis v1.0.1 — Windows Installer](https://github.com/Mujtaba4444/ChabokNevis/releases/latest/download/ChabokNevis_Setup.exe)

</div>

### System Requirements

- Windows 10 or later.
- 64-bit Windows.
- No Python installation required.

**Installation:** Download `ChabokNevis_Setup.exe`, run it, and follow the installation instructions.

[View All Releases](https://github.com/Mujtaba4444/ChabokNevis/releases)

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Structured Lessons** | 4 levels (Beginner → Advanced) covering home row, top/bottom rows, numbers, punctuation, and literature |
| **Free Practice** | Characters, words, sentences, paragraphs, literature, and custom text modes |
| **Speed Tests** | Timed tests (30s, 1m, 3m, 5m) with WPM and accuracy scoring |
| **Virtual Keyboard** | 3D interactive keyboard with finger guidance and key highlighting |
| **Real-time Feedback** | Per-character color coding (green = correct, red = incorrect, highlight = current) |
| **Wrong-Character Sound** | Error sounds with multiple options, volume control, and preview |
| **Bilingual UI** | English and Dari (Afghan Persian) interfaces with RTL support |
| **Progress Tracking** | SQLite-backed statistics: WPM history, accuracy, daily goals, and charts |
| **Themes** | Light and dark modes with automatic language-aware layout mirroring |
| **Font Selection** | Choose from system fonts with live preview in the typing area |
| **Fully Offline** | No internet required; all data stored locally in SQLite |

---

## Screenshots

<!-- Add application screenshots to the screenshots/ directory and uncomment these examples. -->

<!--
### Dashboard
![Dashboard](screenshots/dashboard.png)

### Learn Mode
![Learn Mode](screenshots/learn.png)

### Practice Mode
![Practice Mode](screenshots/practice.png)

### Settings
![Settings](screenshots/settings.png)

### Statistics
![Statistics](screenshots/statistics.png)

### Virtual Keyboard
![Virtual Keyboard](screenshots/virtual-keyboard.png)
-->

---

## Technologies

- **Language:** Python 3.10+
- **GUI Framework:** PySide6 (Qt 6)
- **Database:** SQLite (built-in, no server required)
- **Packaging:** PyInstaller + Inno Setup
- **Testing:** pytest

---

## Installation

### Windows Installer (Recommended)

1. Visit [ChabokNevis Releases](https://github.com/Mujtaba4444/ChabokNevis/releases).
2. Download the latest `ChabokNevis_Setup.exe`.
3. Run the installer.
4. Follow the installation instructions.
5. Launch ChabokNevis from the Desktop shortcut or Start Menu.

No Python installation is required when using the Windows installer.

### From Source

#### Prerequisites

- Windows 10 or later (64-bit).
- Python 3.10 or higher.
- Git.

#### Setup

Clone the repository:

```bash
git clone https://github.com/Mujtaba4444/ChabokNevis.git
cd ChabokNevis
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

---

## Project Structure

```text
ChabokNevis/
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
│   │   ├── locales/
│   │   │   ├── en.json
│   │   │   └── fa_AF.json
│   │   └── translator.py
│   │
│   ├── resources/
│   │   ├── fonts/
│   │   ├── icons/
│   │   ├── images/
│   │   └── sounds/
│   │
│   ├── services/
│   ├── ui/
│   │   ├── widgets/
│   │   ├── dashboard/
│   │   ├── learn/
│   │   ├── practice/
│   │   ├── speed_test/
│   │   ├── statistics/
│   │   ├── settings/
│   │   ├── about/
│   │   └── main_window.py
│   │
│   └── config.py
│
├── content/
│   ├── shared/
│   ├── dari/
│   ├── iranian_persian/
│   └── layouts/
│
├── tests/
│
└── extras/
```

---

## Usage

### Learning Flow

1. **Dashboard** → View progress, daily goal, and next lesson.
2. **Learn** → Follow structured lessons by level, starting with the home row.
3. **Practice** → Improve typing through characters, words, sentences, and custom text.
4. **Speed Test** → Take timed tests to measure your typing speed.
5. **Statistics** → Review detailed typing statistics and progress history.

### Keyboard Input Modes

- **OS Persian Keyboard:** Direct Persian character input.
- **English OS Layout:** Physical keys mapped to their corresponding Persian letters.
- **Relaxed Mode (Default):** Treats Arabic ي/ك as Persian ی/ک and unifies digit styles.
- **Strict Mode:** Requires exact character matching for keyboard layout training.

### Settings

- **Language:** English / Dari (افغانستان).
- **Theme:** Light / Dark.
- **Font:** Customize typing area font family and size.
- **Virtual Keyboard:** Show or hide the 3D keyboard.
- **Sounds:** Enable or disable wrong-character sounds, select sound effects, preview sounds, and adjust volume.
- **Strict Mode:** Enable exact character matching.
- **Daily Goal:** Set a daily typing practice target.

---

## Development

### Run Tests

Run the project's test suite:

```powershell
pytest tests --import-mode=importlib
```

### Build Executable

Build the standalone Windows application using PyInstaller:

```powershell
pyinstaller --noconfirm --clean --windowed --onedir --name ChabokNevis --icon "app/resources/icons/ChabokNevis.ico" --add-data "app/resources;app/resources" --add-data "app/i18n/locales;app/i18n/locales" --add-data "content;content" main.py
```

The executable will be generated at:

```text
dist/ChabokNevis/ChabokNevis.exe
```

### Create Windows Installer

The Inno Setup script is located in the project root:

```text
ChabokNevis_Setup.iss
```

Open it using Inno Setup Compiler and compile it to generate the Windows installer.

---

## Contributing

Contributions and suggestions are welcome.

For contributions:

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature/amazing-feature
   ```

3. Commit your changes:

   ```bash
   git commit -m "Add amazing feature"
   ```

4. Push your branch:

   ```bash
   git push origin feature/amazing-feature
   ```

5. Open a Pull Request.

### Code Style

- Follow PEP 8 guidelines.
- Use type hints where appropriate.
- Write tests for new features.
- Update translations when adding new interface text.

---

## Developer

**Mohammad Mujtaba Mohammadi**

- GitHub: [@Mujtaba4444](https://github.com/Mujtaba4444)
- Email: mujtaba.mohd.4444@gmail.com

---

## Acknowledgments

- [Vazirmatn Font](https://github.com/rastikerdar/vazirmatn) for Persian typography.
- Qt and PySide6 teams for the excellent framework.
- Persian typing community for keyboard layout standards.

---

<div align="center">

**Built with ❤️ for Persian language learners**

**ChabokNevis (چابک‌نویس)**

</div>
