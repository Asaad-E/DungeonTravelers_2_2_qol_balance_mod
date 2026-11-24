"""Balance scorecard (docs/generated/BALANCE_SCORECARD.md): pairs every primary balance metric with a counterbalancing
guardrail metric and reads them through a three-zone compass (GREEN / AMBER / RED) rather than binary pass/fail.

Reads only the generated reports and workbooks; plays no battles. Run by tools/full_suite.py after verdicts.py.
"""
import json
import math
import os
import re
import statistics
import sys

import openpyxl

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED = os.path.join(PROJECT, 'docs', 'generated')
MEASURES = os.path.join(PROJECT, 'measures')
OUT = os.path.join(GENERATED, 'BALANCE_SCORECARD.md')


def read_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        return f.read().splitlines()


def table(lines, header_start):
    for i, line in enumerate(lines):
        if line.startswith(header_start):
            rows = []
            for row in lines[i + 2:]:
                if not row.startswith('|'):
                    break
                rows.append([c.strip() for c in row.strip().strip('|').split('|')])
            return rows
    return []


def num(text):
    m = re.search(r'[+-]?\d+(?:\.\d+)?', str(text))
    return float(m.group(0)) if m else 0.0


def load_settings():
    wb = openpyxl.load_workbook(os.path.join(PROJECT, 'data_tables', 'sim_setup.xlsx'), read_only=True)
    try:
        s = {r[0]: r[1] for r in wb['Settings'].iter_rows(min_row=2, values_only=True) if r[0]}
        late = next((r[1] for r in wb['ClassStages'].iter_rows(min_row=2, values_only=True) if r[0] == 'late'), '')
        return s, [x.strip() for x in str(late).split(';') if x.strip()]
    finally:
        wb.close()


