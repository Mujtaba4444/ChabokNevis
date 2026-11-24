"""Single source of truth for speed / accuracy maths."""


def accuracy(correct: int, total: int) -> float:
    """Accuracy = correct keystrokes / total keystrokes x 100."""
    return 0.0 if total <= 0 else correct / total * 100.0


def wpm(correct_chars: int, seconds: float) -> float:
    """WPM = correct characters / 5 / minutes (a 'word' is 5 characters)."""
    return 0.0 if seconds <= 0 else correct_chars / 5.0 / (seconds / 60.0)
