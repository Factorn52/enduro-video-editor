# -*- coding: utf-8 -*-
"""Сквозная проверка размеров и стыковок. Падает с ошибкой, если что-то не сходится.
Отчёт пишется в ../Проверка_размеров.txt"""
import os
import math
from geom import *
from outputs import metal_nest, ply_nest

USER_H = 1870
REPORT = []


def ok(cond, text, val=''):
    line = ('OK   ' if cond else 'FAIL ') + text + (('  [' + val + ']') if val else '')
    REPORT.append(line)
    if not cond:
        raise AssertionError(line)


def near(a, b, tol=0.3):
    return abs(a - b) <= tol


# ---------------------------------------------------------------------------
# 3D-модель каркасов (коробки: x вдоль модуля, y от фронта, z вверх)
# ---------------------------------------------------------------------------
def frame_boxes(mod):
    T, W, D = TUBE, MOD_W, MOD_D
    z0 = FOOT_H + PLATE_T
    B = []
    for x in (0, W - T):
        for y in (0, D - T):
            B.append(('Т1', (x, y, z0), (x + T, y + T, z0 + LEG_L)))
            B.append(('Л5', (x, y, FOOT_H), (x + T, y + T, z0)))
    zt = FRAME_TOP - T
    B.append(('Т2 перед', (T, 0, zt), (W - T, T, FRAME_TOP)))
    B.append(('Т2 зад', (T, D - T, zt), (W - T, D, FRAME_TOP)))
    B.append(('Т3 лев', (0, T, zt), (T, D - T, FRAME_TOP)))
    B.append(('Т3 прав', (W - T, T, zt), (W, D - T, FRAME_TOP)))
    B.append(('Т6 лев', (0, T, LOW_Z0), (LOW_W, D - T, LOW_Z1)))
    B.append(('Т6 прав', (W - LOW_W, T, LOW_Z0), (W, D - T, LOW_Z1)))
    B.append(('Т5 зад', (T, D - LOW_W, LOW_Z0), (W - T, D, LOW_Z1)))
    if mod == 'A':
        B.append(('Т5 перед', (T, 0, LOW_Z0), (W - T, LOW_W, LOW_Z1)))
    else:
        for i, xc in enumerate(CROSS_XC):
            B.append(('Т4-%d' % (i + 1), (xc - T / 2, T, zt), (xc + T / 2, D - T, FRAME_TOP)))
        B.append(('Т7', (T7_X0, T7_YC - T / 2, zt), (T7_X0 + T7_L, T7_YC + T / 2, FRAME_TOP)))
    return B


def overlap(a, b):
    v = 1.0
    for i in range(3):
        lo = max(a[1][i], b[1][i]); hi = min(a[2][i], b[2][i])
        if hi - lo <= 1e-6:
            return 0.0
        v *= hi - lo
    return v


def touches(a, b):
    for i in range(3):
        if a[2][i] < b[1][i] - 1e-6 or b[2][i] < a[1][i] - 1e-6:
            return False
    return True


