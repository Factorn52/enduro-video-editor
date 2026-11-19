# -*- coding: utf-8 -*-
"""
Параметрическая геометрия: верстак из двух модулей (А — слив/мойка, Б — рабочий)
и стеновые панели из фанеры. Все размеры — мм.

Изменили размер — запустите build.py, все DXF/PDF пересчитаются.
"""
import math
from dataclasses import dataclass, field

# ----------------------------------------------------------------------------
# ОБЩИЕ ПАРАМЕТРЫ
# ----------------------------------------------------------------------------
GARAGE_L = 6000          # длина гаража (внутр.)
GARAGE_W = 3000          # ширина гаража (внутр.) — по этой стене стоит верстак

MOD_W = 1400             # ширина одного модуля
MOD_D = 700              # глубина верстака
N_MOD = 2                # модуль А (слив) + модуль Б (рабочий)
BENCH_X0 = (GARAGE_W - N_MOD * MOD_W) / 2   # зазор до боковой стены = 100

FOOT_H = 25              # регулируемая опора М12 (номинал, ±10)
PLATE_T = 4              # пластина-подпятник
LEG_L = 834              # длина ноги
FRAME_TOP = FOOT_H + PLATE_T + LEG_L        # верх каркаса = 863
TUBE = 40                # профиль 40х40х2
TUBE_T = 2
LOW_H, LOW_W = 40, 20    # нижние перемычки 40х20х2 (40 — вертикально)
LOW_Z0 = 80              # низ нижних перемычек от пола
LOW_Z1 = LOW_Z0 + LOW_H  # верх = 120
LEG_HOLES = (250, 650)   # отв. ø9 под стяжку модулей, от низа ноги
CROSS_XC = (467, 933)    # оси поперечин столешницы модуля Б

PLY_T = 18               # фанера берёзовая 18 мм
TOP_PLY = 2 * PLY_T      # основа столешницы — 2 слоя 18 = 36
CAP_T = 1.5
TOP_Z = FRAME_TOP + TOP_PLY + CAP_T         # 900.5 — рабочая высота

KF = 0.42                # K-фактор для гибки нержавейки/стали

def bend_allow(ri, t, k=KF):
    return math.pi / 2 * (ri + k * t)

# ----------------------------------------------------------------------------
# ПОДДОН (Л2) — AISI 304, 1.5 мм, дно с уклоном к сливу (зад-лево)
# ----------------------------------------------------------------------------
TR_T, TR_RI = 1.5, 1.5
TR_GAP = 3                                    # зазор стенка-перемычка
TR_LX = MOD_W - 2 * TUBE - 2 * TR_GAP         # 1314 — наружн. размер по стенкам
TR_LY = MOD_D - 2 * TUBE - 2 * TR_GAP         # 614
TR_X0 = TUBE + TR_GAP                         # 43 — положение стенки в каркасе
TR_H0, TR_A, TR_B = 80, 12, 8                 # мин. глубина, перепад по X и по Y
TR_F = 42                                     # отбортовка (полка) наружу
TR_TAB_H, TR_TAB_L = 10, 120                  # упоры решётки
TR_TABS_X = (350 - TR_X0, 1050 - TR_X0)       # центры упоров на перед./задн. полке
TR_TABS_Y = (350 - TR_X0,)                    # центры упоров на боковых полках
DR_OFF, DR_D = 45, 18                         # слив: от внутр. стенок, ø отв.

def tray_h(x, y):
    """Наружная высота поддона (от низа дна до верха полки) в точке x,y
    (координаты от наружных граней стенок, x — вправо, y — от фронта к стене)."""
    return TR_H0 + TR_A * (TR_LX - x) / TR_LX + TR_B * y / TR_LY

# ----------------------------------------------------------------------------
# РЕШЁТКА (Л3) — AISI 304, 3 мм, 4 шт.
# ----------------------------------------------------------------------------
GR_T, GR_RI = 3.0, 3.0
GR_N = 4
GR_GAP = 1.0
GR_X0 = 1 + TR_T + 1                           # 3.5: упор (1..2.5) + зазор 1
GR_W = (MOD_W - 2 * GR_X0 - (GR_N - 1) * GR_GAP) / GR_N   # 347.5
GR_D = MOD_D - 2 * GR_X0                       # 693
GR_H = TOP_Z - (FRAME_TOP + TR_T)              # 36 — высота борта решётки
GR_MARGIN = 55                                  # поле без перфорации

