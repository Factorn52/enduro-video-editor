# -*- coding: utf-8 -*-
"""Сборка всего комплекта: PDF-чертежи, DXF для лазера и ЧПУ, CSV-спецификация.

    python3 build.py            -> ../ (PDF, DXF_laser/, DXF_cnc_fanera/, *.csv)
    python3 build.py --png DIR  -> дополнительно PNG-превью листов
"""
import os
import sys
import shutil
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geom import *                                  # noqa
from outputs import *                               # noqa
import sheets as S                                  # noqa
from draw import fmt                                # noqa

ROOT = os.path.abspath(os.path.join(HERE, '..'))
PDF = os.path.join(ROOT, 'Чертежи_верстак_и_панели.pdf')
D_LASER = os.path.join(ROOT, 'DXF_laser')
D_CNC = os.path.join(ROOT, 'DXF_cnc_fanera')

HARDWARE = [
    ('Опора регулируемая М12, шарнирная, основание ø40–50', '8 шт', 'крепёж/маркетплейс'),
    ('Гайка М12 (приварить к подпятнику Л5)', '8 шт', 'крепёж'),
    ('Болт М8×100 + 2 шайбы + гайка М8 нейлон (стяжка модулей)', '4 к-т', 'крепёж'),
    ('Полумуфта приварная G1/2" AISI 304', '1 шт', 'нерж. сантехника'),
    ('Кран шаровой 1/2" нар.–вн.', '1 шт', 'сантехника'),
    ('Штуцер-ёлочка 1/2" нар. × 12 мм', '1 шт', 'сантехника'),
    ('Шланг маслобензостойкий ø12, 1 м + хомут', '1 к-т', 'автомагазин'),
    ('Канистра 10 л (высота ≤ 400 мм)', '1 шт', 'автомагазин'),
    ('Тиски слесарные поворотные 125–150 мм', '1 шт', 'инструмент'),
    ('Болт М12×90 + шайбы + гайка (тиски сквозь Л7)', '4 к-т', 'крепёж'),
    ('Саморез по дереву 4,5×30 (фанера к каркасу снизу)', '12 шт', 'крепёж'),
    ('Саморез 4×30 + клей ПВА D3 (склейка 2 слоёв Щ1)', '20 шт', 'крепёж'),
    ('Клей-герметик МС-полимер (крышка Л1 к фанере)', '1 туба', 'строймаг'),
    ('Саморез нерж. 4,2×16 п/кр (юбка крышки)', '10 шт', 'крепёж'),
    ('Дюбель-гвоздь 6×60 (рейки к стене)', '27 шт', 'строймаг'),
    ('Саморез 4,5×35 (панели к рейкам)', '36 шт', 'строймаг'),
    ('Шкант мебельный берёзовый 8×40', '100 шт', 'строймаг'),
    ('Саморез 4×40 + ПВА (сборка держателей А1–А3)', '20 шт', 'строймаг'),
    ('Масло/лак для фанеры', '1 л', 'строймаг'),
    ('Грунт + эмаль по металлу (или порошок)', '—', 'для каркасов'),
    ('Тумба инструментальная на колёсах, h ≤ 800 (опц.)', '1 шт', 'инструмент'),
    ('', '', ''),
    ('МАТЕРИАЛЫ К ЗАКУПКЕ', '', ''),
    ('Труба профильная 40×40×2', '3×6 м', 'металлобаза'),
    ('Труба профильная 40×20×2', '2×6 м', 'металлобаза'),
    ('Лист AISI 304, 1,5 мм, 1000×2000 (поддон Л2)', '1 лист', 'лазерный цех'),
    ('Лист AISI 304, 3 мм, 1000×2000 (решётки Л3)', '1 лист', 'лазерный цех'),
    ('Лист AISI 430 шлиф., 1,5 мм, 1000×2000 (крышка Л1)', '1 лист', 'лазерный цех'),
    ('Лист Ст 08пс, 1,5 мм, 1000×2000 (полка Л4)', '1 лист', 'лазерный цех'),
    ('Ст3 4 мм (Л5, Л6) и 6 мм (Л7) — обрезки', '—', 'лазерный цех'),
    ('Фанера берёзовая ФК 18 мм, 1525×1525, сорт 2/2 и выше', '4 листа', 'ЧПУ-цех'),
]


def main(png_dir=None):
    for d in (D_LASER, D_CNC):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)
    # --- DXF деталей
    laser_files = []
    for p in metal_parts():
        laser_files.append((p, write_part_dxf(p, D_LASER)))
    for p in ply_parts():
        write_part_dxf(p, D_CNC)
    # --- раскладки
    mn = metal_nest()
    for sh in mn:
        write_nest_dxf(sh['w'], sh['h'], sh['parts'], os.path.join(D_LASER, sh['file']), sh['title'])
    pn = ply_nest()
    for k, (name, L) in enumerate(pn):
        write_nest_dxf(PLY_SHEET, PLY_SHEET, L, os.path.join(D_CNC, 'NEST_fanera_list%d.dxf' % (k + 1)),
                       name)
    # --- CSV спецификация
    rows = []
    for t in tubes():
        rows.append(('Труба', t.code, t.name, t.profile, fmt(t.L), t.qty, t.note))
    for p, fn in laser_files:
        w, h = p.size()
        rows.append(('Лазер+гибка', p.code, p.name, '%s %s мм' % (p.material, fmt(p.t)),
                     '%s×%s' % (fmt(w), fmt(h)), p.qty, fn))
    for p in ply_parts():
        w, h = p.size()
        rows.append(('Фанера ЧПУ', p.code, p.name, p.material, '%s×%s' % (fmt(w), fmt(h)), p.qty,
                     'отв.: %d' % len(p.drills)))
    for a, b, c in HARDWARE:
        if a:
            rows.append(('Покупное', '', a, '', '', b, c))
    write_spec_csv(os.path.join(ROOT, 'Спецификация.csv'),
                   ['Тип', 'Поз.', 'Наименование', 'Материал/профиль', 'Размер', 'Кол.', 'Примечание'],
                   rows)
    # --- PDF
    figs = [S.sheet1(), S.sheet_frame('A'), S.sheet_frame('B'), S.sheet_tray(),
            S.sheet_grate_cap(), S.sheet_small(), S.sheet_spec(HARDWARE), S.sheet_panels(),
            S.sheet_ply_nest(pn), S.sheet_metal_nest(mn)]
    with PdfPages(PDF) as pdf:
        for f in figs:
            pdf.savefig(f)
        d = pdf.infodict()
        d['Title'] = 'Гараж 6x3: верстак сдвоенный и стеновые панели'
    if png_dir:
        os.makedirs(png_dir, exist_ok=True)
        for k, f in enumerate(figs):
            f.savefig(os.path.join(png_dir, 'sheet%02d.png' % (k + 1)), dpi=110)
    for f in figs:
        plt.close(f)
    print('PDF:', PDF)
    print('DXF laser:', len(os.listdir(D_LASER)), 'files; DXF cnc:', len(os.listdir(D_CNC)), 'files')


if __name__ == '__main__':
    png = None
    if '--png' in sys.argv:
        png = sys.argv[sys.argv.index('--png') + 1]
    main(png)
