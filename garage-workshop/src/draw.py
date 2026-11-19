# -*- coding: utf-8 -*-
"""Помощники для листов чертежей A3 (matplotlib -> PDF) и изометрии."""
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly, Circle, Rectangle
from geom import bulge_points

A3 = (420, 297)
LW_THICK = 1.0
LW_THIN = 0.45
LW_HAIR = 0.3
FS_DIM = 6.0
FS_TXT = 6.5
FS_LBL = 7.5
FS_TITLE = 10


def new_sheet(title, sheet_no, sheet_total, scale_txt='', material=''):
    fig = plt.figure(figsize=(A3[0] / 25.4, A3[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, A3[0]); ax.set_ylim(0, A3[1]); ax.set_aspect('equal'); ax.axis('off')
    # рамка
    ax.add_patch(Rectangle((20, 5), A3[0] - 25, A3[1] - 10, fill=False, lw=LW_THICK))
    # основная надпись (упрощённая) 185 x 40
    x0, y0, w, h = A3[0] - 5 - 185, 5, 185, 40
    ax.add_patch(Rectangle((x0, y0), w, h, fill=False, lw=LW_THICK))
    for yy in (y0 + 10, y0 + 20, y0 + 30):
        ax.plot([x0 + 120, x0 + w], [yy, yy], 'k-', lw=LW_THIN)
    ax.plot([x0 + 120, x0 + 120], [y0, y0 + h], 'k-', lw=LW_THICK)
    ax.plot([x0 + 150, x0 + 150], [y0, y0 + 20], 'k-', lw=LW_THIN)
    ax.text(x0 + 60, y0 + 30, 'Гараж 6×3 — мастерская', ha='center', va='center', fontsize=8)
    ax.text(x0 + 60, y0 + 17, title, ha='center', va='center', fontsize=FS_TITLE, weight='bold',
            wrap=True)
    ax.text(x0 + 60, y0 + 5, 'Верстак сдвоенный + стеновые панели', ha='center', va='center',
            fontsize=7, color='0.3')
    ax.text(x0 + 122, y0 + 35, 'Материал:', fontsize=6, va='center')
    ax.text(x0 + 140, y0 + 35, material, fontsize=6, va='center')
    ax.text(x0 + 122, y0 + 25, 'Масштаб:', fontsize=6, va='center')
    ax.text(x0 + 140, y0 + 25, scale_txt, fontsize=7, va='center')
    ax.text(x0 + 122, y0 + 15, 'Лист', fontsize=6, va='center')
    ax.text(x0 + 135, y0 + 15, '%d' % sheet_no, fontsize=8, va='center', weight='bold')
    ax.text(x0 + 152, y0 + 15, 'Листов  %d' % sheet_total, fontsize=7, va='center')
    ax.text(x0 + 122, y0 + 5, 'Размеры в мм. Неуказ. допуски ±1', fontsize=5.5, va='center')
    fig._title_block = (x0, y0, w, h)
    return fig, ax


class View:
    """Вид: модельные мм -> мм листа: X = ox + s*x, Y = oy + s*y."""

    def __init__(self, ax, ox, oy, scale):
        self.ax, self.ox, self.oy, self.s = ax, ox, oy, scale

    def P(self, x, y):
        return self.ox + self.s * x, self.oy + self.s * y

    def line(self, x1, y1, x2, y2, lw=LW_THICK, ls='-', color='k', z=2):
        a, b = self.P(x1, y1), self.P(x2, y2)
        self.ax.plot([a[0], b[0]], [a[1], b[1]], ls=ls, lw=lw, color=color, zorder=z,
                     solid_capstyle='butt', dash_capstyle='butt')

    def hidden(self, x1, y1, x2, y2):
        self.line(x1, y1, x2, y2, lw=LW_THIN, ls=(0, (4, 2)), color='0.25')

    def axis(self, x1, y1, x2, y2):
        self.line(x1, y1, x2, y2, lw=LW_HAIR, ls=(0, (10, 2, 2, 2)), color='0.35')

    def polyline(self, pts, closed=True, lw=LW_THICK, color='k', fill=None, ls='-', z=2,
                 hatch=None, alpha=1.0):
        P = [self.P(x, y) for x, y in pts]
        patch = MplPoly(P, closed=closed, fill=fill is not None, fc=fill if fill else 'none',
                        ec=color, lw=lw, ls=ls, zorder=z, hatch=hatch, alpha=alpha)
        self.ax.add_patch(patch)

    def rect(self, x, y, w, h, **kw):
        self.polyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], **kw)

    def circle(self, cx, cy, r, lw=LW_THIN, color='k', fill=None, z=3):
        X, Y = self.P(cx, cy)
        self.ax.add_patch(Circle((X, Y), r * self.s, fill=fill is not None,
                                 fc=fill if fill else 'none', ec=color, lw=lw, zorder=z))

    def contour(self, verts, lw=LW_THICK, color='k', fill=None, z=2):
        self.polyline(bulge_points(verts), lw=lw, color=color, fill=fill, z=z)

    def text(self, x, y, s, size=FS_TXT, ha='center', va='center', rot=0, color='k',
             weight='normal', z=5, bg=False):
        X, Y = self.P(x, y)
        kw = {}
        if bg:
            kw['bbox'] = dict(fc='white', ec='none', pad=0.3)
        self.ax.text(X, Y, s, fontsize=size, ha=ha, va=va, rotation=rot, color=color,
                     weight=weight, zorder=z, **kw)

    def _arrow(self, X, Y, dx, dy, L=2.2, W=0.6):
        n = math.hypot(dx, dy)
        dx, dy = dx / n, dy / n
        px, py = -dy, dx
        pts = [(X, Y), (X - dx * L + px * W, Y - dy * L + py * W),
               (X - dx * L - px * W, Y - dy * L - py * W)]
        self.ax.add_patch(MplPoly(pts, closed=True, fc='k', ec='k', lw=0.2, zorder=4))

    def dimx(self, x1, x2, y, y1=None, y2=None, text=None, tdx=0, above=True, fs=FS_DIM):
        """Горизонтальный размер; линия на модельной высоте y."""
        A = self.P(x1, y); B = self.P(x2, y)
        for xx, yy in ((x1, y1), (x2, y2)):
            if yy is not None:
                P0 = self.P(xx, yy); P1 = self.P(xx, y)
                sg = 1 if P1[1] >= P0[1] else -1
                self.ax.plot([P0[0], P0[0]], [P0[1] + sg * 0.8, P1[1] + sg * 1.5], 'k-',
                             lw=LW_HAIR, zorder=3)
        self.ax.plot([A[0], B[0]], [A[1], A[1]], 'k-', lw=LW_HAIR, zorder=3)
        L = abs(B[0] - A[0])
        if L > 7:
            self._arrow(A[0], A[1], -1 if B[0] > A[0] else 1, 0)
            self._arrow(B[0], B[1], 1 if B[0] > A[0] else -1, 0)
        else:
            sg = 1 if B[0] > A[0] else -1
            self._arrow(A[0], A[1], sg, 0); self._arrow(B[0], B[1], -sg, 0)
            self.ax.plot([min(A[0], B[0]) - 4, max(A[0], B[0]) + 4], [A[1], A[1]], 'k-',
                         lw=LW_HAIR, zorder=3)
        if text is None:
            text = fmt(abs(x2 - x1))
        tx = (A[0] + B[0]) / 2 + tdx
        self.ax.text(tx, A[1] + (0.6 if above else -0.6), text, fontsize=fs, ha='center',
                     va='bottom' if above else 'top', zorder=5)

    def dimy(self, y1, y2, x, x1=None, x2=None, text=None, tdy=0, left=True, fs=FS_DIM):
        A = self.P(x, y1); B = self.P(x, y2)
        for xx, yy in ((x1, y1), (x2, y2)):
            if xx is not None:
                P0 = self.P(xx, yy); P1 = self.P(x, yy)
                sg = 1 if P1[0] >= P0[0] else -1
                self.ax.plot([P0[0] + sg * 0.8, P1[0] + sg * 1.5], [P0[1], P0[1]], 'k-',
                             lw=LW_HAIR, zorder=3)
        self.ax.plot([A[0], A[0]], [A[1], B[1]], 'k-', lw=LW_HAIR, zorder=3)
        L = abs(B[1] - A[1])
        sg = 1 if B[1] > A[1] else -1
        if L > 7:
            self._arrow(A[0], A[1], 0, -sg); self._arrow(B[0], B[1], 0, sg)
        else:
            self._arrow(A[0], A[1], 0, sg); self._arrow(B[0], B[1], 0, -sg)
            self.ax.plot([A[0], A[0]], [min(A[1], B[1]) - 4, max(A[1], B[1]) + 4], 'k-',
                         lw=LW_HAIR, zorder=3)
        if text is None:
            text = fmt(abs(y2 - y1))
        ty = (A[1] + B[1]) / 2 + tdy
        self.ax.text(A[0] + (-0.7 if left else 0.7), ty, text, fontsize=fs,
                     ha='center', va='bottom' if left else 'top', rotation=90, zorder=5)

    def leader(self, x, y, tx, ty, s, size=FS_LBL, ha='left', ball=False, weight='normal'):
        """Выноска: точка модели (x,y) -> текст в смещении (tx,ty) мм листа."""
        X, Y = self.P(x, y)
        TX, TY = X + tx, Y + ty
        self.ax.plot([X, TX], [Y, TY], 'k-', lw=LW_HAIR, zorder=4)
        self.ax.add_patch(Circle((X, Y), 0.45, fc='k', ec='k', zorder=4))
        if ball:
            self.ax.add_patch(Circle((TX, TY), 3.2, fc='white', ec='k', lw=LW_THIN, zorder=5))
            self.ax.text(TX, TY, s, fontsize=6.5, ha='center', va='center', zorder=6,
                         weight='bold')
        else:
            self.ax.plot([TX, TX + (len(s) * 1.45 if ha == 'left' else -len(s) * 1.45)],
                         [TY, TY], 'k-', lw=LW_HAIR, zorder=4)
            self.ax.text(TX + (0.5 if ha == 'left' else -0.5), TY + 0.5, s, fontsize=size,
                         ha=ha, va='bottom', zorder=5, weight=weight)


