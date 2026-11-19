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
FOOT_BASE_D = 32         # пята опоры (на стыке модулей оси ног через 40 мм!)
PLATE_T = 4              # пластина-подпятник
LEG_L = 902              # длина ноги (рост 187 → столешница 950)
FRAME_TOP = FOOT_H + PLATE_T + LEG_L        # верх каркаса = 931
TUBE = 40                # профиль 40х40х2
TUBE_T = 2
LOW_H, LOW_W = 40, 20    # нижние перемычки 40х20х2 (40 — вертикально)
LOW_Z0 = 80              # низ нижних перемычек от пола
LOW_Z1 = LOW_Z0 + LOW_H  # верх = 120
LEG_HOLES = (250, 650)   # отв. ø9 под стяжку модулей, от низа ноги (сверлить в сборе)
CROSS_XC = (450, 750, 1055)  # оси 3 поперечин модуля Б (450 — край плиты Л7)

PLY_T = 18               # фанера берёзовая 18 мм
TOP_PLY = PLY_T          # основа столешницы — 1 слой 18
CAP_T = 1.5
TOP_Z = FRAME_TOP + TOP_PLY + CAP_T         # 950.5 — рабочая высота

# Плита Л7 (20 мм) — под тиски + площадка для правки. Утоплена вровень со столешницей,
# лежит прямо на каркасе в ЛЕВОМ переднем углу модуля Б — над стянутыми ногами
# стыка модулей (самое жёсткое место, далеко от боковой стены).
PL_T = 20
PL_X0, PL_W, PL_D = 0, 450, 300            # x от левого края модуля Б
PL_GAP = 2                                  # зазор до фанеры и крышки (конусность реза 20 мм)
# потай М10 сквозь трубы с распорными втулками; не ближе 30 мм к косынке Л6 (x 40..140)
PL_BOLTS = ((170, 20), (430, 20), (20, 130), (20, 250))   # коорд. плиты (= модуля Б)
VISE_XC = 310                               # ось тисков на плите (зона правки — слева, над ногами)
ANVIL_X = (0, 190)                          # зона правки по X
CORNER_GAP = 0.3                            # зазор в закрытых углах коробов под TIG
T7_YC = PL_D                               # ось перемычки Т7 под задним краем плиты
T7_X0 = TUBE                                # от левой боковой Т3 до поперечины Т4-1
T7_L = CROSS_XC[0] - TUBE / 2 - T7_X0       # 390
SEAM_X = CROSS_XC[1]                        # стык двух кусков фанеры — на средней поперечине
GUSSET = 100                                # косынка Л6 (катет)

KF = 0.42                # K-фактор для гибки нержавейки/стали

def bend_allow(ri, t, k=KF):
    return math.pi / 2 * (ri + k * t)

# ----------------------------------------------------------------------------
# ПОДДОН (Л2) — AISI 304, 1.5 мм, дно с уклоном ~2 % к сливу (перёд-лево)
# ----------------------------------------------------------------------------
TR_T, TR_RI = 1.5, 1.5
TR_GAP = 4                                    # зазор стенка-перемычка (место под швы рамы)
TR_LX = MOD_W - 2 * TUBE - 2 * TR_GAP         # 1314 — наружн. размер по стенкам
TR_LY = MOD_D - 2 * TUBE - 2 * TR_GAP         # 614
TR_X0 = TUBE + TR_GAP                         # 43 — положение стенки в каркасе
TR_H0, TR_A, TR_B = 80, 25, 16                # мин. глубина, перепад по X (1,9 %) и по Y (2,6 %)
TR_F = TR_X0 - 1                              # 43 — отбортовка (полка) наружу, кромка в 1 мм от края
TR_TAB_H, TR_TAB_L = 10, 120                  # упоры решётки
TR_TABS_X = (350 - TR_X0, 1050 - TR_X0)       # центры упоров на перед./задн. полке
TR_TABS_Y = (350 - TR_X0,)                    # центры упоров на боковых полках
DR_OFF, DR_D = 40, 28                         # слив: ось от внутр. стенок; ø отв. = наружн. ø полумуфты
DR_MAX_LEVEL = 40                             # макс. уровень жидкости у слива (риска), мм

