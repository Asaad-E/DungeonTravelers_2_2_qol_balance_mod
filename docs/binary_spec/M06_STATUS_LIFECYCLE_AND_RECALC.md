# M06 — Status Lifecycle, Vtable Flag Matrix, Stat/Resistance Recalculation, Dispel, Countdown, and Performance Groups

Clean-room binary specification of `CGameStatusBase` (`vtable 0x6d4104`), `CCommandBase` / `CCommandTurnBase` (`0x6d119c` / `0x6d130c`), stat/resistance recalculation, status expiry/dispel/cure, and performance groups in `DT22_en_unwrapped.vanilla.exe` (x86-32, PE imagebase `0x00400000`).

> **Scope & Conventions:**
> - All arithmetic widths are explicit (`i32`, `u32`, `f32`, `f64`, `bool`). `trunc0(x)` denotes truncation toward zero (`cvttss2si` or `_ftol2_sse` at `0x61d550`, or `cdq; sub eax, edx; sar eax, 1` for integer `/ 2`). `round_f32_to_i32(x)` denotes `0x61e650` (`fld / fistp` round-to-nearest-even).
> - `CGameStatusBase` core offsets: `+0x0c CurHP`, `+0x10 MaxHP`, `+0x14 CurTP`, `+0x18 MaxTP`, `+0x1c..+0x30 RawStat[0..5]` (`0=ATK, 1=DEF, 2=INT, 3=RES, 4=DEX, 5=AGI`), `+0x34..+0x50 RawResist[0..7]`, `+0x54..+0x68 EffStat[0..5]`, `+0x6c..+0x88 EffResist[0..7]`, `+0x8c..+0x94 std::vector<CCommand*> StatusList`, `+0x98 i32 MaxHPDelta`.
> - Resistance index order across `RawResist`/`EffResist` (`vt+0x30`/`vt+0x34` indices `6..13`, offsets `+0x6c..+0x88`): `6=Slash`, `7=Stab`, `8=Bash`, `9=Fire`, `10=Water`, `11=Wind`, `12=Earth`, `13=Lightning`.
> - Ailment command IDs (verified from `backups/CommandData.pck` and `0x4fb570..0x4fb650`): `113 (0x71)=Poison`, `114 (0x72)=Freeze`, `115 (0x73)=Paralysis`, `116 (0x74)=Sleep`, `117 (0x75)=Silence`, `118 (0x76)=Stun`, `119 (0x77)=Instakill`, `120 (0x78)=Petrification`, `121 (0x79)=Special Petrification`, `122 (0x7a)=Slow`, `123 (0x7b)=Instant Death`.

---

### M06.01 `CGameStatusBase::AddStatus`, Removal, and Status Wipe

**Binary VA(s):**
- `0x4f9930..0x4fa609` (`CGameStatusBase::AddStatus`, `vt+0x5c`)
- `0x4fa610..0x4fa68f` (`RemoveStatusById`, `vt+0x64` / `RemoveStatusByPtr`, `vt+0x68`)
- `0x4fa690..0x4fa86c` (`RemoveStatusByIndex`, `vt+0x6c`)
- `0x4fa870..0x4fa95a` (`ClearStatuses(clearPetrify, clearSkills)`, `vt+0x74`)
- `0x4fa960..0x4fab46` (`ClearBattleStatusesOnEnd`, `vt+0x78`)
- `0x4fc890..0x4fc9a4` (`CGameStatusBase::OnDeathCleanup`, `vt+0x114`)
- `0x4f5fa0..0x4f60bf` (`CGamePlayerStatus::OnDeathCleanup`, `vt+0x114`)
- `0x4fc9b0..0x4fcb00` (`StatusList` sort comparator)

**Calls:**
- `vt+0xc8` (`0x4fb610` `HasFullPetrify_120`: returns `true` iff `120` is present with `stage >= 3`)
- `vt+0xa8` (`0x4fb470` `GetWeaponEnchants`), `vt+0xac` (`0x4fb4f0` `GetBarriers`), `vt+0x64` (`RemoveStatusById`), `vt+0x68` (`RemoveStatusByPtr`)
- `0x43bdd0` (`AddSongCommand`), `0x43c2a0` (`AddDanceCommand`), `0x43c790` (`AddPuppetCommand`), `0x43cb80` (`AddGeassCommand`)
- `0x43bc50` (`CancelChant`), `0x43c110` (`CancelSong`), `0x43c600` (`CancelDance`), `0x43c9b0` (`CancelPuppet`), `0x43ce30` (`CancelGeass`), `0x43d2c0` (`DestroyOwnedDolls`)
- `0x43cfb0` (`ResyncAllyPerformancesOnPetrifyCure`), `vt+0x108` (`RecalculateAll`)

**CalledBy:**
- `CCommand::Execute` (`0x47e500`), `CBattleBase::AddSongCommand` (`0x43bdd0`), `AddDanceCommand` (`0x43c2a0`), `AddGeassCommand` (`0x43cb80`), `0x43cfb0`, battle end (`0x4391a0`), and death hooks (`0x4f5fa0`/`0x4fc890`).

