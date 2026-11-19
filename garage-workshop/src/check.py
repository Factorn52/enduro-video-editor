# -*- coding: utf-8 -*-
"""Сквозная проверка размеров и стыковок. Падает с ошибкой, если что-то не сходится.
Отчёт пишется в ../Проверка_размеров.txt

Принцип (после нормоконтроля): проверки сравнивают ФАКТИЧЕСКУЮ геометрию (контуры развёрток,
перечитанные DXF, 3D-коробки с косынками и крепежом) с НЕЗАВИСИМЫМИ требованиями —
а не производные величины сами с собой."""
import os
import math
import glob
import ezdxf
from shapely.geometry import Polygon, box as sbox
from geom import *
from outputs import metal_nest, ply_nest, metal_parts, ply_parts, translit, _mat_short

USER_H = 1870
REPORT = []
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))


def ok(cond, text, val=''):
    line = ('OK   ' if cond else 'FAIL ') + text + (('  [' + val + ']') if val else '')
    REPORT.append(line)
    if not cond:
        raise AssertionError(line)


def near(a, b, tol=0.3):
    return abs(a - b) <= tol


def outline_bbox(p):
    pts = bulge_points(p.outer)
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
    return max(xs) - min(xs), max(ys) - min(ys)


def BA_(ri, t, k=0.42):                       # независимая формула (не из geom)
    return math.pi / 2 * (ri + k * t)


# ---------------------------------------------------------------------------
# 3D-модель (коробки: x вдоль модуля, y от фронта, z вверх)
# ---------------------------------------------------------------------------
def frame_boxes(mod):
    T, W, D = TUBE, MOD_W, MOD_D
    z0 = FOOT_H + PLATE_T
    zt = FRAME_TOP - T
    B = []
    for x in (0, W - T):
        for y in (0, D - T):
            B.append(('Т1', (x, y, z0), (x + T, y + T, z0 + LEG_L)))
            B.append(('Л5', (x, y, FOOT_H), (x + T, y + T, z0)))
    B.append(('Т2 перед', (T, 0, zt), (W - T, T, FRAME_TOP)))
    B.append(('Т2 зад', (T, D - T, zt), (W - T, D, FRAME_TOP)))
    B.append(('Т3 лев', (0, T, zt), (T, D - T, FRAME_TOP)))
    B.append(('Т3 прав', (W - T, T, zt), (W, D - T, FRAME_TOP)))
    B.append(('Т6 лев', (0, T, LOW_Z0), (LOW_W, D - T, LOW_Z1)))
    B.append(('Т6 прав', (W - LOW_W, T, LOW_Z0), (W, D - T, LOW_Z1)))
    B.append(('Т5 зад', (T, D - LOW_W, LOW_Z0), (W - T, D, LOW_Z1)))
    B.append(('Т8', (W / 2 - 25, D - 4, zt - 40), (W / 2 + 25, D, zt)))
    if mod == 'A':
        B.append(('Т5 перед', (T, 0, LOW_Z0), (W - T, LOW_W, LOW_Z1)))
    else:
        for i, xc in enumerate(CROSS_XC):
            B.append(('Т4-%d' % (i + 1), (xc - T / 2, T, zt), (xc + T / 2, D - T, FRAME_TOP)))
        B.append(('Т7', (T7_X0, T7_YC - T / 2, zt), (T7_X0 + T7_L, T7_YC + T / 2, FRAME_TOP)))
        # косынки Л6 (в плоскости передних ног, толщина 4 по центру профиля)
        B.append(('Л6 лев', (T, T / 2 - 2, zt - GUSSET), (T + GUSSET, T / 2 + 2, zt)))
        B.append(('Л6 прав', (W - T - GUSSET, T / 2 - 2, zt - GUSSET), (W - T, T / 2 + 2, zt)))
    return B


