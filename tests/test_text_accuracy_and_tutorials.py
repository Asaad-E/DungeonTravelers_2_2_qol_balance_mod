"""Regression tests for tutorial dialogue text, QoL/Balance text accuracy, and class overrides."""
import os
import sys
import tempfile
import unittest

import openpyxl

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_DIR, 'tools'))

import build_variant as bv  # noqa: E402
import class_tutorial_text as ctt  # noqa: E402
from pck_handler import ClassDataHelper, PckArchive, SkillHelper  # noqa: E402
import text_checks  # noqa: E402


FORBIDDEN_TUTORIAL_PHRASES = (
    'dainger guard',
    'circle protection',
    'tier-2',
    'tier-3',
    'the entire game',
    'mid-game',
    'nukes',
    'health bars',
    'room-clearers',
    'boss skills',
    'single best',
    'hyper-fast',
    'holy light',
    'with cheer',
    'confusion',
)


def _sheet_rows_by_key(xlsx_path, sheet_name, key_col):
    """Return {key_value: dict(row)} for every non-empty row of a workbook sheet."""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb[sheet_name]
    cols = [c.value for c in ws[1]]
    out = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        record = dict(zip(cols, row))
        key = record.get(key_col)
        if key is not None:
            out[key] = record
    return out


class TestClassTutorialText(unittest.TestCase):
    """Every teaching dialogue box must fit box bounds, encoding, and in-universe wording."""

    def test_all_new_teaching_boxes_meet_bounds_and_wording(self):
        self.assertGreater(len(ctt.NEW_TEACHING_SCRIPTS), 0)
        for script_name, (_title, _start, intro, boxes, _end, _msg_id) in ctt.NEW_TEACHING_SCRIPTS.items():
            self.assertTrue(intro, f'{script_name}: missing intro line')
            intro.encode('latin-1')
            for idx, box in enumerate(boxes):
                ctx = f'{script_name} box {idx}'
                self.assertTrue(box, f'{ctx}: empty box')
                box.encode('latin-1')
                self.assertNotIn('~', box, f'{ctx}: tilde glyph is invisible in DT2-2 font')
                lines = box.split('\n')
                self.assertLessEqual(len(lines), 3, f'{ctx}: {len(lines)} lines (> 3)')
                for line_no, line in enumerate(lines, 1):
                    cap = 65 if line_no == 3 else 70
                    self.assertLessEqual(len(line), cap, f'{ctx} line {line_no}: {len(line)} chars (> {cap})')
                self.assertEqual(text_checks.out_of_game_words(box, ''), [], f'{ctx}: out-of-game words')
                lowered = box.lower()
                for phrase in FORBIDDEN_TUTORIAL_PHRASES:
                    self.assertNotIn(phrase, lowered, f'{ctx}: stale/slang phrase {phrase!r}')

    def test_class_tutorials_match_actual_kits(self):
        by_prefix = {}
        for boxes in (ctt.LESSON_08_BOXES, ctt.LESSON_13_BOXES, ctt.LESSON_24_BOXES):
            for box in boxes:
                if ':' in box.split('\n', 1)[0]:
                    cls = box.split(':', 1)[0].strip()
                    by_prefix[cls] = box
        self.assertNotIn('Cheer', by_prefix['Maid'])
        self.assertIn('Cook', by_prefix['Maid'])
        self.assertNotIn('doll', by_prefix['Spieler'].lower())
        self.assertNotIn('bonus exp', by_prefix['Spieler'].lower())
        self.assertNotIn('Accelerator', by_prefix['Enchantress'])
        self.assertIn('Circle Brave', by_prefix['Enchantress'])
        self.assertNotIn('Holy Light', by_prefix['Bishop'])
        self.assertIn('Full Heal', by_prefix['Bishop'])
        self.assertIn('two songs at once', by_prefix['Diva'].lower())
        self.assertIn('two dances active at once', by_prefix['Etoile'].lower())

    def test_build_tutorials_succeeds_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            param_dir = os.path.join(tmp, 'Data', 'ENG', 'Parameter')
            os.makedirs(param_dir, exist_ok=True)
            problems = []
            counts, packs = bv.build_tutorials(
                param_dir, os.path.join(bv.TABLES_DIR, 'balance_tutorial_text.xlsx'), problems
            )
            self.assertEqual(problems, [])
            self.assertEqual(sorted(packs), ['Lesson.pck', 'Teaching.pck'])
            self.assertGreater(counts['written'], 0)
            script_dir = os.path.join(tmp, 'Data', 'ENG', 'Script')
            for pck_name in packs:
                self.assertTrue(os.path.isfile(os.path.join(script_dir, pck_name)))