**Typed Pseudocode:**
```text
fn CGameStatusBase::AddStatus(this, cmd: CCommand*, recalcFlag: bool) -> CCommand*:
    // 1. Full Petrify (120, stage >= 3) blocks ALL new statuses
    if this->vt_0xc8_HasFullPetrify_120():
        return null

    cmdId: i32 = cmd->vt_0x24_GetCommandId()
    battle: CBattleBase* = dynamic_cast<CBattleBase*>(g_SceneMgr[0x71fbdc]->curScene)

    // 2. Same-effect deduplication (0x4f9b72..0x4f9bfc)
    shouldAppend: bool = true
    for i in 0 .. this.StatusList.len - 1:
        if this.StatusList[i]->GetCommandId() == cmdId:
            if cmdId == 120 (0x78):
                stage: u32 = dynamic_cast<CCommand_0120*>(cmd)->vt_0xb0_GetStage()
                if stage < 3:
                    // Partial petrify does NOT overwrite an existing petrify entry
                    shouldAppend = false
                    break
            delete this.StatusList[i]
            this.StatusList.erase(i)
            break

    if not shouldAppend:
        return null

    // 3. Exclusive vtable groups (0x4f9c02..0x4f9cfb)
    if cmd->vt_0x7c_IsWeaponEnchant():      // IDs 325..329
        for existing in this->vt_0xa8_GetWeaponEnchants():
            this->vt_0x64_RemoveStatusById(existing->GetCommandId())
    if cmd->vt_0x84_IsBarrier():            // IDs 101, 102, 181
        for existing in this->vt_0xac_GetBarriers():
            this->vt_0x64_RemoveStatusById(existing->GetCommandId())

    // 4. Performance-group registration in battle (0x4f9cfc..0x4f9dc0)
    if battle != null:
        if cmd->vt_0x6c_IsSong():    battle->AddSongCommand_0x43bdd0(this, cmd)
        if cmd->vt_0x70_IsDance():   battle->AddDanceCommand_0x43c2a0(this, cmd)
        if cmd->vt_0x74_IsPuppet():  battle->AddPuppetCommand_0x43c790(this, cmd)
        if cmd->vt_0x78_IsGeass():   battle->AddGeassCommand_0x43cb80(this, cmd)

    // 5. Append & sort (0x4fc9b0: cmdId == 120 sorts first, else ascending cmdId)
    this.StatusList.push_back(cmd)
    sort(this.StatusList, cmp_0x4fc9b0)

    // 6. Ailment side-effects & performance-cancel hooks (0x4f9e6f..0x4fa56f)
    if cmdId == 114 (0x72, Freeze):
        if battle != null:
            battle->CancelDance_0x43c600(this)
            battle->CancelPuppet_0x43c9b0(this)
            battle->CancelGeass_0x43ce30(this)
            // Note: Freeze does NOT cancel Song (0x43c110) or Chant (0x43bc50)
    else if cmdId == 116 (0x74, Sleep):
        if battle != null:
            battle->CancelSong_0x43c110(this)
            battle->CancelDance_0x43c600(this)
            battle->CancelPuppet_0x43c9b0(this)
            battle->CancelGeass_0x43ce30(this)
            battle->CancelChant_0x43bc50(this)
        // Strip all active statuses with cmd->vt_0x8c_IsSleepCleared() == true (0x4fa03a)
        for s in this.StatusList (in-place):
            if s->vt_0x8c_IsSleepCleared():
                this->vt_0x68_RemoveStatusByPtr(s)
    else if cmdId == 117 (0x75, Silence):
        if battle != null:
            battle->CancelSong_0x43c110(this)
            battle->CancelChant_0x43bc50(this)
            // Note: Silence does NOT cancel Dance, Puppet, or Geass
    else if cmdId == 118 (0x76, Stun):
        if battle != null:
            battle->CancelSong_0x43c110(this)
            battle->CancelDance_0x43c600(this)
            battle->CancelPuppet_0x43c9b0(this)
            battle->CancelGeass_0x43ce30(this)
            battle->CancelChant_0x43bc50(this)
            unit = battle->FindUnit(this)
            unit.actionGauge_0x08 = 0.0f
            battle->_SortTime(0, 0)
        this->vt_0x64_RemoveStatusById(118) // Stun is transient; never persists
        return null
    else if cmdId == 121 (0x79, Special Petrification):
        if battle != null:
            battle->CancelSong_0x43c110(this)
            battle->CancelDance_0x43c600(this)
            battle->CancelPuppet_0x43c9b0(this)
            battle->CancelGeass_0x43ce30(this)
            battle->CancelChant_0x43bc50(this)
        this->ClearStatuses_0x4fa870(clearPetrify=false, clearSkills=true)
        // Replaces 121 with full Petrify 120 (stage = 3 via vt+0xac(3))
    else if cmdId == 123 (0x7b, Instant Death):
        if battle != null:
            battle->CancelSong_0x43c110(this)
            battle->CancelDance_0x43c600(this)
            battle->CancelPuppet_0x43c9b0(this)
            battle->CancelGeass_0x43ce30(this)
            battle->CancelChant_0x43bc50(this)
            battle->DestroyOwnedDolls_0x43d2c0(this)
        // Triggers player death state via vt+0x130 on CGamePlayerStatus

    if recalcFlag:
        this->vt_0x108_RecalculateAll()
    return cmd

fn CGameStatusBase::RemoveStatusByIndex(this, idx: u32, recalcFlag: bool):
    cmd = this.StatusList[idx]
    cmdId = cmd->GetCommandId()
    // Marks sibling commands sharing the same source skillId/enemyAttackId via vt+0x4c
    delete cmd
    this.StatusList.erase(idx)
    if cmdId in {116, 120, 123}:
        this->vt_0x58_OnControlStatusChanged()
    if cmdId == 120 and not this->vt_0x38_IsDead() and battle != null:
        battle->ResyncAllyPerformances_0x43cfb0(this) // Re-applies active ally Songs/Dances/Geasses
    if recalcFlag:
        this->vt_0x108_RecalculateAll()

fn CGameStatusBase::ClearStatuses(this, clearPetrify: bool, clearSkills: bool):
    isDead: bool = this->vt_0x38_IsDead()
    for s in this.StatusList (in-place):
        canRemove: bool = true
        if isDead:
            canRemove = s->vt_0x90_ClearOnDeath() // (CommandData[id].flags38 >> 2) & 1
        if not clearPetrify and s->GetCommandId() == 120 (0x78):
            continue
        if not clearSkills and s->vt_0x34_GetSkillId() != -1 and IsInSkillTable(0x738a5c, skillId):
            continue
        if canRemove:
            this->vt_0x6c_RemoveStatusByIndex(i, recalcFlag=false)
    // Unconditional cleanup sweep over 20 hardcoded IDs at .rdata 0x6d40b0:
    // [261, 113, 114, 115, 116, 117, 122, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]
    for id in k_ClearIds_0x6d40b0[0..19]:
        this->vt_0x64_RemoveStatusById(id)

fn CGameStatusBase::OnDeathCleanup(this):
    if this->vt_0x38_IsDead():
        this->ClearStatuses(clearPetrify=true, clearSkills=true)
        if battle != null:
            battle->CancelSong_0x43c110(this)
            battle->CancelDance_0x43c600(this)
            battle->CancelPuppet_0x43c9b0(this)
            battle->CancelGeass_0x43ce30(this)
            battle->CancelChant_0x43bc50(this)
```

| Ailment Applied in `AddStatus` | Cancels Chant (`0x43bc50`) | Cancels Song (`0x43c110`) | Cancels Dance (`0x43c600`) | Cancels Puppet (`0x43c9b0`) | Cancels Geass (`0x43ce30`) | Extra Action |
|---|---|---|---|---|---|---|
| `113` Poison / `115` Paralysis / `122` Slow | No | No | No | No | No | None |
| `114` (`0x72`) Freeze | No | No | **Yes** | **Yes** | **Yes** | None |
| `116` (`0x74`) Sleep | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | Strips all statuses with `vt+0x8c() == true` (`0x4fa03a`) |
| `117` (`0x75`) Silence | **Yes** | **Yes** | No | No | No | None |
| `118` (`0x76`) Stun | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | Sets `gauge=0.0f`, `_SortTime(0,0)`, self-removes |
| `121` (`0x79`) Special Petrify | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | `ClearStatuses(0, 1)`, converts to `120` stage 3 |
| `123` (`0x7b`) Instant Death | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | `DestroyOwnedDolls` (`0x43d2c0`), death state |

**Program Evidence:**
```asm
004f9950  mov eax, dword ptr [eax + 0xc8]
004f9956  call eax
004f9958  test al, al
004f995a  jne 0x4fa5f9
004f9b9f  cmp ecx, 0x78
004f9ba2  jne 0x4f9bd3
004f9bc2  call dword ptr [edx + 0xb0]
004f9bc8  cmp eax, 3
004f9bcb  jae 0x4f9bd3
004f9bcd  mov byte ptr [ebp - 0xd], 0
004f9c30  call dword ptr [eax + 0xa8]
004f9c54  call dword ptr [esi + 0x64]
004f9c80  mov eax, dword ptr [eax + 0x84]
004f9e6f  cmp eax, 0x72
004f9e96  call 0x43c600
004f9eb5  call 0x43c9b0
004fa056  mov eax, dword ptr [eax + 0x8c]
004fa05c  call eax
004fa06f  call dword ptr [edx + 0x68]
004fa0e2  cmp eax, 0x75
004fa109  call 0x43c110
004fa128  call 0x43bc50
004fa8b1  mov eax, dword ptr [eax + 0x90]
004fa8cc  cmp eax, 0x78
```

---

### M06.02 `CCommand` Vtable Boolean Flag Matrix (All 328 Instantiated IDs)

**Binary VA(s):**
- `0x47b220..0x47de14` (`CCommand` factory; jump tables `0x47de14` / `0x47e0a4`; fallback `0x47dd9c` checks `CommandData[id].flags38` bit 3 via `0x554a50` to pick `CCommandTurnBase 0x6d130c` vs `CCommandBase 0x6d119c`)
- `0x479df0..0x479e0b` (dynamic `+0x54` `IsBuff`: `GetValue() >= 0.0f`)
- `0x479e40..0x479e56` (dynamic `+0x54` `IsBuff` for ID `32`: `GetValue() < 0.0f`, inverted sign!)
- `0x479e10..0x479e15` (dynamic `+0x64` `IsDispellable`: tail-calls `this->vt+0x54()`)
- `0x479e20..0x479e2c` (dynamic `+0x5c` `IsDebuff`: `!this->vt+0x54()`)
- `0x48bec0..0x48bee9` (`+0x8c` `IsSleepCleared`: `(CommandData[id].flags38 >> 1) & 1`)
- `0x48bef0..0x48bf19` (`+0x90` `ClearOnDeath`: `(CommandData[id].flags38 >> 2) & 1`)
- `0x4faf20..0x4fb564` (`CGameStatusBase` filter methods `vt+0x7c..+0xac`)

