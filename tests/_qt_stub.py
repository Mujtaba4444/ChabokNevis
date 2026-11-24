"""Minimal stand-in for PySide6.QtCore so the translation logic can be tested without Qt installed."""
import sys
import types


class _Bound:
    def __init__(self):
        self.slots = []

    def connect(self, fn):
        self.slots.append(fn)

    def emit(self, *a):
        for fn in list(self.slots):
            fn(*a)


class Signal:
    def __init__(self, *a):
        pass

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, inst, owner):
        return self if inst is None else inst.__dict__.setdefault("_sig_" + self.name, _Bound())


class QObject:
    def __init__(self, *a, **k):
        pass


class _Qt:
    RightToLeft, LeftToRight = "RTL", "LTR"


def install():
    try:
        import PySide6  # noqa: F401
        return False
    except ImportError:
        pkg = types.ModuleType("PySide6")
        core = types.ModuleType("PySide6.QtCore")
        core.QObject, core.Signal, core.Qt = QObject, Signal, _Qt
        pkg.QtCore = core
        sys.modules["PySide6"], sys.modules["PySide6.QtCore"] = pkg, core
        return True
