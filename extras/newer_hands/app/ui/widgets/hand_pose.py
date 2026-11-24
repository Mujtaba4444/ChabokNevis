"""Pure-Python hand geometry (key units, y grows downward). No Qt: unit-testable.

Touch-typing model: both hands stay anchored on the home row (ASDF / JKL;).
Only the finger that must press a key reaches out from its knuckle, then returns.
The palm may sway a tiny amount for naturalness, never travel."""
from __future__ import annotations

import math

_MX = 13.5  # mirror axis between the hands (x' = 13.5 - x)

# finger id -> (knuckle base, resting fingertip on the home row, max reach, finger width)   [left hand]
_LEFT = {
    "L5": ((2.55, 4.95), (2.25, 2.5), 5.0, 0.74),
    "L4": ((3.40, 4.70), (3.25, 2.5), 5.3, 0.86),
    "L3": ((4.30, 4.60), (4.25, 2.5), 5.6, 0.90),
    "L2": ((5.15, 4.70), (5.25, 2.5), 5.4, 0.90),
    "TL": ((4.40, 8.40), (5.70, 5.3), 5.0, 0.98),
}
# big palm that starts high (overlaps the bottom key row) and runs past the widget bottom
PALM_LEFT = [(2.05, 5.3), (2.35, 4.6), (3.1, 4.4), (4.2, 4.4), (5.2, 4.5), (5.65, 5.0), (5.2, 6.0),
             (4.75, 7.2), (4.6, 9.0), (4.6, 10.8), (2.8, 10.8), (2.0, 8.8), (1.85, 6.8)]
_PALM = PALM_LEFT
_MIRROR_ID = {"L5": "R5", "L4": "R4", "L3": "R3", "L2": "R2", "TL": "TR"}
SWAY, SWAY_MAX = 0.12, 0.35            # tiny palm sway toward the target (units)
HOME_KEYS = ("a", "s", "d", "f", "j", "k", "l", ";")


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
    main_fid presses main_target (key centre); shift_fid (opposite pinky) holds Shift."""
    pose, palms = {}, {}
    shift_target = SHIFT_CENTER.get(shift_fid) if shift_fid else None
    for hand, table, palm in (("L", _LEFT, _PALM), ("R", _RIGHT, _PALM_R)):
        off = (0.0, 0.0)
        if main_fid in table and main_target:
            rx, ry = table[main_fid][1]
            off = (_clamp(SWAY * (main_target[0] - rx), -SWAY_MAX, SWAY_MAX),
                   _clamp(SWAY * (main_target[1] - ry), -SWAY_MAX, SWAY_MAX))
        fingers = {}
        for fid, (b, t, reach, w) in table.items():
            base = (b[0] + off[0], b[1] + off[1])
            tip = (t[0] + off[0], t[1] + off[1])
            target = main_target if fid == main_fid else (shift_target if fid == shift_fid else None)
            if target:
                tip = _reach(base, target, reach)
                ext = math.dist(base, tip) / max(math.dist(base, t), 1e-6)
                w = w * (1 + 0.06 * _clamp(1.0 - ext, 0.0, 1.0) - 0.04 * _clamp(ext - 1.0, 0.0, 1.0))   # curled = a touch fuller, extended = a touch slimmer
            fingers[fid] = (base, tip, w)
        pose[hand] = fingers
        palms[hand] = [(x + off[0], y + off[1]) for x, y in palm]
    return pose, palms


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def blend_pose(a, b, t):
    """Interpolate two (pose, palms) results for smooth finger movement (t in 0..1)."""
    pa, la = a
    pb, lb = b
    pose = {h: {f: (_lerp(pa[h][f][0], pb[h][f][0], t), _lerp(pa[h][f][1], pb[h][f][1], t),
                    pa[h][f][2] + (pb[h][f][2] - pa[h][f][2]) * t) for f in pb[h]} for h in pb}
    palms = {h: [_lerp(p, q, t) for p, q in zip(la[h], lb[h])] for h in lb}
    return pose, palms