def tray_h(x, y):
    """Наружная высота поддона (от низа дна до верха полки) в точке x,y
    (координаты от наружных граней стенок, x — вправо, y — от фронта к стене).
    Самая глубокая точка — перёд-лево (слив)."""
    return TR_H0 + TR_A * (TR_LX - x) / TR_LX + TR_B * (TR_LY - y) / TR_LY


def drain_xy():
    """Центр слива в координатах поддона (от наружных граней стенок)."""
    return TR_T + DR_OFF, TR_T + DR_OFF


def drain_frame_xy():
    x, y = drain_xy()
    return TR_X0 + x, TR_X0 + y


def tray_volume(level):
    """Объём жидкости (л) при уровне level мм над самой низкой точкой дна."""
    n = 120
    hmax = max(tray_h(0, 0), tray_h(0, TR_LY), tray_h(TR_LX, 0), tray_h(TR_LX, TR_LY))
    ix, iy = TR_LX - 2 * TR_T, TR_LY - 2 * TR_T
    V = 0.0
    for i in range(n):
        for j in range(n):
            x = TR_T + (i + .5) * ix / n
            y = TR_T + (j + .5) * iy / n
            V += max(0.0, level - (hmax - tray_h(x, y))) * (ix / n) * (iy / n)
    return V / 1e6

# ----------------------------------------------------------------------------
# РЕШЁТКА (Л3) — AISI 304, 3 мм, 4 шт.
# ----------------------------------------------------------------------------
GR_T, GR_RI = 3.0, 3.0
GR_N = 4
GR_GAP = 1.0
GR_X0 = 1 + TR_T + 1                           # 3.5: упор (1..2.5) + зазор 1
GR_W = (MOD_W - 2 * GR_X0 - (GR_N - 1) * GR_GAP) / GR_N   # 347.5
GR_D = MOD_D - 2 * GR_X0                       # 693
GR_H = TOP_Z - (FRAME_TOP + TR_T)              # 18 — высота борта решётки
GR_MARGIN = 50                                  # поле без перфорации у наружного борта
GR_MARGIN_IN = 20                               # ... у внутреннего (глубокого) борта
GR_HANDLE = (100, 30)                           # ручки-прорези
GR_DEEP = 30                                    # внутренние борта глубже на 30 (жёсткость)
GR_DEEP_Y = (TR_X0 + TR_T + 2.5, MOD_D - TR_X0 - TR_T - 2.5)   # 47..653 — внутри стенок поддона

# ----------------------------------------------------------------------------
# КРЫШКА (Л1) — AISI 430, 1.5 мм; полка нижняя (Л4) — Ст 1.5 мм
# ----------------------------------------------------------------------------
CAP_W, CAP_D = MOD_W, MOD_D
CAP_H = TOP_PLY + CAP_T                         # 19.5 — юбка закрывает фанеру
CAP_RI = 1.5
TOPBOARD_W, TOPBOARD_D = MOD_W - 2 * CAP_T - 1, MOD_D - 2 * CAP_T - 1  # 1396 x 696

SH_T, SH_RI = 1.5, 1.5
SH_W, SH_D = MOD_W - 4, MOD_D - 4               # 1396 x 696
SH_LIP = 40                                     # борт 40 — вторичный поддон (~38 л)
SH_NOTCH = 45                                   # вырез под ногу (с запасом на швы)