def bolt_boxes():
    """Пакеты болтов плиты под трубой: шайба ø20 + гайка (z ниже нижней стенки)."""
    zb = FRAME_TOP - TUBE
    B = []
    for bx, by in PL_BOLTS:
        X, Y = PL_X0 + bx, by
        B.append(('болт Л7 (%g;%g)' % (X, Y), (X - 10, Y - 10, zb - 14), (X + 10, Y + 10, zb)))
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
    REPORT.clear()
    # ---------------- высоты ----------------
    ok(near(FOOT_H + PLATE_T + LEG_L, 931), 'опора 25 + подпятник 4 + нога = верх каркаса 931',
       '%g' % (FOOT_H + PLATE_T + LEG_L))
    ok(abs(FRAME_TOP + 18 + 1.5 - 950) <= 1, 'каркас + фанера 18 + крышка 1,5 ≈ 950', '%g' % TOP_Z)
    C = cap_flat()
    wC, hC = outline_bbox(C)
    skirt = (wC - (CAP_W - 2 * (CAP_RI + CAP_T)) - 2 * BA_(CAP_RI, CAP_T)) / 2 + (CAP_RI + CAP_T)
    ok(near(skirt, TOP_Z - FRAME_TOP, 0.05), 'юбка Л1 (по контуру развёртки) = верх каркаса → верх крышки',
       'юбка %.2f' % skirt)
    G = grate_flat()
    wG, hG = outline_bbox(G)
    gskirt = (hG - (GR_D - 2 * (GR_RI + GR_T)) - 2 * BA_(GR_RI, GR_T)) / 2 + (GR_RI + GR_T)
    ok(near(FRAME_TOP + TR_T + gskirt, TOP_Z, 0.05), 'борт решётки (по контуру) → верх решётки = верх столешницы',
       'борт %.2f' % gskirt)
    pr = FRAME_TOP + PL_T - TOP_Z
    ok(0 <= pr <= 2, 'плита Л7 выше крышки на 0…2 мм (подкладками до 0,5–1,5)', '%+.1f мм' % pr)
    r = TOP_Z / USER_H
    ok(0.49 <= r <= 0.54, 'высота столешницы под рост %d мм' % USER_H,
       '%.0f мм = %.3f роста; губки тисков ≈ %.0f' % (TOP_Z, r, TOP_Z + 135))
    ok(PN_Z0 - TOP_Z >= 50, 'низ панелей выше столешницы', '%g мм' % (PN_Z0 - TOP_Z))
    # досягаемость: плечо 0,82H, рука 0,44H, наклон через край стола (+300 мм)
    sh, arm, reach_d = 0.82 * USER_H, 0.44 * USER_H + 300, MOD_D - 36 + 150
    zmax = sh + math.sqrt(max(0, arm ** 2 - reach_d ** 2))
    ok(PN_Z0 + PN_H - zmax <= 150, 'верх панелей: досягаемость с наклоном через стол',
       'достаём до ≈%.0f, верх %d — верхние ~%d мм для редкого' % (zmax, PN_Z0 + PN_H, max(0, PN_Z0 + PN_H - zmax)))

    # ---------------- габариты ----------------
    ok(N_MOD * MOD_W + 2 * 50 <= GARAGE_W, 'верстак входит в ширину гаража (≥50 до стен)',
       '%d + %g/%g' % (N_MOD * MOD_W, BENCH_X0, BENCH_X0))
    tl = {t.code: t for t in tubes()}
    ok(near(tl['Т2'].L + 2 * 40, 1400) and near(tl['Т5'].L + 2 * 40, 1400), 'Т2/Т5 = 1400 − 2 ноги')
    ok(all(near(tl[c].L + 2 * 40, 700) for c in ('Т3', 'Т4', 'Т6')), 'Т3/Т4/Т6 = 700 − 2 трубы')
    ok(near(T7_X0, TUBE) and near(T7_X0 + T7_L, CROSS_XC[0] - TUBE / 2), 'Т7: от левой Т3 до грани Т4-1',
       'L=%g' % T7_L)

    # ---------------- 3D: пересечения, косынки, крепёж ----------------
    for mod in ('A', 'B'):
        B = frame_boxes(mod)
        bad = [(a[0], b[0]) for i, a in enumerate(B) for b in B[i + 1:] if overlap(a, b) > 1e-3]
        ok(not bad, 'каркас %s: элементы (с Л6, Т8) не пересекаются' % mod, str(bad) if bad else '')
        lonely = [a[0] for a in B if not any(touches(a, b) for b in B if b is not a)]
        ok(not lonely, 'каркас %s: каждый элемент примыкает к соседнему' % mod)
    BB = frame_boxes('B')
    for bb in bolt_boxes():
        hit = [b[0] for b in BB if overlap(bb, b) > 1e-3]
        ok(not hit, '%s: шайба+гайка не задевают косынки/трубы' % bb[0], ', '.join(hit))
        X, Y = (bb[1][0] + bb[2][0]) / 2, (bb[1][1] + bb[2][1]) / 2
        on_front = TUBE <= X <= MOD_W - TUBE and 8 <= Y <= TUBE - 8
        on_left = 8 <= X <= TUBE - 8 and TUBE + 10 <= Y <= MOD_D - TUBE - 10
        ok(on_front or on_left, '%s: в полости трубы (через втулку), не в ноге' % bb[0])
        if Y < TUBE:
            gx = min(X - (TUBE + GUSSET), (MOD_W - TUBE - GUSSET) - X)
            ok(gx >= 25, '%s: ≥25 мм от центра до кромки косынки Л6' % bb[0], '%g' % gx)
    # опоры на стыке модулей
    ok(FOOT_BASE_D <= TUBE - 5, 'пяты опор соседних ног на стыке модулей не налезают',
       'ø%g при осях через %g' % (FOOT_BASE_D, TUBE))

    # ---------------- поддон ----------------
    ok(near(TR_X0 + TR_LX + TR_GAP + TUBE, MOD_W) and TR_GAP >= 4,
       'поддон в проёме: зазор ≥4 до перемычек (место под швы)', '%g' % TR_GAP)
    ok(0.5 <= TR_X0 - TR_F <= 2, 'полка поддона не выходит за каркас', 'кромка на %g' % (TR_X0 - TR_F))
    T = tray_flat()
    wT, hT = outline_bbox(T)
    ok(wT <= 1980 and hT <= 980, 'развёртка Л2 в лист 1000×2000', '%.1f×%.1f' % (wT, hT))
    sx_ = 100 * TR_A / TR_LX; sy_ = 100 * TR_B / TR_LY
    ok(sx_ >= 1.5 and sy_ >= 1.5, 'уклон дна ≥1,5 % (прогиб листа 1,5 до 2,6 мм)', '%.1f %% / %.1f %%' % (sx_, sy_))
    dx_, dy_ = drain_xy()
    hd = tray_h(dx_, dy_)
    hmax = max(tray_h(x, y) for x in (0, TR_LX) for y in (0, TR_LY))
    puddle = tray_volume(hmax - hd) * 1000
    ok(hmax - hd <= 2.0 and puddle < 5, 'слив у самого низкого угла: остаток в углу < 5 мл',
       'угол ниже слива на %.1f мм, %.1f мл' % (hmax - hd, puddle))
    dfx, dfy = drain_frame_xy()
    ok(dfy < MOD_D / 2, 'кран слива — у фронта', 'y=%.1f от передней грани' % dfy)
    z_drain = FRAME_TOP + TR_T - hd
    z_low = z_drain - (25 + 55 + 35)
    gap_can = z_low - (LOW_Z1 + SH_T + 470)
    ok(gap_can >= 40, 'под сливом входит канистра 20 л (h=470)', 'зазор %.0f мм' % gap_can)
    ok(dfx - 16 > TUBE and dfy - 16 > TUBE, 'кран слива не задевает ногу', '(%.1f; %.1f)' % (dfx, dfy))
    vmax = tray_volume(DR_MAX_LEVEL)
    ok(vmax <= 20 * 0.9, 'риска «МАКС» %d мм: объём ≤ 90 %% канистры 20 л' % DR_MAX_LEVEL, '%.1f л' % vmax)
    v_sh = (SH_W - 2 * SH_T) * (SH_D - 2 * SH_T) * (SH_LIP - SH_T) / 1e6 - 4 * (SH_NOTCH ** 2) * SH_LIP / 1e6
    ok(v_sh >= vmax * 1.5, 'полка-поддон Л4 вмещает пролив ≥1,5× рабочего объёма', '%.0f л' % v_sh)
    # строгая проверка контура полки: вырез под ногу
    S = shelf_flat()
    sp = Polygon(bulge_points(S.outer))
    BAs = BA_(SH_RI, SH_T); SBs = SH_RI + SH_T
    # угол основания в координатах развёртки: физич. x=2..(2+SH_NOTCH)-зона ноги
    leg = sbox(-100, -100, (TUBE + 2 + 2) - 2 - SBs, (TUBE + 2 + 2) - 2 - SBs)   # нога + швы 2 мм
    ok(sp.intersection(leg).area < 1e-6, 'вырез полки Л4 (по контуру) охватывает ногу + швы 2 мм',
       'вырез %g' % SH_NOTCH)

    # ---------------- решётки ----------------
    stack = GR_N * GR_W + (GR_N - 1) * GR_GAP
    inner = MOD_W - 2 * ((TR_X0 - TR_F) + TR_T)
    ok(0 < inner - stack <= 4, 'решётки между упорами', 'люфт %.1f мм' % (inner - stack))
    y_in0, y_in1 = TR_X0 + TR_T, MOD_D - TR_X0 - TR_T
    ok(GR_DEEP_Y[0] - y_in0 >= 2 and y_in1 - GR_DEEP_Y[1] >= 2,
       'глубокие борта внутри стенок поддона', '%.1f / %.1f мм' % (GR_DEEP_Y[0] - y_in0, y_in1 - GR_DEEP_Y[1]))
    zb = TOP_Z - GR_H - GR_DEEP
    zt = FRAME_TOP + TR_T
    xs = [GR_X0 + k * (GR_W + GR_GAP) + d for k in range(GR_N) for d in (0, GR_W)][1:-1]
    worst = min(zb - (zt - tray_h(x - TR_X0, y - TR_X0)) for x in xs for y in GR_DEEP_Y)
    ok(worst >= 25, 'глубокие борта не достают до дна поддона', 'мин. зазор %.0f мм' % worst)
    for P_ in (G, grate_mid_flat()):
        sl = P_.holes[:-2]                       # без ручек
        xs_ = [q[0] + P_.SB for h_ in sl for q in bulge_points(h_)]
        ys_ = [q[1] + P_.SB for h_ in sl for q in bulge_points(h_)]
        ml, mr = min(xs_), GR_W - max(xs_)
        my0, my1 = min(ys_), GR_D - max(ys_)
        for side, m, deep in (('лев', ml, P_.deep[0]), ('прав', mr, P_.deep[1])):
            need = 15 if deep else (TR_X0 + TR_T) - GR_X0 + 3   # над поддоном, а не над полкой
            ok(m >= need, '%s: пазы у %s. борта — над поддоном, не над полкой' % (P_.code, side),
               'поле %.1f ≥ %.1f' % (m, need))
        need_y = (TR_X0 + TR_T) - GR_X0 + 3
        ok(min(my0, my1) >= need_y, '%s: пазы спереди/сзади — над поддоном' % P_.code, '%.1f' % min(my0, my1))
    # прочность решётки: пролёт по опиранию бортов на полку ≈ 690
    t = GR_T
    def I_sec(hw):
        A1, y1 = GR_W * t, t / 2
        A2, y2 = 2 * t * (hw - t), t + (hw - t) / 2
        yc = (A1 * y1 + A2 * y2) / (A1 + A2)
        I = GR_W * t ** 3 / 12 + A1 * (yc - y1) ** 2 + 2 * t * (hw - t) ** 3 / 12 + A2 * (yc - y2) ** 2
        return I, hw - yc
    Ls = GR_D - 2 * 3
    I, c = I_sec(GR_H + GR_DEEP)
    sig = 400 * Ls / 4 * c / I
    dfl = 400 * Ls ** 3 / (48 * 200000 * I)
    ok(sig < 120 and dfl < 0.5, 'решётка средняя: 40 кг в центре, пролёт %d' % Ls,
       'σ=%.0f МПа, прогиб %.2f мм' % (sig, dfl))
    I1, c1 = I_sec(GR_H)
    sig1 = 400 * Ls / 4 * max(c, c1) / ((I1 + I) / 2)
    ok(sig1 < 150, 'решётка крайняя: 40 кг в центре', 'σ≈%.0f МПа' % sig1)
    # головки саморезов крышки не на стороне решёток
    fx_, rx_, dtop = C.screws
    ok(not any(cx < 0 for cx, cy, r in C.circles), 'в левой юбке Л1 (к решёткам модуля А) нет саморезов',
       '%d отв. всего' % len(C.circles))

    # ---------------- плита Л7 и фанера ----------------
    ok(near(PL_X0 + PL_W, CROSS_XC[0]), 'правый край плиты — по оси Т4-1 (опора 20 мм)')
    ok(near(PL_D, T7_YC), 'задний край плиты — по оси Т7 (опора 20 мм)')
    ok(near(PL_X0, 0), 'плита над стянутыми ногами стыка модулей (x=0 модуля Б)')
    vx = BENCH_X0 + MOD_W + PL_X0 + VISE_XC
    ok(min(vx, GARAGE_W - vx) >= 800, 'ось тисков ≥800 мм от боковых стен',
       '%.0f / %.0f' % (vx, GARAGE_W - vx))
    a, b = topboards()
    pa = Polygon(bulge_points(a.moved(*a.pos).outer))
    pb = Polygon(bulge_points(b.moved(*b.pos).outer))
    plate = sbox(PL_X0, 0, PL_X0 + PL_W, PL_D)
    ok(pa.distance(plate) >= PL_GAP - 0.01 and pb.distance(plate) >= PL_GAP - 0.01,
       'фанера не налезает на плиту (по контурам)', 'зазор %g' % pa.distance(plate))
    ok(near(pa.distance(pb), 0, 0.01), 'Щ1 и Щ2 стыкуются без щели')
    cap_in = sbox(CAP_T + 1.2, CAP_T + 1.2, MOD_W - CAP_T - 1.2, MOD_D - CAP_T - 1.2)
    ok(cap_in.contains(pa) and cap_in.contains(pb), 'фанера ≥1,2 мм от внутр. граней юбок (радиус гиба)')
    # опирание кромок фанеры (по контуру) на трубы ≥15
    supports = [sbox(0, 0, TUBE, MOD_D), sbox(MOD_W - TUBE, 0, MOD_W, MOD_D), sbox(0, 0, MOD_W, TUBE),
                sbox(0, MOD_D - TUBE, MOD_W, MOD_D)]
    supports += [sbox(xc - TUBE / 2, 0, xc + TUBE / 2, MOD_D) for xc in CROSS_XC]
    supports += [sbox(T7_X0, T7_YC - TUBE / 2, T7_X0 + T7_L, T7_YC + TUBE / 2)]
    for nm, pp in (('Щ1', pa), ('Щ2', pb)):
        ring = pp.difference(pp.buffer(-15))
        bad = ring.difference(sbox(0, 0, 0, 0))
        for sup in supports:
            bad = bad.difference(sup)
        ok(bad.area < 50, '%s: все кромки лежат на трубах полосой ≥15 мм' % nm, 'без опоры %.0f мм²' % bad.area)
    # пролёты фанеры: максимальный неподпёртый прямоугольник ≈ по сетке опор
    xs_sup = sorted([TUBE] + [c - 20 for c in CROSS_XC] + [c + 20 for c in CROSS_XC] + [MOD_W - TUBE])
    spans = [CROSS_XC[1] - CROSS_XC[0] - TUBE, CROSS_XC[2] - CROSS_XC[1] - TUBE,
             MOD_W - TUBE - CROSS_XC[2] - TUBE / 2]
    behind = (CROSS_XC[0] - TUBE / 2 - TUBE, MOD_D - TUBE - (T7_YC + TUBE / 2))
    ok(max(spans) <= 300, 'пролёты фанеры между поперечинами ≤300', ' / '.join('%g' % s for s in spans))
    ok(max(behind) <= 400, 'поле за плитой (опора по 4 сторонам) ≤400', '%g×%g' % behind)
    # саморезы фанеры попадают в трубы и в фанеру
    for x, y in ply_screws():
        from shapely.geometry import Point
        pt = Point(x, y)
        inside_tube = any(sup.contains(pt) and sup.exterior.distance(pt) >= 6 for sup in supports)
        in_ply = any(pp.contains(pt) and pp.exterior.distance(pt) >= 9 for pp in (pa, pb))
        ok(inside_tube and in_ply, 'саморез фанеры (%g;%g): ≥6 от края трубы, ≥9 от кромки фанеры' % (x, y))
    Cp = Polygon(bulge_points(C.outer))
    # вырез крышки (в координатах развёртки) совпадает с плитой + зазор
    corner = (C.uc + C.SB, C.vc + C.SB)
    ok(near(corner[0], PL_X0 + PL_W + PL_GAP) and near(corner[1], PL_D + PL_GAP),
       'вырез Л1 = плита + зазор %g' % PL_GAP)
    ok(near(a.cut[0] + a.pos[0], corner[0]) and near(a.cut[1] + a.pos[1], corner[1]),
       'вырез Щ1 = вырез Л1')

    # ---------------- развёртки: обратная сборка по контуру ----------------
    for p, W, D, H in ((C, CAP_W, CAP_D, CAP_H), (S, SH_W, SH_D, SH_LIP)):
        w_, h_ = outline_bbox(p)
        ri = CAP_RI if p is C else SH_RI
        tt = CAP_T if p is C else SH_T
        sb = ri + tt
        exp_w = (W - 2 * sb) + 2 * (BA_(ri, tt) + H - sb)
        ok(near(w_, exp_w, 0.05), '%s: габарит развёртки по контуру = расчётному' % p.code,
           '%.2f / %.2f' % (w_, exp_w))
    for p in (G, grate_mid_flat()):
        w_, h_ = outline_bbox(p)
        exp_h = (GR_D - 12) + 2 * (BA_(3, 3) + GR_H - 6)
        exp_w = (GR_W - 12) + sum(BA_(3, 3) + GR_H - 6 + (GR_DEEP if d else 0) for d in p.deep)
        ok(near(h_, exp_h, 0.05) and near(w_, exp_w, 0.05), '%s: развёртка по контуру' % p.code,
           '%.2f×%.2f' % (w_, h_))

    # ---------------- панели ----------------
    P = panel()
    grid = [(x, y) for x, y, r in P.drills if r == PN_HOLE / 2]
    mount = [(x, y) for x, y, r in P.drills if r == PN_MOUNT_D / 2]
    dmin = min(math.hypot(x - u, y - v) for x, y in mount for u, v in grid)
    ok(dmin >= 24, 'крепёжные отв. ø5 не пересекают сетку ø8', 'мин. %.1f мм между центрами' % dmin)
    ok(sorted(PN_MOUNT_X) == sorted(PN_W - x for x in PN_MOUNT_X), 'крепёж панели симметричен (не путается при зеркале)')
    for x, y in mount:
        on = any(abs(x - xc) <= BT_W / 2 - 15 for xc in BT_XC) and BT_Y0 + 15 <= y <= BT_Y0 + BT_L - 15
        ok(on, 'саморез панели (%g;%g) попадает в рейку' % (x, y))
    anc = [(xc, BT_Y0 + a_) for xc in BT_XC for a_ in BT_ANCHOR]
    da = min(math.hypot(x - u, y - v) for x, y in mount for u, v in anc)
    ok(da >= 40, 'дюбели реек не под саморезами панели', 'мин. %.0f мм' % da)
    for q in acc_parts():
        if q.code.endswith('.1'):
            dw = [(x, y) for x, y, r in q.drills if r == 4]
            sc_ = [(x, y) for x, y, r in q.drills if r < 4]
            ok(len(dw) == 4 and len(sc_) == 1, '%s: 4 шканта + 1 саморез' % q.code)
            sx, sy = sc_[0]
            gx = (sx - dw[0][0]) % 50; gy = (sy - dw[0][1]) % 50
            ok(near(gx, 25) and near(gy, 25), '%s: саморез между отв. сетки панели' % q.code)

    # ---------------- DXF: перечитать файлы ----------------
    for p in metal_parts() + ply_parts():
        fn = '%s_%s_t%s_%dsht.dxf' % (translit(p.code), _mat_short(p.material), ('%g' % p.t).replace('.', ','), p.qty)
        d = os.path.join(ROOT, 'DXF_laser' if p.kind == 'metal' else 'DXF_cnc_fanera', fn)
        if not os.path.exists(d):
            continue
        msp = ezdxf.readfile(d).modelspace()
        nc = sum(1 for e in msp if e.dxftype() == 'CIRCLE')
        npl = sum(1 for e in msp if e.dxftype() == 'LWPOLYLINE')
        nb = sum(1 for e in msp if e.dxftype() == 'LINE' and e.dxf.layer.startswith('BEND'))
        ok(nc == len(p.circles) + len(p.drills) and npl == 1 + len(p.holes) and nb == len(p.bends),
           'DXF %s: контуры/отверстия/гибы = модели' % fn, '%d/%d/%d' % (npl, nc, nb))

    # ---------------- раскрой и закупка ----------------
    pn = ply_nest()
    ok(len(pn) == 2, 'фанера: всё в 2 листа %d×%d' % (PLY_SW, PLY_SH))
    need = {}
    for p in ply_parts():
        need[p.code] = need.get(p.code, 0) + p.qty
    have = {}
    for _, L in pn:
        for p in L:
            have[p.code] = have.get(p.code, 0) + 1
    ok(need == have, 'раскладка фанеры содержит все детали в нужном количестве')
    mn = metal_nest()
    needm, havem = {}, {}
    for p in metal_parts():
        needm[p.code] = p.qty
    for s_ in mn:
        for p in s_['parts']:
            havem[p.code] = havem.get(p.code, 0) + 1
    ok(needm == havem, 'раскладки металла содержат все детали в нужном количестве',
       ', '.join('%s×%d' % kv for kv in sorted(havem.items())))
    for prof in ('40х40х2', '40х20х2'):
        pieces = [(t_.code, t_.L) for t_ in tubes() if t_.profile == prof for _ in range(t_.qty)]
        st = cut_sticks(pieces)
        ok(all(sum(L for _, L in s) + 3 * len(s) + 20 <= 6000 for s in st) and
           sum(len(s) for s in st) == len(pieces),
           'труба %s: %d хлыст(а) по 6 м, все отрезки размещены' % (prof, len(st)))
    return REPORT


if __name__ == '__main__':
    rep = run()
    print('\n'.join(rep))
