import os
import openpyxl
from pck_handler import PckArchive, SkillHelper

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
GAME_PARAM_DIR = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Parameter')
GAME_SCRIPT_DIR = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Script')

def run_audit():
    print("=" * 60)
    print("           DT2-2 MOD AUDIT & QA VERIFICATION REPORT")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # 1. Check Skills table
    excel_path = os.path.join(TABLES_DIR, 'skills.xlsx')
    if not os.path.exists(excel_path):
        print(f"[FAIL] Missing {excel_path}")
        return False
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["Skills"]
    
    total_skills = ws.max_row - 1
    modified_skills = 0
    
    for row_idx in range(2, ws.max_row + 1):
        cat = ws.cell(row=row_idx, column=2).value
        name = ws.cell(row=row_idx, column=4).value
        status = ws.cell(row=row_idx, column=11).value
        mod_desc = ws.cell(row=row_idx, column=9).value or ""
        mod_lvup = ws.cell(row=row_idx, column=10).value or ""
        
        if status in ['Approved', 'Applied', 'Draft'] and (mod_desc or mod_lvup):
            modified_skills += 1
            
            lines = mod_desc.split('\n') if mod_desc else []
            if mod_lvup:
                lines.extend(mod_lvup.split('\n'))
                
            if len(lines) > 3:
                errors.append(f"[SKILLS ROW {row_idx}] '{name}' ({cat}): Exceeds 3 lines ({len(lines)} lines)!")
                
            for line_idx, l in enumerate(lines):
                if len(l) > 85:
                    errors.append(f"[SKILLS ROW {row_idx}] '{name}' Line {line_idx+1}: Too long ({len(l)} chars > 85 max): '{l}'")
                elif len(l) > 80:
                    warnings.append(f"[SKILLS ROW {row_idx}] '{name}' Line {line_idx+1}: Close to limit ({len(l)} chars): '{l}'")
                if '~' in l:
                    errors.append(f"[SKILLS ROW {row_idx}] '{name}' Line {line_idx+1}: Contains invalid tilde (~): '{l}'")
                    
    print(f"\n[1] SKILLS DATA TABLE CHECK:")
    print(f"    Total Skills Indexed:    {total_skills}")
    print(f"    Modified/Active Skills:  {modified_skills}")
    print(f"    Errors:   {len(errors)}")
    print(f"    Warnings: {len(warnings)}")
    
    for err in errors:
        print(f"    [FAIL] {err}")
    for warn in warnings:
        print(f"    [WARN] {warn}")
        
    # 2. Check Items table
    items_path = os.path.join(TABLES_DIR, 'items.xlsx')
    if os.path.exists(items_path):
        wb_it = openpyxl.load_workbook(items_path)
        ws_it = wb_it["Items"]
        modified_items = 0
        for r in range(2, ws_it.max_row + 1):
            name = ws_it.cell(row=r, column=3).value
            status = ws_it.cell(row=r, column=7).value
            m_desc = ws_it.cell(row=r, column=6).value or ""
            if status in ['Approved', 'Applied', 'Draft'] and m_desc:
                modified_items += 1
                lines = m_desc.split('\n')
                if len(lines) > 3:
                    errors.append(f"[ITEMS ROW {r}] '{name}': Exceeds 3 lines ({len(lines)})")
                for l in lines:
                    if len(l) > 85:
                        errors.append(f"[ITEMS ROW {r}] '{name}': Exceeds 85 chars ({len(l)}): '{l}'")
                    if '~' in l:
                        errors.append(f"[ITEMS ROW {r}] '{name}': Contains invalid tilde (~)")
        print(f"\n[2] ITEMS DATA TABLE CHECK:")
        print(f"    Total Items Indexed:     {ws_it.max_row - 1}")
        print(f"    Modified/Active Items:   {modified_items}")

    # 3. Check Grand Seals table
    seals_path = os.path.join(TABLES_DIR, 'grand_seals.xlsx')
    if os.path.exists(seals_path):
        wb_gs = openpyxl.load_workbook(seals_path)
        ws_gs = wb_gs["GrandSeals"]
        modified_seals = 0
        for r in range(2, ws_gs.max_row + 1):
            name = ws_gs.cell(row=r, column=2).value
            status = ws_gs.cell(row=r, column=6).value
            m_desc = ws_gs.cell(row=r, column=5).value or ""
            if status in ['Approved', 'Applied', 'Draft'] and m_desc:
                modified_seals += 1
                lines = m_desc.split('\n')
                if len(lines) > 3:
                    errors.append(f"[SEALS ROW {r}] '{name}': Exceeds 3 lines ({len(lines)})")
                for l in lines:
                    if len(l) > 85:
                        errors.append(f"[SEALS ROW {r}] '{name}': Exceeds 85 chars ({len(l)}): '{l}'")
                    if '~' in l:
                        errors.append(f"[SEALS ROW {r}] '{name}': Contains invalid tilde (~)")
        print(f"\n[3] GRAND SEALS DATA TABLE CHECK:")
        print(f"    Total Seals Indexed:     {ws_gs.max_row - 1}")
        print(f"    Modified/Active Seals:   {modified_seals}")

    # 4. Check Joint Skills table
    joints_path = os.path.join(TABLES_DIR, 'joint_skills.xlsx')
    if os.path.exists(joints_path):
        wb_js = openpyxl.load_workbook(joints_path)
        ws_js = wb_js["JointSkills"]
        modified_joints = 0
        for r in range(2, ws_js.max_row + 1):
            name = ws_js.cell(row=r, column=2).value
            status = ws_js.cell(row=r, column=5).value
            m_desc = ws_js.cell(row=r, column=4).value or ""
            if status in ['Approved', 'Applied', 'Draft'] and m_desc:
                modified_joints += 1
                lines = m_desc.split('\n')
                if len(lines) > 3:
                    errors.append(f"[JOINTS ROW {r}] '{name}': Exceeds 3 lines ({len(lines)})")
                for l in lines:
                    if len(l) > 85:
                        errors.append(f"[JOINTS ROW {r}] '{name}': Exceeds 85 chars ({len(l)}): '{l}'")
                    if '~' in l:
                        errors.append(f"[JOINTS ROW {r}] '{name}': Contains invalid tilde (~)")
        print(f"\n[4] JOINT SKILLS DATA TABLE CHECK:")
        print(f"    Total Joint Skills Indexed: {ws_js.max_row - 1}")
        print(f"    Modified/Active Joint Skills: {modified_joints}")

    # 5. Check Enchants table
    enchants_path = os.path.join(TABLES_DIR, 'enchants.xlsx')
    if os.path.exists(enchants_path):
        wb_enc = openpyxl.load_workbook(enchants_path)
        ws_enc = wb_enc["Enchants"]
        modified_enchants = 0
        for r in range(2, ws_enc.max_row + 1):
            name = ws_enc.cell(row=r, column=2).value
            status = ws_enc.cell(row=r, column=6).value
            m_name = ws_enc.cell(row=r, column=5).value or ""
            if status in ['Approved', 'Applied', 'Draft'] and m_name:
                modified_enchants += 1
                if len(m_name) > 85:
                    errors.append(f"[ENCHANTS ROW {r}] '{name}': Exceeds 85 chars ({len(m_name)}): '{m_name}'")
                if '~' in m_name:
                    errors.append(f"[ENCHANTS ROW {r}] '{name}': Contains invalid tilde (~)")
        print(f"\n[5] ENCHANTS DATA TABLE CHECK:")
        print(f"    Total Enchants Indexed:     {ws_enc.max_row - 1}")
        print(f"    Modified/Active Enchants:   {modified_enchants}")

    # 6. Check Party Skills table
    party_path = os.path.join(TABLES_DIR, 'party_skills.xlsx')
    if os.path.exists(party_path):
        wb_ps = openpyxl.load_workbook(party_path)
        ws_ps = wb_ps["PartySkills"]
        modified_party = 0
        for r in range(2, ws_ps.max_row + 1):
            name = ws_ps.cell(row=r, column=2).value
            status = ws_ps.cell(row=r, column=6).value
            m_eff = ws_ps.cell(row=r, column=5).value or ""
            if status in ['Approved', 'Applied', 'Draft'] and m_eff:
                modified_party += 1
                lines = m_eff.split('\n')
                if len(lines) > 3:
                    errors.append(f"[PARTY SKILLS ROW {r}] '{name}': Exceeds 3 lines ({len(lines)})")
                for l in lines:
                    if len(l) > 85:
                        errors.append(f"[PARTY SKILLS ROW {r}] '{name}': Exceeds 85 chars ({len(l)}): '{l}'")
                    if '~' in l:
                        errors.append(f"[PARTY SKILLS ROW {r}] '{name}': Contains invalid tilde (~)")
        print(f"\n[6] PARTY SKILLS DATA TABLE CHECK:")
        print(f"    Total Party Skills Indexed: {ws_ps.max_row - 1}")
        print(f"    Modified/Active Party Skills: {modified_party}")

    # 7. Check Food Menu table
    food_path = os.path.join(TABLES_DIR, 'food_menu.xlsx')
    if os.path.exists(food_path):
        wb_fm = openpyxl.load_workbook(food_path)
        ws_fm = wb_fm["FoodMenu"]
        modified_food = 0
        for r in range(2, ws_fm.max_row + 1):
            name = ws_fm.cell(row=r, column=2).value
            status = ws_fm.cell(row=r, column=6).value
            m_eff = ws_fm.cell(row=r, column=5).value or ""
            if status in ['Approved', 'Applied', 'Draft'] and m_eff:
                modified_food += 1
                lines = m_eff.split('\n')
                if len(lines) > 3:
                    errors.append(f"[FOOD MENU ROW {r}] '{name}': Exceeds 3 lines ({len(lines)})")
                for l in lines:
                    if len(l) > 85:
                        errors.append(f"[FOOD MENU ROW {r}] '{name}': Exceeds 85 chars ({len(l)}): '{l}'")
                    if '~' in l:
                        errors.append(f"[FOOD MENU ROW {r}] '{name}': Contains invalid tilde (~)")
        print(f"\n[7] FOOD MENU DATA TABLE CHECK:")
        print(f"    Total Meals Indexed:        {ws_fm.max_row - 1}")
        print(f"    Modified/Active Meals:      {modified_food}")

    # 8. Check Enemy & Summon Attacks table
    attacks_path = os.path.join(TABLES_DIR, 'enemy_attacks.xlsx')
    if os.path.exists(attacks_path):
        wb_ea = openpyxl.load_workbook(attacks_path)
        ws_ea = wb_ea["EnemyAttacks"]
        modified_ea = 0
        for r in range(2, ws_ea.max_row + 1):
            name = ws_ea.cell(row=r, column=3).value
            status = ws_ea.cell(row=r, column=7).value
            m_desc = ws_ea.cell(row=r, column=6).value or ""
            if status in ['Approved', 'Applied', 'Draft'] and m_desc:
                modified_ea += 1
                lines = m_desc.split('\n')
                if len(lines) > 3:
                    errors.append(f"[ENEMY ATTACKS ROW {r}] '{name}': Exceeds 3 lines ({len(lines)})")
                for l in lines:
                    if len(l) > 85:
                        errors.append(f"[ENEMY ATTACKS ROW {r}] '{name}': Exceeds 85 chars ({len(l)}): '{l}'")
                    if '~' in l:
                        errors.append(f"[ENEMY ATTACKS ROW {r}] '{name}': Contains invalid tilde (~)")
        print(f"\n[8] ENEMY & SUMMON ATTACKS CHECK:")
        print(f"    Total Attacks Indexed:      {ws_ea.max_row - 1}")
        print(f"    Modified/Active Attacks:    {modified_ea}")

    # 9. Verify Game Binary & PCK Files
    print(f"\n[9] GAME BINARY & PCK ARCHIVE INTEGRITY CHECK:")
    param_pcks = [
        'TechniqueSkillData.pck', 
        'PassiveSkillData.pck', 
        'MagicSkillData.pck', 
        'UniqueSkillData.pck', 
        'ItemData.pck',
        'SealScrollData.pck',
        'JoinSkillData.pck',
        'EnchantData.pck',
        'PartySkillData.pck',
        'FoodMenuData.pck',
        'EnemyAttackData.pck'
    ]
    for pck_file in param_pcks:
        game_pck = os.path.join(GAME_PARAM_DIR, pck_file)
        if not os.path.exists(game_pck):
            print(f"    [FAIL] Missing in Parameter directory: {pck_file}")
            errors.append(f"Missing {pck_file}")
            continue
            
        try:
            archive = PckArchive(game_pck)
            print(f"    [PASS] {pck_file:<25}: Valid PCK ({len(archive.files)} entries, {os.path.getsize(game_pck)} bytes)")
        except Exception as e:
            print(f"    [FAIL] {pck_file} corrupted: {e}")
            errors.append(str(e))

    # Script PCKs
    script_pcks = ['Teaching.pck', 'Lesson.pck']
    for pck_file in script_pcks:
        game_pck = os.path.join(GAME_SCRIPT_DIR, pck_file)
        if not os.path.exists(game_pck):
            print(f"    [FAIL] Missing in Script directory: {pck_file}")
            errors.append(f"Missing {pck_file}")
            continue
        try:
            archive = PckArchive(game_pck)
            print(f"    [PASS] {pck_file:<25}: Valid PCK ({len(archive.files)} entries, {os.path.getsize(game_pck)} bytes)")
        except Exception as e:
            print(f"    [FAIL] {pck_file} corrupted: {e}")
            errors.append(str(e))

    print(f"\n[10] VERSION CONTROL STATUS:")
    tracked_files = os.popen("git status -s").read().strip().splitlines()
    print(f"    Tracked/Changed files in repo: {len(tracked_files)}")
    
    print("\n" + "=" * 60)
    if not errors:
        print("          ALL CHECKS PASSED: READY FOR IN-GAME TESTING")
    else:
        print(f"          AUDIT FOUND {len(errors)} ERROR(S) - ACTION REQUIRED")
    print("=" * 60 + "\n")
    return len(errors) == 0

if __name__ == "__main__":
    run_audit()
