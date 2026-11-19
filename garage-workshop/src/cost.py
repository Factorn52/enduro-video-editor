# -*- coding: utf-8 -*-
"""Ориентировочная смета на листовые детали (лазер + гибка + металл).
Объёмы (длина реза, врезки, гибы, масса) берутся из геометрии деталей,
ставки — диапазоны «мин–макс» из открытых прайсов исполнителей (ноябрь 2026, см. SOURCES).
Пишет ../Смета.md"""
import os
import math
from shapely.geometry import Polygon
from geom import *
from outputs import metal_parts

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# ---- ставки, ₽ (мин, макс) ----------------------------------------------------------
CUT = {   # рез, ₽/м
    ('нерж', 1.5): (40, 90), ('нерж', 3.0): (60, 160),
    ('ст', 1.5): (20, 35), ('ст', 4.0): (40, 70), ('ст', 20.0): (250, 450),
}
PIERCE = {'нерж': (1.5, 6), 'ст': (1, 4), ('ст', 20.0): (20, 40)}
BEND = {  # ₽ за гиб: (до 1 м), (1–2 м)
    ('нерж', 1.5): ((35, 41), (52, 60)), ('нерж', 3.0): ((56, 65), (71, 85)),
    ('ст', 1.5): ((10, 25), (15, 35)),
}
BOX_K = (1.5, 2.0)          # поддон: короб с отбортовкой — наценка за сложную гибку (оценка)
SHEETS = [  # (название, кол-во, мин, макс, комментарий)
    ('AISI 304, 1,5 мм, 1000×2000 (Л2, Л11)', 1, 6000, 7000, 'прайсы Apex, Fortis, Металлинвест'),
    ('AISI 304, 3 мм, 1000×2000 (Л3, Л8)', 1, 13800, 15700, 'оценка: 47,6 кг × 290–330 ₽/кг'),
    ('AISI 430 шлиф., 1,5 мм, 1000×2000 (Л1)', 1, 4200, 5800, 'оценка: 23,1 кг × 180–250 ₽/кг'),
    ('AISI 430 2B, 1,5 мм, 1000×2000 (Л4, Л10)', 1, 4000, 5500, 'оценка: 23,1 кг × 175–240 ₽/кг'),
    ('Ст3, 4 мм, обрезок 450×200 (Л5, Л6, Л9)', 1, 400, 800, 'оценка'),
    ('Ст45, 20 мм, заготовка 490×340 (Л7)', 1, 2400, 4200, 'оценка: 26 кг × 90–160 ₽/кг'),
]
SOURCES = [
    ('Orgplex — резка нерж. по объёму + врезка', 'https://orgplex.com/lazernaya-rezka-nerzhavejki'),
    ('Orgplex — гибка нерж. от 35 ₽/гиб', 'https://orgplex.com/gibka-nerzhaveyushhej-stali'),
    ('СиМП — прайс резки (без НДС)', 'https://www.lazermetal.ru/price/lazernay-rezka/'),
    ('Svone — резка нерж.', 'https://svone.ru/lazernaya-rezka-metalla/nerzhaveyushchej-stali/'),
    ('Mnitek — резка', 'https://mnitek.ru/uslugi/lazernaya-rezka-metalla/'),
    ('Л-Конт — гибка, цена за гиб', 'https://l-cont.ru/services/gibka_metalla/'),
    ('Apex-Metal — лист AISI 304 1,5 мм', 'https://apex-metal.ru/nerzh/list_nerjavejuschij/list_304/1_5mm/'),
    ('Fortis — лист AISI 304 1,5 мм', 'https://fortis-steel.ru/produkciya/prod/list-nerzhaveyushchiy-aisi-304-shlifovannyy-1-5kh1000kh2000-mm-/'),
    ('ГК Металлинвест — лист 304 2B 1,5 мм, резка', 'https://gkmetallinvest.ru/list-nerzhaveyushchiy/nikelesod-aisi-304-08h18n10-2b-1-5mm/'),
    ('КатШара — онлайн по DXF, гибка, СДЭК по России', 'https://cutshare.ru/'),
    ('LaserMetall — онлайн-калькуляторы резки и изделий', 'https://www.lasermetall.com/culc'),
    ('PrixCut — расчёт длины реза и врезок по DXF', 'https://prixcut.ru/'),
]


