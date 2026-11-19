# -*- coding: utf-8 -*-
"""Листы чертежей A3."""
import math
from matplotlib.patches import Rectangle, Polygon as MplPoly, Circle, FancyArrowPatch
from geom import *
from draw import *

TOTAL = 11
HATCH = '////'


# ============================================================================
# Общие элементы верстака в виде спереди (x — вдоль модуля, z — вверх)
# ============================================================================
def front_frame(v, mod, x0=0, thin=False, holes=True):
    W, T = MOD_W, TUBE
    lw = LW_THIN if thin else LW_THICK
    z0 = FOOT_H + PLATE_T
    for x in (x0, x0 + W - T):
        v.rect(x, FOOT_H, T, PLATE_T, lw=LW_THIN)
        v.rect(x + T / 2 - 6, 8, 12, FOOT_H - 8, lw=LW_THIN)
        v.rect(x + T / 2 - 20, 0, 40, 8, lw=LW_THIN)
        v.rect(x, z0, T, LEG_L, lw=lw)
        if holes:
            for hz in LEG_HOLES:
                v.hidden(x, z0 + hz - 4.5, x + T, z0 + hz - 4.5)
                v.hidden(x, z0 + hz + 4.5, x + T, z0 + hz + 4.5)
    v.rect(x0 + T, FRAME_TOP - T, W - 2 * T, T, lw=lw)
    if mod == 'A':
        v.rect(x0 + T, LOW_Z0, W - 2 * T, LOW_H, lw=lw)
    else:
        v.rect(x0 + T, LOW_Z0, W - 2 * T, LOW_H, lw=LW_THIN)          # задняя, видна насквозь
        g = [(0, 12), (12, 0), (100, 0), (100, 6), (6, 100), (0, 100)]
        for side in (1, -1):
            xc = x0 + T if side == 1 else x0 + W - T
            v.polyline([(xc + side * gy, FRAME_TOP - T - gx) for gx, gy in g], lw=lw)


def front_tray(v, x0=0, lw=LW_THIN):
    """Видимая часть поддона ниже верхней перемычки (вид спереди)."""
    zt = FRAME_TOP + TR_T
    xl, xr = x0 + TR_X0, x0 + TR_X0 + TR_LX
    zfl, zfr = zt - tray_h(0, 0), zt - tray_h(TR_LX, 0)
    zrl, zrr = zt - tray_h(0, TR_LY), zt - tray_h(TR_LX, TR_LY)
    zc = FRAME_TOP - TUBE
    v.polyline([(xl, zc), (xl, zrl), (xr, zrr), (xr, zc)], closed=False, lw=lw)
    v.line(xl, zfl, xr, zfr, lw=lw)
    # слив
    xd = x0 + TR_X0 + TR_T + DR_OFF
    zd = zt - tray_h(TR_T + DR_OFF, TR_LY - TR_T - DR_OFF)
    v.rect(xd - 14, zd - 25, 28, 25, lw=LW_THIN)
    v.rect(xd - 16, zd - 80, 32, 55, lw=LW_THIN)        # кран
    v.line(xd + 16, zd - 52, xd + 70, zd - 52, lw=LW_THIN)  # ручка
    v.rect(xd - 7, zd - 115, 14, 35, lw=LW_THIN)        # штуцер
    return xd, zd


def front_top_A(v, x0=0, lw=LW_THICK):
    # полка поддона + упоры
    v.rect(x0 + 1, FRAME_TOP, MOD_W - 2, TR_T, lw=LW_THIN)
    for tc in TR_TABS_X:
        v.rect(x0 + TR_X0 + tc - TR_TAB_L / 2, FRAME_TOP, TR_TAB_L, TR_TAB_H, lw=LW_THIN)
    for k in range(GR_N):
        gx = x0 + GR_X0 + k * (GR_W + GR_GAP)
        v.rect(gx, FRAME_TOP + TR_T, GR_W, GR_H, lw=lw)


def front_top_B(v, x0=0, lw=LW_THICK):
    xc = x0 + PL_X0 - PL_GAP
    v.rect(x0, FRAME_TOP, xc - x0, CAP_H, lw=lw)
    v.rect(x0 + PL_X0, FRAME_TOP, PL_W, PL_T, lw=lw, fill='#8a9097')


def vise_x(x0=0):
    return x0 + PL_X0 + 140


def vise(v, x, z, lw=LW_THIN):
    """Тиски (покупные), условно. x — ось, z — верх столешницы."""
    v.rect(x - 90, z, 180, 30, lw=lw, fill='white', z=4)
    v.rect(x - 70, z + 30, 140, 80, lw=lw, fill='white', z=4)
    v.rect(x - 80, z + 110, 160, 25, lw=lw, fill='white', z=4)
    v.line(x + 80, z + 60, x + 200, z + 60, lw=lw, z=4)


# ============================================================================
# ЛИСТ 1 — Общий вид
# ============================================================================
def sheet1():
    fig, ax = new_sheet('Общий вид. Планировка', 1, TOTAL, 'План 1:50, виды 1:20',
                        'см. спецификацию')
    # ---------------- План ----------------
    v = View(ax, 38, 150, 1 / 50)
    label(ax, 38, 283, 'ПЛАН ГАРАЖА 1:50')
    Wg, Lg = GARAGE_W, GARAGE_L
    for x1, y1, x2, y2 in ((0, 0, 0, Lg), (Wg, 0, Wg, Lg), (0, Lg, Wg, Lg)):
        v.line(x1, y1, x2, y2, lw=2.2)
    v.line(0, 0, 250, 0, lw=2.2); v.line(Wg - 250, 0, Wg, 0, lw=2.2)
    v.line(250, -60, Wg - 250, -60, lw=LW_THIN, ls=(0, (6, 3)))
    v.text(Wg / 2, -260, 'ворота', size=6)
    # верстак
    bx = BENCH_X0
    by = Lg - MOD_D
    v.rect(bx, by, MOD_W, MOD_D, lw=LW_THICK, fill='#dfe8f1')
    v.rect(bx + MOD_W, by, MOD_W, MOD_D, lw=LW_THICK, fill='#eeeeee')
    v.text(bx + MOD_W / 2, by + 350, 'А', size=8, weight='bold')
    v.text(bx + 1.5 * MOD_W, by + 350, 'Б', size=8, weight='bold')
    v.circle(bx + TR_X0 + TR_T + DR_OFF, by + MOD_D - (TR_X0 + TR_T + DR_OFF), 45, lw=0.6)
    # панели
    for k in range(PN_N):
        v.rect(bx + k * PN_W, Lg - 2 * PLY_T, PN_W, 2 * PLY_T, fill='#c8a26a', lw=LW_THIN)
    v.leader(bx + 300, Lg - 18, -6, 7, 'П1 (×2)', size=6)
    v.rect(bx + MOD_W + PL_X0, by, PL_W, PL_D, lw=LW_THIN, fill='#8a9097')
    # мотоцикл, стеллаж
    v.polyline([(1250, 1700), (1750, 1700), (1750, 3900), (1250, 3900)], lw=LW_THIN, ls='--')
    v.text(1500, 2800, 'мото', size=6, rot=90)
    v.rect(0, 3600, 450, 1000, lw=LW_THIN, ls='--')
    v.text(225, 4100, 'стеллаж', size=5, rot=90)
    v.dimx(0, Wg, Lg + 450, Lg, Lg)
    v.dimy(0, Lg, -350, 0, 0)
    v.dimy(by, Lg, Wg + 420, Wg, Wg, left=False)
    v.dimx(0, bx, by - 380, 0, by, text='100')
    v.dimx(bx, bx + 2 * MOD_W, by - 380, by, by)

    # ---------------- Фасад задней стены ----------------
    s = 1 / 20
    v = View(ax, 122, 150, s)
    label(ax, 122, 283, 'ФАСАД ЗАДНЕЙ СТЕНЫ (верстак + панели) 1:20')
    v.line(-100, 0, Wg + 100, 0, lw=LW_THICK)
    v.line(0, 0, 0, 2450, lw=1.6); v.line(Wg, 0, Wg, 2450, lw=1.6)
    for k, mod in enumerate(('A', 'B')):
        x0 = bx + k * MOD_W
        front_frame(v, mod, x0, holes=False)
        if mod == 'A':
            front_tray(v, x0)
            front_top_A(v, x0)
            v.rect(x0 + 2, LOW_Z1, MOD_W - 4, SH_LIP, lw=LW_THIN)
            v.polyline([(x0 + 60, LOW_Z1 + SH_T), (x0 + 330, LOW_Z1 + SH_T),
                        (x0 + 330, LOW_Z1 + 330), (x0 + 60, LOW_Z1 + 330)], lw=LW_THIN,
                       ls=(0, (3, 2)))
            v.text(x0 + 195, LOW_Z1 + 165, 'канистра\n10–20 л', size=5)
        else:
            front_top_B(v, x0)
            vise(v, vise_x(x0), TOP_Z)
            v.polyline([(x0 + 200, 0), (x0 + 900, 0), (x0 + 900, 860), (x0 + 200, 860)],
                       lw=LW_THIN, ls=(0, (3, 2)))
            v.text(x0 + 550, 450, 'тумба на колёсах\n(покупная, h≤870)', size=5)
    # панели
    for k in range(PN_N):
        px = bx + k * PN_W
        v.rect(px, PN_Z0, PN_W, PN_H, lw=LW_THICK, fill='#f3e3c7')
        xs, ys = [], []
        for i in range(27):
            for j in range(23):
                X, Y = v.P(px + 50 + 50 * i, PN_Z0 + 50 + 50 * j)
                xs.append(X); ys.append(Y)
        ax.scatter(xs, ys, s=0.15, c='0.35', linewidths=0, zorder=3)
        v.text(px + PN_W / 2, PN_Z0 + PN_H + 60, 'П1 — панель 1400×1200 (сетка ø8 шаг 50)',
               size=5.5)
    # навесные держатели условно
    def acc_front(x, z, L, kind):
        v.rect(x, z, L, 90, lw=LW_THIN, fill='#e4c896')
        v.rect(x, z + 72, L, 18, lw=LW_THIN, fill='#d9b77d')
        v.text(x + L / 2, z + 36, kind, size=5)
    acc_front(bx + 250, 1750, 400, 'А2 ключница')
    acc_front(bx + 850, 1500, 300, 'А1 отвёртки')
    acc_front(bx + MOD_W + 250, 1350, 400, 'А3 полка')
    acc_front(bx + MOD_W + 800, 1800, 400, 'А3 полка')
    v.dimx(0, bx, -170, 0, 0, text='100')
    v.dimx(bx, bx + MOD_W, -170, 0, 0)
    v.dimx(bx + MOD_W, bx + 2 * MOD_W, -170, 0, 0)
    v.dimx(bx + 2 * MOD_W, Wg, -170, 0, 0, text='100')
    v.dimy(0, TOP_Z, -230, bx, bx, text=fmt(round(TOP_Z, -1)))
    v.dimy(0, PN_Z0, -420, bx, bx)
    v.dimy(PN_Z0, PN_Z0 + PN_H, -230, bx, bx)
    v.text(bx + MOD_W / 2, -330, 'Модуль А — разборка вилок/моторов, слив', size=5.5)
    v.text(bx + 1.5 * MOD_W, -330, 'Модуль Б — рабочий, тиски', size=5.5)

    # ---------------- Разрезы ----------------
    for k, mod in enumerate(('A', 'B')):
        v = View(ax, 300 + k * 55, 150, s)
        label(ax, 300 + k * 55, 283, 'Разрез %s' % ('А' if mod == 'A' else 'Б'), size=7)
        side_section(v, mod)
    fig._iso_area = (25, 12, 200, 125)
    iso_scene(ax, 25, 10, 200, 128)
    label(ax, 27, 137, 'ИЗОМЕТРИЯ (условно)')
    notes(ax, 236, 127, [
        'ОСНОВНЫЕ РЕШЕНИЯ',
        '1. Верстак 2800×700, высота 950 (под рост 187), два модуля по 1400,',
        '   стягиваются болтами М8 через ноги. Зазор до боковых стен по 100.',
        '2. Модуль А: поддон из нерж. 1,5 мм, дно с уклоном ~1% к сливу',
        '   (зад-лево). Сверху 4 съёмные решётки 3 мм вровень со столешницей.',
        '   Слив: полумуфта G1/2" → кран → шланг → канистра на полке.',
        '   Решётки снял — получил мойку-ванну ~60 л для деталей.',
        '3. Модуль Б: фанера 18 мм на 3 поперечинах + крышка из нерж. 1,5.',
        '   В правом переднем углу — плита 20 мм вровень со столешницей,',
        '   лежит прямо на каркасе: тиски + площадка для правки/рихтовки.',
        '   Под столешницей место под инструментальную тумбу (h ≤ 870).',
        '4. Каркасы: профиль 40×40×2 и 40×20×2, сварка MAG, покраска.',
        '5. Стена: 2 панели из фанеры 18 мм над верстаком, отверстия ø8',
        '   сеткой 50 — под шканты/держатели. Панели на вертикальных рейках.',
        '   Вся фанера — 2 листа 2440×1220.',
        '6. Перед заказом — замерить гараж! Если ширина < 2900, уменьшить',
        '   MOD_W в geom.py и пересобрать (build.py).',
    ], size=5.8, dy=3.35)
    return fig


