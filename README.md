<div align="center">

# ChabokNevis (چابک‌نویس)

**Offline Persian (Dari & Iranian Farsi) Typing Tutor for Windows**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://microsoft.com/windows)

</div>

---

## Overview

**ChabokNevis** (چابک‌نویس) is a complete, offline typing tutor designed for learning Persian (Dari & Iranian Farsi) keyboard layouts. Built with Python and PySide6, it provides a structured learning path from beginner to advanced, with interactive exercises, real-time feedback, and comprehensive progress tracking.

### Key Features

| Feature | Description |
|---------|-------------|
| **Structured Lessons** | 4 levels (Beginner → Advanced) covering home row, top/bottom rows, numbers, punctuation, and literature |
| **Free Practice** | Characters, words, sentences, paragraphs, literature, and custom text modes |
| **Speed Tests** | Timed tests (30s, 1m, 3m, 5m) with WPM and accuracy scoring |
| **Virtual Keyboard** | 3D interactive keyboard with finger guidance and key highlighting |
| **Real-time Feedback** | Per-character color coding (green=correct, red=incorrect, highlight=current) |
| **Mechanical Keyboard Sounds** | Authentic click/clack sounds with volume control and variation pool |
| **Bilingual UI** | English and Dari (Afghan Persian) interfaces with RTL support |
| **Progress Tracking** | SQLite-backed statistics: WPM history, accuracy, daily goals, charts |
| **Themes** | Light and dark mode with automatic language-aware layout mirroring |
| **Font Selection** | Choose from system fonts with live preview in typing area |
| **Fully Offline** | No internet required; all data stored locally in SQLite |

---

## Screenshots

> Add screenshots here showing: Dashboard, Learn mode, Practice mode, Settings, Statistics, Virtual Keyboard

---

## Technologies

- **Language**: Python 3.10+
- **GUI Framework**: PySide6 (Qt 6)
- **Database**: SQLite (built-in, no server required)
- **Packaging**: PyInstaller + Inno Setup
- **Testing**: pytest

---

## Installation

### Prerequisites
- Windows 10/11 (64-bit)
- Python 3.10 or higher

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/ChabokNevis.git
cd ChabokNevis

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Windows Installer
Download the latest `ChabokNevis_Setup.exe` from [GitHub Releases](https://github.com/yourusername/ChabokNevis/releases) and run it.

---

## Project Structure

```
ChabokNevis/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .gitignore                 # Git ignore rules
├── app/
│   ├── core/                  # Core configuration & constants
│   ├── engine/                # Typing engine & text normalization
│   ├── i18n/                  # Internationalization (EN / Dari)
│   │   ├── locales/
│   │   │   ├── en.json        # English translations
│   │   │   └── fa_AF.json     # Dari translations
│   │   └── translator.py      # Translation manager
│   ├── resources/             # Fonts, icons, sounds, images
│   │   ├── fonts/             # Embedded fonts (Vazirmatn, etc.)
│   │   ├── icons/             # Application icons
│   │   ├── images/            # Brand images
│   │   └── sounds/            # Mechanical keyboard WAV sounds
│   ├── services/              # Settings, content, progress, sound
│   ├── ui/
│   │   ├── widgets/           # Reusable UI components
│   │   ├── dashboard/         # Dashboard page
│   │   ├── learn/             # Learn/lessons page
│   │   ├── practice/          # Practice page
│   │   ├── speed_test/        # Speed test page
│   │   ├── statistics/        # Statistics page
│   │   ├── settings/          # Settings page
│   │   ├── about/             # About page
│   │   └── main_window.py     # Main window & navigation
│   └── config.py              # Resource/content path helpers
├── content/
│   ├── shared/                # Shared lessons & practice pools
│   ├── dari/                  # Dari-specific content
│   ├── iranian_persian/       # Iranian Persian-specific content
│   └── layouts/               # Keyboard layout definitions
└── tests/                     # Unit tests
    ├── test_engine.py
    ├── test_hands.py
    └── test_i18n.py
```

---

## Usage

### Learning Flow
1. **Dashboard** → View progress, daily goal, next lesson
2. **Learn** → Structured lessons by level (start with home row)
3. **Practice** → Free practice: characters, words, sentences, custom text
4. **Speed Test** → Timed tests for WPM measurement
5. **Statistics** → Detailed charts and history

### Keyboard Input Modes
- **OS Persian Keyboard**: Direct character input
- **English OS Layout**: Keys mapped to Persian letters on same physical key (Settings → "Accept English-layout keys as Persian")
- **Relaxed Mode** (default): Treats Arabic ي/ك as Persian ی/ک, unifies digit styles
- **Strict Mode**: Requires exact character matching (for layout training)

### Settings
- **Language**: English / Dari (افغانستان)
- **Theme**: Light / Dark
- **Font**: Family and size for typing area
- **Virtual Keyboard**: Show/hide 3D keyboard
- **Sounds**: Enable/disable, correct key sound, error sound, volume slider (0–100%)
- **Strict Mode**: Exact character matching
- **Daily Goal**: Minutes per day target

---

## Development

### Run Tests
```bash
pytest
```

### Build Executable
```bash
pyinstaller --noconsole --name ChabokNevis \
  --add-data "content;content" \
  --add-data "app/resources;app/resources" \
  --add-data "app/i18n/locales;app/i18n/locales" \
  main.py
```

### Create Installer (Windows)
Use the provided `app/resources/icons/ChabokNevis_Setup.iss` with Inno Setup Compiler.

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8
- Type hints encouraged
- Write tests for new features
- Update translations for new UI text

---

## Developer

**Mohammad Mujtaba Mohammadi**

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Vazirmatn Font](https://github.com/rastikerdar/vazirmatn) for Persian typography
- Qt/PySide6 team for the excellent framework
- Persian typing community for layout standards

---

<div align="center">

**Built with ❤️ for Persian language learners**

</div>