def kind(p):
    return 'нерж' if 'AISI' in p.material else 'ст'


def part_volumes(p):
    P = Polygon(bulge_points(p.outer))
    cut, pierce, area = P.length, 1, P.area
    for h in p.holes:
        hp = Polygon(bulge_points(h)); cut += hp.length; pierce += 1; area -= hp.area
    for cx, cy, r in p.circles:
        cut += 2 * math.pi * r; pierce += 1; area -= math.pi * r * r
    bends = [math.hypot(b[2] - b[0], b[3] - b[1]) for b in p.bends]
    return cut / 1000, pierce, bends, area


def run():
    rows = []
    tot = [0, 0]
    cut_tot = [0, 0]
    bend_tot = [0, 0]
    for p in metal_parts():
        k = kind(p)
        cut, pierce, bends, area = part_volumes(p)
        q = p.qty
        cr = CUT[(k, p.t)]
        pr = PIERCE.get((k, p.t), PIERCE[k])
        c = [q * (cut * cr[i] + pierce * pr[i]) for i in (0, 1)]
        b = [0, 0]
        if bends:
            br = BEND[(k, p.t)]
            for L in bends:
                rr = br[0] if L <= 1000 else br[1]
                b[0] += rr[0]; b[1] += rr[1]
            if p.code == 'Л2':
                b = [b[0] * BOX_K[0], b[1] * BOX_K[1]]
            b = [q * x for x in b]
        rows.append((p.code, p.name, '%s %s' % (p.material, fmt_t(p.t)), q, cut * q, pierce * q,
                     len(bends) * q, c, b))
        for i in (0, 1):
            cut_tot[i] += c[i]; bend_tot[i] += b[i]
    mat = [sum(s[1] * s[2] for s in SHEETS), sum(s[1] * s[3] for s in SHEETS)]
    total = [mat[i] + cut_tot[i] + bend_tot[i] for i in (0, 1)]
    nerzh_parts = ('Л1', 'Л2', 'Л3', 'Л8', 'Л4', 'Л10', 'Л11')
    nz = [sum(r[7][i] + r[8][i] for r in rows if r[0] in nerzh_parts) for i in (0, 1)]
    nz_mat = [sum(s[1] * s[2 + i] for s in SHEETS[:4]) for i in (0, 1)]
    return rows, mat, cut_tot, bend_tot, total, nz, nz_mat


def fmt_t(t):
    return ('%g мм' % t).replace('.', ',')


def r(v):
    return '{:,.0f}'.format(round(v, -1)).replace(',', ' ')