# ----------------------------------------------------------------------------
# СТЕНОВЫЕ ПАНЕЛИ (фанера 18)
# ----------------------------------------------------------------------------
PLY_SW, PLY_SH = 2440, 1220                     # формат листа фанеры
PN_W, PN_H = 1400, 1200
PN_N = 2
PN_Z0 = 1010                                    # низ панели от пола
PN_PITCH, PN_HOLE, PN_MARGIN = 50, 8, 50
PN_MOUNT_X = (75, 700, 1325)                    # = оси вертикальных реек (симметрично)
PN_MOUNT_Y = (75, 425, 775, 1125)
PN_MOUNT_D = 5
BT_L, BT_W = 1180, 70                           # рейка-отступ (вертикальная)
BT_XC = PN_MOUNT_X
BT_Y0 = 10                                      # низ рейки от низа панели
BT_ANCHOR = (150, 590, 1030)                    # дюбели вдоль рейки
BT_ANCHOR_D = 8                                 # рамный дюбель 8×80 / анкер по материалу стены

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
        'right': dict(Lw=Ly, h0=tray_h(Lx, 0), h1=tray_h(Lx, Ly), e0=t + CORNER_GAP,
                      e1=Ly - t - CORNER_GAP, tabs=TR_TABS_Y),
        'rear':  dict(Lw=Lx, h0=tray_h(0, Ly), h1=tray_h(Lx, Ly), e0=0.0, e1=Lx, tabs=TR_TABS_X),
        'left':  dict(Lw=Ly, h0=tray_h(0, 0), h1=tray_h(0, Ly), e0=t + CORNER_GAP,
                      e1=Ly - t - CORNER_GAP, tabs=TR_TABS_Y),
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
    dx_, dy_ = drain_xy()
    drain = (dx_ - SB, dy_ - SB, DR_D / 2)
    part = FlatPart('Л2', 'Поддон сливной', 'AISI 304 (08Х18Н10)', t, 1,
                    poly(outline), circles=[drain], bends=bends,
                    note='Б1 — на себя 90°, Б2 — от себя 90°, Б3 — на себя 90°; Rвн=1.5')
    part.bend_dir = {'Б1': 'UP', 'Б2': 'DOWN', 'Б3': 'UP'}
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
        e_side = -(SB - t - CORNER_GAP)   # бока: до внутр. грани переднего борта, зазор 0,3
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


