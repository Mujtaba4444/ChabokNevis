"""Organic hand outlines as cubic-bezier commands (pure Python, key units).

Commands: ('M',(x,y)), ('C',(x1,y1),(x2,y2),(x,y)), ('Z',). Qt code turns them into
QPainterPath; tests/preview sample them into polygons."""
from __future__ import annotations

import math

# gentle sideways curve of each finger (units of finger width); mirrored for the right hand
_BEND = {"L5": -0.30, "L4": -0.10, "L3": 0.05, "L2": 0.25, "TL": 0.55}
_BEND.update({"R5": 0.30, "R4": 0.10, "R3": -0.05, "R2": -0.25, "TR": -0.55})


def _frame(fid, base, tip, w):
    thumb = fid in ("TL", "TR")
    dx, dy = tip[0] - base[0], tip[1] - base[1]
    L = math.hypot(dx, dy) or 1e-6
    d = (dx / L, dy / L)
    n = (-d[1], d[0])
    bend = _BEND.get(fid, 0.0) * w

    def P(s, t):  # local (along, across) -> world, with a slight curve
        t = t + bend * (s / L) ** 2
        return (base[0] + d[0] * s + n[0] * t, base[1] + d[1] * s + n[1] * t)

    hb, hm, r = (0.54 * w, 0.50 * w, 0.47 * w) if not thumb else (0.62 * w, 0.50 * w, 0.47 * w)
    return P, L, hb, hm, r


def finger_cmds(fid, base, tip, w):
    """Closed outline of one finger: flared base, slim waist, rounded fingertip."""
    P, L, hb, hm, r = _frame(fid, base, tip, w)
    k = 1.33 * r
    return [
        ("M", P(0, -hb)),
        ("C", P(0.30 * L, -hb * 0.97), P(0.62 * L, -hm * 1.03), P(L, -r)),
        ("C", P(L + k, -r), P(L + k, r), P(L, r)),
        ("C", P(0.62 * L, hm * 1.03), P(0.30 * L, hb * 0.97), P(0, hb)),
        ("Z",),
    ]


def finger_marks(fid, base, tip, w):
    """Realistic details for one finger: nail, gloss, knuckle creases, shading lines."""
    P, L, hb, hm, r = _frame(fid, base, tip, w)
    thumb = fid in ("TL", "TR")
    hn = 0.31 * w
    s0, s1 = L - 0.60 * w, L + 0.20 * w
    third = lambda a, b, t: a + (b - a) * t
    nail = [
        ("M", P(s0, -hn)),
        ("C", P(third(s0, s1 - hn, 1 / 3), -hn), P(third(s0, s1 - hn, 2 / 3), -hn), P(s1 - hn, -hn)),
        ("C", P(s1 - hn + 1.1 * hn, -hn), P(s1 - hn + 1.1 * hn, hn), P(s1 - hn, hn)),
        ("C", P(third(s1 - hn, s0, 1 / 3), hn), P(third(s1 - hn, s0, 2 / 3), hn), P(s0, hn)),
        ("C", P(s0 - 0.16 * w, hn * 0.55), P(s0 - 0.16 * w, -hn * 0.55), P(s0, -hn)),
        ("Z",),
    ]
    creases = []
    for f in ((0.52,) if thumb else (0.47, 0.77)):
        s_, c = f * L, 0.30 * w
        creases.append([("M", P(s_, -c)), ("C", P(s_ + 0.12 * w, -c * 0.4), P(s_ + 0.12 * w, c * 0.4), P(s_, c))])
        s2 = s_ + 0.09 * w * 2
        creases.append([("M", P(s2, -c * 0.6)), ("C", P(s2 + 0.07 * w, -c * 0.2), P(s2 + 0.07 * w, c * 0.2), P(s2, c * 0.6))])
    lines = {off: (P(0.10 * L, off * w), P(0.90 * L, off * w)) for off in (-0.36, -0.20, 0.20, 0.36)}
    gloss = (P(s0 + 0.22 * w, -hn * 0.45), P(s1 - 0.25 * w, -hn * 0.45))
    return {"nail": nail, "creases": creases, "lines": lines, "gloss": gloss}


def smooth_closed(points):
    """Catmull-Rom -> cubic bezier through `points` (closed, rounded blob)."""
    n = len(points)
    cmds = [("M", points[0])]
    for i in range(n):
        p0, p1, p2, p3 = points[i - 1], points[i], points[(i + 1) % n], points[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        cmds.append(("C", c1, c2, p2))
    cmds.append(("Z",))
    return cmds


def sample(cmds, steps=16):
    """Flatten commands to a polygon (for tests / previews)."""
    pts, cur = [], None
    for c in cmds:
        if c[0] == "M":
            cur = c[1]; pts.append(cur)
        elif c[0] == "C":
            p0, (p1, p2, p3) = cur, c[1:]
            for i in range(1, steps + 1):
                t = i / steps; u = 1 - t
                pts.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
            cur = p3
    return pts


def finger_point(fid, base, tip, w, f, across=0.0):
    """World point at fraction f (0 = knuckle, 1 = fingertip) along the finger centre line,
    `across` units sideways, following the same curve as finger_cmds."""
    dx, dy = tip[0] - base[0], tip[1] - base[1]
    L = math.hypot(dx, dy) or 1e-6
    d = (dx / L, dy / L)
    n = (-d[1], d[0])
    t = across + _BEND.get(fid, 0.0) * w * f * f
    return (base[0] + d[0] * L * f + n[0] * t, base[1] + d[1] * L * f + n[1] * t)