def write_md(path):
    rows, mat, cut, bend, total, nz, nz_mat = run()
    L = []
    L.append('# Смета: листовые детали (лазер + гибка + металл)\n')
    L.append('Ориентир на ноябрь 2026, Москва/СПб, розница, мелкая партия. Объёмы посчитаны из '
             'геометрии деталей (`src/cost.py`), ставки — диапазоны из открытых прайсов (ссылки внизу). '
             'В регионах обычно дешевле на 10–30 %. **Это оценка, не КП** — точную цену даст цех по DXF.\n')
    L.append('## 1. Резка и гибка по деталям\n')
    L.append('| Поз. | Деталь | Материал | Кол. | Рез, м | Врезок | Гибов | Резка, ₽ | Гибка, ₽ |')
    L.append('|---|---|---|---|---|---|---|---|---|')
    for code, name, m, q, c_m, pc, nb, c, b in rows:
        L.append('| %s | %s | %s | %d | %.1f | %d | %d | %s–%s | %s |' % (
            code, name, m, q, c_m, pc, nb, r(c[0]), r(c[1]),
            ('%s–%s' % (r(b[0]), r(b[1]))) if nb else '—'))
    L.append('| | **Итого работа** | | | | | | **%s–%s** | **%s–%s** |\n' % (r(cut[0]), r(cut[1]), r(bend[0]), r(bend[1])))
    L.append('Гибка поддона Л2 посчитана с наценкой ×%g–%g: это короб с отбортовкой и упорами, '
             'нужен сегментный пуансон («коробочный» инструмент). Перфорация решёток (~570 врезок) — '
             'главная статья резки. Отверстия плиты Л7 сверлятся (в резку не входят).\n' % BOX_K)
    L.append('## 2. Металл\n')
    L.append('| Лист / заготовка | Кол. | ₽ | Основание |')
    L.append('|---|---|---|---|')
    for name, q, a, b, note in SHEETS:
        L.append('| %s | %d | %s–%s | %s |' % (name, q, r(a), r(b), note))
    L.append('| **Итого металл** | | **%s–%s** | |\n' % (r(mat[0]), r(mat[1])))
    L.append('## 3. Итого по листовым деталям\n')
    L.append('| | ₽ |')
    L.append('|---|---|')
    L.append('| Металл | %s–%s |' % (r(mat[0]), r(mat[1])))
    L.append('| Лазерная резка | %s–%s |' % (r(cut[0]), r(cut[1])))
    L.append('| Гибка | %s–%s |' % (r(bend[0]), r(bend[1])))
    L.append('| **Всего** | **%s–%s** |' % (r(total[0]), r(total[1])))
    L.append('| в т.ч. только нержавейка (Л1–Л4, Л8, Л10, Л11: листы + резка + гибка) | %s–%s |\n' % (
        r(nz[0] + nz_mat[0]), r(nz[1] + nz_mat[1])))
    L.append('**Как сэкономить:** решётки из AISI 430 3 мм вместо 304 (−5…6 тыс., для масел/ДТ годится); '
             'плиту Л7 купить готовой фрезерованной 450×300 и просверлить самому; брать металл у цеха '
             '(без доставки листов).\n')
    L.append('Не входит: доставка (СДЭК/ТК по весу ~130 кг), минимальный заказ у части цехов '
             '(2 000–15 000 ₽ — на наш объём обычно не влияет), снятие заусенцев/зачистка, '
             'сварка поддона TIG (у вас свой сварщик), НДС у юрлиц без НДС-прайса.\n')
    L.append('## 4. Остальное (для полной картины, грубо)\n')
    L.append('| Статья | ₽ |')
    L.append('|---|---|')
    L.append('| Труба 40×40×2 — 18 м, 40×20×2 — 12 м | 5 000–7 000 |')
    L.append('| Метизы, опоры М12, сантехника слива, клей, шканты | 7 000–11 000 |')
    L.append('| Тиски поворотные 125–150 мм | 5 000–15 000 |')
    L.append('| Фанера 18 мм 2440×1220 ×2 + ЧПУ (у вас свой исполнитель) | 12 000–20 000 |')
    L.append('| Краска/грунт, лак для фанеры | 2 500–4 000 |\n')
    L.append('## 5. Где заказать лазер + гибку нержавейки\n')
    L.append('1. **Онлайн с доставкой по России** — загрузка DXF, расчёт сразу: '
             '[КатШара](https://cutshare.ru/) (заявлены резка и гибка по развёртке DXF, доставка СДЭК), '
             '[LaserMetall](https://www.lasermetall.com/culc) (калькуляторы резки и изделий с гибкой). '
             'Для сверки длины реза: [PrixCut](https://prixcut.ru/).')
    L.append('2. **Москва** (резка + гибка нержавейки, прайсы на сайтах): [Orgplex](https://orgplex.com/lazernaya-rezka-nerzhavejki), '
             '[Svone](https://svone.ru/lazernaya-rezka-metalla/nerzhaveyushchej-stali/), [СиМП](https://www.lazermetal.ru/price/lazernay-rezka/), '
             '[ГК Металлинвест](https://gkmetallinvest.ru/uslugi/lazernaya-rezka/) (металл свой — удобно взять лист + резку в одном месте).')
    L.append('3. **Местный цех** — часто дешевле и без доставки; искать «лазерная резка нержавейки + гибка» '
             'в своём городе, слать файл `Заявка_лазер_гибка.txt` + папку DXF_laser и листы 4–7 PDF. '
             'Брать КП у 2–3 исполнителей.\n')
    L.append('Что уточнить у цеха: (1) есть ли сегментный пуансон под короб Л2 высотой 100 мм с отбортовкой; '
             '(2) их K-фактор/радиус для 1,5 и 3 мм — пересчитают ли развёртки сами; (3) резка 20 мм '
             '(Л7) — лазер или плазма, или купить готовую заготовку; (4) гнуть в плёнке; '
             '(5) доставка или самовывоз.\n')
    L.append('## Источники ставок\n')
    for n, u in SOURCES:
        L.append('- [%s](%s)' % (n, u))
    L.append('')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    return total