def side_section(v, mod):
    """Разрез через модуль (вид слева, стена слева). h = расстояние от стены."""
    D, T = MOD_D, TUBE
    hy = lambda y: D - y            # локальная y модуля (0 — перед) -> от стены
    # стена + панель
    v.line(0, 0, 0, 2450, lw=1.6)
    v.polyline([(-60, 0), (0, 0), (0, 2450), (-60, 2450)], lw=0, fill='0.85', hatch=HATCH)
    v.rect(0, PN_Z0 + BT_Y0, PLY_T, BT_L, lw=LW_THIN, fill='#d9b77d')
    v.rect(PLY_T, PN_Z0, PLY_T, PN_H, lw=LW_THICK, fill='#f3e3c7')
    v.line(-80, 0, D + 80, 0, lw=LW_THICK)
    # ноги (за плоскостью разреза)
    for h0 in (0, D - T):
        v.rect(h0, FOOT_H + PLATE_T, T, LEG_L, lw=LW_THIN)
        v.rect(h0, FOOT_H, T, PLATE_T, lw=LW_THIN)
        v.rect(h0 + 14, 8, 12, FOOT_H - 8, lw=LW_THIN)
        v.rect(h0, 0, 40, 8, lw=LW_THIN)
    # сечения перемычек
    for h0 in (0, D - T):
        v.rect(h0, FRAME_TOP - T, T, T, lw=LW_THICK, fill='0.6')
        v.rect(h0 + 2, FRAME_TOP - T + 2, T - 4, T - 4, lw=LW_HAIR, fill='white')
    lows = (0, D - LOW_W) if mod == 'A' else (0,)
    for h0 in lows:
        v.rect(h0, LOW_Z0, LOW_W, LOW_H, lw=LW_THICK, fill='0.6')
    if mod == 'A':
        xs = 600 - TR_X0
        zt = FRAME_TOP + TR_T
        zf = zt - tray_h(xs, 0); zr = zt - tray_h(xs, TR_LY)
        hf, hr = hy(TR_X0), hy(TR_X0 + TR_LY)
        prof = [(D - 1, FRAME_TOP + TR_T), (hf, FRAME_TOP + TR_T), (hf, zf), (hr, zr),
                (hr, FRAME_TOP + TR_T), (1, FRAME_TOP + TR_T)]
        v.polyline(prof, closed=False, lw=1.3, color='#1f5fa8')
        for k in range(1):
            v.rect(hy(GR_X0 + GR_D), FRAME_TOP + TR_T + GR_H - GR_T, GR_D, GR_T, lw=LW_THICK,
                   fill='#9fb4c8')
            v.rect(hy(GR_X0 + GR_D), FRAME_TOP + TR_T, GR_T, GR_H, lw=LW_THICK, fill='#9fb4c8')
            v.rect(hy(GR_X0) - GR_T, FRAME_TOP + TR_T, GR_T, GR_H, lw=LW_THICK, fill='#9fb4c8')
        # полка + канистра
        v.polyline([(2, LOW_Z1 + SH_LIP), (2, LOW_Z1), (D - 2, LOW_Z1), (D - 2, LOW_Z1 + SH_LIP)],
                   closed=False, lw=1.0)
        v.polyline([(hr + 10, LOW_Z1), (hr + 230, LOW_Z1), (hr + 230, LOW_Z1 + 330),
                    (hr + 10, LOW_Z1 + 330)], lw=LW_THIN, ls=(0, (3, 2)))
        zd = zt - tray_h(TR_T + DR_OFF, TR_LY - TR_T - DR_OFF)
        hd = hy(TR_X0 + TR_LY - TR_T - DR_OFF)
        v.rect(hd - 14, zd - 25, 28, 25, lw=LW_THIN)
        v.rect(hd - 16, zd - 80, 32, 55, lw=LW_THIN)
        v.rect(hd - 7, zd - 115, 14, 35, lw=LW_THIN)
        v.line(hd, zd - 115, hd + 40, LOW_Z1 + 330, lw=0.8, color='#555')
        v.text(D / 2, LOW_Z1 + 470, 'уклон\n→ слив', size=5)
    else:
        v.rect(0, FRAME_TOP, D, PLY_T, lw=LW_THIN, fill='#e9cf9f', hatch='xxx')
        v.polyline([(0, FRAME_TOP), (0, TOP_Z), (D, TOP_Z), (D, FRAME_TOP)], closed=False,
                   lw=1.2, color='#1f5fa8')
        v.polyline([(120, 0), (580, 0), (580, 860), (120, 860)], lw=LW_THIN, ls=(0, (3, 2)))
        v.text(350, 420, 'тумба', size=5)
    v.dimy(0, TOP_Z, D + 120, D, D, left=False, text=fmt(round(TOP_Z, -1)))
    v.dimx(0, D, -170, 0, 0)


def iso_scene(ax, x, y, w, h):
    I = Iso(e=(-0.62, -1.0, 0.62))
    Wg = GARAGE_W
    yb = GARAGE_L
    # стены и пол
    I.face([(0, yb - 2600, 0), (Wg, yb - 2600, 0), (Wg, yb, 0), (0, yb, 0)], (0, 0, 1), '#d7d7d2',
           ec='0.6', prio=0, force=True)
    I.face([(0, yb, 0), (Wg, yb, 0), (Wg, yb, 2500), (0, yb, 2500)], (0, -1, 0), '#f4f4f0',
           ec='0.6', prio=0)
    I.face([(Wg, yb - 2600, 0), (Wg, yb, 0), (Wg, yb, 2500), (Wg, yb - 2600, 2500)], (-1, 0, 0),
           '#ececE6', ec='0.6', prio=0)
    # панели
    for k in range(2):
        px = BENCH_X0 + k * PN_W
        dots = [(px + 50 + 50 * i, yb - 2 * PLY_T, PN_Z0 + 50 + 50 * j)
                for i in range(0, 27) for j in range(0, 23)]
        I.box(px, yb - 2 * PLY_T, PN_Z0, PN_W, PLY_T, PN_H, '#e3c48f', prio=1, dots={0: dots})
    # держатели
    for (ax_, az, L) in ((BENCH_X0 + 250, 1750, 400), (BENCH_X0 + 850, 1500, 300),
                          (BENCH_X0 + MOD_W + 250, 1350, 400), (BENCH_X0 + MOD_W + 800, 1800, 400)):
        I.box(ax_, yb - 2 * PLY_T - 18, az, L, 18, 90, '#d2a86a', prio=1.5)
        I.box(ax_, yb - 2 * PLY_T - 90, az + 72, L, 72, 18, '#d2a86a', prio=1.5)
    # верстак
    steel = '#3b3f45'
    ss = '#c5ccd3'
    for k, mod in enumerate(('A', 'B')):
        x0 = BENCH_X0 + k * MOD_W
        Y = lambda yy: yb - MOD_D + yy     # локальная y модуля (0 — перед)
        zl = FOOT_H + PLATE_T
        for lx in (0, MOD_W - TUBE):
            for ly in (0, MOD_D - TUBE):
                I.box(x0 + lx, Y(ly), zl, TUBE, TUBE, LEG_L, steel)
                I.box(x0 + lx + 5, Y(ly) + 5, 0, 30, 30, zl, '#777')
        I.box(x0 + TUBE, Y(0), FRAME_TOP - TUBE, MOD_W - 2 * TUBE, TUBE, TUBE, steel)
        I.box(x0 + TUBE, Y(MOD_D - TUBE), FRAME_TOP - TUBE, MOD_W - 2 * TUBE, TUBE, TUBE, steel)
        for lx in (0, MOD_W - TUBE):
            I.box(x0 + lx, Y(TUBE), FRAME_TOP - TUBE, TUBE, MOD_D - 2 * TUBE, TUBE, steel)
            I.box(x0 + lx, Y(TUBE), LOW_Z0, LOW_W, MOD_D - 2 * TUBE, LOW_H, steel)
        I.box(x0 + TUBE, Y(MOD_D - LOW_W), LOW_Z0, MOD_W - 2 * TUBE, LOW_W, LOW_H, steel)
        if mod == 'A':
            I.box(x0 + TUBE, Y(0), LOW_Z0, MOD_W - 2 * TUBE, LOW_W, LOW_H, steel)
            I.box(x0 + 2, Y(2), LOW_Z1, MOD_W - 4, MOD_D - 4, SH_T, '#5a5f66')
            I.box(x0 + 60, Y(330), LOW_Z1 + SH_T, 230, 330, 330, '#b3261e')
            zt = FRAME_TOP + TR_T
            I.box(x0 + TR_X0, Y(TR_X0), zt - 90, TR_LX, TR_LY, 90 - TR_T, '#9aa4ad')
            I.box(x0 + 1, Y(1), FRAME_TOP, MOD_W - 2, MOD_D - 2, TR_T, ss)
            for g in range(GR_N):
                gx = x0 + GR_X0 + g * (GR_W + GR_GAP)
                dots = [(gx + 60 + 18 * i, Y(GR_X0 + 100 + 27.5 * j), TOP_Z)
                        for i in range(13) for j in range(18)]
                I.box(gx, Y(GR_X0), FRAME_TOP + TR_T, GR_W, GR_D, GR_H, '#d4dae0',
                      dots={4: dots})
        else:
            xc = PL_X0 - PL_GAP
            I.box(x0, Y(0), FRAME_TOP, xc, MOD_D, CAP_H, '#d9dee3')
            I.box(x0 + xc, Y(PL_D + PL_GAP), FRAME_TOP, MOD_W - xc, MOD_D - PL_D - PL_GAP, CAP_H,
                  '#d9dee3')
            I.box(x0 + PL_X0, Y(0), FRAME_TOP, PL_W, PL_D, PL_T, '#7d838a')
            I.box(x0 + 200, Y(40), 0, 700, 470, 860, '#1d5e3a')
            vx = vise_x(x0) - 90
            I.box(vx, Y(10), TOP_Z, 180, 160, 30, '#2f3338')
            I.box(vx + 20, Y(-30), TOP_Z + 30, 140, 200, 80, '#2f3338')
            I.box(vx + 10, Y(-40), TOP_Z + 110, 160, 30, 25, '#2f3338')
    x0_, y0_, x1_, y1_ = I.extent()
    sc = min(w / (x1_ - x0_), h / (y1_ - y0_))
    ox = x + (w - sc * (x1_ - x0_)) / 2 - sc * x0_
    oy = y + (h - sc * (y1_ - y0_)) / 2 - sc * y0_
    I.render(ax, ox, oy, sc)