# ----------------------------------------------------------------------------
# КРЫШКА (Л1) — AISI 430, 1.5 мм; полка нижняя (Л4) — Ст 1.5 мм
# ----------------------------------------------------------------------------
CAP_W, CAP_D = MOD_W, MOD_D
CAP_H = TOP_PLY + CAP_T                         # 37.5 — юбка закрывает фанеру
CAP_RI = 1.5
TOPBOARD_W, TOPBOARD_D = MOD_W - 2 * CAP_T - 1, MOD_D - 2 * CAP_T - 1  # 1396 x 696

SH_T, SH_RI = 1.5, 1.5
SH_W, SH_D = MOD_W - 4, MOD_D - 4               # 1396 x 696
SH_LIP = 20
SH_NOTCH = 40

# ----------------------------------------------------------------------------
# СТЕНОВЫЕ ПАНЕЛИ (фанера 18)
# ----------------------------------------------------------------------------
PLY_SHEET = 1525
PN_W, PN_H = 1400, 1200
PN_N = 3
PN_Z0 = 960                                     # низ панели от пола
PN_PITCH, PN_HOLE, PN_MARGIN = 50, 8, 50
PN_MOUNT_X = (75, 525, 875, 1325)
PN_MOUNT_Y = (75, 625, 1125)
PN_MOUNT_D = 5
BT_L, BT_W = 1380, 70                           # рейка-отступ
BT_YC = PN_MOUNT_Y                              # оси реек = ряды крепежа
BT_ANCHOR_X = (100, 690, 1280)
BT_ANCHOR_D = 6

# ----------------------------------------------------------------------------
# СТРУКТУРЫ ДАННЫХ
# ----------------------------------------------------------------------------
@dataclass
class FlatPart:
    code: str
    name: str
    material: str
    t: float
    qty: int
    outer: list                     # [(x, y, bulge)] замкнутый контур
    holes: list = field(default_factory=list)     # контуры [(x,y,b)]
    circles: list = field(default_factory=list)   # (cx, cy, r) — рез/сверловка
    drills: list = field(default_factory=list)    # (cx, cy, r) — сверлить (фанера)
    bends: list = field(default_factory=list)     # (x1,y1,x2,y2,label)
    note: str = ''
    kind: str = 'metal'             # metal | ply

    def bbox(self):
        pts = bulge_points(self.outer)
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)

    def size(self):
        x0, y0, x1, y1 = self.bbox()
        return x1 - x0, y1 - y0

    def normalized(self):
        """Сдвиг в (0,0) левого нижнего угла габарита."""
        x0, y0, _, _ = self.bbox()
        return self.moved(-x0, -y0)

    def moved(self, dx, dy, rot90=False):
        def tp(x, y):
            if rot90:
                x, y = -y, x
            return x + dx, y + dy
        def tv(lst):
            return [(*tp(x, y), b) for x, y, b in lst]
        def tc(c):
            return (*tp(c[0], c[1]), c[2])
        def tb(b):
            return (*tp(b[0], b[1]), *tp(b[2], b[3]), b[4])
        return FlatPart(self.code, self.name, self.material, self.t, self.qty,
                        tv(self.outer), [tv(h) for h in self.holes],
                        [tc(c) for c in self.circles], [tc(c) for c in self.drills],
                        [tb(b) for b in self.bends], self.note, self.kind)

    def rotated(self):
        """Поворот на 90° CCW с нормализацией."""
        return self.moved(0, 0, rot90=True).normalized()


def bulge_points(verts, seg_deg=8.0):
    """Контур с bulge -> список точек (дуги аппроксимируются)."""
    pts = []
    n = len(verts)
    for i in range(n):
        x1, y1, b = verts[i]
        x2, y2, _ = verts[(i + 1) % n]
        pts.append((x1, y1))
        if abs(b) > 1e-9:
            theta = 4 * math.atan(b)
            ch = math.hypot(x2 - x1, y2 - y1)
            if ch < 1e-9:
                continue
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = (x2 - x1) / ch, (y2 - y1) / ch
            lnx, lny = -dy, dx
            k = ch * (1 - b * b) / (4 * b)
            cx, cy = mx + lnx * k, my + lny * k
            a1 = math.atan2(y1 - cy, x1 - cx)
            r = math.hypot(x1 - cx, y1 - cy)
            nseg = max(2, int(abs(math.degrees(theta)) / seg_deg))
            for j in range(1, nseg):
                a = a1 + theta * j / nseg
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def poly(pts):
    return [(x, y, 0.0) for x, y in pts]