def write_rfq(path):
    """Текст заявки для цеха (без личных данных)."""
    from outputs import translit, _mat_short
    lines = ['ЗАЯВКА: лазерная резка + гибка листовых деталей (DXF 1:1, мм)', '',
             'Слои: CUT — рез; BEND_UP / BEND_DOWN — оси гибов «на себя / от себя» относительно вида DXF;',
             'DRILL — сверлить (не резать). BEND/DRILL не кернить. Развёртки: Rвн = t, K = 0,42 —',
             'прошу подтвердить или пересчитать под ваш инструмент. Нержавейку гнуть в плёнке.', '']
    lines.append('%-4s %-30s %-20s %5s %4s %6s  %s' % ('Поз', 'Деталь', 'Материал', 't, мм', 'Кол', 'Гибов', 'Файл'))
    for p in metal_parts():
        fn = '%s_%s_t%s_%dsht.dxf' % (translit(p.code), _mat_short(p.material),
                                       ('%g' % p.t).replace('.', ','), p.qty)
        lines.append('%-4s %-30s %-20s %5g %4d %6d  %s' % (p.code, p.name[:30], p.material[:20], p.t,
                                                          p.qty, len(p.bends), fn))
    lines += ['', 'Особые позиции:',
              '- Л2 поддон: короб %d×%d×(80…%d) с отбортовкой %d мм наружу и 6 упорами 10 мм; стенки' % (
                  TR_LX, TR_LY, round(max(tray_h(0, 0), tray_h(0, TR_LY))), TR_F),
              '  трапециевидные (дно с уклоном ~2 %). Порядок Б3 → Б2 → Б1. Нужны: сегмент пуансона 120–124 мм',
              '  под упоры, секционная матрица, коробчатый секционный пуансон высотой ≥140 мм. Базирование',
              '  Б1 — по таблице на листе 4 (Б1 не параллелен Б2). Отв. ø28 под полумуфту G1/2".',
              '- Л3/Л8 решётки 3 мм: борта 18 мм вниз (контроль 18 +0,2/−0, матрица V16 или пересчёт),',
              '  у Л8 оба боковых борта 48 мм с фасками 45°, у Л3 — один.',
              '- Л4 полка AISI 430: борт 40 вверх; Л10 — 4 вставки (уголки), Л11 — колпак 76×76×12.',
              '- Л7 плита 20 мм: контур лазером (или плазмой — зазор заложен); 4 отв. ø11 в слое DRILL — сверлить.',
              '  Можно вместо резки фрезерованную заготовку 450×300.',
              '- Л1 крышка 430 шлиф.: резать лицом и плёнкой вверх, шлифовка вдоль стороны 1400;',
              '  юбки 19,5 вниз, задний бортик 19,5 вверх, вырез в углу под плиту.',
              '', 'Чертежи: листы 4–7 PDF (поддон, решётки, столешница Б и плита, полка и мелочь).',
              'Прошу: стоимость металла, резки, гибки, сроки, доставка/самовывоз.']
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    t = write_md(os.path.join(ROOT, 'Смета.md'))
    write_rfq(os.path.join(ROOT, 'Заявка_лазер_гибка.txt'))
    print('total', t)
