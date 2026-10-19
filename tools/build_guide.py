"""
Builds the player reference guide for Dungeon Travelers 2-2 into docs/guide/*.md.
All figures and data come strictly from the extracted snapshot (build/engine_snapshot.json)
and game binaries. Wording, glossary terms, column headers, and official descriptions
are loaded from data_tables/guide_text.xlsx.
"""
import argparse
import json
import os
import re
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import enemy_ai
import enemy_data

SNAPSHOT_PATH = os.path.join(PROJECT, 'build', 'engine_snapshot.json')
GUIDE_TEXT_PATH = os.path.join(PROJECT, 'data_tables', 'guide_text.xlsx')
SOT_PATH = os.path.join(PROJECT, 'data_tables', 'vanilla_source_of_truth.xlsx')
SETUP_PATH = os.path.join(PROJECT, 'data_tables', 'sim_setup.xlsx')
DEFAULT_OUT_DIR = os.path.join(PROJECT, 'docs', 'guide')

MILESTONE_LEVELS = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]
ATTR_NAMES = {0: 'Weapon', 1: 'Slash', 2: 'Stab', 3: 'Bash', 4: 'Fire', 5: 'Water', 6: 'Wind', 7: 'Earth', 8: 'Lightning', 9: 'Neutral'}


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
            
    formulas = []
    if 'Formulas' in wb.sheetnames:
        for row in wb['Formulas'].iter_rows(values_only=True):
            if row and row[0] != 'Key':
                formulas.append({
                    'key': row[0],
                    'title': row[1] or '',
                    'formula': row[2] or '',
                    'summary': row[3] or ''
                })

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
        'formulas': formulas,
    }


def load_source_of_truth(path=SOT_PATH, setup_path=SETUP_PATH):
    wb = openpyxl.load_workbook(path, read_only=True)
    unique_skills = {}
    if 'UniqueSkills' in wb.sheetnames:
        for r in list(wb['UniqueSkills'].iter_rows(values_only=True))[1:]:
            unique_skills[r[1]] = {
                'name': r[2],
                'values': r[4:14],
                'desc': r[21] or ''
            }
    weapon_reqs = {}
    if 'Skills' in wb.sheetnames:
        for r in list(wb['Skills'].iter_rows(values_only=True))[1:]:
            cat, sid = r[0], r[2]
            w_req = r[10]
            if w_req:
                weapon_reqs[(cat, sid)] = w_req
    enchants = {}
    if 'Enchants' in wb.sheetnames:
        for r in list(wb['Enchants'].iter_rows(values_only=True))[1:]:
            enchants[r[1]] = {
                'name': r[2],
                'stacks': bool((r[5] or 0) & 1)
            }
    weapon_ranks = {}
    if 'WeaponRanks' in wb.sheetnames:
        for r in list(wb['WeaponRanks'].iter_rows(values_only=True))[1:]:
            weapon_ranks[r[1]] = {
                'rank': r[2],
                'delay': r[3]
            }

    items = {}
    if 'Items' in wb.sheetnames:
        for r in list(wb['Items'].iter_rows(values_only=True))[1:]:
            if r[1] is not None:
                items[r[1]] = r[2]

    equipment_names = {}
    if 'Equipment' in wb.sheetnames:
        for r in list(wb['Equipment'].iter_rows(values_only=True))[1:]:
            if r[1] is not None:
                equipment_names[r[1]] = r[2]

    enchant_names = {eid: d['name'] for eid, d in enchants.items()}

    enemy_attacks = {}
    if 'EnemyAttacks' in wb.sheetnames:
        for r in list(wb['EnemyAttacks'].iter_rows(values_only=True))[1:]:
            sid = r[1]
            effs = []
            for k in range(1, 6):
                c_id = 15 + (k - 1) * 4
                c_name = 16 + (k - 1) * 4
                c_val = 17 + (k - 1) * 4
                if c_id < len(r) and r[c_id] is not None and r[c_name]:
                    effs.append((r[c_id], r[c_name], r[c_val]))
            enemy_attacks[sid] = {
                'name': r[2] or '',
                'header': r[3] or '',
                'target': r[6] or '',
                'attr': r[8] or '',
                'chant_speed': r[9] or 0,
                'accuracy': r[10] or 0,
                'power': r[11] or 0,
                'turns': r[12] or 0,
                'speed': r[13] if r[13] is not None else 1.0,
                'effects': effs,
                'desc': r[36] if len(r) > 36 and r[36] else ''
            }

    mercenary_unlocks = {}
    if os.path.exists(setup_path):
        wb_setup = openpyxl.load_workbook(setup_path, read_only=True)
        if 'MercenaryUnlocks' in wb_setup.sheetnames:
            for r in list(wb_setup['MercenaryUnlocks'].iter_rows(values_only=True))[1:]:
                flag = r[0]
                basis = str(r[3] or '')
                if flag is not None and basis:
                    clean = re.sub(r'\b0x[0-9a-fA-F]+\b\s*', '', basis).strip()
                    clean = clean.replace('joined by opcode', 'joined by story event')
                    mercenary_unlocks[flag] = clean

    return {
        'unique_skills': unique_skills,
        'weapon_reqs': weapon_reqs,
        'enchants': enchants,
        'weapon_ranks': weapon_ranks,
        'items': items,
        'equipment_names': equipment_names,
        'enchant_names': enchant_names,
        'enemy_attacks': enemy_attacks,
        'mercenary_unlocks': mercenary_unlocks,
    }


ENCHANT_SIZES_PATH = os.path.join(PROJECT, 'docs', 'generated', 'ENCHANT_SIZES.md')


def load_enchant_sizes(path=ENCHANT_SIZES_PATH):
    sizes = {}
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('|') and not line.startswith('| Id') and not line.startswith('|---'):
                    parts = [p.strip() for p in line.split('|')[1:-1]]
                    if len(parts) >= 4:
                        try:
                            eid = int(parts[0])
                            sizes[eid] = (parts[2], parts[3])
                        except ValueError:
                            pass
    return sizes


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


