"""Sheet MercenaryUnlocks of data_tables/sim_setup.xlsx (2026-10-17): when each flag that unlocks a stage of a mercenary is set, as a
checkpoint of the model. The bar offers, of the stages whose flag is set, the one of the highest level (0x58adb0 - 0x58b060, read
2026-10-17; docs/FORMULAS.md 16.5). The flag of each stage is the int at 0xB4 of its NPCData.

Every flag is located in the event scripts (.adv.bin in Data/ENG/Script/*.pck and Data/ENG/Dungeon/Dungeon.pck, opcode 0x4C calling
vtable+0x1fc SetFlag at 0x4c88ff after fixed-battle opcode 0x1F at 0x4cc130) or in QuestRankData.pck (0x596176 and 0x59618d,
SetFlag(quest_rank + 1400, 1)). When a script sets a flag after a checkpoint's boss battle, the stage is open from the next checkpoint."""
import os
import openpyxl

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
PATH = os.path.join(ROOT, 'data_tables', 'sim_setup.xlsx')
SOURCE = 'docs/FORMULAS.md 16.5 (0x58adb0, 0x4c88ff, 0x59618d); Data/ENG/Script/*.pck, Dungeon.pck, QuestRankData.pck'

# (flag, from_cp, until_cp, basis)
UNLOCKS = [
    (135, 'C25', None, 'story: evt02.pck/evt02.adv.bin (Main07_20_Start, chapter 7, the Tavern opens after C24)'),
    (136, 'C27', None, 'story: evt02.pck/evt02.adv.bin (Main08_00_Start, start of chapter 8 after C26)'),
    (151, 'C30', None, 'story: St10_0010/Main08_09.adv.bin (Main08_15_Start, chapter 8 before C30)'),
    (172, 'C35', None, 'story: evt02.pck/evt02.adv.bin (Main10_00_Start, start of chapter 10 after C34)'),
    (197, 'C36', None, 'story: St13_0140/Main10_25.adv.bin (Dreamscape 14F, after C35 on 14F, before C36 on 15F)'),
    (204, 'C37', None, 'story: evt02.pck/evt02.adv.bin (Main11_00_Start, start of chapter 11 after C36)'),
    (211, 'C37', None, 'story: St14_1040/Main11_07.adv.bin (Gruneworth 4F, chapter 11 before C37a)'),
    (215, 'C38', None, 'story: St15_0010/Main12_00.adv.bin (Main12_00_Start, start of chapter 12 before C38)'),
    (220, 'C39', None, 'story: St15_1060/Main12_05.adv.bin (after battle 41 Samael, C38)'),
    (224, 'C39', None, 'story: St15_1120/Main12_09.adv.bin (Main12_09_Start, before battle 41 Melek Taus, C39)'),
    (230, 'P01', None, 'postgame: evt02.pck/evt02.adv.bin (Main20_00_Start, start of postgame after C40)'),
    (250, 'P11', None, 'postgame: St00_1020/St00_c0020.adv.bin (after battle 41 Kuchinawa, P10)'),
    (263, 'P05', None, 'postgame: St03_0011/St03_b0020.adv.bin (after battle 41 Kaguya on Vrachia North, before P05)'),
    (284, 'P08', None, 'postgame: St06_0030/St06_c0050.adv.bin (after battle 44 Vitoria/Siegdrad/Airavata, P07)'),
    (318, 'P15', None, 'postgame: St11_0010/St11_0090.adv.bin (after battle 45 Murasaki Shikibu, P14)'),
    (319, 'C33', None, 'story: St12_0010/St12_a0110.adv.bin (after battle 41 Moby Dick, C32)'),
    (320, 'C34', None, 'story: St12_0010/St12_a0130.adv.bin (after battle 42 Death Cataphract, C33)'),
    (334, 'P24', None, 'postgame: St13_0030/St13_c0060.adv.bin (after battle 41 Samael Lv88, P23)'),
    (353, 'C38', None, 'story: St14_1010/St14_a0080.adv.bin (after battle 41 Iron Maiden, C37)'),
    (358, 'P25', None, 'postgame: St14_1050/St14_e0060.adv.bin (after battle 42 7th Aradia, P24)'),
    (359, 'P28', None, 'postgame: St14_1060/St14_f0040.adv.bin (after battle 41 Melek Taus Lv90, P27)'),
    (365, 'P33', None, 'postgame: St15_1160/St15_q0030.adv.bin (after battle 41 8th Aradia, P32)'),
    (370, 'P03', None, 'postgame: St20_1020/St20_c0040.adv.bin (after battle 42 Iktomi, P02)'),
    (374, 'P21', None, 'postgame: St20_1040/St20_e0010.adv.bin (after battle 41 weakened Crom Cruach, P20)'),
    (376, 'P05', None, 'postgame: St20_1040/St20_e0040.adv.bin (after battle 43 Sukuna-Hikona, P04)'),
    (381, 'P08', None, 'postgame: St21_0010/St21_a0150.adv.bin (after battle 41 Jungfrau on Casino 1F, before P08)'),
    (384, 'P09', None, 'postgame: St21_0020/St21_b0110.adv.bin (after battle 41 Qitian Dasheng, P08)'),
    (385, 'P10', None, 'postgame: St21_0060/St21_f0020.adv.bin (after battle 41 Azathoth, P09)'),
    (386, 'P41', None, 'postgame: St21_0060/St21_f0080.adv.bin (after battle 42 Casino VIP 7th fight, P40)'),
    (388, 'P31', None, 'postgame: St21_0060/St21_f0100.adv.bin (after battle 45 weakened Lolo and Tenerezza, P30)'),
    (400, 'P13', None, 'postgame: St22_1010/St22_a0110.adv.bin (after battle 41 Genbu, P12)'),
    (402, 'P12', None, 'postgame: St22_1010/St22_a0020.adv.bin (Matrix 1F entry event, before P12)'),
    (407, 'P14', None, 'postgame: St22_1020/St22_b0080.adv.bin (after battle 43 Nuwa, P13)'),
    (412, 'P32', None, 'postgame: St22_1020/St22_b0540.adv.bin (after battle 45 weakened Magna Meretrix, P31)'),
    (418, 'P18', None, 'postgame: St23_0060/St23_f0040.adv.bin (after battle 41 Last Judgment, P17)'),
    (928, 'P06', None, 'postgame: evt02.pck/St93.adv.bin (after defeating Euthys on Vrachia North, P05)'),
    (1000, None, None, 'never: placeholder record 101 (Battle.pck/Main06_10.adv.bin, cleared in Item0885.pck/Main06_12.adv.bin)'),
    (1001, None, None, 'never: placeholder record 102 (Battle.pck/Main06_10.adv.bin, cleared in Item0885.pck/Main06_12.adv.bin)'),
    (1002, None, None, 'never: placeholder record 103 (St07_0010/Main06_13.adv.bin, cleared in Item0885.pck/Main06_12.adv.bin)'),
    (1003, None, None, 'never: Michelle, a guest of the story (joined by opcode 0x81, not hired at the Tavern)'),
    (1004, 'P20', None, 'postgame: SEV.pck/sev_296.adv.bin (after defeating Three Fates at Khorramshahr, P19)'),
    (1006, 'P45', None, 'postgame: St23_0040/St23_d0030.adv.bin (after battle 41 Yoshitsune, P44)'),
    (1008, 'P43', None, 'postgame: St21_1010/St21_g0020.adv.bin (after battle 41 Marduk, P42)'),
    (1010, 'P42', None, 'postgame: St20_1040/St20_e0140.adv.bin (after battle 45 Citlalinicue, P41)'),
    (1012, 'P44', None, 'postgame: St22_1020/St22_b0030.adv.bin (after battle 42 Arjuna, P43)'),
    (1089, 'C37', None, 'side event: St10_0010/St10_0390.adv.bin (after battle 52 Azmaria Lv50 in Prizren Woods; party reaches Lv50 at C37)'),
    (1094, 'C38', None, 'quest rank: QuestRankData_12.bin (Quest Rank 12, 390 pts; Miranda Lv53, party reaches Lv53 at C38)'),
    (1104, 'P21', None, 'postgame: St21_1010/St21_g0010.adv.bin (Casino basement after Octopunch; Lv86, party reaches Lv86 at P21)'),
    (1106, 'C28', 'C32', 'story: St10_0010/cont_09.adv.bin (set in 9th talk event, chapter 8) to St12_0040/cont_10.adv.bin (cleared in 10th, chapter 9)'),
    (1419, 'P21', None, 'quest rank: 0x59618d SetFlag(quest_rank + 1400, 1) on QuestRankData_19.bin (Quest Rank 19, 840 pts; Lv82-90 stages)'),
]

wb = openpyxl.load_workbook(PATH)
if 'MercenaryUnlocks' in wb.sheetnames:
    del wb['MercenaryUnlocks']
ws = wb.create_sheet('MercenaryUnlocks')
ws.append(['Flag', 'From checkpoint', 'Until checkpoint', 'Basis', 'Source'])
for flag, f_cp, u_cp, basis in UNLOCKS:
    ws.append([flag, f_cp, u_cp, basis, SOURCE])
wb.save(PATH)
print(len(UNLOCKS), 'flags written to MercenaryUnlocks')