# ============================================================================
# ЛИСТЫ 2, 3 — Каркасы
# ============================================================================
def sheet_frame(mod):
    no = 2 if mod == 'A' else 3
    ttl = 'Каркас модуля А (слив)' if mod == 'A' else 'Каркас модуля Б (рабочий)'
    fig, ax = new_sheet(ttl, no, TOTAL, '1:10', 'Труба 40×40×2, 40×20×2 (ГОСТ 30245)')
    s = 0.1
    W, D, T = MOD_W, MOD_D, TUBE
    # ---- вид спереди
    vf = View(ax, 45, 170, s)
    label(ax, 45, 283, 'ВИД СПЕРЕДИ' + (' (поддон, решётки, полка сняты)' if mod == 'A' else
                                         ' (крышка и фанера сняты)'), size=7)
    vf.line(-50, 0, W + 50, 0, lw=LW_THIN)
    front_frame(vf, mod)
    vf.dimx(0, W, FRAME_TOP + 120, FRAME_TOP, FRAME_TOP)
    vf.dimx(T, W - T, FRAME_TOP + 60, FRAME_TOP, FRAME_TOP)
    vf.dimy(0, FRAME_TOP, -150, 0, 0)
    vf.dimy(FOOT_H + PLATE_T, FRAME_TOP, -80, 0, 0, text='%d (Т1)' % LEG_L)
    vf.dimy(0, LOW_Z0, W + 70, W, W, left=False)
    vf.dimy(FRAME_TOP - T, FRAME_TOP, W + 70, W, W, left=False, text='40')
    vf.dimy(0, FOOT_H, W + 160, W, W, left=False, text='≈25')
    vf.leader(20, 500, 12, 4, 'Т1', ball=True)
    vf.leader(560, FRAME_TOP - 20, 0, -12, 'Т2', ball=True)
    vf.leader(560 if mod == 'A' else 900, LOW_Z0 + 20, 0, 12, 'Т5', ball=True)
    vf.leader(20, FOOT_H + 2, -10, -6, 'Л5', ball=True)
    if mod == 'B':
        vf.leader(T + 30, FRAME_TOP - T - 30, 10, -12, 'Л6', ball=True)
        vf.text(700, 420, 'ниша под тумбу:\nширина 1320 (1120 вверху у косынок),\nвысота до %d от пола' % (FRAME_TOP - TUBE - 10), size=6, color='0.3')
    # отв. стяжки
    vf.leader(W - 20, FOOT_H + PLATE_T + LEG_HOLES[1], 14, 6, '2 отв. ø9 сквозь', size=6)
    vf.dimy(FOOT_H + PLATE_T, FOOT_H + PLATE_T + LEG_HOLES[0], W + 250, W, W, left=False,
            text='250')
    vf.dimy(FOOT_H + PLATE_T, FOOT_H + PLATE_T + LEG_HOLES[1], W + 330, W, W, left=False,
            text='650')

    # ---- вид слева
    vs = View(ax, 245, 170, s)
    label(ax, 245, 283, 'ВИД СЛЕВА', size=7)
    vs.line(-50, 0, D + 50, 0, lw=LW_THIN)
    z0 = FOOT_H + PLATE_T
    for h0 in (0, D - T):
        vs.rect(h0, FOOT_H, T, PLATE_T, lw=LW_THIN)
        vs.rect(h0 + 14, 8, 12, FOOT_H - 8, lw=LW_THIN)
        vs.rect(h0, 0, 40, 8, lw=LW_THIN)
        vs.rect(h0, z0, T, LEG_L)
        for hz in LEG_HOLES:
            vs.circle(h0 + T / 2, z0 + hz, 4.5, lw=LW_THIN)
    vs.rect(T, FRAME_TOP - T, D - 2 * T, T)
    vs.rect(T, LOW_Z0, D - 2 * T, LOW_H)
    vs.dimx(0, D, FRAME_TOP + 120, FRAME_TOP, FRAME_TOP)
    vs.dimx(T, D - T, FRAME_TOP + 60, FRAME_TOP, FRAME_TOP)
    vs.leader(D / 2, FRAME_TOP - 20, 0, -12, 'Т3', ball=True)
    vs.leader(D / 2, LOW_Z0 + 20, 0, 12, 'Т6', ball=True)
    vs.text(0, -60, 'стена', size=5.5, ha='left', va='top')
    vs.text(D, -60, 'перед', size=5.5, ha='right', va='top')

    # ---- вид сверху
    vt = View(ax, 45, 62, s)
    label(ax, 45, 143, 'ВИД СВЕРХУ' + (' (поддон снят)' if mod == 'A' else ' (столешница снята)'),
          size=7)
    vt.rect(0, 0, W, D)
    vt.rect(T, T, W - 2 * T, D - 2 * T)
    for xx in (T, W - T):
        vt.line(xx, 0, xx, T, lw=LW_THIN); vt.line(xx, D - T, xx, D, lw=LW_THIN)
    for yy in (T, D - T):
        vt.line(0, yy, T, yy, lw=LW_THIN); vt.line(W - T, yy, W, yy, lw=LW_THIN)
    # нижние перемычки (видны насквозь)
    vt.hidden(LOW_W, T, LOW_W, D - T); vt.hidden(W - LOW_W, T, W - LOW_W, D - T)
    vt.hidden(T, D - LOW_W, W - T, D - LOW_W)
    if mod == 'A':
        vt.hidden(T, LOW_W, W - T, LOW_W)
    if mod == 'B':
        for xc in CROSS_XC:
            vt.rect(xc - T / 2, T, T, D - 2 * T)
        vt.rect(T7_X0, T7_YC - T / 2, T7_L, T)
        vt.polyline([(PL_X0, 0), (W, 0), (W, PL_D), (PL_X0, PL_D)], lw=LW_THIN, ls=(0, (5, 2)),
                    color='#c0392b')
        vt.text(PL_X0 + 230, PL_D - 70, 'плита Л7 (сверху)', size=5, color='#c0392b')
        for bx_, by_ in PL_BOLTS:
            X, Y = PL_X0 + bx_, by_
            vt.circle(X, Y, 5.5, lw=LW_THIN, color='#c0392b')
            vt.line(X - 12, Y, X + 12, Y, lw=LW_HAIR); vt.line(X, Y - 12, X, Y + 12, lw=LW_HAIR)
        for k, xc in enumerate(CROSS_XC):
            vt.dimx(0, xc, -60 - 60 * k, 0, 0)
        vt.dimy(0, T7_YC, W + 60, W, W, left=False)
        vt.leader(CROSS_XC[0], D / 2 + 80, -10, 6, 'Т4', ball=True)
        vt.leader(T7_X0 + 80, T7_YC, -4, 8, 'Т7', ball=True)
        vt.leader(PL_X0 + PL_BOLTS[1][0], PL_BOLTS[1][1], 4, -16,
                  '4 отв. ø11 в трубах — сверлить по плите Л7', size=5.5)
    vt.dimx(0, W, D + 60, D, D)
    vt.dimy(0, D, -60, 0, 0)
    vt.text(W / 2, D + 130, 'стена', size=5.5)
    vt.text(W / 2 + 350 if mod == 'B' else W / 2, -60, 'перед', size=5.5)

    # ---- деталь ноги и подпятника
    vl = View(ax, 335, 170, s)
    label(ax, 318, 283, 'Т1 НОГА (8 шт.) 1:10', size=7)
    vl.rect(0, 0, T, LEG_L)
    for hz in LEG_HOLES:
        vl.circle(T / 2, hz, 4.5, lw=LW_THIN)
        vl.axis(-60, hz, T + 60, hz)
    vl.dimy(0, LEG_L, -80, 0, 0)
    vl.dimy(0, LEG_HOLES[0], T + 80, T, T, left=False)
    vl.dimy(0, LEG_HOLES[1], T + 170, T, T, left=False)
    vl.text(T + 260, LEG_L / 2, 'отв. ø9\nсквозь,\nось X\n(вдоль\nверстака)', size=5.5, ha='left')

    # примечания + таблица труб модуля
    rows = []
    for tb in tubes():
        if mod == 'B' and tb.code == 'Т5':
            q = 1
        elif mod == 'A' and tb.code in ('Т4', 'Т7'):
            continue
        elif tb.code == 'Т5':
            q = 2
        elif tb.code in ('Т4', 'Т7'):
            q = tb.qty
        else:
            q = tb.qty // N_MOD
        rows.append((tb.code, tb.name, tb.profile, fmt(tb.L), q))
    rows.append(('Л5', 'Подпятник 40×40×4 + гайка М12', 'лист 4', '—', 4))
    if mod == 'B':
        rows.append(('Л6', 'Косынка', 'лист 4', '—', 2))
        rows.append(('Л7', 'Плита 20 мм (кладётся сверху, болты)', 'лист 6', '—', 1))
    yb = table(ax, 233, 158, ['Поз.', 'Наименование', 'Профиль', 'L, мм', 'Кол.'], rows,
               [11, 72, 22, 16, 11])
    lines = [
        'ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ',
        '1. Все торцы резать под 90°. Перемычки — встык между ногами,',
        '   наружные грани заподлицо с ногами (верх Т2/Т3 = верх ног).',
        '2. Сварка MAG (п/а), швы по контуру; собрать на прихватках,',
        '   проверить диагонали верхней рамы (разница ≤ 2 мм), затем обварить.',
        '3. Плоскостность верха каркаса ≤ 2 мм на всю длину.',
        '4. Л5 с приваренной гайкой М12 — к низу ноги, сплошной шов.',
        '5. Отверстия ø9 в ногах сверлить до сварки, соосно у всех 8 ног.',
        '6. Окалину/брызги зачистить, покраска (грунт + эмаль/порошок).',
    ]
    if mod == 'A':
        lines += ['7. Поддон Л2 лежит полкой на верхней раме, не приваривается.',
                  '8. Нижняя полка Л4 лежит на Т5/Т6, фиксируется ногами.']
    else:
        lines += ['7. Т4 и Т7 — вровень по верху с Т2. Л6 вварить в плоскости',
                  '   передних ног, по центру профиля (с двух сторон).',
                  '8. Верх Т2/Т3/Т4-3/Т7 под плитой Л7 — без наплывов (зачистить),',
                  '   плита должна лечь без качки. Отв. ø11 сверлить по плите.',
                  '9. Фанеру крепить сверху саморезами с крылышками 4,8×38.']
    notes(ax, 233, yb - 4, lines, size=5.6, dy=3.2)
    return fig