def dedupe(pts, eps=1e-6):
    out = []
    for p in pts:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > eps:
            out.append(p)
    if len(out) > 1 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) < eps:
        out.pop()
    return out


def rect_r(w, h, r):
    """Прямоугольник со скруглёнными углами (bulge) от (0,0)."""
    if r <= 0:
        return poly([(0, 0), (w, 0), (w, h), (0, h)])
    b = math.tan(math.radians(90) / 4)
    return [(r, 0, 0), (w - r, 0, b), (w, r, 0), (w, h - r, b),
            (w - r, h, 0), (r, h, b), (0, h - r, 0), (0, r, b)]


def slot(cx, cy, w, L, along='y'):
    """Паз (обраунд) шириной w, общей длиной L."""
    c = L / 2 - w / 2
    if along == 'y':
        return [(cx + w / 2, cy - c, 0), (cx + w / 2, cy + c, 1.0),
                (cx - w / 2, cy + c, 0), (cx - w / 2, cy - c, 1.0)]
    return [(cx - c, cy - w / 2, 0), (cx + c, cy - w / 2, 1.0),
            (cx + c, cy + w / 2, 0), (cx - c, cy + w / 2, 1.0)]


# ----------------------------------------------------------------------------
# РАЗВЁРТКИ ЛИСТОВЫХ ДЕТАЛЕЙ
# ----------------------------------------------------------------------------
def tray_flat():
    """Поддон: дно-плоскость с уклоном к углу (зад-лево), стенки-трапеции,
    горизонтальная полка наружу по верху и упоры решётки.
    Развёртка — вид с внутренней (рабочей) стороны."""
    t, Ri = TR_T, TR_RI
    BA = bend_allow(Ri, t)
    SB = Ri + t
    Lx, Ly = TR_LX, TR_LY
    Bx, By = Lx - 2 * SB, Ly - 2 * SB
    F = TR_F
    relief_w, relief_x = 2.0, 0.5

    walls = {
        'front': dict(Lw=Lx, h0=tray_h(0, 0), h1=tray_h(Lx, 0), e0=0.0, e1=Lx, tabs=TR_TABS_X),
        'right': dict(Lw=Ly, h0=tray_h(Lx, 0), h1=tray_h(Lx, Ly), e0=t, e1=Ly - t, tabs=TR_TABS_Y),
        'rear':  dict(Lw=Lx, h0=tray_h(0, Ly), h1=tray_h(Lx, Ly), e0=0.0, e1=Lx, tabs=TR_TABS_X),
        'left':  dict(Lw=Ly, h0=tray_h(0, 0), h1=tray_h(0, Ly), e0=t, e1=Ly - t, tabs=TR_TABS_Y),
    }

    def arm(w):
        Lw, h0, h1, e0, e1 = w['Lw'], w['h0'], w['h1'], w['e0'], w['e1']
        m = -(h1 - h0) / Lw            # наклон нижней кромки стенки
        q = math.sqrt(1 + m * m)

        def loc(xi, zeta):              # точка стенки -> локальная развёртка
            s = (xi + m * zeta) / q
            n = (-m * xi + zeta) / q
            return (s - SB, BA + (n - SB))

        def zeta_n(xi, n):
            return n * q + m * xi
        zt = h0 - SB                     # касательная верхнего гиба
        nrm = (m / q, 1 / q)

        def fp(xi, off):
            px, py = loc(xi, zt)
            return (px + off * nrm[0], py + off * nrm[1])

        def off_d(d):
            return BA + (d - Ri)
        o_edge = off_d(F)
        o_b3 = off_d(F - SB)
        o_tip = o_b3 + BA + (TR_TAB_H - SB)
        pts = [(0, 0), (0, BA), loc(e0, zeta_n(e0, SB)), loc(e0, zt),
               fp(e0, BA), fp(-Ri, off_d(Ri)), fp(-F, o_edge)]
        bends = [((0, BA / 2), (Lw - 2 * SB, BA / 2), 'Б1'),
                 (fp(e0, BA / 2), fp(e1, BA / 2), 'Б2')]
        for tc in sorted(w['tabs']):
            x0, x1 = tc - TR_TAB_L / 2, tc + TR_TAB_L / 2
            pts += [fp(x0 - relief_w, o_edge), fp(x0 - relief_w, o_b3 - relief_x),
                    fp(x0, o_b3 - relief_x), fp(x0, o_tip), fp(x1, o_tip),
                    fp(x1, o_b3 - relief_x), fp(x1 + relief_w, o_b3 - relief_x),
                    fp(x1 + relief_w, o_edge)]
            bends.append((fp(x0, o_b3 + BA / 2), fp(x1, o_b3 + BA / 2), 'Б3'))
        pts += [fp(Lw + F, o_edge), fp(Lw + Ri, off_d(Ri)), fp(e1, BA),
                loc(e1, zt), loc(e1, zeta_n(e1, SB)), (Lw - 2 * SB, BA), (Lw - 2 * SB, 0)]
        return pts, bends

    maps = {
        'front': lambda p: (p[0], -p[1]),
        'right': lambda p: (Bx + p[1], p[0]),
        'rear':  lambda p: (p[0], By + p[1]),
        'left':  lambda p: (-p[1], p[0]),
    }
    outline = []
    bends = []
    for name, rev in (('front', False), ('right', False), ('rear', True), ('left', True)):
        pts, bl = arm(walls[name])
        g = [maps[name](p) for p in pts]
        if rev:
            g = g[::-1]
        outline += g
        for p1, p2, lab in bl:
            a, b = maps[name](p1), maps[name](p2)
            bends.append((a[0], a[1], b[0], b[1], lab))
    outline = dedupe(outline)
    drain = (DR_OFF + t - SB, (Ly - t - DR_OFF) - SB, DR_D / 2)
    part = FlatPart('Л2', 'Поддон сливной', 'AISI 304 (08Х18Н10)', t, 1,
                    poly(outline), circles=[drain], bends=bends,
                    note='Б1 — на себя 90°, Б2 — от себя 90°, Б3 — на себя 90°; Rвн=1.5')
    part.walls = walls
    part.BA = BA
    return part


