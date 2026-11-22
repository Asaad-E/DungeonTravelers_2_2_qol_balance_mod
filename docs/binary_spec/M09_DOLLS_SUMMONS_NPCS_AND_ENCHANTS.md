# M09 — Dolls, Summons, Guest NPCs & Enchantments (`DT22_en_unwrapped.vanilla.exe`)

> **Clean-Room Binary Specification (`0x413000..0x570000`)**
> Extracted directly from `backups/exe/DT22_en_unwrapped.vanilla.exe` (x86-32, image base `0x400000`, SHA-256 `785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60`), `docs/binary_spec/00_INVENTORY.json`, and raw `backups/**/*.pck`. Covers:
> 1. **Dolls & ETC Units (`unitId 2000..2999`):** `CCommand_0146::AddTask` spawner (`0x484330`), `CCommand_0427` Genjimaru (`0x48b1f0`), Shadow Heart (`0x437a1f`), global cap (`12`), `cmd 313` Double Puppet manager (`0x43c790`), stat inheritance, Soul Seal (`cmd 314`), Doll Bonus (`cmd 286` + enchants `304`/`305`), `vtable+0xfc` combat guards, AI/turn dispatch, lifetime expiry, and owner death/ailment cancellation.
> 2. **Summons & Guest NPCs (`unitId 3000..3999`):** `GameManager+0x141c` (`CGamePlayerStatusSummon`, `unitId 3000`) and `GameManager+0x1424` (`CGamePlayerStatusNPC`, `unitId 3001`), `flag33` initial gauge, untargetability (`0x43e6d0`), avg-level tier walk & party-max stat scaling (`0x4ffc90`), party Sealbook inheritance (`0x4ff530`), Mercenary Buddy enchants `295`/`297`, Samba/Salsa `199` turn-start tick (`0x436322`), and Guest NPC battle-count expiry (`0x447150`).
> 3. **Enchantment Aggregation & Stacking Engine:** `_SetupEnchant` (`0x4f62c0`), `_AddEnchant` (`0x4f64b0`), dual-wield offhand `flags & 0x80` filter, `flags & 1` stacking vs boolean deduplication, `vtable+0xf0` (`0x4f5470`), enemy stub (`0x4d4dd0`), and `PartyHasEnchant` (`0x4e4f50`).
> 4. **Complete Grouped Master Table & Specifications of ALL 280 Enchantments** from `EnchantData.pck` (100% coverage across all 15 functional families; note that `0x5182c9`/`0x5222b2` in `00_INVENTORY.json` are UI `GameManager` 4-arg calls rather than enchant `1`, while enchant `1` is handled directly inside `_CalculateParameterEnchant` at `0x4f8382`).

---

## 1. Dolls & ETC Units (`unitId 2000..2999`)

### M09.01 ETC Class Hierarchy, Doll Spawner (`CCommand_0146::AddTask`) & Complete Doll Table

- **Binary VA(s):** `0x484330..0x485f9f` (`Command::CCommand_0146::AddTask`, jump tables `0x485d5c`, `0x485e54`, `0x485f04`), `0x48b1f0..0x48b3b0` (`Command::CCommand_0427::AddTask` Genjimaru), `0x437950..0x437a60` (Turn-Start Shadow Heart `cmd 448`), `0x6cc7b8..0x6cc7e7` (12-entry inherited status table), `0x6d448c` / `0x6d45cc` / `0x6d4768` / `0x6d4904` / `0x6d4aa0` / `0x6d4c3c` / `0x6d4dd8` / `0x6d4f70` (ETC RTTI vtables)
- **Calls:** `0x47e340` (`FindCommand`), `0x61e650` (`round_f32_to_i32`), `0x4fd840` (`CGamePlayerStatusETCBase::ctor`), `0x4fe5f0` (`CGamePlayerStatusOtherETCBase::ctor`), `0x4fd3d0` (`CGameEnemyStatusETCBase::ctor`), `0x4fe2e0` (`CGamePlayerStatusETCShadowHearts::ctor`), `0x4fa870`, `0x48bbc0` (clone `CCommand`), `0x43a150` (`M09.02` `CBattleBase::AddETCUnit`)
- **CalledBy:** `CCommand::Execute` (`M00.06` / `0x47e500` via `CCommand_0146` / `CCommand_0427`), `CBattleBase::Update` TurnPhaseNo 15 (`M00.03` / `0x4378d9`)
- **Typed Pseudocode:**
```text
// 12-entry inherited command whitelist at 0x6cc7b8 (copied from caster onto every CCommand_0146 ETC unit):
const INHERITED_CMDS_0x6cc7b8: u32[12] = [
    41 (0x29 ATK), 42 (0x2a DEF), 43 (0x2b INT), 44 (0x2c RES), 45 (0x2d DEX), 46 (0x2e AGI),
    48 (0x30 Trump Card), 189 (0xbd Magical Change), 193 (0xc1 Limiter Removal),
    194 (0xc2 Beginning of the End), 256 (0x100 Lefty Bonus), 286 (0x11e Doll Bonus)
]

function CCommand_0146_AddTask(this: CCommand_0146*, outTasks, battleInfo, caster, casterCmds):
    if battleInfo.battle == null: return
    spawnCount: i32 = round_f32_to_i32(this.GetValue())             // 0x61e650
    baseTurns: i32  = (c147 = FindCommand(casterCmds, 0x93)) ? round_f32_to_i32(c147.GetValue()) : 0
    for i in 0 .. spawnCount - 1:
        if playerCaster = dynamic_cast<CGamePlayerStatusBase*>(caster):
            if !playerCaster.vtable_0x100_IsNPCOrSummon():          // Player-side Doll / Arrow (0x484449..0x484905)
                skillId = this.skillId                              // [this+0x14]
                skillLv = IsFixedLvSkill(skillId) ? 1 : playerCaster.GetSkillLevel(skillId)
                turns = baseTurns
                // Player Dolls (0x5f..0x64) ALSO add cmd 297 (0x129 Doll Turn Count UP); Arrows (0x31, 0x13b) do NOT:
                switch skillId:
                    case 0x31  (49):  etc = new CGamePlayerStatusETCArrow(playerCaster, turns, [0x6a], skillLv, 0x31)
                    case 0x5f  (95):  turns += round(cmd297); etc = new CGamePlayerStatusETCDoll(..., [0x65], cmdId=0xe4 Spartan)
                    case 0x60  (96):  turns += round(cmd297); etc = new CGamePlayerStatusETCDoll(..., [0x66], cmdId=0xe5 Oracles)
                    case 0x61  (97):  turns += round(cmd297); etc = new CGamePlayerStatusETCDoll(..., [0x68], cmdId=0xe6 Catalina)
                    case 0x62  (98):  turns += round(cmd297); etc = new CGamePlayerStatusETCDoll(..., [0x67], cmdId=0xe7 Mercidarian)
                    case 0x63  (99):  turns += round(cmd297); etc = new CGamePlayerStatusETCDoll(..., [0x69], cmdId=0xe8 Perdurabo)
                    case 0x64  (100): turns += round(cmd297); etc = new CGamePlayerStatusETCDoll(..., [0xeb,0xec,0xed,0xee,0xef], cmdId=0xe9 Musiy)
                    case 0x13b (315): etc = new CGamePlayerStatusETCArrow(playerCaster, turns, [0x155], 1, 0x13b)
                etc.InitStatus(1, 1); etc.vtable_0x108_RecalcStats()
            else:                                                   // NPC-cast Doll (0x48490a..0x4852c9)
                // Dispatches on enemyAttackId ([this+0x18]) in {0x2b2..0x2df (31 cases via 0x485e54), 0x6fd, 0x6fe, 0x6ff}
                // Constructs CGamePlayerStatusOtherETCBase (0x190 bytes) or CGamePlayerStatusOtherETCDoll (vt 0x6d4f70, [etc+0x190]=puppetCmd)
        else:                                                       // Enemy-cast Doll (0x4852ca..0x485c24)
            // Dispatches on same 34 enemyAttackIds via jump table 0x485f04 -> CGameEnemyStatusETCDoll (vt 0x6d448c, [etc+0x19c]=puppetCmd)
        // Inherit whitelist statuses & strip all non-ailment non-whitelisted statuses (0x485c25..0x485d54):
        for cmd in casterCmds:
            if !cmd.vtable_0x68_IsTrueAilment():
                if cmd.GetCommandId() in INHERITED_CMDS_0x6cc7b8:
                    etc.AddStatus(CloneCommand(cmd))                // 0x48bbc0 -> vtable+0x54
                else:
                    etc.RemoveStatus(cmd.GetCommandId())            // vtable+0x64
        battleInfo.battle.AddETCUnit(etc)                           // 0x43a150

function CCommand_0427_AddTask(this, outTasks, battleInfo, caster, casterCmds): // Genjimaru (0x48b1f0)
    // Refuses if any active ETC unit in battle already casts to CGamePlayerStatusETCGenzimaru (RTTI 0x70855c).
    // Otherwise spawns CGamePlayerStatusETCGenzimaru (vt 0x6d4aa0, turns=3, actions=[0x6b], lv=1) -> AddETCUnit (0x43a150).

function TurnStart_ShadowHeart_cmd448(battle, actor):               // 0x437950..0x437a60
    // Refuses if actor already owns any ETC unit on its side; otherwise spawns CGamePlayerStatusETCShadowHearts
    // (0x300 bytes, vt 0x6d4c3c, turns=3, skillId=0x17c, actions=basic attack) -> AddETCUnit (0x43a150).
```

| Trigger Source | Trigger ID | Spawned RTTI Class (Vtable) | Puppet Status Cmd (`+0x180`) | Action Skill / Attack IDs | Turn Limit Formula |
|---|---|---|---|---|---|
| Player Skill | `49` (`0x31`) | `CGamePlayerStatusETCArrow` (`0x6d45cc`) | None | `[106 (0x6a)]` | `round(cmd147)` |
| Player Skill | `95` (`0x5f`) | `CGamePlayerStatusETCDoll` (`0x6d4904`) | `228` (`0xe4` Spartan) | `[101 (0x65)]` | `round(cmd147) + round(cmd297)` |
| Player Skill | `96` (`0x60`) | `CGamePlayerStatusETCDoll` (`0x6d4904`) | `229` (`0xe5` Oracles) | `[102 (0x66)]` | `round(cmd147) + round(cmd297)` |
| Player Skill | `97` (`0x61`) | `CGamePlayerStatusETCDoll` (`0x6d4904`) | `230` (`0xe6` Catalina) | `[104 (0x68)]` | `round(cmd147) + round(cmd297)` |
| Player Skill | `98` (`0x62`) | `CGamePlayerStatusETCDoll` (`0x6d4904`) | `231` (`0xe7` Mercidarian) | `[103 (0x67)]` | `round(cmd147) + round(cmd297)` |
| Player Skill | `99` (`0x63`) | `CGamePlayerStatusETCDoll` (`0x6d4904`) | `232` (`0xe8` Perdurabo) | `[105 (0x69)]` | `round(cmd147) + round(cmd297)` |
| Player Skill | `100` (`0x64`) | `CGamePlayerStatusETCDoll` (`0x6d4904`) | `233` (`0xe9` Musiy) | `[235..239 (0xeb..0xef)]` | `round(cmd147) + round(cmd297)` |
| Player Skill | `315` (`0x13b`) | `CGamePlayerStatusETCArrow` (`0x6d45cc`) | None | `[341 (0x155)]` | `round(cmd147)` (lv forced `1`) |
| `CCommand_0427` | `427` (`0x1ab`) | `CGamePlayerStatusETCGenzimaru` (`0x6d4aa0`) | None (max 1 in battle) | `[107 (0x6b)]` | Fixed `3` |
| Turn-Start `cmd 448` | `380` (`0x17c`) | `CGamePlayerStatusETCShadowHearts` (`0x6d4c3c`) | None (refused if owner has ETC) | Basic Attack (`ActionType 1`) | Fixed `3` |
| NPC Attack | `690..735, 1789..1791` | `CGamePlayerStatusOtherETCBase`/`Doll` (`0x6d4f70`) | `0xe4..0xe9` (12 doll cases) | EnemyAttack IDs via `0x485e54` | `round(cmd147)` |
| Enemy Attack | `690..735, 1789..1791` | `CGameEnemyStatusETCBase`/`Doll` (`0x6d448c`) | `0xe4..0xe9` (12 doll cases) | EnemyAttack IDs via `0x485f04` | `round(cmd147)` |

- **Program Evidence:**
```asm
004843b2  mov      eax, dword ptr [eax + 0x2c]
004843b5  call     eax
004843bf  call     0x61e650
004843c9  mov      edx, 0x93
004843d1  call     0x47e340
004843f0  call     0x61e650
004844ff  mov      ecx, dword ptr [ebp + 0x78]
00484502  mov      edx, 0x129
00484507  call     0x47e340
00484526  call     0x61e650
0048452b  add      dword ptr [ebp + 0x74], eax
0048456a  call     0x4fd840
00484573  mov      dword ptr [edi], 0x6d4904
00484579  mov      dword ptr [edi + 0x180], 0xe4
00484588  sub      ecx, 0x60
0048459e  jmp      dword ptr [eax*4 + 0x485d5c]
00485c70  cmp      edx, dword ptr [ecx*4 + 0x6cc7b8]
00485cd6  mov      ecx, dword ptr [ebp + 0x34]
00485cda  call     0x43a150
0048b32c  call     0x4fd840
0048b33b  mov      dword ptr [esi], 0x6d4aa0
00437a35  call     0x4fe2e0
00437a44  call     0x43a150
```

---

### M09.02 ETC Slot Allocation (`CBattleBase::AddETCUnit`), Global Cap (`12`) & Puppet Slot Manager (`cmd 313`)

- **Binary VA(s):** `0x43a150..0x43a315` (`CBattleBase::AddETCUnit`), `0x43c790..0x43c9a0` (`CBattleBase::RegisterPuppet`), `0x43caf0..0x43cb7f` (`CBattleBase::CancelOnePuppet`), `0x43f210..0x43f312` (`CBattleBase::RemoveDollByOwnerAndCmdId`)
- **Calls:** `0x43b330` (collect ETC units), `0x43a010` (`BattleUnit_s::ctor`), `0x490790` (`CRandom::Get`), `0x43e510` (`_SortTime`), `0x43e6d0` (`_GetUnits`), `0x43b3a0` (collect Summons/NPCs), `0x43f210`, `0x43caf0`
- **CalledBy:** `M09.01` (`0x485cda`, `0x48b358`, `0x437a44`), `CGamePlayerStatusBase::AddStatus` (`M00.08` / `0x4f9930` for `vtable+0x74` puppet commands `228..233`)
- **Typed Pseudocode:**
```text
function CBattleBase_AddETCUnit(this: CBattleBase*, etcStatus: CGameStatusBase*):
    // 0x43a150..0x43a315: Hard global battle cap of 12 concurrent ETC/Doll units.
    existingCount: u32 = this.GetETCUnits().size()                  // 0x43b330
    if existingCount >= 12u32: return                               // 0x43a1a0 cmp esi, 0xc; jae exit
    unit = new BattleUnit_s(etcStatus)                              // 0x114 bytes
    if etc = dynamic_cast<CGamePlayerStatusETCBase|OtherETCBase*>(etcStatus):
        ownerUnit = this.FindUnit(etc.ownerStatus)                  // [etc+0x170]
        unit.isPlayerSide = 1u8; unit.isFrontRow = ownerUnit.isFrontRow
    else:                                                           // CGameEnemyStatusETCBase
        unit.isPlayerSide = 0u8; unit.isFrontRow = etcStatus.isFrontRow // [etc+0xa4]
    unit.slotIdx      = existingCount + 2000u32                     // +0x7d0
    unit.unitId       = this.etcCounter + 2000u32                   // [this+0x34] + 0x7d0
    unit.sortTiebreak = this.etcCounter                             // [this+0x34]
    // Initial ATB gauge uses 1 GlobalRng draw in [0..91] -> 0.00f..0.91f (bypasses CBattle::_SetTime):
    unit.gauge = f32(GlobalRng_0x816ce8.Rand(92)) / 100.0f          // 0x43a2a3 push 0x5c; divss 100.0f
    this.units.push_back(unit)
    this.vtable_SortTime(0, 0)                                      // 0x43e510
    this.etcCounter = (this.etcCounter == 0u32) ? 0x3c2u32 : (this.etcCounter - 1u32) // wraps 0 -> 962

function CBattleBase_RegisterPuppet(this: CBattleBase*, ownerStatus, puppetCmd: CCommand*):
    // 0x43c790..0x43c9a0: Invoked by AddStatus when puppetCmd->vtable+0x74() == 1 (cmds 228..233).
    owner = this.FindUnit(ownerStatus)
    cmdId = puppetCmd.GetCommandId()
    // 1. Side-wide uniqueness per puppet type: evict same cmdId from any ally (including owner):
    allies = (owner.unitId in 3000..3999) ? this.GetSummonUnits() : this.GetSideUnits(owner.isPlayerSide)
    for ally in allies:
        if cmdId in ally.puppetIds ([ally+0xd4..0xd8]):
            this.RemoveDollByOwnerAndCmdId(cmdId, ally.status)      // 0x43f210 destroys matching ETC unit
            ally.status.RemoveStatus(cmdId)                         // vtable+0x64
            ally.puppetIds.erase(cmdId)
            break
    // 2. Per-owner puppet cap: 2 with passive 313 (0x139 Double Puppet), else 1 (FIFO eviction of oldest):
    cap: u32 = owner.status.HasPassive(0x139) ? 2u32 : 1u32         // 0x43c920 push 0x139; vtable+0x50
    if owner.puppetIds.size() >= cap:
        this.CancelOnePuppet(owner.status, owner.puppetIds[0])      // 0x43caf0 removes status + calls 0x43f210
    owner.puppetIds.push_back(cmdId)
```
- **Program Evidence:**
```asm
0043a18f  call     0x43b330
0043a194  mov      esi, dword ptr [ebp - 0x20]
0043a19a  sar      esi, 2
0043a1a0  cmp      esi, 0xc
0043a1a3  jae      0x43a2fc
0043a205  lea      ecx, [esi + 0x7d0]
0043a20d  mov      ecx, dword ptr [edi + 0x34]
0043a210  add      ecx, 0x7d0
0043a225  mov      byte ptr [ebx + 0x78], 1
0043a29d  mov      ecx, dword ptr [0x816ce8]
0043a2a3  push     0x5c
0043a2a8  call     0x490790
0043a2b7  divss    xmm0, dword ptr [0x6d9540]    ; float 100
0043a2bf  movss    dword ptr [ebx + 8], xmm0
0043a2f1  mov      eax, 0x3c2
0043c8d9  mov      ecx, dword ptr [ebp - 0x10]
0043c8dd  call     0x43f210
0043c91b  mov      esi, 1
0043c920  push     0x139
0043c92d  call     eax
0043c931  mov      ecx, 2
0043c936  cmovne   esi, ecx
0043c94f  cmp      eax, esi
0043c95b  call     0x43caf0
```