def fmt(v):
    if abs(v - round(v)) < 0.05:
        return '%d' % round(v)
    return ('%.1f' % v).replace('.', ',')


def label(ax, x, y, s, size=FS_LBL, weight='bold', ha='left', va='center', color='k'):
    ax.text(x, y, s, fontsize=size, weight=weight, ha=ha, va=va, color=color, zorder=6)


def notes(ax, x, y, lines, size=FS_TXT, dy=3.6, width=None):
    for i, s in enumerate(lines):
        ax.text(x, y - i * dy, s, fontsize=size, ha='left', va='top', zorder=6)


def table(ax, x, y, cols, rows, widths, rh=4.6, fs=5.8, header_fs=6.0):
    """Таблица: (x,y) — левый верхний угол."""
    W = sum(widths)
    n = len(rows) + 1
    ax.add_patch(Rectangle((x, y - n * rh), W, n * rh, fill=False, lw=LW_THICK, zorder=4))
    ax.add_patch(Rectangle((x, y - rh), W, rh, fc='0.9', ec='k', lw=LW_THIN, zorder=3))
    cx = x
    for w in widths[:-1]:
        cx += w
        ax.plot([cx, cx], [y, y - n * rh], 'k-', lw=LW_THIN, zorder=4)
    for i in range(1, n):
        ax.plot([x, x + W], [y - i * rh, y - i * rh], 'k-', lw=LW_HAIR, zorder=4)
    for j, (c, w) in enumerate(zip(cols, widths)):
        cx = x + sum(widths[:j])
        ax.text(cx + 1, y - rh / 2, c, fontsize=header_fs, va='center', ha='left', weight='bold',
                zorder=5)
    for i, r in enumerate(rows):
        for j, (c, w) in enumerate(zip(r, widths)):
            cx = x + sum(widths[:j])
            ax.text(cx + 1, y - (i + 1.5) * rh, str(c), fontsize=fs, va='center', ha='left',
                    zorder=5)
    return y - n * rh


