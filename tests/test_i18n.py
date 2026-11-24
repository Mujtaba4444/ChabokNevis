import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
import _qt_stub  # noqa: E402

_qt_stub.install()

from PySide6.QtCore import Qt  # noqa: E402

LOCALES = ROOT / "app" / "i18n" / "locales"
EN = json.loads((LOCALES / "en.json").read_text(encoding="utf-8"))
FA = json.loads((LOCALES / "fa_AF.json").read_text(encoding="utf-8"))
PLACEHOLDER = re.compile(r"\{(\w+)(?::[^}]*)?\}")


def _keys(d):
    return {k for k in d if k != "_meta"}


def test_locales_have_identical_keys():
    assert _keys(EN) == _keys(FA), sorted(_keys(EN) ^ _keys(FA))


def test_placeholders_match_between_languages():
    for k in _keys(EN):
        if k == "lesson.code":      # the code can be shown as "L1-01" or as level-number; all three values are always passed
            assert set(PLACEHOLDER.findall(FA[k])) <= {"id", "level", "num"}
            continue
        assert set(PLACEHOLDER.findall(EN[k])) == set(PLACEHOLDER.findall(FA[k])), k


def test_no_empty_translations_and_meta_complete():
    assert all(FA[k].strip() for k in _keys(FA))
    for meta in (EN["_meta"], FA["_meta"]):
        for field in ("code", "native", "rtl", "digits", "qt_locale", "fonts", "font_size"):
            assert field in meta
    assert FA["_meta"]["rtl"] is True and EN["_meta"]["rtl"] is False


def test_dari_has_no_stray_english_words():
    allowed = re.compile(r"SQLite|F11|Shift|Backspace|Language|[A-Z]( [A-Z])*|[JKL];?|/|\{[^}]*\}")
    for k in _keys(FA):
        text = allowed.sub("", FA[k])
        assert not re.search(r"[A-Za-z]{2,}", text), (k, FA[k])


def _source_keys():
    keys = set()
    pats = [r'\btr\(\s*"([\w.]+)"', r'\btlabel\(\s*"([\w.]+)"', r'\bStatCard\(\s*"([\w.]+)"',
            r'\.bind\([^,\n]+,\s*"([\w.]+)"', r'\bbind_combo\([^,\n]+,\s*"([\w.{}]+)"']
    for p in (ROOT / "app").rglob("*.py"):
        text = p.read_text(encoding="utf-8")
        for pat in pats:
            keys.update(re.findall(pat, text))
    return keys


def test_every_key_used_in_code_exists():
    missing = [k for k in _source_keys() if "{" not in k and k not in EN]
    assert not missing, missing


def test_dynamic_key_families_exist():
    fams = ([f"nav.{k}" for k in ("dashboard", "learn", "practice", "speed_test", "games", "statistics", "settings", "about")]
            + [f"level.{i}" for i in range(1, 5)] + [f"session.{s}" for s in ("lesson", "practice", "speed_test")]
            + [f"finger.{f}" for f in ("L5", "L4", "L3", "L2", "R2", "R3", "R4", "R5", "TL", "TR")]
            + [f"speed.dur.{s}" for s in (30, 60, 180, 300)] + [f"practice.dur.{s}" for s in (0, 60, 120, 180, 300)]
            + [f"practice.cat.{c}" for c in ("characters", "words", "sentences", "paragraphs", "literature", "educational", "conversation", "custom")]
            + [f"practice.diff.{i}" for i in (1, 2, 3)] + ["theme.light", "theme.dark", "variant.dari", "variant.iranian_persian", "layout.persian_windows"]
            + [f"speed.col.{c}" for c in ("date", "duration", "wpm", "accuracy", "chars")])
    for lessons in ("content/shared/lessons.json", "content/dari/lessons.json", "content/iranian_persian/lessons.json"):
        for d in json.loads((ROOT / lessons).read_text(encoding="utf-8")):
            fams += [f"lesson.{d['id']}.title", f"lesson.{d['id']}.intro"]
    assert [k for k in fams if k not in EN or k not in FA] == []