---

### M09.03 Doll Stat Inheritance, Soul Seal (`cmd 314`), Doll Efficacy (`cmd 286` + Enchants `304`/`305`) & `vtable+0xfc` Guards

- **Binary VA(s):** `0x4fd840..0x4fd93e` (`CGamePlayerStatusETCBase::ctor`), `0x4fdfd0..0x4fe135` (`CGamePlayerStatusETCDoll::RecalcStats`, `vtable+0x108`), `0x44b4a6..0x44b5b2` (Physical Doll Bonus), `0x44dd6b..0x44de6d` (Magical Doll Bonus), `0x48d730..0x48d86b` (Heal Doll Bonus), `0x4218a2..0x421923` / `0x4227e5..0x422810` / `0x422f13..0x422f33` / `0x422fff..0x42301f` / `0x42802a..0x42803c` (`vtable+0xfc` `IsETC` combat guards)
- **Calls:** `0x4f3290` (`CGamePlayerStatusBase` copy-ctor), `0x4f7c00` (`RecalcStats`), `0x4f4fc0` (get equipped Sealbook ID), `0x507310` (`MonsterData_0x7389d8` lookup), `0x47e340` (`FindCommand`), `vtable+0xf0` (`M09.07`), `vtable+0x110` (stat cap)
- **CalledBy:** `M09.01`, `CalcPhysicalAttack` (`M00.06` / `0x44a850`), `CalcMagicalAttack` (`M00.06` / `0x44d370`), Heal formula (`0x481838`), `CActionPatternBase::_Task` (`M00.06` / `0x420f10`)
- **Typed Pseudocode:**
```text
function CGamePlayerStatusETCBase_Construct(this, owner, maxTurns, actions, skillLv, skillId):
    // 0x4fd840..0x4fd93e: Full copy of owner's base stats, level, class, equipment, sealbook & enchantList!
    CGamePlayerStatusBase_CopyCtor(this, owner)                     // 0x4f3290
    this.ownerStatus = owner                                        // [this+0x170]
    this.maxTurns = maxTurns; this.spawnSkillId = skillId           // [this+0x174], [this+0x178]
    this.skillList = [(a, skillLv) for a in actions]                // [this+0xc0..0xc8]
    this.curTP = 9999; this.maxTP = 9999                            // 0x4fd922..0x4fd929 (0x270f)

function CGamePlayerStatusETCDoll_RecalcStats(this: CGamePlayerStatusETCDoll*):
    // 0x4fdfd0..0x4fe118 (vtable+0x108 override; runs on Dolls only):
    CGamePlayerStatus_RecalcStats(this)                             // 0x4f7c00
    if cmd314 = this.ownerStatus.GetCommand(0, 0x13a):              // Passive 314 (Soul Seal)
        sealMonsterId: i32 = this.GetEquippedSealbookId()           // 0x4f4fc0 (-1 if unequipped)
        if sealMonsterId != -1:
            mon = MonsterData_0x7389d8.Find(sealMonsterId)          // ATK..AGI at [mon+0x34..0x48]
            for statIdx in 0..5:                                    // jump table 0x4fe11c
                this.stats[statIdx] += trunc0(f32(mon.stats[statIdx]) * cmd314.GetValue())
    this.vtable_0x110_ClampStats()

function DollEfficacyBonus(attacker: CGameStatusBase*, attackerCmds) -> (cmdVal: f32, enchVal: f32):
    // Guarded by RTTI cast to {PlayerETCDoll 0x7086d0, OtherETCDoll 0x708634, EnemyETCDoll 0x708608} ONLY.
    // Does NOT apply to Arrows, Genjimaru, or ShadowHearts!
    cmd286Val: f32 = (c = FindCommand(attackerCmds, 0x11e)) ? c.GetValue() : 0.0f
    e304: u32 = attacker.GetEnchantCount(0x130)                     // Doll skill efficacy UP (0.02f)
    e305: u32 = attacker.GetEnchantCount(0x131)                     // Doll skill efficacy MiniUP (0.01f)
    enchBonus: f32 = min(0.05f, f32(e304) * 0.02f + f32(e305) * 0.01f) // Hard-capped at 0.05f!
    // Applied at 3 sites:
    //   1. Physical Attack (0x44b4fd..0x44b5ad): skillPowerMult += cmd286Val + enchBonus
    //   2. Magical Attack  (0x44dda8..0x44de68): magicPower     += cmd286Val * 500.0f + enchBonus * 500.0f
    //   3. Heal Formula    (0x48d730..0x48d86b): healPower      += cmd286Val * 20.0f  + enchBonus * 20.0f

// Combat vtable+0xfc (IsETC == true for all ETC subclasses, false for Player/Enemy/Summon/NPC):
//   - 0x4218a6: If IsETC or IsNPCOrSummon: non-CGamePlayerStatusETCBase uses enemyAttackId ([Action+0x10]);
//               CGamePlayerStatusETCBase (Player Dolls/Arrows/Genjimaru/ShadowHearts) uses skillId ([Action+0x08]).
//   - 0x4227e9: If attacker IsETC or IsNPCOrSummon: skip target Sugar Coma (cmd 346 / 0x15a) reactive proc.
//   - 0x422f1a & 0x423006: If attacker IsETC: skip HP drain (cmd 10) and TP drain (cmd 11) healing on attacker.
//   - 0x42802c: If actor IsETC: skip post-hit soul/capture processing at 0x42803c.
```
- **Program Evidence:**
```asm
004fd867  call     0x4f3290
004fd8a0  mov      dword ptr [ebx + 0x170], esi
004fd922  mov      dword ptr [ebx + 0x18], 0x270f
004fd929  mov      dword ptr [ebx + 0x14], 0x270f
004fdfd7  call     0x4f7c00
004fdfe2  push     0x13a
004fdfeb  call     dword ptr [eax + 0x48]
004fdffc  call     0x4f4fc0
004fe0f2  mulss    xmm0, xmm1
004fe0f6  cvttss2si eax, xmm0
004fe0fa  add      dword ptr [edi + esi*4 + 0x54], eax
0044b4fd  mov      edx, 0x11e
0044b527  push     0x130
0044b533  call     dword ptr [eax + 0xf0]
0044b55b  mulss    xmm0, dword ptr [0x6d92e0]    ; float 0.02
0044b568  call     dword ptr [eax + 0xf0]
0044b56e  movss    xmm1, dword ptr [0x6d92ec]    ; float 0.05
0044b58e  mulss    xmm0, dword ptr [0x6d92d4]    ; float 0.01
0044b59b  minss    xmm1, xmm0
0044de26  mulss    xmm2, dword ptr [0x6d9640]    ; float 500
0044de5c  mulss    xmm1, dword ptr [0x6d9640]    ; float 500
0048d821  mulss    xmm2, dword ptr [0x6d948c]    ; float 20
0048d859  mulss    xmm1, dword ptr [0x6d948c]    ; float 20
004218a6  mov      eax, dword ptr [eax + 0xfc]
004227e9  mov      eax, dword ptr [eax + 0xfc]
00422f1a  mov      eax, dword ptr [eax + 0xfc]
00423006  mov      eax, dword ptr [eax + 0xfc]
```

---

### M09.04 Doll Turn Selection, Lifetime Countdown & Owner Death / Ailment Cancellation

- **Binary VA(s):** `0x43660d..0x436647` (turn-start state machine skip), `0x4388ea..0x438a65` (ETC action selection), `0x4fd980..0x4fd9db` (`ETCBase::SelectAction`), `0x4fe510..0x4fe5c2` (`ShadowHearts::SelectAction`), `0x4fe860..0x4fe8ab` (`OtherETCDoll::SelectAction`), `0x4fd650..0x4fd69b` (`EnemyETCDoll::SelectAction`), `0x438cea..0x438e40` (lifetime expiry), `0x43f320..0x43f44a` (`RemoveDollAndOwnerStatus`), `0x43d2c0..0x43d3bc` (`DestroyAllETCOfOwner`), `0x43c9b0..0x43cae1` (`CancelAllPuppets`), `0x43fe50..0x43fec1` (`ClearAllETCUnits`)
- **Calls:** `0x4359e0` (`IsETC`: `unitId in 2000..2999`), `0x490790` (`CRandom::Get`), `0x4fd960` / `0x4d4230` (get `maxTurns`), `0x43caf0`, `0x43f210`, `0x43e510` (`_SortTime`)
- **CalledBy:** `CBattleBase::Update` (`M00.02`, `M00.04`, `M00.08`), `CBattleBase::OnUnitDeath` (`0x43a4a0`), `CGamePlayerStatusBase::AddStatus` (`M00.08` / `0x4f9930`), `CCommand_0425` (`0x48b060`), Victory init (`0x4393ee`)
- **Typed Pseudocode:**
```text
function DollTurnAndLifecycle(battle: CBattleBase*, actor: BattleUnit_s*):
    // 1. Turn-Start Skip (0x43660d..0x43662c):
    //    Units with unitId in 2000..2999 skip the entire 25-state TurnPhaseNo machine (M00.03) -> jump to 0x43875a.
    // 2. Action Selection (Outer State 1 at 0x4388ea..0x438a65):
    //    - CGamePlayerStatusETCBase (Dolls/Arrow/Genjimaru): vtable+0x190 = 0x4fd980 sets ActionType = 2 (Skill),
    //      picks skillList[GlobalRng.Rand(skillList.size())] (1 RNG draw; Musiy picks uniformly among 0xeb..0xef).
    //    - CGamePlayerStatusETCShadowHearts: vtable+0x190 = 0x4fe510 sets ActionType = 1 (Basic Attack) on
    //      aliveEnemies[GlobalRng.Rand(aliveEnemies.size())] (1 RNG draw).
    //    - CGamePlayerStatusOtherETCDoll / EnemyETCDoll: ActionType = 8 (EnemyAttack), picks uniformly via Rand(n).
    // 3. Post-Action Lifetime Countdown (Outer State 3 at 0x438cea..0x438e40):
    //    actor.totalActionCount ([actor+0xb8]) already incremented at 0x438cbd.
    if actor.IsETC():                                               // 0x4359e0: (unitId - 2000) <= 999
        maxTurns: u32 = GetETCMaxTurns(actor.status)                // 0x4fd960 / 0x4d4230
        if maxTurns == 0u32: maxTurns = 0xffffffffu32               // 0 means infinite turns
        if actor.totalActionCount < maxTurns:
            // Survives -> normal _SetTime (0x43e5c0)
        else:
            SetETCExpiredFlag(actor.status)                         // 0x4fd970 / 0x4fe850 / 0x4fd640
            if !battle.RemoveDollAndOwnerStatus(actor.status):      // 0x43f320 -> calls 0x43caf0(owner, puppetCmd)
                battle.EraseAndFreeUnit(actor)                      // Non-doll ETC (Arrow/Genjimaru/ShadowHearts)
            battle.vtable_SortTime(1, 1)
    // 4. Owner Death, Ailment & Dispel Cancellation:
    //    - Owner dies (0x43a4a0): calls DestroyAllETCOfOwner (0x43d2c0 at 0x43a513) AND CancelAllPuppets (0x43c9b0 at 0x43a533).
    //    - AddStatus (0x4f9930) on owner:
    //        * Freeze (114 / 0x72), Sleep (116 / 0x74), Stun (118 / 0x76), Special Petrification (121 / 0x79):
    //            calls CancelAllPuppets (0x43c9b0) -> destroys Dolls (228..233), preserves Arrows/Genjimaru/ShadowHearts!
    //        * Paralysis (115 / 0x73), Poison (113), Silence (117), Petrification (120), Slow (122):
    //            does NOT cancel Puppets or ETC units!
    //        * Shadow Sew (123 / 0x7b): calls CancelAllPuppets (0x43c9b0 at 0x4fa499) AND DestroyAllETCOfOwner (0x43d2c0 at 0x4fa4d7)!
    //    - Command 425 (Cancel Chant/Song/Dance/Doll at 0x48b0d6): calls CancelAllPuppets (0x43c9b0).
    //    - Battle Victory (0x4393ee): calls ClearAllETCUnits (0x43fe50), erasing every unitId in 2000..2999.
```
- **Program Evidence:**
```asm
00436610  cmp      eax, 0x7d0
00436617  cmp      eax, 0xbb8
00436626  jne      0x43875a
004388ec  call     0x4359e0
00438949  call     dword ptr [edx + 0x190]
004fd988  mov      ecx, dword ptr [0x816ce8]
004fd9b2  call     0x490790
004fe54d  mov      dword ptr [ecx + 4], 1
004fe586  call     0x490790
00438cec  call     0x4359e0
00438d18  call     0x4fd960
00438d65  or       ecx, 0xffffffff
00438d68  test     eax, eax
00438d6a  cmove    eax, ecx
00438d6d  cmp      dword ptr [esi + 0xb8], eax
00438d73  jb       0x439278
00438dee  call     0x43f320
0043a513  call     0x43d2c0
0043a533  call     0x43c9b0
004f9e6f  cmp      eax, 0x72
004f9f8e  cmp      eax, 0x74
004fa185  cmp      eax, 0x76
004fa430  cmp      eax, 0x7b
004fa499  call     0x43c9b0
004fa4d7  call     0x43d2c0
0043fe65  mov      ecx, dword ptr [edi + 4]
0043fe68  sub      ecx, 0x7d0
0043fe6e  cmp      ecx, 0x3e7
```

---

## 2. Summons & Guest NPCs (`unitId 3000..3999`)

### M09.05 Summon & Guest NPC Slot Allocation, Initial Gauge (`flag33`), Targetability & Damage Dispatch

- **Binary VA(s):** `0x449750..0x4498ff` (`CBattle::_InitSummonAndNPC`), `0x449155..0x4491cf` (`CBattle::_Initialize` initial gauge & `flag33`), `0x43e6d0..0x43e7bf` (`CBattleBase::_GetUnits` targetability filter), `0x438a66..0x438b68` (Summon/NPC AI turn dispatch), `0x449a45..0x449a57` / `0x449c71` / `0x449d79` (`CBattle::_SetTime` enemy-attack path), `0x44a9fc` / `0x44b483` (`CalcPhysicalAttack` enemy-attack path), `0x4731fb` / `0x473220` (`CGame` slot ownership)
- **Calls:** `0x43a010` (`BattleUnit_s::ctor`), `0x430aa0` (`CBattleAI::ctor`), `0x490790` (`CRandom::Get`), `0x4499d0` (`CBattle::_SetTime`), `0x430f00` (`CBattleAI::SelectAction`), `0x5576a0` (`EnemyAttackData` lookup)
- **CalledBy:** `CBattle::_Initialize` (`M00.01`), `CBattleBase::Update` (`M00.02`, `M00.04`), `CalcPhysicalAttack` (`M00.06`), `CBattleBase::_GetAlivePlayerCount` (`0x43afc0`)
- **Typed Pseudocode:**
```text
function CBattle_InitSummonAndNPC(this: CBattle*):
    // 0x449750..0x4498ff: Allocates up to 2 companion units in unitId range 3000..3999 (0xbb8..0xf9f).
    // Slot ownership verified at CGame::ctor (0x4731fb -> Summon, 0x473220 -> NPC):
    //   [GameManager+0x141c] = CGamePlayerStatusSummon* (vt 0x6d5430, vtable+0x100 = true)
    //   [GameManager+0x1424] = CGamePlayerStatusNPC*    (vt 0x6d5108, vtable+0x100 = true)
    summon = GameManager.summonSlot                                 // [0x71fc24]+0x141c
    if summon.summonId ([summon+0x170]) != -1:
        u = new BattleUnit_s(summon)
        u.slotIdx = summon.GetId() + 3000u32; u.unitId = 3000u32    // 0xbb8
        u.sortTiebreak = 930u32                                     // 0x3a2
        u.isPlayerSide = 1u8; u.isFrontRow = 1u8                    // word [u+0x78] = 0x0101
        u.ai = new CBattleAI(this.battleInfo, this, u.status)       // 0x430aa0
        this.units.push_back(u)
    npc = GameManager.npcSlot                                       // [0x71fc24]+0x1424
    if npc.npcId ([npc+0x170]) != -1:
        u = new BattleUnit_s(npc)
        u.slotIdx = npc.GetId() + 3000u32; u.unitId = 3001u32       // 0xbb9
        u.sortTiebreak = 929u32                                     // 0x3a1
        u.isPlayerSide = 1u8; u.isFrontRow = 1u8
        u.ai = new CBattleAI(this.battleInfo, this, u.status)       // 0x430aa0
        this.units.push_back(u)

function CBattle_InitUnitGauges(this: CBattle*):                    // 0x449155..0x4491cf
    for u in this.units:
        if u.unitId in 3000..3999:
            if this.flag33 ([this+0x33]) != 0u8:
                this.vtable_SetTime(u, 0)                           // Normal AGI-based gauge
            else:
                // 1 GlobalRng draw in [0..499] -> +1 -> /1000.0f => 0.001f .. 0.500f!
                u.gauge = f32(GlobalRng_0x816ce8.Rand(500) + 1) / 1000.0f
        else:
            this.vtable_SetTime(u, 0)

// Targetability, Party-Wipe & Combat Rules for unitId 3000..3999:
//   - CBattleBase::_GetUnits (0x43e6d0..0x43e7bf) rejects unitId in 2000..2999, 3000..3999, and >= 4000.
//     Therefore Summons & Guest NPCs are UNTARGETABLE by all attacks/spells/heals and are EXCLUDED from
//     GetAlivePlayerCount (0x43afc0): if all player party members die, battle ends in Defeat even with active Summon/NPC.
//   - Outer State 1 (0x438a66..0x438b68): executes chant completion (ActionType 9 -> 8) or calls u.ai->0x430f00();
//     if AI returns false, falls back to EnemyAttack ID 0 (basic attack, ActionType = 8).
//   - CBattle::_SetTime (0x449a48, 0x449c71, 0x449d79) & CalcPhysicalAttack (0x44a9fc, 0x44b483):
//     Summons/NPCs take the EnemyAttack data path ([EnemyAttack+0x3c] skill power, enemy chant delay) despite isPlayerSide == 1.
//   - No per-battle action-count expiry (0x438cea checks IsETC 2000..2999 only).
```
- **Program Evidence:**
```asm
00449771  mov      ebx, dword ptr [eax + 0x141c]
0044977b  cmp      dword ptr [ebx + 0x170], -1
004497ce  mov      dword ptr [esi + 4], 0xbb8
004497d5  mov      dword ptr [esi + 0xc], 0x3a2
004497df  mov      word ptr [esi + 0x78], 0x101
00449822  call     0x430aa0
00449839  mov      ebx, dword ptr [eax + 0x1424]
00449892  mov      dword ptr [esi + 4], 0xbb9
00449899  mov      dword ptr [esi + 0xc], 0x3a1
004498a3  mov      word ptr [esi + 0x78], 0x101
0044916a  sub      eax, 0xbb8
0044916f  cmp      eax, 0x3e7
00449182  cmp      byte ptr [ebx + 0x33], 0
0044919a  push     0x1f4
0044919f  call     0x490790
004491a4  inc      eax
004491b2  divss    xmm0, dword ptr [0x6d96b0]    ; float 1000
004491ba  movss    dword ptr [eax + 8], xmm0
0043e72a  mov      eax, dword ptr [esi + 4]
0043e72d  cmp      eax, 0x7d0
0043e734  cmp      eax, 0xbb8
0043e73b  cmp      eax, 0xbb8
0043e742  cmp      eax, 0xfa0
0043e749  cmp      eax, 0xfa0
0044a9fc  sub      eax, 0xbb8
0044b483  sub      eax, 0xbb8
00438a68  call     0x435a00
00438a9d  call     0x430f00
```