def build_formulas_content(guide_text, snapshot):
    sec = guide_text['sections']
    lines = []
    
    lines.append(sec['formulas_title']['title'])
    lines.append('')
    lines.append(sec['formulas_title']['text'])
    lines.append('')
    
    for f in guide_text.get('formulas', []):
        lines.append('---')
        lines.append('')
        lines.append(f"## {f['title']}")
        lines.append('')
        lines.append('```')
        lines.append(f['formula'])
        lines.append('```')
        lines.append('')
        lines.append(f['summary'])
        lines.append('')
        
    return '\n'.join(lines)


def build_skills_content(guide_text, snapshot, sot_data):
    sec = guide_text['sections']
    h = guide_text['headers']
    lines = []
    
    lines.append(sec['skills_title']['title'])
    lines.append('')
    lines.append(sec['skills_title']['text'])
    lines.append('')
    
    class_names = dict(snapshot['class_names'])
    skills_list = snapshot['skills']
    
    by_category = {'Technique': [], 'Magic': [], 'Passive': []}
    for s in skills_list:
        cat = s['category']
        by_category.setdefault(cat, []).append(s)
        
    category_titles = {
        'Technique': 'Techniques',
        'Magic': 'Magic Spells',
        'Passive': 'Passive Skills'
    }
    
    for cat in ['Technique', 'Magic', 'Passive']:
        cat_skills = by_category.get(cat, [])
        if not cat_skills:
            continue
            
        lines.append('---')
        lines.append('')
        lines.append(f"## {category_titles.get(cat, cat)}")
        lines.append('')
        
        for s in sorted(cat_skills, key=lambda x: x['name']):
            s_name = s['name']
            s_id = s['id']
            max_lv = s['levels']
            sp_list = s['sp'][:max_lv] if s['sp'] else []
            total_sp = sum(sp_list)
            sp_str = f'{total_sp} SP' if total_sp > 0 else '0 SP'
            
            tgt_code = s['target'] if s['target'] is not None else -1
            tgt_str = guide_text['targets'].get(tgt_code, '-')
            rng_code = s['range'] if s['range'] is not None else -1
            rng_str = guide_text['ranges'].get(rng_code, '-')
            
            classes_str = ', '.join(class_names[c] for c in s['classes']) if s['classes'] else 'None'
            
            lines.append('---')
            lines.append('')
            lines.append(f"### {s_name}")
            lines.append('')
            lines.append(f"- **{h['category']}:** {cat} | **{h['classes']}:** {classes_str}")
            
            prop_parts = [
                f"**{h['max_lv']}:** {max_lv}",
                f"**{h['sp_cost']}:** {sp_str}"
            ]
            if tgt_code != -1:
                prop_parts.append(f"**{h['target']}:** {tgt_str}")
            if rng_code != -1:
                prop_parts.append(f"**{h['range']}:** {rng_str}")
            lines.append(f"- {' | '.join(prop_parts)}")
            
            w_req = sot_data['weapon_reqs'].get((cat, s_id), sot_data['weapon_reqs'].get(s_name, ''))
            if w_req:
                lines.append(f"- **Required Weapon:** {w_req}")
                
            lines.append('')
            
            desc, scaling = guide_text['skill_descriptions'].get((cat, s_id), guide_text['skill_descriptions'].get(s_name, ('', '')))
            if desc:
                lines.append(f"> {desc}")
                lines.append('')
                
            if scaling:
                for sline in scaling.splitlines():
                    clean_line = sline.strip()
                    if clean_line:
                        lines.append(f"- {clean_line}")
                lines.append('')
                
    return '\n'.join(lines)


RECRUITMENT_INFO = {
    'Siena': 'Prologue starting member (St00_0010)',
    'Luco': 'Prologue starting member (St00_0010)',
    'Tsurara': 'Defeat Mad Catter (St01_0010, Battle 43)',
    'Yuni': 'Defeat Sorrowful Songstress (St02_0070, Battle 41)',
    'Lizerietta': 'Defeat Countess of Vrachia (St03_0010, Battle 43)',
    'Irena': 'Join event following Countess of Vrachia (St03_0010)',
    'Yae': 'Defeat Boozehound Samurai (St99_0000, Battle 41)',
    'Conette': 'Defeat Oh-So-Hime (St04_0011, Battle 42)',
    'Mefmera': 'Defeat Warden of the Wall (St99_0000, Battle 42)',
    'Monica': 'Defeat Agent M (St06_0030, Battle 42)',
    'Eltricia': 'Defeat True Queen Eltricia (St06_0030, Battle 43)',
    'Souffle': 'Defeat Trafficker Twinny (St07_0010, Battle 45)',
    'Grishna': 'Defeat Maerchen Little (St08_0010, Battle 43)',
    'Lilian': 'Defeat Michelle and Beatrice (St09_0015, Battle 42)',
    'Fiora': 'Defeat Michelle and Beatrice (St09_0015, Battle 42)',
    'Ist': 'Defeat Spirit of Mag Mell (St11_0010, Battle 42)',
    'Alisia': 'Defeat Heartless Avenger (St10_0010, Battle 43)',
    'Melvy': 'Defeat Queen of Darkness (St12_0040, Battle 41)'
}


def format_unique_value(skill_id, val):
    if skill_id == 364:  # Positive Trance
        return str(val)
    if skill_id == 381:  # Yearning
        return f"+{val}%"
    if skill_id == 379:  # Arcane Shield
        if isinstance(val, (int, float)):
            return f"{round(val * 100):g}%"
    if isinstance(val, float):
        if 0 < abs(val) < 1:
            return f"{round(val * 100):g}%"
        return f"{val:g}"
    return str(val)