**Calls:**
- `cmd->vt+0x2c` (`GetValue`), `0x507310` (`CommandData` map lookup at `[0x7389c4]`, record flags at `[node+0x50]`, equivalent to `.pck` `[record+0x38]`).

**CalledBy:**
- `AddStatus` (`0x4f9930`), `ClearStatuses` (`0x4fa870`), `ClearBattleStatusesOnEnd` (`0x4fa960`), `TickCountdown` (`0x48d590`), `Dispel 74` (`0x422730` / `0x47ef25`), `Cure 106` (`0x481b35`).

**Typed Pseudocode:**
```text
// CCommand vtable boolean flag slots (constant return helpers: ret0 = false, ret1 = true)
//   +0x54 IsBuff()           (used by CGameStatusBase::vt+0x84/+0x88, and by +0x5c / +0x64)
//   +0x5c IsDebuff()         (used by CGameStatusBase::vt+0x8c/+0x90, Cure 106 lvl 8)
//   +0x64 IsDispellable()    (used by CGameStatusBase::vt+0x94 = 0x4fb1f0, Dispel 74)
//   +0x68 IsAilment()        (used by CGameStatusBase::vt+0x7c/+0x80, ClearBattleStatusesOnEnd)
//   +0x6c IsSong()           (used by CGameStatusBase::vt+0x98, AddStatus -> AddSongCommand)
//   +0x70 IsDance()          (used by CGameStatusBase::vt+0x9c, AddStatus -> AddDanceCommand)
//   +0x74 IsPuppet()         (used by CGameStatusBase::vt+0xa4, AddStatus -> AddPuppetCommand)
//   +0x78 IsGeass()          (used by CGameStatusBase::vt+0xa0, AddStatus -> AddGeassCommand)
//   +0x7c IsWeaponEnchant()  (used by CGameStatusBase::vt+0xa8, AddStatus exclusive group)
//   +0x84 IsBarrier()        (used by CGameStatusBase::vt+0xac, AddStatus exclusive group)
//   +0x8c IsSleepCleared()   (0x48bec0 on ALL 328 IDs: (CommandData[id].flags38 >> 1) & 1)
//   +0x90 ClearOnDeath()     (0x48bef0 on ALL 328 IDs: (CommandData[id].flags38 >> 2) & 1)

fn dynamic_0x479df0_IsBuff(this) -> bool:
    return this->vt_0x2c_GetValue() >= 0.0f    // comiss xmm0, [0x6d928c (0.0f)]; setae al

fn dynamic_0x479e40_IsBuff_ID32(this) -> bool:
    // ID 32 (Critical Vulnerability): negative value reduces enemy crit -> BUFF; positive -> DEBUFF
    return 0.0f > this->vt_0x2c_GetValue()     // xorps xmm0,xmm0; comiss xmm0,[esp]; seta al

fn dynamic_0x479e20_IsDebuff(this) -> bool:
    return !this->vt_0x54_IsBuff()

fn dynamic_0x479e10_IsDispellable(this) -> bool:
    return this->vt_0x54_IsBuff()              // tail-jump to vt+0x54

fn slot_0x48bec0_IsSleepCleared(this) -> bool:
    return ((CommandData[this.cmdId].flags38) >> 1) & 1
```

**Grouped Vtable Matrix Covering All 328 Route (a) `CCommand` IDs (13 Exact Equivalence Classes):**
All 328 IDs inherit `+0x8c = 0x48bec0` and `+0x90 = 0x48bef0`. Blank cells = static `0` (`false`).

| Class | Count | Command IDs (Decimal) | `+0x54` Buff | `+0x5c` Debuff | `+0x64` Dispel | `+0x68` Ail | `+0x6c` Song | `+0x70` Dance | `+0x74` Puppet | `+0x78` Geass | `+0x7c` WpnEnch | `+0x84` Barrier |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | `21, 26, 28, 31, 41..46, 161..169, 172..174, 184..186` | `val>=0` (`0x479df0`) | `!+54` (`0x479e20`) | `+54` (`0x479e10`) | | | | | | | |
| 2 | 1 | `32` (Crit Vulnerability) | `val<0` (`0x479e40`) | `!+54` (`0x479e20`) | `0` | | | | | | | |
| 3 | 2 | `27, 171` | `1` | | `+54` (`=1`) | | | | | | | |
| 4 | 5 | `325..329` (Fire/Water/Wind/Earth/Light Wpn Enchant) | `1` | | `+54` (`=1`) | | | | | | `1` | |
| 5 | 1 | `30` (Debuff-only) | | `1` | `+54` (`=0`) | | | | | | | |
| 6 | 3 | `101, 102, 181` (Barriers: Phys/Mag/Absorb) | | | `1` | | | | | | | `1` |
| 7 | 4 | `189, 191, 193, 194` (Stances/Charges) | | | `1` | | | | | | | |
| 8 | 11 | `113..122, 139` (True Ailments; note `123` is Class 13!) | | | `+54` (`=0`) | `1` | | | | | | |
| 9 | 14 | `210..223` (Songs; NOT dispellable!) | | | `+54` (`=0`) | | `1` | | | | | |
| 10 | 11 | `195..205` (Dances; NOT dispellable!) | | | `+54` (`=0`) | | | `1` | | | | |
| 11 | 6 | `228..233` (Puppets; NOT dispellable!) | | | `+54` (`=0`) | | | | `1` | | | |
| 12 | 7 | `335..341` (Geasses; NOT dispellable!) | | | `+54` (`=0`) | | | | | `1` | | |
| 13 | 238 | `9..20, 22..25, 29, 47..77, 79..100, 103..112, 123..138, 140..159, 170, 175..176, 178..180, 182..183, 187..188, 190, 192, 206..209, 224..227, 234..242, 246..247, 261, 272..273, 290..292, 294..296, 299, 302, 312, 318, 322..324, 330..334, 342..344, 347, 351, 359, 378..404, 406..414, 416..439, 441..442, 444..445` | | | `+54` (`=0`) | | | | | | | |

- **Exact `flags38` Bit 1 (`+0x8c` `IsSleepCleared`, 36 IDs in `backups/CommandData.pck`):** `[146, 147, 171, 180, 190, 228, 229, 230, 231, 232, 233, 235, 249, 250, 253, 255, 259, 260, 267, 268, 283, 285, 296, 300, 303, 305, 306, 308, 320, 345, 350, 357, 446, 447, 448, 449]`.
- **Exact `flags38` Bit 2 (`+0x90` `ClearOnDeath`):** `1` for 356 of 364 records; `0` ONLY for `[67, 68, 81, 133, 134, 355, 428, 433]`.

**Program Evidence:**
```asm
00479df0  push ecx
00479df3  mov eax, dword ptr [eax + 0x2c]
00479df6  call eax
00479e00  comiss xmm0, dword ptr [0x6d928c]
00479e07  setae al
00479e10  mov eax, dword ptr [ecx]
00479e12  mov eax, dword ptr [eax + 0x54]
00479e15  jmp eax
00479e22  mov eax, dword ptr [eax + 0x54]
00479e25  call eax
00479e27  test al, al
00479e29  sete al
00479e4b  xorps xmm0, xmm0
00479e4e  comiss xmm0, dword ptr [esp]
00479e52  seta al
0048bec3  mov eax, dword ptr [ecx + 0xc]
0048bedf  mov eax, dword ptr [eax + 0x50]
0048bee2  shr eax, 1
0048bee4  and al, 1
```

---

### M06.03 Stat Recalculation (`0x4fbdd0..0x4fc6cc`)

**Binary VA(s):**
- `0x4f7c00..0x4f7c69` (`CGamePlayerStatus::RecalculateAll`, `vt+0x108`)
- `0x4f2820..0x4f2845` (`CGameEnemyStatus::RecalculateAll`, `vt+0x108`)
- `0x4f6530..0x4f6696` (`CGamePlayerStatus::_CalculateParameterEquipment`)
- `0x4fbdd0..0x4fc610` (`CGameStatusBase::ApplyStatusStatAndResistModifiers`, `vt+0x10c`)
- `0x4fc620..0x4fc6cc` (`CGameStatusBase::ClampStats`, `vt+0x110`)

