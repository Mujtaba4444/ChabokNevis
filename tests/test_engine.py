import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.engine.statistics_engine import accuracy, wpm
from app.engine.text_normalizer import RELAXED, STRICT, normalize, chars_match
from app.engine.typing_engine import TypingEngine, CharState
from app.core.layouts import load_layouts


def test_normalizer():
    assert normalize("كتاب ي") == "کتاب ی"
    assert normalize("٣2۱") == "۳۲۱"
    assert chars_match("ی", "ي") and not chars_match("ی", "ي", STRICT)


def test_engine_flow_and_accuracy():
    e = TypingEngine("سلام")
    assert e.type_char("س") and e.type_char("ل") and e.type_char("ا")
    assert e.type_char("x") is False
    assert e.finished and e.correct_chars == 3
    r = e.result(60)
    assert r["total_characters"] == 4 and r["accuracy"] == 75.0
    assert e.type_char("م") is None


def test_backspace_and_states():
    e = TypingEngine("اب")
    e.type_char("x"); e.backspace()
    assert e.states() == [CharState.CURRENT, CharState.PENDING]
    e.type_char("ا"); e.type_char("ب")
    assert e.finished and e.correct_chars == 2 and e.incorrect_keystrokes == 1


def test_stats_formulas():
    assert wpm(50, 60) == 10.0 and accuracy(9, 10) == 90.0 and wpm(5, 0) == 0


def test_layout_mapping_and_locate():
    lay = load_layouts()["persian_windows"]
    assert lay.map_input("a") == "ش" and lay.map_input("f") == "ب" and lay.map_input(";") == "ک"
    assert lay.map_input("ش") == "ش" and lay.map_input(" ") == " " and lay.map_input(".") == "."
    key, shift = lay.locate("ب")
    assert key.latin == "f" and not shift and key.finger == "L2"
    assert lay.locate("؟")[1] is True
    assert lay.locate("ي")[0].latin == "d"  # Arabic yeh folds onto Persian yeh key