def build_characters_content(guide_text, snapshot, sot_data):
    sec = guide_text['sections']
    h = guide_text['headers']
    lines = []
    
    lines.append(sec['characters_title']['title'])
    lines.append('')
    lines.append(sec['characters_title']['text'])
    lines.append('')
    
    class_names = dict(snapshot['class_names'])
    exp_curve = snapshot['exp_curve']
    unique_skills = sot_data['unique_skills']
    
    def get_start_level(exp):
        cum = 0
        matched = 1
        for lvl, step in exp_curve:
            if lvl > 1:
                cum += step
            if exp >= cum:
                matched = lvl
            else:
                break
        return matched

    chars = sorted(snapshot['characters'], key=lambda x: x['start_exp'])
    
    for c in chars:
        name = c['name']
        base_cid = c['base_class']
        base_cname = class_names.get(base_cid, f'Class {base_cid}')
        start_exp = c['start_exp']
        start_lvl = get_start_level(start_exp)
        join_info = RECRUITMENT_INFO.get(name, '-')
        
        uid = c['unique_skill']
        uinfo = unique_skills.get(uid, {'name': f'Skill {uid}', 'values': [], 'desc': ''})
        uname = uinfo['name']
        udesc = uinfo['desc']
        uvals = uinfo['values']
        
        lines.append('---')
        lines.append('')
        lines.append(f"### {name}")
        lines.append('')
        lines.append(f"- **{h['base_class']}:** {base_cname}")
        lines.append(f"- **{h['start_level']}:** {start_lvl} ({start_exp:,} EXP)")
        lines.append(f"- **{h['join_point']}:** {join_info}")
        lines.append('')
        
        lines.append(f"#### {h['unique_skill']}: {uname}")
        lines.append('')
        if udesc:
            lines.append(f"> {udesc}")
            lines.append('')
            
        if uvals:
            lines.append(f"| {h['rank']} | Lv 1 | Lv 2 | Lv 3 | Lv 4 | Lv 5 | Lv 6 | Lv 7 | Lv 8 | Lv 9 | EX |")
            lines.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
            val_strs = [format_unique_value(uid, v) for v in uvals]
            lines.append(f"| {h['value']} | {' | '.join(val_strs)} |")
            lines.append('')
            
    return '\n'.join(lines)


def format_enchant_entry(eid, name, stacks, enchant_sizes):
    size_info = enchant_sizes.get(eid, ('', ''))
    raw_val = size_info[0]
    
    val_str = '-'
    cap_str = '-'
    
    if 29 <= eid <= 44:
        cap_str = '+50'
    elif 47 <= eid <= 48:
        cap_str = '-50'
    elif 51 <= eid <= 56:
        cap_str = '+50% (+0.50)'
    elif 66 <= eid <= 71:
        cap_str = '25% damage cut'
    elif 78 <= eid <= 82:
        cap_str = '+40% (+0.40)'
    elif eid == 275:
        val_str = '2.0x multiplier'
        cap_str = 'Single piece'
    elif eid == 269:
        val_str = '-15 points'
        cap_str = 'Trap check'
        
    if raw_val == 'any piece':
        val_str = 'Active switch'
    elif raw_val in ('4', '2', '3'):
        val_str = f'+{raw_val}'
    elif raw_val == '0.1':
        val_str = '-10%' if 'DOWN' in name or eid in (66, 68) else ('10% of damage' if 'TP' in name else '+10%')
    elif raw_val == '0.05':
        val_str = '-5%' if 'DOWN' in name or eid in (67, 69) else ('5% of damage' if 'TP' in name else '+5%')
    elif raw_val == '0.2':
        val_str = '-20%' if 'DOWN' in name else '+20%'
    elif raw_val == '0.08':
        val_str = '-8%'
    elif raw_val == '0.04':
        val_str = '-4%'
    elif raw_val == '0.06':
        val_str = '-6%' if 'DOWN' in name else '+6%'
    elif raw_val == '0.03':
        val_str = '-3%'
    elif raw_val.startswith('0.2'):
        val_str = '+20%'
    elif raw_val and raw_val != '?':
        val_str = raw_val
        
    stack_str = 'Stacks per piece' if stacks else 'Single piece (switch)'
    return val_str, stack_str, cap_str


def build_enchantments_content(guide_text, snapshot, sot_data, enchant_sizes):
    sec = guide_text['sections']
    h = guide_text['headers']
    lines = []
    
    lines.append(sec['enchantments_title']['title'])
    lines.append('')
    lines.append(sec['enchantments_title']['text'])
    lines.append('')
    
    lines.append(f"| ID | {h.get('enchantment', 'Enchantment')} | {h.get('magnitude', 'Value / Scaling')} | {h.get('stacking', 'Stacking Rule')} | {h.get('cap', 'Cap / Limit')} |")
    lines.append('| --- | --- | --- | --- | --- |')
    
    enchants = sot_data['enchants']
    for eid in sorted(enchants):
        einfo = enchants[eid]
        ename = einfo['name']
        stacks = einfo['stacks']
        val_str, stack_str, cap_str = format_enchant_entry(eid, ename, stacks, enchant_sizes)
        lines.append(f"| {eid} | {ename} | {val_str} | {stack_str} | {cap_str} |")
        
    lines.append('')
    return '\n'.join(lines)