def box_flat(code, name, mat, t, qty, W, D, H, Ri, closed=True, notch=None,
             skirt_holes=None, relief_r=0.0):
    """Короб/крышка: основание W x D (наружн.), 4 борта высотой H (наружн.).
    closed=True — перед/зад во всю длину, боковые до них (углы закрыты).
    notch=(nx, ny) — вырезы под стойки (для полки), борта между вырезами.
    skirt_holes: dict side-> [(pos_along, depth_from_top)] отверстия в бортах."""
    BA = bend_allow(Ri, t)
    SB = Ri + t
    Bx, By = W - 2 * SB, D - 2 * SB
    S = H - SB
    E = BA + S
    outline = []
    bends = []
    holes = []

    if notch:
        n = notch - SB
        pts = [(n, -E), (Bx - n, -E), (Bx - n, n), (Bx + E, n), (Bx + E, By - n),
               (Bx - n, By - n), (Bx - n, By + E), (n, By + E), (n, By - n),
               (-E, By - n), (-E, n), (n, n)]
        outline = poly(pts)
        bends = [(n, -BA / 2, Bx - n, -BA / 2, 'Б'), (Bx + BA / 2, n, Bx + BA / 2, By - n, 'Б'),
                 (n, By + BA / 2, Bx - n, By + BA / 2, 'Б'), (-BA / 2, n, -BA / 2, By - n, 'Б')]
    elif closed:
        e_full = -SB          # перед/зад: от наружной грани
        e_side = -(SB - t)    # бока: до внутренней грани переднего борта
        pts = []
        # перед (y<0), слева направо
        pts += [(0, 0), (0, -BA), (e_full, -BA), (e_full, -E), (Bx - e_full, -E),
                (Bx - e_full, -BA), (Bx, -BA), (Bx, 0)]
        # право (x>Bx), снизу вверх
        pts += [(Bx + BA, 0), (Bx + BA, e_side), (Bx + E, e_side), (Bx + E, By - e_side),
                (Bx + BA, By - e_side), (Bx + BA, By), (Bx, By)]
        # зад (y>By), справа налево
        pts += [(Bx, By + BA), (Bx - e_full, By + BA), (Bx - e_full, By + E),
                (e_full, By + E), (e_full, By + BA), (0, By + BA), (0, By)]
        # лево (x<0), сверху вниз
        pts += [(-BA, By), (-BA, By - e_side), (-E, By - e_side), (-E, e_side),
                (-BA, e_side), (-BA, 0)]
        outline = poly(dedupe(pts))
        bends = [(0, -BA / 2, Bx, -BA / 2, 'Б'), (Bx + BA / 2, 0, Bx + BA / 2, By, 'Б'),
                 (0, By + BA / 2, Bx, By + BA / 2, 'Б'), (-BA / 2, 0, -BA / 2, By, 'Б')]
    else:
        # открытые углы + круглая разгрузка в углах
        r = relief_r
        bb = -math.tan(math.radians(270) / 4)
        pts = [(0, -E, 0), (Bx, -E, 0), (Bx, -r, bb), (Bx + r, 0, 0), (Bx + E, 0, 0),
               (Bx + E, By, 0), (Bx + r, By, bb), (Bx, By + r, 0), (Bx, By + E, 0),
               (0, By + E, 0), (0, By + r, bb), (-r, By, 0), (-E, By, 0), (-E, 0, 0),
               (-r, 0, bb), (0, -r, 0)]
        outline = pts
        bends = [(0, -BA / 2, Bx, -BA / 2, 'Б'), (Bx + BA / 2, 0, Bx + BA / 2, By, 'Б'),
                 (0, By + BA / 2, Bx, By + BA / 2, 'Б'), (-BA / 2, 0, -BA / 2, By, 'Б')]

    circles = []
    if skirt_holes:
        for side, lst in skirt_holes.items():
            for pos, dtop, dia in lst:
                off = BA + (dtop - SB)      # от кромки основания по развёртке
                if side == 'front':
                    circles.append((pos - SB, -off, dia / 2))
                elif side == 'rear':
                    circles.append((pos - SB, By + off, dia / 2))
                elif side == 'left':
                    circles.append((-off, pos - SB, dia / 2))
                elif side == 'right':
                    circles.append((Bx + off, pos - SB, dia / 2))
    p = FlatPart(code, name, mat, t, qty, outline, circles=circles, bends=bends)
    p.BA, p.SB, p.Bx, p.By = BA, SB, Bx, By
    return p