# ============================================================================
# ЛИСТ 4 — Поддон
# ============================================================================
def sheet_tray():
    fig, ax = new_sheet('Поддон Л2 (модуль А)', 4, TOTAL, '1:10; узлы 1:1, 1:2',
                        'AISI 304, 1,5 мм')
    s = 0.1
    T = tray_flat()
    zt = FRAME_TOP + TR_T
    X0 = TR_X0
    # ---- вид сверху (в координатах каркаса)
    v = View(ax, 40, 200, s)
    label(ax, 40, 283, 'ВИД СВЕРХУ (в каркасе)', size=7)
    v.rect(1, 1, MOD_W - 2, MOD_D - 2)
    v.rect(X0 + TR_T, X0 + TR_T, TR_LX - 2 * TR_T, TR_LY - 2 * TR_T, lw=LW_THIN)
    v.polyline([(X0, X0), (X0 + TR_LX, X0), (X0 + TR_LX, X0 + TR_LY), (X0, X0 + TR_LY)],
               lw=LW_HAIR, ls=(0, (3, 2)))
    for (a_, b_) in (((1, 1), (X0, X0)), ((MOD_W - 1, 1), (X0 + TR_LX, X0)),
                     ((MOD_W - 1, MOD_D - 1), (X0 + TR_LX, X0 + TR_LY)), ((1, MOD_D - 1), (X0, X0 + TR_LY))):
        v.line(a_[0], a_[1], b_[0], b_[1], lw=LW_THIN)
    for tc in TR_TABS_X:
        for yy in (1, MOD_D - 1):
            v.line(X0 + tc - 60, yy, X0 + tc + 60, yy, lw=2.4)
    for tc in TR_TABS_Y:
        for xx in (1, MOD_W - 1):
            v.line(xx, X0 + tc - 60, xx, X0 + tc + 60, lw=2.4)
    xd, yd = X0 + TR_T + DR_OFF, X0 + TR_LY - TR_T - DR_OFF
    v.circle(xd, yd, DR_D / 2, lw=LW_THICK)
    v.axis(xd - 40, yd, xd + 40, yd); v.axis(xd, yd - 40, xd, yd + 40)
    v.leader(xd, yd, 22, -7, 'слив ø18 (узел 2)', size=6)
    # уклоны к сливу
    for (p, q, t_, tx, ty) in (((1050, 300), (650, 300), 'уклон ≈0,9%', 850, 335),
                               ((1150, 160), (1150, 480), 'уклон ≈1,3%', 1230, 320)):
        A, B = v.P(*p), v.P(*q)
        ax.annotate('', xy=B, xytext=A, arrowprops=dict(arrowstyle='->', lw=0.7))
        v.text(tx, ty, t_, size=5.5, rot=0 if p[1] == q[1] else 90)
    for (x, y, hx, hy_) in ((X0, X0, 0, 0), (X0 + TR_LX, X0, TR_LX, 0),
                            (X0 + TR_LX, X0 + TR_LY, TR_LX, TR_LY), (X0, X0 + TR_LY, 0, TR_LY)):
        dx = 130 if hx == 0 else -110
        dy = 50 if hy_ == 0 else -50
        if hx == 0 and hy_ == TR_LY:
            dx, dy = 230, -50
        v.text(x + dx, y + dy, 'h=%s' % fmt(tray_h(hx, hy_)), size=5.5, weight='bold')
    v.dimx(1, MOD_W - 1, MOD_D + 60, MOD_D, MOD_D, text='1398 (по полке)')
    v.dimx(X0, X0 + TR_LX, -60, X0, X0, text='%d (по стенкам)' % TR_LX)
    v.dimy(1, MOD_D - 1, -60, 1, 1, text='698')
    v.dimy(X0, X0 + TR_LY, MOD_W + 60, X0 + TR_LX, X0 + TR_LX, left=False, text='%d' % TR_LY)
    v.dimx(X0, X0 + TR_TABS_X[0], -130, X0, X0, text='%d' % TR_TABS_X[0])
    v.text(MOD_W / 2, MOD_D + 130, 'стена', size=5.5)
    v.text(X0 + TR_TABS_X[1], 70, 'упоры 120×10 — 6 шт.', size=5)

    # ---- вид спереди
    vf = View(ax, 40, 178 - (FRAME_TOP + TR_TAB_H) * s, s)
    label(ax, 88, 184, 'ВИД СПЕРЕДИ', size=6.5)
    xl, xr = X0, X0 + TR_LX
    vf.rect(1, FRAME_TOP, MOD_W - 2, TR_T, lw=LW_THIN)
    for tc in TR_TABS_X:
        vf.rect(X0 + tc - 60, FRAME_TOP, TR_TAB_L, TR_TAB_H, lw=LW_THIN)
    vf.polyline([(xl, FRAME_TOP), (xl, zt - tray_h(0, TR_LY)), (xr, zt - tray_h(TR_LX, TR_LY)),
                 (xr, FRAME_TOP)], closed=False)
    vf.line(xl, zt - tray_h(0, 0), xr, zt - tray_h(TR_LX, 0))
    vf.rect(xd - 14, zt - tray_h(TR_T + DR_OFF, TR_LY - TR_T - DR_OFF) - 25, 28, 25, lw=LW_THIN)
    vf.dimy(zt - tray_h(0, 0), zt, -40, xl, xl, text='92')
    vf.dimy(zt - tray_h(0, TR_LY), zt, -110, xl, xl, text='100')
    vf.dimy(zt - tray_h(TR_LX, 0), zt, MOD_W + 40, xr, xr, left=False, text='80')
    vf.dimy(zt - tray_h(TR_LX, TR_LY), zt, MOD_W + 110, xr, xr, left=False, text='88')

    # ---- развёртка
    p = T.normalized()
    vw = View(ax, 212, 178, s)
    label(ax, 205, 283, 'РАЗВЁРТКА Л2 (вид с внутренней стороны) 1:10 — 1 шт.', size=7)
    vw.contour(p.outer, lw=LW_THICK)
    for cx, cy, r in p.circles:
        vw.circle(cx, cy, r, lw=LW_THIN)
    for x1, y1, x2, y2, lab in p.bends:
        vw.line(x1, y1, x2, y2, lw=LW_HAIR, ls=(0, (8, 2, 2, 2)), color='#c0392b')
    w, h = p.size()
    vw.dimx(0, w, h + 60, h, h)
    vw.dimy(0, h, -60, 0, 0)
    x0, y0, _, _ = T.bbox()
    ox, oy = -x0, -y0
    Bx, By = TR_LX - 2 * (TR_RI + TR_T), TR_LY - 2 * (TR_RI + TR_T)
    vw.dimx(ox, ox + Bx, oy + By * 0.3, None, None, text='%s (дно между Б1)' % fmt(Bx))
    vw.dimy(oy, oy + By, ox + Bx * 0.7, None, None, text=fmt(By))
    vw.text(ox + Bx / 2, oy - 45, 'ПЕРЕД  h 92 → 80', size=5)
    vw.text(ox + Bx / 2, oy + By + 45, 'ЗАД  h 100 → 88', size=5)
    vw.text(ox - 50, oy + By / 2, 'ЛЕВО  h 92 → 100', size=5, rot=90)
    vw.text(ox + Bx + 50, oy + By / 2, 'ПРАВО  h 80 → 88', size=5, rot=90)
    cx, cy, r = p.circles[0]
    vw.leader(cx, cy, 12, -9, 'ø18: %s от Б1 лев., %s от Б1 задн.' % (fmt(cx - ox), fmt(oy + By - cy)),
              size=5.5)
    vw.text(ox + Bx / 2, oy + By * 0.55, 'Б1, Б3 — на себя 90°;  Б2 — от себя 90°', size=5.5, color='#c0392b')

    # ---- узел 1 (1:1): сечение края у фронта
    z_lo = FRAME_TOP - 28
    u = View(ax, 48, 80 - z_lo, 1.0)
    label(ax, 28, 156, 'УЗЕЛ 1 — край у фронта 1:1', size=7)
    zr = FRAME_TOP - 40
    # перемычка Т2 (верхняя часть, обрыв снизу)
    u.polyline([(0, z_lo), (0, FRAME_TOP), (40, FRAME_TOP), (40, z_lo)], closed=False, lw=LW_THICK)
    u.polyline([(2, z_lo), (2, FRAME_TOP - 2), (38, FRAME_TOP - 2), (38, z_lo)], closed=False, lw=LW_HAIR)
    u.polyline([(0, z_lo), (2, z_lo), (2, FRAME_TOP - 2), (38, FRAME_TOP - 2), (38, z_lo), (40, z_lo),
                (40, FRAME_TOP), (0, FRAME_TOP)], lw=0, fill='0.6')
    zz = [(-2 + 4.4 * k, z_lo + (1.2 if k % 2 else -1.2)) for k in range(11)]
    u.polyline(zz, closed=False, lw=LW_HAIR)
    t = TR_T
    prof = [(1, FRAME_TOP + TR_TAB_H), (1, FRAME_TOP), (X0, FRAME_TOP), (X0, z_lo),
            (X0 + t, z_lo), (X0 + t, FRAME_TOP + t), (1 + t, FRAME_TOP + t),
            (1 + t, FRAME_TOP + TR_TAB_H)]
    u.polyline(prof, lw=LW_THIN, fill='#1f5fa8')
    gz = FRAME_TOP + t
    u.polyline([(GR_X0, gz), (GR_X0, TOP_Z), (62, TOP_Z), (62, TOP_Z - GR_T), (GR_X0 + GR_T, TOP_Z - GR_T),
                (GR_X0 + GR_T, gz)], lw=LW_THIN, fill='#9fb4c8')
    u.leader(20, FRAME_TOP - 15, 8, -12, 'Т2', ball=True)
    u.leader(X0 + 0.7, FRAME_TOP - 18, 9, 0, 'Л2', ball=True)
    u.leader(45, TOP_Z - 1.5, 4, 8, 'Л3', ball=True)
    u.leader(1.7, FRAME_TOP + 8, -6, 8, 'упор', size=5.5, ha='right')
    u.dimy(gz, TOP_Z, 68, 62, 62, left=False, text=fmt(GR_H))
    u.dimy(FRAME_TOP, FRAME_TOP + TR_TAB_H, -5, 1, 1, text='10')
    u.dimx(1, X0, z_lo - 6, FRAME_TOP, FRAME_TOP, text='42', above=False)
    u.dimx(40, X0, FRAME_TOP + 22, FRAME_TOP, FRAME_TOP, text='3')
    u.text(22, TOP_Z + 6, 'верх решётки = верх столешницы Б', size=5.2)
    # ---- узел 2 — слив (1:2)
    d = View(ax, 152, 92, 0.5)
    label(ax, 122, 156, 'УЗЕЛ 2 — слив 1:2', size=7)
    d.rect(-60, 100, 120, 3, lw=LW_THIN, fill='#1f5fa8')
    d.rect(-9, 100, 18, 3, lw=0, fill='white')
    d.rect(-14, 75, 28, 25, lw=LW_THICK)
    d.rect(-9, 75, 18, 25, lw=LW_HAIR, fill='0.9')
    d.rect(-16, 20, 32, 55, lw=LW_THIN)
    d.line(16, 50, 50, 50, lw=1.2)
    d.rect(-7, -15, 14, 35, lw=LW_THIN)
    d.polyline([(-6, -15), (-6, -60), (6, -60), (6, -15)], closed=False, lw=LW_THIN)
    ax.add_patch(MplPoly([d.P(-14, 100), d.P(-20, 100), d.P(-14, 94)], fc='k', zorder=4))
    ax.add_patch(MplPoly([d.P(14, 100), d.P(20, 100), d.P(14, 94)], fc='k', zorder=4))
    d.leader(40, 103, 4, 6, 'дно Л2, отв. ø18', size=5.5)
    d.leader(14, 88, 14, 2, 'полумуфта G1/2"', size=5.5)
    d.leader(16, 35, 14, 0, 'кран 1/2"', size=5.5)
    d.leader(7, 0, 14, -2, 'ёлочка', size=5.5)
    d.leader(6, -45, 14, -2, 'шланг → канистра', size=5.5)
    d.text(-42, 88, 'TIG\nкругом', size=5)

    notes(ax, 233, 150, [
        'ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ',
        '1. Резка — лазер по DXF (слой CUT). Слой BEND — линии гиба, не резать.',
        '2. Развёртка: Rвн = 1,5; K = 0,42; Б1/Б3 — на себя 90°, Б2 — от себя 90°.',
        '   Перед резкой уточнить K-фактор у гибщика, при необходимости пересчитать.',
        '3. Порядок гибки: Б3 (упоры) → Б2 (полки) → Б1 (стенки).',
        '4. Дно — плоскость с уклоном к сливу: стенки трапециевидные,',
        '   полка горизонтальна. Высоты стенок h — наружные, до верха полки.',
        '5. 4 вертикальных угла — TIG (ER308L), герметично; углы полки',
        '   (по диагонали) — проварить и зачистить. Полумуфту G1/2" вварить',
        '   снизу соосно отв. ø18, сплошной шов. Проверить водой на течь.',
        '6. После сварки — травление/пассивация швов.',
        '7. Поддон опирается полкой на раму, не крепится; съёмный.',
        '8. Объём до полки ≈ 70 л; рабочий уровень жидкости — до 50 мм.',
    ], size=5.6, dy=3.25)
    return fig


