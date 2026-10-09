# Level curve of the story (generated)

Written by `tools/checkpoint_levels.py` from the game data and `data_tables/sim_setup.xlsx`. Reference level: the guides (sheet `GuideLevels`), else the level of the random enemies of the zone where the boss stands (the lowest level covering 90% of its encounters), never below the checkpoint before (assumption A15, decided by the user on 2026-10-07). Gap: boss level minus reference. Step: reference minus the reference of the checkpoint before. The mod keeps every jump in its place and none larger (Regression R03).

| Checkpoint | Boss | Boss level | Zone level | Guide | Reference | From | Gap | Step |
|---|---|---|---|---|---|---|---|---|
| C01 | 獣欲の魔女 | 5 | 3 |  | 3 | zone | +2 |  |
| C02 | 狂気の魔猫？ | 7 | 5 |  | 5 | zone | +2 | +2 |
| C03 | ビッグフット | 7 | - |  | 5 | before | +2 | +0 |
| C04 | 狂気の魔猫？×3 | 7 | 5 |  | 5 | zone | +2 | +0 |
| C05 | 狂気の魔猫 | 9 | 6 |  | 6 | zone | +3 | +1 |
| C06 | ガースト | 12 | 9 |  | 9 | zone | +3 | +3 |
| C07 | 嘆きの歌姫 | 13 | 11 | 13 - 15 (atwiki dt2-2 page 37 (Wind Tower, boss)) | 15 | guide | -2 | +6 |
| C08 | ドール | 13 | 12 |  | 15 | zone, held | -2 | +0 |
| C09 | クピードー | 15 | 13 |  | 15 | zone, held | +0 | +0 |
| C10 | ヴラキアの領主 | 16 | 13 |  | 15 | zone, held | +1 | +0 |
| C11 | ヘケト | 18 | 15 |  | 15 | zone | +3 | +0 |
| C12 | 酒乱の剣士 | 18 | - |  | 15 | before | +3 | +0 |
| C13 | エロス | 20 | 18 |  | 18 | zone | +2 | +3 |
| C14 | オツ姫 | 20 | - |  | 18 | before | +2 | +0 |
| C15 | 結界の番人 | 21 | - |  | 18 | before | +3 | +0 |
| C16 | モゲラ | 23 | 21 |  | 21 | zone | +2 | +3 |
| C17 | エージェントM | 26 | 25 |  | 25 | zone | +1 | +4 |
| C18 | 真王エルトリシアが出現 | 28 | 27 | 27 or more (GameFAQs, Hentaicheg, Rousset Royal Villa) | 27 | guide | +1 | +2 |
| C19 | シエスタ | 33 | 30 |  | 30 | zone | +3 | +3 |
| C20 | はぐれベアード | 30 | 30 |  | 30 | zone | +0 | +0 |
| C21 | 闇の商人スフレ | 31 | - |  | 30 | before | +1 | +0 |
| C22 | ペギン先生と七体のペギン / メルヘン・リトル (連戦) | 33 | 33 |  | 33 | zone | +0 | +3 |
| C24 | アーヴァンク | 36 | 35 |  | 35 | zone | +1 | +2 |
| C25 | 武闘家 | 38 | 36 |  | 36 | zone | +2 | +1 |
| C26 | ミシェルとベアトリーチェ | 36 | 38 |  | 38 | zone | -2 | +2 |
| C27 | 森ガーディアン×2 | 40 | 40 |  | 40 | zone | +0 | +2 |
| C28 | マグ・メルの精霊 | 39 | - |  | 40 | before | -1 | +0 |
| C29 | カリオペー | 42 | 44 |  | 44 | zone | -2 | +4 |
| C29a | ドラゴンパピー | 42 | 44 |  | 44 | zone | -2 | +0 |
| C30 | 蛮野の狂戦士 (二連戦) | 41 | 44 |  | 44 | zone | -3 | +0 |
| C31 | マンゴーチン、ドリリアン | 44 | 44 |  | 44 | zone | +0 | +0 |
| C32 | モビーディック | 44 | 44 |  | 44 | zone | +0 | +0 |
| C33 | デスカタフラクト | 46 | 44 |  | 44 | zone | +2 | +0 |
| C34 | 闇の女王 (魔力供給装置を破壊、2連戦) | 46 | 50 |  | 50 | zone | -4 | +6 |
| C35 | スキャナーズ | 52 | 52 |  | 52 | zone | +0 | +2 |
| C36 | 魔神フリード | 54 | 53 |  | 53 | zone | +1 | +1 |
| C37 | アイアンメイデン | 55 | 55 |  | 55 | zone | +0 | +2 |
| C38 | サマエル | 62 | 62 |  | 62 | zone | +0 | +7 |
| C39 | マリクタウス | 65 | 62 |  | 62 | zone | +3 | +0 |
| C40 | デミウルゴス / アティアルコ (連戦) | 70 | 64 |  | 64 | zone | +6 | +2 |
| P01 | Aradia (1st fight), Ruined Shrine Cave | 60 | - |  | 64 | before | -4 | +0 |
| P02 | Hell's Hole, 1st boss (Iktomi) | 66 | 66 |  | 66 | zone | +0 | +2 |
| P03 | Aradia (2nd fight), Wind Tower | 66 | 11 |  | 66 | zone, held | +0 | +0 |
| P04 | Hell's Hole, 2nd boss (Sukuna-Hikona) | 68 | 67 |  | 67 | zone | +1 | +1 |
| P05 | Euthys, Vrachia Town North | 64 | 57 |  | 67 | zone, held | -3 | +0 |
| P06 | Prizren Woods, new part (Overdue) | 68 | 42 |  | 67 | zone, held | +1 | +0 |
| P07 | Rousset Royal Villa, three bosses (Vitoria, Siegdrad, Airavata) | 60 | 27 |  | 67 | zone, held | -7 | +0 |
| P08 | Casino Esperanza, 1st boss (Qitian Dasheng) | 70 | 72 |  | 72 | zone | -2 | +5 |
| P09 | Casino Esperanza, 2nd boss (Azathoth) | 73 | 74 |  | 74 | zone | -1 | +2 |
| P10 | Ruined Shrine Cave, underground (Kuchinawa) | 75 | 66 |  | 74 | zone, held | +1 | +0 |
| P11 | Aradia (3rd fight), Dragon Palace | 72 | 17 |  | 74 | zone, held | -2 | +0 |
| P12 | Matrix, 1st boss (Genbu) | 76 | 78 |  | 78 | zone | -2 | +4 |
| P13 | Matrix, 2nd boss (Nuwa) | 79 | 79 |  | 79 | zone | +0 | +1 |
| P14 | Prizren Woods, final part (Murasaki Shikibu) | 82 | 73 |  | 79 | zone, held | +3 | +0 |
| P15 | Aradia (4th fight), Khorramshahr | 77 | 28 |  | 79 | zone, held | -2 | +0 |
| P16 | Aradia (5th fight), Actim Castle | 80 | 50 |  | 79 | zone, held | +1 | +0 |
| P17 | Plains of Light map 6 (Last Judgment) | 83 | 84 |  | 84 | zone | -1 | +5 |
| P18 | Aradia (6th fight), Dreamscape depth 3 | 84 | 53 |  | 84 | zone, held | +0 | +0 |
| P19 | Three goddesses, Khorramshahr (Atropos, Clotho, Lachesis) | 85 | 33 |  | 84 | zone, held | +1 | +0 |
| P20 | Hell's Hole superboss, weakened (Crom Cruach) | 85 | 67 |  | 84 | zone, held | +1 | +0 |
| P21 | Dreamscape depth ?, 1st boss (Ria the Farsighted) | 85 | 82 |  | 84 | zone, held | +1 | +0 |
| P22 | Dreamscape depth ?, 2nd boss (Chika the Impenetrable) | 85 | 83 |  | 84 | zone, held | +1 | +0 |
| P23 | Dreamscape depth ?, 3rd boss (Samael) | 88 | 83 |  | 84 | zone, held | +4 | +0 |
| P24 | Aradia (7th fight), Gruneworth map 5 | 88 | 90 |  | 90 | zone | -2 | +6 |
| P25 | Gruneworth map 6, 1st boss (Mil the Overlord) | 88 | 90 |  | 90 | zone | -2 | +0 |
| P26 | Gruneworth map 6, 2nd boss (Lina the Statuesque) | 88 | 90 |  | 90 | zone | -2 | +0 |
| P27 | Gruneworth map 6, 3rd boss (Melek Taus) | 90 | 90 |  | 90 | zone | +0 | +0 |
| P28 | Plains of Light map 11 (Hell's Angel) | 92 | 95 |  | 95 | zone | -3 | +5 |
| P29 | Plains of Light map 15, final boss weakened (Panagia) | 99 | 35 |  | 95 | zone, held | +4 | +0 |
| P30 | Casino superboss, weakened (Lolo and Tenerezza) | 90 | 74 |  | 95 | zone, held | -5 | +0 |
| P31 | Matrix superboss, weakened (Magna Meretrix) | 93 | 79 |  | 95 | zone, held | -2 | +0 |
| P32 | Aradia (8th fight), First Sealbook afterword | 99 | 90 |  | 95 | zone, held | +4 | +0 |
| P33 | Final boss after the 8th Aradia (Panagia, then Radiant Being) | 99 | 35 |  | 95 | zone, held | +4 | +0 |
| P34 | Casino VIP, 1st (Tama the Red) | 95 | 65 |  | 95 | zone, held | +0 | +0 |
| P35 | Casino VIP, 2nd (Riko the Reclusive) | 95 | 65 |  | 95 | zone, held | +0 | +0 |
| P36 | Casino VIP, 3rd (Rai the Sweltering) | 96 | 65 |  | 95 | zone, held | +1 | +0 |
| P37 | Casino VIP, 4th (Mor the Drunken) | 96 | 65 |  | 95 | zone, held | +1 | +0 |
| P38 | Casino VIP, 5th (Gam the Wise) | 96 | 65 |  | 95 | zone, held | +1 | +0 |
| P39 | Casino VIP, 6th (Ruu the Woodsy) | 97 | 65 |  | 95 | zone, held | +2 | +0 |
| P40 | Casino VIP, 7th (five bosses with Mandra Prince and Princess) | 99 | 65 |  | 95 | zone, held | +4 | +0 |
| P41 | Wandering Brigade (Citlalinicue) | 96 | 68 |  | 95 | zone, held | +1 | +0 |
| P42 | Wandering Brigade (Marduk) | 97 | 69 |  | 95 | zone, held | +2 | +0 |
| P43 | Wandering Brigade (Arjuna) | 95 | 78 |  | 95 | zone, held | +0 | +0 |
| P44 | Wandering Brigade (Yoshitsune) | 98 | 83 |  | 95 | zone, held | +3 | +0 |
| P45 | Four Therian Kings (Zouchou Kuma) | 98 | 29 |  | 95 | zone, held | +3 | +0 |
| P46 | Four Therian Kings (Jikoku Peggin) | 98 | 40 |  | 95 | zone, held | +3 | +0 |
| P47 | Four Therian Kings (Koumoku Mary) | 98 | 75 |  | 95 | zone, held | +3 | +0 |
| P48 | Four Therian Kings (Bishamon Peggy) | 99 | 52 |  | 95 | zone, held | +4 | +0 |
| P49 | Hell's Hole superboss (Crom Cruach, two fights) | 99 | 67 |  | 95 | zone, held | +4 | +0 |
| P50 | Casino superboss (Lolo and Tenerezza) | 99 | 74 |  | 95 | zone, held | +4 | +0 |
| P51 | Matrix superboss (Adon, Magna Meretrix, Samson) | 99 | 79 |  | 95 | zone, held | +4 | +0 |
| P52 | First Sealbook afterword (Bearerophon) | 94 | 90 |  | 95 | zone, held | -1 | +0 |
| P53 | First Sealbook afterword (Magical Mary) | 95 | 90 |  | 95 | zone, held | +0 | +0 |
| P54 | First Sealbook afterword (Beard Master) | 96 | 90 |  | 95 | zone, held | +1 | +0 |
| P55 | First Sealbook afterword (Mul the Mechanical) | 98 | 90 |  | 95 | zone, held | +3 | +0 |

## Jumps of vanilla (30)

A rise of 5 levels or more, or a boss 3 levels or more above its reference.

| Checkpoint | Boss | Step | Gap |
|---|---|---|---|
| C05 | 狂気の魔猫 | +1 | +3 |
| C06 | ガースト | +3 | +3 |
| C07 | 嘆きの歌姫 | +6 | -2 |
| C11 | ヘケト | +0 | +3 |
| C12 | 酒乱の剣士 | +0 | +3 |
| C15 | 結界の番人 | +0 | +3 |
| C19 | シエスタ | +3 | +3 |
| C34 | 闇の女王 (魔力供給装置を破壊、2連戦) | +6 | -4 |
| C38 | サマエル | +7 | +0 |
| C39 | マリクタウス | +0 | +3 |
| C40 | デミウルゴス / アティアルコ (連戦) | +2 | +6 |
| P08 | Casino Esperanza, 1st boss (Qitian Dasheng) | +5 | -2 |
| P14 | Prizren Woods, final part (Murasaki Shikibu) | +0 | +3 |
| P17 | Plains of Light map 6 (Last Judgment) | +5 | -1 |
| P23 | Dreamscape depth ?, 3rd boss (Samael) | +0 | +4 |
| P24 | Aradia (7th fight), Gruneworth map 5 | +6 | -2 |
| P28 | Plains of Light map 11 (Hell's Angel) | +5 | -3 |
| P29 | Plains of Light map 15, final boss weakened (Panagia) | +0 | +4 |
| P32 | Aradia (8th fight), First Sealbook afterword | +0 | +4 |
| P33 | Final boss after the 8th Aradia (Panagia, then Radiant Being) | +0 | +4 |
| P40 | Casino VIP, 7th (five bosses with Mandra Prince and Princess) | +0 | +4 |
| P44 | Wandering Brigade (Yoshitsune) | +0 | +3 |
| P45 | Four Therian Kings (Zouchou Kuma) | +0 | +3 |
| P46 | Four Therian Kings (Jikoku Peggin) | +0 | +3 |
| P47 | Four Therian Kings (Koumoku Mary) | +0 | +3 |
| P48 | Four Therian Kings (Bishamon Peggy) | +0 | +4 |
| P49 | Hell's Hole superboss (Crom Cruach, two fights) | +0 | +4 |
| P50 | Casino superboss (Lolo and Tenerezza) | +0 | +4 |
| P51 | Matrix superboss (Adon, Magna Meretrix, Samson) | +0 | +4 |
| P55 | First Sealbook afterword (Mul the Mechanical) | +0 | +3 |
