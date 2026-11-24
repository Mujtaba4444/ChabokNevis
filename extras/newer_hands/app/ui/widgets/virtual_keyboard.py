"""Pseudo-3D virtual keyboard: raised keycaps, perspective tilt, shaded hands."""
from __future__ import annotations

import math
import unicodedata

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, Qt, QTimer, QVariantAnimation
from PySide6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient, QTransform
from PySide6.QtWidgets import QSizePolicy, QWidget

from ...i18n import tr, translator
from .. import theme
from .hand_pose import HOME_KEYS, blend_pose, compute_pose
from .hand_shapes import finger_cmds, finger_point, smooth_closed
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
        self._pose_args = (None, None, None)
        self._pose_to = compute_pose()
        self._pose_from = None
        self._k = 1.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(130)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._on_anim)
        self.setMinimumHeight(380)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def set_layout(self, layout):
        self.layout_obj = layout
        self.update()

    def _compute_args(self):
        t = self._target
        if t is SPACE:
            return ("TR", (6.5, 4.5), None)
        if t is None:
            return (None, None, None)
        sf = ("R5" if t.finger.startswith("L") else "L5") if self._shift else None
        return (t.finger, (_ROW_OFFSET[t.row] + t.col + 0.5, t.row + 0.5), sf)

    def _pose_now(self):
        if self._pose_from is None or self._k >= 1.0:
            return self._pose_to
        return blend_pose(self._pose_from, self._pose_to, self._k)

    def _on_anim(self, v):
        self._k = float(v)
        self.update()

    def set_target(self, key, shift=False):
        self._target, self._shift = key, shift
        args = self._compute_args()
        if args != self._pose_args:          # only the reaching finger moves; animate it smoothly
            self._pose_from = self._pose_now()
            self._pose_args = args
            self._pose_to = compute_pose(*args)
            self._k = 0.0
            self._anim.stop()
            self._anim.start()
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
            if k.latin in HOME_KEYS:   # the 8 anchor keys get a small marker
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(c["secondary"]))
                p.drawEllipse(QPointF(top.center().x(), top.top() + u * 0.15), u * 0.055, u * 0.055)
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

    def _layer(self):
        dpr = self.devicePixelRatioF()
        img = QImage(int(self.width() * dpr) + 1, int(self.height() * dpr) + 1, QImage.Format_ARGB32_Premultiplied)
        img.setDevicePixelRatio(dpr)
        img.fill(Qt.transparent)
        q = QPainter(img)
        q.setRenderHint(QPainter.Antialiasing)
        return img, q

    def _fade(self, q, y0, u):
        q.setCompositionMode(QPainter.CompositionMode_DestinationIn)   # fade out toward the bottom edge
        fade = QLinearGradient(0, y0 + 5.8 * u, 0, y0 + 8.7 * u)
        fade.setColorAt(0.0, QColor(255, 255, 255, 255))
        fade.setColorAt(1.0, QColor(255, 255, 255, 0))
        q.setPen(Qt.NoPen)
        q.setBrush(fade)
        q.drawRect(QRectF(0, 0, self.width() + 1, self.height() + 1))
        q.setCompositionMode(QPainter.CompositionMode_SourceOver)

    def _draw_hands(self, p, c, x0, y0, u):
        self._ox, self._oy = x0, y0
        main_fid, _xy, shift_fid = self._pose_args          # animated pose: only the reaching finger moves
        pose, palms = self._pose_now()
        PX = lambda q: QPointF(x0 + q[0] * u, y0 + q[1] * u)
        hands = []   # (palm_path, union_path, [finger info])
        for hand in ("L", "R"):
            palm = self._qpath(smooth_closed(palms[hand]), u)
            union, fingers = QPainterPath(palm), []
            for fid, (base, tip, wd) in pose[hand].items():
                fp = self._qpath(finger_cmds(fid, base, tip, wd), u)
                union = union.united(fp)
                fingers.append((fid, fp, base, tip, wd))
            hands.append((palm, union, fingers, palms[hand]))

        # soft shadow the hands cast on the keys
        sh, sp = self._layer()
        sp.translate(0.14 * u, 0.38 * u)
        sp.setPen(Qt.NoPen)
        sp.setBrush(QColor(0, 0, 0, 255))
        for _pa, union, _f, _pp in hands:
            sp.drawPath(union)
        sp.resetTransform()
        self._fade(sp, y0, u)
        sp.end()
        p.setOpacity(0.30)
        p.drawImage(0, 0, sh)

        img, ip = self._layer()
        skin = QLinearGradient(0, y0 + 2.2 * u, 0, y0 + 8.6 * u)       # natural skin tone
        skin.setColorAt(0.0, QColor(228, 180, 152))
        skin.setColorAt(1.0, QColor(190, 138, 112))
        ip.setPen(Qt.NoPen)
        ip.setBrush(skin)
        for palm, union, fingers, _pts in hands:
            ip.drawPath(union)
        ip.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        for palm, union, fingers, pts in hands:
            cx = sum(q[0] for q in pts) / len(pts); cy = sum(q[1] for q in pts) / len(pts)
            rg = QRadialGradient(PX((cx, cy - 0.4)), 3.0 * u)           # rounded back of the hand
            rg.setColorAt(0.0, QColor(255, 236, 216, 70))
            rg.setColorAt(1.0, QColor(120, 70, 50, 0))
            ip.setBrush(rg)
            ip.drawPath(palm)
            for fid, fp, base, tip, wd in fingers:
                a, b = PX(base), PX(tip)
                L = math.hypot(b.x() - a.x(), b.y() - a.y()) or 1.0
                nx, ny = -(b.y() - a.y()) / L, (b.x() - a.x()) / L
                mid = QPointF((a.x() + b.x()) / 2, (a.y() + b.y()) / 2)
                wpx = wd * u
                g = QLinearGradient(mid.x() - nx * wpx * 0.55, mid.y() - ny * wpx * 0.55, mid.x() + nx * wpx * 0.55, mid.y() + ny * wpx * 0.55)
                g.setColorAt(0.00, QColor(110, 62, 46, 135))     # shaded edge
                g.setColorAt(0.28, QColor(255, 244, 232, 0))
                g.setColorAt(0.40, QColor(255, 246, 236, 80))    # highlight
                g.setColorAt(0.72, QColor(0, 0, 0, 0))
                g.setColorAt(1.00, QColor(110, 62, 46, 150))
                ip.setBrush(g)
                ip.drawPath(fp)
                kg = QRadialGradient(a, wpx * 0.75)              # knuckle bump
                kg.setColorAt(0.0, QColor(255, 240, 224, 85))
                kg.setColorAt(1.0, QColor(255, 240, 224, 0))
                ip.setBrush(kg)
                ip.drawEllipse(a, wpx * 0.75, wpx * 0.75)
                if fid == main_fid:                              # blue glow on the finger to use
                    glow = QLinearGradient(b, a)
                    glow.setColorAt(0.0, QColor(46, 142, 230, 215))
                    glow.setColorAt(0.65, QColor(46, 142, 230, 100))
                    glow.setColorAt(1.0, QColor(46, 142, 230, 0))
                    ip.setBrush(glow)
                    ip.drawPath(fp)
        ip.setCompositionMode(QPainter.CompositionMode_SourceOver)

        for palm, union, fingers, pts in hands:
            cxp = sum(q[0] for q in pts) / len(pts)
            for fid, fp, base, tip, wd in fingers:
                wpx = wd * u
                thumb = fid in ("TL", "TR")
                if not thumb:                                    # tendons on the back of the hand
                    ip.setPen(QPen(QColor(120, 72, 56, 42), 1.4))
                    ip.drawLine(PX((base[0], base[1] + 0.25)), PX((base[0] + (cxp - base[0]) * 0.18, base[1] + 2.1)))
                crease = QPen(QColor(112, 66, 52, 125), 1.2)     # knuckle wrinkles
                ip.setPen(crease)
                ip.setBrush(Qt.NoBrush)
                for f, half, double in ((0.36 if not thumb else 0.5, 0.30, True), (0.68 if not thumb else 0.0, 0.24, False)):
                    if f <= 0:
                        continue
                    for k in ((-0.035, 0.0) if double else (0.0,)):
                        l = PX(finger_point(fid, base, tip, wd, f + k, -half * wd))
                        r = PX(finger_point(fid, base, tip, wd, f + k, half * wd))
                        cpt = PX(finger_point(fid, base, tip, wd, f + k + 0.03, 0.0))
                        path = QPainterPath(l)
                        path.quadTo(cpt, r)
                        ip.drawPath(path)
                # fingernail
                end = finger_point(fid, base, tip, wd, 1.0)
                prev = finger_point(fid, base, tip, wd, 0.93)
                e, pv = PX(end), PX(prev)
                ang = math.degrees(math.atan2(e.y() - pv.y(), e.x() - pv.x()))
                ip.save()
                ip.translate(e)
                ip.rotate(ang)
                nail = QRectF(-0.34 * wpx, -0.27 * wpx, 0.64 * wpx, 0.54 * wpx)
                ng = QLinearGradient(0, nail.top(), 0, nail.bottom())
                ng.setColorAt(0.0, QColor(255, 234, 228, 235))
                ng.setColorAt(1.0, QColor(238, 188, 178, 235))
                ip.setBrush(ng)
                ip.setPen(QPen(QColor(150, 94, 84, 170), 1.0))
                ip.drawRoundedRect(nail, 0.2 * wpx, 0.2 * wpx)
                ip.setPen(Qt.NoPen)
                ip.setBrush(QColor(255, 255, 255, 120))          # lunula (pale half-moon at the nail base)
                ip.drawEllipse(QPointF(nail.left() + 0.07 * wpx, 0), 0.09 * wpx, 0.2 * wpx)
                ip.setPen(QPen(QColor(255, 255, 255, 170), 1.3))  # gloss
                ip.drawLine(QPointF(nail.left() + 0.2 * wpx, nail.top() + 0.1 * wpx), QPointF(nail.right() - 0.14 * wpx, nail.top() + 0.1 * wpx))
                ip.restore()
            ip.setBrush(Qt.NoBrush)                              # skin edge
            ip.setPen(QPen(QColor(120, 74, 58, 130), 1.5))
            ip.drawPath(union)
            for fid, fp, base, tip, wd in fingers:
                if fid == shift_fid:                             # Shift finger: dashed outline
                    pen = QPen(QColor(46, 142, 230, 230), 2.4)
                    pen.setStyle(Qt.DashLine)
                    ip.setPen(pen)
                    ip.drawPath(fp)
        self._fade(ip, y0, u)
        ip.end()
        p.setOpacity(0.9)
        p.drawImage(0, 0, img)
        p.setOpacity(1.0)