def grate_flat():
    p = box_flat('Л3', 'Решётка съёмная', 'AISI 304 (08Х18Н10)', GR_T, GR_N,
                 GR_W, GR_D, GR_H, GR_RI, closed=False, relief_r=2.0)
    SB = p.SB
    # перфорация: пазы 6х40 вдоль Y, шахматный порядок
    x0, x1 = GR_MARGIN, GR_W - GR_MARGIN
    hy = 72                                    # оси ручек от торцов
    y0, y1 = 100, GR_D - 100
    w, L, px, py = 6.0, 40.0, 18.0, 55.0
    nc = int((x1 - x0 - w) // px) + 1
    span_x = (nc - 1) * px
    cx0 = (x0 + x1) / 2 - span_x / 2
    nr = int((y1 - y0 - L) // py) + 1
    span_y = (nr - 1) * py
    cy0 = (y0 + y1) / 2 - span_y / 2
    holes = []
    for i in range(nc):
        cx = cx0 + i * px
        if i % 2 == 0:
            ys = [cy0 + j * py for j in range(nr)]
        else:
            ys = [cy0 + py / 2 + j * py for j in range(nr - 1)]
        for cy in ys:
            holes.append(slot(cx - SB, cy - SB, w, L, 'y'))
    # ручки-прорези 70х22
    for cy in (hy, GR_D - hy):
        holes.append(slot(GR_W / 2 - SB, cy - SB, 22, 70, 'x'))
    p.holes = holes
    p.perf = dict(n=len(holes) - 2, w=w, L=L, px=px, py=py, nc=nc, nr=nr,
                  cx0=cx0, cy0=cy0, hy=hy)
    p.note = 'Все гибы — от себя 90° (борта вниз), Rвн=3'
    return p


def cap_flat():
    holes = {
        'front': [(x, 11, 4.5) for x in (200, 700, 1200)],
        'rear':  [(x, 11, 4.5) for x in (200, 700, 1200)],
        'left':  [(y, 11, 4.5) for y in (200, 500)],
        'right': [(y, 11, 4.5) for y in (200, 500)],
    }
    p = box_flat('Л1', 'Крышка столешницы', 'AISI 430 шлиф.', CAP_T, 1,
                 CAP_W, CAP_D, CAP_H, CAP_RI, closed=True, skirt_holes=holes)
    p.note = 'Все гибы — от себя 90° (юбка вниз), Rвн=1.5'
    return p


def shelf_flat():
    p = box_flat('Л4', 'Полка нижняя (модуль А)', 'Ст 08пс/Ст3', SH_T, 1,
                 SH_W, SH_D, SH_LIP, SH_RI, notch=SH_NOTCH)
    p.note = 'Все гибы — на себя 90° (борт вверх), Rвн=1.5'
    return p


def foot_plate():
    o = rect_r(40, 40, 2)
    return FlatPart('Л5', 'Подпятник ноги', 'Ст3', PLATE_T, 2 * 4, o,
                    circles=[(20, 20, 6.5)], note='Приварить гайку М12 сверху соосно')


def gusset():
    pts = [(0, 12), (12, 0), (100, 0), (100, 6), (6, 100), (0, 100)]
    return FlatPart('Л6', 'Косынка', 'Ст3', 4, 2, poly(pts),
                    note='Модуль Б: перед. ноги + верх. перемычка')


def vise_plate():
    return FlatPart('Л7', 'Пластина под тиски', 'Ст3', 6, 1, rect_r(200, 200, 10),
                    note='Отв. под тиски сверлить по месту')


# ----------------------------------------------------------------------------
# ФАНЕРА
# ----------------------------------------------------------------------------
def panel():
    o = poly([(0, 0), (PN_W, 0), (PN_W, PN_H), (0, PN_H)])
    drills = []
    nx = int((PN_W - 2 * PN_MARGIN) // PN_PITCH) + 1
    ny = int((PN_H - 2 * PN_MARGIN) // PN_PITCH) + 1
    for i in range(nx):
        for j in range(ny):
            drills.append((PN_MARGIN + i * PN_PITCH, PN_MARGIN + j * PN_PITCH, PN_HOLE / 2))
    for x in PN_MOUNT_X:
        for y in PN_MOUNT_Y:
            drills.append((x, y, PN_MOUNT_D / 2))
    p = FlatPart('П1', 'Панель стеновая', 'Фанера берёзовая ФК 18', PLY_T, PN_N, o,
                 drills=drills, kind='ply')
    p.grid = (nx, ny)
    return p


def batten():
    o = poly([(0, 0), (BT_L, 0), (BT_L, BT_W), (0, BT_W)])
    d = [(x, BT_W / 2, BT_ANCHOR_D / 2) for x in BT_ANCHOR_X]
    return FlatPart('Р1', 'Рейка-отступ', 'Фанера берёзовая ФК 18', PLY_T, 3 * PN_N, o,
                    drills=d, kind='ply')


def topboard():
    o = poly([(0, 0), (TOPBOARD_W, 0), (TOPBOARD_W, TOPBOARD_D), (0, TOPBOARD_D)])
    return FlatPart('Щ1', 'Основа столешницы (2 слоя)', 'Фанера берёзовая ФК 18',
                    PLY_T, 2, o, kind='ply')


def acc_parts():
    """Навесные держатели из обрезков фанеры. Задняя планка с 4 шкантами ø8
    (шаг 50 по сетке панели)."""
    parts = []
    M = 'Фанера берёзовая ФК 18'

    def back(code, L):
        o = poly([(0, 0), (L, 0), (L, 90), (0, 90)])
        xs = (75, 225) if L == 300 else (50, 350)
        d = [(x, y, 4) for x in xs for y in (15, 65)]
        return FlatPart(code, 'Задняя планка', M, PLY_T, 1, o, drills=d, kind='ply')

    def gus(code, h, w):
        return FlatPart(code, 'Косынка', M, PLY_T, 2, poly([(0, 0), (w, 0), (0, h)]), kind='ply')
    # А1 — отвёрточница
    parts.append(back('А1.1', 300))
    sh = FlatPart('А1.2', 'Полка с отв.', M, PLY_T, 1, poly([(0, 0), (300, 0), (300, 80), (0, 80)]),
                  drills=[(30 + 30 * i, 30, 6) for i in range(9)], kind='ply')
    parts.append(sh)
    parts.append(gus('А1.3', 70, 60))
    # А2 — ключница (пазы открыты к краю y=70)
    parts.append(back('А2.1', 400))
    pts = [(0, 0, 0), (400, 0, 0), (400, 70, 0)]
    pitch, n, sw, sd = 33, 11, 8, 45
    xs = [400 / 2 - (n - 1) * pitch / 2 + i * pitch for i in range(n)]
    for x in reversed(xs):
        pts += [(x + sw / 2, 70, 0), (x + sw / 2, 70 - sd + sw / 2, -1.0),
                (x - sw / 2, 70 - sd + sw / 2, 0), (x - sw / 2, 70, 0)]
    pts += [(0, 70, 0)]
    parts.append(FlatPart('А2.2', 'Полка с пазами', M, PLY_T, 1, pts, kind='ply'))
    parts.append(gus('А2.3', 70, 55))
    # А3 — полка для масел/баллонов
    parts.append(back('А3.1', 400))
    parts.append(FlatPart('А3.2', 'Полка', M, PLY_T, 1,
                          poly([(0, 0), (400, 0), (400, 90), (0, 90)]), kind='ply'))
    parts.append(FlatPart('А3.3', 'Бортик', M, PLY_T, 1,
                          poly([(0, 0), (400, 0), (400, 40), (0, 40)]), kind='ply'))
    parts.append(gus('А3.4', 70, 75))
    return parts


# ----------------------------------------------------------------------------
# ТРУБЫ (каркас)
# ----------------------------------------------------------------------------
@dataclass
class Tube:
    code: str
    name: str
    profile: str
    L: float
    qty: int
    note: str = ''
    mods: str = ''


def tubes():
    W_in = MOD_W - 2 * TUBE
    D_in = MOD_D - 2 * TUBE
    return [
        Tube('Т1', 'Нога', '40х40х2', LEG_L, 4 * N_MOD,
             '2 отв. ø9 насквозь (по оси X) на 250 и 650 от низа', 'А, Б'),
        Tube('Т2', 'Перемычка верхняя продольная', '40х40х2', W_in, 2 * N_MOD,
             'Мод. Б: 3 отв. ø5 сверху + ø10 снизу (крепление фанеры)', 'А, Б'),
        Tube('Т3', 'Перемычка верхняя боковая', '40х40х2', D_in, 2 * N_MOD,
             'Мод. Б: 1 отв. ø5/ø10 по центру', 'А, Б'),
        Tube('Т4', 'Поперечина столешницы', '40х40х2', D_in, 2,
             '2 отв. ø5/ø10 (на 150 и 470)', 'Б'),
        Tube('Т5', 'Перемычка нижняя продольная', '40х20х2', W_in, 3,
             'А — перед. и задн., Б — только задн.', 'А, Б'),
        Tube('Т6', 'Перемычка нижняя боковая', '40х20х2', D_in, 2 * N_MOD, '', 'А, Б'),
    ]


def cut_sticks(pieces, stock=6000, kerf=3):
    """Раскрой хлыстов: first-fit decreasing. pieces: [(code, L)]."""
    items = sorted(pieces, key=lambda p: -p[1])
    sticks = []
    for code, L in items:
        for s in sticks:
            used = sum(l for _, l in s) + kerf * len(s)
            if used + L + kerf <= stock:
                s.append((code, L))
                break
        else:
            sticks.append([(code, L)])
    return sticks


if __name__ == '__main__':
    from shapely.geometry import Polygon
    for f in (tray_flat, grate_flat, cap_flat, shelf_flat, foot_plate, gusset, vise_plate,
              panel, batten, topboard):
        p = f()
        poly_ = Polygon(bulge_points(p.outer))
        print(p.code, p.name, 'size=%.1f x %.1f' % p.size(), 'valid=', poly_.is_valid,
              'area=%.0f' % poly_.area, 'holes=', len(p.holes), 'circ=', len(p.circles),
              'drills=', len(p.drills))
    for p in acc_parts():
        poly_ = Polygon(bulge_points(p.outer))
        print(p.code, p.name, 'size=%.1f x %.1f' % p.size(), 'valid=', poly_.is_valid)
    print('TOP_Z', TOP_Z, 'FRAME_TOP', FRAME_TOP, 'GR_W', GR_W, 'GR_D', GR_D, 'GR_H', GR_H)
    t = tray_flat()
    for k, w in t.walls.items():
        print(k, 'h0=%.1f h1=%.1f' % (w['h0'], w['h1']))