# ----------------------------------------------------------------------------
# Простая изометрия (painter's algorithm, отсечение задних граней)
# ----------------------------------------------------------------------------
class Iso:
    """Камера по направлению e (от сцены к наблюдателю), ось Z — вверх."""

    def __init__(self, e=(-0.55, -1.0, 0.7)):
        n = math.sqrt(sum(c * c for c in e))
        self.e = tuple(c / n for c in e)
        f = tuple(-c for c in self.e)
        up = (0, 0, 1)
        r = (f[1] * up[2] - f[2] * up[1], f[2] * up[0] - f[0] * up[2], f[0] * up[1] - f[1] * up[0])
        rn = math.sqrt(sum(c * c for c in r))
        self.r = tuple(c / rn for c in r)
        u = (self.r[1] * f[2] - self.r[2] * f[1], self.r[2] * f[0] - self.r[0] * f[2],
             self.r[0] * f[1] - self.r[1] * f[0])
        self.u = u
        self.faces = []

    def proj(self, p):
        d = lambda a, b: a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
        return d(p, self.r), d(p, self.u), d(p, self.e)

    def box(self, x0, y0, z0, dx, dy, dz, color, ec='k', lw=0.2, alpha=1.0, prio=2, dots=None):
        x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
        V = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        F = [((0, 1, 5, 4), (0, -1, 0)), ((1, 2, 6, 5), (1, 0, 0)), ((2, 3, 7, 6), (0, 1, 0)),
             ((3, 0, 4, 7), (-1, 0, 0)), ((4, 5, 6, 7), (0, 0, 1)), ((3, 2, 1, 0), (0, 0, -1))]
        c = self.proj(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))[2]
        for k, (idx, n) in enumerate(F):
            dd = dots.get(k) if isinstance(dots, dict) else None
            self.face([V[i] for i in idx], n, color, ec, lw, alpha, prio=prio, gkey=c, dots=dd)

    def face(self, pts, n, color, ec='k', lw=0.2, alpha=1.0, prio=2, gkey=None, dots=None,
             force=False):
        self.faces.append(dict(pts=pts, n=n, color=color, ec=ec, lw=lw, alpha=alpha, prio=prio,
                               gkey=gkey, dots=dots, force=force))

    def render(self, ax, ox, oy, s, z0=2):
        items = []
        for f in self.faces:
            n = f['n']
            if not f['force'] and (n[0] * self.e[0] + n[1] * self.e[1] + n[2] * self.e[2]) <= 1e-9:
                continue
            P = [self.proj(p) for p in f['pts']]
            d = sum(p[2] for p in P) / len(P)
            g = f['gkey'] if f['gkey'] is not None else d
            items.append(((f['prio'], g, d), P, f))
        items.sort(key=lambda t: t[0])
        L = (0.35, -0.55, 0.75)
        Ln = math.sqrt(sum(c * c for c in L))
        for k, (key, P, f) in enumerate(items):
            zo = z0 + k * 1e-4
            n = f['n']
            nn = math.sqrt(sum(c * c for c in n)) or 1
            sh = 0.62 + 0.38 * max(0, sum(n[i] * L[i] for i in range(3)) / (nn * Ln))
            rgb = matplotlib.colors.to_rgb(f['color'])
            fc = tuple(min(1, c * sh) for c in rgb)
            XY = [(ox + s * p[0], oy + s * p[1]) for p in P]
            ax.add_patch(MplPoly(XY, closed=True, fc=fc, ec=f['ec'], lw=f['lw'],
                                 alpha=f['alpha'], zorder=zo))
            if f['dots']:
                xs, ys = [], []
                for q in f['dots']:
                    X, Y, _ = self.proj(q)
                    xs.append(ox + s * X); ys.append(oy + s * Y)
                ax.scatter(xs, ys, s=0.05, c='0.3', marker='o', linewidths=0, zorder=zo + 5e-5)

    def extent(self):
        xs, ys = [], []
        for f in self.faces:
            for p in f['pts']:
                X, Y, _ = self.proj(p)
                xs.append(X); ys.append(Y)
        return min(xs), min(ys), max(xs), max(ys)
