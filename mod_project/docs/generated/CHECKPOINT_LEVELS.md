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

## Jumps of vanilla (11)

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