# ============================================================================
# ЛИСТ 5 — Решётки
# ============================================================================
def sheet_grates():
    fig, ax = new_sheet('Решётки Л3, Л8 (модуль А)', 5, TOTAL, '1:5, 1:20', 'AISI 304, 3 мм')
    G, Gm = grate_flat(), grate_mid_flat()
    s = 0.2
    # ---- вид сверху (одинаковый у Л3 и Л8)
    v = View(ax, 40, 131, s)
    label(ax, 30, 283, 'Л3, Л8 — вид сверху 1:5', size=7)
    v.rect(0, 0, GR_W, GR_D)
    SB = G.SB
    for hh in G.holes:
        v.contour([(x + SB, y + SB, b) for x, y, b in hh], lw=LW_HAIR)
    v.dimx(0, GR_W, GR_D + 40, GR_D, GR_D, text=fmt(GR_W))
    v.dimy(0, GR_D, -40, 0, 0)
    pf = G.perf
    v.dimy(0, pf['hy'], GR_W + 30, GR_W, GR_W / 2, left=False, text='%d' % pf['hy'])
    c0x, c0y = pf['cx0'], pf['cy0']
    v.dimx(0, c0x, -30, 0, c0y - 20, text=fmt(c0x))
    v.dimx(c0x, c0x + pf['px'], -60, c0y - 20, c0y - 20, text='18')
    v.dimy(c0y - 20, c0y + 20, GR_W + 30, None, None, text='40')
    # ---- виды спереди
    for k, (p, ttl) in enumerate(((G, 'Л3 крайняя — вид спереди'), (Gm, 'Л8 средняя — вид спереди'))):
        oy = 105 - 20 * k
        f = View(ax, 40, oy, s)
        label(ax, 40, oy + 3.5, ttl, size=5.8, weight='normal')
        f.rect(0, -GR_H, GR_W, GR_H)
        for side, deep in zip((0, 1), p.deep):
            if deep:
                x = 0 if side == 0 else GR_W - GR_T
                f.rect(x, -GR_H - GR_DEEP, GR_T, GR_DEEP, lw=LW_THIN)
        f.dimy(-GR_H, 0, -30, 0, 0, text=fmt(GR_H))
        f.dimy(-GR_H - GR_DEEP, 0, GR_W + 30, GR_W, GR_W, left=False, text=fmt(GR_H + GR_DEEP))
    # ---- развёртки
    for k, (p, ttl) in enumerate(((G, 'Развёртка Л3 — 2 шт.'), (Gm, 'Развёртка Л8 — 2 шт.'))):
        q = p.normalized()
        ox = 140 + 103 * k
        vw = View(ax, ox, 112, s)
        label(ax, ox - 5, 283, ttl, size=7)
        vw.contour(q.outer)
        for hh in q.holes:
            vw.contour(hh, lw=LW_HAIR)
        for x1, y1, x2, y2, lab in q.bends:
            vw.line(x1, y1, x2, y2, lw=LW_HAIR, ls=(0, (8, 2, 2, 2)), color='#c0392b')
        w, h = q.size()
        vw.dimx(0, w, h + 25, h, h)
        vw.dimy(0, h, -30, 0, 0)
        xl = p.Ed if p.deep[0] else p.E
        vw.dimx(xl, xl + p.Bx, -25, xl, xl, text=fmt(p.Bx))
        vw.dimy(p.E, p.E + p.By, w + 25, w - (p.Ed if p.deep[1] else p.E),
                w - (p.Ed if p.deep[1] else p.E), left=False, text=fmt(p.By))
        vw.text(w / 2, p.E / 2, 'борт %s' % fmt(p.E), size=5)
        vw.text(w / 2, h - p.E / 2, 'гибы от себя 90°', size=5, color='#c0392b')
    # ---- профиль глубокого борта
    pr = View(ax, 140, 80, s)
    label(ax, 135, 97, 'Профиль глубокого борта (Л3 — с одной стороны, Л8 — с двух) 1:5', size=6)
    y1 = GR_DEEP_Y[0] - GR_X0
    y2 = GR_DEEP_Y[1] - GR_X0
    pr.polyline([(0, 0), (GR_D, 0), (GR_D, -GR_H), (y2, -GR_H), (y2 - GR_DEEP, -GR_H - GR_DEEP),
                 (y1 + GR_DEEP, -GR_H - GR_DEEP), (y1, -GR_H), (0, -GR_H)])
    pr.dimx(0, y1, 25, 0, 0, text=fmt(y1))
    pr.dimx(y1, y1 + GR_DEEP, -GR_H - GR_DEEP - 25, -GR_H, -GR_H - GR_DEEP, text='45°×%d' % GR_DEEP,
            above=False)
    pr.dimy(-GR_H - GR_DEEP, 0, GR_D + 30, GR_D, y2, left=False, text=fmt(GR_H + GR_DEEP))
    pr.dimy(-GR_H, 0, -30, 0, 0, text=fmt(GR_H))
    # ---- раскладка решёток на модуле
    va = View(ax, 40, 24, 0.05)
    label(ax, 30, 67, 'Раскладка на модуле А 1:20', size=6.5)
    va.rect(0, 0, MOD_W, MOD_D, lw=LW_THIN)
    names = ('Л3', 'Л8', 'Л8', 'Л3↻')
    for k in range(GR_N):
        gx = GR_X0 + k * (GR_W + GR_GAP)
        va.rect(gx, GR_X0, GR_W, GR_D, fill='#e6ebf0', lw=LW_THIN)
        va.text(gx + GR_W / 2, MOD_D / 2, names[k], size=6)
    va.dimx(0, MOD_W, -90, 0, 0)
    notes(ax, 135, 58, [
        'ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ',
        '1. Резка — лазер по DXF (слой CUT); BEND — линии гиба.',
        '   Гибы бортов от себя 90°, Rвн = 3, K = 0,42.',
        '2. Л3 крайняя — 2 шт.: глубокий борт только с внутренней',
        '   стороны. Правая крайняя = та же деталь, повёрнутая на 180°.',
        '3. Л8 средняя — 2 шт.: глубокие борта с обеих сторон.',
        '4. Наружные борта 18 мм лежат на полке поддона между',
        '   упорами — верх решёток вровень со столешницей Б (950).',
        '   Глубокие борта (48) уходят внутрь поддона: дают жёсткость',
        '   (40 кг в центре — прогиб < 0,1 мм) и фиксируют решётки.',
        '5. Перфорация: пазы 6×40, шаг 18×55 шахматный — %d шт.;' % G.perf['n'],
        '   ручки 70×22 — 2 шт. Заусенцы снять, углы открытые.',
    ], size=5.6, dy=3.25)
    return fig