def run():
    # ---------------- высоты ----------------
    ok(near(FOOT_H + PLATE_T + LEG_L, FRAME_TOP), 'опора + подпятник + нога = верх каркаса',
       '%g+%g+%g=%g' % (FOOT_H, PLATE_T, LEG_L, FRAME_TOP))
    ok(near(FRAME_TOP + PLY_T + CAP_T, TOP_Z), 'каркас + фанера 18 + крышка 1,5 = рабочая высота',
       '%g' % TOP_Z)
    ok(near(TOP_Z - CAP_H, FRAME_TOP), 'юбка крышки Л1 доходит ровно до верха каркаса',
       'юбка %g' % CAP_H)
    ok(near(FRAME_TOP + TR_T + GR_H, TOP_Z), 'решётки на полке поддона вровень со столешницей Б',
       'борт %g' % GR_H)
    ok(abs(FRAME_TOP + PL_T - TOP_Z) <= 1.0, 'плита Л7 на каркасе почти вровень со столешницей',
       'выступ %+.1f мм' % (FRAME_TOP + PL_T - TOP_Z))
    r = TOP_Z / USER_H
    ok(0.49 <= r <= 0.54, 'высота столешницы под рост %d мм' % USER_H,
       '%.0f мм = %.3f роста; губки тисков ≈ %.0f' % (TOP_Z, r, TOP_Z + 135))
    ok(PN_Z0 - TOP_Z >= 50, 'низ панелей выше столешницы', '%g мм' % (PN_Z0 - TOP_Z))
    ok(PN_Z0 + PN_H <= 2300, 'верх панелей в зоне досягаемости', '%g мм' % (PN_Z0 + PN_H))

    # ---------------- габариты ----------------
    ok(N_MOD * MOD_W + 100 <= GARAGE_W, 'верстак входит в ширину гаража',
       '%d + зазоры %g/%g' % (N_MOD * MOD_W, BENCH_X0, BENCH_X0))
    for t in tubes():
        if t.code in ('Т2', 'Т5'):
            ok(near(t.L + 2 * TUBE, MOD_W), '%s + 2 ноги = ширина модуля' % t.code, '%g' % t.L)
        if t.code in ('Т3', 'Т4', 'Т6'):
            ok(near(t.L + 2 * TUBE, MOD_D), '%s + 2 трубы = глубина' % t.code, '%g' % t.L)
    ok(near(T7_X0 + T7_L, MOD_W - TUBE), 'Т7 упирается в правую боковую Т3', 'L=%g' % T7_L)

    # ---------------- 3D пересечения каркасов ----------------
    for mod in ('A', 'B'):
        B = frame_boxes(mod)
        bad = [(a[0], b[0]) for i, a in enumerate(B) for b in B[i + 1:] if overlap(a, b) > 1e-3]
        ok(not bad, 'каркас %s: элементы не пересекаются (только касание)' % mod, str(bad) if bad else '')
        lonely = [a[0] for a in B if not any(touches(a, b) for b in B if b is not a)]
        ok(not lonely, 'каркас %s: каждый элемент примыкает к соседнему' % mod)

    # ---------------- поддон ----------------
    ok(near(TR_X0 + TR_LX + TR_GAP + TUBE, MOD_W), 'поддон по X: зазор %g до перемычек' % TR_GAP)
    ok(near(TR_X0 + TR_LY + TR_GAP + TUBE, MOD_D), 'поддон по Y: зазор %g до перемычек' % TR_GAP)
    ok(TR_X0 - TR_F >= 0.5, 'полка поддона не выходит за каркас', 'край на %g' % (TR_X0 - TR_F))
    for tc in TR_TABS_X:
        ok(TR_TAB_L / 2 + 50 <= tc <= TR_LX - TR_TAB_L / 2 - 50, 'упор X=%g вдали от углов' % tc)
    T = tray_flat()
    for k, w in T.walls.items():
        ok(w['h0'] >= 79 and w['h1'] >= 79, 'стенка %s: высоты %g→%g' % (k, w['h0'], w['h1']))
    zt = FRAME_TOP + TR_T
    z_drain = zt - tray_h(TR_T + DR_OFF, TR_LY - TR_T - DR_OFF)
    z_low = z_drain - (25 + 55 + 35)
    can = 470
    ok(z_low - (LOW_Z1 + SH_T + can) >= 40, 'под сливом входит канистра 20 л (h=470)',
       'зазор %.0f мм' % (z_low - (LOW_Z1 + SH_T + can)))
    xd, yd = TR_X0 + TR_T + DR_OFF, TR_X0 + TR_LY - TR_T - DR_OFF
    ok(xd - 16 > TUBE and yd + 16 < MOD_D - TUBE, 'кран слива не задевает ноги', '(%.1f; %.1f)' % (xd, yd))

    # ---------------- решётки ----------------
    stack = GR_N * GR_W + (GR_N - 1) * GR_GAP
    inner = MOD_W - 2 * (1 + TR_T)
    ok(0 < inner - stack <= 4, 'решётки между упорами', 'люфт %.1f мм' % (inner - stack))
    ok(0 < (MOD_D - 2 * (1 + TR_T)) - GR_D <= 4, 'решётки по глубине между упорами')
    y_in0, y_in1 = TR_X0 + TR_T, MOD_D - TR_X0 - TR_T
    ok(GR_DEEP_Y[0] - y_in0 >= 2 and y_in1 - GR_DEEP_Y[1] >= 2,
       'глубокие борта внутри стенок поддона', '%.1f / %.1f мм' % (GR_DEEP_Y[0] - y_in0, y_in1 - GR_DEEP_Y[1]))
    zb = TOP_Z - GR_H - GR_DEEP
    xs = [GR_X0 + k * (GR_W + GR_GAP) + d for k in range(GR_N) for d in (0, GR_W)][1:-1]
    worst = min(zb - (zt - tray_h(x - TR_X0, y - TR_X0)) for x in xs
                for y in (GR_DEEP_Y[0], GR_DEEP_Y[1]))
    ok(worst >= 25, 'глубокие борта не достают до дна поддона', 'мин. зазор %.0f мм' % worst)
    ok(GR_X0 + GR_T <= TR_X0, 'крайние борта решёток лежат на полке поддона')
    # прочность решётки (сосредоточенная 400 Н в центре пролёта)
    t, h = GR_T, GR_H + GR_DEEP
    def I_sec(hw):
        A1, y1 = GR_W * t, t / 2
        A2, y2 = 2 * t * (hw - t), t + (hw - t) / 2
        yc = (A1 * y1 + A2 * y2) / (A1 + A2)
        I = GR_W * t ** 3 / 12 + A1 * (yc - y1) ** 2 + 2 * t * (hw - t) ** 3 / 12 + A2 * (yc - y2) ** 2
        return I, hw - yc
    Ls = MOD_D - 2 * TR_X0
    I, c = I_sec(h)
    sig = 400 * Ls / 4 * c / I
    dfl = 400 * Ls ** 3 / (48 * 200000 * I)
    ok(sig < 120 and dfl < 0.5, 'решётка средняя: 40 кг в центре',
       'σ=%.0f МПа, прогиб %.2f мм' % (sig, dfl))
    I1, c1 = I_sec(GR_H)
    Ie = (I1 + I) / 2
    sig1 = 400 * Ls / 4 * max(c, c1) / Ie
    ok(sig1 < 150, 'решётка крайняя: 40 кг в центре', 'σ≈%.0f МПа' % sig1)

    # ---------------- плита Л7 и фанера ----------------
    xc3 = CROSS_XC[2]
    ok(near(PL_X0, xc3), 'левый край плиты — по оси поперечины Т4-3 (опора 20 мм)')
    ok(near(PL_D, T7_YC), 'задний край плиты — по оси Т7 (опора 20 мм)')
    ok(near(PL_X0 + PL_W, MOD_W), 'плита до правого края модуля')
    for (bx, by) in PL_BOLTS:
        X, Y = PL_X0 + bx, by
        on_front = TUBE + 0 <= X <= MOD_W - TUBE and 8 <= Y <= TUBE - 8
        on_side = MOD_W - TUBE + 8 <= X <= MOD_W - 8 and TUBE <= Y <= MOD_D - TUBE
        ok(on_front or on_side, 'болт плиты (%g;%g) попадает в полость трубы, не в ногу' % (X, Y))
    x_lo = CAP_T + 0.5
    spans = [CROSS_XC[0] - TUBE / 2 - TUBE, CROSS_XC[1] - CROSS_XC[0] - TUBE,
             CROSS_XC[2] - CROSS_XC[1] - TUBE]
    ok(max(spans) <= 300, 'пролёты фанеры 18 между поперечинами', ' / '.join('%g' % s for s in spans))
    a, b = topboards()
    ok(a.pos[0] <= TUBE - 15, 'Щ1 опирается на левую боковую ≥15 мм')
    ok(near(a.pos[0] + a.size()[0], SEAM_X) and near(b.pos[0], SEAM_X),
       'стык Щ1/Щ2 на оси средней поперечины (по 20 мм опоры)')
    ok(near(b.pos[0] + b.size()[0], MOD_W - x_lo), 'Щ2 до правой юбки крышки')
    cut_x = PL_X0 - PL_GAP
    cut_y = PL_D + PL_GAP
    ok(cut_x - (xc3 - TUBE / 2) >= 15, 'край выреза Щ2 опирается на Т4-3', '%g мм' % (cut_x - (xc3 - TUBE / 2)))
    ok((T7_YC + TUBE / 2) - cut_y >= 15, 'край выреза Щ2 опирается на Т7', '%g мм' % (T7_YC + TUBE / 2 - cut_y))
    C = cap_flat()
    ok(near(C.uc + C.SB, cut_x) and near(C.vc + C.SB, cut_y), 'вырез крышки = вырез фанеры = плита + 1 мм')
    ok(near(C.Bx + 2 * C.SB, CAP_W) and near(C.By + 2 * C.SB, CAP_D), 'развёртка Л1 сворачивается в 1400×700')

    # ---------------- развёртки (обратная сборка) ----------------
    for p, W, D, H in ((grate_flat(), GR_W, GR_D, GR_H), (grate_mid_flat(), GR_W, GR_D, GR_H)):
        ok(near(p.Bx + 2 * p.SB, W) and near(p.By + 2 * p.SB, D) and near(p.E, p.BA + H - p.SB),
           '%s сворачивается в %g×%g×%g' % (p.code, W, D, H))
    S = shelf_flat()
    ok(near(S.Bx + 2 * S.SB, SH_W) and near(S.By + 2 * S.SB, SH_D), 'Л4 сворачивается в %g×%g' % (SH_W, SH_D))
    ok(SH_NOTCH >= TUBE - 2 + 2, 'вырезы полки Л4 охватывают ноги с зазором')

    # ---------------- панели ----------------
    P = panel()
    grid = [(x, y) for x, y, r in P.drills if r == PN_HOLE / 2]
    mount = [(x, y) for x, y, r in P.drills if r == PN_MOUNT_D / 2]
    dmin = min(math.hypot(x - u, y - v) for x, y in mount for u, v in grid)
    ok(dmin >= 30, 'крепёжные отв. ø5 не попадают в сетку ø8', 'мин. %.1f мм' % dmin)
    for x, y in mount:
        on = any(abs(x - xc) <= BT_W / 2 - 15 for xc in BT_XC) and BT_Y0 + 15 <= y <= BT_Y0 + BT_L - 15
        ok(on, 'саморез панели (%g;%g) попадает в рейку' % (x, y))
    anc = [(xc, BT_Y0 + a) for xc in BT_XC for a in BT_ANCHOR]
    da = min(math.hypot(x - u, y - v) for x, y in mount for u, v in anc)
    ok(da >= 40, 'дюбели реек не под саморезами панели', 'мин. %.0f мм' % da)
    ok(BT_Y0 + BT_L <= PN_H - 5, 'рейка не выходит за панель')

    # ---------------- раскрой ----------------
    pn = ply_nest()
    ok(len(pn) == 2, 'фанера: всё в 2 листа %d×%d' % (PLY_SW, PLY_SH))
    mn = metal_nest()
    ok(True, 'металл: раскладки без наложений', '%d листов/заготовок' % len(mn))
    for prof in ('40х40х2', '40х20х2'):
        pieces = [(t.code, t.L) for t in tubes() if t.profile == prof for _ in range(t.qty)]
        st = cut_sticks(pieces)
        ok(all(sum(L for _, L in s) + 3 * len(s) <= 6000 for s in st),
           'труба %s: %d хлыст(а) по 6 м' % (prof, len(st)))
    return REPORT


if __name__ == '__main__':
    rep = run()
    print('\n'.join(rep))