def main():
    s, late_cids = load_settings()
    with open(os.path.join(PROJECT, 'data_tables', 'measure_config.json'), encoding='utf-8') as f:
        cfg = json.load(f)

    check_runs = int(s.get('check_runs', 40))
    ci95 = 1.96 * math.sqrt(0.25 / max(1, check_runs)) * 100.0
    scan_runs = int(cfg['class_search']['presets']['balance']['scan'])

    rows_out = []

    # 1. Story difficulty <-> Party battery diversity & resource guardrails
    dc_lines = read_lines(os.path.join(GENERATED, 'DIFFICULTY_CURVE.md'))
    dc_rows = table(dc_lines, '| Checkpoint | Level')
    dc_within = sum(1 for r in dc_rows if r[-1] == 'within')
    dc_easier = sum(1 for r in dc_rows if 'easier' in r[-1])
    dc_harder = sum(1 for r in dc_rows if 'harder' in r[-1] and 'easier' not in r[-1])
    early_wipes = []
    for r in dc_rows:
        if len(r) >= 9:
            parts = r[7].split('>')
            if len(parts) == 2 and num(parts[1]) - num(parts[0]) >= 10:
                early_wipes.append(f'{r[0]} ({parts[0].strip()}->{parts[1].strip()})')

    pb_lines = read_lines(os.path.join(GENERATED, 'PARTY_BATTERY.md'))
    pb_sum = table(pb_lines, '| Archetype | Above floor')
    worst_arch = ''
    total_pb_drops = 0
    if pb_sum:
        scored = [(num(r[2]), r[0], r[3]) for r in pb_sum]
        scored.sort()
        worst_arch = f'{scored[0][1]} {scored[0][0]:+.1f} pp (drops>=15: {scored[0][2]})'
        total_pb_drops = sum(int(num(r[3].split()[0])) for r in pb_sum if r[3] != '0')
    dc_zone = 'GREEN'
    if dc_easier >= 3 or dc_harder >= 4 or total_pb_drops >= 6:
        dc_zone = 'RED'
    elif dc_easier > 0 or dc_harder > 0 or total_pb_drops >= 3 or early_wipes:
        dc_zone = 'AMBER'
    rows_out.append((
        'Story difficulty',
        f'{dc_within}/{len(dc_rows)} within ({dc_easier} easier, {dc_harder} harder)',
        f'Worst archetype: {worst_arch or "n/a"}; total >=15pp drops: {total_pb_drops}' + (f'; early-wipe spikes: {", ".join(early_wipes)}' if early_wipes else ''),
        dc_zone,
        'Avoid tuning Meta at the expense of Mage-Heavy / Dual-Support.',
    ))

    # 2. Postgame easier <-> harder + 0% collapses
    pg_lines = read_lines(os.path.join(MEASURES, 'POSTGAME_COMPARE.md'))
    pg_rows = table(pg_lines, '| Boss | Class | Crown')
    pg_reached, pg_easier, pg_harder, pg_zero = 0, [], [], []
    for r in pg_rows:
        if 'floor not reached' in r[2]:
            continue
        pg_reached += 1
        v, m = [num(x) for x in r[3].split('>')]
        cid = r[0].split()[0]
        if m - v > 15:
            pg_easier.append(f'{cid} ({v:.0f}%->{m:.0f}%)')
        elif v - m > 15:
            pg_harder.append(f'{cid} ({v:.0f}%->{m:.0f}%)')
        if m == 0 and v > 0:
            pg_zero.append(f'{cid} ({v:.0f}%->0%)')
    pg_zone = 'RED' if (len(pg_easier) >= 3 or len(pg_zero) > 0) else ('AMBER' if (len(pg_easier) > 0 or len(pg_harder) >= 5) else 'GREEN')
    rows_out.append((
        'Postgame balance',
        f'{len(pg_easier)} easier of {pg_reached} floor-reached ({", ".join(pg_easier[:4]) or "none"})',
        f'{len(pg_harder)} harder; 0% collapses: {", ".join(pg_zero) or "0"}',
        pg_zone,
        'Zero-win collapses (vanilla winnable -> 0%) are high-priority player pain points.',
    ))

    # 3. Class balance <-> Class stages (late diversity) + drops + monotonic fastest share
    cb_lines = read_lines(os.path.join(GENERATED, 'CLASS_BALANCE.md'))
    cb_band = table(cb_lines, '| Class | Wins | Deviations')
    cb_scan = table(cb_lines, '| Class | Cells')
    in_band = sum(1 for r in cb_band if r[-1] == 'yes')
    out_classes = [f'{r[0]} ({r[-1]})' for r in cb_band if r[-1] != 'yes']
    cb_head = next((l for l in cb_lines if 'Confirmed:' in l), '')
    m_dom = re.search(r'Confirmed:\s*(\d+)\s*dominant.*?,\s*(\d+)\s*drops', cb_head)
    dom_cnt = int(m_dom.group(1)) if m_dom else 0
    drop_cnt = int(m_dom.group(2)) if m_dom else 0
    top_fast = max(((num(r[5].split('>')[1]), r[0]) for r in cb_scan if '>' in r[5]), default=(0.0, '?'))

    cs_lines = read_lines(os.path.join(GENERATED, 'CLASS_STAGES.md'))
    cs_head = next((l.strip('*') for l in cs_lines if 'role and stage rows' in l), '')
    m_cs = re.search(r'(\d+)\s+of\s+(\d+).*?,\s*(\d+)\s+slow or weak', cs_head)
    cs_in = int(m_cs.group(1)) if m_cs else 0
    cs_tot = int(m_cs.group(2)) if m_cs else 0
    cs_out = int(m_cs.group(3)) if m_cs else 0
    cb_zone = 'RED' if (dom_cnt > 0 or len(out_classes) >= 2 or cs_out >= 3) else ('AMBER' if (len(out_classes) == 1 or cs_out > 0 or drop_cnt >= 45) else 'GREEN')
    rows_out.append((
        'Class balance & stages',
        f'{in_band}/{len(cb_band)} final classes in band, {dom_cnt} dominant ({", ".join(out_classes) or "all yes"})',
        f'ClassStages {cs_in}/{cs_tot} within ({len(late_cids)} late bosses); {drop_cnt} drops; top fastest-5% share: {top_fast[1]} {top_fast[0]:.0f}%',
        cb_zone,
        'Track monotonic fastest-5% share + late ClassStages alongside z-band to avoid midgame overfitting.',
    ))

    # 4. Random battles
    rb_lines = read_lines(os.path.join(MEASURES, 'RANDOM_BATTLES.md'))
    rb_rows = table(rb_lines, '| Floor of | Level')
    rb_within = sum(1 for r in rb_rows if r[-1] == 'within')
    rb_easier = sum(1 for r in rb_rows if 'easier' in r[-1])
    rb_harder = sum(1 for r in rb_rows if 'harder' in r[-1] and 'easier' not in r[-1])
    rb_zero = sum(1 for r in rb_rows if '>' in r[2] and num(r[2].split('>')[1]) == 0)
    rb_zone = 'RED' if rb_harder >= 3 else ('AMBER' if (rb_easier >= 4 or rb_harder > 0) else 'GREEN')
    rows_out.append((
        'Random battles (30-chain)',
        f'{rb_within}/{len(rb_rows)} floors within ({rb_easier} easier, {rb_harder} harder)',
        f'{rb_zero} floors at 0% chain survival (30-fight no-heal chain stress test)',
        rb_zone,
        'Informational for attrition; 30-battle no-heal chains are harsher than real play.',
    ))

    # 5. Skills & Uniques
    sb_lines = read_lines(os.path.join(GENERATED, 'SKILL_BATTERY.md'))
    sb_rows = table(sb_lines, '| Skill | Kind')
    sv_lines = read_lines(os.path.join(GENERATED, 'SKILL_BATTERY_VARIANTS.md'))
    sv_map = {r[0]: r for r in table(sv_lines, '| Skill | Kind')}
    sb_eff = [sv_map.get(r[0], r) for r in sb_rows]
    dead_cnt = sum(1 for r in sb_eff if r[-1] == 'dead')
    hurts_cnt = sum(1 for r in sb_eff if r[-1] == 'hurts')
    high_backfire = sum(1 for r in sb_eff if num(r[5]) >= 25)
    ub_head = next((l.strip('*') for l in read_lines(os.path.join(GENERATED, 'UNIQUE_BATTERY.md')) if l.startswith('**')), '')
    sk_zone = 'RED' if (hurts_cnt > 0 or dead_cnt >= 8) else ('AMBER' if (dead_cnt > 0 or high_backfire >= 15) else 'GREEN')
    rows_out.append((
        'Skills & uniques',
        f'{len(sb_eff)} skills: {dead_cnt} dead, {hurts_cnt} hurts (after rule variants)',
        f'{high_backfire} skills with >=25% worse-cells under fixed AI rules; Uniques: {ub_head.split(".")[0]}',
        sk_zone,
        'Niche skills can backfire under fixed AI rules; focus fixes on hurts / dead.',
    ))

    # 6. Mercenaries
    mb_part = os.path.join(GENERATED, 'mercenary_battery', 'part_1.json')
    low_m, high_m = cfg['skill_battery']['mercenary_band']
    exempt_m = set(cfg['skill_battery']['mercenary_band_exempt'])
    m_over, m_under = [], []
    if os.path.exists(mb_part):
        with open(mb_part, encoding='utf-8') as f:
            mdata = json.load(f)
        for r in mdata:
            name = r['guest']
            if name in exempt_m or not r.get('profile'):
                continue
            ps = r['profile']
            w = statistics.mean(p['wins'] for p in ps if p.get('wins') is not None)
            l = statistics.mean([p['length'] for p in ps if p.get('length') is not None] or [0.0])
            tot = w + l
            if tot > high_m:
                m_over.append(f'{name} ({tot*100:.1f})')
            elif tot < low_m:
                m_under.append(f'{name} ({tot*100:.1f})')
    m_zone = 'RED' if len(m_over) >= 10 else ('AMBER' if (m_over or m_under) else 'GREEN')
    rows_out.append((
        'Mercenaries',
        f'Band {low_m*100:.0f}-{high_m*100:.0f} pts: {len(m_over)} above, {len(m_under)} below',
        f'Above: {", ".join(m_over[:5]) or "none"}' + (f' (+{len(m_over)-5} more)' if len(m_over) > 5 else '') + f'; Below: {", ".join(m_under) or "none"}',
        m_zone,
        'Review strong mercenaries (e.g. Euthys) before concluding postgame is too easy.',
    ))

    # 7. Process & Anti-Goodhart safeguards
    brc_rows = table(read_lines(os.path.join(MEASURES, 'BOSS_ROWS_CHECK.md')), '| Boss | Rows')
    brc_unneeded = [r[0] for r in brc_rows if 'not needed' in r[-1]]
    brc_nobetter = [r[0] for r in brc_rows if 'no better' in r[-1]]
    ver_lines = read_lines(os.path.join(GENERATED, 'VERDICTS.md'))
    ver_open = sum(1 for r in table(ver_lines, '| ID |') if len(r) >= 4 and r[3].lower() == 'open')

    counts = {z: sum(1 for x in rows_out if x[3] == z) for z in ('GREEN', 'AMBER', 'RED')}
    md = [
        '# Balance Scorecard & Guardrail Compass (generated)',
        '',
        'Generated by `tools/balance_scorecard.py` (reads suite reports; plays no battles). Each primary target is paired with a counterbalancing guardrail to prevent Goodhart overfitting.',
        '',
        f'**Compass summary: {counts["GREEN"]} GREEN, {counts["AMBER"]} AMBER, {counts["RED"]} RED.**',
        '',
        '> **How to read the compass:** `GREEN` = healthy; `AMBER` = borderline or intentional design trade-off (review, do **not** reflexively micro-patch); `RED` = statistically real regression, exploit, or `0%` collapse requiring attention.',
        '',
        '## Paired Guardrail Metrics',
        '',
        '| Area | Primary metric | Counterbalancing guardrail | Compass | Guidance |',
        '|---|---|---|---|---|',
    ]
    for area, prim, guard, zone, note in rows_out:
        md.append(f'| {area} | {prim} | {guard} | **{zone}** | {note} |')

    md.extend([
        '',
        '## Process & Anti-Goodhart Safeguards',
        '',
        '| Safeguard | Current reading | Why it matters |',
        '|---|---|---|',
        f'| Difficulty / Postgame sample size | `check_runs = {check_runs}` (95% CI +-`{ci95:.1f}` pp at 50%) | Prevents tuning boss stats to random seed noise inside the +-10 pp window |',
        f'| Class-search scan precision | `scan = {scan_runs}` runs/cell across 8,800 cells | Cuts discretization noise in top-5% fastest party identification |',
        f'| Late ClassStages boss diversity | {len(late_cids)} bosses (`{", ".join(late_cids)}`) | Avoids a single anti-magic or anti-physical boss deciding 50% of late verdicts |',
        f'| Unneeded boss overrides (`BOSS_ROWS_CHECK.md`) | {len(brc_unneeded)} `not needed`, {len(brc_nobetter)} `no better` | Flags stale boss stat rows that no longer earn their keep |',
        f'| Open register verdicts (`VERDICTS.md`) | {ver_open} open | Tracks unresolved balance register items |',
    ])

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    print(f'scorecard: {counts["GREEN"]} GREEN, {counts["AMBER"]} AMBER, {counts["RED"]} RED -> {os.path.relpath(OUT, PROJECT)}')
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
