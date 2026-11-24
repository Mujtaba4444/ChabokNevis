"""Pure-Python hand geometry (key units, y grows downward). No Qt: unit-testable.

The keyboard is 15 key-units wide; the home row is y=2.5. Hands rest on the home
row; the active finger reaches its target key and the whole hand drifts a little
toward it, like a real hand."""
from __future__ import annotations

import math

_MX = 13.5  # mirror axis between the hands (x' = 13.5 - x)

# finger id -> (knuckle base, resting fingertip, max reach, finger width)   [left hand]
_LEFT = {
    "L5": ((2.60, 6.5), (2.25, 2.5), 5.7, 0.74),
    "L4": ((3.40, 6.3), (3.25, 2.5), 5.6, 0.86),
    "L3": ((4.35, 6.3), (4.25, 2.5), 5.9, 0.90),
    "L2": ((5.20, 6.2), (5.25, 2.5), 5.7, 0.90),
    "TL": ((4.45, 9.2), (5.95, 5.5), 5.0, 0.98),
}
# palm outline; runs past the bottom of the widget (clipped / faded when drawn)
PALM_LEFT = [(2.2, 6.4), (3.0, 5.8), (4.2, 5.8), (5.3, 5.85), (5.65, 6.3), (5.2, 7.0), (4.7, 8.0),
             (4.55, 9.4), (4.6, 10.8), (2.7, 10.8), (1.95, 8.9), (1.95, 7.4)]
_PALM = PALM_LEFT
_MIRROR_ID = {"L5": "R5", "L4": "R4", "L3": "R3", "L2": "R2", "TL": "TR"}


def _mir(pt):
    return (_MX - pt[0], pt[1])


_RIGHT = {_MIRROR_ID[f]: (_mir(b), _mir(t), r, w) for f, (b, t, r, w) in _LEFT.items()}
_PALM_R = [_mir(p) for p in _PALM]
SHIFT_CENTER = {"L5": (1.125, 3.5), "R5": (13.625, 3.5)}  # left / right Shift key centres


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _reach(base, target, reach):
    dx, dy = target[0] - base[0], target[1] - base[1]
    d = math.hypot(dx, dy)
    if d <= reach or d == 0:
        return target
    return (base[0] + dx / d * reach, base[1] + dy / d * reach)


def compute_pose(main_fid=None, main_target=None, shift_fid=None):
    """Return ({'L': {fid: (base, tip, width)}, 'R': {...}}, {'L': palm_pts, 'R': palm_pts}).
    main_fid: finger that presses the target (e.g. 'L2', 'TR'); main_target: key centre.
    shift_fid: pinky of the opposite hand that holds Shift (it reaches the Shift key)."""
    pose, palms = {}, {}
    shift_target = SHIFT_CENTER.get(shift_fid) if shift_fid else None
    for hand, table, palm in (("L", _LEFT, _PALM), ("R", _RIGHT, _PALM_R)):
        off = (0.0, 0.0)
        if main_fid in table and main_target:
            rx, ry = table[main_fid][1]
            off = (_clamp(0.35 * (main_target[0] - rx), -0.5, 0.5), _clamp(0.35 * (main_target[1] - ry), -0.9, 0.6))
        fingers = {}
        for fid, (b, t, reach, w) in table.items():
            base = (b[0] + off[0], b[1] + off[1])
            tip = (t[0] + off[0], t[1] + off[1])
            if fid == main_fid and main_target:
                tip = _reach(base, main_target, reach)
            elif fid == shift_fid and shift_target:
                tip = _reach(base, shift_target, reach)
            fingers[fid] = (base, tip, w)
        pose[hand] = fingers
        palms[hand] = [(x + off[0], y + off[1]) for x, y in palm]
    return pose, palms
