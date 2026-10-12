"""The writers must reproduce the original files byte for byte when nothing is changed."""
import os
import struct
import unittest

import _paths
from pck_handler import PckArchive, SkillHelper

SKILL_PCKS = {
    'Technique': 'TechniqueSkillData.pck',
    'Magic': 'MagicSkillData.pck',
    'Passive': 'PassiveSkillData.pck',
    'Unique': 'UniqueSkillData.pck',
}


def rewrite(b, category, desc, lvup):
    return SkillHelper.write_skill(b, category, desc, lvup if category != 'Unique' else None)


class ContainerRoundTrip(unittest.TestCase):
    def test_every_backup_archive_rebuilds_identically(self):
        names = sorted(f for f in os.listdir(_paths.BACKUP_DIR) if f.endswith('.pck'))
        scripts = os.path.join(_paths.BACKUP_DIR, 'Script')      # scripts that share a name with a Parameter file
        names += sorted(os.path.join('Script', f) for f in os.listdir(scripts) if f.endswith('.pck'))
        self.assertGreaterEqual(len(names), 47)
        for name in names:
            path = os.path.join(_paths.BACKUP_DIR, name)
            with open(path, 'rb') as f:
                raw = f.read()
            with self.subTest(archive=name):
                self.assertEqual(PckArchive(path).build(), raw)


class SkillEntryRoundTrip(unittest.TestCase):
    def test_rewriting_the_original_text_reproduces_the_entry(self):
        for category, pck in SKILL_PCKS.items():
            for fn, b in PckArchive(os.path.join(_paths.BACKUP_DIR, pck)).files:
                info = SkillHelper.read_skill(b, category)
                with self.subTest(entry=fn):
                    self.assertEqual(rewrite(b, category, info['desc'], info['lvup']), bytes(b))

    def test_battle_message_survives_a_text_change(self):
        """The 4th string ("%name hung in there! Gutsy!") was once dropped by the writer."""
        for category in ('Technique', 'Magic', 'Passive'):
            for fn, b in PckArchive(os.path.join(_paths.BACKUP_DIR, SKILL_PCKS[category])).files:
                info = SkillHelper.read_skill(b, category)
                new = rewrite(b, category, info['desc'] + ' (longer text)', info['lvup'] + '\nextra line')
                with self.subTest(entry=fn):
                    self.assertEqual(SkillHelper.read_skill(new, category)['msg'], info['msg'])
                    self.assertLess(struct.unpack_from('<Q', new, 32)[0], len(new))


if __name__ == '__main__':
    unittest.main()