def _grate(code, name, qty, deep_left, deep_right):
    """Решётка: верх 3 мм с перфорацией, борта вниз на 4 стороны (открытые углы).
    Внутренние боковые борта (между решётками) — глубже на GR_DEEP в зоне поддона.
    Развёртка — вид сверху (с лица)."""
    t, Ri = GR_T, GR_RI
    BA = bend_allow(Ri, t)
    SB = Ri + t
    Bx, By = GR_W - 2 * SB, GR_D - 2 * SB
    E = BA + (GR_H - SB)
    Ed = E + GR_DEEP
    v1 = GR_DEEP_Y[0] - GR_X0 - SB          # начало глубокой зоны (коорд. развёртки)
    v2 = GR_DEEP_Y[1] - GR_X0 - SB
    ch = GR_DEEP                            # фаска 45° на переходе
    c = 3.0                                 # фаски 3×45° на концах бортов (открытые углы)
    r = 2.0
    bb = -math.tan(math.radians(270) / 4)
    pts = [(c, -E, 0), (Bx - c, -E, 0), (Bx, -E + c, 0), (Bx, -r, bb), (Bx + r, 0, 0),
           (Bx + E - c, 0, 0), (Bx + E, c, 0)]
    if deep_right:
        pts += [(Bx + E, v1, 0), (Bx + Ed, v1 + ch, 0), (Bx + Ed, v2 - ch, 0), (Bx + E, v2, 0)]
    pts += [(Bx + E, By - c, 0), (Bx + E - c, By, 0), (Bx + r, By, bb), (Bx, By + r, 0),
            (Bx, By + E - c, 0), (Bx - c, By + E, 0), (c, By + E, 0), (0, By + E - c, 0),
            (0, By + r, bb), (-r, By, 0), (-E + c, By, 0), (-E, By - c, 0)]
    if deep_left:
        pts += [(-E, v2, 0), (-Ed, v2 - ch, 0), (-Ed, v1 + ch, 0), (-E, v1, 0)]
    pts += [(-E, c, 0), (-E + c, 0, 0), (-r, 0, bb), (0, -r, 0), (0, -E + c, 0)]
    bends = [(0, -BA / 2, Bx, -BA / 2, 'Б'), (Bx + BA / 2, 0, Bx + BA / 2, By, 'Б'),
             (0, By + BA / 2, Bx, By + BA / 2, 'Б'), (-BA / 2, 0, -BA / 2, By, 'Б')]
    p = FlatPart(code, name, 'AISI 304 (08Х18Н10)', t, qty, pts, bends=bends)
    p.BA, p.SB, p.Bx, p.By, p.E, p.Ed = BA, SB, Bx, By, E, Ed
    p.bend_dir = {'Б': 'DOWN'}
    # перфорация: пазы 6х40 вдоль Y, шахматный порядок; у глубокого борта поле уже
    x0 = GR_MARGIN_IN if deep_left else GR_MARGIN
    x1 = GR_W - (GR_MARGIN_IN if deep_right else GR_MARGIN)
    hy = 72
    y0, y1 = 100, GR_D - 100
    w, L, px, py = 6.0, 40.0, 18.0, 55.0
    nc = int((x1 - x0 - w) // px) + 1
    cx0 = (x0 + x1) / 2 - (nc - 1) * px / 2
    nr = int((y1 - y0 - L) // py) + 1
    cy0 = (y0 + y1) / 2 - (nr - 1) * py / 2
    holes = []
    for i in range(nc):
        cx = cx0 + i * px
        ys = [cy0 + j * py for j in range(nr)] if i % 2 == 0 else \
             [cy0 + py / 2 + j * py for j in range(nr - 1)]
        for cy in ys:
            holes.append(slot(cx - SB, cy - SB, w, L, 'y'))
    hl, hw = GR_HANDLE
    for cy in (hy, GR_D - hy):
        holes.append(slot(GR_W / 2 - SB, cy - SB, hw, hl, 'x'))
    p.holes = holes
    p.perf = dict(n=len(holes) - 2, w=w, L=L, px=px, py=py, nc=nc, nr=nr, cx0=cx0, cy0=cy0, hy=hy,
                  x0=x0, x1=x1)
    p.deep = (deep_left, deep_right)
    p.note = 'Все гибы — от себя 90° (борта вниз), Rвн=3'
    return p


def grate_flat():
    """Крайняя решётка (2 шт.): глубокий борт только с внутренней стороны.
    Правая крайняя = та же деталь, повёрнутая на 180°."""
    return _grate('Л3', 'Решётка крайняя', 2, False, True)


def grate_mid_flat():
    """Средняя решётка (2 шт.): оба боковых борта глубокие."""
    return _grate('Л8', 'Решётка средняя', 2, True, True)


def cap_flat():
    """Крышка 1,5 мм: юбка 19,5 вниз спереди, справа и слева (за вырезом), сзади — бортик
    19,5 ВВЕРХ (не даёт скатиться за верстак). Вырез в левом переднем углу под плиту Л7.
    Развёртка — вид с лица."""
    t, Ri = CAP_T, CAP_RI
    BA = bend_allow(Ri, t)
    SB = Ri + t
    Bx, By = CAP_W - 2 * SB, CAP_D - 2 * SB
    E = BA + (CAP_H - SB)
    uc = PL_X0 + PL_W + PL_GAP - SB          # конец выреза по X (коорд. развёртки)
    vc = PL_D + PL_GAP - SB                  # конец выреза по Y
    es = SB - t - CORNER_GAP                 # удлинение боковых юбок (зазор 0,3 в углу)
    pts = [(uc, vc), (uc, -E), (Bx + SB, -E), (Bx + SB, -BA), (Bx, -BA), (Bx, 0),
           (Bx + BA, 0), (Bx + BA, -es), (Bx + E, -es), (Bx + E, By + es), (Bx + BA, By + es),
           (Bx + BA, By), (Bx, By),
           (Bx, By + BA), (Bx + SB, By + BA), (Bx + SB, By + E), (-SB, By + E), (-SB, By + BA),
           (0, By + BA), (0, By),
           (-BA, By), (-BA, By + es), (-E, By + es), (-E, vc)]
    bends = [(uc, -BA / 2, Bx, -BA / 2, 'Б'), (Bx + BA / 2, 0, Bx + BA / 2, By, 'Б'),
             (0, By + BA / 2, Bx, By + BA / 2, 'Бз'), (-BA / 2, vc, -BA / 2, By, 'Б')]
    dtop = CAP_T + PLY_T / 2                 # отв. по середине толщины фанеры
    off = BA + (dtop - SB)
    CAP_SCREWS_FRONT = (650, 950, 1250)
    CAP_SCREWS_RIGHT = (200, 500)
    circles = [(x - SB, -off, 2.25) for x in CAP_SCREWS_FRONT]
    circles += [(Bx + off, y - SB, 2.25) for y in CAP_SCREWS_RIGHT]
    p = FlatPart('Л1', 'Крышка столешницы', 'AISI 430 шлиф.', t, 1, poly(dedupe(pts)),
                 circles=circles, bends=bends,
                 note='Юбки перед/право/лево — от себя 90°, задний бортик — на себя 90°; Rвн=1.5')
    p.bend_dir = {'Б': 'DOWN', 'Бз': 'UP'}
    p.BA, p.SB, p.Bx, p.By, p.E, p.uc, p.vc = BA, SB, Bx, By, E, uc, vc
    p.screws = (CAP_SCREWS_FRONT, CAP_SCREWS_RIGHT, dtop)
    return p


def shelf_flat():
    p = box_flat('Л4', 'Полка-поддон нижняя (модуль А)', 'AISI 430', SH_T, 1,
                 SH_W, SH_D, SH_LIP, SH_RI, notch=SH_NOTCH)
    p.note = 'Все гибы — на себя 90° (борт вверх), Rвн=1.5; углы у ног закрыть вставками Л10'
    p.bend_dir = {'Б': 'UP'}
    return p


def shelf_insert():
    """Л10 — угловая вставка полки: закрывает борт вокруг выреза под ногу (сварка TIG)."""
    t, Ri = SH_T, SH_RI
    BA = bend_allow(Ri, t)
    SB = Ri + t
    a = SH_NOTCH - SB            # прямые участки (наружный размер стенки = SH_NOTCH)
    L = a + BA + a
    o = poly([(0, 0), (L, 0), (L, SH_LIP), (0, SH_LIP)])
    p = FlatPart('Л10', 'Вставка угловая полки', 'AISI 430', t, 4, o,
                 bends=[(a + BA / 2, 0, a + BA / 2, SH_LIP, 'Б')],
                 note='Гиб 90°, вварить в угол выреза полки Л4 вокруг ноги')
    p.bend_dir = {'Б': 'UP'}
    return p


def drain_strainer():
    """Л11 — колпак-фильтр над сливом: верх с отв. ø3, борта 12 мм вниз с прорезями 3×3."""
    t, Ri = 1.5, 1.5
    BA = bend_allow(Ri, t)
    SB = Ri + t
    W, H = 76, 12
    B = W - 2 * SB
    E = BA + (H - SB)
    pts = [(0, -E), (B, -E), (B, 0), (B + E, 0), (B + E, B), (B, B), (B, B + E), (0, B + E),
           (0, B), (-E, B), (-E, 0), (0, 0)]
    # прорези-зубцы по нижним кромкам бортов (3 шир × 3 гл, шаг 9)
    out = []
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
        out.append((x1, y1))
        free = (abs(y1 - y2) < 1e-6 and abs(abs(y1) - E) < 1e-6 or abs(y1 - (B + E)) < 1e-6 and abs(y1 - y2) < 1e-6) \
            or (abs(x1 - x2) < 1e-6 and (abs(x1 + E) < 1e-6 or abs(x1 - (B + E)) < 1e-6))
        if not free:
            continue
        Lseg = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / Lseg, (y2 - y1) / Lseg
        nx, ny = -uy, ux                      # внутрь контура (CCW)
        k = 1
        while 9 * k + 1.5 < Lseg - 6:
            s0 = 9 * k - 1.5
            s1 = s0 + 3
            for s_, d_ in ((s0, 0), (s0, 3), (s1, 3), (s1, 0)):
                out.append((x1 + ux * s_ + nx * d_, y1 + uy * s_ + ny * d_))
            k += 1
    drills = []
    pitch, nh = 7.5, 8
    m = (B - (nh - 1) * pitch) / 2               # 8,75 от касательной гиба
    circles = [(m + i * pitch, m + j * pitch, 1.5) for i in range(nh) for j in range(nh)]
    bends = [(0, -BA / 2, B, -BA / 2, 'Б'), (B + BA / 2, 0, B + BA / 2, B, 'Б'),
             (0, B + BA / 2, B, B + BA / 2, 'Б'), (-BA / 2, 0, -BA / 2, B, 'Б')]
    p = FlatPart('Л11', 'Колпак-фильтр слива', 'AISI 304 (08Х18Н10)', t, 1, poly(out),
                 circles=circles, bends=bends, note='Борта 12 мм от себя 90°; ставится на дно над сливом')
    p.bend_dir = {'Б': 'DOWN'}
    return p


def foot_plate():
    o = rect_r(40, 40, 2)
    return FlatPart('Л5', 'Подпятник ноги', 'Ст3', PLATE_T, 2 * 4, o,
                    circles=[(20, 20, 6.5)], note='Приварить гайку М12 (без цинка) сверху соосно')


def gusset():
    pts = [(0, 12), (12, 0), (GUSSET, 0), (GUSSET, 6), (6, GUSSET), (0, GUSSET)]
    return FlatPart('Л6', 'Косынка', 'Ст3', 4, 2, poly(pts),
                    note='Модуль Б: перед. ноги + верх. перемычка')


def square_washer():
    return FlatPart('Л9', 'Шайба квадратная 36×36', 'Ст3', 4, 8, rect_r(36, 36, 2),
                    circles=[(18, 18, 4.5)], note='Стяжка модулей М8: по 2 на болт, на внутр. грани ног')


def vise_plate():
    d = [(x, y, 5.5) for x, y in PL_BOLTS]
    p = FlatPart('Л7', 'Плита под тиски / наковальня', 'Ст45 (или Ст3)', PL_T, 1,
                 rect_r(PL_W, PL_D, 3), drills=d,
                 note='Контур — лазер (плазма — только с PL_GAP≥2). 4 отв. ø11 СВЕРЛИТЬ, '
                      'зенковать 90°×ø21 сверху. Отв. тисков М12 — по месту')
    return p


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
    d = [(x, BT_W / 2, BT_ANCHOR_D / 2) for x in BT_ANCHOR]
    return FlatPart('Р1', 'Рейка-отступ', 'Фанера берёзовая ФК 18', PLY_T, 3 * PN_N, o,
                    drills=d, kind='ply')


TOPBOARD_GAP = 1.5                                   # зазор фанера—юбка крышки (радиус гиба)


def topboards():
    """Основа столешницы Б — 1 слой 18 мм, из двух частей со стыком на средней
    поперечине (так вся фанера укладывается в 2 листа 2440×1220).
    Левая часть — с вырезом под плиту Л7."""
    x_lo, x_hi = CAP_T + TOPBOARD_GAP, MOD_W - CAP_T - TOPBOARD_GAP     # 3 .. 1397
    y_lo, y_hi = CAP_T + TOPBOARD_GAP, MOD_D - CAP_T - TOPBOARD_GAP     # 3 .. 697
    M = 'Фанера берёзовая ФК 18'
    w1 = SEAM_X - x_lo
    cx = PL_X0 + PL_W + PL_GAP - x_lo
    cy = PL_D + PL_GAP - y_lo
    D = y_hi - y_lo
    L = poly([(cx, 0), (w1, 0), (w1, D), (0, D), (0, cy), (cx, cy)])
    w2 = x_hi - SEAM_X
    R = poly([(0, 0), (w2, 0), (w2, D), (0, D)])
    a = FlatPart('Щ1', 'Столешница, левая часть (вырез под Л7)', M, PLY_T, 1, L, kind='ply')
    b = FlatPart('Щ2', 'Столешница, правая часть', M, PLY_T, 1, R, kind='ply')
    a.pos = (x_lo, y_lo); b.pos = (SEAM_X, y_lo)
    a.cut = (cx, cy)
    return [a, b]


def ply_screws():
    """Саморезы с крылышками: фанера → трубы. Точки в координатах модуля Б."""
    pts = []
    T = TUBE
    e = T / 2
    # передняя Т2 (справа от плиты), задняя Т2, правая Т3, левая Т3 (за плитой)
    for x in range(PL_X0 + PL_W + 80, MOD_W - 60, 200):
        pts.append((x, e))
    for x in range(120, MOD_W - 60, 200):
        pts.append((x, MOD_D - e))
    for y in (200, 450):
        pts.append((MOD_W - e, y))
    pts.append((e, 480))
    # поперечины: Т4-1 — только за плитой; Т4-2 — по обе стороны стыка; Т4-3
    for y in (420, 580):
        pts.append((CROSS_XC[0], y))
    for y in (150, 350, 550):
        pts.append((CROSS_XC[1] - 11, y)); pts.append((CROSS_XC[1] + 11, y + 100))
    for y in (200, 450):
        pts.append((CROSS_XC[2], y))
    return pts


def acc_parts():
    """Навесные держатели из обрезков фанеры. Задняя планка с 4 шкантами ø8
    (шаг 50 по сетке панели) + 1 саморез от вырыва."""
    parts = []
    M = 'Фанера берёзовая ФК 18'

    def back(code, L):
        o = poly([(0, 0), (L, 0), (L, 90), (0, 90)])
        xs = (75, 225) if L == 300 else (50, 350)
        d = [(x, y, 4) for x in xs for y in (15, 65)]
        sx = xs[0] + 75 if L == 300 else xs[0] + 175          # смещение 25 от сетки
        d.append((sx, 40, 2.25))
        return FlatPart(code, 'Задняя планка', M, PLY_T, 1, o, drills=d, kind='ply')

    def gus(code, h, w):
        return FlatPart(code, 'Косынка', M, PLY_T, 2, poly([(0, 0), (w, 0), (0, h)]), kind='ply')
    # А1 — отвёрточница
    parts.append(back('А1.1', 300))
    sh = FlatPart('А1.2', 'Полка с отв.', M, PLY_T, 1, poly([(0, 0), (300, 0), (300, 80), (0, 80)]),
                  drills=[(30 + 40 * i, 50, 6) for i in range(7)], kind='ply')
    parts.append(sh)
    parts.append(gus('А1.3', 70, 60))
    # А2 — ключница (пазы открыты к переднему краю y=70)
    parts.append(back('А2.1', 400))
    pts = [(0, 0, 0), (400, 0, 0), (400, 70, 0)]
    pitch, n, sw, sd = 45, 8, 8, 45
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
    # А4 — ложемент под перо вилки (на решётку / на верстак), V 90°
    v = poly([(0, 0), (120, 0), (120, 80), (95, 80), (60, 45), (25, 80), (0, 80)])
    parts.append(FlatPart('А4', 'Ложемент под перо вилки', M, PLY_T, 2, v, kind='ply'))
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
             'Отв. ø9 под стяжку — сверлить в сборе модулей (на 252 и 652 от верха)', 'А, Б'),
        Tube('Т2', 'Перемычка верхняя продольная', '40х40х2', W_in, 2 * N_MOD,
             'Мод. Б перед.: 2 втулки под болты плиты (лист 6)', 'А, Б'),
        Tube('Т3', 'Перемычка верхняя боковая', '40х40х2', D_in, 2 * N_MOD,
             'Мод. Б лев.: 2 втулки под болты плиты (лист 6)', 'А, Б'),
        Tube('Т4', 'Поперечина столешницы', '40х40х2', D_in, len(CROSS_XC),
             'Мод. Б, ОСИ на %s от левого края' % ', '.join(str(c) for c in CROSS_XC), 'Б'),
        Tube('Т5', 'Перемычка нижняя продольная', '40х20х2', W_in, 3,
             'А — перед. и задн., Б — только задн.', 'А, Б'),
        Tube('Т6', 'Перемычка нижняя боковая', '40х20х2', D_in, 2 * N_MOD, '', 'А, Б'),
        Tube('Т7', 'Перемычка под плиту Л7', '40х40х2', T7_L, 1,
             'Мод. Б, ОСЬ на %d от фронта, между Т3 лев. и Т4-1' % T7_YC, 'Б'),
        Tube('Т8', 'Ухо крепления к стене', 'уголок 40х40х4', 50, N_MOD,
             'Отв. ø10; к низу задней Т2 посередине, полкой вниз', 'А, Б'),
        Tube('Т9', 'Втулка распорная', 'труба 16х2,5', 38, 4,
             'Внутрь Т2/Т3 под болты плиты, обварить снизу заподлицо', 'Б'),
    ]


TUBE_STOCK = {'40х40х2': 6000, '40х20х2': 6000}


def cut_sticks(pieces, stock=6000, kerf=3, trim=10):
    """Раскрой хлыстов: first-fit decreasing, с торцовкой концов хлыста (trim с каждой стороны)."""
    usable = stock - 2 * trim
    items = sorted(pieces, key=lambda p: -p[1])
    sticks = []
    for code, L in items:
        for s in sticks:
            used = sum(l for _, l in s) + kerf * len(s)
            if used + L + kerf <= usable:
                s.append((code, L))
                break
        else:
            sticks.append([(code, L)])
    return sticks


if __name__ == '__main__':
    from shapely.geometry import Polygon
    for f in (tray_flat, grate_flat, grate_mid_flat, cap_flat, shelf_flat, shelf_insert,
              drain_strainer, foot_plate, gusset, square_washer, vise_plate, panel, batten):
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