class TestTextAccuracyAndOverrides(unittest.TestCase):
    """Fixed skill/class tooltips and variant overrides must stay consistent across QoL and Balance."""

    def test_qol_rules_positive_trance_stays_vanilla_100(self):
        rules = _sheet_rows_by_key(os.path.join(bv.TABLES_DIR, 'qol_rules.xlsx'), 'UniqueSkillLabels', 'Skill')
        self.assertEqual(rules['Positive Trance']['Label'], 'Pep over 100 per +1% damage')

    def test_qol_skill_text_fixes(self):
        skills = _sheet_rows_by_key(os.path.join(bv.TABLES_DIR, 'qol_skill_text.xlsx'), 'Skills', 'Filename')
        self.assertIn('Pep over 100 per +1% damage', skills['UniqueSkillData_0364.bin']['QoL_Desc'])
        self.assertEqual(skills['PassiveSkillData_0309.bin']['QoL_LvUp'], 'Activation rate: 10%')
        rose = skills['TechniqueSkillData_0089.bin']
        self.assertIn('minor', rose['QoL_Desc'])
        self.assertIn('ATK: 120%', rose['QoL_LvUp'])
        self.assertIn('TP Cost: 5', rose['QoL_LvUp'])

    def test_balance_skill_text_overrides(self):
        bal = _sheet_rows_by_key(os.path.join(bv.TABLES_DIR, 'balance_skill_text.xlsx'), 'Skills', 'Filename')
        self.assertIn('Pep over 85 per +1% damage', bal['UniqueSkillData_0364.bin']['Balance_Desc'])
        self.assertEqual(bal['PassiveSkillData_0309.bin']['Balance_LvUp'], 'Activation rate: 15%')
        rose = bal['TechniqueSkillData_0089.bin']
        self.assertIn('severe', rose['Balance_Desc'])
        self.assertIn('ATK: 180%', rose['Balance_LvUp'])
        self.assertIn('TP Cost: 12', rose['Balance_LvUp'])
        self.assertIn('Speed: 1.05x -> 1.18x', bal['TechniqueSkillData_0095.bin']['Balance_LvUp'])
        for guard_fn in ('MagicSkillData_0184.bin', 'MagicSkillData_0185.bin', 'MagicSkillData_0186.bin'):
            self.assertIn('Chant: 2.2x -> 3x', bal[guard_fn]['Balance_LvUp'], guard_fn)
        self.assertIn('Speed: 1.56x -> 1.71x', bal['MagicSkillData_0195.bin']['Balance_LvUp'])
        for tier2_fn in ('MagicSkillData_0145.bin', 'MagicSkillData_0149.bin', 'MagicSkillData_0153.bin',
                         'MagicSkillData_0157.bin', 'MagicSkillData_0161.bin'):
            self.assertIn('Chant: 0.7x', bal[tier2_fn]['Balance_LvUp'], tier2_fn)

    def test_qol_and_balance_class_descriptions(self):
        qol_classes = bv.load_class_text(os.path.join(bv.TABLES_DIR, 'qol_class_text.xlsx'))
        valk = qol_classes['ClassData_03.bin']['desc']
        self.assertIn('Material Guard and\nSpell Guard', valk)
        self.assertIn('spears,\nswords, and shields', valk)
        self.assertNotIn('Circle Protection', valk)

        diva = qol_classes['ClassData_23.bin']['desc']
        self.assertIn('restore TP, raise crits and\nspeed, and accelerate chanting', diva)
        self.assertNotIn('boost ATK', diva)

        self.assertEqual(bv.VARIANTS['balance'].get('class_overrides'), 'balance_class_text.xlsx')
        problems = []
        changed = bv.apply_class_overrides(qol_classes, os.path.join(bv.TABLES_DIR, 'balance_class_text.xlsx'), problems)
        self.assertEqual(problems, [])
        self.assertEqual(changed, 1)
        sniper = qol_classes['ClassData_09.bin']['desc']
        self.assertIn('bows or firearms', sniper)
        self.assertEqual(text_checks.out_of_game_words(sniper, qol_classes['ClassData_09.bin']['vanilla']), [])

        with tempfile.TemporaryDirectory() as tmp:
            build_problems = []
            bv.build_classes(tmp, qol_classes, build_problems)
            self.assertEqual(build_problems, [])
            built_pck = dict(PckArchive(os.path.join(tmp, 'ClassData.pck')).files)
            sniper_bin = ClassDataHelper.read_class(built_pck['ClassData_09.bin'])
            self.assertIn('bows or firearms', sniper_bin['desc'])
            valk_bin = ClassDataHelper.read_class(built_pck['ClassData_03.bin'])
            self.assertIn('Material Guard and', valk_bin['desc'])

    def test_built_variants_match_fixed_texts(self):
        qol_dir = os.path.join(bv.BUILD_DIR, 'qol', 'Data', 'ENG', 'Parameter')
        bal_dir = os.path.join(bv.BUILD_DIR, 'balance', 'Data', 'ENG', 'Parameter')
        if not (os.path.isdir(qol_dir) and os.path.isdir(bal_dir)):
            return

        qol_classes = dict(PckArchive(os.path.join(qol_dir, 'ClassData.pck')).files)
        bal_classes = dict(PckArchive(os.path.join(bal_dir, 'ClassData.pck')).files)
        self.assertIn('bows rather than firearms', ClassDataHelper.read_class(qol_classes['ClassData_09.bin'])['desc'])
        self.assertIn('bows or firearms', ClassDataHelper.read_class(bal_classes['ClassData_09.bin'])['desc'])

        qol_uniq = SkillHelper.read_skill(dict(PckArchive(os.path.join(qol_dir, 'UniqueSkillData.pck')).files)['UniqueSkillData_0364.bin'], 'Unique')
        bal_uniq = SkillHelper.read_skill(dict(PckArchive(os.path.join(bal_dir, 'UniqueSkillData.pck')).files)['UniqueSkillData_0364.bin'], 'Unique')
        self.assertIn('Pep over 100', qol_uniq['desc'])
        self.assertIn('Pep over 85', bal_uniq['desc'])

        qol_pass = SkillHelper.read_skill(dict(PckArchive(os.path.join(qol_dir, 'PassiveSkillData.pck')).files)['PassiveSkillData_0309.bin'], 'Passive')
        bal_pass = SkillHelper.read_skill(dict(PckArchive(os.path.join(bal_dir, 'PassiveSkillData.pck')).files)['PassiveSkillData_0309.bin'], 'Passive')
        self.assertEqual(qol_pass['lvup'], 'Activation rate: 10%')
        self.assertEqual(bal_pass['lvup'], 'Activation rate: 15%')

        qol_tech = dict(PckArchive(os.path.join(qol_dir, 'TechniqueSkillData.pck')).files)
        bal_tech = dict(PckArchive(os.path.join(bal_dir, 'TechniqueSkillData.pck')).files)
        qol_rose = SkillHelper.read_skill(qol_tech['TechniqueSkillData_0089.bin'], 'Technique')
        bal_rose = SkillHelper.read_skill(bal_tech['TechniqueSkillData_0089.bin'], 'Technique')
        self.assertIn('minor', qol_rose['desc'])
        self.assertIn('TP Cost: 5', qol_rose['lvup'])
        self.assertIn('severe', bal_rose['desc'])
        self.assertIn('TP Cost: 12', bal_rose['lvup'])
        bal_spartan = SkillHelper.read_skill(bal_tech['TechniqueSkillData_0095.bin'], 'Technique')
        self.assertIn('1.05x -> 1.18x', bal_spartan['lvup'])

        bal_mag = dict(PckArchive(os.path.join(bal_dir, 'MagicSkillData.pck')).files)
        self.assertIn('Chant: 2.2x -> 3x', SkillHelper.read_skill(bal_mag['MagicSkillData_0184.bin'], 'Magic')['lvup'])
        self.assertIn('Speed: 1.56x -> 1.71x', SkillHelper.read_skill(bal_mag['MagicSkillData_0195.bin'], 'Magic')['lvup'])
        self.assertIn('Chant: 0.7x', SkillHelper.read_skill(bal_mag['MagicSkillData_0145.bin'], 'Magic')['lvup'])


if __name__ == '__main__':
    unittest.main()