---

### M09.06 Summon & Guest NPC Stat Scaling, Party Sealbook Inheritance, Buddy Enchants (`295`/`297`), Samba (`199`) Tick & Expiry

- **Binary VA(s):** `0x4ffc90..0x500165` (`CGamePlayerStatusSummon::vtable+0xf8`), `0x4fec90..0x4fee45` (`CGamePlayerStatusNPC::vtable+0xf8`), `0x4ff630..0x4ff678` (`CGamePlayerStatusNPC::vtable+0x110`), `0x4ff530..0x4ff62e` (`vtable+0x178` Party-Slot-0 Sealbook inheritance), `0x436322..0x4365fb` (Samba/Salsa `199` turn-start tick), `0x446554..0x446569` / `0x447150..0x4471ca` / `0x4446b4..0x4446c5` (Guest NPC battle-count expiry), `0x43abfa..0x43ac42` (Summon 100-kill trophy counter)
- **Calls:** `0x573250` (base summon group lookup), `0x4ff7b0` (`CGamePlayerStatusTemporary::ctor`), `0x4e4f50` (`M09.07` `PartyHasEnchant`), `0x4fc620` (stat clamp), `0x47e500` (`CCommand::Execute`), `0x4fef00` (`CGamePlayerStatusNPC::Clear`)
- **CalledBy:** Battle init/level-up recalc (`0x4441e9`, `0x4fe9a0`, `0x4ff9d0`), `CBattleBase::Update` Outer State 0 (`M00.02` / `0x436322`), `CBattleResult::_Initialize` (`M00.09` / `0x446554`) & `CBattleResult::Update` (`0x4446b4`)
- **Typed Pseudocode:**
```text
function CGamePlayerStatusSummon_RecalcFromData(this: CGamePlayerStatusSummon*):
    // 0x4ffc90..0x500165 (vtable+0xf8):
    if this.summonId == -1: return
    party = GameManager.GetPartyMembers()
    avgLv: u32 = (party.size() > 0) ? (sum(m.GetLevel() for m in party) / party.size()) : 0u32
    // 1. Tier promotion inside SummonData_0x738a70 (loaded from backups/Summon/Summon.pck):
    groupId = SummonData[this.summonId].groupId                     // [+0x2c]
    idx = FindFirstSummonInGroup(groupId)                           // 0x573250
    while SummonData.Contains(idx) and SummonData[idx].minLv <= avgLv and SummonData[idx].groupId == groupId:
        this.summonId = idx; idx += 1
    // 2. Seed ATK..AGI from MonsterData_0x7389d8[groupId] (+0x34..+0x48), then take party-max scaled stats:
    for k in 0..5: this.stats[k] = MonsterData[groupId].stats[k]
    for m in party:
        tmp = new CGamePlayerStatusTemporary(m)                     // 0x4ff7b0 (strips combat buffs)
        for k in 0..5:
            cand: i32 = trunc0(f32(tmp.GetStat(k)) * SummonData[this.summonId].statMult[k]) // [+0x3c..+0x50]
            if cand > this.stats[k]: this.stats[k] = cand
        delete tmp
    this.baseStats[0..5] = this.stats[0..5]
    this.vtable_0x108_Recalc(); this.vtable_0x58_InitPassives(); this.vtable_0x178_LoadLeaderSealbook()

function CGamePlayerStatusNPC_RecalcFromData(this: CGamePlayerStatusNPC*):
    // 0x4fec90..0x4fee45 (vtable+0xf8) + 0x4ff630..0x4ff678 (vtable+0x110):
    if this.npcId == -1: return
    bonusFlat: i32 = PartyHasEnchant(0x129) ? 30 : 0                // Enchant 297 (+30 to ATK..AGI)
    rec = NPCData_0x738a04.Find(this.npcId)                         // loaded from backups/NPC/NPC.pck
    this.level = rec.level ([rec+0x30])
    for k in 0..5: this.stats[k] = this.baseStats[k] = rec.stats[k] + bonusFlat
    // Inside CGamePlayerStatusNPC::vtable+0x110 (0x4ff630; Guest NPC ONLY, NOT Summon):
    if PartyHasEnchant(0x127):                                      // Enchant 295 (+10% to ATK..AGI)
        for k in 0..5:
            this.stats[k] = this.stats[k] - trunc0(f32(this.stats[k]) * -0.10f)
    ClampStats_0x4fc620(this)

function Companion_LoadLeaderSealbook(this):                        // 0x4ff530 (vtable+0x178 on BOTH Summon & NPC)
    // Reads Party Slot 0's equipped Sealbook ([GameManager+0x13f0]->slot[5] at +0xbc) and appends all of its
    // SealScrollData enchants into this.enchantList ([this+0x12c..0x134])!

function CBattleBase_SummonNPCSambaTick(this: CBattleBase*, actor: BattleUnit_s*):
    // 0x436322..0x4365fb (Outer State 0 for unitId in 3000..3999, before skipping 25-state TurnPhaseNo):
    // Runs 2-step TurnPhaseNo (0 -> 1 -> 2). In step 0, if cmd 199 (0xc7 Salsa) is in actor.dances ([actor+0xc8]):
    // Collects all enemy units via _GetUnits(isPlayer=0); if any enemy has cmd 199, queues HP damage =
    // trunc0(f32(enemy.MaxHP) * cmd199.GetValue()) for every enemy and executes via CCommand::Execute (0x47e500, mode=6).

function GuestNPC_BattleCountExpiry():
    // On every battle victory (CBattleResult::_Initialize at 0x446554..0x446569):
    //   if GameManager.npcSlot.npcId != -1: GameManager.npcSlot.battleCount ([+0x174]) += 1
    // On result screen (0x447150..0x4471ca & 0x4446b4..0x4446c5):
    //   if npc.battleCount >= NPCData[npc.npcId].maxBattles ([+0xc8]):
    //       npc.Clear() (0x4fef00 -> sets npcId = -1; Guest NPC leaves party).
    // Summon ([GameManager+0x141c]) has NO battle-count expiry (stays until unequipped; kills increment [GameManager+0x1420]).
```
- **Program Evidence:**
```asm
004ffd45  div      ecx
004ffdc1  cmp      ecx, dword ptr [eax + 0x30]
004ffe4f  mov      eax, dword ptr [eax + 0x34]
004fff1c  call     0x4ff7b0
004fff5f  mulss    xmm0, dword ptr [ebp - 0x24]
004fff64  cvttss2si eax, xmm0
004fff68  cmp      dword ptr [edi + 0x54], eax
004fff6d  mov      dword ptr [edi + 0x54], eax
004fecc0  mov      ecx, 0x129
004fecc5  call     0x4e4f50
004fecce  mov      dword ptr [ebp + 0xe4], 0x1e
004ff633  mov      ecx, 0x127
004ff638  call     0x4e4f50
004ff641  movss    xmm1, dword ptr [0x6d9780]    ; float -0.1
004ff65e  mulss    xmm0, xmm1
004ff662  cvttss2si eax, xmm0
004ff666  sub      ecx, eax
004ff538  mov      eax, dword ptr [eax + 0x13f0]
004ff541  mov      eax, dword ptr [eax + 0xbc]
004ff5b9  mov      ecx, dword ptr [eax + ebp]
00436325  cmp      ecx, 0xbb8
004363d0  cmp      dword ptr [edx], 0xc7
00436530  fmul     dword ptr [ebp - 0x10]
00436540  cvttss2si eax, dword ptr [ebp - 0x10]
0043657e  call     0x47e500
00446554  mov      eax, dword ptr [eax + 0x1424]
00446563  inc      dword ptr [eax + 0x174]
004471c4  cmp      esi, dword ptr [eax + 0xc8]
004446c0  call     0x4fef00
```

---

## 3. Enchantment Aggregation & Stacking Engine (`vtable+0xf0` & `_SetupEnchant`)

### M09.07 Equipment Slot Scan, Dual-Wield Offhand `flags & 0x80` Filter, Sealbook Expansion & Deduplication

- **Binary VA(s):** `0x4f62c0..0x4f64a6` (`Game::CGamePlayerStatusBase::_SetupEnchant`, `vtable+0x178`), `0x4f64b0..0x4f652d` (`_AddEnchant`, `vtable+0x17c`), `0x4f5470..0x4f54cd` (`CGamePlayerStatusBase::GetEnchantCount`, `vtable+0xf0`), `0x4d4dd0..0x4d4dd4` (`CGameEnemyStatus::GetEnchantCount`, `vtable+0xf0`), `0x4e4f50..0x4e4fb6` (`PartyHasEnchant`)
- **Calls:** `0x507310` (`EquipData_0x7389e0`, `EnchantData_0x7389d0`, `SealScrollData_0x738a14`), `0x61edf4` (`__RTDynamicCast`), `vtable+0x108` (`RecalcStats`), `vtable+0xf0`
- **CalledBy:** Equipment change / battle init / status rebuild, `CGamePlayerStatusBase` copy-ctor (`0x4f3290` copies `enchantList` directly to Dolls), `M09.06` (`0x4ff530` populates Summon/NPC `enchantList` from Party Slot 0 Sealbook), all 152+ combat & field callers
- **Typed Pseudocode:**
```text
function CGamePlayerStatusBase_SetupEnchant(this: CGamePlayerStatusBase*):
    // 0x4f62c0..0x4f64a6: Rebuilds this.enchantList ([this+0x12c..0x134]) across all 6 equipment slots.
    // There is NO broken/durability/cursed filter: any non-null item in slots 0..5 is scanned.
    // Status-granted enchants do NOT exist: enchantList is populated exclusively from equipped gear & Sealbooks.
    this.enchantList.clear()
    for slot in 0..5:                                               // 0=RHand, 1=LHand, 2=Head, 3=Body, 4=Acc, 5=Sealbook
        item = this.equipSlots[slot]                                // [this + 0xa8 + slot*4]
        if item == null: continue
        if item.vtable_0x18_IsEquipment():                          // CGameArticleEquipment (RTTI 0x708454)
            for enchId in item.enchants ([item+0x84..0x88]):
                // DUAL-WIELD OFFHAND RULE (0x4f6334..0x4f6387):
                // If Left Hand (slot == 1) holds a Weapon (EquipData[id].equipType [+0x38] == 0):
                //   ONLY enchants with EnchantData[enchId].flags bit 7 (0x80) set are aggregated!
                //   Shields (equipType != 0) in slot 1 bypass this filter and aggregate ALL enchants.
                if slot == 1 and EquipData_0x7389e0[item.id].equipType == 0:
                    if ((EnchantData_0x7389d0[enchId].flags_0x38 >> 7) & 1) == 0:
                        continue                                    // Offhand weapon enchant suppressed!
                this.vtable_0x17c_AddEnchant(enchId)                // 0x4f64b0
        else if item.vtable_0x1c_IsSealScroll():                    // CGameArticleSealScroll (RTTI 0x708768)
            scroll = SealScrollData_0x738a14[item.id]
            for j in 0 .. scroll.enchantCount ([+0x34]) - 1:
                this.vtable_0x17c_AddEnchant(scroll.enchants[j])    // [+0x38 + j*4]
    this.vtable_0x108_RecalcStats()

function CGamePlayerStatusBase_AddEnchant(this, enchId: u32):       // 0x4f64b0..0x4f652d
    // Deduplicates non-stacking enchants (bit 0 of EnchantData[enchId].flags_0x38 == 0) at insertion time:
    if enchId in this.enchantList:
        if (EnchantData_0x7389d0[enchId].flags_0x38 & 1u8) == 0u8:
            return                                                  // Capped at 1 occurrence
    this.enchantList.push_back(enchId)

function CGamePlayerStatusBase_GetEnchantCount(this, enchId: u32) -> u32: // 0x4f5470 (vtable+0xf0)
    stacks: bool = ((EnchantData_0x7389d0[enchId].flags_0x38 & 1u8) != 0u8)
    count: u32 = 0u32
    for id in this.enchantList:
        if id == enchId:
            count += 1u32
            if !stacks: break                                       // Non-stacking enchants always return 0 or 1
    return count

function CGameEnemyStatus_GetEnchantCount(this, enchId: u32) -> u32: // 0x4d4dd0 (vtable+0xf0)
    return 0u32                                                     // Enemies & EnemyETCDolls always return 0

function PartyHasEnchant(enchId: u32) -> bool:                      // 0x4e4f50
    for i in 0 .. GameManager.GetPartyCount() - 1:
        if GameManager.GetPartyMember(i).GetEnchantCount(enchId) != 0u32:
            return true                                             // Party-wide boolean OR (no alive check)
    return false
```
- **Program Evidence:**
```asm
004f62e0  mov      esi, dword ptr [ebp + ebx*4 + 0xa8]
004f62f3  mov      eax, dword ptr [eax + 0x18]
004f6334  cmp      dword ptr [esp + 0x10], 1
004f635c  cmp      dword ptr [eax + 0x38], 0
004f637d  mov      eax, dword ptr [eax + 0x38]
004f6380  shr      eax, 7
004f6383  test     al, 1
004f638d  call     dword ptr [eax + 0x17c]
004f63b2  mov      eax, dword ptr [eax + 0x1c]
004f642f  call     dword ptr [edx + 0x17c]
004f6472  cmp      ebx, 6
004f6487  jmp      dword ptr [eax + 0x108]
004f64d0  cmp      dword ptr [eax], esi
004f64fc  mov      al, byte ptr [eax + 0x38]
004f64ff  and      al, 1
004f6501  je       0x4f6526
004f5487  mov      ecx, dword ptr [0x7389d0]
004f5499  mov      bl, byte ptr [eax + 0x38]
004f54a2  and      bl, 1
004f54b4  cmp      edi, dword ptr [eax]
004f54b8  inc      edx
004f54b9  test     bl, bl
004f54bb  je       0x4f54c5
004d4dd0  xor      eax, eax
004d4dd2  ret      4
004e4f84  call     dword ptr [edx + 0xf0]
004e4fb2  setb     al
```

---

## 4. Detailed Non-Combat-Formula Enchantment Specifications (`M09.08` – `M09.14`)

### M09.08 Stat, Row-Conditional & Resistance Enchants (`_CalculateParameterEnchant`, 94 IDs)

- **Binary VA(s):** `0x4f8270..0x4f8fdf` (`CGamePlayerStatusBase::vtable+0x180`, `_CalculateParameterEnchant`), `0x4f7c42` (call site in `RecalcStats`)
- **Calls:** `0x507310` (`EnchantData_0x7389d0`), `vtable+0x30` (base stat before gear/buffs), `vtable+0x34` (current stat with gear), `GameManager->vtable+0x164` (`IsFrontRow`), `GameManager->vtable+0x16c` (`IsBackRow`)
- **CalledBy:** `CGamePlayerStatus::RecalcStats` (`0x4f7c00` at `0x4f7c42`)
- **Typed Pseudocode:**
```text
function CGamePlayerStatusBase_CalculateParameterEnchant(this, baseMaxHP: i32, baseMaxTP: i32):
    // 0x4f8270..0x4f8fdf: Directly iterates this.enchantList ([this+0x12c..0x130]) WITHOUT calling vtable+0xf0.
    // Maintains local `seen` vector ([ebp-0x34]) to enforce non-stacking (flags_0x38 & 1 == 0) per pass.
    hpDelta: i32 = 0; tpDelta: i32 = 0
    statDelta: i32[6] = [0, 0, 0, 0, 0, 0]                          // ATK, DEF, INT, RES, DEX, AGI ([ebp-0x6c..-0x58])
    resDelta:  i32[8] = [0, 0, 0, 0, 0, 0, 0, 0]                    // Slash, Stab, Bash, Fire, Water, Wind, Earth, Lightning
    for enchId in this.enchantList:
        if (EnchantData[enchId].flags_0x38 & 1u8) == 0 and enchId in seen: continue
        seen.push_back(enchId)
        switch enchId:
            // 1. MaxHP (0..2) & MaxTP (3..5) — integer trunc0 division on baseMaxHP/baseMaxTP:
            case 0, 3: delta += max(4, base / 10)                   // +10%, min +4
            case 1, 4: delta += max(2, base / 20)                   // +5%,  min +2
            case 2, 5: delta -= max(0, base / 10)                   // -10%, min 0
            // 2. Individual Stats ATK..AGI (6..23) — integer trunc0 division on BASE stat (vtable+0x30):
            case 6, 9, 12, 15, 18, 21: statDelta[k] += max(4, this.GetBaseStat(k) / 10)
            case 7, 10, 13, 16, 19, 22: statDelta[k] += max(2, this.GetBaseStat(k) / 20)
            case 8, 11, 14, 17, 20, 23: statDelta[k] -= max(0, this.GetBaseStat(k) / 10)
            // 3. Flat All-Stats (24..28):
            case 24: all 6 stats += 1;  case 25: += 3;  case 26: += 6;  case 27: += 9;  case 28: += 12
            // 4. Row-Conditional Stats (222..225, 281) — uses CURRENT stat (vtable+0x34, includes gear!):
            case 222 (0xde): if IsFrontRow(this): statDelta[ATK] += trunc0(f32(GetStat(ATK)) * 0.08f)
            case 223 (0xdf): if IsFrontRow(this): statDelta[ATK] += GetStat(ATK) / 25; statDelta[DEF] += GetStat(DEF) / 25
            case 224 (0xe0): if IsBackRow(this):  statDelta[INT] += trunc0(f32(GetStat(INT)) * 0.08f)
            case 225 (0xe1): if IsBackRow(this):  statDelta[INT] += GetStat(INT) / 25; statDelta[RES] += GetStat(RES) / 25
            case 281 (0x119): if IsBackRow(this): statDelta[DEX] += GetStat(DEX) / 50; statDelta[AGI] += GetStat(AGI) / 50
            // 5. Elemental & Physical Resistances (88..119, 310..356):
            //    Accumulated into resDelta[0..7] (see M09.15 Family 3 for all 60 exact deltas).
    // Commit with exact clamps (0x4f842c..0x4f84ae):
    this.maxHP += clamp(hpDelta, -(baseMaxHP / 2), +(baseMaxHP / 2)) // ±50% cap!
    this.maxTP += clamp(tpDelta, -(baseMaxTP / 2), +(baseMaxTP / 2)) // ±50% cap!
    for k in 0..5: this.stats[k] += statDelta[k]                    // NO clamp here (clamped later in vtable+0x110)
    for r in 0..7: this.resists[r] += clamp(resDelta[r], -100, +100)// Each enchant resistance delta clamped [-100, +100]
```
- **Program Evidence:**
```asm
004f8311  test     byte ptr [eax + 0x38], 1
004f8354  test     esi, esi
004f835b  mov      eax, 0x66666667
004f8368  sar      edx, 2
004f8372  cmp      eax, 4
004f8375  cmovl    eax, ecx
004f8382  cmp      esi, 1
004f8397  sar      edx, 3
004f83a1  cmp      eax, 2
004f83ae  cmp      esi, 2
004f83c3  sar      edx, 2
004f83cd  cmovs    eax, ecx
004f8437  sar      eax, 1
004f8439  cmp      esi, eax
004f8440  cmp      esi, eax
004f844a  add      dword ptr [ebx + 0x10], eax
004f8456  sar      eax, 1
004f8467  add      dword ptr [ebx + 0x18], eax
004f8497  cmp      eax, 0x64
004f849d  cmp      eax, -0x64
004f8514  cmp      esi, 6
004f8520  call     dword ptr [eax + 0x30]
004f88bc  cmp      esi, 0x18
004f88dd  add      dword ptr [ebp - 0x6c], 3
004f8b9c  cmp      esi, 0xde
004f8bde  mulss    xmm0, dword ptr [0x6d9300]    ; float 0.08
004f8bf2  cmp      esi, 0xdf
004f8c31  mov      eax, 0x51eb851f
004f8d36  cmp      esi, 0x119
004f8dad  cmp      esi, 0x136
```