**Calls:**
- `0x47e340` (`FindCommandInVector`), `vt+0x30` (`GetRawStat`, `0x4f98c0`), `vt+0x34` (`GetEffStat`, `0x4f98d0`), `vt+0x48` (`GetCommand`), `vt+0x50` (`HasCommand`), `0x507310` (`EquipData` lookup `[0x7389e0]`).

**CalledBy:**
- `AddStatus` (`0x4f9930`), `RemoveStatusByIndex` (`0x4fa690`), `ClearBattleStatusesOnEnd` (`0x4fa960`), equipment/level/motivation updates (`0x4f69e0`).

**Typed Pseudocode:**
```text
fn CGamePlayerStatus::RecalculateAll(this):
    this->vt_0x104_CalculateBase()          // 0x4f5d60: sets RawStat, EffStat, RawResist, EffResist, MaxHP, MaxTP
    baseMaxHP: i32 = this.MaxHP             // saved at 0x4f7c29 BEFORE passives/equip/enchants!
    baseMaxTP: i32 = this.MaxTP             // saved at 0x4f7c2c
    this->vt_0x18c_ApplyClassPassives()     // 0x4f7c70
    this->_CalculateParameterEquipment()    // 0x4f6530 (skips slot 1 [this+0xac] if equipRec[+0x38]==0 offhand weapon)
    this->vt_0x180_ApplyEnchants(baseMaxHP, baseMaxTP) // 0x4f8270
    this->vt_0x10c_ApplyStatusModifiers(baseMaxHP, baseMaxTP) // 0x4fbdd0
    this->ApplySpecialPassives_0x4f8fe0()
    this->vt_0x110_ClampAndSamsara()        // 0x4fc620

fn CGameEnemyStatus::RecalculateAll(this):
    this->vt_0x104_CalculateBase()          // 0x4f25f0
    this->vt_0x10c_ApplyStatusModifiers(this.MaxHP, this.MaxTP) // 0x4fbdd0
    this->vt_0x110_ClampAndSamsara()        // 0x4fc620

fn CGameStatusBase::ApplyStatusStatAndResistModifiers(this, baseMaxHP: i32, baseMaxTP: i32):
    delta: i32[14] = {0} // indices 0..5 = ATK,DEF,INT,RES,DEX,AGI; 6..13 = Resistances (see M06.05)

    // 1. Stat buff/debuff commands 41..46 (0x29..0x2e) -> ATK..AGI (0x4fbe00..0x4fbfc9)
    for i in 0..5:
        cmd = FindCommand(this.StatusList, 41 + i)
        val: f32 = (cmd != null) ? cmd->GetValue() : 0.0f
        delta[i] += trunc0(f32(this.EffStat[i]) * val)

    // 2. Trump Card 48 (0x30) (0x4fbfca..0x4fc018)
    if (cmd48 = this->GetCommand(48)) != null:
        delta[1] = -10000 (0xffffd8f0)      // overwrites DEF delta (ignores earlier ID 42!)
        delta[0] += trunc0(f32(this.EffStat[1]) * cmd48->GetValue()) // adds DEF * val to ATK

    // 3. Petrification 120 (0x78) — applies at ANY stage (partial or full) (0x4fc019..0x4fc04f)
    if this->HasCommand(120):
        delta[1] += trunc0(this.RawStat[1] / 2)   // DEF += RawDEF / 2 (cdq; sub; sar 1)
        delta[5] -= trunc0(this.RawStat[5] / 2)   // AGI -= RawAGI / 2

    // (4..6: Resistances 169, MaxHP 172, Resistances 184..186 — see M06.04 & M06.05)

    // 7. Mutually exclusive all-stat modifiers: 189 -> 193 -> 194 (0x4fc140..0x4fc1ab)
    cmdAll = this->GetCommand(189) ?? this->GetCommand(193) ?? this->GetCommand(194)
    if cmdAll != null:
        val: f32 = cmdAll->GetValue()
        for i in 0..5:
            delta[i] += trunc0(f32(this.EffStat[i]) * val)

    // (8..10: Resistances 192, 202/341, 248 — see M06.05)

    // 11. Dual-Wield Offhand Passive 256 (0x100, Lefty Bonus) (0x4fc26f..0x4fc5c5)
    if (cmd256 = this->GetCommand(256)) != null:
        player = dynamic_cast<CGamePlayerStatus*>(this)
        offhand = dynamic_cast<CEquipItem*>(player->slot1_0xac)
        if offhand != null:
            rec = EquipData[offhand.itemId_0x70]
            if rec.equipType_0x38 == 0:     // 0 = Weapon (not shield/armor)
                rate: f32 = cmd256->GetValue()
                for s in 0..5:              // ATK, DEF, INT, RES, DEX, AGI from offhand
                    baseVal: i32 = offhand.statBase[s]
                    upVal: i32 = (baseVal != 0)
                        ? (baseVal + trunc0(f32(u32(offhand.upgradeLv)) * rec.upgradeRate_0x54))
                        : 0
                    delta[s] += trunc0(f32(upVal) * rate)

    // 12. Commit accumulated deltas to EffStat[0..5] and EffResist[0..7]
    for i in 0..13:
        this.EffField[i] += delta[i]

fn CGameStatusBase::ClampStats(this):       // 0x4fc65e..0x4fc6cc
    for i in 0..5:
        this.EffStat[i] = clamp(this.EffStat[i], 0, 9999) // 0x270f
```

**Program Evidence:**
```asm
004fbfb4  push 0x30
004fbfca  call dword ptr [eax + 0x48]
004fbfef  mov ebx, 0xffffd8f0
004fc00d  cvttss2si eax, dword ptr [esp + 0x1c]
004fc013  add ebp, eax
004fc01d  push 0x78
004fc02e  call dword ptr [eax + 0x30]
004fc031  cdq
004fc034  sub eax, edx
004fc036  sar eax, 1
004fc038  add ebx, eax
004fc04a  sub esi, eax
004fc144  push 0xbd
004fc156  push 0xc1
004fc169  push 0xc2
004fc19a  mulss xmm0, xmm1
004fc19e  cvttss2si eax, xmm0
004fc26f  push 0x100
004fc2db  cmp dword ptr [eax + 0x38], 0
004fc649  mov edx, 0x270f
004fc665  cmovns ecx, eax
004fc66d  cmovg ecx, edx
```

---

### M06.04 Max HP Buff `172` & Life Bringer `133` MaxHP Drain Modifier

**Binary VA(s):**
- `0x4f7c29..0x4f7c4e` (`CGamePlayerStatus::RecalculateAll` capturing `baseMaxHP` before passives/equipment/enchants)
- `0x4fc089..0x4fc0c4` (Effect `172` (`0xac`) inside `ApplyStatusStatAndResistModifiers`)
- `0x4fc5c5..0x4fc5ff` (applying `hpBuffDelta` to `[this+0x10]`)
- `0x4fc620..0x4fc65d` (`ClampStats`: applies `[this+0x98] MaxHPDelta`, floors `MaxHP` at `1`, clamps `CurHP` to `MaxHP`)
- `0x4f9880..0x4f988a` (`CGameStatusBase::AddMaxHPDelta`, `vt+0x2c`: `this.MaxHPDelta += arg`)
- `0x483ee0..0x483fa0` (`CCommand_0133::OnPostHit` — Life Bringer MaxHP drain)

**Calls:**
- `this->vt+0x48(0xac)` (`GetCommand(172)`), `target->vt+0x2c(delta)` (`0x4f9880`).

**CalledBy:**
- `RecalculateAll` (`0x4f7c00` / `0x4f2820`), `CActionPatternBase::_Task` post-hit hook (calls `CCommand_0133` `0x483ee0`).

