"""
Builds the player reference guide for Dungeon Travelers 2-2 into docs/guide/*.md.
All figures and data come strictly from the extracted snapshot (build/engine_snapshot.json)
and game binaries. Wording, glossary terms, column headers, and official descriptions
are loaded from data_tables/guide_text.xlsx.
"""
import argparse
import json
import os
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
SNAPSHOT_PATH = os.path.join(PROJECT, 'build', 'engine_snapshot.json')
GUIDE_TEXT_PATH = os.path.join(PROJECT, 'data_tables', 'guide_text.xlsx')
DEFAULT_OUT_DIR = os.path.join(PROJECT, 'docs', 'guide')

MILESTONE_LEVELS = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]


def load_guide_text(path=GUIDE_TEXT_PATH):
    wb = openpyxl.load_workbook(path, read_only=True)
    
    sections = {}
    for row in wb['Sections'].iter_rows(values_only=True):
        if row and row[0] != 'Key':
            sections[row[0]] = {'title': row[1] or '', 'text': row[2] or ''}
            
    glossary = []
    for row in wb['Glossary'].iter_rows(values_only=True):
        if row and row[0] != 'Term':
            glossary.append((row[0], row[1]))
            
    headers = {}
    for row in wb['Headers'].iter_rows(values_only=True):
        if row and row[0] != 'Key':
            headers[row[0]] = row[1]
            
    targets = {}
    for row in wb['Targets'].iter_rows(values_only=True):
        if row and row[0] != 'Code':
            targets[row[0]] = row[1]
            
    ranges = {}
    for row in wb['Ranges'].iter_rows(values_only=True):
        if row and row[0] != 'Code':
            ranges[row[0]] = row[1]
            
    equiptypes = {}
    for row in wb['EquipTypes'].iter_rows(values_only=True):
        if row and row[0] != 'Category_Code':
            cat = row[0]
            t = row[1]
            equiptypes[(cat, t)] = row[2]
            
    class_meta = {}
    for row in wb['ClassMetadata'].iter_rows(values_only=True):
        if row and row[0] != 'Class_ID':
            class_meta[row[0]] = {
                'line': row[1],
                'tier': row[2],
                'route_from': row[3] or ''
            }

    class_profiles = {}
    if 'ClassProfiles' in wb.sheetnames:
        for row in wb['ClassProfiles'].iter_rows(values_only=True):
            if row and row[0] != 'Class_ID':
                class_profiles[row[0]] = row[2] or ''

    skill_descriptions = {}
    if 'SkillDescriptions' in wb.sheetnames:
        for row in wb['SkillDescriptions'].iter_rows(values_only=True):
            if row and row[0] != 'Category':
                cat, sid, sname = row[0], row[1], row[2]
                sdesc = row[3] or ''
                scaling = row[4] or '' if len(row) > 4 else ''
                entry = (sdesc, scaling)
                skill_descriptions[(cat, sid)] = entry
                skill_descriptions[sname] = entry
            
    return {
        'sections': sections,
        'glossary': glossary,
        'headers': headers,
        'targets': targets,
        'ranges': ranges,
        'equiptypes': equiptypes,
        'class_meta': class_meta,
        'class_profiles': class_profiles,
        'skill_descriptions': skill_descriptions,
    }


def load_snapshot(side='vanilla', path=SNAPSHOT_PATH):
    if not os.path.exists(path):
        import subprocess
        subprocess.run([sys.executable, os.path.join(HERE, 'engine_export.py')], check=True)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if side not in data['sides']:
        raise ValueError(f"Side '{side}' not found in {path}. Available sides: {list(data['sides'].keys())}")
    return data['sides'][side]


def build_readme_content(guide_text, snapshot):
    sec = guide_text['sections']
    lines = []
    
    # Title & Scope
    lines.append(sec['readme_title']['title'])
    lines.append('')
    lines.append(sec['readme_title']['text'])
    lines.append('')
    
    # Reading tables
    lines.append(sec['readme_how_to_read']['title'])
    lines.append('')
    lines.append(sec['readme_how_to_read']['text'])
    lines.append('')
    lines.append('Total SP indicates the cumulative Skill Points required to master a skill from level 0 to Max Level (generally 30 SP for 5-level skills and 55 SP for 10-level skills). Effect & Scaling lists both base functionality and exact numerical increases across skill levels.')
    lines.append('')
    
    # Glossary
    lines.append(sec['readme_glossary']['title'])
    lines.append('')
    lines.append(sec['readme_glossary']['text'])
    lines.append('')
    lines.append('| Term | Definition |')
    lines.append('| --- | --- |')
    for term, definition in guide_text['glossary']:
        lines.append(f'| {term} | {definition} |')
    lines.append('')
    
    return '\n'.join(lines)