---

### M09.09 On-Hit Normal Attack Ailment & Drain Enchants (`153..165, 197`) & Weapon Element Imbue (`78..82`)

- **Binary VA(s):** `0x42124c..0x4216e9` (Normal Attack enchant command injection in `CActionPatternBase::_Task`), `0x4161cf..0x41621d` (`IsAttributeFire`), `0x4164df..0x41652d` (`IsAttributeWater`), `0x4167ef..0x41683d` (`IsAttributeWind`), `0x416aff..0x416b4d` (`IsAttributeEarth`), `0x416e0f..0x416e5d` (`IsAttributeLightning`)
- **Calls:** `vtable+0xf0` (`M09.07`), `0x47e340` (`FindCommand`), `0x47b220` (`CCommand` factory), `0x5587c0` (`MonsterData` lookup for Undead species check), `vtable+0x50` (check exclusive weapon-element statuses `325..329`)
- **CalledBy:** `CActionPatternBase::_Task` (`M00.06` / `0x420f10`), `CalcPhysicalAttack` (`M00.06`)
- **Typed Pseudocode:**
```text
function InjectNormalAttackEnchants(attacker, target, action, hitCmdList):
    // 0x42124c..0x4216e9: Runs ONLY when action.actionType == 1 (Normal Attack)!
    // Each enchant checks (attacker.GetEnchantCount(eid) != 0) AND (!FindCommand(hitCmdList, cmdId)).
    // Order-of-evaluation precedence creates exact override rules when two tiers are both equipped:
    //   - Ench 160 (0.07f Instakill) is checked BEFORE Ench 197 (0.75f Instakill) -> 160 BLOCKS 197!
    //   - Ench 161 (0.50f HP Drain)  is checked BEFORE Ench 162 (0.15f HP Drain)  -> 161 overrides 162.
    //   - Ench 163 (0.20f TP Drain)  is checked BEFORE Ench 164 (0.05f TP Drain)  -> 163 overrides 164.
    const AILMENT_ENCHANTS = [
        (153/0x99, cmd 113/0x71 Poison, 0.18f),       (154/0x9a, cmd 116/0x74 Sleep, 0.15f),
        (155/0x9b, cmd 117/0x75 Silence, 0.18f),      (156/0x9c, cmd 114/0x72 Freeze, 0.18f),
        (157/0x9d, cmd 115/0x73 Paralysis, 0.15f),    (158/0x9e, cmd 118/0x76 Stun, 0.12f),
        (159/0x9f, cmd 120/0x78 Petrification, 0.10f),(160/0xa0, cmd 119/0x77 Instakill, 0.07f),
        (197/0xc5, cmd 119/0x77 Instakill, 0.75f),    (165/0xa5, cmd 122/0x7a Slow, 0.12f)
    ]
    for (eid, cmdId, prob) in AILMENT_ENCHANTS:
        if attacker.GetEnchantCount(eid) != 0 and !FindCommand(hitCmdList, cmdId):
            hitCmdList.push_back(CreateCommand(cmdId, prob))        // 0x47b220
    // Drain enchants (161..164) are BLOCKED against Undead targets (MonsterData[targetId].species [+0x10] == 5):
    canDrain: bool = (target.monsterId == -1) or (MonsterData[target.monsterId].species != 5)
    if canDrain:
        // (161/0xa1, cmd 75/0x4b HP Drain, 0.50f) -> (162/0xa2, cmd 75/0x4b, 0.15f)
        // (163/0xa3, cmd 76/0x4c TP Drain, 0.20f) -> (164/0xa4, cmd 76/0x4c, 0.05f)

function IsNormalAttackElement(attacker, elemIdx in 0..4) -> bool:
    // 0x4161cf..0x416e5d (Fire=0, Water=1, Wind=2, Earth=3, Lightning=4):
    // Weapon-element status buffs (325..329 / 0x145..0x149) take strict precedence:
    //   if any OTHER weapon-element buff in 325..329 is active -> return false;
    //   if matching weapon-element buff (325 + elemIdx) is active -> return true;
    //   else -> return (attacker.GetEnchantCount(78 + elemIdx) != 0) // Enchants 78..82 (0x4e..0x52)
```
- **Program Evidence:**
```asm
0042124f  cmp      dword ptr [ecx + 4], eax
0042125a  push     0x99
00421261  call     dword ptr [eax + 0xf0]
0042127c  movss    xmm2, dword ptr [0x6d9320]    ; float 0.18
00421284  lea      edx, [eax + 0x71]
0042148f  push     0xa0
004214b3  movss    xmm2, dword ptr [0x6d92fc]    ; float 0.07
004214e0  push     0xc5
00421504  movss    xmm2, dword ptr [0x6d9368]    ; float 0.75
00421538  call     0x5587c0
0042153d  cmp      dword ptr [eax + 0x10], 5
00421541  setne    bl
00421547  push     0xa1
0042156f  movss    xmm2, dword ptr [0x6d9348]    ; float 0.5
0042159c  push     0xa2
004215c4  movss    xmm2, dword ptr [0x6d931c]    ; float 0.15
004215f1  push     0xa3
00421619  movss    xmm2, dword ptr [0x6d9324]    ; float 0.2
00421646  push     0xa4
0042166e  movss    xmm2, dword ptr [0x6d92ec]    ; float 0.05
0042169b  push     0xa5
004216bf  movss    xmm2, dword ptr [0x6d9310]    ; float 0.12
004161d1  push     0x148
004161e3  push     0x149
004161f5  push     0x145
00416209  push     0x4e
0041620d  call     dword ptr [eax + 0xf0]
00416215  setne    bl
```

---

### M09.10 Damage Nullification (`120..128`), Ailment Nullification (`129..139`), Trap Evasion (`269`) & Dissipation (`265`)

- **Binary VA(s):** `0x421b01..0x421c60` (Damage nullification `120..128` in `CActionPatternBase::_Task`), `0x481f0a..0x4838d0` (11 ailment `CCommand::AddTask` handlers checking `129..139` & `269`), `0x48d1e0..0x48d241` (`265` out-of-battle ailment dissipation)
- **Calls:** `vtable+0xf0` (`M09.07`), `0x415410`/`0x415710`/`0x415a10` (Slash/Stab/Bash checks), `0x415f50`..`0x416b90` (Fire..Lightning checks), `0x490790` (`CRandom::Get`)
- **CalledBy:** `CActionPatternBase::_Task` (`M00.06`), `CCommand_0113..0123::AddTask`, Dungeon step tick (`0x48d180`)
- **Typed Pseudocode:**
```text
function CheckDamageNullificationEnchants(action, target, hitResult) -> bool:
    // 0x421b01..0x421c60: Evaluated BEFORE damage calculation; any match sets resultCode = 4 (Nullified) & returns true.
    if target.GetEnchantCount(123/0x7b) != 0 and (IsSlash(action) or IsStab(action) or IsBash(action)):
        goto NULLIFY
    if (IsSlash(action) and target.GetEnchantCount(120/0x78) != 0)
    or (IsStab(action)  and target.GetEnchantCount(121/0x79) != 0)
    or (IsBash(action)  and target.GetEnchantCount(122/0x7a) != 0)
    or (IsFire(action)  and target.GetEnchantCount(124/0x7c) != 0)
    or (IsWater(action) and target.GetEnchantCount(125/0x7d) != 0)
    or (IsWind(action)  and target.GetEnchantCount(126/0x7e) != 0)
    or (IsEarth(action) and target.GetEnchantCount(127/0x7f) != 0)
    or (IsLight(action) and target.GetEnchantCount(128/0x80) != 0):
        NULLIFY:
            hitResult.hpDmg = hitResult.tpDmg = 0x7fffffff; hitResult.resultCode = 4; hitResult.nullified = 1u8
            return true
    return false

function CheckAilmentNullificationAndTrap(cmdId, sourceType, target, baseRate: f32) -> i32:
    // Shared across CCommand_0113..0123 (0x481ea0..0x483840):
    //   1. If sourceType == 4 (dungeon gas trap) and target.GetEnchantCount(138/0x8a) != 0: result = 4 (Nullified)
    //   2. If target.GetEnchantCount(specificNullEnch) != 0: result = 4 (Nullified), immediate return
    //        (131 Poison, 130 Freeze, 136 Paralysis, 132 Sleep, 133 Silence, 129 Stun, 134 Instakill,
    //         135 Petrification & Special Petrification, 139 Slow)
    //   3. If target.GetEnchantCount(137/0x89 Nullify All Ailments) != 0: result = 4 (Nullified), immediate return
    //   4. If sourceType == 4 and target.GetEnchantCount(269/0x10d) != 0: rate -= 15.0f (before Rand(100) < trunc0(rate))

function CheckOutOfBattleAilmentDissipation(cmd, battleInfo, unit): // 0x48d1e0..0x48d241
    // Runs ONLY outside battle (battleInfo.battle == null):
    //   stepPeriod = (unit.GetEnchantCount(265/0x109) != 0) ? 2 : 5
    //   cmd.stepCounter += 1; if cmd.stepCounter >= stepPeriod: cmd.stepCounter = 0; roll Rand(100) < cmd.cureRate
```
- **Program Evidence:**
```asm
00421b03  push     0x7b
00421b07  call     dword ptr [eax + 0xf0]
00421b35  mov      dword ptr [ebx + 0x1c], 0x7fffffff
00421b51  mov      dword ptr [ebx + 0x2c], 4
00421b67  push     0x78
00421b6b  call     dword ptr [eax + 0xf0]
00421bcf  call     dword ptr [eax + 0xf0]
00421c52  call     dword ptr [eax + 0xf0]
00481f0a  cmp      dword ptr [edi + 8], 4
00481f14  push     0x8a
00481f19  call     dword ptr [eax + 0xf0]
00481f2d  push     0x83
00481f32  call     dword ptr [eax + 0xf0]
00481f4a  push     0x89
00481f4f  call     dword ptr [eax + 0xf0]
00481ff9  push     0x10d
00481ffe  call     dword ptr [eax + 0xf0]
0048200d  subss    xmm1, dword ptr [0x6d947c]    ; float 15
0048d1e3  cmp      dword ptr [edi + 0x40], 0
0048d1ed  push     0x109
0048d1f2  call     dword ptr [eax + 0xf0]
0048d1f8  neg      eax
0048d1fa  sbb      eax, eax
0048d1ff  and      eax, 0xfffffffd
0048d202  add      eax, 5
0048d205  cmp      dword ptr [ebx + 0x30], eax
```

---

### M09.11 Turn-Start Regen (`144..149, 296`), Defend Regen (`257, 292`), Damage-to-TP (`72, 73`) & Post-Battle Recovery (`193, 194`)

- **Binary VA(s):** `0x437bc4..0x437e00` (TurnPhaseNo 16 turn-start regen `144..149, 296`), `0x4197ab..0x4198c0` (`CActionDefense` `257, 292`), `0x47e687..0x47e750` (`CCommand::Execute` damage-to-TP `72, 73`), `0x43d85e..0x43d927` (`CBattleBase::End` post-battle full heal `193, 194`)
- **Calls:** `vtable+0xf0` (`M09.07`), `vtable+0x28` (`GetMaxHP`), `0x505ac0` (`Rand(100)`), `0x47e500` (`CCommand::Execute`)
- **CalledBy:** `CBattleBase::Update` TurnPhaseNo 16 (`M00.03`), `CActionDefense` (`M00.04`), `CCommand::Execute` (`M00.06`), `CBattleBase::End` (`M00.09`)
- **Typed Pseudocode:**
```text
function TurnStartRegenEnchants(actor):                             // 0x437bc4..0x437e00 (TurnPhaseNo 16)
    hpHeal: i32 = 0
    if (c144 = actor.GetEnchantCount(144/0x90)) > 0: hpHeal += max(4,  trunc0(f32(actor.MaxHP) * (f32(c144) * 0.04f)))
    if (c145 = actor.GetEnchantCount(145/0x91)) > 0: hpHeal += max(2,  trunc0(f32(actor.MaxHP) * (f32(c145) * 0.02f)))
    if (c148 = actor.GetEnchantCount(148/0x94)) > 0: hpHeal += max(10, trunc0(f32(actor.MaxHP) * (f32(c148) * 0.08f)))
    if actor.GetEnchantCount(296/0x128) != 0:
        if Rand(100) < 4: hpHeal += actor.MaxHP                     // 1 RNG draw (4% full MaxHP heal)
    // TP regen is FLAT integer (NOT percent of MaxTP):
    tpHeal: i32 = 4 * actor.GetEnchantCount(146/0x92)
                + 2 * actor.GetEnchantCount(147/0x93)
                + 6 * actor.GetEnchantCount(149/0x95)

function DefendActionRegenEnchants(actor):                          // 0x4197ab..0x4198c0
    if actor.GetEnchantCount(257/0x101) != 0:
        actor.HealHP(max(10, trunc0(f32(actor.MaxHP) * 0.20f)))     // Boolean (> 0)
    if actor.GetEnchantCount(292/0x124) != 0:
        actor.curTP = clamp(actor.curTP + max(5, trunc0(f32(actor.MaxTP) * 0.10f)), 0, actor.MaxTP)

function DamageToTPEnchants(target, hpDamage: i32, existingTpGain: i32) -> i32: // 0x47e687..0x47e750
    rate72: f32 = f32(target.GetEnchantCount(72/0x48)) * 0.05f
    rate73: f32 = f32(target.GetEnchantCount(73/0x49)) * 0.10f
    minTp:  i32 = (rate73 > 0.0f) ? 5 : 1                           // Ench 73 raises floor from 1 to 5 TP!
    totalRate: f32 = rate72 + ((rate73 > 0.0f) ? rate73 : 0.0f)
    if totalRate > 0.0f:
        tpGain = existingTpGain + trunc0(f32(hpDamage) * min(0.50f, totalRate)) // Hard cap 50%!
        return max(minTp, tpGain)
    return existingTpGain

function PostBattleFullHealEnchants(member, partyHpRate: f32, partyTpRate: f32): // 0x43d85e..0x43d927
    hpRate = (member.GetEnchantCount(193/0xc1) != 0) ? 1.0f : partyHpRate
    tpRate = (member.GetEnchantCount(194/0xc2) != 0) ? 1.0f : partyTpRate
```
- **Program Evidence:**
```asm
00437bcc  call     eax
00437be9  mulss    xmm0, dword ptr [0x6d92e8]    ; float 0.04
00437c09  mov      ecx, 4
00437c1a  cvttss2si eax, xmm0
00437c29  push     0x91
00437c53  mulss    xmm0, dword ptr [0x6d92e0]    ; float 0.02
00437c93  push     0x94
00437cbd  mulss    xmm0, dword ptr [0x6d9300]    ; float 0.08
00437cfd  push     0x128
00437d15  call     0x505ac0
00437d1a  cmp      eax, 4
00437d7d  push     0x92
00437d96  shl      esi, 2
00437da6  push     0x95
00437dc1  lea      esi, [esi + eax*2]
004197ae  push     0x101
004197b7  call     dword ptr [eax + 0xf0]
004197f3  mulss    xmm0, dword ptr [0x6d9324]    ; float 0.2
00419801  cmovl    esi, eax
00419843  push     0x124
0041984c  call     dword ptr [eax + 0xf0]
0041988c  mulss    xmm0, dword ptr [0x6d930c]    ; float 0.1
0041989a  cmovl    edi, eax
0047e689  push     0x48
0047e68d  call     dword ptr [eax + 0xf0]
0047e6b1  mulss    xmm0, dword ptr [0x6d92ec]    ; float 0.05
0047e6be  call     dword ptr [eax + 0xf0]
0047e6e4  mulss    xmm1, dword ptr [0x6d930c]    ; float 0.1
0047e70e  movss    xmm1, dword ptr [0x6d9348]    ; float 0.5
0047e716  minss    xmm1, xmm0
0047e72e  cmovl    edi, ecx
0043d85e  push     0xc1
0043d868  call     dword ptr [eax + 0xf0]
0043d872  movss    xmm0, dword ptr [0x6d938c]    ; float 1
0043d904  push     0xc2
0043d90e  call     dword ptr [eax + 0xf0]
```

---

### M09.12 TP Cost (`246..249`), Performance Efficacy (`300..305`), Unarmed (`263`), Class Weapon Mod (`264`) & Unique Skill Lv+1 (`293`)