# ============================================================================
# ЛИСТ 6 — Столешница Б: крышка, фанера, плита
# ============================================================================
def sheet_topB():
    fig, ax = new_sheet('Столешница Б: Л1, Щ1/Щ2, плита Л7', 6, TOTAL, '1:10, 1:5, 1:1',
                        'AISI 430 1,5; Ст45 20; фанера 18')
    C = cap_flat()
    pc = C.normalized()
    vc = View(ax, 42, 190, 0.1)
    label(ax, 30, 283, 'Л1 КРЫШКА — развёртка 1:10 — 1 шт.', size=7)
    vc.contour(pc.outer)
    for cx, cy, r in pc.circles:
        vc.circle(cx, cy, 6, lw=LW_THIN)
    for x1, y1, x2, y2, lab in pc.bends:
        vc.line(x1, y1, x2, y2, lw=LW_HAIR, ls=(0, (8, 2, 2, 2)), color='#c0392b')
    w, h = pc.size()
    E = C.E
    vc.dimx(0, w, h + 50, h, h)
    vc.dimy(0, h, -50, 0, 0)
    vc.dimx(E, E + C.Bx, h * 0.6, None, None, text='%s (верх между гибами)' % fmt(C.Bx))
    vc.dimy(E, E + C.By, w * 0.3, None, None, text=fmt(C.By))
    ux, vy = E + C.uc, E + C.vc
    vc.dimx(0, ux, -40, 0, 0, text=fmt(ux))
    vc.dimy(0, vy, w + 40, w, ux, left=False, text=fmt(vy))
    vc.text(ux + (w - ux) / 2, vy / 2, 'вырез\nпод Л7', size=5.5)
    vc.text(w * 0.45, h * 0.3, 'юбка %s вниз (от себя 90°), Rвн 1,5;\n9 отв. ø4,5 в юбке' % fmt(CAP_H),
            size=5.5, color='#c0392b')

    # ---- сборка столешницы Б, вид сверху
    vt = View(ax, 42, 92, 0.1)
    label(ax, 30, 179, 'СБОРКА СТОЛЕШНИЦЫ Б — вид сверху 1:10 (крышка условно снята)', size=7)
    vt.rect(0, 0, MOD_W, MOD_D, lw=LW_THIN)
    a, b = topboards()
    for p_ in (a, b):
        q = p_.moved(*p_.pos)
        vt.contour(q.outer, lw=LW_THICK, fill='#f3e3c7')
        x0, y0, x1, y1 = q.bbox()
        vt.text((x0 + x1) / 2 - (100 if p_.code == 'Щ2' else 0), y1 - 120, p_.code, size=7,
                weight='bold')
    vt.rect(PL_X0, 0, PL_W, PL_D, lw=LW_THICK, fill='#9aa0a7')
    vt.text(PL_X0 + PL_W / 2, PL_D / 2, 'Л7', size=7, weight='bold')
    for xc in CROSS_XC:
        vt.hidden(xc - TUBE / 2, TUBE, xc - TUBE / 2, MOD_D - TUBE)
        vt.hidden(xc + TUBE / 2, TUBE, xc + TUBE / 2, MOD_D - TUBE)
    vt.hidden(T7_X0, T7_YC - TUBE / 2, T7_X0 + T7_L, T7_YC - TUBE / 2)
    vt.hidden(T7_X0, T7_YC + TUBE / 2, T7_X0 + T7_L, T7_YC + TUBE / 2)
    vt.dimx(0, SEAM_X, MOD_D + 50, MOD_D, MOD_D, text='%d (стык)' % SEAM_X)
    vt.dimx(0, PL_X0, MOD_D + 110, MOD_D, PL_D)
    vt.dimx(PL_X0, MOD_W, -50, 0, 0)
    vt.dimy(0, PL_D, MOD_W + 50, MOD_W, MOD_W, left=False)
    vt.dimy(0, MOD_D, -50, 0, 0)
    vt.text(MOD_W / 2, -110, 'перед', size=5.5)
    vt.text(300, 200, 'поперечины Т4 и Т7 — пунктиром', size=5, color='0.35')

    # ---- плита Л7
    P = vise_plate()
    vp = View(ax, 222, 205, 0.2)
    label(ax, 215, 283, 'Л7 ПЛИТА 20 мм — 1 шт. 1:5', size=7)
    vp.contour(P.outer)
    for cx, cy, r in P.circles:
        vp.circle(cx, cy, r, lw=LW_THIN)
        vp.circle(cx, cy, 10.5, lw=LW_HAIR)
    vp.polyline([(40, -15), (240, -15), (240, 160), (40, 160)], lw=LW_THIN, ls=(0, (4, 2)),
                color='#1f5fa8')
    vp.text(140, 90, 'тиски\n(пример,\nотв. М12\nпо месту)', size=5, color='#1f5fa8')
    vp.polyline([(265, 10), (440, 10), (440, 290), (265, 290)], lw=0, fill='#e8e8e8', hatch='...')
    vp.text(352, 160, 'зона\nправки', size=6, bg=True)
    vp.dimx(0, PL_W, PL_D + 25, PL_D, PL_D)
    vp.dimy(0, PL_D, -25, 0, 0)
    xs = sorted(set(x for x, y in PL_BOLTS))
    for k, x in enumerate(xs):
        vp.dimx(0, x, -20 - 25 * k, 0, 20 if x < 400 else 120)
    for k, y in enumerate(sorted(set(y for x, y in PL_BOLTS))):
        vp.dimy(0, y, PL_W + 25 + 28 * k, PL_W, 430 if y > 20 else 380, left=False)
    vp.text(PL_W / 2, PL_D + 60, '4 отв. ø11, зенковка 90°×ø21 (потай М10)', size=5.5)

    # ---- узел 3: край столешницы
    z_lo = FRAME_TOP - 14
    u = View(ax, 222, 112 - z_lo, 1.0)
    label(ax, 215, 172, 'УЗЕЛ 3 — край столешницы Б 1:1', size=7)
    u.polyline([(0, z_lo), (0, FRAME_TOP), (40, FRAME_TOP), (40, z_lo), (38, z_lo), (38, FRAME_TOP - 2),
                (2, FRAME_TOP - 2), (2, z_lo)], lw=LW_THIN, fill='0.6')
    u.rect(CAP_T + 0.5, FRAME_TOP, 66, PLY_T, lw=LW_THIN, fill='#e9cf9f', hatch='xxx')
    u.polyline([(0, FRAME_TOP), (0, TOP_Z), (70, TOP_Z), (70, TOP_Z - CAP_T), (CAP_T, TOP_Z - CAP_T),
                (CAP_T, FRAME_TOP)], lw=LW_THIN, fill='#1f5fa8')
    u.polyline([(44, FRAME_TOP + PLY_T), (46, FRAME_TOP + PLY_T - 3.5), (46, FRAME_TOP - 2),
                (48, FRAME_TOP + PLY_T - 3.5), (50, FRAME_TOP + PLY_T)], lw=LW_HAIR, fill='0.4')
    u.dimy(FRAME_TOP, TOP_Z, -5, 0, 0, text=fmt(CAP_H))
    u.dimy(FRAME_TOP, FRAME_TOP + PLY_T, 75, 68, 68, left=False, text='18')
    u.leader(0.7, FRAME_TOP + CAP_T + PLY_T / 2, -8, -7, 'саморез 4,2×16', size=5.5, ha='right')
    u.leader(47, FRAME_TOP + 6, 14, -14, 'саморез с крылышками 4,8×38', size=5.5)
    u.leader(25, TOP_Z - 0.7, 3, 6, 'Л1', ball=True)
    u.leader(20, FRAME_TOP - 8, -2, -9, 'Т2', ball=True)
    # ---- узел 5: плита на каркасе
    z5 = FRAME_TOP - 52
    w5 = View(ax, 335, 163 - (FRAME_TOP + PL_T), 1.0)
    label(ax, 318, 172, 'УЗЕЛ 5 — плита Л7 на Т2 1:1', size=7)
    w5.polyline([(0, FRAME_TOP - TUBE), (0, FRAME_TOP), (40, FRAME_TOP), (40, FRAME_TOP - TUBE),
                 (38, FRAME_TOP - TUBE), (38, FRAME_TOP - 2), (2, FRAME_TOP - 2), (2, FRAME_TOP - TUBE)],
                lw=LW_THIN, fill='0.6')
    w5.line(2, FRAME_TOP - TUBE + 2, 38, FRAME_TOP - TUBE + 2, lw=LW_THIN)
    w5.rect(0, FRAME_TOP - TUBE, 40, 2, lw=LW_THIN, fill='0.6')
    w5.polyline([(0, FRAME_TOP), (60, FRAME_TOP), (60, FRAME_TOP + PL_T), (0, FRAME_TOP + PL_T)],
                lw=LW_THIN, fill='#9aa0a7')
    by = 20
    zt5 = FRAME_TOP + PL_T
    w5.polyline([(by - 10.5, zt5), (by + 10.5, zt5), (by + 5, zt5 - 5.5), (by + 5, FRAME_TOP - TUBE - 18),
                 (by - 5, FRAME_TOP - TUBE - 18), (by - 5, zt5 - 5.5)], lw=LW_THIN, fill='#5d6168')
    w5.rect(by - 10, FRAME_TOP - TUBE - 2.5, 20, 2.5, lw=LW_THIN, fill='0.8')
    w5.rect(by - 8.5, FRAME_TOP - TUBE - 11, 17, 8.5, lw=LW_THIN, fill='0.8')
    w5.dimy(FRAME_TOP, zt5, 66, 60, 60, left=False, text='20')
    w5.dimy(FRAME_TOP - TUBE, FRAME_TOP, -6, 0, 0, text='40')
    w5.leader(45, zt5 - 4, 6, 8, 'Л7', ball=True)
    w5.leader(38, FRAME_TOP - 25, 14, -4, 'Т2', ball=True)
    w5.leader(by + 5, FRAME_TOP - 15, 24, 4, 'М10×80 DIN 7991', size=5.5)
    w5.leader(by + 8, FRAME_TOP - TUBE - 7, 18, -2, 'шайба + гайка М10', size=5.5)

    notes(ax, 215, 84, [
        'ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ',
        '1. Каркас Б → плита Л7 (4 болта М10 потай) → фанера Щ1, Щ2 (саморезы',
        '   с крылышками 4,8×38 через фанеру в трубы, головки утопить) →',
        '   крышка Л1 на МС-полимер + 9 саморезов 4,2×16 через юбку.',
        '2. Стык Щ1/Щ2 — на оси средней поперечины, по 20 мм опоры каждой.',
        '3. Верх Л7 выше крышки на %.1f мм — специально (кромка крышки' % (FRAME_TOP + PL_T - TOP_Z),
        '   не цепляется). Зазор плита—фанера/крышка 1 мм.',
        '4. Л7: лазер/плазма; лучше Ст45 (твёрже под правку). Верх —',
        '   прошлифовать. Отв. под тиски: сверлить ø10,2 и нарезать М12.',
        '5. Л1: гибы от себя 90°, Rвн 1,5, K 0,42. Углы юбки — прихватить TIG',
        '   и зашлифовать. Плёнку снять после монтажа.',
    ], size=5.6, dy=3.25)
    return fig


