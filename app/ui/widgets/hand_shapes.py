"""Organic hand outlines as cubic-bezier commands (pure Python, key units).

Commands: ('M',(x,y)), ('C',(x1,y1),(x2,y2),(x,y)), ('Z',). Qt code turns them into
QPainterPath; tests/preview sample them into polygons."""
from __future__ import annotations

import math

# gentle sideways curve of each finger (units of finger width); mirrored for the right hand
_BEND = {"L5": -0.30, "L4": -0.10, "L3": 0.05, "L2": 0.25, "TL": 0.55}
_BEND.update({"R5": 0.30, "R4": 0.10, "R3": -0.05, "R2": -0.25, "TR": -0.55})


def finger_cmds(fid, base, tip, w):
    """Closed outline of one finger: flared base, slim waist, rounded fingertip."""
    thumb = fid in ("TL", "TR")
    dx, dy = tip[0] - base[0], tip[1] - base[1]
    L = math.hypot(dx, dy) or 1e-6
    d = (dx / L, dy / L)
    n = (-d[1], d[0])
    bend = _BEND.get(fid, 0.0) * w
    hb, hm, r = (0.54 * w, 0.50 * w, 0.47 * w) if not thumb else (0.62 * w, 0.50 * w, 0.47 * w)

    def P(s, t):  # local (along, across) -> world, with a slight curve
        t = t + bend * (s / L) ** 2
        return (base[0] + d[0] * s + n[0] * t, base[1] + d[1] * s + n[1] * t)

    k = 1.33 * r
    return [
        ("M", P(0, -hb)),
        ("C", P(0.30 * L, -hb * 0.97), P(0.62 * L, -hm * 1.03), P(L, -r)),
        ("C", P(L + k, -r), P(L + k, r), P(L, r)),
        ("C", P(0.62 * L, hm * 1.03), P(0.30 * L, hb * 0.97), P(0, hb)),
        ("Z",),
    ]


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