- **Binary VA(s):** `0x4fd250..0x4fd3bf` (`GetEffectiveTpCost` `246..249`), `0x48c01b..0x48c0ca` (`GetPerformanceEfficacyBonus` `300..303`), `0x4f5595..0x4f55e7` (`vtable+0xf4` Unarmed Rank `263`), `0x4f7fb0..0x4f7fdf` (`264` Class weapon modifier), `0x4f7150..0x4f718f` / `0x4f4de1` / `0x4f72fe` (`293` Unique skill level +1)
- **Calls:** `vtable+0xf0` (`M09.07`), `0x507310` (`TechniqueData_0x738a64`, `SpellData_0x738a58`, `WeaponRank_0x738a94`), `0x61c040` (`floor`), `0x4f68a0` (`_SearchSkill`)
- **CalledBy:** Skill cost check / execution (`M00.04`), Song/Dance command value getters (`0x48bf90`), `CBattle::_SetTime`, `RecalcStats` (`0x4f7c00`), `CGamePlayerStatusBase::GetSkillLevel` (`vtable+0x148`)
- **Typed Pseudocode:**
```text
function GetEffectiveTpCost(unit, skillId: u32, baseCost: i32) -> i32: // 0x4fd250..0x4fd3bf
    cost: i32 = baseCost
    if IsTechnique(skillId):                                        // found in 0x738a64
        if unit.GetEnchantCount(246/0xf6) != 0: cost = trunc0(f32(cost) * 0.80f)
        if unit.GetEnchantCount(247/0xf7) != 0: cost = trunc0(f32(cost) * 0.60f) // Multiplicative if both!
    else if IsSpell(skillId):                                       // found in 0x738a58
        if unit.GetEnchantCount(248/0xf8) != 0: cost = trunc0(f32(cost) * 0.80f)
        if unit.GetEnchantCount(249/0xf9) != 0: cost = trunc0(f32(cost) * 0.60f) // Multiplicative if both!
    cost = max(1, cost)
    // Followed by in-battle passive cmd 266 (0x10a): cost = max(1, cost - trunc0(floor(f32(cost) * cmd266.val))).
    return cost

function GetPerformanceEfficacyBonus(unit, perfPassiveId: u32) -> f32: // 0x48c01b..0x48c0ca
    // Song (perfPassiveId == 0x117 / 279):  min(0.05f, f32(ench300)*0.02f + f32(ench301)*0.01f)
    // Dance (perfPassiveId == 0x118 / 280): min(0.05f, f32(ench302)*0.02f + f32(ench303)*0.01f)
    // Doll (M09.03):                        min(0.05f, f32(ench304)*0.02f + f32(ench305)*0.01f)

function UnarmedRank_ClassMod_UniqueSkill(unit):
    // 1. Unarmed Speed (0x4f5595..0x4f55e7, vtable+0xf4): when right-hand slot 0 is null, defaults to class unarmed rank;
    //    if unit.GetEnchantCount(263/0x107) != 0: overrides rank to 1 (Rank A speed multiplier in 0x738a94)!
    // 2. Class Weapon Modifier (0x4f7fb0..0x4f7fdf): if unit.GetEnchantCount(264/0x108) != 0: mod += 0.02f (boolean).
    // 3. Unique Skill Level +1 (0x4f7150..0x4f718f): if skillId == unit.uniqueSkillId ([unit+0xcc])
    //    AND unit.GetEnchantCount(293/0x125) != 0 AND learnedLv in 1..8 ((learnedLv - 1) <= 7): return learnedLv + 1 (max 9).
```
- **Program Evidence:**
```asm
004fd291  push     0xf6
004fd296  call     dword ptr [eax + 0xf0]
004fd2a7  mulss    xmm0, dword ptr [0x6d936c]    ; float 0.8
004fd2b3  push     0xf7
004fd2e2  push     0xf8
004fd2e7  call     dword ptr [eax + 0xf0]
004fd2f8  mulss    xmm0, dword ptr [0x6d936c]    ; float 0.8
004fd304  push     0xf9
004fd30d  call     dword ptr [eax + 0xf0]
004fd31e  mulss    xmm0, dword ptr [0x6d934c]    ; float 0.6
004fd336  cmovle   edi, eax
0048c01b  cmp      edi, 0x117
0048c027  push     0x12c
0048c02c  call     dword ptr [eax + 0xf0]
0048c032  push     0x12d
0048c045  push     0x12e
0048c04a  call     dword ptr [eax + 0xf0]
0048c050  push     0x12f
0048c071  mulss    xmm0, dword ptr [0x6d92e0]    ; float 0.02
0048c09c  mulss    xmm1, dword ptr [0x6d92d4]    ; float 0.01
0048c0a9  movss    xmm0, dword ptr [0x6d92ec]    ; float 0.05
0048c0b1  minss    xmm0, xmm1
004f5595  push     0x107
004f55ab  call     dword ptr [eax + 0xf0]
004f55b5  mov      dword ptr [esp + 4], 1
004f7fb0  push     0x108
004f7fc1  call     dword ptr [eax + 0xf0]
004f7fd1  addss    xmm0, dword ptr [0x6d92e0]    ; float 0.02
004f7162  cmp      esi, dword ptr [ebx + 0xcc]
004f716e  push     0x125
004f7173  call     dword ptr [edx + 0xf0]
004f717d  lea      ecx, [edi - 1]
004f7180  lea      eax, [edi + 1]
004f7183  cmp      ecx, 7
```

---

### M09.13 Escape (`262`), Missed Spell (`272`), Conditional/Species Damage (`170..290`), Fast-Chant Bug (`298`) & Crit Floor (`268`)

- **Binary VA(s):** `0x41ae21..0x41aef0` (`CActionEscape` `262`), `0x44ee33..0x44ee6f` (Missed spell `272`), `0x44bd54..0x44bee5` (Species dmg reduction `227..244`), `0x44bfb5..0x44c3b5` (Species slayer `170..186, 196, 203..209`), `0x44c8b4..0x44cd90` (Joint `261/290`, Party-size `267`, Full-HP `271`, Lv-diff `219/220`, Ailed `280`), `0x44a355..0x44a399` (Fast-Chant `298`), `0x44f4af..0x44f4d9` (Crit floor `268`)
- **Calls:** `vtable+0xf0` (`M09.07`), `0x490790` (`CRandom::Get`), `vtable+0x7c` (`HasTrueAilment`), `0x5587c0` (`MonsterData`), `0x4f21c0`/`0x4f21f0` (Feline/SeaCreature checks)
- **CalledBy:** `CActionEscape::Update`, `CalcPhysicalAttack`, `CalcMagicalAttack`, `CBattle::_SetTime`, `CBattle::_CalcCritical` (`M00.06`, `M00.08`)
- **Typed Pseudocode:**
```text
function EscapeProbabilityEnchant(actor, avgEnemyAGI: f32, bonus: f32, retryBonus: f32) -> bool: // 0x41ae21..0x41aef0
    raw: f32   = 0.30f + (f32(actor.AGI) - avgEnemyAGI) / 50.0f + bonus
    floor: f32 = (actor.GetEnchantCount(262/0x106) != 0) ? 0.50f : 0.20f
    rate: f32  = max(floor, min(0.95f, raw))
    if retryBonus > 0.0f: rate = min(0.95f, rate + retryBonus)
    return GlobalRng_0x816ce8.Rand(100) < trunc0(rate * 100.0f)     // 1 RNG draw

function MissedSpellEnchant(attacker, dmg: i32) -> i32:             // 0x44ee33..0x44ee6f
    return (attacker.GetEnchantCount(272/0x110) != 0) ? ((dmg * 3) / 4) : (dmg / 2)

function ConditionalAndSpeciesPhysicalEnchants(attacker, target, dmgMult: f32, dmg: i32):
    // 0x44c8b4..0x44cd90:
    dmgMult += f32(attacker.GetEnchantCount(267/0x10b)) * f32(5 - PartyCount) * 0.10f
    if attacker.CurHP == attacker.MaxHP: dmgMult += f32(attacker.GetEnchantCount(271/0x10f)) * 0.10f
    if target.Lv > attacker.Lv:          dmgMult += f32(attacker.GetEnchantCount(219/0x0db)) * 0.10f
    if target.Lv < attacker.Lv:          dmgMult += f32(attacker.GetEnchantCount(220/0x0dc)) * 0.10f
    // Joint skills add +0.10f * ench261 + 0.20f * ench290; Species slayers add +0.15f/+0.30f/+0.60f (or +0.50f/+1.00f Fruit/Feline/Sea).
    // Post-calc ailment bonus (0x44cd5a..0x44cd8f):
    if attacker.GetEnchantCount(280/0x118) != 0 and target.vtable_0x7c_HasTrueAilment():
        dmg += trunc0(f32(dmg) * 0.15f)

function FastChantEnchant298_And_CritFloor268(unit):
    // 1. Enchant 298 (0x12a) at 0x44a355..0x44a399 (inside CBattle::_SetTime when entering chant):
    //    if unit.GetEnchantCount(298) != 0:
    //        if GlobalRng_0x816ce8.Rand(10) < 10:                      // VANILLA BUG: 0..9 < 10 ALWAYS TRUE (1 RNG draw)!
    //            unit.gauge = min(0.92f, unit.gauge + 0.25f)
    // 2. Enchant 268 (0x10c) at 0x44f4af..0x44f4d9 (inside _CalcCritical):
    //    critFloor: f32 = (unit.GetEnchantCount(268) != 0) ? 20.0f : 5.0f; critRate = max(critFloor, critRate)
```
- **Program Evidence:**
```asm
0041ae3c  push     0x106
0041ae54  divss    xmm0, dword ptr [0x6d94e0]    ; float 50
0041ae5c  addss    xmm0, dword ptr [0x6d9330]    ; float 0.3
0041ae6e  call     dword ptr [eax + 0xf0]
0041ae78  movss    xmm1, dword ptr [0x6d9348]    ; float 0.5
0041ae82  movss    xmm1, dword ptr [0x6d9324]    ; float 0.2
0041ae8f  movss    xmm2, dword ptr [0x6d9384]    ; float 0.95
0041aeec  cmp      eax, ecx
0044ee36  push     0x110
0044ee3d  call     dword ptr [eax + 0xf0]
0044ee47  lea      eax, [esi + esi*2]
0044ee51  sar      esi, 2
0044ee5d  sar      esi, 1
0044c95f  mov      ecx, 5
0044c97e  mulss    xmm0, dword ptr [0x6d930c]    ; float 0.1
0044c9af  push     0x10f
0044c9b6  call     dword ptr [eax + 0xf0]
0044ca04  push     0xdb
0044ca59  push     0xdc
0044cd5a  push     0x118
0044cd83  mulss    xmm0, dword ptr [0x6d931c]    ; float 0.15
0044a359  push     0x12a
0044a35e  call     dword ptr [eax + 0xf0]
0044a36e  push     0xa
0044a370  call     0x490790
0044a375  cmp      eax, 0xa
0044a380  addss    xmm0, dword ptr [0x6d932c]    ; float 0.25
0044a388  movss    xmm1, dword ptr [0x6d9380]    ; float 0.92
0044a390  minss    xmm1, xmm0
0044f4b2  push     0x10c
0044f4b9  call     dword ptr [eax + 0xf0]
0044f4c3  movss    xmm1, dword ptr [0x6d948c]    ; float 20
0044f4cd  movss    xmm1, dword ptr [0x6d9434]    ; float 5
```

---

### M09.14 EXP (`270, 275`), Equipment Drop (`276`), Pep (`195, 200, 201, 266, 294`) & Field/Dungeon Enchants (`192, 211..217, 258..260, 291`)

- **Binary VA(s):** `0x450768` (`CBattle::_AddExp` `270`), `0x445a06..0x445a25` (`CBattleResult::_Initialize` `275`), `0x55824e..0x558282` (`276` drop rate), `0x4f69e0..0x4f6a6a` (`Pep` `195/200/201`), `0x50983b..0x50985c` / `0x509a6d` / `0x509bbd` (`Pep` `266/294`), `0x4fb723..0x4fb805` (`216/217` step TP), `0x4e4d80..0x4e4dc5` (`192` scan), `0x4bc800..0x4bc850` & `0x55639e..0x556410` (`211..214, 259`), `0x4c46b0..0x4c46da` (`260`), `0x55576d..0x55578e` (`291`), `0x5558d0` / `0x555a3d` (`258`)
- **Calls:** `vtable+0xf0` (`M09.07`), `0x4e4f50` (`M09.07` `PartyHasEnchant`)
- **CalledBy:** `CBattle::_AddExp`, `CBattleResult::_Initialize` (`M00.09`), Drop table roll (`0x558180`), `CGamePlayerStatusBase::UpdatePep` (`0x4f69e0`), Dungeon step/chest/trap handlers
- **Typed Pseudocode:**
```text
function RewardPepAndFieldEnchants():
    // 1. EXP & Drops:
    //    - Ench 270 (0x10e, 0x450768): boosts underdog EXP multipliers for playerLv - enemyLv < 0:
    //        -4..-1 -> 1.15f (was 1.00f), -9..-5 -> 1.30f (was 1.10f), -19..-10 -> 1.50f (was 1.25f), <=-20 -> 1.75f (was 1.25f).
    //    - Ench 275 (0x113, 0x445a06): in CBattleResult::_Initialize, doubles final member EXP (exp += exp).
    //    - Ench 276 (0x114, 0x558255): equipment drop bonus += f32(20 * killer.GetEnchantCount(276)) (shl (n*5), 2).
    // 2. Pep Priority Chain (0x4f69e0..0x4f6a6a):
    //    pep = clamp(pep, 70.0f, 130.0f)
    //    if unit.GetEnchantCount(201/0xc9) != 0: pep = 70.0f
    //    if unit.GetEnchantCount(200/0xc8) != 0: pep = max(100.0f, pep)
    //    if unit.GetEnchantCount(195/0xc3) != 0: pep = 130.0f       // Strict priority: 195 > 200 > 201!
    //    Ench 266 (0x10a, 0x509844): Pep decay delta *= 0.50f. Ench 294 (0x126, 0x509a6d/0x509bbd): intensifies food Pep delta.
    // 3. Field / Dungeon Utility:
    //    - Ench 192 (0xc0, 0x4e4d9a): alive party member check -> reveals enemy HP & stats in UI.
    //    - Ench 216/217 (0xd8/0xd9, 0x4fb72c/0x4fb7c6): every 10 dungeon steps, recovers +1 TP (216) and/or +3 TP (217).
    //    - Ench 211..214 (0xd3..0xd6, 0x4bc809..0x4bc83a & 0x5563cb..0x5563fd): party-wide encounter step delta (-1, -2, +1, +2; min 1).
    //    - Ench 259 (0x103, 0x5563a7): party-wide shop encounter step threshold 50 -> 25.
    //    - Ench 260 (0x104, 0x4c46b8): party-wide non-gas trap damage = trunc0(f32(dmg) * 0.10f).
    //    - Ench 291 (0x123, 0x555771): party-wide chest Mimic rate += 20 percentage points (0x14).
    //    - Ench 258 (0x102, 0x5558d0/0x555a3d): party-wide higher-level equipment roll from treasure boxes.
```
- **Program Evidence:**
```asm
00450768  push     0x10e
00445a06  push     0x113
00445a1e  addss    xmm1, xmm1
00558250  push     0x114
00558255  call     dword ptr [eax + 0xf0]
0055825b  lea      eax, [eax + eax*4]
0055825e  shl      eax, 2
004f69e0  movss    xmm1, dword ptr [0x6d950c]    ; float 70
004f69e8  movss    xmm0, dword ptr [0x6d956c]    ; float 130
004f69f3  push     0xc9
004f6a0e  call     dword ptr [eax + 0xf0]
004f6a18  mov      dword ptr [esi + 0xd8], 0x428c0000
004f6a26  push     0xc8
004f6a2b  call     dword ptr [eax + 0xf0]
004f6a35  movss    xmm0, dword ptr [0x6d9540]    ; float 100
004f6a51  push     0xc3
004f6a56  call     dword ptr [eax + 0xf0]
004f6a60  mov      dword ptr [esi + 0xd8], 0x43020000
0050983f  push     0x10a
00509844  call     dword ptr [edx + 0xf0]
00509854  mulss    xmm0, dword ptr [0x6d9348]    ; float 0.5
004fb727  push     0xd8
004fb72c  call     dword ptr [eax + 0xf0]
004fb780  mov      dword ptr [ebp - 0x64], 1
004fb7c1  push     0xd9
004fb7c6  call     dword ptr [eax + 0xf0]
004e4d95  push     0xc0
004e4d9a  call     dword ptr [edx + 0xf0]
004bc802  mov      ecx, 0xd3
004bc809  call     0x4e4f50
004bc815  mov      ecx, 0xd4
004bc81a  call     0x4e4f50
004bc826  mov      ecx, 0xd5
004bc82b  call     0x4e4f50
004bc835  mov      ecx, 0xd6
004bc83a  call     0x4e4f50
005563a2  mov      esi, 0x32
005563a7  call     0x4e4f50
005563ae  mov      ecx, 0x19
004c46b3  mov      ecx, 0x104
004c46b8  call     0x4e4f50
004c46c9  mulss    xmm0, dword ptr [0x6d930c]    ; float 0.1
00555771  call     0x4e4f50
0055577a  add      ebx, 0x14
```

---

## 5. Complete Grouped Master Table of All 280 Enchantments

### M09.15 Complete Grouped Master Table of All 280 `EnchantData.pck` Enchantments

- **Binary VA(s):** `0x4f5470..0x4f54cd` (`vtable+0xf0`), `0x4f62c0..0x4f652d` (`_SetupEnchant` / `_AddEnchant`), `0x4f8270..0x4f8fdf` (`_CalculateParameterEnchant`), `0x4e4f50..0x4e4fb6` (`PartyHasEnchant`), `0x4d4dd0..0x4d4dd4` (`CGameEnemyStatus::vtable+0xf0`)
- **Calls:** `0x507310` (`EnchantData_0x7389d0`), `M09.07`, `M09.08`, `M09.09`, `M09.10`, `M09.11`, `M09.12`, `M09.13`, `M09.14`
- **CalledBy:** All 36 `vtable+0xf0` functions, `_CalculateParameterEnchant` (`0x4f8270`), TurnPhaseNo 16 (`0x437bc4`), `CBattleResult::_Initialize` (`0x445a06`), and all 14 `PartyHasEnchant` (`0x4e4f50`) call sites
- **Typed Pseudocode:**
```text
// Complete inventory invariant across EnchantData.pck (280 total entries):
//   - Direct _CalculateParameterEnchant (0x4f8270): 94 IDs (0..28, 88..119, 222..225, 281, 310..356)
//   - Direct vtable+0xf0 (0x4f5470) & shared jump tails: 175 IDs
//   - PartyHasEnchant (0x4e4f50 -> vtable+0xf0): 11 IDs (211..214, 258..260, 291, 295, 297)
//   - Unused / Zero-handler IDs in EnchantData.pck: 0 (100% of all 280 IDs have verified binary handlers!)
//   - IDs with Vanilla Uses == 0 exist in EnchantData.pck and have live binary handlers in DT22_en_unwrapped.vanilla.exe.
//   - Flags bit 0 (0x01) = Stacks (additive count in vtable+0xf0 and _SetupEnchant); bit 7 (0x80) = Offhand dual-wield weapon allowed.
```