# ============================================================================
# ЛИСТ 7 — Полка и мелкие детали
# ============================================================================
def sheet_small():
    fig, ax = new_sheet('Полка Л4, детали Л5, Л6', 7, TOTAL, '1:10, 1:1, 1:2',
                        'Ст 08пс 1,5; Ст3 4 мм')
    S = shelf_flat()
    p = S.normalized()
    v = View(ax, 45, 175, 0.1)
    label(ax, 35, 283, 'Л4 ПОЛКА НИЖНЯЯ (модуль А) — развёртка 1:10 — 1 шт.', size=7)
    v.contour(p.outer)
    for x1, y1, x2, y2, lab in p.bends:
        v.line(x1, y1, x2, y2, lw=LW_HAIR, ls=(0, (8, 2, 2, 2)), color='#c0392b')
    w, h = p.size()
    v.dimx(0, w, h + 50, h, h)
    v.dimy(0, h, -50, 0, 0)
    E = SH_LIP - (SH_RI + SH_T) + S.BA
    n = SH_NOTCH - (SH_RI + SH_T)
    v.dimx(0, E + n, -40, E, E, text=fmt(E + n))
    v.dimy(0, E + n, w + 40, w - E - n, w - E - n, left=False, text=fmt(E + n))
    v.text(w / 2, h / 2, 'борт 20 вверх (на себя 90°), Rвн 1,5\nвырезы 40×40 под ноги', size=6)
    # вид собранной полки
    vv = View(ax, 45, 140, 0.1)
    vv.polyline([(0, SH_LIP), (0, 0), (SH_W, 0), (SH_W, SH_LIP)], closed=False)
    vv.dimx(0, SH_W, -40, 0, 0)
    vv.dimy(0, SH_LIP, -40, 0, 0, text='20')
    label(ax, 45, 152, 'Вид спереди (после гибки)', size=6, weight='normal')

    # Л5
    a = View(ax, 230, 230, 1.0)
    label(ax, 225, 283, 'Л5 ПОДПЯТНИК — 8 шт. 1:1 (4 мм)', size=7)
    a.contour(foot_plate().outer)
    a.circle(20, 20, 6.5, lw=LW_THICK)
    a.axis(-5, 20, 45, 20); a.axis(20, -5, 20, 45)
    a.dimx(0, 40, 48, 40, 40); a.dimy(0, 40, -6, 0, 0)
    a.leader(24.6, 24.6, 10, 10, 'ø13', size=6)
    a2 = View(ax, 290, 230, 1.0)
    a2.rect(0, 0, 40, 4, fill='0.7'); a2.rect(11, 4, 18, 10, lw=LW_THIN)
    a2.rect(14, -20, 12, 20, lw=LW_HAIR, ls=(0, (3, 2)))
    a2.text(20, 22, 'гайка М12 — приварить\nсверху, соосно', size=5.5)
    a2.text(20, -25, 'опора М12', size=5.5, va='top')
    # Л6
    g = View(ax, 345, 220, 0.5)
    label(ax, 340, 283, 'Л6 КОСЫНКА — 2 шт. 1:2 (4 мм)', size=7)
    g.contour(gusset().outer)
    g.dimx(0, 100, -14, 0, 0); g.dimy(0, 100, -14, 0, 0)
    g.dimx(0, 12, 112, 100, 100, text='12')
    g.text(55, 55, '', size=5)
    notes(ax, 233, 190, [
        'Л4 — после гибки грунт + краска в цвет каркаса.',
        'Ставится на нижние перемычки модуля А,',
        'вырезы 40×40 охватывают ноги. Борт 20 держит',
        'канистру и пролитое масло.',
        '',
        'Л5 — 8 шт. (по одной на каждую ногу), гайку',
        'М12 приварить до приварки Л5 к ноге.',
        'Л6 — 2 шт., только модуль Б (передние углы).',
    ], size=5.8, dy=3.3)
    notes(ax, 40, 120, [
        'ОБЩИЕ УКАЗАНИЯ ПО ЛИСТОВЫМ ДЕТАЛЯМ',
        '— Резка: лазер, по DXF (папка DXF_laser). Слой CUT — рез, слой BEND — линии',
        '  гиба (кернить/не резать). Масштаб DXF 1:1, мм.',
        '— Развёртки посчитаны при K = 0,42 и Rвн = t. Если у гибщика другой инструмент —',
        '  пусть пересчитает по своим таблицам, внешние размеры деталей — на листах 4–7.',
        '— Острые кромки притупить. Нержавейку гнуть в плёнке.',
        '— Количество — в спецификации (лист 8) и в имени файла DXF.',
    ], size=5.8, dy=3.4)
    return fig


# ============================================================================
# ЛИСТ 8 — Спецификация
# ============================================================================
def sheet_spec(hardware):
    fig, ax = new_sheet('Спецификация, карта резки', 8, TOTAL, '—', '—')
    label(ax, 25, 287, '1. ПРОФИЛЬНАЯ ТРУБА — нарезать (торцы 90°)', size=7.5)
    rows = [(t.code, t.name, t.profile, fmt(t.L), t.qty, t.mods, t.note) for t in tubes()]
    yb = table(ax, 25, 283, ['Поз.', 'Наименование', 'Профиль', 'L, мм', 'Кол.', 'Модуль', 'Обработка'],
               rows, [10, 52, 18, 13, 10, 13, 84], fs=5.4)
    # карта резки
    label(ax, 25, yb - 5, 'КАРТА РЕЗКИ ХЛЫСТОВ 6000 мм (рез 3 мм)', size=7.5)
    y = yb - 12
    for prof in ('40х40х2', '40х20х2'):
        pieces = []
        for t in tubes():
            if t.profile == prof:
                pieces += [(t.code, t.L)] * t.qty
        st = cut_sticks(pieces)
        for k, stick in enumerate(st):
            ax.text(25, y + 1.5, '%s №%d' % (prof, k + 1), fontsize=5.6, va='center')
            x = 50
            sc = 160 / 6000
            ax.add_patch(Rectangle((x, y - 1), 6000 * sc, 5, fc='0.93', ec='k', lw=LW_THIN))
            cx = x
            for code, L in stick:
                ax.add_patch(Rectangle((cx, y - 1), L * sc, 5, fc='#cfe0f1', ec='k', lw=LW_THIN))
                ax.text(cx + L * sc / 2, y + 1.5, '%s %s' % (code, fmt(L)), fontsize=4.6,
                        ha='center', va='center')
                cx += (L + 3) * sc
            used = sum(L for _, L in stick) + 3 * len(stick)
            ax.text(x + 6000 * sc + 2, y + 1.5, 'ост. %d' % (6000 - used), fontsize=5, va='center')
            y -= 7.5
    y -= 2
    label(ax, 25, y, '2. ЛИСТОВЫЕ ДЕТАЛИ — лазер + гибка (DXF_laser)', size=7.5)
    rows = []
    from outputs import translit, metal_parts
    for p in metal_parts():
        w, h = p.size()
        nb = len(p.bends)
        rows.append((p.code, p.name, p.material, fmt(p.t), p.qty, '%s×%s' % (fmt(w), fmt(h)),
                     nb if nb else '—', translit(p.code) + '_*.dxf'))
    yb = table(ax, 25, y - 4, ['Поз.', 'Наименование', 'Материал', 't', 'Кол.', 'Развёртка', 'Гибов',
                               'Файл'], rows, [10, 42, 34, 8, 9, 27, 11, 59], fs=5.4)
    notes(ax, 25, yb - 3, [
        'В цех: каркасы — листы 2, 3; поддон — 4; решётки — 5; столешница Б и плита — 6; полка, мелочь — 7.',
    ], size=5.6)
    label(ax, 25, yb - 12, '4. ПОРЯДОК РАБОТ', size=7.5)
    notes(ax, 25, yb - 16, [
        '1. Замерить гараж (ширина у задней стены, высота, ровность пола). При необходимости — MOD_W в geom.py.',
        '2. Лазер + гибка: отдать DXF_laser/*.dxf (кроме NEST_*) + листы 4–7. Проверить первую деталь по размерам.',
        '3. Трубы: нарезать по карте резки, просверлить ноги Т1 (ø9 на 250 и 650).',
        '4. Сварить 2 каркаса на ровной плите (листы 2, 3), приварить Л5 с гайками, Л6. Зачистить верх под плиту.',
        '5. Положить плиту Л7, просверлить через неё 4 отв. ø11 в Т2/Т3, болты М10. Покрасить каркасы.',
        '6. Поддон: TIG-сварка углов, вварить полумуфту, проверить водой. Пассивация.',
        '7. ЧПУ фанеры: DXF_cnc_fanera/NEST_fanera_list1..2.dxf. Щ1/Щ2 — на саморезы, сверху крышка Л1.',
        '8. Установка: модули к стене, опорами в уровень, стянуть болтами М8. Поддон, решётки, полка, слив.',
        '9. Стена: рейки Р1 вертикально по отвесу → панели П1 → держатели А1–А3 на шкантах.',
    ], size=5.6, dy=3.4)
    # покупное
    label(ax, 233, 287, '3. ПОКУПНЫЕ ИЗДЕЛИЯ И МЕТИЗЫ', size=7.5)
    yb = table(ax, 233, 283, ['Наименование', 'Кол.', 'Где'], hardware, [118, 18, 46], fs=5.3, rh=4.25)
    return fig


