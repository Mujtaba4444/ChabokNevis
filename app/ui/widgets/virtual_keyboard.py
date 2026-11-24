"""Pseudo-3D virtual keyboard: raised keycaps, perspective tilt, shaded hands."""
from __future__ import annotations

import math
import unicodedata

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QTransform
from PySide6.QtWidgets import QSizePolicy, QWidget

from ...i18n import tr, translator
from .. import theme
from .hand_pose import compute_pose
from .hand_shapes import finger_cmds, smooth_closed
from .perspective import perspective_matrix

SPACE = "space"
_HUES = {"L5": 0.93, "L4": 0.07, "L3": 0.14, "L2": 0.36, "R2": 0.50, "R3": 0.58, "R4": 0.70, "R5": 0.80}
_ROW_OFFSET = [0, 1.5, 1.75, 2.25]


def _label(ch: str) -> str:
    return "\u25cc" + ch if ch and unicodedata.combining(ch) else ch


class VirtualKeyboard(QWidget):
    def __init__(self, layout=None):
        super().__init__()
        self.setLayoutDirection(Qt.LeftToRight)   # a physical keyboard never mirrors
        translator.languageChanged.connect(lambda _c: self.update())
        self.layout_obj = layout
        self._target = None
        self._shift = False
        self._flash = None
        self._flash_ok = True
        self._ox = self._oy = 0.0
        self.setMinimumHeight(380)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def set_layout(self, layout):
        self.layout_obj = layout
        self.update()

    def set_target(self, key, shift=False):
        self._target, self._shift = key, shift
        self.update()

    def flash(self, key, ok):
        self._flash, self._flash_ok = key, ok
        self.update()
        QTimer.singleShot(200, self._clear_flash)

    def _clear_flash(self):
        self._flash = None
        self.update()

    def _fill(self, key, c):
        if key is self._flash:
            return QColor(c["success"] if self._flash_ok else c["error"])
        if key is self._target:
            return QColor(c["secondary"])
        dark = c["name"] == "dark"
        return QColor.fromHslF(_HUES.get(key.finger, 0.0), 0.35 if dark else 0.55, 0.30 if dark else 0.88)

    # ---- 3D keycap ------------------------------------------------------------
    def _cap(self, p, r, base, c, u, pressed=False, glow=False):
        """Draw a raised keycap; returns the top-face rect (for labels)."""
        dark = c["name"] == "dark"
        d = u * 0.14                      # key height
        rad = max(4.0, u * 0.12)
        p.setPen(Qt.NoPen)
        if glow:                          # soft halo around the target key
            for grow, alpha in ((7, 40), (4, 70)):
                g = QColor(c["secondary"]); g.setAlpha(alpha)
                p.setBrush(g)
                p.drawRoundedRect(r.adjusted(-grow, -grow, grow, grow + d), rad + 3, rad + 3)
        if not pressed:                   # cast shadow on the board
            p.setBrush(QColor(0, 0, 0, 95 if dark else 60))
            p.drawRoundedRect(r.translated(d * 0.6, d * 1.5), rad, rad)
        side = base.darker(165)
        p.setBrush(side)
        p.setPen(QPen(side.darker(130), 1))
        p.drawRoundedRect(r.translated(0, d), rad, rad)          # side wall
        top = r.translated(0, d * 0.85 if pressed else 0)
        grad = QLinearGradient(top.topLeft(), top.bottomLeft())
        grad.setColorAt(0.0, base.lighter(120))
        grad.setColorAt(1.0, base.darker(108))
        p.setBrush(grad)
        p.setPen(QPen(base.darker(140), 1))
        p.drawRoundedRect(top, rad, rad)                          # top face
        dish = top.adjusted(u * 0.09, u * 0.08, -u * 0.09, -u * 0.13)
        dg = QLinearGradient(dish.topLeft(), dish.bottomLeft())
        dg.setColorAt(0.0, QColor(0, 0, 0, 28))
        dg.setColorAt(1.0, QColor(255, 255, 255, 38))
        p.setPen(Qt.NoPen)
        p.setBrush(dg)
        p.drawRoundedRect(dish, rad * 0.7, rad * 0.7)             # concave dish
        p.setPen(QPen(QColor(255, 255, 255, 120 if not dark else 60), 1.3))
        p.drawLine(QPointF(top.left() + rad, top.top() + 1.5), QPointF(top.right() - rad, top.top() + 1.5))  # gloss
        return top

    def paintEvent(self, _):
        if not self.layout_obj:
            return
        c = theme.colors()
        dark = c["name"] == "dark"
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        w, h = self.width(), self.height()
        p.setTransform(QTransform(*perspective_matrix(w, h)))   # tilt back: far side smaller

        u = min(w / 15.6, h / 8.8)
        x0, y0 = (w - 15 * u) / 2, (h - 8.6 * u) / 2 + 0.2 * u
        gap = max(2.0, u * 0.06)

        def rect(x, row, wd=1.0):
            return QRectF(x0 + x * u + gap / 2, y0 + row * u + gap / 2, wd * u - gap, u - gap)

        # keyboard case
        case = QRectF(x0 - 0.35 * u, y0 - 0.3 * u, 15.7 * u, 5.65 * u)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 110 if dark else 70))
        p.drawRoundedRect(case.translated(0.1 * u, 0.4 * u), 0.5 * u, 0.5 * u)
        cg = QLinearGradient(case.topLeft(), case.bottomLeft())
        cg.setColorAt(0, QColor("#2A3556") if dark else QColor("#D5DBE7"))
        cg.setColorAt(1, QColor("#0B1020") if dark else QColor("#AEB8CC"))
        p.setBrush(cg)
        p.setPen(QPen(QColor(c["border"]), 1.5))
        p.drawRoundedRect(case, 0.5 * u, 0.5 * u)

        t = self._target
        has_key = t is not None and t is not SPACE
        shift_left = self._shift and has_key and t.finger.startswith("R")
        shift_right = self._shift and has_key and t.finger.startswith("L")
        neutral = QColor(c["key"])

        def special(x, row, wd, text, active=False):
            base = QColor(c["secondary"]) if active else neutral
            top = self._cap(p, rect(x, row, wd), base, c, u, glow=active)
            f = QFont(self.font()); f.setPixelSize(max(8, int(u * 0.22)))
            p.setFont(f)
            p.setPen(QColor("#06201C") if active else QColor(c["muted"]))
            p.drawText(top, Qt.AlignCenter, text)

        special(13, 0, 2, tr("kbd.back")); special(0, 1, 1.5, tr("kbd.tab")); special(0, 2, 1.75, tr("kbd.caps")); special(12.75, 2, 2.25, tr("kbd.enter"))
        special(0, 3, 2.25, tr("kbd.shift"), shift_left); special(12.25, 3, 2.75, tr("kbd.shift"), shift_right)
        special(3.5, 4, 6, tr("kbd.space"), t is SPACE)

        big, small = QFont(self.font()), QFont(self.font())
        big.setPixelSize(max(10, int(u * 0.42))); big.setBold(True)
        small.setPixelSize(max(7, int(u * 0.2)))
        for k in self.layout_obj.keys:
            r = rect(_ROW_OFFSET[k.row] + k.col, k.row)
            active = k is self._target or k is self._flash
            top = self._cap(p, r, self._fill(k, c), c, u, pressed=(k is self._flash), glow=(k is self._target))
            ink = QColor("#06201C") if active else QColor(c["text"])
            if k.base:
                p.setFont(big); p.setPen(ink)
                p.drawText(top, Qt.AlignCenter, _label(k.base))
            p.setFont(small); p.setPen(ink if active else QColor(c["muted"]))
            p.drawText(top.adjusted(5, 2, 0, 0), Qt.AlignLeft | Qt.AlignTop, k.latin.upper())
            if k.shift:
                p.drawText(top.adjusted(0, 2, -5, 0), Qt.AlignRight | Qt.AlignTop, _label(k.shift))
            if k.latin in ("f", "j"):  # home-row bumps
                p.setPen(QPen(QColor(c["muted"]), 2))
                p.drawLine(int(top.center().x() - u * 0.1), int(top.bottom() - 6), int(top.center().x() + u * 0.1), int(top.bottom() - 6))
        self._draw_hands(p, c, x0, y0, u)

    # ---- hands (organic bezier silhouettes, drawn on an offscreen layer) -----
    def _qpath(self, cmds, u):
        pt = lambda q: QPointF(self._ox + q[0] * u, self._oy + q[1] * u)
        path = QPainterPath()
        for c in cmds:
            if c[0] == "M":
                path.moveTo(pt(c[1]))
            elif c[0] == "C":
                path.cubicTo(pt(c[1]), pt(c[2]), pt(c[3]))
            else:
                path.closeSubpath()
        return path

    def _draw_hands(self, p, c, x0, y0, u):
        self._ox, self._oy = x0, y0
        t = self._target
        main_fid = main_xy = shift_fid = None
        if t is SPACE:
            main_fid, main_xy = "TR", (6.5, 4.5)
        elif t is not None:
            main_fid = t.finger
            main_xy = (_ROW_OFFSET[t.row] + t.col + 0.5, t.row + 0.5)
            if self._shift:
                shift_fid = "R5" if t.finger.startswith("L") else "L5"
        pose, palms = compute_pose(main_fid, main_xy, shift_fid)
        dark = c["name"] == "dark"
        w, h = self.width(), self.height()
        dpr = self.devicePixelRatioF()
        img = QImage(int(w * dpr) + 1, int(h * dpr) + 1, QImage.Format_ARGB32_Premultiplied)
        img.setDevicePixelRatio(dpr)
        img.fill(Qt.transparent)
        ip = QPainter(img)
        ip.setRenderHint(QPainter.Antialiasing)
        top_c, bot_c = ((176, 128, 126), (140, 96, 100)) if dark else ((190, 138, 118), (156, 108, 96))
        skin = QLinearGradient(0, y0 + 2.2 * u, 0, y0 + 8.6 * u)
        skin.setColorAt(0.0, QColor(*top_c))
        skin.setColorAt(1.0, QColor(*bot_c))
        ip.setPen(Qt.NoPen)
        ip.setBrush(skin)
        fingers = []
        for hand in ("L", "R"):
            ip.drawPath(self._qpath(smooth_closed(palms[hand]), u))          # palm
            for fid, (base, tip, wd) in pose[hand].items():
                fp = self._qpath(finger_cmds(fid, base, tip, wd), u)
                ip.drawPath(fp)
                fingers.append((fid, fp, base, tip))
        ip.setCompositionMode(QPainter.CompositionMode_SourceAtop)           # blue glow only on the active finger
        for fid, fp, base, tip in fingers:
            if fid == main_fid:
                glow = QLinearGradient(QPointF(x0 + tip[0] * u, y0 + tip[1] * u), QPointF(x0 + base[0] * u, y0 + base[1] * u))
                glow.setColorAt(0.0, QColor(46, 142, 230, 245))
                glow.setColorAt(0.65, QColor(46, 142, 230, 120))
                glow.setColorAt(1.0, QColor(46, 142, 230, 0))
                ip.setBrush(glow)
                ip.drawPath(fp)
        ip.setCompositionMode(QPainter.CompositionMode_DestinationIn)        # fade out toward the bottom edge
        fade = QLinearGradient(0, y0 + 5.8 * u, 0, y0 + 8.7 * u)
        fade.setColorAt(0.0, QColor(255, 255, 255, 255))
        fade.setColorAt(1.0, QColor(255, 255, 255, 0))
        ip.setBrush(fade)
        ip.drawRect(QRectF(0, 0, w + 1, h + 1))
        ip.setCompositionMode(QPainter.CompositionMode_SourceOver)
        for fid, fp, base, tip in fingers:                                   # Shift finger: dashed outline
            if fid == shift_fid:
                pen = QPen(QColor(46, 142, 230, 220), 2.2)
                pen.setStyle(Qt.DashLine)
                ip.setPen(pen)
                ip.setBrush(Qt.NoBrush)
                ip.drawPath(fp)
        ip.end()
        p.setOpacity(0.82)                                                   # translucent, keys show through
        p.drawImage(0, 0, img)
        p.setOpacity(1.0)