**Typed Pseudocode:**
```text
// 1. Effect 172 (0xac, Max HP Buff) inside 0x4fbdd0 (0x4fc089..0x4fc0c4, 0x4fc5c5..0x4fc5e5)
//    On Players: baseMaxHP was captured at 0x4f7c29 AFTER _CalculateParameterBase (0x4f5d60)
//                and BEFORE class passives (0x4f7c70), equipment (0x4f6530), and enchants (0x4f8270).
//    On Enemies: baseMaxHP is [this+0x10] from 0x4f25f0.
hpBuffDelta: i32 = 0
if (cmd172 = this->GetCommand(172)) != null:
    hpBuffDelta = trunc0(f32(baseMaxHP) * cmd172->GetValue())
// Note: Effect 172 does NOT modify CurHP when applied; CurHP is only clamped down on expiry/removal.
this.MaxHP = max(1, this.MaxHP + hpBuffDelta)

// 2. Final HP/TP Clamp inside 0x4fc620 (0x4fc624..0x4fc65d)
//    Runs on every RecalculateAll (including when 172 expires/is dispelled or after 133 drains MaxHP).
effMaxHP: i32 = this.MaxHP + this.MaxHPDelta_0x98
if effMaxHP <= 0:
    effMaxHP = 1
this.MaxHP = effMaxHP
if this.CurHP > this.MaxHP:
    this.CurHP = this.MaxHP

if this.MaxTP <= 0:
    this.MaxTP = 1
if this.CurTP > this.MaxTP:
    this.CurTP = this.MaxTP

// 3. Life Bringer 133 (0x85) — permanent battle MaxHP drain (0x483ee0..0x483f8c)
fn CCommand_0133::Execute(this, results: vector<TaskResult>*, battleInfo, target: CGameStatusBase*):
    if results.empty():
        return
    hpDmg: i32 = results[0].hpDamage_0x1c
    if hpDmg == 0x7fffffff or hpDmg <= 0:
        return
    drain: i32 = trunc0(f32(hpDmg) * this->vt_0x2c_GetValue())
    target->vt_0x2c_AddMaxHPDelta(-drain)   // 0x4f9880: target.MaxHPDelta_0x98 += (-drain)
    // Subsequent RecalculateAll applies MaxHPDelta_0x98 at 0x4fc629..0x4fc646,
    // flooring MaxHP at 1 and clamping CurHP <= MaxHP.
    // Note: Command 133 has ClearOnDeath (flags38 bit 2) = 0 (persists across death).
```

**Program Evidence:**
```asm
004f7c29  mov edi, dword ptr [ebx + 0x10]
004f7c4d  push edi
004f7c4e  call dword ptr [eax + 0x10c]
004fc08d  push 0xac
004fc094  call dword ptr [eax + 0x48]
004fc0a4  movd xmm0, dword ptr [esp + 0x60]
004fc0aa  cvtdq2ps xmm0, xmm0
004fc0b3  fmul dword ptr [esp + 0x60]
004fc629  mov edx, dword ptr [esi + 0x98]
004fc62f  add edx, dword ptr [esi + 0x10]
004fc635  test edx, edx
004fc637  cmovle edx, edi
004fc63a  cmp dword ptr [esi + 0xc], edx
004fc63d  mov dword ptr [esi + 0x10], edx
004fc640  cmovle edx, dword ptr [esi + 0xc]
004fc646  mov dword ptr [esi + 0xc], edx
004f9880  mov eax, dword ptr [esp + 4]
004f9884  add dword ptr [ecx + 0x98], eax
00483f4a  mov edx, dword ptr [esi + 0x1c]
00483f4d  cmp edx, 0x7fffffff
00483f59  test edx, edx
00483f82  cvttss2si eax, dword ptr [ebp + 0x10]
00483f87  neg eax
00483f89  push eax
00483f8a  call dword ptr [edx + 0x2c]
```

---

### M06.05 Resistance Recalculation & Samsara Override (`0x4fc050..0x4fc889`)

**Binary VA(s):**
- `0x4fc050..0x4fc088` (Elemental resist buff/debuff `169` / `0xa9`)
- `0x4fc0c5..0x4fc13f` (Physical resist buffs/debuffs `184` / `0xb8`, `185` / `0xb9`, `186` / `0xba`)
- `0x4fc1ac..0x4fc1e5` (Effect `192` / `0xc0` `+10000` to all 8 resistances via SIMD constant `0x6d9e10`)
- `0x4fc1e6..0x4fc231` (Exclusive elemental resist `202` / `0xca` Hopak vs `341` / `0x155` Emaciating Geas)
- `0x4fc232..0x4fc26a` (Passive `248` / `0xf8` Resistance)
- `0x4fc6c7..0x4fc76e` (`[-100, +100]` clamp on `EffResist[0..7]`)
- `0x4fc76f..0x4fc889` (Samsara resistance override `416..423` / `0x1a0..0x1a7`, post-clamp)

**Calls:**
- `this->vt+0x48(id)` (`GetCommand`), `this->vt+0x50(0xc0)` (`HasCommand(192)`), `0x61d550` (`_ftol2_sse`, truncates toward zero).

**CalledBy:**
- `CGamePlayerStatus::RecalculateAll` (`0x4f7c00`), `CGameEnemyStatus::RecalculateAll` (`0x4f2820`).

**Typed Pseudocode:**
```text
// Resistance slots in delta[6..13] / EffResist[0..7] ([this+0x6c..+0x88]):
//   delta[6]  (+0x6c) = Slash      (Physical)
//   delta[7]  (+0x70) = Stab       (Physical)
//   delta[8]  (+0x74) = Bash       (Physical)
//   delta[9]  (+0x78) = Fire       (Elemental)
//   delta[10] (+0x7c) = Water      (Elemental)
//   delta[11] (+0x80) = Wind       (Elemental)
//   delta[12] (+0x84) = Earth      (Elemental)
//   delta[13] (+0x88) = Lightning  (Elemental)

// Inside 0x4fbdd0 (ApplyStatusStatAndResistModifiers):
// 1. Effect 169 (0xa9, All-Element Resist Buff/Debuff) (0x4fc050..0x4fc088)
if (cmd169 = this->GetCommand(169)) != null:
    v: i32 = trunc0(cmd169->GetValue())
    for idx in 9..13:
        delta[idx] += v

// 2. Physical Resist Buffs/Debuffs 184, 185, 186 (0x4fc0c5..0x4fc13f)
if (cmd184 = this->GetCommand(184)) != null: delta[7] += trunc0(cmd184->GetValue()) // Stab
if (cmd185 = this->GetCommand(185)) != null: delta[6] += trunc0(cmd185->GetValue()) // Slash
if (cmd186 = this->GetCommand(186)) != null: delta[8] += trunc0(cmd186->GetValue()) // Bash

// 3. Effect 192 (0xc0, Invulnerability / All-Resist +10000) (0x4fc1ac..0x4fc1e5)
//    .rdata 0x6d9e10 = int32x4 { 10000, 10000, 10000, 10000 }
if this->HasCommand(192):
    for idx in 6..13:
        delta[idx] += 10000

// 4. Exclusive Dance 202 (0xca, Hopak) vs Geass 341 (0x155, Emaciating Geas) (0x4fc1e6..0x4fc231)
//    Note: 202 takes priority over 341 (if/else-if); 202 GetValue() includes Dance Bonus (M06.08).
cmdElemPerf = this->GetCommand(202) ?? this->GetCommand(341)
if cmdElemPerf != null:
    v: i32 = trunc0(cmdElemPerf->GetValue())
    for idx in 9..13:
        delta[idx] += v

// 5. Passive 248 (0xf8, Elemental Resistance) (0x4fc232..0x4fc26a)
if (cmd248 = this->GetCommand(248)) != null:
    v: i32 = trunc0(cmd248->GetValue())
    for idx in 9..13:
        delta[idx] += v

// After committing delta[6..13] to EffResist[0..7], inside 0x4fc620 (ClampAndSamsara):
// 6. Standard clamp to [-100, +100] (0x4fc6c7..0x4fc76e)
for k in 0..7:
    this.EffResist[k] = clamp(this.EffResist[k], -100, +100) // 0xffffff9c .. 0x64

// 7. Samsara Override 416..423 (0x1a0..0x1a7) — runs AFTER clamp, NO re-clamp! (0x4fc76f..0x4fc889)
//    416=Slash(+0x6c), 417=Stab(+0x70), 418=Bash(+0x74),
//    419=Fire(+0x78),  420=Water(+0x7c), 421=Wind(+0x80), 422=Earth(+0x84), 423=Lightning(+0x88)
for k in 0..7:
    if (cmdSamsara = this->GetCommand(416 + k)) != null:
        this.EffResist[k] = trunc0(cmdSamsara->GetValue())  // _ftol2_sse (0x61d550)
```

