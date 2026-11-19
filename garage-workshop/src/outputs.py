# -*- coding: utf-8 -*-
"""DXF для лазера/ЧПУ, раскладки листов, спецификация CSV."""
import os
import csv
import ezdxf
from ezdxf import units
from shapely.geometry import Polygon, box as sbox
from geom import *

TRANS = {'Л': 'L', 'П': 'P', 'Р': 'R', 'Щ': 'SCH', 'А': 'A', 'Т': 'T'}


def translit(code):
    return ''.join(TRANS.get(c, c) for c in code).replace('.', '-')


def _new_doc():
    doc = ezdxf.new('R2010', setup=True)
    doc.units = units.MM
    doc.header['$INSUNITS'] = 4
    doc.header['$MEASUREMENT'] = 1
    L = doc.layers
    L.add('CUT', color=7)                       # контур реза (наружный + внутренние)
    L.add('BEND_UP', color=1, linetype='DASHED')     # гиб «на себя» (к виду DXF) — НЕ резать
    L.add('BEND_DOWN', color=30, linetype='DASHED')  # гиб «от себя» — НЕ резать
    L.add('DRILL', color=4)                     # металл: сверлить по месту, НЕ резать
    L.add('CUT_INSIDE', color=5)                # фанера: внутренние контуры фрезой
    L.add('DRILL_D8', color=3)
    L.add('DRILL_D6', color=4)
    L.add('DRILL_D5', color=6)
    L.add('SHEET', color=8)                     # граница листа — НЕ резать
    L.add('TEXT', color=2)                      # подписи — НЕ резать
    return doc


def _add_part(msp, p, dx=0.0, dy=0.0, with_text=False):
    def T(v):
        return [(x + dx, y + dy, b) for x, y, b in v]
    msp.add_lwpolyline(T(p.outer), format='xyb', close=True, dxfattribs={'layer': 'CUT'})
    inner_layer = 'CUT' if p.kind == 'metal' else 'CUT_INSIDE'
    for h in p.holes:
        msp.add_lwpolyline(T(h), format='xyb', close=True, dxfattribs={'layer': inner_layer})
    for cx, cy, r in p.circles:
        msp.add_circle((cx + dx, cy + dy), r, dxfattribs={'layer': 'CUT'})
    for cx, cy, r in p.drills:
        d = round(2 * r)
        if p.kind == 'metal':
            lay = 'DRILL'
        else:
            lay = 'DRILL_D%d' % d if d in (5, 6, 8) else 'CUT_INSIDE'
        msp.add_circle((cx + dx, cy + dy), r, dxfattribs={'layer': lay})
    bd = getattr(p, 'bend_dir', {})
    for x1, y1, x2, y2, lab in p.bends:
        lay = 'BEND_UP' if bd.get(lab, 'DOWN') == 'UP' else 'BEND_DOWN'
        msp.add_line((x1 + dx, y1 + dy), (x2 + dx, y2 + dy), dxfattribs={'layer': lay})


def write_part_dxf(p, folder):
    p = p.normalized()
    doc = _new_doc()
    _add_part(doc.modelspace(), p)
    w, h = p.size()
    fn = '%s_%s_t%s_%dsht.dxf' % (translit(p.code), _mat_short(p.material), _t(p.t), p.qty)
    path = os.path.join(folder, fn)
    doc.saveas(path)
    return fn


def _t(t):
    return ('%g' % t).replace('.', ',')


def _mat_short(m):
    if '304' in m:
        return 'AISI304'
    if '430' in m:
        return 'AISI430'
    if 'Фанера' in m:
        return 'fanera'
    return 'St3'


def write_nest_dxf(sheet_w, sheet_h, placed, path, title=''):
    """Раскладка: граница листа — слой SHEET (не резать); подписи — только ЗА листом."""
    doc = _new_doc()
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (sheet_w, 0), (sheet_w, sheet_h), (0, sheet_h)], close=True,
                       dxfattribs={'layer': 'SHEET'})
    for p in placed:
        _add_part(msp, p)
    if title:
        codes = {}
        for p in placed:
            codes[p.code] = codes.get(p.code, 0) + 1
        legend = title + ':  ' + ', '.join('%s ×%d' % kv for kv in codes.items())
        msp.add_text(legend, height=15, dxfattribs={'layer': 'TEXT'}).set_placement((0, sheet_h + 30))
    doc.saveas(path)


# ----------------------------------------------------------------------------
# Раскладки
# ----------------------------------------------------------------------------
def place(p, x, y, rot=False):
    q = p.rotated() if rot else p.normalized()
    return q.moved(x, y)


