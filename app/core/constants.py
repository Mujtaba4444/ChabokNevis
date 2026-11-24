APP_NAME = "ChabokNevis"
APP_VERSION = "1.0.0"

DEFAULT_LANGUAGE = "fa_AF"   # Dari is the default interface language

LEVELS = {1: "Beginner", 2: "Elementary", 3: "Intermediate", 4: "Advanced"}
LESSON_PASS_ACCURACY = 80.0  # % needed to complete a lesson

VARIANTS = {"iranian_persian": "Iranian Persian", "dari": "Dari (Afghanistan)"}

SPEED_TEST_DURATIONS = [(30, "30 seconds"), (60, "1 minute"), (180, "3 minutes"), (300, "5 minutes")]

NAV_ITEMS = [
    ("dashboard", "Dashboard"),
    ("learn", "Learn"),
    ("practice", "Practice"),
    ("speed_test", "Speed Test"),
    ("games", "Games"),
    ("statistics", "Statistics"),
    ("settings", "Settings"),
    ("about", "About"),
]

FINGER_NAMES = {
    "L5": "Left pinky", "L4": "Left ring finger", "L3": "Left middle finger", "L2": "Left index finger",
    "R2": "Right index finger", "R3": "Right middle finger", "R4": "Right ring finger", "R5": "Right pinky",
    "thumb": "Thumb",
}

DEFAULT_SETTINGS = {
    "content_variant": "iranian_persian",
    "keyboard_layout": "persian_windows",
    "theme": "light",
    "font_family": "Vazirmatn",
    "font_size": 22,
    "sound": False,
    "sound_correct": True,
    "sound_error": True,
    "sound_volume": 75,         # 0-100, default 75%
    "show_keyboard": True,
    "strict_mode": False,       # strict = exact characters (layout training)
    "accept_latin": True,       # map English-layout keys to Persian (no OS layout needed)
    "daily_goal_minutes": 10,
    "ui_language": DEFAULT_LANGUAGE,   # interface language code (see app/i18n/locales)
}
