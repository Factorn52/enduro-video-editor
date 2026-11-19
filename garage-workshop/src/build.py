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

def hardware():
    """Покупное и метизы — количества считаются из геометрии (а не вписаны руками)."""
    cap = cap_flat()
    n_cap = len(cap.circles)
    n_ply = len(ply_screws())
    n_anchor = len(BT_ANCHOR) * 3 * PN_N
    n_pscr = len(PN_MOUNT_X) * len(PN_MOUNT_Y) * PN_N
    n_acc = sum(1 for p in acc_parts() if p.code.endswith('.1'))
    st40 = len(cut_sticks([(t.code, t.L) for t in tubes() if t.profile == '40х40х2' for _ in range(t.qty)]))
    st20 = [s for s in cut_sticks([(t.code, t.L) for t in tubes() if t.profile == '40х20х2' for _ in range(t.qty)])]
    last20 = sum(L for _, L in st20[-1]) + 3 * len(st20[-1]) + 20
    tube20 = '%d×6 м' % len(st20) if last20 > 2000 else '%d×6 м + %.1f м' % (len(st20) - 1, last20 / 1000 + 0.05)
    return [
        ('Опора регулируемая М12, пята ø%d (≤35!), h пяты ≤15, шпилька ≥60' % FOOT_BASE_D, '8 шт', 'крепёж'),
        ('Гайка М12 без цинка (приварить к подпятнику Л5)', '8 шт', 'крепёж'),
        ('Болт М8×110 + гайка DIN 985 (стяжка модулей; шайбы — Л9)', '4 к-т', 'крепёж'),
        ('Анкер/рамный дюбель М8 (уши Т8 к стене)', '%d шт' % N_MOD, 'строймаг'),
        ('Полумуфта приварная G1/2" AISI 304 (наружн. ø≈28)', '1 шт', 'нерж. сантехника'),
        ('Кран шаровой 1/2" нар.–вн., полнопроходной', '1 шт', 'сантехника'),
        ('Штуцер-ёлочка 1/2" нар. × 12 мм', '1 шт', 'сантехника'),
        ('Шланг маслобензостойкий ø12, 1 м + хомут', '1 к-т', 'автомагазин'),
        ('Канистра 20 л, полупрозрачная (h ≤ 470)', '1 шт', 'автомагазин'),
        ('Тиски слесарные поворотные 125–150 мм', '1 шт', 'инструмент'),
        ('Мягкие губки + призма под ø48–60 к тискам', '1 к-т', 'инструмент'),
        ('Болт М12 (длина ≤ лапа тисков + 18) + шайба', '4 шт', 'крепёж'),
        ('Болт М10×80 потай DIN 7991 + шайба + гайка DIN 985 (плита Л7)', '4 к-т', 'крепёж'),
        ('Саморез с крылышками 4,8×38 (фанера Щ к каркасу)', '%d шт' % n_ply, 'крепёж'),
        ('Клей-герметик МС-полимер (крышка Л1, зазор у плиты)', '2 тубы', 'строймаг'),
        ('Саморез нерж. 4,2×16 п/кр (юбка крышки)', '%d шт' % n_cap, 'крепёж'),
        ('Рамный дюбель 8×80 (рейки к стене)', '%d шт' % n_anchor, 'строймаг'),
        ('Саморез 4,5×35 (панели к рейкам)', '%d шт' % n_pscr, 'строймаг'),
        ('Шкант мебельный берёзовый 8×40', '100 шт', 'строймаг'),
        ('Саморез 4×30 (держатель к панели, по 1)', '%d шт' % n_acc, 'строймаг'),
        ('Саморез 4×40 + ПВА D3 (сборка держателей)', '20 шт', 'строймаг'),
        ('Саморез 5×35 (крюки под тяжёлое в рейки)', '10 шт', 'строймаг'),
        ('Лак 2К полиуретановый для фанеры', '1 л', 'строймаг'),
        ('Порошковая окраска каркасов или 2К эпокс. грунт + 2К ПУ', '—', 'для каркасов'),
        ('Тумба инструментальная на колёсах, h ≤ 870 (опц.)', '1 шт', 'инструмент'),
        ('', '', ''),
        ('МАТЕРИАЛЫ К ЗАКУПКЕ', '', ''),
        ('Труба профильная 40×40×2', '%d×6 м' % st40, 'металлобаза'),
        ('Труба профильная 40×20×2', tube20, 'металлобаза'),
        ('Уголок 40×40×4 (Т8) / труба 16×2,5 (Т9)', '0,1 м / 0,2 м', 'металлобаза'),
        ('Лист AISI 304, 1,5 мм, 1000×2000 (Л2, Л11)', '1 лист', 'лазерный цех'),
        ('Лист AISI 304, 3 мм, 1000×2000 (решётки Л3, Л8)', '1 лист', 'лазерный цех'),
        ('Лист AISI 430 шлиф., 1,5 мм, 1000×2000 (крышка Л1)', '1 лист', 'лазерный цех'),
        ('Лист AISI 430, 1,5 мм, 1000×2000 (полка Л4, Л10)', '1 лист', 'лазерный цех'),
        ('Ст3 4 мм — обрезок 450×200 (Л5, Л6, Л9)', '1 шт', 'лазерный цех'),
        ('Ст45 20 мм — заготовка 490×340 (или фрезер. 450×300)', '1 шт', 'лазер/плазма'),
        ('Фанера берёзовая ФК 18 мм, %d×%d, сорт 2/2+' % (PLY_SW, PLY_SH), '2 листа', 'ЧПУ-цех'),
    ]


HARDWARE = hardware()


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
        write_nest_dxf(PLY_SW, PLY_SH, L, os.path.join(D_CNC, 'NEST_fanera_list%d.dxf' % (k + 1)),
                       name)
    # --- проверка (после записи DXF — она их перечитывает)
    import check
    rep = check.run()
    with open(os.path.join(ROOT, 'Проверка_размеров.txt'), 'w', encoding='utf-8') as f:
        f.write('Автоматическая проверка размеров и стыковок (src/check.py)\n\n')
        f.write('\n'.join(rep) + '\n')
    print('check: %d OK' % len(rep))
    # --- смета и заявка для цеха
    import cost
    cost.write_md(os.path.join(ROOT, 'Смета.md'))
    cost.write_rfq(os.path.join(ROOT, 'Заявка_лазер_гибка.txt'))
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
            S.sheet_grates(), S.sheet_topB(), S.sheet_small(), S.sheet_spec(HARDWARE),
            S.sheet_panels(), S.sheet_ply_nest(pn), S.sheet_metal_nest(mn)]
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