def build_equipment_content(guide_text, snapshot, sot_data):
    sec = guide_text['sections']
    h = guide_text['headers']
    lines = []
    
    lines.append(sec['equipment_title']['title'])
    lines.append('')
    lines.append(sec['equipment_title']['text'])
    lines.append('')
    
    # 1. Weapon Delay Ranks
    lines.append('---')
    lines.append('')
    lines.append('## Weapon Delay Ranks')
    lines.append('')
    lines.append('Weapon recovery delay is determined by weapon rank. Slower weapon ranks impose larger recovery delays, reducing action frequency.')
    lines.append('')
    lines.append('| Rank | Delay Multiplier |')
    lines.append('| --- | --- |')
    
    rank_dict = {}
    for idx, rinfo in sorted(sot_data['weapon_ranks'].items()):
        rk = rinfo['rank']
        dl = rinfo['delay']
        rank_dict[idx] = f"{rk} ({dl:g}x)"
        lines.append(f"| {rk} | {dl:.2f}x |")
    lines.append('')
    
    ench_names = {eid: info['name'] for eid, info in sot_data['enchants'].items()}
    equipment_list = snapshot['equipment']
    
    # Weapons grouped by weapon type
    weapon_groups = [
        ('Swords', [0]),
        ('Daggers', [1]),
        ('Axes', [2]),
        ('Polearms', [3]),
        ('Maces', [4]),
        ('Staves', [5]),
        ('Tomes', [6]),
        ('Bows', [7]),
        ('Katanas', [8]),
        ('Projectiles', [9]),
        ('Whips', [10]),
        ('Fans', [11]),
        ('Microphones', [12]),
        ('Instruments', [13]),
        ('Guns', list(range(14, 21))),
    ]
    
    lines.append('---')
    lines.append('')
    lines.append('## Weapons')
    lines.append('')
    
    for group_title, type_codes in weapon_groups:
        group_items = [p for p in equipment_list if p['category'] == 0 and p['type'] in type_codes]
        if not group_items:
            continue
            
        lines.append(f"### {group_title}")
        lines.append('')
        lines.append(f"| {h.get('weapon', 'Weapon')} | {h.get('delay_rank', 'Delay Rank')} | {h['atk']} | {h['def']} | {h['int']} | {h['res']} | {h['dex']} | {h['agi']} | {h.get('upgrade_rate', 'Upgrade Rate')} | {h['range']} | {h.get('two_handed', '2-Handed')} | {h.get('innate_enchants', 'Innate Enchants')} |")
        lines.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
        
        for p in group_items:
            st = p['stats']
            rnk = rank_dict.get(p['rank'], '-')
            rng_code = p['range']
            rng_str = guide_text['ranges'].get(rng_code, '-')
            two_h = 'Yes' if p['two_handed'] else 'No'
            enchs = ', '.join(ench_names.get(e, f'Enchant {e}') for e in p['enchants']) if p['enchants'] else '-'
            u_rate = f"+{p['rate']:g}" if p['rate'] > 0 else '0'
            lines.append(f"| {p['name']} | {rnk} | {st['atk']} | {st['def']} | {st['int']} | {st['res']} | {st['dex']} | {st['agi']} | {u_rate} | {rng_str} | {two_h} | {enchs} |")
        lines.append('')
        
    # Armor categories: Shields (1), Headgear (2), Body Armor (3), Accessories (4)
    armor_categories = [
        ('Shields', 1, h.get('shield', 'Shield')),
        ('Headgear', 2, h.get('headgear', 'Headgear')),
        ('Body Armor', 3, h.get('body_armor', 'Armor')),
        ('Accessories', 4, h.get('accessory', 'Accessory')),
    ]
    
    for cat_title, cat_code, col_header in armor_categories:
        cat_items = [p for p in equipment_list if p['category'] == cat_code]
        lines.append('---')
        lines.append('')
        lines.append(f"## {cat_title}")
        lines.append('')
        lines.append(f"| {col_header} | {h['def']} | {h['res']} | {h['atk']} | {h['int']} | {h['dex']} | {h['agi']} | {h.get('upgrade_rate', 'Upgrade Rate')} | {h.get('innate_enchants', 'Innate Enchants')} |")
        lines.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
        
        for p in cat_items:
            st = p['stats']
            enchs = ', '.join(ench_names.get(e, f'Enchant {e}') for e in p['enchants']) if p['enchants'] else '-'
            u_rate = f"+{p['rate']:g}" if p['rate'] > 0 else '0'
            lines.append(f"| {p['name']} | {st['def']} | {st['res']} | {st['atk']} | {st['int']} | {st['dex']} | {st['agi']} | {u_rate} | {enchs} |")
        lines.append('')
        
    return '\n'.join(lines)


def format_effect_summary(effs, power=None):
    parts = []
    for eid, name, val in effs:
        if name:
            if val not in (None, 0, 1):
                parts.append(f"{name} ({val})")
            else:
                parts.append(name)
    if not parts and power not in (None, 0):
        parts.append(f"Power {power}")
    return '; '.join(parts) if parts else '-'


def format_script_markdown(script, attack_names):
    if not script:
        return []
    lines = []
    
    def resolve_slots(text):
        def rep(m):
            idx = int(m.group(1))
            if idx < len(attack_names):
                return f"{attack_names[idx]} (slot {idx})"
            return m.group(0)
        return re.sub(r'\bslot (\d+)\b', rep, text)

    opening = script.get('opening', [])
    if opening:
        lines.append('**Opening Actions:**')
        for c in opening:
            desc = enemy_ai.describe(c)
            lines.append(f'- {resolve_slots(desc)}')

    sets = script.get('sets', [])
    if isinstance(sets, dict):
        sets = [{'set': k, **v} for k, v in sets.items()]

    if sets:
        lines.append('**Action Sets:**')
        for s in sets:
            set_num = s['set']
            weights = s['weights']
            active_weights = []
            for slot_idx, w in enumerate(weights):
                if w > 0:
                    att_name = attack_names[slot_idx] if slot_idx < len(attack_names) else f"Slot {slot_idx}"
                    active_weights.append(f"{att_name} ({w}%)")
            w_str = ', '.join(active_weights) if active_weights else 'None'
            lines.append(f'- **Set {set_num}:** {w_str}')
            for c in s.get('commands', []):
                desc = enemy_ai.describe(c)
                lines.append(f'  - *Condition:* {resolve_slots(desc)}')
    return lines