def check_nest(sheet_w, sheet_h, placed, margin=5, gap=5):
    polys = []
    for p in placed:
        P = Polygon(bulge_points(p.outer)).buffer(0)
        x0, y0, x1, y1 = P.bounds
        assert x0 >= margin - 1e-6 and y0 >= margin - 1e-6, (p.code, P.bounds)
        assert x1 <= sheet_w - margin + 1e-6 and y1 <= sheet_h - margin + 1e-6, (p.code, P.bounds)
        polys.append((p.code, P))
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            d = polys[i][1].distance(polys[j][1])
            assert d >= gap - 1e-6, (polys[i][0], polys[j][0], d)
    return True


def ply_nest():
    """2 листа 2440×1220: панель + часть столешницы + 3 рейки + держатели."""
    P1, R1 = panel(), batten()
    S1, S2 = topboards()
    acc = {p.code: p for p in acc_parts()}
    m, g = 10, 12
    sx = m + PN_W + g                       # 1422 — правая полоса шириной 1008

    def sheet(top, codes_rows, extra=()):
        L = [place(P1, m, m), place(top, sx, m)]
        bx = sx + top.size()[0] + g
        for k in range(3):
            L.append(place(R1, bx + k * (BT_W + g), m, rot=True))
        y = m + top.size()[1] + g
        for row in codes_rows:
            x = sx
            hmax = 0
            for code in row:
                q = place(acc[code], x, y)
                L.append(q)
                x += q.size()[0] + g
                hmax = max(hmax, q.size()[1])
            y += hmax + g
        for code, x, y in extra:
            L.append(place(acc[code], x, y))
        return L
    s1 = sheet(S1, [('А1.1', 'А1.2'), ('А2.1', 'А1.3', 'А1.3'), ('А2.2', 'А2.3', 'А2.3')],
               extra=(('А4', 1980, m + 696 + g + 102), ('А4', 1980, m + 696 + g + 204)))
    s2 = sheet(S2, [('А3.1', 'А3.4', 'А3.4'), ('А3.2',), ('А3.3',)])
    sheets = [('Лист фанеры №1 (2440×1220)', s1), ('Лист фанеры №2 (2440×1220)', s2)]
    for name, L in sheets:
        check_nest(PLY_SW, PLY_SH, L, margin=m, gap=g - 0.01)
    return sheets


def metal_nest():
    out = []
    T = tray_flat(); G = grate_flat(); Gm = grate_mid_flat(); C = cap_flat(); S = shelf_flat()
    m = 10
    st = drain_strainer()
    out.append(dict(title='AISI 304, 1,5 мм — лист 1000×2000', w=2000, h=1000,
                    parts=[place(T, m, m), place(st, 1650, m)], file='NEST_AISI304_t1,5_1000x2000.dxf'))
    parts, x = [], m
    for p in (G, G, Gm, Gm):
        q = place(p, x, m)
        parts.append(q)
        x += q.size()[0] + 12
    out.append(dict(title='AISI 304, 3 мм — лист 1000×2000', w=2000, h=1000, parts=parts,
                    file='NEST_AISI304_t3_1000x2000.dxf'))
    out.append(dict(title='AISI 430 шлиф., 1,5 мм — лист 1000×2000 (крышка)', w=2000, h=1000,
                    parts=[place(C, m, m)], file='NEST_AISI430_t1,5_list1_1000x2000.dxf'))
    ins = shelf_insert()
    sp = [place(S, m, m)] + [place(ins, 1500, m + k * 52) for k in range(4)]
    out.append(dict(title='AISI 430, 1,5 мм — лист 1000×2000 (полка)', w=2000, h=1000,
                    parts=sp, file='NEST_AISI430_t1,5_list2_1000x2000.dxf'))
    fp, gs, sw, vp = foot_plate(), gusset(), square_washer(), vise_plate()
    small4 = [place(fp, m + (k % 4) * 50, m + (k // 4) * 50) for k in range(8)]
    small4 += [place(gs, 220, m), place(gs, 330, m)]
    small4 += [place(sw, m + (k % 8) * 46, 125 + (k // 8) * 46) for k in range(8)]
    out.append(dict(title='Ст3, 4 мм — обрезок 450×200', w=450, h=200, parts=small4,
                    file='NEST_St3_t4_450x200.dxf'))
    out.append(dict(title='Ст45/Ст3, 20 мм — заготовка 490×340', w=490, h=340,
                    parts=[place(vp, 20, 20)], file='NEST_St_t20_490x340.dxf'))
    for s_ in out:
        check_nest(s_['w'], s_['h'], s_['parts'], margin=m - 0.01, gap=5)
    return out


def metal_parts():
    return [cap_flat(), tray_flat(), grate_flat(), grate_mid_flat(), shelf_flat(), shelf_insert(),
            drain_strainer(), foot_plate(), gusset(), square_washer(), vise_plate()]


def ply_parts():
    return [panel(), batten()] + topboards() + acc_parts()


def write_spec_csv(path, rows_header, rows):
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(rows_header)
        for r in rows:
            w.writerow(r)