#### 1. Core Stat Enchants (HP / TP / ATK..AGI / All-Stat) (29 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 0 (`0x000`) | Max HP UP | `0x9d` | Yes | Yes | 0 | `0x4f8354` | MaxHP += max(4, baseMaxHP / 10); total HP delta clamped to [-base/2, +base/2] |
| 1 (`0x001`) | Max HP MiniUP | `0x9f` | Yes | Yes | 27 | `0x4f8382` | MaxHP += max(2, baseMaxHP / 20); total HP delta clamped to [-base/2, +base/2] |
| 2 (`0x002`) | Max HP DOWN | `0xbd` | Yes | Yes | 6 | `0x4f83ae` | MaxHP -= max(0, baseMaxHP / 10); total HP delta clamped to [-base/2, +base/2] |
| 3 (`0x003`) | Max TP UP | `0x9d` | Yes | Yes | 81 | `0x4f83d7` | MaxTP += max(4, baseMaxTP / 10); total TP delta clamped to [-base/2, +base/2] |
| 4 (`0x004`) | Max TP MiniUP | `0x9f` | Yes | Yes | 15 | `0x4f84cb` | MaxTP += max(2, baseMaxTP / 20); total TP delta clamped to [-base/2, +base/2] |
| 5 (`0x005`) | Max TP DOWN | `0xbd` | Yes | Yes | 7 | `0x4f84ed` | MaxTP -= max(0, baseMaxTP / 10); total TP delta clamped to [-base/2, +base/2] |
| 6 (`0x006`) | ATK UP | `0x9b` | Yes | Yes | 48 | `0x4f8514` | ATK += max(4, baseATK / 10) (via vtable+0x30) |
| 7 (`0x007`) | ATK MiniUP | `0x9b` | Yes | Yes | 14 | `0x4f8549` | ATK += max(2, baseATK / 20) (via vtable+0x30) |
| 8 (`0x008`) | ATK DOWN | `0xbb` | Yes | Yes | 5 | `0x4f857e` | ATK -= max(0, baseATK / 10) (via vtable+0x30) |
| 9 (`0x009`) | DEF UP | `0x9d` | Yes | Yes | 63 | `0x4f85b0` | DEF += max(4, baseDEF / 10) (via vtable+0x30) |
| 10 (`0x00a`) | DEF MiniUP | `0x9d` | Yes | Yes | 19 | `0x4f85e5` | DEF += max(2, baseDEF / 20) (via vtable+0x30) |
| 11 (`0x00b`) | DEF DOWN | `0xbd` | Yes | Yes | 5 | `0x4f861a` | DEF -= max(0, baseDEF / 10) (via vtable+0x30) |
| 12 (`0x00c`) | INT UP | `0x9f` | Yes | Yes | 29 | `0x4f8649` | INT += max(4, baseINT / 10) (via vtable+0x30) |
| 13 (`0x00d`) | INT MiniUP | `0x9f` | Yes | Yes | 11 | `0x4f867e` | INT += max(2, baseINT / 20) (via vtable+0x30) |
| 14 (`0x00e`) | INT DOWN | `0xbf` | Yes | Yes | 14 | `0x4f86b3` | INT -= max(0, baseINT / 10) (via vtable+0x30) |
| 15 (`0x00f`) | RES UP | `0x9f` | Yes | Yes | 51 | `0x4f86e2` | RES += max(4, baseRES / 10) (via vtable+0x30) |
| 16 (`0x010`) | RES MiniUP | `0x9f` | Yes | Yes | 16 | `0x4f8717` | RES += max(2, baseRES / 20) (via vtable+0x30) |
| 17 (`0x011`) | RES DOWN | `0xbf` | Yes | Yes | 8 | `0x4f874c` | RES -= max(0, baseRES / 10) (via vtable+0x30) |
| 18 (`0x012`) | DEX UP | `0x9f` | Yes | Yes | 67 | `0x4f877e` | DEX += max(4, baseDEX / 10) (via vtable+0x30) |
| 19 (`0x013`) | DEX MiniUP | `0x9f` | Yes | Yes | 14 | `0x4f87b9` | DEX += max(2, baseDEX / 20) (via vtable+0x30) |
| 20 (`0x014`) | DEX DOWN | `0xbf` | Yes | Yes | 9 | `0x4f87ee` | DEX -= max(0, baseDEX / 10) (via vtable+0x30) |
| 21 (`0x015`) | AGI UP | `0x9f` | Yes | Yes | 69 | `0x4f8820` | AGI += max(4, baseAGI / 10) (via vtable+0x30) |
| 22 (`0x016`) | AGI MiniUP | `0x9f` | Yes | Yes | 21 | `0x4f8855` | AGI += max(2, baseAGI / 20) (via vtable+0x30) |
| 23 (`0x017`) | AGI DOWN | `0xbf` | Yes | Yes | 9 | `0x4f888a` | AGI -= max(0, baseAGI / 10) (via vtable+0x30) |
| 24 (`0x018`) | All stats +1 | `0x1ac` | No | Yes | 1 | `0x4f88bc` | ATK, DEF, INT, RES, DEX, AGI each +1 |
| 25 (`0x019`) | All stats +3 | `0x1ac` | No | Yes | 10 | `0x4f88d8` | ATK, DEF, INT, RES, DEX, AGI each +3 |
| 26 (`0x01a`) | All stats +6 | `0x1ac` | No | Yes | 2 | `0x4f88fa` | ATK, DEF, INT, RES, DEX, AGI each +6 |
| 27 (`0x01b`) | All stats +9 | `0x1ac` | No | Yes | 2 | `0x4f891c` | ATK, DEF, INT, RES, DEX, AGI each +9 |
| 28 (`0x01c`) | All stats +12 | `0x1ac` | No | Yes | 0 | `0x4f893e` | ATK, DEF, INT, RES, DEX, AGI each +12 |

#### 2. Row-Conditional Stat Enchants (5 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 222 (`0x0de`) | Front line ATK 8% UP | `0xe0` | No | Yes | 1 | `0x4f8b9c` | Front row: ATK += trunc0(f32(curATK) * 0.08f) |
| 223 (`0x0df`) | Front line ATK + DEF 4% UP | `0xe0` | No | Yes | 1 | `0x4f8bf2` | Front row: ATK += curATK / 25, DEF += curDEF / 25 (+4% each) |
| 224 (`0x0e0`) | Back line INT 8% UP | `0xe0` | No | Yes | 1 | `0x4f8c69` | Back row: INT += trunc0(f32(curINT) * 0.08f) |
| 225 (`0x0e1`) | Back line INT + RES 4% UP | `0xe0` | No | Yes | 1 | `0x4f8cbf` | Back row: INT += curINT / 25, RES += curRES / 25 (+4% each) |
| 281 (`0x119`) | Back line DEX + AGI 2% UP | `0xe0` | No | Yes | 1 | `0x4f8d36` | Back row: DEX += curDEX / 50, AGI += curAGI / 50 (+2% each) |

#### 3. Elemental & Physical Resistance Enchants (60 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 88 (`0x058`) | Fire resistance UP | `0xbd` | Yes | Yes | 16 | `0x4f8960` | Fire resist +20 (clamped [-100, +100]) |
| 89 (`0x059`) | Fire resistance MiniUP | `0xbd` | Yes | Yes | 5 | `0x4f896e` | Fire resist +10 (clamped [-100, +100]) |
| 90 (`0x05a`) | Fire resistance DOWN | `0xbd` | Yes | Yes | 18 | `0x4f897c` | Fire resist -20 (clamped [-100, +100]) |
| 91 (`0x05b`) | Water resistance UP | `0xbd` | Yes | Yes | 42 | `0x4f898a` | Water resist +20 (clamped [-100, +100]) |
| 92 (`0x05c`) | Water resistance MiniUP | `0xbd` | Yes | Yes | 10 | `0x4f8998` | Water resist +10 (clamped [-100, +100]) |
| 93 (`0x05d`) | Water resistance DOWN | `0xbd` | Yes | Yes | 13 | `0x4f89a6` | Water resist -20 (clamped [-100, +100]) |
| 94 (`0x05e`) | Wind resistance UP | `0xbd` | Yes | Yes | 24 | `0x4f89b4` | Wind resist +20 (clamped [-100, +100]) |
| 95 (`0x05f`) | Wind resistance MiniUP | `0xbd` | Yes | Yes | 6 | `0x4f89c2` | Wind resist +10 (clamped [-100, +100]) |
| 96 (`0x060`) | Wind resistance DOWN | `0xbd` | Yes | Yes | 4 | `0x4f89d0` | Wind resist -20 (clamped [-100, +100]) |
| 97 (`0x061`) | Earth resistance UP | `0xbd` | Yes | Yes | 29 | `0x4f89de` | Earth resist +20 (clamped [-100, +100]) |
| 98 (`0x062`) | Earth resistance MiniUP | `0xbd` | Yes | Yes | 7 | `0x4f89ee` | Earth resist +10 (clamped [-100, +100]) |
| 99 (`0x063`) | Earth resistance DOWN | `0xbd` | Yes | Yes | 5 | `0x4f89fe` | Earth resist -20 (clamped [-100, +100]) |
| 100 (`0x064`) | Lightning resistance UP | `0xbd` | Yes | Yes | 16 | `0x4f8a0e` | Lightning resist +20 (clamped [-100, +100]) |
| 101 (`0x065`) | Lightning resistance MiniUP | `0xbd` | Yes | Yes | 6 | `0x4f8a1e` | Lightning resist +10 (clamped [-100, +100]) |
| 102 (`0x066`) | Lightning resistance DOWN | `0xbd` | Yes | Yes | 6 | `0x4f8a2e` | Lightning resist -20 (clamped [-100, +100]) |
| 103 (`0x067`) | Elemental resistance GrandUP | `0xa5` | Yes | Yes | 4 | `0x4f8a3e` | All 5 elemental resists +50 (clamped [-100, +100]) |
| 104 (`0x068`) | Elemental resistance UP | `0xbd` | Yes | Yes | 29 | `0x4f8a60` | All 5 elemental resists +15 (clamped [-100, +100]) |
| 105 (`0x069`) | Elemental resistance MiniUP | `0xbd` | Yes | Yes | 6 | `0x4f8a82` | All 5 elemental resists +7 (clamped [-100, +100]) |
| 106 (`0x06a`) | Elemental resistance DOWN | `0xbd` | Yes | Yes | 3 | `0x4f8aa4` | All 5 elemental resists -15 (clamped [-100, +100]) |
| 107 (`0x06b`) | Slash resistance UP | `0xbd` | Yes | Yes | 11 | `0x4f8ac6` | Slash resist +20 (clamped [-100, +100]) |
| 108 (`0x06c`) | Slash resistance MiniUP | `0xbd` | Yes | Yes | 3 | `0x4f8ad4` | Slash resist +10 (clamped [-100, +100]) |
| 109 (`0x06d`) | Slash resistance DOWN | `0xbd` | Yes | Yes | 3 | `0x4f8ae2` | Slash resist -20 (clamped [-100, +100]) |
| 110 (`0x06e`) | Stab resistance UP | `0xbd` | Yes | Yes | 16 | `0x4f8af0` | Stab resist +20 (clamped [-100, +100]) |
| 111 (`0x06f`) | Stab resistance MiniUP | `0xbd` | Yes | Yes | 3 | `0x4f8afe` | Stab resist +10 (clamped [-100, +100]) |
| 112 (`0x070`) | Stab resistance DOWN | `0xbd` | Yes | Yes | 2 | `0x4f8b0c` | Stab resist -20 (clamped [-100, +100]) |
| 113 (`0x071`) | Bash resistance UP | `0xbd` | Yes | Yes | 17 | `0x4f8b1a` | Bash resist +20 (clamped [-100, +100]) |
| 114 (`0x072`) | Bash resistance MiniUP | `0xbd` | Yes | Yes | 7 | `0x4f8b28` | Bash resist +10 (clamped [-100, +100]) |
| 115 (`0x073`) | Bash resistance DOWN | `0xbd` | Yes | Yes | 4 | `0x4f8b36` | Bash resist -20 (clamped [-100, +100]) |
| 116 (`0x074`) | Physical resistance GrandUP | `0xb5` | Yes | Yes | 29 | `0x4f8b44` | All 3 physical resists (Slash/Stab/Bash) +25 (clamped [-100, +100]) |
| 117 (`0x075`) | Physical resistance UP | `0xbd` | Yes | Yes | 15 | `0x4f8b5a` | All 3 physical resists +10 (clamped [-100, +100]) |
| 118 (`0x076`) | Physical resistance MiniUP | `0xbd` | Yes | Yes | 4 | `0x4f8b70` | All 3 physical resists +5 (clamped [-100, +100]) |
| 119 (`0x077`) | Physical resistance DOWN | `0xbd` | Yes | Yes | 5 | `0x4f8b86` | All 3 physical resists -10 (clamped [-100, +100]) |
| 310 (`0x136`) | Fire resistance MegaUP | `0xa4` | No | Yes | 3 | `0x4f8dad` | Fire resist +100 (clamped [-100, +100]) |
| 311 (`0x137`) | Fire resistance GrandUP | `0xa5` | Yes | Yes | 13 | `0x4f8dbe` | Fire resist +50 (clamped [-100, +100]) |
| 312 (`0x138`) | Fire resistance GrandDOWN | `0xad` | Yes | Yes | 4 | `0x4f8dcf` | Fire resist -50 (clamped [-100, +100]) |
| 315 (`0x13b`) | Water resistance MegaUP | `0xa4` | No | Yes | 2 | `0x4f8de0` | Water resist +100 (clamped [-100, +100]) |
| 316 (`0x13c`) | Water resistance GrandUP | `0xa5` | Yes | Yes | 22 | `0x4f8df1` | Water resist +50 (clamped [-100, +100]) |
| 317 (`0x13d`) | Water resistance GrandDOWN | `0xad` | Yes | Yes | 2 | `0x4f8e02` | Water resist -50 (clamped [-100, +100]) |
| 320 (`0x140`) | Wind resistance MegaUP | `0xa4` | No | Yes | 1 | `0x4f8e13` | Wind resist +100 (clamped [-100, +100]) |
| 321 (`0x141`) | Wind resistance GrandUP | `0xa5` | Yes | Yes | 17 | `0x4f8e24` | Wind resist +50 (clamped [-100, +100]) |
| 322 (`0x142`) | Wind resistance GrandDOWN | `0xad` | Yes | Yes | 3 | `0x4f8e35` | Wind resist -50 (clamped [-100, +100]) |
| 325 (`0x145`) | Earth resistance MegaUP | `0xa4` | No | Yes | 2 | `0x4f8e46` | Earth resist +100 (clamped [-100, +100]) |
| 326 (`0x146`) | Earth resistance GrandUP | `0xa5` | Yes | Yes | 20 | `0x4f8e59` | Earth resist +50 (clamped [-100, +100]) |
| 327 (`0x147`) | Earth resistance GrandDOWN | `0xad` | Yes | Yes | 0 | `0x4f8e6c` | Earth resist -50 (clamped [-100, +100]) |
| 330 (`0x14a`) | Lightning resistance MegaUP | `0xa4` | No | Yes | 5 | `0x4f8e7f` | Lightning resist +100 (clamped [-100, +100]) |
| 331 (`0x14b`) | Lightning resistance GrandUP | `0xa5` | Yes | Yes | 9 | `0x4f8e92` | Lightning resist +50 (clamped [-100, +100]) |
| 332 (`0x14c`) | Lightning resistance GrandDOWN | `0xad` | Yes | Yes | 3 | `0x4f8ea5` | Lightning resist -50 (clamped [-100, +100]) |
| 335 (`0x14f`) | Elemental resistance MegaUP | `0xa5` | Yes | Yes | 1 | `0x4f8eb8` | All 5 elemental resists +75 (clamped [-100, +100]) |
| 336 (`0x150`) | Elemental resistance GrandDOWN | `0xad` | Yes | Yes | 3 | `0x4f8edd` | All 5 elemental resists -30 (clamped [-100, +100]) |
| 340 (`0x154`) | Slash resistance MegaUP | `0xa4` | No | Yes | 4 | `0x4f8f02` | Slash resist +100 (clamped [-100, +100]) |
| 341 (`0x155`) | Slash resistance GrandUP | `0xa5` | Yes | Yes | 8 | `0x4f8f13` | Slash resist +50 (clamped [-100, +100]) |
| 342 (`0x156`) | Slash resistance GrandDOWN | `0xad` | Yes | Yes | 1 | `0x4f8f24` | Slash resist -50 (clamped [-100, +100]) |
| 345 (`0x159`) | Stab resistance MegaUP | `0xa4` | No | Yes | 4 | `0x4f8f35` | Stab resist +100 (clamped [-100, +100]) |
| 346 (`0x15a`) | Stab resistance GrandUP | `0xa5` | Yes | Yes | 10 | `0x4f8f46` | Stab resist +50 (clamped [-100, +100]) |
| 347 (`0x15b`) | Stab resistance GrandDOWN | `0xad` | Yes | Yes | 0 | `0x4f8f57` | Stab resist -50 (clamped [-100, +100]) |
| 350 (`0x15e`) | Bash resistance MegaUP | `0xa4` | No | Yes | 3 | `0x4f8f68` | Bash resist +100 (clamped [-100, +100]) |
| 351 (`0x15f`) | Bash resistance GrandUP | `0xa5` | Yes | Yes | 12 | `0x4f8f79` | Bash resist +50 (clamped [-100, +100]) |
| 352 (`0x160`) | Bash resistance GrandDOWN | `0xad` | Yes | Yes | 1 | `0x4f8f8a` | Bash resist -50 (clamped [-100, +100]) |
| 355 (`0x163`) | Physical resistance MegaUP | `0xa5` | Yes | Yes | 9 | `0x4f8f9b` | All 3 physical resists +50 (clamped [-100, +100]) |
| 356 (`0x164`) | Physical resistance GrandDOWN | `0xad` | Yes | Yes | 4 | `0x4f8fb4` | All 3 physical resists -20 (clamped [-100, +100]) |

#### 4. Damage Nullification Enchants (9 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 120 (`0x078`) | Nullify slash attacks | `0xa4` | No | Yes | 1 | `0x421b6b` | Nullify Slash attacks (result code = 4, damage cleared) |
| 121 (`0x079`) | Nullify stab attacks | `0xa4` | No | Yes | 1 | `0x421b87` | Nullify Stab attacks (result code = 4, damage cleared) |
| 122 (`0x07a`) | Nullify bash attacks | `0xa4` | No | Yes | 2 | `0x421ba3` | Nullify Bash attacks (result code = 4, damage cleared) |
| 123 (`0x07b`) | Nullify physical attacks | `0xa4` | No | Yes | 1 | `0x421b07` | Nullify all Physical (Slash/Stab/Bash) attacks |
| 124 (`0x07c`) | Nullify fire damage | `0xa4` | No | Yes | 1 | `0x421bcf` | Nullify Fire attacks |
| 125 (`0x07d`) | Nullify water damage | `0xa4` | No | Yes | 2 | `0x421bef` | Nullify Water attacks |
| 126 (`0x07e`) | Nullify wind damage | `0xa4` | No | Yes | 1 | `0x421c0f` | Nullify Wind attacks |
| 127 (`0x07f`) | Nullify earth damage | `0xa4` | No | Yes | 1 | `0x421c2f` | Nullify Earth attacks |
| 128 (`0x080`) | Nullify lightning damage | `0xa4` | No | Yes | 1 | `0x421c52` | Nullify Lightning attacks |