def get_equipment_counts_for_class(cid, snapshot, guide_text):
    weapons = {}
    armor = {}
    for p in snapshot['equipment']:
        if (p['classes'] >> cid) & 1:
            cat = p['category']
            t = p['type']
            if cat == 0:
                name = guide_text['equiptypes'].get((0, t), f'Type {t}')
                weapons[name] = weapons.get(name, 0) + 1
            else:
                name = guide_text['equiptypes'].get((cat, -1), f'Category {cat}')
                armor[name] = armor.get(name, 0) + 1
    return weapons, armor


def format_skill_cell(s_cat, sid, s_name, guide_text):
    desc, scaling = guide_text['skill_descriptions'].get((s_cat, sid), guide_text['skill_descriptions'].get(s_name, ('', '')))
    parts = []
    if desc:
        parts.append(desc)
    if scaling:
        for line in scaling.splitlines():
            line_clean = line.strip().replace('   |   ', ' | ').replace('|', '\\|')
            if line_clean:
                parts.append(f"- {line_clean}")
    return '<br>'.join(parts) if parts else '-'


def build_classes_content(guide_text, snapshot):
    sec = guide_text['sections']
    h = guide_text['headers']
    lines = []
    
    lines.append(sec['classes_title']['title'])
    lines.append('')
    lines.append(sec['classes_title']['text'])
    lines.append('')
    if sec['classes_intro']['text']:
        lines.append(sec['classes_intro']['text'])
        lines.append('')
        
    class_names = dict(snapshot['class_names'])
    growth_dict = {k: v for k, v in snapshot['growth']}
    skills_list = snapshot['skills']
    
    # Group class modifiers by class ID
    class_mods = {}
    for m in snapshot['class_modifiers']:
        class_mods.setdefault(m['class'], []).append(m)
        
    # Group classes by line
    lines_by_name = {}
    for cid in range(32):
        meta = guide_text['class_meta'].get(cid, {})
        line_name = meta.get('line', 'Other')
        lines_by_name.setdefault(line_name, []).append(cid)
        
    for line_name, class_ids in lines_by_name.items():
        lines.append('---')
        lines.append('')
        lines.append(f'## {line_name} Line')
        lines.append('')
        
        for cid in class_ids:
            cname = class_names[cid]
            meta = guide_text['class_meta'].get(cid, {})
            tier = meta.get('tier', '')
            route_from = meta.get('route_from', '')
            profile = guide_text['class_profiles'].get(cid, '')
            
            lines.append('---')
            lines.append('')
            lines.append(f'### {cname}')
            lines.append('')
            
            # Classification details
            tier_info = f'- **{h["tier"]}:** {tier}'
            if route_from:
                tier_info += f' ({h["route"]}: {route_from})'
            lines.append(tier_info)
            lines.append('')
            
            # Class Overview & Role
            if profile:
                lines.append(sec['overview_section']['title'])
                lines.append('')
                lines.append(f'> {profile}')
                lines.append('')
                
            # Weapon specialty modifiers
            mods_for_class = class_mods.get(cid, [])
            if mods_for_class:
                lines.append(sec['modifier_section']['title'])
                lines.append('')
                lines.append(sec['modifier_section']['text'])
                lines.append('')
                
                has_prev = any(m['previous'] is not None for m in mods_for_class)
                if has_prev:
                    lines.append(f'| {h["route"]} | {h["slot"]} | {h["equipment_type"]} | {h["bonus"]} |')
                    lines.append('| --- | --- | --- | --- |')
                    for m in mods_for_class:
                        p_name = class_names[m['previous']] if m['previous'] is not None else 'Any'
                        for entry in m['entries']:
                            slot_name = 'Weapon' if entry['slot'] == 0 else ('Shield' if entry['slot'] == 1 else 'Accessory')
                            eq_name = guide_text['equiptypes'].get((0, entry['type']), '-') if entry['slot'] == 0 else slot_name
                            bonus_pct = f"+{round(entry['modifier'] * 100)}%"
                            lines.append(f'| From {p_name} | {slot_name} | {eq_name} | {bonus_pct} |')
                else:
                    lines.append(f'| {h["slot"]} | {h["equipment_type"]} | {h["bonus"]} |')
                    lines.append('| --- | --- | --- |')
                    for m in mods_for_class:
                        for entry in m['entries']:
                            slot_name = 'Weapon' if entry['slot'] == 0 else ('Shield' if entry['slot'] == 1 else 'Accessory')
                            eq_name = guide_text['equiptypes'].get((0, entry['type']), '-') if entry['slot'] == 0 else slot_name
                            bonus_pct = f"+{round(entry['modifier'] * 100)}%"
                            lines.append(f'| {slot_name} | {eq_name} | {bonus_pct} |')
                lines.append('')
                
            # Usable Equipment
            weapons, armor = get_equipment_counts_for_class(cid, snapshot, guide_text)
            lines.append(sec['equip_section']['title'])
            lines.append('')
            if sec['equip_section']['text']:
                lines.append(sec['equip_section']['text'])
                lines.append('')
            weapon_str = ', '.join(f'{w} ({cnt})' for w, cnt in sorted(weapons.items()))
            armor_str = ', '.join(f'{a} ({cnt})' for a, cnt in sorted(armor.items()))
            lines.append(f'- **{h["weapon_types"]}:** {weapon_str}')
            lines.append(f'- **{h["gear_categories"]}:** {armor_str}')
            lines.append('')
            
            # Stat growth
            lines.append(sec['growth_section']['title'])
            lines.append('')
            growth_info = snapshot['growth_row'][str(cid)]
            
            if 'by_previous' in growth_info:
                for prev_cid, row_idx in growth_info['by_previous']:
                    prev_name = class_names[prev_cid]
                    lines.append(f'##### Route from {prev_name}')
                    lines.append('')
                    lines.append(f'| {h["level"]} | {h["hp"]} | {h["tp"]} | {h["atk"]} | {h["def"]} | {h["int"]} | {h["res"]} | {h["dex"]} | {h["agi"]} |')
                    lines.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
                    row_data = growth_dict[row_idx]
                    for lvl in MILESTONE_LEVELS:
                        st = row_data[lvl - 1]
                        lines.append(f'| {lvl} | {st[6]} | {st[7]} | {st[0]} | {st[1]} | {st[2]} | {st[3]} | {st[4]} | {st[5]} |')
                    lines.append('')
            else:
                row_idx = growth_info['row']
                row_data = growth_dict[row_idx]
                lines.append(f'| {h["level"]} | {h["hp"]} | {h["tp"]} | {h["atk"]} | {h["def"]} | {h["int"]} | {h["res"]} | {h["dex"]} | {h["agi"]} |')
                lines.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
                for lvl in MILESTONE_LEVELS:
                    st = row_data[lvl - 1]
                    lines.append(f'| {lvl} | {st[6]} | {st[7]} | {st[0]} | {st[1]} | {st[2]} | {st[3]} | {st[4]} | {st[5]} |')
                lines.append('')
                
            # Learned skills
            learned = [s for s in skills_list if cid in s['classes']]
            lines.append(sec['skills_section']['title'])
            lines.append('')
            if learned:
                lines.append(f'| {h["skill"]} | {h["category"]} | {h["max_lv"]} | {h["sp_cost"]} | {h["target"]} | {h["range"]} | {h["description"]} |')
                lines.append('| --- | --- | --- | --- | --- | --- | --- |')
                for s in learned:
                    s_name = s['name']
                    s_cat = s['category']
                    max_lv = s['levels']
                    sp_list = s['sp'][:max_lv] if s['sp'] else []
                    total_sp = sum(sp_list)
                    sp_str = f'{total_sp} SP' if total_sp > 0 else '0 SP'
                    tgt_code = s['target'] if s['target'] is not None else -1
                    tgt_str = guide_text['targets'].get(tgt_code, '-')
                    rng_code = s['range'] if s['range'] is not None else -1
                    rng_str = guide_text['ranges'].get(rng_code, '-')
                    cell_desc = format_skill_cell(s_cat, s['id'], s_name, guide_text)
                    lines.append(f'| {s_name} | {s_cat} | {max_lv} | {sp_str} | {tgt_str} | {rng_str} | {cell_desc} |')
                lines.append('')
            else:
                lines.append('No skills learned directly.')
                lines.append('')
                
    return '\n'.join(lines)


def build_guide(side='vanilla', out_dir=DEFAULT_OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    guide_text = load_guide_text()
    snapshot = load_snapshot(side=side)
    
    # 1. README.md
    readme_path = os.path.join(out_dir, 'README.md')
    readme_content = build_readme_content(guide_text, snapshot)
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
        
    # 2. classes.md
    classes_path = os.path.join(out_dir, 'classes.md')
    classes_content = build_classes_content(guide_text, snapshot)
    with open(classes_path, 'w', encoding='utf-8') as f:
        f.write(classes_content)
        
    return {
        'README.md': readme_content,
        'classes.md': classes_content
    }


def main():
    parser = argparse.ArgumentParser(description='Build player reference guide from game snapshot.')
    parser.add_argument('side', nargs='?', default='vanilla', choices=['vanilla', 'variant'],
                        help='Data side to build guide for (default: vanilla)')
    parser.add_argument('--out', default=DEFAULT_OUT_DIR, help='Output directory for markdown files')
    args = parser.parse_args()
    
    res = build_guide(side=args.side, out_dir=args.out)
    print(f"Successfully generated guide for side '{args.side}' in {args.out}")
    for fname in res:
        print(f" - {fname}")


if __name__ == '__main__':
    main()