**Program Evidence:**
```asm
004fc054  push 0xa9
004fc06f  cvttss2si eax, dword ptr [esp + 0x1c]
004fc0c9  push 0xb8
004fc0f2  push 0xb9
004fc11b  push 0xba
004fc1b0  push 0xc0
004fc1be  movaps xmm1, xmmword ptr [0x6d9e10]
004fc1d5  paddd xmm0, xmm1
004fc1ea  push 0xca
004fc1fc  push 0x155
004fc236  push 0xf8
004fc6c7  mov edx, 0xffffff9c
004fc6cf  mov ecx, 0x64
004fc6d9  cmovl eax, edx
004fc6de  cmovg eax, ecx
004fc709  push 0x1a0
004fc771  call dword ptr [eax + 0x48]
004fc781  call 0x61d550
004fc786  mov dword ptr [esi + 0x6c], eax
004fc78d  push 0x1a1
```

---

### M06.06 Timed Status Countdown, Sleep-Decay, and Map Step Counter (`X15`)

**Binary VA(s):**
- `0x436d4c..0x436d5d` (Inner Turn-Start State 8: calls `actor.status->vt+0xdc(battleInfo)`)
- `0x4fba20..0x4fbb30` (`CGameStatusBase::TickTurnStartStatuses`, `vt+0xdc`)
- `0x4fb660..0x4fb780` (`CGameStatusBase::TickMapStepStatuses`, `vt+0xd4`)
- `0x48d160..0x48d2f4` (`CCommandTurnBase::OnMapStep`, `vt+0x0c`)
- `0x48d590..0x48d6b9` (`CCommandTurnBase::TickCountdown`, `vt+0x14`)
- `0x47fdc0..0x47fddf` (Field-only countdown wrapper for IDs `[17, 18, 21, 107]`)

**Calls:**
- `target->vt+0xbc` (`0x4fb5d0` `HasSleep_116`), `this->vt+0x8c` (`0x48bec0` `IsSleepCleared`), `0x47e500` (`CCommand::Execute`).

**CalledBy:**
- Inner Turn-Start State 8 (`0x436d4c`), dungeon step update (`vt+0xd4` -> `0x4fb660` -> `cmd->vt+0x0c` `0x48d160` -> `cmd->vt+0x14` `0x48d590`).

**Typed Pseudocode:**
```text
// CCommandTurnBase layout (sizeof = 0x30, vtable 0x6d130c; used by 97 timed status IDs):
//   +0x28 u32 turnsRemaining   (0 = permanent, never expires by turn countdown)
//   +0x2c u32 mapStepCounter   (counts out-of-battle map steps modulo 5)

fn CGameStatusBase::TickTurnStartStatuses(this, battleInfo): // vt+0xdc = 0x4fba20
    results: vector<TaskResult> = {}
    for cmd in this.StatusList:
        cmd->vt_0x14_TickCountdown(&results, battleInfo, this)
    if not results.empty():
        CCommand::Execute_0x47e500(&results, battleInfo)     // removes expired statuses & recalcs

fn CCommandTurnBase::TickCountdown(this, results, battleInfo, target) -> bool: // 0x48d590
    // 1. Sleep-Decay check (0x48d5b5..0x48d5d7):
    //    Fires EVEN IF turnsRemaining == 0!
    if target != null and target->vt_0xbc_HasSleep_116() and this->vt_0x8c_IsSleepCleared():
        goto EXPIRE

    // 2. Permanence check (0x48d5d9..0x48d5de):
    //    turnsRemaining == 0 means permanent (aura, passive, stance, or infinite buff)
    if this.turnsRemaining_0x28 == 0:
        return false

    // 3. Out-of-battle map step counter (X15 patch site at 0x48d5f3: vanilla imm8 = 5)
    if battleInfo.inBattleFlag_0x40 == 0:
        this.mapStepCounter_0x2c += 1
        if this.mapStepCounter_0x2c < 5:    // 0x48d5f0: cmp dword ptr [esi+0x2c], 5; jb
            return false
        this.mapStepCounter_0x2c = 0

    // 4. Decrement turns; expire at 0 (0x48d601..0x48d612)
    this.turnsRemaining_0x28 -= 1
    if this.turnsRemaining_0x28 != 0:
        return false

EXPIRE:                                     // 0x48d613..0x48d6a6
    entry = TaskResult(target)
    entry.removeCmdId_0x08 = this->GetCommandId()
    entry.actionType_0x2c  = 2              // remove status
    results.push_back(entry)
    return true

// Field-only countdown wrapper 0x47fdc0 (IDs 17, 18, 21, 107):
fn CCommandFieldOnly::TickCountdown(this, results, battleInfo, target) -> bool:
    if battleInfo.inBattleFlag_0x40 != 0:
        return false                        // never ticks down during battle
    return CCommandTurnBase::TickCountdown(this, results, battleInfo, target)
```

**Program Evidence:**
```asm
00436d4c  inc dword ptr [edi + 0x20]
00436d57  call dword ptr [eax + 0xdc]
0048d5b5  test edi, edi
0048d5b7  je 0x48d5d9
0048d5bd  mov eax, dword ptr [eax + 0xbc]
0048d5c3  call eax
0048d5cd  mov eax, dword ptr [eax + 0x8c]
0048d5d3  call eax
0048d5d7  jne 0x48d613
0048d5d9  mov ecx, dword ptr [esi + 0x28]
0048d5dc  test ecx, ecx
0048d5de  je 0x48d6a7
0048d5e7  cmp dword ptr [eax + 0x40], 0
0048d5eb  jne 0x48d601
0048d5ed  inc dword ptr [esi + 0x2c]
0048d5f0  cmp dword ptr [esi + 0x2c], 5
0048d5f4  jb 0x48d6a7
0048d5fa  mov dword ptr [esi + 0x2c], 0
0048d605  lea eax, [ecx - 1]
0048d608  mov dword ptr [esi + 0x28], eax
0048d60b  test eax, eax
0048d60d  jne 0x48d6a7
```

---

### M06.07 Dispel (`74`), Cure (`106`), Light (`107`), and Esarhaddon (`311`)

**Binary VA(s):**
- `0x4226c4..0x4227d5` (Dispel `74` / `0x4a`, attack-embedded path in `CActionPatternBase::_Task`)
- `0x47ee62..0x47efc4` (Dispel `74` / `0x4a`, skill/command execution path in `CCommand::Execute`; **`X16`** Third Eye Wide Dispel guard at `0x47ee6f..0x47ee78`)
- `0x4fb1f0..0x4fb264` (`CGameStatusBase::GetDispellableCommands`, `vt+0x94`, filters `cmd->vt+0x64()`)
- `0x481a60..0x481d68` (`CCommand_0106::Execute` — Cure `106` & Level 8 Debuff Strip; `.rdata` table `0x6cc79c`)
- `0x4fb170..0x4fb1ef` (`CGameStatusBase::GetDebuffCommands`, `vt+0x90`, filters `cmd->vt+0x5c()`)
- `0x47fde0..0x47fe78` (`CCommand_0107::Execute` — Light `107`, dungeon illumination, NOT combat debuff strip)
- `0x436724..0x43692f` (Esarhaddon `311` / `0x137` in Inner Turn-Start State 0; `.rdata` table `0x6c9a7c`)