def build_enemies_content(guide_text, snapshot, sot_data):
    all_enemies = enemy_data.enemies()
    attacks_dict = {a['id']: a for a in snapshot['attacks']}
    sot_attacks = sot_data.get('enemy_attacks', {})
    items_dict = sot_data.get('items', {})
    targets_dict = guide_text['targets']

    lines = [
        guide_text['sections']['enemies_title']['title'],
        "",
        guide_text['sections']['enemies_title']['text'],
        ""
    ]

    by_habitat = {}
    for e in all_enemies:
        hab = e.get('habitat') or 'Unknown Habitat'
        by_habitat.setdefault(hab, []).append(e)

    for hab in sorted(by_habitat.keys()):
        lines.append(f"## {hab}")
        lines.append("")
        elist = sorted(by_habitat[hab], key=lambda x: (x['level'], x['name']))
        
        for e in elist:
            name = e['name']
            level = e['level']
            race = e['race_name']
            lines.append(f"### {name} (Lv {level})")
            lines.append("")
            
            lines.append("| HP | ATK | DEF | INT | RES | DEX | AGI | EXP | Gold |")
            lines.append("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
            lines.append(f"| {e['hp']:,} | {e['atk']} | {e['def']} | {e['int']} | {e['res']} | {e['dex']} | {e['agi']} | {e['exp']:,} | {e['gold']:,} |")
            lines.append("")
            
            lines.append("| Slash | Stab | Bash | Fire | Water | Wind | Earth | Lightning |")
            lines.append("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
            lines.append(f"| {e['res_slash']} | {e['res_stab']} | {e['res_bash']} | {e['res_fire']} | {e['res_water']} | {e['res_wind']} | {e['res_earth']} | {e['res_lightning']} |")
            lines.append("")
            
            imm_str = ', '.join(e['immune']) if e['immune'] else 'None'
            drops_list = []
            for item_id, ch in e['drops']:
                iname = items_dict.get(item_id, f"Item {item_id}")
                drops_list.append(f"{iname} ({ch}%)")
            drops_str = ', '.join(drops_list) if drops_list else 'None'
            
            eq_ch, eq_slots_cnt = e['equipment_drop']
            eq_drop_str = f"{eq_ch}%" if eq_ch > 0 else 'None'
            snack_str = items_dict.get(e['snack_item'], '-') if e['snack'] else '-'
            steal_str = 'Yes' if e['can_steal'] else 'No'

            lines.append(f"- **Race:** {race} | **Stealable:** {steal_str} | **Snack:** {snack_str}")
            lines.append(f"- **Immunities:** {imm_str}")
            lines.append(f"- **Item Drops:** {drops_str} | **Equipment Drop:** {eq_drop_str}")
            lines.append("")
            
            if e['attacks']:
                lines.append("#### Attacks")
                lines.append("")
                lines.append("| Attack | Target | Element | Spd | Chant | Power | Effect |")
                lines.append("| :--- | :--- | :--- | ---: | ---: | ---: | :--- |")
                for aid in e['attacks']:
                    a_snap = attacks_dict.get(aid, {})
                    a_sot = sot_attacks.get(aid, {})
                    aname = a_sot.get('name') or a_snap.get('name') or f"Attack {aid}"
                    tgt_code = a_snap.get('target', 0)
                    tgt_str = a_sot.get('target') or targets_dict.get(tgt_code, str(tgt_code))
                    attr_code = a_snap.get('attr', 0)
                    attr_str = a_sot.get('attr') or ATTR_NAMES.get(attr_code, str(attr_code))
                    spd = a_snap.get('speed', 1.0)
                    chant = a_snap.get('chant_speed', 0)
                    chant_str = f"{chant}s" if chant > 0 else '-'
                    power = a_snap.get('power', 0)
                    power_str = f"{power}" if power != 0 else '-'
                    effs = a_sot.get('effects', [])
                    eff_str = format_effect_summary(effs, power)
                    lines.append(f"| {aname} | {tgt_str} | {attr_str} | {spd:.2f}x | {chant_str} | {power_str} | {eff_str} |")
                lines.append("")
                
            if e['passives']:
                lines.append("#### Passives")
                lines.append("")
                lines.append("| Passive | Effect |")
                lines.append("| :--- | :--- |")
                for pid in e['passives']:
                    p_sot = sot_attacks.get(pid, {})
                    pname = p_sot.get('name') or attacks_dict.get(pid, {}).get('name') or f"Passive {pid}"
                    effs = p_sot.get('effects', [])
                    eff_str = format_effect_summary(effs)
                    lines.append(f"| {pname} | {eff_str} |")
                lines.append("")

    return "\n".join(lines)


def build_bosses_content(guide_text, snapshot, sot_data):
    all_enemies = {e['id']: e for e in enemy_data.enemies()}
    fixed_battles = snapshot['fixed']
    attacks_dict = {a['id']: a for a in snapshot['attacks']}
    sot_attacks = sot_data.get('enemy_attacks', {})
    items_dict = sot_data.get('items', {})
    targets_dict = guide_text['targets']

    lines = [
        guide_text['sections']['bosses_title']['title'],
        "",
        guide_text['sections']['bosses_title']['text'],
        ""
    ]

    by_floor = {}
    for b in fixed_battles:
        by_floor.setdefault(b['floor'], []).append(b)

    for floor in sorted(by_floor.keys()):
        lines.append(f"## Floor {floor}")
        lines.append("")
        
        battles = sorted(by_floor[floor], key=lambda x: x['number'])
        for b in battles:
            b_num = b['number']
            e_entries = b['enemies']
            
            counts = {}
            for eid, is_front in e_entries:
                ename = all_enemies.get(eid, {}).get('name', f"Enemy {eid}")
                row_str = "Front" if is_front else "Back"
                counts.setdefault((eid, ename), []).append(row_str)
            
            battle_title_parts = []
            for (eid, ename), rows in counts.items():
                if len(rows) > 1:
                    battle_title_parts.append(f"{ename} x{len(rows)}")
                else:
                    battle_title_parts.append(ename)
            
            lines.append(f"### Battle {b_num}: {', '.join(battle_title_parts)}")
            lines.append("")
            
            part_desc = []
            for (eid, ename), rows in counts.items():
                front_cnt = rows.count("Front")
                back_cnt = rows.count("Back")
                row_parts = []
                if front_cnt > 0: row_parts.append(f"{front_cnt} Front")
                if back_cnt > 0: row_parts.append(f"{back_cnt} Back")
                part_desc.append(f"**{ename}** ({', '.join(row_parts)})")
            lines.append(f"- **Encounter:** {'; '.join(part_desc)}")
            lines.append("")

            seen_eids = set()
            for eid, _ in e_entries:
                if eid in seen_eids:
                    continue
                seen_eids.add(eid)
                e = all_enemies.get(eid)
                if not e:
                    continue
                
                name = e['name']
                level = e['level']
                race = e['race_name']
                lines.append(f"#### {name} (Lv {level})")
                lines.append("")

                lines.append("| HP | ATK | DEF | INT | RES | DEX | AGI | EXP | Gold |")
                lines.append("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
                lines.append(f"| {e['hp']:,} | {e['atk']} | {e['def']} | {e['int']} | {e['res']} | {e['dex']} | {e['agi']} | {e['exp']:,} | {e['gold']:,} |")
                lines.append("")

                lines.append("| Slash | Stab | Bash | Fire | Water | Wind | Earth | Lightning |")
                lines.append("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
                lines.append(f"| {e['res_slash']} | {e['res_stab']} | {e['res_bash']} | {e['res_fire']} | {e['res_water']} | {e['res_wind']} | {e['res_earth']} | {e['res_lightning']} |")
                lines.append("")

                imm_str = ', '.join(e['immune']) if e['immune'] else 'None'
                drops_list = []
                for item_id, ch in e['drops']:
                    iname = items_dict.get(item_id, f"Item {item_id}")
                    drops_list.append(f"{iname} ({ch}%)")
                drops_str = ', '.join(drops_list) if drops_list else 'None'
                
                eq_ch, eq_slots_cnt = e['equipment_drop']
                eq_drop_str = f"{eq_ch}%" if eq_ch > 0 else 'None'
                snack_str = items_dict.get(e['snack_item'], '-') if e['snack'] else '-'
                steal_str = 'Yes' if e['can_steal'] else 'No'

                lines.append(f"- **Race:** {race} | **Stealable:** {steal_str} | **Snack:** {snack_str}")
                lines.append(f"- **Immunities:** {imm_str}")
                lines.append(f"- **Item Drops:** {drops_str} | **Equipment Drop:** {eq_drop_str}")
                lines.append("")

                att_names_list = []
                if e['attacks']:
                    lines.append("##### Attacks")
                    lines.append("")
                    lines.append("| Attack | Target | Element | Spd | Chant | Power | Effect |")
                    lines.append("| :--- | :--- | :--- | ---: | ---: | ---: | :--- |")
                    for aid in e['attacks']:
                        a_snap = attacks_dict.get(aid, {})
                        a_sot = sot_attacks.get(aid, {})
                        aname = a_sot.get('name') or a_snap.get('name') or f"Attack {aid}"
                        att_names_list.append(aname)
                        tgt_code = a_snap.get('target', 0)
                        tgt_str = a_sot.get('target') or targets_dict.get(tgt_code, str(tgt_code))
                        attr_code = a_snap.get('attr', 0)
                        attr_str = a_sot.get('attr') or ATTR_NAMES.get(attr_code, str(attr_code))
                        spd = a_snap.get('speed', 1.0)
                        chant = a_snap.get('chant_speed', 0)
                        chant_str = f"{chant}s" if chant > 0 else '-'
                        power = a_snap.get('power', 0)
                        power_str = f"{power}" if power != 0 else '-'
                        effs = a_sot.get('effects', [])
                        eff_str = format_effect_summary(effs, power)
                        lines.append(f"| {aname} | {tgt_str} | {attr_str} | {spd:.2f}x | {chant_str} | {power_str} | {eff_str} |")
                    lines.append("")

                if e['passives']:
                    lines.append("##### Passives")
                    lines.append("")
                    lines.append("| Passive | Effect |")
                    lines.append("| :--- | :--- |")
                    for pid in e['passives']:
                        p_sot = sot_attacks.get(pid, {})
                        pname = p_sot.get('name') or attacks_dict.get(pid, {}).get('name') or f"Passive {pid}"
                        effs = p_sot.get('effects', [])
                        eff_str = format_effect_summary(effs)
                        lines.append(f"| {pname} | {eff_str} |")
                    lines.append("")

                if e.get('script'):
                    lines.append("##### AI Behavior")
                    lines.append("")
                    script_lines = format_script_markdown(e['script'], att_names_list)
                    lines.extend(script_lines)
                    lines.append("")

    return "\n".join(lines)


def build_summons_content(guide_text, snapshot, sot_data):
    summons = snapshot['summons']
    sealbooks = {s['id']: s for s in snapshot['sealbooks']}
    enchant_names = sot_data.get('enchant_names', {})
    attacks_dict = {a['id']: a for a in snapshot['attacks']}
    sot_attacks = sot_data.get('enemy_attacks', {})
    targets_dict = guide_text['targets']

    lines = [
        guide_text['sections']['summons_title']['title'],
        "",
        guide_text['sections']['summons_title']['text'],
        ""
    ]

    by_family = {}
    for s in summons:
        by_family.setdefault(s['family'], []).append(s)

    for fam_id, forms in sorted(by_family.items()):
        name = forms[0]['name']
        lines.append(f"## {name} (Family {fam_id})")
        lines.append("")

        sb = sealbooks.get(fam_id)
        if sb and sb.get('enchants'):
            ench_strs = [enchant_names.get(eid, f"Enchantment {eid}") for eid in sb['enchants']]
            lines.append(f"- **Grand Sealbook Enchantment:** {', '.join(ench_strs)}")
        else:
            lines.append("- **Grand Sealbook Enchantment:** None")
        lines.append("")

        lines.append("| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |")
        lines.append("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |")
        for k, form in enumerate(forms, 1):
            f_atk = form['factors'].get('atk', 1.0)
            f_def = form['factors'].get('def', 1.0)
            f_int = form['factors'].get('int', 1.0)
            f_res = form['factors'].get('res', 1.0)
            f_dex = form['factors'].get('dex', 1.0)
            f_agi = form['factors'].get('agi', 1.0)
            pas = form.get('passive')
            pas_str = sot_attacks.get(pas, {}).get('name') if pas else '-'
            lines.append(f"| Form {k} | {form['level']} | {form['rank']} | {f_atk:.2f}x | {f_def:.2f}x | {f_int:.2f}x | {f_res:.2f}x | {f_dex:.2f}x | {f_agi:.2f}x | {pas_str} |")
        lines.append("")

        for k, form in enumerate(forms, 1):
            f_level = form['level']
            lines.append(f"### {name} - Form {k} (Lv {f_level})")
            lines.append("")

            att_names = []
            if form['attacks']:
                lines.append("| Attack | Target | Element | Spd | Chant | Power | Effect |")
                lines.append("| :--- | :--- | :--- | ---: | ---: | ---: | :--- |")
                for aid in form['attacks']:
                    a_snap = attacks_dict.get(aid, {})
                    a_sot = sot_attacks.get(aid, {})
                    aname = a_sot.get('name') or a_snap.get('name') or f"Attack {aid}"
                    att_names.append(aname)
                    tgt_code = a_snap.get('target', 0)
                    tgt_str = a_sot.get('target') or targets_dict.get(tgt_code, str(tgt_code))
                    attr_code = a_snap.get('attr', 0)
                    attr_str = a_sot.get('attr') or ATTR_NAMES.get(attr_code, str(attr_code))
                    spd = a_snap.get('speed', 1.0)
                    chant = a_snap.get('chant_speed', 0)
                    chant_str = f"{chant}s" if chant > 0 else '-'
                    power = a_snap.get('power', 0)
                    power_str = f"{power}" if power != 0 else '-'
                    effs = a_sot.get('effects', [])
                    eff_str = format_effect_summary(effs, power)
                    lines.append(f"| {aname} | {tgt_str} | {attr_str} | {spd:.2f}x | {chant_str} | {power_str} | {eff_str} |")
                lines.append("")

            if form.get('script'):
                lines.append("#### AI Behavior")
                lines.append("")
                script_lines = format_script_markdown(form['script'], att_names)
                lines.extend(script_lines)
                lines.append("")

    return "\n".join(lines)


def build_mercenaries_content(guide_text, snapshot, sot_data):
    npcs = [n for n in snapshot['npcs'] if n['character'] not in (300, 301, 302)]
    unlocks = sot_data.get('mercenary_unlocks', {})
    attacks_dict = {a['id']: a for a in snapshot['attacks']}
    sot_attacks = sot_data.get('enemy_attacks', {})
    targets_dict = guide_text['targets']

    lines = [
        guide_text['sections']['mercenaries_title']['title'],
        "",
        guide_text['sections']['mercenaries_title']['text'],
        ""
    ]

    by_char = {}
    for n in npcs:
        by_char.setdefault(n['character'], []).append(n)

    for char_id, stages in sorted(by_char.items()):
        name = stages[0]['name']
        lines.append(f"## {name} (Character {char_id})")
        lines.append("")

        init_flag = stages[0]['unlock_flag']
        basis = unlocks.get(init_flag, f"Unlock Flag {init_flag}")
        lines.append(f"- **Tavern Availability:** {basis}")
        lines.append("")

        lines.append("| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |")
        lines.append("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for k, st in enumerate(stages, 1):
            contract_str = f"{st['contract']} battles" if st['contract'] > 0 else 'Permanent'
            lines.append(f"| {k} | {st['level']} | {st['cost']:,} Gold | {contract_str} | {st['atk']} | {st['def']} | {st['int']} | {st['res']} | {st['dex']} | {st['agi']} | {st['unlock_flag']} |")
        lines.append("")

        for k, st in enumerate(stages, 1):
            st_level = st['level']
            lines.append(f"### Stage {k} (Lv {st_level})")
            lines.append("")

            att_names = []
            if st['attacks']:
                lines.append("#### Attacks")
                lines.append("")
                lines.append("| Attack | Target | Element | Spd | Chant | Power | Effect |")
                lines.append("| :--- | :--- | :--- | ---: | ---: | ---: | :--- |")
                for aid in st['attacks']:
                    a_snap = attacks_dict.get(aid, {})
                    a_sot = sot_attacks.get(aid, {})
                    aname = a_sot.get('name') or a_snap.get('name') or f"Attack {aid}"
                    att_names.append(aname)
                    tgt_code = a_snap.get('target', 0)
                    tgt_str = a_sot.get('target') or targets_dict.get(tgt_code, str(tgt_code))
                    attr_code = a_snap.get('attr', 0)
                    attr_str = a_sot.get('attr') or ATTR_NAMES.get(attr_code, str(attr_code))
                    spd = a_snap.get('speed', 1.0)
                    chant = a_snap.get('chant_speed', 0)
                    chant_str = f"{chant}s" if chant > 0 else '-'
                    power = a_snap.get('power', 0)
                    power_str = f"{power}" if power != 0 else '-'
                    effs = a_sot.get('effects', [])
                    eff_str = format_effect_summary(effs, power)
                    lines.append(f"| {aname} | {tgt_str} | {attr_str} | {spd:.2f}x | {chant_str} | {power_str} | {eff_str} |")
                lines.append("")

            if st['passives']:
                lines.append("#### Passives")
                lines.append("")
                lines.append("| Passive | Effect |")
                lines.append("| :--- | :--- |")
                for pid in st['passives']:
                    p_sot = sot_attacks.get(pid, {})
                    pname = p_sot.get('name') or attacks_dict.get(pid, {}).get('name') or f"Passive {pid}"
                    effs = p_sot.get('effects', [])
                    eff_str = format_effect_summary(effs)
                    lines.append(f"| {pname} | {eff_str} |")
                lines.append("")

            if st.get('script'):
                lines.append("#### AI Behavior")
                lines.append("")
                script_lines = format_script_markdown(st['script'], att_names)
                lines.extend(script_lines)
                lines.append("")

    return "\n".join(lines)


def build_progression_content(guide_text, snapshot, sot_data):
    exp_curve = snapshot['exp_curve']
    sp_curve = snapshot['sp_curve']
    floors = snapshot['floors']
    fixed_battles = snapshot['fixed']
    all_enemies = {e['id']: e for e in enemy_data.enemies()}

    lines = [
        guide_text['sections']['progression_title']['title'],
        "",
        guide_text['sections']['progression_title']['text'],
        "",
        "## Experience and Skill Point Curves",
        "",
        "Level progression from Level 1 to 99, detailing the required experience points to reach each level, cumulative experience thresholds, skill points awarded per level, and total accumulated skill points.",
        "",
        "| Level | EXP to Next | Cumulative EXP | SP Gained | Cumulative SP |",
        "| ---: | ---: | ---: | ---: | ---: |"
    ]

    cum_exp = 0
    cum_sp = 0
    sp_dict = dict(sp_curve)

    for lv, req_exp in exp_curve:
        cum_exp += req_exp
        gain_sp = sp_dict.get(lv, 1)
        cum_sp += gain_sp
        lines.append(f"| {lv} | {req_exp:,} | {cum_exp:,} | +{gain_sp} | {cum_sp} |")

    lines.append("")
    lines.append("## Crown Resets")
    lines.append("")
    lines.append("A character who reaches Level 30 or higher can undergo a Crown Reset. The character's level returns to Level 1, previously allocated skill points are refunded to be re-earned through leveling, and the character gains permanent bonus stat points. Resets stack additively up to a maximum cap of +50 total bonus stat points.")
    lines.append("")
    lines.append("| Reset Level Range | Bonus Stat Points | Reset Level | Cumulative Cap |")
    lines.append("| :--- | ---: | :--- | :--- |")
    lines.append("| Level 99 | +10 | Level 1 | +50 stats max |")
    lines.append("| Level 90–98 | +9 | Level 1 | +50 stats max |")
    lines.append("| Level 80–89 | +8 | Level 1 | +50 stats max |")
    lines.append("| Level 70–79 | +7 | Level 1 | +50 stats max |")
    lines.append("| Level 60–69 | +6 | Level 1 | +50 stats max |")
    lines.append("| Level 50–59 | +5 | Level 1 | +50 stats max |")
    lines.append("| Level 40–49 | +4 | Level 1 | +50 stats max |")
    lines.append("| Level 30–39 | +3 | Level 1 | +50 stats max |")
    lines.append("")

    lines.append("## Dungeon Floor Level Progression")
    lines.append("")
    lines.append("Encounter levels across all dungeon floors in Dungeon Travelers 2-2, including random encounter level ranges and fixed story or postgame boss encounters.")
    lines.append("")
    lines.append("| Floor | Dungeon / Habitat | Random Enemy Levels | Boss / Fixed Encounters |")
    lines.append("| :--- | :--- | :--- | :--- |")

    seen_floors = set()
    for z in floors:
        fl_code = z['floor']
        if fl_code in seen_floors:
            continue
        seen_floors.add(fl_code)

        habs = {all_enemies[e]['habitat'] for f in z['formations'] for e, _ in f['enemies'] if e in all_enemies and all_enemies[e].get('habitat')}
        hab_name = ', '.join(sorted(habs)) if habs else z['dungeon']

        floor_zones = [fz for fz in floors if fz['floor'] == fl_code]
        r_levels = [all_enemies[e]['level'] for fz in floor_zones for f in fz['formations'] for e, _ in f['enemies'] if e in all_enemies]
        if r_levels:
            r_str = f"Lv {min(r_levels)}–{max(r_levels)}"
        else:
            r_str = "-"

        f_battles = [b for b in fixed_battles if b['floor'] == fl_code]
        f_parts = []
        for b in sorted(f_battles, key=lambda x: x['number']):
            b_names = [f"{all_enemies[e]['name']} (Lv {all_enemies[e]['level']})" for e, _ in b['enemies'] if e in all_enemies]
            f_parts.append(f"B{b['number']}: {', '.join(b_names)}")
        boss_str = '; '.join(f_parts) if f_parts else "-"

        lines.append(f"| {fl_code} | {hab_name} | {r_str} | {boss_str} |")

    return "\n".join(lines)


def build_guide(side='vanilla', out_dir=DEFAULT_OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    guide_text = load_guide_text()
    snapshot = load_snapshot(side=side)
    sot_data = load_source_of_truth()
    enchant_sizes = load_enchant_sizes()
    
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
        
    # 3. formulas.md
    formulas_path = os.path.join(out_dir, 'formulas.md')
    formulas_content = build_formulas_content(guide_text, snapshot)
    with open(formulas_path, 'w', encoding='utf-8') as f:
        f.write(formulas_content)
        
    # 4. skills.md
    skills_path = os.path.join(out_dir, 'skills.md')
    skills_content = build_skills_content(guide_text, snapshot, sot_data)
    with open(skills_path, 'w', encoding='utf-8') as f:
        f.write(skills_content)
        
    # 5. characters.md
    chars_path = os.path.join(out_dir, 'characters.md')
    chars_content = build_characters_content(guide_text, snapshot, sot_data)
    with open(chars_path, 'w', encoding='utf-8') as f:
        f.write(chars_content)
        
    # 6. enchantments.md
    ench_path = os.path.join(out_dir, 'enchantments.md')
    ench_content = build_enchantments_content(guide_text, snapshot, sot_data, enchant_sizes)
    with open(ench_path, 'w', encoding='utf-8') as f:
        f.write(ench_content)
        
    # 7. equipment.md
    eq_path = os.path.join(out_dir, 'equipment.md')
    eq_content = build_equipment_content(guide_text, snapshot, sot_data)
    with open(eq_path, 'w', encoding='utf-8') as f:
        f.write(eq_content)
        
    # 8. enemies.md
    enemies_path = os.path.join(out_dir, 'enemies.md')
    enemies_content = build_enemies_content(guide_text, snapshot, sot_data)
    with open(enemies_path, 'w', encoding='utf-8') as f:
        f.write(enemies_content)
        
    # 9. bosses.md
    bosses_path = os.path.join(out_dir, 'bosses.md')
    bosses_content = build_bosses_content(guide_text, snapshot, sot_data)
    with open(bosses_path, 'w', encoding='utf-8') as f:
        f.write(bosses_content)
        
    # 10. summons.md
    summons_path = os.path.join(out_dir, 'summons.md')
    summons_content = build_summons_content(guide_text, snapshot, sot_data)
    with open(summons_path, 'w', encoding='utf-8') as f:
        f.write(summons_content)
        
    # 11. mercenaries.md
    merc_path = os.path.join(out_dir, 'mercenaries.md')
    merc_content = build_mercenaries_content(guide_text, snapshot, sot_data)
    with open(merc_path, 'w', encoding='utf-8') as f:
        f.write(merc_content)
        
    # 12. progression.md
    prog_path = os.path.join(out_dir, 'progression.md')
    prog_content = build_progression_content(guide_text, snapshot, sot_data)
    with open(prog_path, 'w', encoding='utf-8') as f:
        f.write(prog_content)
        
    return {
        'README.md': readme_content,
        'classes.md': classes_content,
        'formulas.md': formulas_content,
        'skills.md': skills_content,
        'characters.md': chars_content,
        'enchantments.md': ench_content,
        'equipment.md': eq_content,
        'enemies.md': enemies_content,
        'bosses.md': bosses_content,
        'summons.md': summons_content,
        'mercenaries.md': merc_content,
        'progression.md': prog_content,
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