#### 5. Ailment Nullification, Trap Evasion & Dissipation Enchants (13 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 129 (`0x081`) | Nullify stun | `0xa4` | No | Yes | 16 | `0x482d00` | Nullify Stun (cmd 118 / 0x76) |
| 130 (`0x082`) | Nullify freeze | `0xa4` | No | Yes | 12 | `0x482352` | Nullify Freeze (cmd 114 / 0x72) |
| 131 (`0x083`) | Nullify poison | `0xa4` | No | Yes | 12 | `0x481f32` | Nullify Poison (cmd 113 / 0x71) |
| 132 (`0x084`) | Nullify sleep | `0xa4` | No | Yes | 8 | `0x482832` | Nullify Sleep (cmd 116 / 0x74) |
| 133 (`0x085`) | Nullify silence | `0xa4` | No | Yes | 13 | `0x482aa2` | Nullify Silence (cmd 117 / 0x75) |
| 134 (`0x086`) | Nullify instakill | `0xa4` | No | Yes | 11 | `0x482ec0` | Nullify Instakill (cmd 119 / 0x77) |
| 135 (`0x087`) | Nullify petrification | `0xa4` | No | Yes | 9 | `0x483282, 0x483530` | Nullify Petrification (cmd 120 / 0x78) & Special Petrification (cmd 121 / 0x79) |
| 136 (`0x088`) | Nullify paralysis | `0xa4` | No | Yes | 10 | `0x4825c2` | Nullify Paralysis (cmd 115 / 0x73) |
| 137 (`0x089`) | Nullify all status ailments | `0xa4` | No | Yes | 2 | `0x481f4f..0x4838be` | Nullify all 11 ailments (cmds 113..123) |
| 138 (`0x08a`) | Nullify gas traps | `0xa4` | No | Yes | 6 | `0x481f19..0x483649` | Nullify dungeon gas-trap ailments (source type == 4) |
| 139 (`0x08b`) | Nullify slow | `0xa4` | No | Yes | 8 | `0x483662` | Nullify Slow (cmd 122 / 0x7a) |
| 265 (`0x109`) | Rate of status ailments dissipation UP | `0xe0` | No | Yes | 1 | `0x48d1f2` | Out-of-battle ailment cure roll interval: 5 steps -> 2 steps |
| 269 (`0x10d`) | Reduced trap trigger rate *(raw ID 269)* | `0xe0` | No | Yes | 0 | `0x481ffe..0x48372e` | Dungeon trap ailment rate -= 15.0f (source type == 4) |

#### 6. On-Hit Normal Attack Ailment & Drain Enchants (14 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 153 (`0x099`) | Normal attacks may inflict poison | `0x2a` | No | No | 8 | `0x421261` | Normal attack appends cmd 113 (Poison) @ 0.18f |
| 154 (`0x09a`) | Normal attacks may inflict sleep | `0x2a` | No | No | 3 | `0x4212b2` | Normal attack appends cmd 116 (Sleep) @ 0.15f |
| 155 (`0x09b`) | Normal attacks may inflict silence | `0x2a` | No | No | 7 | `0x421303` | Normal attack appends cmd 117 (Silence) @ 0.18f |
| 156 (`0x09c`) | Normal attacks may inflict freeze | `0x2a` | No | No | 3 | `0x421354` | Normal attack appends cmd 114 (Freeze) @ 0.18f |
| 157 (`0x09d`) | Normal attacks may inflict paralysis | `0x2a` | No | No | 9 | `0x4213a5` | Normal attack appends cmd 115 (Paralysis) @ 0.15f |
| 158 (`0x09e`) | Normal attacks may inflict stun | `0x2a` | No | No | 12 | `0x4213f6` | Normal attack appends cmd 118 (Stun) @ 0.12f |
| 159 (`0x09f`) | Normal attacks may inflict petrification | `0x2a` | No | No | 4 | `0x421447` | Normal attack appends cmd 120 (Petrification) @ 0.10f |
| 160 (`0x0a0`) | Normal attacks may instakill | `0x2a` | No | No | 10 | `0x421498` | Normal attack appends cmd 119 (Instakill) @ 0.07f (blocks 197 if both present) |
| 161 (`0x0a1`) | Normal attacks absorb lots of HP | `0x22` | No | No | 4 | `0x421550` | Normal attack appends cmd 75 (HP Drain) @ 0.50f (blocked vs Undead species 5) |
| 162 (`0x0a2`) | Normal attacks absorb HP | `0x2a` | No | No | 7 | `0x4215a5` | Normal attack appends cmd 75 (HP Drain) @ 0.15f (if cmd 75 absent; blocked vs species 5) |
| 163 (`0x0a3`) | Normal attacks absorb lots of TP | `0x22` | No | No | 5 | `0x4215fa` | Normal attack appends cmd 76 (TP Drain) @ 0.20f (blocked vs Undead species 5) |
| 164 (`0x0a4`) | Normal attacks absorb TP | `0x2a` | No | No | 11 | `0x42164f` | Normal attack appends cmd 76 (TP Drain) @ 0.05f (if cmd 76 absent; blocked vs species 5) |
| 165 (`0x0a5`) | Normal attacks may inflict slow | `0x2a` | No | No | 4 | `0x4216a4` | Normal attack appends cmd 122 (Slow) @ 0.12f |
| 197 (`0x0c5`) | Normal attacks high-chance instakill *(raw ID 197)* | `0x22` | No | No | 2 | `0x4214e9` | Normal attack appends cmd 119 (Instakill) @ 0.75f (if cmd 119 absent) |

#### 7. Weapon Element Imbue & Elemental Magic Buff Enchants (10 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 78 (`0x04e`) | Fire magic buff | `0x2a` | No | No | 10 | `0x41620d, 0x44e04b, 0x44e082` | Imbue normal attacks with Fire (under 325..329); Fire magic power +0.20f/stack |
| 79 (`0x04f`) | Water magic buff | `0x2a` | No | No | 11 | `0x41651d, 0x44e101, 0x44e138` | Imbue normal attacks with Water (under 325..329); Water magic power +0.20f/stack |
| 80 (`0x050`) | Wind magic buff | `0x2a` | No | No | 8 | `0x41682d, 0x44e1b7, 0x44e1ee` | Imbue normal attacks with Wind (under 325..329); Wind magic power +0.20f/stack |
| 81 (`0x051`) | Earth magic buff | `0x2a` | No | No | 4 | `0x416b3d, 0x44e26d, 0x44e2a4` | Imbue normal attacks with Earth (under 325..329); Earth magic power +0.20f/stack |
| 82 (`0x052`) | Lightning magic buff | `0x2a` | No | No | 8 | `0x416e4d, 0x44e37d, 0x44e3b4` | Imbue normal attacks with Lightning (under 325..329); Lightning magic power +0.20f/stack |
| 251 (`0x0fb`) | Fire attack for both sides UP | `0xe0` | No | Yes | 0 | `0x44c3ce, 0x44e0bc` | Fire attack damage +0.20f (both attacker & defender checked) |
| 252 (`0x0fc`) | Water attack for both sides UP | `0xe0` | No | Yes | 0 | `0x44c3f4, 0x44e172` | Water attack damage +0.20f (both attacker & defender checked) |
| 253 (`0x0fd`) | Wind attack for both sides UP | `0xe0` | No | Yes | 0 | `0x44c417, 0x44e228` | Wind attack damage +0.20f (both attacker & defender checked) |
| 254 (`0x0fe`) | Earth attack for both sides UP | `0xe0` | No | Yes | 0 | `0x44c43a, 0x44e2de` | Earth attack damage +0.20f (both attacker & defender checked) |
| 255 (`0x0ff`) | Lightning attack for both sides UP | `0xe0` | No | Yes | 0 | `0x44c45d, 0x44e3ee` | Lightning attack damage +0.20f (both attacker & defender checked) |

#### 8. Turn-Start, Defend, Damage-to-TP & Post-Battle Recovery Enchants (13 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 72 (`0x048`) | Convert received damage into TP | `0xad` | Yes | Yes | 43 | `0x47e68d` | Damage-to-TP rate += 0.05f/stack (combined with 73 capped at 0.50f; min 1 TP) |
| 73 (`0x049`) | Convert received damage into big TP | `0xad` | Yes | Yes | 3 | `0x47e6be` | Damage-to-TP rate += 0.10f/stack (combined with 72 capped at 0.50f; raises min to 5 TP) |
| 144 (`0x090`) | HP recovery every turn | `0xad` | Yes | Yes | 56 | `0x437bcc` | Turn-start HP += max(4, trunc0(f32(MaxHP) * 0.04f * stacks)) |
| 145 (`0x091`) | Slight HP recovery every turn | `0xad` | Yes | Yes | 12 | `0x437c36` | Turn-start HP += max(2, trunc0(f32(MaxHP) * 0.02f * stacks)) |
| 146 (`0x092`) | TP recovery every turn | `0xad` | Yes | Yes | 66 | `0x437d8a` | Turn-start TP += 4 * stacks (flat) |
| 147 (`0x093`) | Slight TP recovery every turn | `0xad` | Yes | Yes | 16 | `0x437da4` | Turn-start TP += 2 * stacks (flat) |
| 148 (`0x094`) | Large HP recovery every turn | `0xad` | Yes | Yes | 5 | `0x437ca0` | Turn-start HP += max(10, trunc0(f32(MaxHP) * 0.08f * stacks)) |
| 149 (`0x095`) | Large TP recovery every turn | `0xad` | Yes | Yes | 6 | `0x437dbc` | Turn-start TP += 6 * stacks (flat) |
| 193 (`0x0c1`) | Fully recover HP after battle | `0xa4` | No | Yes | 6 | `0x43d868` | Post-battle alive HP recovery rate overridden to 1.00f (100% MaxHP) |
| 194 (`0x0c2`) | Fully recover TP after battle | `0xa4` | No | Yes | 6 | `0x43d90e` | Post-battle alive TP recovery rate overridden to 1.00f (100% MaxTP) |
| 257 (`0x101`) | HP recovers while defending | `0xe0` | No | Yes | 1 | `0x4197b7` | On Defend: heal max(10, trunc0(f32(MaxHP) * 0.20f)) HP |
| 292 (`0x124`) | TP recovers slightly while defending | `0xe0` | No | Yes | 1 | `0x41984c` | On Defend: recover max(5, trunc0(f32(MaxTP) * 0.10f)) TP |
| 296 (`0x128`) | May rarely recover all HP when turn starts | `0xe0` | No | Yes | 1 | `0x437d0a` | Turn-start: if Rand(100) < 4, HP += MaxHP (1 RNG draw) |

#### 9. Combat Offense, Defense, Accuracy & Evasion Enchants (22 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 29 (`0x01d`) | Physical attack UP | `0xbb` | Yes | Yes | 44 | `0x44b69a` | Physical ATK bonus += 4 * stacks |
| 30 (`0x01e`) | Physical attack MiniUP | `0xbb` | Yes | Yes | 4 | `0x44b6d4` | Physical ATK bonus += 2 * stacks |
| 31 (`0x01f`) | Physical accuracy UP | `0xbf` | Yes | Yes | 70 | `0x44ad18` | Physical ACC bonus += 4 * stacks |
| 32 (`0x020`) | Physical accuracy MiniUP | `0xbf` | Yes | Yes | 12 | `0x44ad52` | Physical ACC bonus += 2 * stacks |
| 33 (`0x021`) | Physical defense UP | `0xbd` | Yes | Yes | 50 | `0x44b8eb` | Physical DEF bonus += 4 * stacks |
| 34 (`0x022`) | Physical defense MiniUP | `0xbd` | Yes | Yes | 11 | `0x44b925` | Physical DEF bonus += 2 * stacks |
| 35 (`0x023`) | Physical evasion UP | `0xbf` | Yes | Yes | 68 | `0x44ad91` | Physical EVA bonus += 4 * stacks |
| 36 (`0x024`) | Physical evasion MiniUP | `0xbf` | Yes | Yes | 9 | `0x44adcb` | Physical EVA bonus += 2 * stacks |
| 37 (`0x025`) | Magic attack UP | `0xbb` | Yes | Yes | 29 | `0x44df30` | Magic INT bonus += 4 * stacks |
| 38 (`0x026`) | Magic attack MiniUP | `0xbb` | Yes | Yes | 3 | `0x44df6a` | Magic INT bonus += 2 * stacks |
| 39 (`0x027`) | Magic accuracy UP | `0xbf` | Yes | Yes | 19 | `0x44d656` | Magic ACC bonus += 3 * stacks |
| 40 (`0x028`) | Magic accuracy MiniUP | `0xbf` | Yes | Yes | 4 | `0x44d690` | Magic ACC bonus += 1.5f * stacks |
| 41 (`0x029`) | Magic defense UP | `0xbd` | Yes | Yes | 34 | `0x44e58c` | Magic RES bonus += 4 * stacks |
| 42 (`0x02a`) | Magic defense MiniUP | `0xbd` | Yes | Yes | 5 | `0x44e5c6` | Magic RES bonus += 2 * stacks |
| 43 (`0x02b`) | Magic evasion UP | `0xbf` | Yes | Yes | 33 | `0x44d6cb` | Magic EVA bonus += 3 * stacks |
| 44 (`0x02c`) | Magic evasion MiniUP | `0xbf` | Yes | Yes | 5 | `0x44d71c` | Magic EVA bonus += 1.5f * stacks |
| 66 (`0x042`) | Received physical damage DOWN | `0xad` | Yes | Yes | 49 | `0x44bb79` | Received physical damage mult -= 0.10f * stacks |
| 67 (`0x043`) | Received physical damage MiniDOWN | `0xad` | Yes | Yes | 8 | `0x44bbb7` | Received physical damage mult -= 0.05f * stacks |
| 68 (`0x044`) | Received magic damage DOWN | `0xad` | Yes | Yes | 36 | `0x44e732` | Received magic damage mult -= 0.10f * stacks |
| 69 (`0x045`) | Received magic damage MiniDOWN | `0xad` | Yes | Yes | 6 | `0x44e76b` | Received magic damage mult -= 0.05f * stacks |
| 70 (`0x046`) | Received damage DOWN | `0xad` | Yes | Yes | 27 | `0x44bbf2, 0x44e7a6` | Received all damage mult -= 0.08f * stacks |
| 71 (`0x047`) | Received damage MiniDOWN | `0xad` | Yes | Yes | 7 | `0x44bc2d, 0x44e7e1` | Received all damage mult -= 0.04f * stacks |

#### 10. Crit, Speed, Chant, Aggro & Interrupt Enchants (19 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 45 (`0x02d`) | Critical rate UP | `0xbb` | Yes | Yes | 66 | `0x44f424` | Crit rate += 4.0f * stacks |
| 46 (`0x02e`) | Critical rate MiniUP | `0xbb` | Yes | Yes | 8 | `0x44f45e` | Crit rate += 2.0f * stacks |
| 47 (`0x02f`) | Enemy critical rate DOWN | `0xbd` | Yes | Yes | 44 | `0x44f4eb` | Enemy crit rate vs wearer -= 4.0f * stacks |
| 48 (`0x030`) | Enemy critical rate MiniDOWN | `0xbd` | Yes | Yes | 5 | `0x44f525` | Enemy crit rate vs wearer -= 2.0f * stacks |
| 49 (`0x031`) | Enmity UP | `0xbf` | Yes | Yes | 56 | `0x44a72d` | Target aggro weight += 10 * stacks |
| 50 (`0x032`) | Enmity DOWN | `0xbf` | Yes | Yes | 34 | `0x44a761` | Target aggro weight -= 5 * stacks |
| 51 (`0x033`) | Speed UP | `0xbf` | Yes | Yes | 95 | `0x44a14a` | ATB speed factor += 0.06f * stacks |
| 52 (`0x034`) | Speed MiniUP | `0xbf` | Yes | Yes | 24 | `0x44a182` | ATB speed factor += 0.03f * stacks |
| 53 (`0x035`) | Speed DOWN | `0xbf` | Yes | Yes | 15 | `0x44a1ba` | ATB speed factor -= 0.06f * stacks |
| 54 (`0x036`) | Chant speed UP | `0xbf` | Yes | Yes | 62 | `0x44a24f` | Chant speed factor += 0.06f * stacks |
| 55 (`0x037`) | Chant speed MiniUP | `0xbf` | Yes | Yes | 8 | `0x44a289` | Chant speed factor += 0.03f * stacks |
| 56 (`0x038`) | Chant speed DOWN | `0xbf` | Yes | Yes | 11 | `0x44a2c3` | Chant speed factor -= 0.06f * stacks |
| 57 (`0x039`) | Interruption rate GrandDOWN | `0x1ad` | Yes | Yes | 16 | `0x44d083` | Chant interrupt rate -= 0.10f * stacks |
| 58 (`0x03a`) | Interruption rate DOWN | `0xbd` | Yes | Yes | 31 | `0x44d0bd` | Chant interrupt rate -= 0.06f * stacks |
| 59 (`0x03b`) | Interruption rate MiniDOWN | `0xbd` | Yes | Yes | 14 | `0x44d0f4` | Chant interrupt rate -= 0.03f * stacks |
| 60 (`0x03c`) | Interruption rate UP | `0xbd` | Yes | Yes | 3 | `0x44d12b` | Chant interrupt rate += 0.06f * stacks |
| 61 (`0x03d`) | Interruption rate MegaDOWN | `0x1ad` | Yes | Yes | 1 | `0x44d166` | Chant interrupt rate -= 0.20f * stacks |
| 268 (`0x10c`) | Critical rate UP | `0xe0` | No | Yes | 1 | `0x44f4b9` | Raises crit rate floor from 5.0f to 20.0f |
| 298 (`0x12a`) | Magic incantations go very fast... sometimes | `0xe0` | No | Yes | 1 | `0x44a35e` | Chant start gauge += 0.25f (capped 0.92f); Rand(10) < 10 always triggers (1 RNG draw) |