**Calls:**
- `0x505ac0` (`Rand(100)` in `_Task`), `0x490790` (`GlobalRng.Rand(100)` via `[0x816ce8]` in `CCommand::Execute`), `0x48cc40` (`GetTaskResultCommand`), `0x61e650` (`round_f32_to_i32`), `target->vt+0x94` (`0x4fb1f0`), `target->vt+0x90` (`0x4fb170`), `target->vt+0x68` (`RemoveStatusByPtr`), `0x47e500` (`CCommand::Execute`).

**CalledBy:**
- `CActionPatternBase::_Task` (`0x4226c4`), `CCommand::Execute` (`0x47e500`), Inner Turn-Start State 0 (`0x436724`).

**Typed Pseudocode:**
```text
// 1. Dispel 74 (0x4a) — Path A: Attack-Embedded in CActionPatternBase::_Task (0x4226c4..0x4227d5)
if (cmd74 = FindCommand(attackCmds, 74)) != null:
    roll: i32 = Rand_0x505ac0(100)              // uniform [0, 99]
    chance: i32 = trunc0(cmd74->GetValue() * 100.0f)
    if roll < chance:                           // strict < (0x422711: cmp edi, esi; jge skip)
        dispellables = target->vt_0x94_GetDispellableCommands() // filters cmd->vt+0x64()
        for c in dispellables:
            target->vt_0x68_RemoveStatusByPtr(c)

// 2. Dispel 74 (0x4a) — Path B: Skill/Command Execution in CCommand::Execute (0x47ee62..0x47efc4)
//    X16 Patch Site: at 0x47ee6f..0x47ee78, vanilla skips Dispel if entry.removeCmdId_0x08 == -1.
if battleInfo.inBattleFlag_0x40 != 0 and entry.cmdRef_0x08 != -1:
    cmd = GetTaskResultCommand_0x48cc40(entry)
    if cmd != null and cmd->GetCommandId() == 74 (0x4a):
        roll: i32 = g_Rng[0x816ce8]->Rand_0x490790(100)
        chance: i32 = trunc0(cmd->GetValue() * 100.0f)
        if roll < chance:
            dispellables = target->vt_0x94_GetDispellableCommands() // 0x4fb1f0 (cmd->vt+0x64())
            for c in dispellables:
                target->vt_0x68_RemoveStatusByPtr(c)

// 3. Cure 106 (0x6a) & Debuff Strip at Level 8 (0x481a92..0x481c1c)
//    .rdata 0x6cc79c[0..6] = [113 (Poison), 115 (Paralysis), 117 (Silence),
//                             114 (Freeze), 116 (Sleep), 120 (Petrify), 122 (Slow)]
fn CCommand_0106::Execute(this, results, battleInfo, target):
    lvl: u32 = round_f32_to_i32(this->GetValue())  // 0x61e650
    n: u32 = min_u32(lvl, 7)                       // 0x481ab4: cmova eax, 7
    toRemove: vector<CCommand*> = {}
    for i in 0 .. n - 1:
        if (c = target->GetCommand(k_CureTable_0x6cc79c[i])) != null:
            toRemove.push_back(c)
    // Level 8 ONLY: also strips ALL active debuffs (cmd->vt+0x5c() == true)!
    if lvl == 8:                                   // 0x481b12: cmp ecx, 8; jne 0x481b60
        debuffs = target->vt_0x90_GetDebuffCommands() // 0x4fb170
        toRemove.append(debuffs)
    // Queues removal TaskResults for each command in toRemove

// 4. Command 107 (0x6b, Light) (0x47fde0..0x47fe78):
//    Dungeon field illumination command (calls GameManager->vt+0x18c(cmd) at 0x5103b0).
//    Has NO combat debuff-strip logic; combat debuff strip is Cure 106 at lvl == 8.

// 5. Esarhaddon 311 (0x137) — Inner Turn-Start State 0 (0x436724..0x43692f)
//    .rdata 0x6c9a7c[0..5] = [113 (Poison), 115 (Paralysis), 117 (Silence),
//                             114 (Freeze), 116 (Sleep), 122 (Slow)]
//    (6 entries; deliberately EXCLUDES 120 Petrification!)
if (cmd311 = actor.status->GetCommand(311)) != null:
    n: u32 = round_f32_to_i32(cmd311->GetValue())  // 0x61e650
    results: vector<TaskResult> = {}
    for i in 0 .. n - 1:                           // indices into k_Esarhaddon_0x6c9a7c
        if (c = actor.status->GetCommand(k_Esarhaddon_0x6c9a7c[i])) != null:
            results.push_back(MakeRemoveResult(actor.status, c->GetCommandId()))
    if not results.empty():
        CCommand::Execute_0x47e500(&results, battleInfo)
```

**Program Evidence:**
```asm
004226c4  mov edx, 0x4a
004226ea  call 0x505ac0
004226f6  mulss xmm0, dword ptr [0x6d9540]
004226fe  cvttss2si esi, xmm0
00422711  cmp edi, esi
00422713  jge 0x4227d2
00422730  call dword ptr [eax + 0x94]
0047ee6f  cmp dword ptr [ebx + 8], -1
0047ee73  je 0x47efc4
0047ee91  cmp eax, 0x4a
0047eeae  call 0x490790
00481aa3  call 0x61e650
00481aaa  mov edx, 7
00481ab4  cmova eax, edx
00481ad3  push dword ptr [esi*4 + 0x6cc79c]
00481b12  cmp ecx, 8
00481b15  jne 0x481b60
00436727  push 0x137
0043676a  call 0x61e650
```

---

### M06.08 Performance Groups: Songs, Dances, Puppets, Geass, Bonuses, Ticks & Cancellation

**Binary VA(s):**
- `0x43bc50..0x43bdcf` (`CancelChant`)
- `0x43bdd0..0x43c292` (`AddSongCommand` `0x43bdd0`, `CancelSong` `0x43c110`, `DeleteSongCommand`)
- `0x43c2a0..0x43c782` (`AddDanceCommand` `0x43c2a0`, `CancelDance` `0x43c600`)
- `0x43c790..0x43cb79` (`AddPuppetCommand` `0x43c790`, `CancelPuppet` `0x43c9b0`, `DeletePuppetCommand` `0x43caf0`)
- `0x43cb80..0x43cfa0` (`AddGeassCommand` `0x43cb80`, `CancelGeass` `0x43ce30`)
- `0x43cfb0..0x43d2bf` (`ResyncAllyPerformancesOnPetrifyCure`), `0x43d2c0..0x43d360` (`DestroyOwnedDolls`)
- `0x48bf90..0x48c1c1` (`CCommandBase::GetSongDanceBonus(passiveId)`)
- `0x487d70`, `0x488400`, `0x488890`, `0x488be0`, `0x488e10`, `0x4894a0`, `0x4895e0` (Song/Dance `GetValue` & regen tick overrides)
- `0x437eda..0x43841a` (Inner Turn-Start States 18–20: Dance `200`, Dance `204`, Dance `199` / Geass `339`)
- `0x42b240..0x42b890` (`CActionPatternE0822` Dance `200`), `0x42b8a0..0x42be70` (`CActionPatternE0835` Dance `204`), `0x42ec90..0x42f300` (`CActionPatternT0094` Dance `199` / Geass `339`), `0x436343..0x4365fb` (Summon/Guest `199` tick)

**Calls:**
- `caster.status->vt+0x50(capPassiveId)`, `player->vt+0xf0(enchantId)` (`GetEnchantCount`), `0x4f69e0` (`ClampMotivation`), `0x47e500` (`CCommand::Execute`).

**CalledBy:**
- `AddStatus` (`0x4f9930`), `RemoveStatusByIndex` (`0x4fa690`), `OnDeathCleanup` (`0x4fc890`/`0x4f5fa0`), `CBattleBase::_TurnStart` Inner States 18–20 (`0x437eda..0x43841a`) & Summon hook (`0x436343`).

