"""Perspective matrix (pure Python) that tilts the keyboard back, like viewing a desk.

Bottom edge stays put; the top edge shrinks by `strength`. Returned values are the
nine QTransform arguments (m11..m33, row-vector convention):
    X = m11*x + m21*y + m31,  Y = m12*x + m22*y + m32,  W = m13*x + m23*y + m33,  point = (X/W, Y/W)
"""


def perspective_matrix(w: float, h: float, strength: float = 0.12, tilt: float = 0.96):
    k = -strength / h
    cx = w / 2
    return (1.0, 0.0, 0.0,
            cx * k, tilt + h * k, k,
            -cx * k * h, h - tilt * h - h * h * k, 1.0 - k * h)


def project(m, x: float, y: float):
    X = m[0] * x + m[3] * y + m[6]
    Y = m[1] * x + m[4] * y + m[7]
    W = m[2] * x + m[5] * y + m[8]
    return X / W, Y / W