#### 11. Species Slayer & Species Damage Reduction Enchants (43 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 170 (`0x0aa`) | Physical attack vs. Demons GrandUP | `0x22` | No | No | 9 | `0x44bfbb` | Phys dmg vs Demons += 0.30f * stacks |
| 171 (`0x0ab`) | Physical attack vs. Demons UP | `0x2a` | No | No | 4 | `0x44bff5` | Phys dmg vs Demons += 0.15f * stacks |
| 172 (`0x0ac`) | Physical attack vs. Apparitions GrandUP | `0x22` | No | No | 9 | `0x44c06f` | Phys dmg vs Apparitions += 0.30f * stacks |
| 173 (`0x0ad`) | Physical attack vs. Apparitions UP | `0x2a` | No | No | 2 | `0x44c0a9` | Phys dmg vs Apparitions += 0.15f * stacks |
| 174 (`0x0ae`) | Phys. attack vs. Magic Beings GrandUP | `0x22` | No | No | 3 | `0x44c0ce` | Phys dmg vs Magic Beings += 0.30f * stacks |
| 175 (`0x0af`) | Physical attack vs. Magic Beings UP | `0x2a` | No | No | 2 | `0x44c108` | Phys dmg vs Magic Beings += 0.15f * stacks |
| 176 (`0x0b0`) | Physical attack vs. Humans MegaUP | `0x22` | No | No | 4 | `0x44c131` | Phys dmg vs Humans += 0.60f * stacks |
| 177 (`0x0b1`) | Physical attack vs. Humans GrandUP | `0x22` | No | No | 6 | `0x44c16b` | Phys dmg vs Humans += 0.30f * stacks |
| 178 (`0x0b2`) | Physical attack vs. Humans UP | `0x2a` | No | No | 4 | `0x44c1a5` | Phys dmg vs Humans += 0.15f * stacks |
| 179 (`0x0b3`) | Physical attack vs. Undead GrandUP | `0x22` | No | No | 2 | `0x44c1e5` | Phys dmg vs Undead += 0.30f * stacks |
| 180 (`0x0b4`) | Physical attack vs. Undead UP | `0x2a` | No | No | 2 | `0x44c21f` | Phys dmg vs Undead += 0.15f * stacks |
| 181 (`0x0b5`) | Physical attack vs. Dragons GrandUP | `0x22` | No | No | 5 | `0x44c244` | Phys dmg vs Dragons += 0.30f * stacks |
| 182 (`0x0b6`) | Physical attack vs. Dragons UP | `0x2a` | No | No | 1 | `0x44c27e` | Phys dmg vs Dragons += 0.15f * stacks |
| 183 (`0x0b7`) | Physical attack vs. Beasts GrandUP | `0x22` | No | No | 4 | `0x44c2a3` | Phys dmg vs Beasts += 0.30f * stacks |
| 184 (`0x0b8`) | Physical attack vs. Beasts UP | `0x2a` | No | No | 4 | `0x44c2dd` | Phys dmg vs Beasts += 0.15f * stacks |
| 185 (`0x0b9`) | Physical attack vs. Fruit MegaUP | `0x22` | No | No | 1 | `0x44c302` | Phys dmg vs Fruit += 1.00f * stacks |
| 186 (`0x0ba`) | Physical attack vs. Fruit GrandUP | `0x2a` | No | No | 3 | `0x44c334` | Phys dmg vs Fruit += 0.50f * stacks |
| 196 (`0x0c4`) | Physical attack vs. Felines MegaUP | `0x22` | No | No | 2 | `0x44c370` | Phys dmg vs Felines += 1.00f * stacks (shared at 0x44c38d) |
| 203 (`0x0cb`) | Physical attack vs. Demons MegaUP | `0x22` | No | No | 4 | `0x44c02f` | Phys dmg vs Demons += 0.60f * stacks |
| 204 (`0x0cc`) | Physical attack vs. Apparitions MegaUP | `0x22` | No | No | 1 | `0x44c0af` | Phys dmg vs Apparitions += 0.60f * stacks (shared at 0x44c000) |
| 205 (`0x0cd`) | Phys. attack vs. Magic Beings MegaUP | `0x22` | No | No | 4 | `0x44c10e` | Phys dmg vs Magic Beings += 0.60f * stacks (shared at 0x44c000) |
| 206 (`0x0ce`) | Physical attack vs. Undead MegaUP | `0x22` | No | No | 1 | `0x44c225` | Phys dmg vs Undead += 0.60f * stacks (shared at 0x44c000) |
| 207 (`0x0cf`) | Physical attack vs. Dragons MegaUP | `0x22` | No | No | 2 | `0x44c284` | Phys dmg vs Dragons += 0.60f * stacks (shared at 0x44c000) |
| 208 (`0x0d0`) | Physical attack vs. Beasts MegaUP | `0x22` | No | No | 1 | `0x44c2e3` | Phys dmg vs Beasts += 0.60f * stacks (shared at 0x44c000) |
| 209 (`0x0d1`) | Phys. attack vs. Sea Creatures MegaUP | `0x22` | No | No | 7 | `0x44c383` | Phys dmg vs Sea Creatures += 1.00f * stacks (shared at 0x44c38d) |
| 227 (`0x0e3`) | Damage from Demons 5% DOWN | `0xa0` | No | Yes | 0 | `0x44bd5e` | Dmg from Demons -= 0.05f |
| 228 (`0x0e4`) | Damage from Demons 10% DOWN | `0xa0` | No | Yes | 0 | `0x44bd64` | Dmg from Demons -= 0.10f (shared at 0x44bea4) |
| 229 (`0x0e5`) | Damage from Apparitions 5% DOWN | `0xa0` | No | Yes | 0 | `0x44bd86` | Dmg from Apparitions -= 0.05f |
| 230 (`0x0e6`) | Damage from Apparitions 10% DOWN | `0xa0` | No | Yes | 0 | `0x44bd8c` | Dmg from Apparitions -= 0.10f (shared at 0x44bea4) |
| 231 (`0x0e7`) | Damage from Magic Beings 5% DOWN | `0xa0` | No | Yes | 0 | `0x44bdae` | Dmg from Magic Beings -= 0.05f |
| 232 (`0x0e8`) | Damage from Magic Beings 10% DOWN | `0xa0` | No | Yes | 0 | `0x44bdb4` | Dmg from Magic Beings -= 0.10f (shared at 0x44bea4) |
| 233 (`0x0e9`) | Damage from Humans 5% DOWN | `0xa0` | No | Yes | 0 | `0x44bdd6` | Dmg from Humans -= 0.05f |
| 234 (`0x0ea`) | Damage from Humans 10% DOWN | `0xa0` | No | Yes | 0 | `0x44bddc` | Dmg from Humans -= 0.10f (shared at 0x44bea4) |
| 235 (`0x0eb`) | Damage from Undead 5% DOWN | `0xa0` | No | Yes | 0 | `0x44bdfe` | Dmg from Undead -= 0.05f |
| 236 (`0x0ec`) | Damage from Undead 10% DOWN | `0xa0` | No | Yes | 0 | `0x44be04` | Dmg from Undead -= 0.10f (shared at 0x44bea4) |
| 237 (`0x0ed`) | Damage from Dragons 5% DOWN | `0xa0` | No | Yes | 0 | `0x44be26` | Dmg from Dragons -= 0.05f |
| 238 (`0x0ee`) | Damage from Dragons 10% DOWN | `0xa0` | No | Yes | 0 | `0x44be2c` | Dmg from Dragons -= 0.10f (shared at 0x44bea4) |
| 239 (`0x0ef`) | Damage from Beasts 5% DOWN | `0xa0` | No | Yes | 0 | `0x44be4b` | Dmg from Beasts -= 0.05f |
| 240 (`0x0f0`) | Damage from Beasts 10% DOWN | `0xa0` | No | Yes | 0 | `0x44be51` | Dmg from Beasts -= 0.10f (shared at 0x44bea4) |
| 241 (`0x0f1`) | Damage from Fruit 5% DOWN | `0xa0` | No | Yes | 0 | `0x44be70` | Dmg from Fruit -= 0.05f |
| 242 (`0x0f2`) | Damage from Fruit 10% DOWN | `0xa0` | No | Yes | 0 | `0x44be76` | Dmg from Fruit -= 0.10f (shared at 0x44bea4) |
| 243 (`0x0f3`) | Damage from Therians 5% DOWN | `0xa0` | No | Yes | 0 | `0x44be99` | Dmg from Therians -= 0.05f |
| 244 (`0x0f4`) | Damage from Therians 10% DOWN | `0xa0` | No | Yes | 0 | `0x44beda` | Dmg from Therians -= 0.10f |

#### 12. Conditional, Joint, Missed-Spell & Escape Enchants (9 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 219 (`0x0db`) | Attack vs. high lvl enemies UP | `0xe0` | No | Yes | 1 | `0x44ca0b` | If target.Lv > attacker.Lv: phys dmg mult += 0.10f * stacks |
| 220 (`0x0dc`) | Attack vs. low lvl enemies UP | `0xe0` | No | Yes | 1 | `0x44ca60` | If target.Lv < attacker.Lv: phys dmg mult += 0.10f * stacks |
| 261 (`0x105`) | Damage of joint skills UP | `0xe0` | No | Yes | 0 | `0x44c8b4` | Joint skill damage mult += 0.10f * stacks |
| 262 (`0x106`) | Escape probability UP | `0xe0` | No | Yes | 1 | `0x41ae6e` | Escape probability floor raised from 0.20f to 0.50f |
| 267 (`0x10b`) | The smaller your party, the higher your damage | `0xe0` | No | Yes | 1 | `0x44c92e` | Phys dmg mult += (5 - partyCount) * 0.10f * stacks |
| 271 (`0x10f`) | When max HP, damage inflicted 10% UP | `0xe0` | No | Yes | 1 | `0x44c9b6` | If CurHP == MaxHP: phys dmg mult += 0.10f * stacks |
| 272 (`0x110`) | Reduce damage penalty for missed spells | `0xe0` | No | Yes | 1 | `0x44ee3d` | Missed spell graze: (dmg * 3) / 4 instead of dmg / 2 |
| 280 (`0x118`) | Damage to enemies with status ailments UP | `0xe0` | No | Yes | 1 | `0x44cd61` | If target HasTrueAilment (vtable+0x7c): phys dmg += trunc0(f32(dmg) * 0.15f) |
| 290 (`0x122`) | Joint skill damage MegaUP | `0xe0` | No | Yes | 1 | `0x44c8ee` | Joint skill damage mult += 0.20f * stacks |

#### 13. TP Cost, Performance, Doll, Unarmed & Skill-Level Enchants (13 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 246 (`0x0f6`) | TP Cost for techniques DOWN | `0xe0` | No | Yes | 1 | `0x4fd296` | Technique TP cost = trunc0(f32(cost) * 0.80f) |
| 247 (`0x0f7`) | TP Cost for techniques MegaDOWN | `0xe0` | No | Yes | 0 | `0x4fd2b3` | Technique TP cost = trunc0(f32(cost) * 0.60f) (multiplicative with 246) |
| 248 (`0x0f8`) | TP Cost for spells DOWN | `0xe0` | No | Yes | 1 | `0x4fd2e7` | Spell TP cost = trunc0(f32(cost) * 0.80f) |
| 249 (`0x0f9`) | TP Cost for spells MegaDOWN | `0xe0` | No | Yes | 0 | `0x4fd30d` | Spell TP cost = trunc0(f32(cost) * 0.60f) (multiplicative with 248) |
| 263 (`0x107`) | A-rank speed when no weapon is equipped | `0xe0` | No | Yes | 1 | `0x4f55ab` | Unarmed weapon rank forced to rank 1 (A-rank speed multiplier) |
| 264 (`0x108`) | Class weapon modifier 2% UP | `0xe0` | No | Yes | 1 | `0x4f7fc1` | Class weapon modifier += 0.02f (boolean) |
| 293 (`0x125`) | Unique skill level +1 | `0xe0` | No | Yes | 1 | `0x4f4de1, 0x4f7173, 0x4f72fe` | Unique skill level +1 when learned level in 1..8 (max 9) |
| 300 (`0x12c`) | Song skill efficacy UP | `0x1ad` | Yes | Yes | 5 | `0x48c02c` | Song efficacy += 0.02f/stack (combined with 301 capped at 0.05f) |
| 301 (`0x12d`) | Song skill efficacy MiniUP | `0xa1` | Yes | Yes | 15 | `0x48c032` | Song efficacy += 0.01f/stack (combined with 300 capped at 0.05f) |
| 302 (`0x12e`) | Dance skill efficacy UP | `0x1ad` | Yes | Yes | 2 | `0x48c04a` | Dance efficacy += 0.02f/stack (combined with 303 capped at 0.05f) |
| 303 (`0x12f`) | Dance skill efficacy UP | `0xa1` | Yes | Yes | 16 | `0x48c07e` | Dance efficacy += 0.01f/stack (combined with 302 capped at 0.05f) |
| 304 (`0x130`) | Doll skill efficacy UP | `0x1ad` | Yes | Yes | 1 | `0x44b533, 0x44ddde, 0x48d7d8` | Doll efficacy += 0.02f/stack (combined with 305 capped at 0.05f) |
| 305 (`0x131`) | Doll skill efficacy MiniUP | `0xa1` | Yes | Yes | 11 | `0x44b568, 0x44de13, 0x48d80d` | Doll efficacy += 0.01f/stack (combined with 304 capped at 0.05f) |

#### 14. EXP, Drop & Pep Enchants (8 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 195 (`0x0c3`) | Pep is fixed at the max value | `0x24` | No | No | 5 | `0x4f6a56` | Fix Pep to 130.0f (highest priority over 200 and 201) |
| 200 (`0x0c8`) | Pep will not drop below 100 | `0x2a` | No | No | 10 | `0x4f6a2b` | Clamp Pep floor to 100.0f (overrides 201) |
| 201 (`0x0c9`) | Pep is fixed at the minimum value | `0x10c` | No | No | 5 | `0x4f6a0e` | Fix Pep to 70.0f (overridden by 200 and 195) |
| 266 (`0x10a`) | Pep decrease rate DOWN | `0xe0` | No | Yes | 1 | `0x509844` | Pep decay delta *= 0.50f |
| 270 (`0x10e`) | Gain more EXP from higher-level enemies | `0xe0` | No | Yes | 1 | `0x450768` | Underdog EXP mults vs higher-level enemy: 1.15f / 1.30f / 1.50f / 1.75f |
| 275 (`0x113`) | Double EXP | `0xa4` | No | Yes | 2 | `0x445a1e` | Post-battle EXP x2 (doubles final EXP in CBattleResult::_Initialize) |
| 276 (`0x114`) | Equipment drop rate UP | `0x1ac` | No | Yes | 1 | `0x558255` | Equipment drop rate bonus += 20 * stacks |
| 294 (`0x126`) | Food likes and dislikes intensify | `0xe0` | No | Yes | 1 | `0x509a6d, 0x509bbd` | Intensifies food like/dislike Pep delta |

#### 15. Field, Dungeon, Trap & Mercenary Buddy Enchants (13 IDs)

| ID (Hex) | Name (`EnchantData.pck`) | Flags | Stacks (`&1`) | Offhand (`&0x80`) | Vanilla Uses | Binary VA(s) | Exact Binary Formula / Behavior |
|---|---|---|---:|---:|---:|---|---|
| 192 (`0x0c0`) | Enemy HP and abilities are viewable | `0xa4` | No | Yes | 5 | `0x4e4d9a` | Party-wide (alive member): reveals enemy HP and abilities |
| 211 (`0x0d3`) | Slightly reduce encounter rate | `0xe0` | No | Yes | 0 | `0x4bc809, 0x5563cb` | Party-wide (0x4e4f50): dungeon encounter step delta -1 |
| 212 (`0x0d4`) | Greatly reduce encounter rate | `0xe0` | No | Yes | 1 | `0x4bc81a, 0x5563dd` | Party-wide (0x4e4f50): dungeon encounter step delta -2 |
| 213 (`0x0d5`) | Slightly increase encounter rate | `0xe0` | No | Yes | 0 | `0x4bc82b, 0x5563ee` | Party-wide (0x4e4f50): dungeon encounter step delta +1 |
| 214 (`0x0d6`) | Greatly increase encounter rate | `0xe0` | No | Yes | 1 | `0x4bc83a, 0x5563fd` | Party-wide (0x4e4f50): dungeon encounter step delta +2 |
| 216 (`0x0d8`) | Recover 1 TP every 10 steps | `0xe0` | No | Yes | 0 | `0x4fb72c` | Dungeon walking: recover +1 TP every 10 steps |
| 217 (`0x0d9`) | Recover 3 TP every 10 steps | `0xe0` | No | Yes | 1 | `0x4fb7c6` | Dungeon walking: recover +3 TP every 10 steps |
| 258 (`0x102`) | Higher lvl equipment from treasure boxes | `0xe0` | No | Yes | 1 | `0x5558d0, 0x555a3d` | Party-wide (0x4e4f50): higher-level equipment in treasure boxes |
| 259 (`0x103`) | Higher chance of shop encounters | `0xe0` | No | Yes | 1 | `0x4c625a, 0x5563a7, 0x560a02` | Party-wide (0x4e4f50): shop encounter threshold 50 -> 25 |
| 260 (`0x104`) | Damage from non-gas traps 90% DOWN | `0xe0` | No | Yes | 1 | `0x4c46b8` | Party-wide (0x4e4f50): non-gas trap damage = trunc0(f32(dmg) * 0.10f) |
| 291 (`0x123`) | Increase Mimic appearance rate in chests | `0xe0` | No | Yes | 1 | `0x555771` | Party-wide (0x4e4f50): chest Mimic rate += 20 percentage points |
| 295 (`0x127`) | Increase Mercenary Buddy stats by 10% | `0xe0` | No | Yes | 0 | `0x4ff638` | Party-wide (0x4e4f50): Guest NPC ATK..AGI += -trunc0(f32(stat) * -0.10f) (+10%) |
| 297 (`0x129`) | Increase Mercenary Buddy stats by 30 | `0xe0` | No | Yes | 1 | `0x4fecc5` | Party-wide (0x4e4f50): Guest NPC base ATK..AGI each +30 |

- **Program Evidence:**
```asm
004f5474  mov      edi, dword ptr [esp + 0x14]
004f5487  mov      ecx, dword ptr [0x7389d0]
004f548e  call     0x507310
004f5499  mov      bl, byte ptr [eax + 0x38]
004f54a2  and      bl, 1
004f54b4  cmp      edi, dword ptr [eax]
004f54b8  inc      edx
004f54bb  je       0x4f54c5
004f6334  cmp      dword ptr [esp + 0x10], 1
004f635c  cmp      dword ptr [eax + 0x38], 0
004f637d  mov      eax, dword ptr [eax + 0x38]
004f6380  shr      eax, 7
004f6383  test     al, 1
004f8311  test     byte ptr [eax + 0x38], 1
004e4f84  call     dword ptr [edx + 0xf0]
004d4dd0  xor      eax, eax
```