**Typed Pseudocode:**
```text
// 1. Performance Group Registration, Slot Caps & FIFO Eviction
//    BattleUnit_s tracks active performance IDs owned by the caster:
//      Songs   [u+0xbc..+0xc0]  IDs 210..223  cap = Has(287 / 0x11f Solo Duet)    ? 2 : 1  targets: caster's side
//      Dances  [u+0xc8..+0xcc]  IDs 195..205  cap = Has(284 / 0x11c On Stage)     ? 2 : 1  targets: opposing side
//      Puppets [u+0xd4..+0xd8]  IDs 228..233  cap = Has(313 / 0x139 Double Puppet)? 2 : 1  targets: caster's dolls
//      Geasses [u+0xe0..+0xe4]  IDs 335..341  cap = Has(284 / 0x11c On Stage)     ? 2 : 1  targets: opposing side
//    NOTE: Geass (0x43cb80) shares passive 284 (0x11c) with Dance (0x43c2a0)!

fn CBattleBase::AddPerformance(this, group, casterUnit, cmd):
    cmdId = cmd->GetCommandId()
    // Remove cmdId from any other unit on caster's side already performing the same cmdId
    for ally in GetSide(casterUnit):
        if cmdId in ally.perfVec[group]:
            ally.perfVec[group].erase(cmdId)
    cap: u32 = casterUnit.status->HasCommand(group.capPassiveId) ? 2 : 1
    // FIFO eviction when full: evicts oldest entry vec[0] from all recipients on target side
    if casterUnit.perfVec[group].len >= cap:
        evictedId = casterUnit.perfVec[group][0]
        casterUnit.perfVec[group].erase_index(0)
        for target in GetRecipients(group, casterUnit):
            target.status->RemoveStatusById(evictedId)
    casterUnit.perfVec[group].push_back(cmdId)

// 2. Song / Dance Bonus Helper (0x48bf90..0x48c1c1)
//    passiveId = 279 (0x117, Song Bonus) or 280 (0x118, Dance Bonus)
fn CCommandBase::GetSongDanceBonus(this, passiveId: i32) -> f32:
    if this.casterPlayerId_0x1c != -1:
        player = g_PartyMgr[0x71fc24]->GetPlayer(this.casterPlayerId_0x1c)
        if player == null or not player->vt_0xe8_IsAliveInParty():
            return 0.0f
        passiveVal: f32 = (p = player->GetCommand(passiveId)) ? p->GetValue() : 0.0f
        enchVal: f32 = 0.0f
        if passiveId == 279 (0x117):        // Song enchants: 300 (+2% ea), 301 (+1% ea)
            cMajor: u32 = player->vt_0xf0_GetEnchantCount(300) // 0x12c
            cMinor: u32 = player->vt_0xf0_GetEnchantCount(301) // 0x12d
            enchVal = min(0.05f, f32(cMajor) * 0.02f + f32(cMinor) * 0.01f)
        else if passiveId == 280 (0x118):   // Dance enchants: 302 (+2% ea), 303 (+1% ea)
            cMajor: u32 = player->vt_0xf0_GetEnchantCount(302) // 0x12e
            cMinor: u32 = player->vt_0xf0_GetEnchantCount(303) // 0x12f
            enchVal = min(0.05f, f32(cMajor) * 0.02f + f32(cMinor) * 0.01f)
        return passiveVal + enchVal
    else if this.casterEnemyId_0x20 != -1:
        enemy = FindAliveEnemy(this.casterEnemyId_0x20)
        if enemy == null: return 0.0f
        return (p = enemy->GetCommand(passiveId)) ? p->GetValue() : 0.0f // no enchants
    return 0.0f

// 3. Performer Turn-Start Ticks (Inner States 18..20 at 0x437eda..0x43841a)
//    Checked on the PERFORMER's own turn against performer.dances_0xc8 / performer.geasses_0xe0!
//    State 18 (0x437eda): Dance 200 (0xc8, Subtle Dance) -> CActionPatternE0822 (0x42b240)
//      For each living opposing unit:
//        tpDmg = min(trunc0(f32(target.MaxTP) * cmd200->GetValue()), cap296_if_present)
//    State 19 (0x438085): Dance 204 (0xcc, Weird Dance)  -> CActionPatternE0835 (0x42b8a0)
//      For each living player target with !player->vt_0x100():
//        player.motivation_0xd8 += cmd204->GetValue()
//        player->ClampMotivation_0x4f69e0()   // clamps [70.0f, 130.0f], applies enchants 201/200/195
//        player->RecalculateAll()
//    State 20 (0x43824e): Dance 199 (0xc7, Salsa) OR Geass 339 (0x153, Debilitating Geas)
//      -> CActionPatternT0094 (0x42ec90):
//        hpDmg = min(trunc0(f32(target.MaxHP) * cmd->GetValue()), cap296_if_present)
//        entry.canCritOrWake_0x37 = 0
//    Summon/Guest Turn Hook (unitId in 3000..3999, 0x436343..0x4365fb):
//      If unit has Dance 199 (0xc7): deals trunc0(f32(unit.MaxHP) * cmd199->GetValue()) directly (no 296 cap).
```

**Song & Dance Bonus Formula Wiring Table (`GetValue` / Tick Overrides):**

| Binary VA | Command IDs | Bonus Passive & Enchants | Exact Effective Value / Tick Formula |
|---|---|---|---|
| `0x487d70` | Dances `195, 196, 197, 198, 201, 205` | `280` + ench `302/303` | `rawVal - Bonus(280)` (negative debuff amplified) |
| `0x488400` | Dance `199` (Salsa) | `280` + ench `302/303` | `rawVal + Bonus(280)` (HP% DoT amplified) |
| `0x488890` | Dance `202` (Hopak) | `280` + ench `302/303` | `rawVal - Bonus(280) * 100.0f` (resist debuff points) |
| `0x488be0` | Songs `210, 212, 213, 214, 217, 218, 222` | `279` + ench `300/301` | `rawVal + Bonus(279)` |
| `0x488e10` | Song `211` (Prelude) | `279` + ench `300/301` | `rawVal + Bonus(279) * 100.0f` |
| `0x4894a0` | Song `215` (Carol HP Regen Tick) | `279` + ench `300/301` | `healHP = trunc0((Bonus(279) * 10.0f + 1.0f) * GetValue())` |
| `0x4895e0` | Song `216` (Chorale TP Regen Tick) | `279` + ench `300/301` | Players ONLY (`_RTDynamicCast`): `healTP = trunc0(GetValue() + Bonus(279) * 100.0f)` |

- **Cancellation on Death / Ailments / Interrupt:** `OnDeathCleanup` (`0x4fc890`/`0x4f5fa0`) cancels all 5 groups (`Chant 0x43bc50`, `Song 0x43c110`, `Dance 0x43c600`, `Puppet 0x43c9b0`, `Geass 0x43ce30`). Ailment-specific cancels in `AddStatus` follow the table in `M06.01` (`Freeze 114` cancels Dance/Puppet/Geass only; `Silence 117` cancels Song/Chant only; `Sleep 116`, `Stun 118`, `Special Petrify 121`, `Instant Death 123` cancel all 5). When a cancelled performer's vector is cleared, every ID in that vector is removed from all affected units on the recipient side.

**Program Evidence:**
```asm
0043bfbd  push 0x11f
0043bfca  call eax
0043bfd7  mov ecx, 2
0043bfdc  cmovne esi, ecx
0043c47e  push 0x11c
0043c48b  call eax
0043c48f  mov ecx, 2
0043c49a  cmovne esi, ecx
0043ccd5  call eax
0043ccd9  mov ecx, 2
0043cce4  cmovne esi, ecx
0048c027  push 0x12c
0048c032  push 0x12d
0048c045  push 0x12e
0048c050  push 0x12f
0048c071  mulss xmm0, dword ptr [0x6d92e0]
0048c09c  mulss xmm1, dword ptr [0x6d92d4]
004894e0  push 0x117
004894ec  call 0x48bf90
004894f1  mulss xmm0, dword ptr [0x6d9468]
004894fd  addss xmm0, dword ptr [0x6d938c]
00489658  mulss xmm0, dword ptr [0x6d9540]
0043809c  mov dword ptr [ebp - 0x10], 0xcc
00438265  mov dword ptr [ebp - 0x10], 0xc7
004382bc  mov dword ptr [ebp - 0x10], 0x153
```