# ============================================================================
# ЛИСТ 8 — Стеновые панели
# ============================================================================
def sheet_panels():
    fig, ax = new_sheet('Стеновая панель П1, рейка Р1, держатели', 9, TOTAL, '1:10, 1:2, 1:5',
                        'Фанера берёзовая ФК 18 мм')
    P = panel()
    v = View(ax, 40, 148, 0.1)
    label(ax, 35, 283, 'П1 ПАНЕЛЬ — %d шт. 1:10 (вид спереди)' % PN_N, size=7)
    v.rect(0, 0, PN_W, PN_H)
    for xc in BT_XC:
        v.polyline([(xc - BT_W / 2, BT_Y0), (xc + BT_W / 2, BT_Y0), (xc + BT_W / 2, BT_Y0 + BT_L),
                    (xc - BT_W / 2, BT_Y0 + BT_L)], lw=LW_THIN, ls=(0, (4, 2)), color='#a05a00')
    for cx, cy, r in P.drills:
        if r == PN_HOLE / 2:
            v.circle(cx, cy, 4, lw=0.2)
        else:
            v.circle(cx, cy, 7, lw=0.5, color='#c0392b')
    v.dimx(0, PN_W, PN_H + 50, PN_H, PN_H)
    v.dimy(0, PN_H, -50, 0, 0)
    v.dimx(0, 50, -40, 0, 50, text='50')
    v.dimx(50, 100, -40, 50, 50, text='50')
    v.dimy(0, 50, PN_W + 40, PN_W, PN_W - 50, left=False, text='50')
    for k, x in enumerate(PN_MOUNT_X):
        v.dimx(0, x, -100 - k * 60, 0, 75)
    for k, y in enumerate(PN_MOUNT_Y):
        v.dimy(0, y, PN_W + 110 + k * 55, PN_W, PN_W - 75, left=False)
    v.leader(PN_MOUNT_X[1], PN_MOUNT_Y[2], 12, 12, '12 отв. ø5 + зенковка (крепёж к рейкам)', size=5.5)
    v.leader(PN_W - 50, PN_H - 50, 8, 12, '%d отв. ø8 сетка 50×50' % (P.grid[0] * P.grid[1]), size=5.5)
    v.text(BT_XC[1] + 60, PN_H / 2, 'рейка Р1 (сзади)', size=5, color='#a05a00', rot=90)

    vb = View(ax, 40, 88, 0.1)
    label(ax, 35, 112, 'Р1 РЕЙКА-ОТСТУП (ставится вертикально) — %d шт. 1:10' % (3 * PN_N), size=7)
    B = batten()
    vb.rect(0, 0, BT_L, BT_W)
    for cx, cy, r in B.drills:
        vb.circle(cx, cy, 6, lw=LW_THIN)
    vb.dimx(0, BT_L, -40, 0, 0)
    vb.dimy(0, BT_W, BT_L + 40, BT_L, BT_L, left=False, text='70')
    for k, x in enumerate(BT_ANCHOR):
        vb.dimx(0, x, -90 - k * 45, 0, BT_W / 2)
    vb.text(BT_L / 2, BT_W + 35, '3 отв. ø6 + зенковка — дюбель-гвоздь/анкер 6×60 в стену', size=5.5)

    # разрез монтажа 1:2
    m = View(ax, 232, 160, 0.5)
    label(ax, 215, 283, 'УЗЕЛ 4 — монтаж 1:2', size=7)
    m.polyline([(-30, -40), (0, -40), (0, 210), (-30, 210)], lw=0, fill='0.85', hatch=HATCH)
    m.line(0, -40, 0, 210, lw=LW_THICK)
    m.rect(0, -40, PLY_T, 250, fill='#d9b77d', lw=LW_THIN)
    m.rect(PLY_T, -40, PLY_T, 250, fill='#f3e3c7', lw=LW_THICK)
    m.rect(-25, 30, 25 + 9, 8, lw=LW_HAIR, fill='0.5')
    m.rect(PLY_T, 55 + 2.5, 2 * PLY_T - PLY_T, 0, lw=LW_HAIR)
    m.polyline([(2 * PLY_T, 55 + 4), (PLY_T - 12, 55 + 2), (PLY_T - 12, 55 - 2), (2 * PLY_T, 55 - 4)],
               lw=LW_HAIR, fill='0.5')
    for zc in (150, 100):
        m.rect(2 * PLY_T - 18, zc - 4, 40, 8, fill='#e6c58c', lw=LW_THIN)
    m.leader(PLY_T / 2, 20, 12, -10, 'Р1', ball=True)
    m.leader(PLY_T * 1.5, 190, 10, 6, 'П1', ball=True)
    m.leader(-10, 34, -4, -14, 'дюбель 6×60', size=5.5, ha='right')
    m.leader(PLY_T + 5, 55, 12, -6, 'саморез 4,5×35', size=5.5)
    m.leader(2 * PLY_T + 15, 150, 6, 6, 'шкант ø8×40', size=5.5)
    m.text(-15, -55, 'стена', size=5.5)
    m.dimx(0, PLY_T, 225, 0, PLY_T, text='18')
    m.dimx(PLY_T, 2 * PLY_T, 225, PLY_T, 2 * PLY_T, text='18')

    # держатели 1:5
    s = 0.2
    def acc_view(ox, oy, title, L, depth, kind):
        label(ax, ox, oy + 30, title, size=6.5)
        f = View(ax, ox, oy, s)
        # вид сбоку (сборка)
        f.rect(0, 0, PLY_T, 90, fill='#e9cf9f', lw=LW_THIN)
        f.rect(PLY_T, 72, depth, PLY_T, fill='#e9cf9f', lw=LW_THIN)
        f.polyline([(PLY_T, 72), (PLY_T, 2), (PLY_T + depth - 10, 72)], lw=LW_THIN, fill='#f3e3c7')
        if kind == 'A3':
            f.rect(PLY_T + depth, 72, PLY_T, 40, fill='#e9cf9f', lw=LW_THIN)
        for zz in (15, 65):
            f.rect(-22, zz - 4, 40, 8, lw=LW_HAIR, fill='#c9a46a')
        f.dimy(0, 90, -40, 0, 0, text='90')
        f.dimx(PLY_T, PLY_T + depth, 105, PLY_T, PLY_T + depth, text=fmt(depth))
        # вид сверху полки
        t = View(ax, ox + 30, oy, s)
        t.rect(0, 0, L, depth, lw=LW_THICK)
        if kind == 'A1':
            for i in range(9):
                t.circle(30 + 30 * i, depth - 30, 6, lw=LW_THIN)
            t.text(L / 2, -25, '9 отв. ø12 шаг 30', size=5)
        elif kind == 'A2':
            n, pitch = 11, 33
            for i in range(n):
                x = L / 2 - (n - 1) * pitch / 2 + i * pitch
                t.rect(x - 4, 0, 8, 45, lw=LW_THIN)
            t.text(L / 2, -25, '11 пазов 8×45 шаг 33 (к краю)', size=5)
        else:
            t.text(L / 2, -25, 'полка + бортик 40', size=5)
        t.dimx(0, L, depth + 25, depth, depth)
    acc_view(300, 238, 'А1 — ОТВЁРТОЧНИЦА 1:5', 300, 80, 'A1')
    acc_view(300, 190, 'А2 — КЛЮЧНИЦА 1:5', 400, 70, 'A2')
    acc_view(300, 140, 'А3 — ПОЛКА (масла, баллоны) 1:5', 400, 90, 'A3')
    notes(ax, 233, 118, [
        'МОНТАЖ И ИСПОЛЬЗОВАНИЕ',
        '1. Рейки Р1 — вертикально, по отвесу: оси на %s от левого края' % ', '.join(str(x) for x in BT_XC),
        '   панели, низ рейки на %d выше низа панели (низ панели — %d от пола).' % (BT_Y0, PN_Z0),
        '   Каждая рейка — 3 дюбеля 6×60.',
        '2. Панель П1 — 12 саморезов 4,5×35 в рейки. Зазор за панелью 18 мм.',
        '3. В сетку ø8 вставляются мебельные шканты 8×40 — как крючки (с наклоном',
        '   вверх) или как фиксаторы держателей. Держатели А1–А3: в задней',
        '   планке 4 шканта на клею, вставляются в любое место сетки.',
        '4. Тяжёлое (колёса, шлемы) — крюки на саморезах 5×50 сквозь панель в рейку.',
        '5. Отделка: шлифовать, 2 слоя лака/масла (стойкость к маслу и бензину).',
    ], size=5.6, dy=3.3)
    return fig


# ============================================================================
# ЛИСТ 10 — Раскрой фанеры
# ============================================================================
def sheet_ply_nest(sheets):
    fig, ax = new_sheet('Раскрой фанеры (ЧПУ-фрезер)', 10, TOTAL, '1:16',
                        'Фанера берёзовая ФК 18 мм, %d×%d' % (PLY_SW, PLY_SH))
    s = 1 / 16
    colors = {'П1': '#f3e3c7', 'Р1': '#e3c48f', 'Щ1': '#e9d7b4', 'Щ2': '#e9d7b4'}
    for k, (name, L) in enumerate(sheets):
        ox = 30 + k * 190
        v = View(ax, ox, 185, s)
        label(ax, ox, 185 + PLY_SH * s + 6, name, size=6.5)
        v.rect(0, 0, PLY_SW, PLY_SH, lw=LW_THIN, fill='#fbfbfb')
        for p in L:
            v.contour(p.outer, lw=LW_THIN, fill=colors.get(p.code, '#f0d9ae'))
            for hh in p.holes:
                v.contour(hh, lw=LW_HAIR)
            if p.code == 'П1':
                xs, ys = [], []
                for cx, cy, r in p.drills:
                    X, Y = v.P(cx, cy); xs.append(X); ys.append(Y)
                ax.scatter(xs, ys, s=0.06, c='0.35', linewidths=0, zorder=4)
            else:
                for cx, cy, r in p.drills:
                    v.circle(cx, cy, max(r, 8), lw=LW_HAIR)
            x0, y0, x1, y1 = p.bbox()
            big = (x1 - x0) > 300 and (y1 - y0) > 300
            vert = (y1 - y0) > (x1 - x0) and not big
            lx, ly = (x0 + x1) / 2, (y0 + y1) / 2
            if p.code == 'Р1':
                ly = y0 + (y1 - y0) * 0.25
            v.text(lx, ly, p.code, size=7 if big else 4.2, rot=90 if vert else 0,
                   weight='bold' if big else 'normal', bg=p.code == 'Р1')
        v.dimx(0, PLY_SW, -70, 0, 0)
        v.dimy(0, PLY_SH, -70, 0, 0)
    rows = []
    for p in ply_parts_list():
        w, h = p.size()
        nd = len(p.drills)
        rows.append((p.code, p.name, p.qty, '%s×%s' % (fmt(w), fmt(h)), nd if nd else '—',
                     'лист 6' if p.code[0] == 'Щ' else 'лист 9'))
    label(ax, 25, 170, 'ДЕТАЛИ ИЗ ФАНЕРЫ 18 мм', size=7.5)
    table(ax, 25, 166, ['Поз.', 'Наименование', 'Кол.', 'Размер', 'Отв.', 'Чертёж'], rows,
          [13, 58, 10, 26, 12, 22], fs=5.4)
    notes(ax, 233, 170, [
        'ДЛЯ ЦЕХА ЧПУ (файлы в папке DXF_cnc_fanera):',
        '— NEST_fanera_list1..2.dxf — готовые раскладки на лист %d×%d.' % (PLY_SW, PLY_SH),
        '— Слои: CUT — контур, фреза ø6 снаружи; CUT_INSIDE — внутр.',
        '  контуры/пазы, фреза внутри; DRILL_D8 / D6 / D5 — сверлить',
        '  насквозь указанным диаметром; SHEET, TEXT — не обрабатывать.',
        '— Зазор между деталями 12 мм, отступ от края 10 мм.',
        '  Панель 1400×1200 встаёт в высоту листа 1220 впритык (по 10 мм).',
        '— Лазер для фанеры 18 мм не подходит (обугливание) — только фрезер.',
        '— Столешница Б из двух частей Щ1 + Щ2: стык на средней поперечине,',
        '  под крышкой не виден. Так вся фанера — 2 листа вместо 3.',
        '— Свободные места на листах — запас под дополнительные держатели.',
    ], size=5.7, dy=3.4)
    return fig


def ply_parts_list():
    from outputs import ply_parts
    return ply_parts()


# ============================================================================
# ЛИСТ 11 — Раскрой металла
# ============================================================================
def sheet_metal_nest(nest):
    fig, ax = new_sheet('Раскрой листового металла (справочно)', 11, TOTAL, '1:25 / 1:5',
                        'см. таблицу')
    s = 1 / 25
    pos = [(28, 225), (118, 225), (208, 225), (298, 225), (25, 150), (125, 128)]
    for k, sh in enumerate(nest):
        ox, oy = pos[k]
        sc = s if sh['w'] >= 1000 else 1 / 5
        v = View(ax, ox, oy, sc)
        label(ax, ox, oy + sh['h'] * sc + 6, sh['title'], size=6)
        v.rect(0, 0, sh['w'], sh['h'], lw=LW_THIN, fill='#fbfbfb')
        for p in sh['parts']:
            v.contour(p.outer, lw=LW_THIN, fill='#dfe6ec')
            for hh in p.holes:
                v.contour(hh, lw=0.15)
            for cx, cy, r in p.circles:
                v.circle(cx, cy, r, lw=0.2)
            for x1, y1, x2, y2, lab in p.bends:
                v.line(x1, y1, x2, y2, lw=0.2, ls=(0, (3, 1)), color='#c0392b')
            x0, y0, x1, y1 = p.bbox()
            v.text((x0 + x1) / 2, (y0 + y1) / 2, p.code, size=6.5 if sc < 0.1 else 5, weight='bold')
        v.dimx(0, sh['w'], -150 if sc < 0.1 else -25, 0, 0)
        v.dimy(0, sh['h'], -120 if sc < 0.1 else -20, 0, 0)
    notes(ax, 233, 140, [
        'ПРИМЕЧАНИЯ',
        '— Раскладка справочная: цех обычно раскладывает сам по своим листам.',
        '  Отдаёте файлы деталей из DXF_laser + таблицу кол-ва (лист 8).',
        '— Готовые раскладки: DXF_laser/NEST_*.dxf (граница листа — слой SHEET).',
        '— Л5/Л6 — из обрезка Ст3 4 мм. Л7 — плита 20 мм: лазер или плазма,',
        '  можно купить готовую заготовку 450×300 и просверлить.',
        '— Нержавейку AISI 304 для поддона и решёток не заменять на чёрную',
        '  сталь — бензин/промывка/вода. Крышку Л1 можно из AISI 304 или',
        '  оцинковки 1,5 (тогда та же развёртка).',
        '— Л4 можно заменить фанерой 18 мм 1396×696 с вырезами 40×40.',
    ], size=5.7, dy=3.4)
    return fig