def test_no_hardcoded_english_ui_strings_left():
    """Widgets must get their text from translation keys, not from string literals."""
    bad = []
    pats = [r'QLabel\(\s*f?"[A-Za-z]', r'QPushButton\(\s*f?"[A-Za-z]', r'\blabel\(\s*f?"[A-Za-z]',
            r'set(?:Text|ToolTip|WindowTitle|PlaceholderText)\(\s*f?"[A-Za-z]', r'addItem\(\s*"[A-Za-z]']
    for p in (ROOT / "app" / "ui").rglob("*.py"):
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if any(re.search(x, line) for x in pats):
                bad.append(f"{p.name}:{n}: {line.strip()}")
    assert not bad, "\n".join(bad)


# ---- behaviour of the translator ------------------------------------------------
class _W:
    def __init__(self):
        self.text = ""
        self.tip = ""

    def setText(self, t):
        self.text = t

    def setToolTip(self, t):
        self.tip = t


def _fresh():
    from app.i18n.translator import Translator
    return Translator()


def test_available_languages_and_default():
    t = _fresh()
    assert t.code == "en" and t.available()[0] == ("en", "English")   # engine fallback; the app default is Dari (see settings test)
    assert ("fa_AF", "دری (Dari)") in t.available()


def test_live_switch_updates_bound_widgets_without_restart():
    t, w = _fresh(), _W()
    t.bind(w, "nav.settings")
    t.bind(w, "settings.strict_tip", "setToolTip")
    assert w.text == "Settings"
    t.set_language("fa_AF")
    assert w.text == "تنظیمات" and "ی" in w.tip and t.is_rtl and t.direction() == Qt.RightToLeft
    t.set_language("en")
    assert w.text == "Settings" and not t.is_rtl and t.direction() == Qt.LeftToRight


def test_watchers_run_on_change_and_unknown_code_falls_back():
    t, calls = _fresh(), []
    t.watch(lambda: calls.append(t.code))
    t.set_language("fa_AF")
    assert t.set_language("xx") == "en"
    assert calls == ["en", "fa_AF", "en"]


def test_persian_digits_decimal_and_percent_in_dari_only():
    t = _fresh()
    assert t.tr("speed.result", wpm="32.5", acc="94.1") == "32.5 WPM  ·  94.1% accuracy"
    t.set_language("fa_AF")
    assert t.tr("speed.result", wpm="32.5", acc="94.1") == "۳۲٫۵ کلمه در دقیقه  ·  دقت ۹۴٫۱٪"
    assert t.tr("dashboard.goal_value", done="5", goal=10) == "۵ / ۱۰ دقیقه"
    assert t.tr("time.ms", m=3, s=7) == "۳ دقیقه و ۷ ثانیه"


def test_missing_key_falls_back_to_default_then_key():
    t = _fresh()
    t.set_language("fa_AF")
    assert t.tr("no.such.key") == "no.such.key" and t.tr("no.such.key", default="x") == "x"


def test_new_language_file_is_picked_up_automatically(tmp_path, monkeypatch=None):
    # a Pashto file dropped into the locales folder shows up in the language list
    path = LOCALES / "ps.json"
    path.write_text(json.dumps({"_meta": {"code": "ps", "native": "پښتو", "rtl": True, "digits": "persian",
                                          "qt_locale": "ps_AF", "fonts": ["Vazirmatn"], "font_size": 11},
                                "nav.settings": "امستنې"}, ensure_ascii=False), encoding="utf-8")
    try:
        t = _fresh()
        assert ("ps", "پښتو") in t.available()
        t.set_language("ps")
        assert t.tr("nav.settings") == "امستنې" and t.tr("nav.about") == "About"   # missing keys fall back to English
    finally:
        path.unlink()


def test_language_choice_persists_and_defaults_to_dari():
    from app.core.constants import DEFAULT_LANGUAGE, DEFAULT_SETTINGS
    from app.database.connection import Database
    from app.database.repositories import SettingsRepo
    from app.services.settings_service import SettingsService
    assert DEFAULT_LANGUAGE == "fa_AF" and DEFAULT_SETTINGS["ui_language"] == "fa_AF"
    db = Database(":memory:")
    assert SettingsService(SettingsRepo(db)).get("ui_language") == "fa_AF"    # nothing saved yet: Dari
    SettingsService(SettingsRepo(db)).set("ui_language", "en")
    assert SettingsService(SettingsRepo(db)).get("ui_language") == "en"       # an explicit English choice is kept after "restart"
