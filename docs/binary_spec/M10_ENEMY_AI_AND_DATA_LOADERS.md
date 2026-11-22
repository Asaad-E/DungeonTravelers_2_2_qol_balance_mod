# M10: Enemy/Summon/NPC AI Script VM, Random Move Tables, Dungeon Floor/Map Triggers & Binary Data Loaders

**Binary Target:** `backups/exe/DT22_en_unwrapped.vanilla.exe` (PE32 x86, image base `0x00400000`)
**SHA-256:** `785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60`
**Scope:** Clean-room Phase 1 binary specification covering (1) the `Battle::CBattleAI2` script VM (`EnemyAIData.bin`, `SummonAIData.bin`, `NPCAIData.bin`), (2) `.rdata` random enemy attack and random skill move tables, (3) `floor_parameters.zip` / `floor_maps.zip` dungeon encounter, zone, and `.adv.bin` opcode `0x1F` triggers, and (4) Aquaplus `.pck` container and binary struct layouts read by `Parameter::*` loaders.

---

## 1. Enemy, Summon & NPC AI Script VM (`Battle::CBattleAI2`)

### M10.01 AI Archive Framing (`EnemyAIData.bin`, `SummonAIData.bin`, `NPCAIData.bin`) & `CBattleAI2::Task_s` Init

**Binary VA(s):** `0x45e590..0x45e5eb`, `0x463ce1..0x463d50`, `0x464a81..0x464af0`, `0x552120..0x5521c5`, `0x5521d0..0x552275`, `0x552280..0x552325`, `0x430390..0x430500`, `0x430aa0..0x430d50`
**Calls:** `0x507310` (`std::map::find`), `0x5c5b30` (heap alloc), `0x606810` (`memcpy`), `0x552410` (AI map insert), `0x61edf4` (`__RTDynamicCast`), `0x431690` (`_Command`)
**CalledBy:** `0x45e590` (`Enemy.pck` loader), `0x463cd9` (`NPC.pck` loader), `0x464a79` (`Summon.pck` loader), `CBattleBase` battle unit setup (`0x430390`)

**Typed Pseudocode:**
```text
// 1. Archive Framing (identical for EnemyAIData.bin, SummonAIData.bin, NPCAIData.bin)
// Loaders:
//   0x552120 -> map [0x7381cc] (EnemyAIData.bin, from backups/Enemy/Enemy.pck/<id>.pck)
//   0x5521d0 -> map [0x7389ac] (SummonAIData.bin, from backups/Summon/Summon.pck/<id>.pck)
//   0x552280 -> map [0x7389a8] (NPCAIData.bin, from backups/NPC/NPC.pck/<id>.pck)
fn LoadAIBinary(raw: ptr<u8>, size: u32, targetMap: ptr<Map<u32, AIBuffer>>) -> void:
    let entityId: u32 = (u32(raw[0]) << 8) | u32(raw[1])     // 2-byte big-endian u16 ID
    if targetMap.find(entityId) != targetMap.end():
        return
    let payloadLen: u32 = size - 2                            // raw bytecode (terminated by 0xFF)
    let buf: ptr<u8> = HeapAllocZero(payloadLen)
    memcpy(buf, raw + 2, payloadLen)
    targetMap.insert(entityId, { id: entityId, bytecode: buf })

// 2. CBattleAI2::Task_s Initialization (0x430390)
// RTTI descriptors:
//   0x707d88 = CGameStatus (base)
//   0x707d5c = CGamePlayerStatusSummon
//   0x707d34 = CGamePlayerStatusNPC
//   0x707dfc = CGameEnemyStatus
fn CBattleAI2_Task_Init(task: ptr<Task_s>, battle: ptr<void>, unitMgr: ptr<void>,
                        unit: ptr<void>, status: ptr<CGameStatus>) -> void:
    task.battle    = battle         // +0x00
    task.unitMgr   = unitMgr        // +0x04
    task.unit      = unit           // +0x08
    task.status    = status         // +0x0c
    task.asSummon  = dynamic_cast<CGamePlayerStatusSummon*>(status)  // +0x10
    task.asNPC     = dynamic_cast<CGamePlayerStatusNPC*>(status)     // +0x14
    task.asEnemy   = dynamic_cast<CGameEnemyStatus*>(status)         // +0x18
    task.isPlayerSide = (task.asEnemy == NULL)                       // +0x1c (1=Summon/NPC, 0=Enemy)
    task.bytecode  = NULL                                            // +0x20

    if task.asSummon != NULL:
        let key: u32 = u32(task.asSummon[+0x170])   // SummonId
        task.bytecode = LookupMap([0x7389ac], key)  // node+0x1c = bytecode ptr
    else if task.asNPC != NULL:
        let key: u32 = u32(task.asNPC[+0x170])      // NpcId
        task.bytecode = LookupMap([0x7389a8], key)
    else if task.asEnemy != NULL:
        let key: u32 = u32(task.asEnemy[+0x9c])     // EnemyId
        task.bytecode = LookupMap([0x7381cc], key)

    // Parse entire bytecode stream once into:
    //   task.globalRules (vector<CommandNode> at +0x2c..+0x34): rules encountered before any opcode 0
    //   task.sets (std::map<u32, SetStruct> at +0x24): keyed by setId from opcode 0
    // Loop stops when *cursor == 0xFF (sentinel byte at 0x430c54 / 0x430d3c).
    // RNG calls: 0.
```

**Program Evidence:**
```asm
0045e5c6  mov      eax, dword ptr [esi]
0045e5cb  push     1
0045e5cd  push     0x654f74    ; 'EnemyAIData.bin'
0045e5d9  call     dword ptr [eax + 0x10]
0045e5dc  mov      edx, dword ptr [ebp - 0x10]
0045e5e0  mov      ecx, dword ptr [ebp + 0xc]
0045e5e3  call     0x552120
00552125  movzx    ebp, byte ptr [ecx]
00552128  lea      eax, [ecx + 2]
00552131  movzx    eax, byte ptr [ecx + 1]
0055213e  shl      ebp, 8
00552141  or       ebp, eax
00552163  add      ebx, -2
004303b5  push     0x707d5c
004303bf  push     0x707d88
004303d3  call     0x61edf4
004303da  push     0x707d34
004303ea  call     0x61edf4
004303f1  push     0x707dfc
00430401  call     0x61edf4
0043040e  mov      dword ptr [ebx + 0x18], edx
00430411  test     edx, edx
00430413  mov      dword ptr [ebx + 0x20], 0
0043041a  sete     cl
0043041d  mov      byte ptr [ebx + 0x1c], cl
```

---

### M10.02 AI Bytecode Instruction Format, `_Command` Parser (`0x431964`) & Action-Word Bitflags

**Binary VA(s):** `0x431690..0x4319cc`, `0x4319d0..0x431a98`, `0x432fd0..0x4330e0`
**Calls:** `0x4319d0` (nested action-word reader), `0x434940` (`sets.find`), `0x433080` (attackId-to-slot resolver), `0x604bc0` (`memset`), `0x5b0480` (assert)
**CalledBy:** `0x430aa0` (`CBattleAI2::Task_s::_Initialize`), `0x4319d0` (recursive on bit `0x1000`)

**Typed Pseudocode:**
```text
// Parsed CommandNode struct: 0x24 (36) bytes
//   +0x00: u32 opcode      (0..15; 8 and >15 assert 'Not found AI command. %d\n')
//   +0x04: u32 arg0
//   +0x08: u32 arg1
//   +0x0c: u32 arg2        (often actionWord or once)
//   +0x10: u32 arg3        (often once or switch)
//   +0x14: u32 arg4        (often switch)
//   +0x18: ptr<CommandNode> nested   (non-NULL iff actionWord & 0x1000 != 0)
//   +0x1c: u32 cmdIndex    (sequential parsed rule counter)
//   +0x20: u8  onceFired   (initialized 0; set to 1 when once-flagged rule fires)
//
// SetStruct (value of task.sets map at +0x24):
//   +0x00..+0x3f: u32 weights[16]    (u8 weights zero-extended to u32)
//   +0x40..+0x48: vector<CommandNode> rules
//   +0x4c:        u8  visited        (reset to 0 at start of every turn)

// Action-Word Bitmask Decoding (big-endian u16 read by 0x4319d0, interpreted by 0x432fd0 / 0x433050):
//   bit 12 (0x1000): NESTED_COND  -> allocate 0x24-byte child at node.nested,
//                                    recursively call _Command(child, cursor, subOpcode = word & 0x0FFF)
//                                    Because subMode != 0xFF, nested nodes omit trailing (once, switch) bytes!
//   bit 13 (0x2000): SWITCH_SET   -> targetSetId = word & 0x0FFF
//   bit 14 (0x4000): SLOT_INDEX   -> attackSlot  = word & 0x3FFF (0..15 into entity's attack table)
//   bit 15 (0x8000): ATTACK_ID    -> attackId    = word & 0x3FFF (resolved to slot via 0x433080)

fn CBattleAI2_ParseCommand(task: ptr<Task_s>, outNode: ptr<CommandNode>,
                           cursor: ptr<ptr<u8>>, subMode: u32) -> bool:
    let op: u32 = if subMode == 0xFF { read_u8(cursor) } else { subMode }
    outNode.opcode = op
    if op > 15:
        Assert("Not found AI command. %d\n", op)

    // Complete 16-entry jump table at 0x431964:
    match op:
        case 0:
            // Define Action Set: u8 setId, u8 weights[16]
            let setId: u32 = read_u8(cursor)
            let w: u32[16]
            for i in 0..15:
                w[i] = u32(read_u8(cursor))
            if setId not in task.sets:
                task.sets[setId] = SetStruct{ weights: w, rules: [], visited: 0 }
            task.currentParsedSetId = setId   // [task+0x100]
            return false                      // NOT appended to rule vector
        case 1:
            // Target Override: u16be skillRef (0x4000|slot or 0x8000|atkId), u8 targetMode (0..15)
            outNode.arg0 = read_u16be(cursor)
            outNode.arg1 = read_u8(cursor)
            return true                       // No trailing once/switch bytes
        case 2, 5, 6, 15:
            // 16-bit parameter + actionWord (+ once, switch if top-level)
            outNode.arg0 = read_u16be(cursor)
            outNode.arg1 = ReadActionWord(task, outNode, cursor)   // 0x4319d0
            if subMode == 0xFF:
                outNode.arg2 = read_u8(cursor)   // once flag
                outNode.arg3 = read_u8(cursor)   // switch stop flag
            return true
        case 3, 10, 12, 13, 14:
            // Source comparison: u8 srcType (0..11), u8 threshold, actionWord (+ once, switch if top-level)
            outNode.arg0 = read_u8(cursor)
            outNode.arg1 = read_u8(cursor)
            outNode.arg2 = ReadActionWord(task, outNode, cursor)
            if subMode == 0xFF:
                outNode.arg3 = read_u8(cursor)   // once flag
                outNode.arg4 = read_u8(cursor)   // switch stop flag
            return true
        case 4, 11:
            // Source existence: u8 srcType (0..11), actionWord (+ once, switch if top-level)
            outNode.arg0 = read_u8(cursor)
            outNode.arg1 = ReadActionWord(task, outNode, cursor)
            if subMode == 0xFF:
                outNode.arg2 = read_u8(cursor)   // once flag
                outNode.arg3 = read_u8(cursor)   // switch stop flag
            return true
        case 7:
            // Skill usage count: u16be skillRef, u8 minCount, actionWord (+ once, switch if top-level)
            outNode.arg0 = read_u16be(cursor)
            outNode.arg1 = read_u8(cursor)
            outNode.arg2 = ReadActionWord(task, outNode, cursor)
            if subMode == 0xFF:
                outNode.arg3 = read_u8(cursor)   // once flag
                outNode.arg4 = read_u8(cursor)   // switch stop flag
            return true
        case 8:
            Assert("Not found AI command. %d\n", 8)
        case 9:
            // Dead ally check (Summon/NPC only): actionWord (+ once, switch if top-level)
            outNode.arg0 = ReadActionWord(task, outNode, cursor)
            if subMode == 0xFF:
                outNode.arg1 = read_u8(cursor)   // once flag
                outNode.arg2 = read_u8(cursor)   // switch stop flag
            return true
    // RNG calls: 0.
```

**Program Evidence:**
```asm
004316c2  cmp      edi, 0xff
004316c8  jne      0x4316d5
004316ca  mov      al, byte ptr [edx]
004316cc  inc      edx
004316d0  movzx    eax, al
004316d3  jmp      0x4316d7
004316d5  mov      eax, edi
004316da  mov      dword ptr [esi], eax
004316dc  cmp      eax, 0xf
004316df  ja       0x431949
004316e5  jmp      dword ptr [eax*4 + 0x431964]
00431701  lea      edi, [edx + 1]
00431704  movzx    eax, byte ptr [edx]
00431726  mov      al, byte ptr [edi]
00431728  inc      edi
00431729  movzx    eax, al
0043172c  mov      dword ptr [ebp + ecx*4 - 0x6c], eax
00431730  inc      ecx
00431731  cmp      ecx, 0x10
00431734  jb       0x431726
```

---

### M10.03 AI VM Entry (`0x43d420`), Evaluation Loop (`0x430f10`), Weighted Set Selection & Fallback Basic Attack (`0x4347a0`)

**Binary VA(s):** `0x43d420..0x43d5b0`, `0x430f10..0x431205`, `0x4313ba..0x431685`, `0x4347a0..0x43485a`
**Calls:** `0x430f10` (`Task_s::Run`), `0x431aa0` (`_Check`), `0x490790` (`GlobalRng::Rand`), `0x433200` (slot-to-attackId), `0x4347a0` (`_SelectNormalAttack`), `0x4183d0` (`SetAttackRange`), `0x417cd0` (`SetHitCount`), `0x43b0d0` (`_SelectTarget`), `0x43bab0` (breath/type-3 target merger), `0x434990` (`sets[id]`)
**CalledBy:** `CBattleBase` enemy/summon/NPC turn action chooser (`0x43d420`)

**Typed Pseudocode:**
```text
// 1. Entry Point (0x43d420)
fn CBattleBase_SelectAIAction(this: ptr<CBattleBase>, outAction: ptr<Action_s>, unitId: u32) -> void:
    let unit: ptr<BattleUnit> = this.GetUnit(unitId)          // vtable+0x38
    let aiObj: ptr<void> = unit[+0x110]
    if aiObj != NULL:
        if CBattleAI2_Task_Run(aiObj + 0x14):                 // 0x430f10
            return                                            // Action_s filled by AI VM
    // Fallback when aiObj == NULL or Task_Run returns false:
    outAction.Init(unit.unitId)                               // 0x41b090
    // Try CGameStatus::vtable+0x138 (always returns false on CGameEnemyStatus at 0x4d6e50):
    if !unit.status.vtable_138(&attackId, &overrideTargets):
        attackId = 0                                          // EnemyAttack ID 0 fallback
    outAction.attackId = attackId
    // Sets Action_s+0x38 = (EnemyAttack[attackId].targetType == 3) at 0x43d593.

// 2. Main AI Evaluation Loop (0x430f10)
fn CBattleAI2_Task_Run(task: ptr<Task_s>) -> bool:
    if task.bytecode == NULL:
        // No AI bytecode loaded: tries vtable+0x138 for Enemy, else _SelectNormalAttack (slot 0)
        goto NoBytecodeFallback (0x4313ba)

    // Step A: Per-turn state reset (0x430f56..0x430fb8)
    task.activeSetId = 0                                      // [task+0x38]
    for setId in 0 .. (task.sets.size() - 1):
        task.sets[setId].visited = 0                          // [set+0x4c]
    for slot in 0..15:
        task.targetOverrides[slot].clear()                    // 16 vectors at [task+0x3c..+0xf8], stride 0x0c
    task.selectedAttackId = -1                                // [task+0xfc]

    // Step B: Global rules scan (0x430fb9..0x431017)
    // Stops on the first rule where _Check returns true.
    for rule in task.globalRules:                             // stride 0x24
        if CBattleAI2_Check(task, rule, checkOnce=1, subCheck=0):
            break

    // Step C: Weighted set loop with visited-cycle guard (0x431018..0x4311ea)
    while task.selectedAttackId == -1:
        let curSetId: u32 = task.activeSetId
        if curSetId not in task.sets:
            break
        let set: ptr<SetStruct> = &task.sets[curSetId]
        if set.visited != 0:
            break

        // Weighted random pick over 16 slots (prefix sum, 1 RNG call)
        let prefix: u32[16]
        let totalWeight: u32 = 0
        for i in 0..15:
            totalWeight += set.weights[i]
            prefix[i] = totalWeight
        let r: u32 = GlobalRng.Rand(totalWeight)              // 0x490790 (1 RNG call per set iteration)
        let chosenSlot: u32 = 0
        while chosenSlot < 16 and !(r < prefix[chosenSlot]):  // strict `<` (`jb`)
            chosenSlot += 1
        task.selectedAttackId = SlotToAttackId(task, chosenSlot) // 0x433200

        // Evaluate set-local rules; may override selectedAttackId, populate targetOverrides,
        // or change task.activeSetId (actionWord & 0x2000).
        for rule in set.rules:
            if CBattleAI2_Check(task, rule, checkOnce=1, subCheck=0):
                break

        // If a rule switched task.activeSetId, mark old set visited, discard rolled attack, and loop:
        if task.activeSetId != curSetId:
            set.visited = 1
            task.selectedAttackId = -1

    // Step D: Fallback basic attack (slot 0) if no attack selected (0x4311eb)
    if task.selectedAttackId == -1:
        CBattleAI2_SelectNormalAttack(task)                   // 0x4347a0

    // Step E: Enemy-only Freeze/Silence/Shadow Sew override + Breath (3) bypass (see M10.07)
    // Step F: Action_s construction & target resolution (0x431451..0x431685):
    //   ea = EnemyAttackParam[task.selectedAttackId]
    //   actionType = ((ea.flags >> 2) & 1) ? 9 (Magic) : 8 (EnemyAttack/Phys)
    //   SetAttackRange(action, ...)  [0x4183d0]; SetHitCount(action, ...) [0x417cd0]
    //   If targetOverrides[slot] is non-empty AND primary target is alive & not full-petrified
    //     (vtable+0x38() == 0 && vtable+0xc8() == 0): use override target;
    //   Else: call CBattleBase::_SelectTarget (0x43b0d0).
    //   Then call 0x43bab0 (expands/merges target list when ea.targetType == 3).

// 3. Fallback Basic Attack _SelectNormalAttack (0x4347a0)
fn CBattleAI2_SelectNormalAttack(task: ptr<Task_s>) -> void:
    task.selectedAttackId = -1
    if task.asSummon != NULL:
        task.selectedAttackId = SummonParam[task.asSummon[+0x170]].attacks[0].attackId  // mem+0x58 (file+0x40)
    else if task.asNPC != NULL:
        task.selectedAttackId = NPCParam[task.asNPC[+0x170]].attacks[0].attackId        // mem+0x54 (file+0x3c)
    else if task.asEnemy != NULL:
        task.selectedAttackId = EnemyParam[task.asEnemy[+0x9c]].attacks[0]              // mem+0xc8 (file+0xb0)
```

**Program Evidence:**
```asm
0043d449  mov      ecx, dword ptr [ebx + 0x110]
0043d44f  test     ecx, ecx
0043d451  je       0x43d463
0043d453  add      ecx, 0x14
0043d456  call     0x430f10
0043d45b  test     al, al
0043d45d  jne      0x43d5a3
00430f33  cmp      dword ptr [esi + 0x20], 0
00430f37  je       0x4313ba
00430f56  mov      dword ptr [esi + 0x38], 0
00430f77  call     0x434990
00430f7c  mov      byte ptr [eax + 0x4c], 0
00430fb3  mov      dword ptr [edi], 0xffffffff
00430fe5  call     0x431aa0
00430fea  test     al, al
00430fec  jne      0x431012
004347a9  mov      dword ptr [esi + 0xfc], 0xffffffff
004347d8  mov      eax, dword ptr [eax + 0x58]
004347db  mov      dword ptr [esi + 0xfc], eax
0043480e  mov      eax, dword ptr [eax + 0x54]
00434844  mov      eax, dword ptr [eax + 0xc8]
0043484a  mov      dword ptr [esi + 0xfc], eax
```

---

### M10.04 AI Condition Evaluator `_Check` (`0x431aa0`, Opcodes `0..15`) & Enemy vs Summon vs NPC Divergences

**Binary VA(s):** `0x431aa0..0x432688`
**Calls:** `0x433350` (`_SelectTargetMode`), `0x433080` (attackId-to-slot), `0x432690` (`_EvalSource`), `0x432fd0` / `0x433050` (action-word executor), `0x509d80` (battle action log), `0x508700` (Summon skill use count), `0x508800` (NPC skill use count), `0x5732f0` (Summon useLimit), `0x55d340` (NPC useLimit), `0x47e390` (active command query), `0x43af10` (party unit list), `0x43b330` (ETC/doll unit list)
**CalledBy:** `0x430f10` (`Task_s::Run`), `0x431aa0` (recursive on nested `0x1000` nodes)

**Typed Pseudocode:**
```text
// Returns true iff the rule matched AND its action-word signals stopping further rule scans
// (direct attack override, or set switch when switchFlag == 0 / stopping rule).
fn CBattleAI2_Check(task: ptr<Task_s>, node: ptr<CommandNode>, checkOnce: u8, subCheck: u8) -> bool:
    // If checkOnce != 0 and node.onceFlag != 0 and node.onceFired != 0: return false immediately.
    let condPassed: bool = false
    match node.opcode:
        case 0:
            // Set lookup no-op (always returns false)
            return false
        case 1:
            // Target Override side-effect: resolves skillRef (0x4000=slot, 0x8000=attackId->slot)
            let slot: u32 = if (node.arg0 & 0x4000) != 0 { node.arg0 & 0x3FFF }
                            else if (node.arg0 & 0x8000) != 0 { AttackIdToSlot(task, node.arg0 & 0x3FFF) }
                            else { 0 }
            CBattleAI2_SelectTargetMode(task, slot, node.arg1, node.cmdIndex)   // 0x433350
            return false                                                         // never stops scan
        case 2:
            // Turn count (1-based actor action count): (battleUnit[+0xb8] + 1) <= arg0
            condPassed = (u32(task.unit[+0xb8]) + 1) <= node.arg0                // unsigned `jbe`
        case 3:
            let v: i32 = CBattleAI2_EvalSource(task, node.arg0)
            condPassed = (v != -1) && (u32(v) <= node.arg1)                      // unsigned `<=` (`ja` fails)
        case 4, 11:
            // Opcode 11 jumps directly into Opcode 4 at 0x43243c (identical behavior)
            let v: i32 = CBattleAI2_EvalSource(task, node.arg0)
            condPassed = (v != -1)
        case 5:
            // Immediately after skill arg0: scans battle log (0x509d80) for entry.type == 0x0E
            // matching actor identity (+0x08 enemyId, +0x0c summonId, +0x10 npcId).
            // True iff the LAST matching entry had entry.attackId (+0x18) == resolved(arg0).
            condPassed = (LastActionLogAttackIdForActor(task) == ResolveSkillRef(task, node.arg0))
        case 6:
            // Skill arg0 currently active:
            //   (1) Self has CCommandTurnBase with vtable+0xb0() != 0 OR Song (vtable+0x6c())
            //   (2) Opposing side has Dance (vtable+0x70()) OR Geass (vtable+0x78()) from this skill
            //   (3) If EnemyAttack[atkId] contains command 0x92 (146, Summon/Doll):
            //       any unit in 0x43b330 (unitId 2000..2999) owned by self with summonSkill == atkId
            condPassed = IsSkillActive(task, ResolveSkillRef(task, node.arg0))
        case 7:
            // Skill battle use count >= arg1 (unsigned `jb` fails).
            // When subCheck == 0 and task.selectedAttackId != -1, ALSO requires atkId == task.selectedAttackId.
            // Deduplicates multi-hit log entries by entry.actionSeq (+0x14).
            // Summon calls 0x508700; NPC calls 0x508800; Enemy scans log inline.
            condPassed = (GetBattleUseCount(task, atkId) >= node.arg1)
        case 9:
            // Dead ally exists: ONLY valid when task.isPlayerSide != 0 (0x43232e)!
            // Enemies ALWAYS evaluate opcode 9 as false!
            if task.isPlayerSide == 0:
                condPassed = false
            else:
                let allies = GetPartyUnits(task.unitMgr, 0, 0, 0)                // 0x43af10
                condPassed = any(u.vtable_38() != 0 for u in allies)             // IsDead
        case 10:
            let v: i32 = CBattleAI2_EvalSource(task, node.arg0)
            condPassed = (v != -1) && (u32(v) > node.arg1)                       // unsigned `>` (`jbe` fails)
        case 12:
            let v: i32 = CBattleAI2_EvalSource(task, node.arg0)
            condPassed = (v != -1) && (u32(v) >= node.arg1)                      // unsigned `>=` (`jb` fails)
        case 13:
            let v: i32 = CBattleAI2_EvalSource(task, node.arg0)
            condPassed = (v != -1) && (u32(v) < node.arg1)                       // unsigned `<` (`jae` fails)
        case 14:
            let v: i32 = CBattleAI2_EvalSource(task, node.arg0)
            condPassed = (v != -1) && (u32(v) == node.arg1)                      // `==` (`jne` fails)
        case 15:
            // Summon / NPC per-skill use-limit reached: usageCount >= useLimit.
            // Summon: useLimit at SummonParam+0x5c (0x5732f0), count via 0x508700.
            // NPC:    useLimit at NPCParam+0x58 (0x55d340),    count via 0x508800.
            // Enemy:  triggers fatal assertion at 0x4325f0!
            condPassed = (GetUseCount(task, atkId) >= GetUseLimit(task, atkId))

    if !condPassed:
        return false

    // Action-word execution on match:
    if (actionWord & 0x1000) != 0:
        // Nested AND condition: recursively evaluate node.nested with (checkOnce=0, subCheck=1)
        let ok: bool = CBattleAI2_Check(task, node.nested, checkOnce=0, subCheck=1)
        if !ok: return false
        if onceFlag != 0: node.onceFired = 1
        return (switchFlag == 0) ? true : false
    if (actionWord & 0x2000) != 0:
        task.activeSetId = actionWord & 0x0FFF
        if onceFlag != 0: node.onceFired = 1
        // switchFlag == 0 -> return true (stop scanning current rule list);
        // switchFlag != 0 -> return false (continue scanning remaining rules in current list).
        return (switchFlag == 0)
    if (actionWord & 0x4000) != 0:
        task.selectedAttackId = SlotToAttackId(task, actionWord & 0x3FFF)
        if onceFlag != 0: node.onceFired = 1
        return true
    if (actionWord & 0x8000) != 0:
        task.selectedAttackId = actionWord & 0x3FFF
        if onceFlag != 0: node.onceFired = 1
        return true
    return false

// Summary of Enemy vs Summon vs NPC AI Divergences:
// 1. Archive & Map: Enemy=[0x7381cc] keyed by status+0x9c; Summon=[0x7389ac] status+0x170; NPC=[0x7389a8] status+0x170.
// 2. Side bit [task+0x1c]: 0 for Enemy (allies=enemies, opps=party); 1 for Summon/NPC (allies=party, opps=enemies).
// 3. Opcode 9 (Dead Ally): functional for Summon/NPC; unconditionally false for Enemy (0x43232e).
// 4. Opcode 15 (Use Limit): functional for Summon/NPC; fatal assert for Enemy (0x4325f0).
// 5. Freeze/Silence/Shadow Sew Override & Breath-3 Bypass (0x431206): executed ONLY for Enemy; skipped for Summon/NPC.
```

**Program Evidence:**
```asm
00431ac9  mov      eax, dword ptr [edi]
00431acb  test     eax, eax
00431acd  jne      0x431b09
00431b09  cmp      eax, 1
00431b0c  jne      0x431b5f
00431b0e  mov      eax, dword ptr [edi + 4]
00431b13  test     eax, 0x4000
00431b18  je       0x431b24
00431b1c  and      ecx, 0xffff3fff
00431b24  test     eax, 0x8000
00431b29  je       0x431b3a
00431b2b  and      eax, 0xffff3fff
00431b33  call     0x433080
00431b3a  push     dword ptr [edi + 0x1c]
00431b3d  push     dword ptr [edi + 8]
00431b40  push     ecx
00431b43  call     0x433350
```

---

### M10.05 AI Source Evaluator (`0x432690`, Complete 12-Case Jump Table `0x432fa0`) & Percent Rounding (`0x430700`)

**Binary VA(s):** `0x430700..0x43087f`, `0x432690..0x432fcc`
**Calls:** `0x430700` (HP/TP percent helper), `0x430770` (min-percent across unit vector), `0x61e650` (`round_f32_to_i32`), `0x43af10` (get player-side units), `0x43b1d0` (get enemy-side units), `0x43bc10` (is unit chanting), `0x606150` (`memmove`)
**CalledBy:** `0x431aa0` (`_Check` opcodes `3`, `4`, `10`, `11`, `12`, `13`, `14`)

**Typed Pseudocode:**
```text
// 1. Percentage Rounding Helper (0x430700)
fn CalcUnitPercent(cur: u32, maxVal: u32) -> i32:
    if maxVal == 0:
        return 100
    let ratio: f32 = (f32(cur) / f32(maxVal)) * 100.0f
    return round_f32_to_i32(ratio)                            // call 0x61e650

// 2. Min-Percent Helper (0x430770)
// Returns minimum CalcUnitPercent across units (isTP=0 -> HP, isTP=1 -> TP), or -1 if vector empty.
//
// 3. Living-or-Petrified Filter (used by Sources 1..4):
//   Keeps unit iff (unit.vtable+0xe8() != 0) OR (unit.vtable+0xc8() != 0)
//   where vtable+0xe8 = alive & not full-petrified, vtable+0xc8 = full-petrified.
//   Effect: removes dead units, keeps living AND full-petrified units.

// 4. Complete 12-Case Source Jump Table at 0x432fa0 (cases 0..11; >11 returns -1):
//   "Allies"    = isPlayerSide ? GetParty(0x43af10) : GetEnemies(0x43b1d0)
//   "Opponents" = isPlayerSide ? GetEnemies(0x43b1d0) : GetParty(0x43af10)
//   Ailment vtable slots on CGameStatus:
//     +0x7c = HasTrueAilment (0x4faf20)
//     +0x84 = HasBuff        (0x4fb010)
//     +0x8c = HasDebuff      (0x4fb100)
fn CBattleAI2_EvalSource(task: ptr<Task_s>, srcType: u32) -> i32:
    if srcType > 11: return -1
    match srcType:
        case 0:  // 0x4326c9: Self HP%
            return CalcUnitPercent(task.status.CurHP(), task.status.MaxHP())
        case 1:  // 0x4326ed: Lowest Ally HP% (living or petrified; -1 if none)
            return MinPercent(FilterAliveOrPetrified(Allies(task)), isTP=0)
        case 2:  // 0x4327a0: Lowest Opponent HP% (living or petrified; -1 if none)
            return MinPercent(FilterAliveOrPetrified(Opponents(task)), isTP=0)
        case 3:  // 0x432850: Lowest Ally TP% (living or petrified; -1 if none)
            return MinPercent(FilterAliveOrPetrified(Allies(task)), isTP=1)
        case 4:  // 0x432900: Lowest Opponent TP% (living or petrified; -1 if none)
            return MinPercent(FilterAliveOrPetrified(Opponents(task)), isTP=1)
        case 5:  // 0x4329b0: Any Ally has Ailment (vt+0x7c) OR Debuff (vt+0x8c) -> 1 else -1
            return any(u.vt_7c() || u.vt_8c() for u in Allies(task)) ? 1 : -1
        case 6:  // 0x432a52: Any Opponent has Ailment (vt+0x7c) OR Debuff (vt+0x8c) -> 1 else -1
            return any(u.vt_7c() || u.vt_8c() for u in Opponents(task)) ? 1 : -1
        case 7:  // 0x432b52: Any Opponent is Chanting (0x43bc10: state==3 party / 9 enemy) -> 1 else -1
            return any(IsChanting(task.unitMgr, u) for u in Opponents(task)) ? 1 : -1
        case 8:  // 0x432c46: Any Back-Row Opponent exists (rowFilter=2) -> 1 else -1
            return (len(OpponentsByRow(task, row=2)) > 0) ? 1 : -1
        case 9:  // 0x432cfa: Any Front-Row Opponent exists (rowFilter=1) -> 1 else -1
            return (len(OpponentsByRow(task, row=1)) > 0) ? 1 : -1
        case 10: // 0x432daa: Any Opponent has Buff (vt+0x84) -> 1 else -1
            return any(u.vt_84() for u in Opponents(task)) ? 1 : -1
        case 11: // 0x432e92: Any Ally has Debuff (vt+0x8c) -> 1 else -1
            return any(u.vt_8c() for u in Allies(task)) ? 1 : -1
    // RNG calls: 0.
```

**Program Evidence:**
```asm
00432715  push     1
00432717  push     0
00432719  push     1
0043271b  push     eax
0043271c  call     0x43af10
00432721  jmp      0x43272d
00432728  call     0x43b1d0
00432744  mov      eax, dword ptr [eax + 0xe8]
0043274a  call     eax
0043274c  test     al, al
0043274e  je       0x432758
0043275c  mov      eax, dword ptr [eax + 0xc8]
00432762  call     eax
00432764  test     al, al
00432766  je       0x432770
00432789  push     0
0043278f  call     0x430770
```

---

### M10.06 AI Target Override Evaluator (`0x433350`, Complete 16-Case Jump Table `0x434754`) & Target 9 Ailment Waterfall

**Binary VA(s):** `0x433350..0x434794`, `0x430880..0x430a98`
**Calls:** `0x430770` (min pct), `0x430880` (filter `pct <= minPct`), `0x4309a0` / `0x4309f0` / `0x430a50` (max ailment+debuff count), `0x490790` (`GlobalRng::Rand`), `0x43af10` (party units), `0x43b1d0` (enemy units), `0x43bc10` (is chanting), `0x47b220` (command factory for Target 8), `0x434880` (dead ally query for Target 15)
**CalledBy:** `0x431b43` (`_Check` opcode `1`)

**Typed Pseudocode:**
```text
// Populates per-slot target override vector at [task + (slot + 5) * 12] (i.e. +0x3c + slot*0x0c).
// First clears the slot's existing vector. On any non-empty candidate set of size N,
// draws 1 RNG call: idx = GlobalRng.Rand(N) (0x490790) and pushes candidates[idx].
// If candidates is empty, slot vector remains empty (0 RNG calls) and normal targeting runs.

fn CBattleAI2_SelectTargetMode(task: ptr<Task_s>, slot: u32, targetMode: u32, cmdIdx: u32) -> void:
    let outVec: ptr<Vec<ptr<CGameStatus>>> = &task.targetOverrides[slot]
    outVec.clear()
    if targetMode > 15: return

    // Complete 16-Case Target Jump Table at 0x434754 (cases 0..15):
    let candidates: Vec<ptr<CGameStatus>> = match targetMode:
        case 0:  // Ally with lowest HP% (living/petrified; keeps pct <= minPct)
            FilterMinPct(FilterAliveOrPetrified(Allies(task)), isTP=0)
        case 1:  // Opponent with lowest HP% (living/petrified)
            FilterMinPct(FilterAliveOrPetrified(Opponents(task)), isTP=0)
        case 2:  // Ally with lowest TP% (living/petrified)
            FilterMinPct(FilterAliveOrPetrified(Allies(task)), isTP=1)
        case 3:  // Opponent with lowest TP% (living/petrified)
            FilterMinPct(FilterAliveOrPetrified(Opponents(task)), isTP=1)
        case 4:  // Ally with highest count of statuses where (vt+0x68 || vt+0x5c) (ailment+debuff)
            FilterMaxStatusCount(Allies(task))                // 0x4309a0 / 0x430a50
        case 5:  // Opponent with highest ailment+debuff count
            FilterMaxStatusCount(Opponents(task))
        case 6:  // Chanting Opponent (0x43bc10)
            [u for u in Opponents(task) if IsChanting(task.unitMgr, u)]
        case 7:  // Back-Row Opponent (rowFilter=2)
            OpponentsByRow(task, row=2)
        case 8:  // Ally NOT currently affected by all CCommandTurnBase commands of this skill
            // Instantiates each command in EnemyAttack[slot] having (flags & 4) via 0x47b220;
            // counts totalTurnCmds; keeps allies whose active matching turn-cmd count < totalTurnCmds.
            [u for u in Allies(task) if ActiveMatchingTurnCmdCount(u, slot) < TotalTurnCmds(slot)]
        case 9:  // Ally with highest-severity ailment — STRICT 9-TIER PRIORITY WATERFALL (0x433e67..0x4342c4):
            //   Tier 1: vt+0xcc() != 0  (Slow, cmd 0x7a / 122)
            //   Tier 2: vt+0xc8() != 0  (Full Petrify, cmd 0x78 / 120, stage >= 3)
            //   Tier 3: vt+0xc4() != 0  (Partial Petrify, cmd 0x78 / 120, stage < 3)
            //   Tier 4: vt+0xbc() != 0  (Sleep, cmd 0x74 / 116)
            //   Tier 5: vt+0xb4() != 0  (Freeze, cmd 0x72 / 114)
            //   Tier 6: vt+0xc0() != 0  (Silence, cmd 0x75 / 117)
            //   Tier 7: vt+0xb8() != 0  (Paralysis, cmd 0x73 / 115)
            //   Tier 8: vt+0xb0() != 0  (Poison, cmd 0x71 / 113)
            //   Tier 9: vt+0x8c() != 0  (Any Debuff)
            // First non-empty tier wins and breaks immediately to uniform tie-break!
            FirstNonEmptyTier(Allies(task), [vt_cc, vt_c8, vt_c4, vt_bc, vt_b4, vt_c0, vt_b8, vt_b0, vt_8c])
        case 10: // Front-Row Opponent (rowFilter=1)
            OpponentsByRow(task, row=1)
        case 11: // Opponent with Buff (vt+0x84)
            [u for u in Opponents(task) if u.vt_84()]
        case 12: // Ally with Debuff (vt+0x8c)
            [u for u in Allies(task) if u.vt_8c()]
        case 13: // Ally with True Ailment (vt+0x7c, includeDead=0)
            [u for u in Allies(task) if u.vt_7c()]
        case 14: // Opponent with True Ailment (vt+0x7c)
            [u for u in Opponents(task) if u.vt_7c()]
        case 15: // Dead Ally (vt+0x38, queried with includeDead=1 via 0x434880)
            [u for u in Allies(task, includeDead=1) if u.vt_38()]

    if len(candidates) > 0:
        let pick: u32 = GlobalRng.Rand(u32(len(candidates)))  // 1 RNG call
        outVec.push_back(candidates[pick])
```

**Program Evidence:**
```asm
00433375  lea      eax, [edi + 5]
00433378  lea      eax, [eax + eax*2]
0043337b  lea      ecx, [ebx + eax*4]
0043337e  mov      eax, dword ptr [ecx]
00433380  mov      dword ptr [ecx + 4], eax
00433389  cmp      eax, 0xf
0043338c  ja       0x434742
00433393  jmp      dword ptr [eax*4 + 0x434754]
00433445  call     0x430770
00433451  call     0x430880
00433460  mov      ecx, dword ptr [0x816ce8]
0043346c  call     0x490790
00433ee4  mov      eax, dword ptr [eax + 0xcc]
00433eea  call     eax
00433eec  test     al, al
00433eee  je       0x433f13
00433f2a  cmp      eax, esi
00433f2c  jne      0x434252
```

---

### M10.07 Enemy Ailment Action Override, Breath (Command `3`) Bypass & Shadow Sew Non-Bypass

**Binary VA(s):** `0x431206..0x4313b5`
**Calls:** `0x507310` (`std::map::find` on `[0x7389d4]` EnemyAttackParam and `[0x7389d8]` EnemyParam), `CGameStatus::vtable+0xb4` (IsFrozen, cmd `0x72`/114), `CGameStatus::vtable+0xc0` (IsSilenced, cmd `0x75`/117), `CGameStatus::vtable+0xd0` (IsShadowSewn, cmd `0x7b`/123)
**CalledBy:** Inline stage of `CBattleAI2::Task_s::Run` (`0x430f10`)

**Typed Pseudocode:**
```text
// Executed ONLY for Enemies ([task+0x18] != NULL); Summons and NPCs jump directly to 0x431451!
fn CBattleAI2_ApplyEnemyAilmentOverride(task: ptr<Task_s>) -> void:
    if task.asEnemy == NULL:
        return

    let ea: ptr<EnemyAttackNode> = LookupMap([0x7389d4], task.selectedAttackId)
    let cmdCount: u32 = ea.cmdCount                           // mem+0x60 (file+0x48)

    // Scan commands[0 .. cmdCount-1] for command ID == 3 (Breath Attack):
    let hasBreathCmd3: bool = false
    for i in 0 .. (cmdCount - 1):
        if ea.cmds[i].id == 3:                                // mem+0x64 + i*0x0c (file+0x4c + i*0x0c)
            hasBreathCmd3 = true
            break

    // Breath (command 3) BYPASSES Freeze (vt+0xb4) AND Silence (vt+0xc0) (`jb 0x431371`):
    if !hasBreathCmd3:
        // 1. Freeze (cmd 0x72 / 114): blocks EnemyAttack with flags bit 1 (Physical/Skill)
        if task.asEnemy.vtable_b4():
            let curEA = LookupMap([0x7389d4], task.selectedAttackId)
            if ((curEA.flags >> 1) & 1) != 0:                 // mem+0x40 (file+0x28), bit 1
                task.selectedAttackId = EnemyParam[task.asEnemy[+0x9c]].attacks[0]  // mem+0xc8

        // 2. Silence (cmd 0x75 / 117): blocks EnemyAttack with flags bit 2 (Magic)
        if task.asEnemy.vtable_c0():
            let curEA = LookupMap([0x7389d4], task.selectedAttackId)
            if ((curEA.flags >> 2) & 1) != 0:                 // mem+0x40 (file+0x28), bit 2
                task.selectedAttackId = EnemyParam[task.asEnemy[+0x9c]].attacks[0]  // mem+0xc8

    // 3. Shadow Sew (cmd 0x7b / 123, vt+0xd0) at 0x431371:
    //    NOT bypassed by Breath (command 3)! Unconditionally forces slot 0 attack.
    if task.asEnemy.vtable_d0():
        task.selectedAttackId = EnemyParam[task.asEnemy[+0x9c]].attacks[0]          // mem+0xc8
    // RNG calls: 0.
```

**Program Evidence:**
```asm
00431231  cmp      dword ptr [eax + 0x60], edi
00431234  jbe      0x43128f
00431257  cmp      dword ptr [ebx + eax + 0x64], 3
0043125c  je       0x431289
004312a7  cmp      edi, dword ptr [eax + 0x60]
004312aa  jb       0x431371
004312b5  mov      eax, dword ptr [eax + 0xb4]
004312bb  call     eax
004312e1  mov      eax, dword ptr [eax + 0x40]
004312e4  shr      eax, 1
004312e6  test     al, 1
0043130b  mov      eax, dword ptr [eax + 0xc8]
00431311  mov      dword ptr [ebx], eax
00431318  mov      eax, dword ptr [eax + 0xc0]
0043131e  call     eax
0043133e  mov      eax, dword ptr [eax + 0x40]
00431341  shr      eax, 2
00431344  test     al, 1
00431376  mov      eax, dword ptr [eax + 0xd0]
0043137c  call     eax
004313ad  mov      eax, dword ptr [eax + 0xc8]
004313b3  mov      dword ptr [ebx], eax
```

---

## 2. Random Enemy Attack & Random Skill Move Tables

### M10.08 `.rdata` Random Enemy Attack (`0x64f1c0`) & Random Skill Tables (`0x64f8c0..0x64fbec`, `0x64f440..0x64f470`)

**Binary VA(s):** `0x41a6c6..0x41a7f9`, `0x41e330..0x41e5fc`, `0x42db00..0x42dc42`, `0x505ad0..0x505b5a`, `.rdata` `0x64f1c0..0x64f25b`, `0x64f440..0x64f46f`, `0x64f8c0..0x64fbeb`
**Calls:** `0x505ad0` (weighted prefix-sum selector), `0x490790` (`GlobalRng::Rand`), `CGameStatus::vtable+0x50` (passive check for `0x13b` / `315`), `0x61edf4` (`__RTDynamicCast` to `CGamePlayerStatusETCGenzimaru` `0x70855c`)
**CalledBy:** `CActionEnemyAttack::_CreatePattern` (`0x41a4a0`, case `17`), `CActionSkill::_CreatePattern` (`0x41e060`, cases `10`, `11`, `12`, `14`)

**Typed Pseudocode:**
```text
// 1. Universal 12-Byte Table Record & Weighted Picker (0x505ad0)
// struct RandomMoveEntry { i32 moveId; i32 sentinel; u32 weight; }  // sentinel == -1 (0xFFFFFFFF)
fn PickWeightedIndex(weights: ptr<u32>, count: u32) -> u32:
    let prefix: u32[count]
    let total: u32 = 0
    for i in 0 .. (count - 1):
        total += weights[i]
        prefix[i] = total
    let r: u32 = GlobalRng.Rand(total)                        // 0x490790 (1 RNG call)
    for i in 0 .. (count - 1):
        if r < prefix[i]:                                     // strict `<` (`jb`)
            return i
    return count

// 2. Enemy Attack Pattern 17 (0x41a6c6..0x41a7f9) -> Table 0x64f1c0 (13 entries, weight sum = 95!)
//   NOTE: Sum of weights is 95 (NOT 100), so GlobalRng.Rand(95) is called!
//   Entries (enemyAttackId, weight):
//     (2701/0xa8d,  5), (2702/0xa8e, 10), (2703/0xa8f,  5), (2704/0xa90, 10),
//     (2705/0xa91, 10), (2706/0xa92,  5), (2707/0xa93,  5), (2708/0xa94,  5),
//     (2709/0xa95, 10), (2710/0xa96, 10), (2711/0xa97,  5), (2712/0xa98, 10),
//     (2713/0xa99,  5)

// 3. Random Skill Base (CActionPatternRandomSkill 0x42db00)
fn CActionPatternRandomSkill_Init(this, normalTbl: ptr<RandomMoveEntry>,
                                  tjTbl: ptr<RandomMoveEntry>, count: u32) -> void:
    // Passive 315 (0x13b, Triple Joker) swaps normalTbl -> tjTbl (0x42db80..0x42db93):
    let hasTripleJoker: bool = actor.status.HasPassive(0x13b) // vtable+0x50(315)
    let tbl: ptr<RandomMoveEntry> = hasTripleJoker ? tjTbl : normalTbl
    let idx: u32 = PickWeightedIndex(extract_weights(tbl, count), count)
    this.selectedEntry = &tbl[idx]                            // [this+0x9c]

// 4. All 4 Random Skill Pattern Table Pairs (verified verbatim from .rdata):
//   Pattern 10 (0x41e330, count = 9, skill IDs 108..116 / 0x6c..0x74):
//     Normal 0x64f8c0 (sum=100): (108,10),(109,10),(110,10),(111,10),(112,10),(113,20),(114,10),(115,10),(116,10)
//     TJ     0x64f930 (sum=100): (108,12),(109,12),(110,12),(111,12),(112,12),(113,20),(114, 5),(115,10),(116, 5)
//
//   Pattern 11 (0x41e374, count = 11, skill IDs 117..127 / 0x75..0x7f):
//     Normal 0x64fa28 (sum=100): (117,10),(118,10),(119,10),(120,10),(121,10),(122,10),(123,10),(124, 5),(125, 5),(126,10),(127,10)
//     TJ     0x64f9a0 (sum=100): (117,10),(118,15),(119, 5),(120,10),(121,15),(122, 5),(123,10),(124, 5),(125, 5),(126, 5),(127,15)
//     SPECIAL OVERRIDE (0x41e3c2..0x41e4d9):
//       If selectedEntry.moveId == 0x79 (121):
//         Scan battle units where unit.isPlayerSide (+0x78) != 0 AND 2000 <= unit.unitId < 3000 (0x7d0..0xbb7).
//         If any such unit dynamic_casts to CGamePlayerStatusETCGenzimaru (0x70855c):
//           Replace selectedEntry with entry for skill 0x7d (125) from normal table 0x64fa28!
//
//   Pattern 12 (0x41e4db, count = 13, skill IDs 128..140 / 0x80..0x8c):
//     Normal 0x64fb50 (sum= 95!): (128, 5),(129,10),(130, 5),(131,10),(132,10),(133, 5),(134, 5),(135, 5),(136,10),(137,10),(138, 5),(139,10),(140, 5)
//     TJ     0x64fab0 (sum=100 ): (128,10),(129,10),(130,10),(131, 3),(132,10),(133, 7),(134, 3),(135,10),(136, 5),(137,12),(138, 3),(139,12),(140, 5)
//     NOTE: Normal Pattern 12 table 0x64fb50 has weight sum = 95 (NOT 100)!
//
//   Pattern 14 (0x41e55f, count = 2, skill IDs 141..142 / 0x8d..0x8e):
//     Normal 0x64f458 (sum=100): (141, 50), (142, 50)
//     TJ     0x64f440 (sum=100): (141, 70), (142, 30)
```

**Program Evidence:**
```asm
0041e342  push     9
0041e344  push     0x64f930
0041e349  push     0x64f8c0
0041e364  call     0x42db00
0041e387  push     0xb
0041e389  push     0x64f9a0
0041e398  push     0x64fa28
0041e3ad  call     0x42db00
0041e3c2  cmp      dword ptr [eax], 0x79
0041e3c5  jne      0x41e4af
0041e402  cmp      ecx, 0x7d0
0041e40a  cmp      ecx, 0xbb8
0042db89  mov      eax, dword ptr [eax + 0x50]
0042db8c  call     eax
0042db8e  mov      esi, dword ptr [ebp + 0x1c]
0042db91  test     al, al
0042db93  cmovne   esi, dword ptr [ebp + 0x20]
0042dbf1  call     0x505ad0
00505b2e  mov      ecx, dword ptr [0x816ce8]
00505b34  push     edx
00505b35  call     0x490790
00505b40  cmp      eax, dword ptr [ebx + esi*4]
00505b43  jb       0x505b4a
```

---

## 3. Dungeon Floor Parameters & Fixed-Battle Map Cell Triggers

### M10.09 Dungeon Floor Parameters (`floor_parameters.zip`): Relocator (`0x555560`), Encounter Groups (`0x58`), Areas (`0xd0`) & Zone Multipliers

**Binary VA(s):** `0x556170..0x5561dd`, `0x555560..0x5556cd`, `0x555b00..0x555c60`, `0x449927..0x4499b5`, `0x44fbb0..0x44fdd2`
**Calls:** `0x555560` (in-place pointer relocator), `0x606810` (`memcpy`), `0x61edf4` (`__RTDynamicCast`)
**CalledBy:** Dungeon floor loader (`0x556170`), `CBattle` init (`0x449927`), `CBattle::_CalcFieldElementRevision` (`0x44fbb0`)

**Typed Pseudocode:**
```text
// Source archive: backups/Dungeon/floor_parameters.zip (104 StXX_YYYY.bin files)
// Loader 0x556170 allocates aligned heap buffer, copies raw .bin bytes, and calls
// 0x555560(basePtr, basePtr) to convert all file-relative u32 offsets into live pointers
// in-place (skipped if (base[+0x00] & base[+0x04]) == 0xFFFFFFFF).

// 1. Floor Parameter Header (relocated offsets -> pointers at 0x555575..0x555625):
//   +0x00: ptr<char>  floorNameStr      (relocated)
//   +0x08: ptr<void>  section08         (relocated)
//   +0x10: ptr<void>  section10         (relocated)
//   +0x18: ptr<void>  section18         (relocated)
//   +0x20: ptr<void>  section20         (relocated)
//   +0x28: u32        fixedGroupCount   (group IDs 40..59 = 0x28..0x3b)
//   +0x30: ptr<EncGroup> fixedGroups    (relocated; array of fixedGroupCount * 0x58 bytes)
//   +0x38: u32        bossGroupCount    (group IDs >= 60 = 0x3c)
//   +0x40: ptr<EncGroup> bossGroups     (relocated; array of bossGroupCount * 0x58 bytes)
//   +0x50: ptr<void>  section50         (relocated)
//   +0x58: u32        count58           (entries at +0x60, stride 0x10, ptr at +0x08 relocated)
//   +0x60: ptr<void>  section60         (relocated)
//   +0x68: u32        count68           (entries at +0x70, stride 0x10, ptr at +0x08 relocated)
//   +0x70: ptr<void>  section70         (relocated)
//   +0x78: u32        count78           (entries at +0x80, stride 0x08, ptr at +0x00 relocated)
//   +0x80: ptr<void>  section80         (relocated)
//   +0x90: ptr<void>  section90         (relocated)
//   +0x98: u32        areaCount         (number of dungeon areas on this floor)
//   +0xa0: ptr<Area>  areas             (relocated; array of areaCount * 0xd0 bytes)

// 2. Encounter Group Struct (0x58 = 88 bytes; used for area groups, fixedGroups, bossGroups):
//   +0x00: u32        groupHeader / id
//   +0x04..+0x33: i32 enemyIds[12]      (up to 12 enemy IDs; -1 terminates empty slots)
//   +0x34..+0x3f: u8  rowFlags[12]      (per-slot row placement byte passed to 0x439d20)
//   +0x40: u32        weight            (encounter selection weight, read at 0x555b72: [base+i*0x58-0x18])
//   +0x48: ptr<char>  bgmName           (relocated at 0x55559a / 0x5555b7 / 0x55566e: +0x58 - 0x10 = +0x48)
//   +0x50: u32        isBossOrNoEscape  (non-zero sets boss/no-escape flag passed as arg3 to 0x439d20)

// 3. Area Parameter Struct (0xd0 = 208 bytes, indexed by Mass_s.areaIdx at cell+0x06):
//   +0x1c: u32        baseEncounterRate (step encounter rate read at 0x4bc773)
//   +0x5c: u32        normalGroupCount  (group IDs 0..39 = < 0x28)
//   +0x60: ptr<EncGroup> normalGroups   (relocated; array of normalGroupCount * 0x58 bytes)
//   +0x70, +0x80, +0x90, +0xa0, +0xb0: ptr<void> subtables (relocated at 0x55567e..0x5556b0)
//   +0xb8: f32        zoneMulPhysAtk    (copied to [battle+0x1e4] at 0x44994d; Zone ID 3)
//   +0xbc: f32        zoneMulMagAtk     (copied to [battle+0x1e8] at 0x449963; Zone ID 4)
//   +0xc0: f32        zoneMulPhysDef    (copied to [battle+0x1ec] at 0x449979; Zone ID 5)
//   +0xc4: f32        zoneMulMagDef     (copied to [battle+0x1f0] at 0x44998f; Zone ID 6)
//   +0xc8: f32        zoneMulElement    (copied to [battle+0x1f4] at 0x4499a5; Zone IDs 7..11)
//   // Verified vanilla values: St00_0010.bin area0 = (2.25f, 2.25f, 0.5f, 0.5f, 2.25f);
//   //                          St00_1020.bin area0 = (2.0f,  2.0f,  0.5f, 0.5f, 2.0f).

// 4. Battle Elemental Zone Consumption (0x44fbb0 _CalcFieldElementRevision):
//   Reads current cell Mass_s.zoneType1 (+0x08) and Mass_s.zoneType2 (+0x0c).
//   If isPhysical != 0:
//     mul = (zone1 == 3 || zone2 == 3) ? battle[+0x1e4] : 1.0f
//     if (zone1 == 5 || zone2 == 5): mul *= battle[+0x1ec]
//   Else (Magical):
//     mul = (zone1 == 4 || zone2 == 4) ? battle[+0x1e8] : 1.0f
//     if (zone1 == 6 || zone2 == 6): mul *= battle[+0x1f0]
//   Elemental Zones 7..11 (Fire/Water/Wind/Earth/Thunder) multiply by battle[+0x1f4] when matching.
//   RNG calls: 0.
```

**Program Evidence:**
```asm
005561c7  mov      ecx, dword ptr [ebx + 4]
005561cd  mov      eax, ecx
005561cf  cdq      
005561d0  push     edx
005561d1  push     eax
005561d2  call     0x555560
00555584  add      dword ptr [ecx + 0x30], edx
00555596  lea      esi, [esi + 0x58]
0055559a  add      dword ptr [esi + eax - 0x10], edx
005555a3  add      dword ptr [ecx + 0x40], edx
00555625  add      dword ptr [ecx + 0xa0], edx
005556b7  add      ebx, 0xd0
0044993e  imul     ecx, eax, 0xd0
0044994d  mov      eax, dword ptr [eax + ecx + 0xb8]
00449954  mov      dword ptr [edi + 0x1e4], eax
00449963  mov      eax, dword ptr [eax + ecx + 0xbc]
0044996a  mov      dword ptr [edi + 0x1e8], eax
00449979  mov      eax, dword ptr [eax + ecx + 0xc0]
00449980  mov      dword ptr [edi + 0x1ec], eax
0044998f  mov      eax, dword ptr [eax + ecx + 0xc4]
00449996  mov      dword ptr [edi + 0x1f0], eax
004499a5  mov      eax, dword ptr [eax + ecx + 0xc8]
004499ac  mov      dword ptr [edi + 0x1f4], eax
```

---

### M10.10 Dungeon Map Cells (`StXX_YYYY.map`, `0x2a`-Byte `Mass_s`) & Fixed-Tile / Group Namespace Dispatch

**Binary VA(s):** `0x4afa40..0x4afb18`, `0x4b5621..0x4b56c0`, `0x4bc6e2..0x4bc7a6`, `0x4b4e30..0x4b4fc0`, `0x4bd2f0..0x4bd567`
**Calls:** `0x4bd2f0` (fixed-tile encounter start), `0x439d20` (spawn battle enemy formation), `0x555df0` / `0x555e60` (battle BGM resolver)
**CalledBy:** `CDungeonBase` map load (`0x4b5621`), step update (`0x4bc5d0`), script battle trigger (`0x4cc33e` / `0x4cc388`)

**Typed Pseudocode:**
```text
// 1. StXX_YYYY.map Binary Format (backups/Dungeon/floor_maps.zip, 103 .map files):
//   Header (12 bytes): { u32 mapId; u32 width; u32 height; }
//   Body: width * height cells, each 0x2a (42) bytes, unpacked into 0x230-byte Mass_s by 0x4afa40:
//     file+0x00 (u8) -> Mass_s+0x00 (u32): cellType (0..11; 5 = fixed-tile encounter cell!)
//     file+0x01 (u8) -> Mass_s+0x04 (u32): cellParam
//     file+0x02 (u8) -> Mass_s+0x08 (u32): zoneType1 (3=PhysAtk, 4=MagAtk, 5=PhysDef, 6=MagDef, 7..11=Elem)
//     file+0x03 (u8) -> Mass_s+0x0c (u32): zoneType2 (second concurrent zone effect on same tile)
//     file+0x04 (u8) -> Mass_s+0x10 (u8 ): bool flag (byte != 0)
//     file+0x05 (u8) -> Mass_s+0x14 (u32): direction remapped via 0x4b0414 (0->4, 1->0, 2->1, 3->2, 4->3)
//     file+0x06 (u8) -> Mass_s+0x18 (u32): areaIdx (index into floor_parameters.areas[], stride 0xd0)
//     file+0x08 (i8) -> Mass_s+0x1c (i32): signed param8
//     file+0x09 (i8) -> Mass_s+0x20 (i32): signed param9 (if >= 0, adds +0x19 = +25 at 0x4afb0c)

// 2. Fixed-Tile Encounter Trigger on Step (0x4bc6e2..0x4bc758):
//   Cell types 2, 3, 4, 7 suppress step encounters completely (jump to 0x4bcb7d).
//   If cell.cellType == 5:
//     Checks cleared-tile flag table [0x71f998] (floor entry stride 0x3c8, byte at +4 + cellIndex).
//     If tile not yet cleared (== 0) AND dungeon.encountersEnabled ([dungeon+0x210] != 0):
//       Sets [dungeon+0x798] = 1 and launches fixed-tile battle via 0x4bd2f0(1)!
//   Otherwise reads Area[cell.areaIdx].baseEncounterRate (+0x1c); if [dungeon+0x770] != 0 and steps < 8, zeroes rate.

// 3. Universal Encounter Group ID Namespace (CDungeonBase::_StartScriptBattle 0x4b4e30 & 0x4bd360):
fn CDungeonBase_StartScriptBattle(dungeon: ptr<CDungeonBase>, battle: ptr<CBattle>, groupId: u32) -> void:
    if groupId < 0x28:                                        // 0 .. 39: Current Area normal group
        let areaIdx: u32 = dungeon.currentCell.areaIdx        // Mass_s+0x18
        let grp: ptr<EncGroup> = &dungeon.floorParam.areas[areaIdx].normalGroups[groupId]
        SpawnFormation(battle, grp.enemyIds, grp.rowFlags, grp.isBossOrNoEscape != 0)   // 0x439d20
    else if groupId < 0x3c:                                   // 40 .. 59 (0x28..0x3b): Floor fixedGroups
        let idx: u32 = groupId - 0x28
        let grp: ptr<EncGroup> = &dungeon.floorParam.fixedGroups[idx]
        SpawnFormation(battle, grp.enemyIds, grp.rowFlags, grp.isBossOrNoEscape != 0)
    else if groupId < 0x80000000:                             // 60 .. 0x7FFFFFFF (>= 0x3c): Floor bossGroups
        let idx: u32 = groupId - 0x3c
        let grp: ptr<EncGroup> = &dungeon.floorParam.bossGroups[idx]
        SpawnFormation(battle, grp.enemyIds, grp.rowFlags, grp.isBossOrNoEscape != 0)
    else:                                                     // >= 0x80000000 (handled in 0x4bd360):
        let directEnemyId: u32 = groupId & 0x7FFFFFFF         // direct single-enemy encounter
    // RNG calls: 0.
```

**Program Evidence:**
```asm
004afa79  movzx    edx, byte ptr [ecx]
004afa7c  mov      dword ptr [esi], edx
004afa7e  movzx    eax, byte ptr [ecx + 1]
004afa82  mov      dword ptr [esi + 4], eax
004afa9c  movzx    eax, byte ptr [ecx + 2]
004afaa0  mov      dword ptr [esi + 8], eax
004afaa3  movzx    eax, byte ptr [ecx + 3]
004afaa7  mov      dword ptr [esi + 0xc], eax
004afaf3  movzx    eax, byte ptr [ecx + 6]
004afaf7  mov      dword ptr [esi + 0x18], eax
004bc706  cmp      eax, 5
004bc709  jne      0x4bc758
004bc74c  call     0x4bd2f0
004b4e43  cmp      ebp, 0x28
004b4e46  jae      0x4b4efd
004b4e8e  cmp      dword ptr [ecx + edx + 0x50], 0
004b4ea8  call     0x439d20
004b4f0a  cmp      ebp, 0x3c
004b4f0d  jae      0x4b4f7c
004b4f12  lea      esi, [ebp - 0x28]
004b4f7f  lea      esi, [ebp - 0x3c]
004b4f89  cmp      dword ptr [ecx + edx + 0x50], 0
```


---

### M10.11 Script `.adv.bin` Bytecode Framing (`0x4d2970`/`0x4d2a10`) & Opcode `0x1F` (`BATTLE`) Trigger (`0x4cc2a4`)

**Binary VA(s):** `0x4d2570..0x4d2a85`, `0x4cc2a4..0x4cc38d`
**Calls:** `0x4d2970` (string-record reader), `0x4b0d40` (temp `CDungeonBase` ctor), `0x448a50` (`CBattle` ctor with `isFixedBattle=1`), `0x4b4e30` (`CDungeonBase::_StartScriptBattle`), `0x603045` (`operator new`)
**CalledBy:** `.adv.bin` script loader (`0x4d2570`), script VM opcode dispatch (`0x4cc2a4` for opcode `0x1F`)

**Typed Pseudocode:**
```text
// 1. .adv.bin Bytecode Stream Format (backups/Dungeon/floor_maps.zip, 1,337 .adv.bin files):
//   Sequential stream of variable-length instructions parsed by 0x4d2570 and skipped by 0x4d2a10:
//     u8 opcode
//     if opcode == 0x00:
//         u32le inlinePayload                                // 4 bytes
//     else if opcode == 0x0A || opcode == 0x12:
//         u32le inlineId                                     // 4 bytes
//         u16be strId; u8 strFlag; char cstr[] (NUL-term)    // read by 0x4d2970
//     u8 argCount
//     for i in 0 .. (argCount - 1):
//         u8 argType
//         if argType == 0x00:
//             u32le intArg                                   // 4-byte little-endian integer
//         else if argType == 0x0A || argType == 0x12:
//             u32le id; u16be strId; u8 strFlag; char cstr[] // string argument (0x4d2970)
//
// 2. Opcode 0x1F ("BATTLE", string at 0x674558) Wire Encoding & Executor (0x4cc2a4..0x4cc38d):
//   Wire bytes (7 bytes total, 168 instances across vanilla floor_maps.zip):
//     [0x1F] [0x01] [0x00] [u32le groupArg]
//       opcode=0x1F, argCount=1, argType=0x00 (u32le), value=groupArg (1-based!)
fn ScriptVM_ExecOpcode_1F_Battle(vm: ptr<ScriptVM>, instr: ptr<ParsedInstr>) -> void:
    let groupArg: u32 = instr.args[0].intVal                  // [eax+4] at 0x4cc2ba
    vm.state = 2                                              // [vm+0x4c] = 2 (in-battle)
    if vm.activeBattle != NULL:                               // [vm+0x135c]
        delete vm.activeBattle

    // Allocate 0x200-byte CBattle with isFixedBattle = 1 (push 1 at 0x4cc317 / 0x4cc35d):
    let battle: ptr<CBattle> = new CBattle(vm.gameApp, isFixedBattle=1)  // 0x448a50
    vm.activeBattle = battle

    // CRITICAL 1-BASED TO 0-BASED CONVERSION (0x4cc32a and 0x4cc370):
    let groupId: u32 = groupArg - 1                           // lea ecx, [ebx - 1]

    if vm.gameApp.mode != 3:                                  // non-dungeon context
        let tmpDungeon: ptr<CDungeonBase> = new CDungeonBase() // 0x7c0 bytes, 0x4b0d40
        CDungeonBase_StartScriptBattle(tmpDungeon, battle, groupId)      // 0x4b4e30
        delete tmpDungeon
    else:                                                     // active dungeon context ([vm+0x1358])
        CDungeonBase_StartScriptBattle(vm.dungeon, battle, groupId)      // 0x4b4e30
    // RNG calls: 0.
```

**Program Evidence:**
```asm
004d297c  movzx    edx, byte ptr [ebp]
004d2983  movzx    eax, byte ptr [ebp + 1]
004d2987  movzx    ecx, byte ptr [ebp + 2]
004d298b  shl      edx, 8
004d298e  or       edx, eax
004d2a19  mov      al, byte ptr [eax]
004d2a1b  test     al, al
004d2a1d  jne      0x4d2a24
004d2a1f  add      ecx, 4
004d2a24  cmp      al, 0x12
004d2a28  cmp      al, 0xa
004d2a43  movzx    esi, byte ptr [ecx]
004cc2ba  mov      ebx, dword ptr [eax + 4]
004cc317  push     1
004cc325  call     0x448a50
004cc32a  lea      ecx, [ebx - 1]
004cc33e  call     0x4b4e30
004cc35d  push     1
004cc36b  call     0x448a50
004cc370  lea      ecx, [ebx - 1]
```

---

## 4. Binary Struct Layouts Read by `.exe` Loaders (`backups/**/*.pck`)

### M10.12 Aquaplus `.pck` Container Parser (`0x5ab540`) & Universal `std::map` `+0x18` Offset Rule

**Binary VA(s):** `0x5ab540..0x5ab669`, `0x501ee0..0x502600`, `0x507310`
**Calls:** `0x604bc0` (`memset`), `0x507310` (`std::map<u32, Record_s>::find`)
**CalledBy:** Master parameter loader (`0x501ee0`), every `Parameter::CParameter*::Load` and getter

**Typed Pseudocode:**
```text
// 1. Aquaplus .pck Archive Binary Layout (verified at 0x5ab540..0x5ab644 & raw backups/*.pck):
//   A .pck file is a sequence of 8-byte-aligned named chunks; each chunk starts with a 24-byte header:
//     +0x00..+0x13 (20 bytes): ASCII chunk tag padded with 0x20 (' ') to 20 bytes
//                              ("Filename            ", "Pack                ")
//     +0x14..+0x17 (u32le):    chunkSize (total bytes including 24-byte header; next chunk
//                              advances by (chunkSize + 7) & ~7 at 0x5ab5ab..0x5ab5b4)
//   Chunk 1 ("Filename            ", payload starts at chunk + 0x18):
//     +0x18 + i*4 (u32le[fileCount]): relative offsets from (chunk + 0x18) to NUL-terminated ASCII filenames
//   Chunk 2 ("Pack                ", payload starts at chunk + 0x18):
//     +0x18 (u32le):                  fileCount
//     +0x1c + i*8 ({u32le off, u32le size}[fileCount]):
//                                     entry bytes lie at [packChunkBase + off .. + off + size]
//
// 2. Universal Parameter::* In-Memory std::map Node Offset Rule:
//   All Parameter::CParameter* singletons store fixed-size binary records in MSVC x86 std::map<u32, Record_s>
//   red-black tree nodes:
//     node+0x00: ptr<Node> left
//     node+0x04: ptr<Node> parent
//     node+0x08: ptr<Node> right
//     node+0x0c: u8        color
//     node+0x0d: u8        isNil
//     node+0x10: u32       mapKey   (record ID, == file+0x00)
//     node+0x14: u32       padding / alignment (4 bytes when value is 8-byte aligned; 0 bytes for 4-byte-aligned maps)
//     node+0x18: Record_s  payload  (mem_offset == file_offset + 0x18 for ALL records below EXCEPT
//                                    PlayerStatusData [0x738a08] and CharacterData [0x7389b4] which use +0x14!)
//   NOTE on variable-length string pools inside .bin records:
//     Each .bin file has a fixed-size binary struct header followed by a NUL-terminated string pool.
//     String fields in the fixed header store u32le file-relative byte offsets; loaders deep-copy each
//     string to a heap buffer (0x5c5b30) and overwrite the offset field with the heap char* pointer.
//   RNG calls: 0.
```

**Program Evidence:**
```asm
005ab540  mov      edi, 0x14
005ab549  mov      al, byte ptr [ecx + 0x6b6388]    ; 'Filename'
005ab56c  push     0x20
005ab56f  call     0x604bc0
005ab5ab  mov      eax, dword ptr [ecx + 0x14]
005ab5ae  add      eax, 7
005ab5b1  and      eax, 0xfffffff8
005ab5b4  add      ecx, eax
005ab5c1  lea      eax, [ecx + 0x18]
005ab5e4  mov      al, byte ptr [ecx + 0x6b6394]    ; 'Pack'
005ab605  push     0x20
005ab608  call     0x604bc0
```

---

### M10.13 `EnemyStatusData.bin` (`backups/Enemy/Enemy.pck`, `0x128` Bytes) Binary Struct Layout

**Binary VA(s):** `0x557ad0..0x557c25`, `0x557da0..0x55817c`, `0x4f2714..0x4f2813`, `0x445dd4..0x445ea8`, `0x4f1fea..0x4f2050`
**Calls:** `0x507310` (`std::map::find` on `[0x7389d8]`), `0x5c5b30` (heap string alloc)
**CalledBy:** `0x45e5a9` (`Enemy.pck` loader), `CGameEnemyStatus` init (`0x4f2714`), battle rewards (`0x445dd4`), ailment immunity getters (`0x557fa0..0x558147`)

**Typed Pseudocode:**
```text
// Archive: backups/Enemy/Enemy.pck (516 nested <id>.pck files; each contains EnemyStatusData.bin + optional EnemyAIData.bin)
// Loader:  0x557ad0 -> map [0x7389d8] (node base offset: mem = file + 0x18)
// Fixed struct copy: rep movsd ecx = 0x4a -> 0x4a * 4 = 0x128 (296) bytes!
//
// Exact Field Map (fileOffset / memOffset = fileOffset + 0x18):
//   file+0x00 (mem+0x18): u32   enemyId              (map key)
//   file+0x04 (mem+0x1c): u32   categoryOrSubId
//   file+0x08 (mem+0x20): u32->char* name            (relocated string offset at 0x557b16..0x557b6d)
//   file+0x10 (mem+0x28): u32   raceOrCategoryType   (0..9 checked by 0x557da0..0x557f9f)
//   file+0x14 (mem+0x2c): u32   level
//   file+0x18 (mem+0x30): u32   maxHP
//   file+0x1c (mem+0x34): u32   baseATK
//   file+0x20 (mem+0x38): u32   baseDEF
//   file+0x24 (mem+0x3c): u32   baseINT
//   file+0x28 (mem+0x40): u32   baseRES
//   file+0x2c (mem+0x44): u32   baseAGI
//   file+0x30 (mem+0x48): u32   baseDEX
//   file+0x3c (mem+0x54): u32   immunityBitmask      (exact bit getters verified at 0x557fa0..0x558147):
//       bit  0 (0x557fa0): called by 0x44bf2f, 0x44eb41 (Instakill/boss flag)
//       bit  3 (0x557fd0): called by 0x482884 (Ailment immunity)
//       bit  4 (0x558000): called by 0x482af4 (Ailment immunity)
//       bit  5 (0x558030): called by 0x4832d4, 0x48356c (Ailment immunity)
//       bit  6 (0x558060): called by 0x482f26 (Ailment immunity)
//       bit  7 (0x558090): called by 0x4823a4 (Ailment immunity)
//       bit  8 (0x5580c0): called by 0x481f84 (Ailment immunity)
//       bit  9 (0x5580f0): called by 0x482614 (Ailment immunity)
//       bit 11 (0x558120): called by 0x4836b4 (Ailment immunity)
//       bit 12 (0x423810): Turn Delay (cmd 54) immunity
//   file+0x48..+0x64 (mem+0x60..+0x7c): 8x i32 combat resistances copied directly into
//       CGameEnemyStatus[+0x6c..+0x88] and [+0x34..+0x50] at 0x4f2721..0x4f280c:
//       file+0x48 (mem+0x60): i32 resist[0] -> [status+0x6c / +0x34] (Phys/Slash)
//       file+0x4c (mem+0x64): i32 resist[1] -> [status+0x70 / +0x38] (Pierce)
//       file+0x50 (mem+0x68): i32 resist[2] -> [status+0x74 / +0x3c] (Strike)
//       file+0x54 (mem+0x6c): i32 resist[3] -> [status+0x78 / +0x40] (Fire)
//       file+0x58 (mem+0x70): i32 resist[4] -> [status+0x7c / +0x44] (Water)
//       file+0x5c (mem+0x74): i32 resist[5] -> [status+0x80 / +0x48] (Wind)
//       file+0x60 (mem+0x78): i32 resist[6] -> [status+0x84 / +0x4c] (Earth)
//       file+0x64 (mem+0x7c): i32 resist[7] -> [status+0x88 / +0x50] (Thunder)
//   file+0x68 (mem+0x80): u32   dropCount            (checked at 0x445dd4)
//   file+0x6c..+0xa4 (mem+0x84..+0xbc): { u32 itemId, u32 dropRate }[] (stride 8, read at 0x445dff)
//   file+0xa8 (mem+0xc0): u32   rareOrStealItemId    (checked at 0x445e90)
//   file+0xac (mem+0xc4): u32   attackCount          (up to 16)
//   file+0xb0..+0xef (mem+0xc8..+0x107): i32 attacks[16]  (stride 4; getter 0x558150; slot 0 = basic attack)
//   file+0xf0..+0x104 (mem+0x108..+0x11c): passive count & passive IDs (read at 0x4f1fea)
//   file+0x108 (mem+0x120): u32->char* description   (relocated string offset at 0x557b84)
//   Total fixed record size: 0x128 (296) bytes. RNG calls: 0.
```

**Program Evidence:**
```asm
00557b16  mov      ebx, dword ptr [ebx + 8]
00557b19  mov      ecx, 0x4a
00557b22  rep movsd dword ptr es:[edi], dword ptr [esi]
00557b84  mov      esi, dword ptr [eax + 0x108]
00557fbc  mov      al, byte ptr [eax + 0x54]
00557fbf  and      al, 1
00557fec  mov      eax, dword ptr [eax + 0x54]
00557fef  shr      eax, 3
0055813c  mov      eax, dword ptr [eax + 0x54]
0055813f  shr      eax, 0xb
004f2721  mov      eax, dword ptr [eax + 0x60]
004f2724  mov      dword ptr [ebx + 0x6c], eax
004f2803  mov      eax, dword ptr [eax + 0x7c]
004f2806  mov      dword ptr [ebx + 0x88], eax
00445dff  cmp      ecx, dword ptr [eax + esi*8 + 0x84]
00445e90  cmp      esi, dword ptr [eax + 0xc0]
00558171  mov      eax, dword ptr [eax + esi*4 + 0xc8]
```

---

### M10.14 `EnemyAttackData.pck` (`0xa0` Bytes, including `pattern` at `+0x90`) Binary Struct Layout

**Binary VA(s):** `0x556f10..0x5572a3`, `0x41a4cf..0x41a508`, `0x431231..0x431346`
**Calls:** `0x556f10` (record copy & string relocator), `0x557730` (map insert into `[0x7389d4]`), `0x507310` (`std::map::find`)
**CalledBy:** Master parameter loader (`0x501ee0`), `CActionEnemyAttack::_CreatePattern` (`0x41a4a0`), `CBattleAI2::Task_s::Run` (`0x430f10`)

**Typed Pseudocode:**
```text
// Archive: backups/EnemyAttackData.pck (2,375 records: EnemyAttackData_0000.bin ..)
// Loader:  0x5570b0 (calls 0x556f10) -> map [0x7389d4] (node base offset: mem = file + 0x18)
// Fixed struct copy: rep movsd ecx = 0x28 -> 0x28 * 4 = 0xa0 (160) bytes!
//
// Exact Field Map (fileOffset / memOffset = fileOffset + 0x18):
//   file+0x00 (mem+0x18): u32   enemyAttackId        (map key)
//   file+0x08 (mem+0x20): u32->char* name            (relocated string offset; icon-prefixed copy at mem+0xb0)
//   file+0x28 (mem+0x40): u32   flags                (bit 1 = Physical/Skill blocked by Freeze;
//                                                     bit 2 = Magic blocked by Silence & sets Action_s type=9)
//   file+0x2c (mem+0x44): u32   targetType           (3 = Breath/row-special target expansion via 0x43bab0)
//   file+0x40 (mem+0x58): f32   powerOrScale
//   file+0x44 (mem+0x5c): f32   actionSpeed
//   file+0x48 (mem+0x60): u32   cmdCount             (0..5; loop upper bound at 0x431231 & 0x4312a7)
//   file+0x4c..+0x87 (mem+0x64..+0x9f): CommandEntry cmds[5], stride 0x0c (12 bytes each):
//       +0x00: i32 cmdId                             (e.g., 3 = Breath Attack, 0x92 = Summon/Doll)
//       +0x04: f32 cmdVal
//       +0x08: u32 cmdFlags                          (bit 2 / 0x04 = CCommandTurnBase checked by AI Target 8)
//   file+0x90 (mem+0xa8): u32   pattern              (0..17 / 0x00..0x11; jump table at 0x41a814;
//                                                     case 17 = Random EnemyAttack table 0x64f1c0)
//   file+0x94 (mem+0xac): u32   iconType             (validated by 0x5575f0 / 0x557180..0x5572c0)
//   file+0x98 (mem+0xb0): char* formattedDisplayName (heap-allocated icon + name string at 0x55727f)
//   Total fixed record size: 0xa0 (160) bytes. RNG calls: 0.
```

**Program Evidence:**
```asm
005570e9  lea      ecx, [esp + 0x1ac]
005570f0  call     0x556f10
00557104  mov      ecx, 0x28
0055710d  rep movsd dword ptr es:[edi], dword ptr [esi]
00557120  call     0x557730
0055727f  mov      dword ptr [eax + 0xb0], ebx
0041a4d2  mov      ecx, dword ptr [0x7389d4]
0041a4e6  call     0x507310
0041a4eb  mov      eax, dword ptr [eax]
0041a4ed  mov      ecx, dword ptr [eax + 0xa8]
0041a4f3  cmp      ecx, 0x11
0041a4f6  ja       0x41a7fa
0041a4fc  movzx    eax, byte ptr [ecx + 0x41a838]
0041a503  jmp      dword ptr [eax*4 + 0x41a814]
```

---

### M10.15 Skill `.pck` Layouts (`Technique`, `Magic`, `Passive`, `Unique`), Level Arrays & `Trailer[0..6]` (`Trailer[4]` Pattern)

**Binary VA(s):** `0x571a40..0x571b20`, `0x570430..0x5704c0`, `0x5712e0..0x571370`, `0x572160..0x572210`, `0x56bd00..0x56bdd8`, `0x56c690..0x56cda8`, `0x56d450..0x56d545`
**Calls:** `0x56ba30` (`GetSkillType`: 0=Technique, 1=Magic, 2=Passive, 3=JoinSkill, 4=Unique, 5=PartySkill), `0x507310` (`std::map::find`), `0x61e650` (`round_f32_to_i32`)
**CalledBy:** Master parameter loader (`0x501ee0`), `CActionSkill::_CreatePattern` (`0x41e060`), skill UI & battle command builders

**Typed Pseudocode:**
```text
// All 6 skill maps use node base offset mem = file + 0x18:
//   type 0 = TechniqueSkillData.pck (143 records): [0x738a64], loader 0x571a40, rep movsd 0x7c -> 0x1f0 (496) B
//   type 1 = MagicSkillData.pck     ( 98 records): [0x738a58], loader 0x570430, rep movsd 0x8e -> 0x238 (568) B
//   type 2 = PassiveSkillData.pck   ( 71 records): [0x738a60], loader 0x5712e0, rep movsd 0x36 -> 0x0d8 (216) B
//   type 3 = JoinSkillData.pck                    [0x738a54]
//   type 4 = UniqueSkillData.pck    ( 18 records): [0x738a68], loader 0x572160, 6x movups     -> 0x060 ( 96) B
//   type 5 = PartySkillData.pck                   [0x738a5c]
//
// 1. Common Trailer[0..6] (7 x u32 = 0x1c bytes at the exact end of each fixed skill struct):
//   Trailer[0] = IconType (0x56bd16..0x56bdd2)
//   Trailer[4] = Pattern  (0x56d450..0x56d52c Parameter::CParameterSkill::GetPattern)
//   Exact byte offsets (file / mem = file + 0x18):
//     Skill Type   | Struct Size | Trailer[0] (Icon)    | Trailer[4] (Pattern) | Trailer End
//     Technique    | 0x1f0 (496) | file+0x1d4 (mem+0x1ec)| file+0x1e4 (mem+0x1fc)| 0x1f0
//     Magic        | 0x238 (568) | file+0x21c (mem+0x234)| file+0x22c (mem+0x244)| 0x238
//     Passive      | 0x0d8 (216) | file+0x0bc (mem+0x0d4)| file+0x0cc (mem+0x0e4)| 0x0d8
//     Unique       | 0x060 ( 96) | file+0x044 (mem+0x05c)| file+0x054 (mem+0x06c)| 0x060
//     JoinSkill    |             | file+0x084 (mem+0x09c)| file+0x090 (mem+0x0a8)|
//     PartySkill   |             | file+0x044 (mem+0x05c)| returns 0 (hardcoded) |
//
// 2. Per-Level Arrays & Command Tables (verified from GetLevelNumber 0x56c690, GetLevelupSkillPoint 0x56c7a0,
//    GetTurn 0x56c8a0, GetSpeed 0x56c9a0, GetCommandNumber 0x56ca90, GetCommand 0x56cbe0; lv in 1..10):
//   TechniqueSkillData (0x1f0 B, [0x738a64]):
//     file+0x00 (mem+0x18): u32   skillId;  file+0x08 (mem+0x20): char* name;  file+0x20 (mem+0x38): char* atkName
//     file+0x30 (mem+0x48): u32   flags (bit 6 = IsAddEnding at 0x56c147)
//     file+0x34..+0x5b (mem+0x4c..+0x73): u32 spCost[10]       (1-based idx: mem+0x48+lv*4; first 0 sets maxLv)
//     file+0x84..+0xab (mem+0x9c..+0xc3): u32 turnOrChant[10]  (1-based idx: mem+0x98+lv*4)
//     file+0xac..+0xd3 (mem+0xc4..+0xeb): f32 speed[10]        (1-based idx: mem+0xc0+lv*4)
//     file+0xe0 (mem+0xf8): u32   cmdCount
//     file+0xe4..+0x1d3 (mem+0xfc..+0x1eb): CommandBlock[3], stride 0x30 (48 bytes:
//       +0x00 i32 cmdId, +0x04..+0x2b f32 valByLv[10] at mem+0xfc+(cmd*12+lv)*4, +0x2c u32 cmdFlags at mem+0x128)
//
//   MagicSkillData (0x238 B, [0x738a58]):
//     file+0x30 (mem+0x48): u32   flags (bit 5 = IsAddEnding at 0x56c16f)
//     file+0x34..+0x5b (mem+0x4c..+0x73): u32 spCost[10]       (mem+0x48+lv*4)
//     file+0x84..+0xab (mem+0x9c..+0xc3): u32 turnOrChant[10]  (mem+0x98+lv*4)
//     file+0xac..+0xd3 (mem+0xc4..+0xeb): f32 speed[10]        (mem+0xc0+lv*4)
//     file+0x128 (mem+0x140): u32 cmdCount
//     file+0x12c..+0x21b (mem+0x144..+0x233): CommandBlock[5], stride 0x30 (48 bytes:
//       +0x00 i32 cmdId, +0x04..+0x2b f32 valByLv[10], +0x2c u32 cmdFlags at mem+0x170)
//
//   PassiveSkillData (0xd8 B, [0x738a60]):
//     file+0x2c..+0x53 (mem+0x44..+0x6b): u32 spCost[10]       (mem+0x40+lv*4)
//     file+0x58 (mem+0x70): u32   cmdCount
//     file+0x5c..+0xbb (mem+0x74..+0xd3): PassiveCmdBlock[2], stride 0x30 (+0x00 i32 cmdId, +0x04 f32 valByLv[10])
//
//   UniqueSkillData (0x60 B, [0x738a68]):
//     file+0x1c..+0x43 (mem+0x34..+0x5b): f32 valByLv[10]      (mem+0x30+lv*4 at 0x56cd78)
//     file+0x50 (mem+0x68): i32   cmdId                        (cmdCount = (cmdId != -1) ? 1 : 0 at 0x56cb63)
//     file+0x44..+0x5c (mem+0x5c..+0x74): Trailer[0..6]        (Trailer[4] Pattern at file+0x54 / mem+0x6c)
//   RNG calls: 0.
```

**Program Evidence:**
```asm
00571a91  mov      ecx, 0x7c
00571a9d  rep movsd dword ptr es:[edi], dword ptr [esi]
00570481  mov      ecx, 0x8e
0057048d  rep movsd dword ptr es:[edi], dword ptr [esi]
00571334  mov      ecx, 0x36
0057133d  rep movsd dword ptr es:[edi], dword ptr [esi]
005721d3  movups   xmm0, xmmword ptr [edi + 0x40]
005721dc  movups   xmm0, xmmword ptr [edi + 0x50]
0056c6d3  cmp      dword ptr [edi + eax], 0
0056c7f4  mov      esi, dword ptr [eax + ebx*4 + 0x48]
0056c8e4  mov      esi, dword ptr [eax + ebx*4 + 0x98]
0056c9e9  movss    xmm0, dword ptr [eax + edi*4 + 0xc0]
0056cc4e  mov      eax, dword ptr [esi + edx*8 + 0xfc]
0056cca3  mov      eax, dword ptr [esi + edx*8 + 0x144]
0056d487  mov      eax, dword ptr [eax + 0x1fc]
0056d4ad  mov      eax, dword ptr [eax + 0x244]
0056d4d3  mov      eax, dword ptr [eax + 0xe4]
0056d51f  mov      eax, dword ptr [eax + 0x6c]
```

---

### M10.16 `EquipmentData.pck` (`0x80` Bytes) & `SealScrollData.pck` (`0x48` Bytes) Binary Struct Layouts

**Binary VA(s):** `0x558ce0..0x558da0`, `0x5590c0..0x5593ab`, `0x4e0f50..0x4e1064`, `0x4e13c0..0x4e155f`, `0x55e9d0..0x55ec80`, `0x49d060..0x49d0da`
**Calls:** `0x507310` (`std::map::find` on `[0x7389e0]` Equipment and `[0x738a14]` SealScroll), `0x61e650` (`round_f32_to_i32`), `0x55ee40` (SealScroll map insert)
**CalledBy:** Master parameter loader (`0x501ee0`), equipment stat/price getters (`0x4e0f50`, `0x4e13c0`), Sealbook UI (`0x49d060`)

**Typed Pseudocode:**
```text
// 1. EquipmentData.pck (551 records: unified struct for Weapons, Armors & Accessories)
//    Loader: 0x558ce0 -> map [0x7389e0] (node base offset: mem = file + 0x18)
//    Fixed struct copy: rep movsd ecx = 0x20 -> 0x20 * 4 = 0x80 (128) bytes!
//
//    Exact Field Map (fileOffset / memOffset = fileOffset + 0x18):
//      file+0x00 (mem+0x18): u32   equipmentId       (map key)
//      file+0x08 (mem+0x20): u32->char* name         (relocated string)
//      file+0x20 (mem+0x38): u32   equipType         (0..5 validated by GetIcon 0x5590c0:
//                                                     0 = Weapon [0x559160],
//                                                     1 = Shield/Head [0x559190],
//                                                     1..4 = Armor group [0x5591f0],
//                                                     4 = Sub-armor [0x5591c0],
//                                                     5 = Accessory)
//      file+0x24..+0x38 (mem+0x3c..+0x50): i32 baseStats (6 stats; e.g. mem+0x44/+0x48/+0x4c in 0x4e13c0..0x4e155f)
//      file+0x3c (mem+0x54): f32   forgeGrowthRate   (canForge iff > 0.0f at 0x55924c;
//                                                     forged stat = baseStat != 0
//                                                       ? baseStat + trunc0(f32(forgeLv) * forgeGrowthRate) : 0
//                                                     at 0x4e13e6..0x4e1437 — cvttss2si!)
//      file+0x50 (mem+0x68): u32   classOrEquipFlags (getter 0x559260)
//      file+0x54 (mem+0x6c): u32   weaponRangeFlags  (when equipType == 0:
//                                                     bit 1 = 0x5592d9, bit 2 = 0x559339, bit 3 = 0x559399)
//      file+0x58 (mem+0x70): u32   basePrice         (0x4e0fb5: + round(basePrice*forgeLv*0.15f),
//                                                     scaled by enchant count 1..4 -> 1.4f / 1.8f / ...)
//      file+0x70 (mem+0x88): u32   unidentifiedValue (returned at 0x4e0f75 when [equip+0x78] != 0)
//    Total fixed record size: 0x80 (128) bytes.
//
// 2. SealScrollData.pck (374 records: Sealbooks / Sealed Monster Books)
//    Loader: 0x55e9d0 -> map [0x738a14] (node base offset: mem = file + 0x18)
//    Fixed struct copy: 4x movups (0x40) + 1x movq (0x08) at 0x55eb60..0x55ebbd -> 0x48 (72) bytes!
//
//    Exact Field Map (fileOffset / memOffset = fileOffset + 0x18):
//      file+0x00 (mem+0x18): u32   sealScrollId      (map key)
//      file+0x08 (mem+0x20): u32->char* name         (prefixed with 0x68c964 at 0x55ebf0..0x55ec80)
//      file+0x10 (mem+0x28): u32   linkedEnemyOrRank (formatted into UI at 0x49d07e)
//      file+0x38 (mem+0x50): u32->char* description  (relocated string at 0x55eb04..0x55eb5e)
//    Total fixed record size: 0x48 (72) bytes. RNG calls: 0.
```

**Program Evidence:**
```asm
005590dc  mov      eax, dword ptr [ecx + 0x38]
005590e2  cmp      eax, 5
005590e7  jmp      dword ptr [eax*4 + 0x559144]
0055924c  movss    xmm0, dword ptr [eax + 0x54]
00559251  comiss   xmm0, dword ptr [0x6d928c]    ; float 0
00559258  seta     al
005592d9  mov      eax, dword ptr [eax + 0x6c]
005592dc  shr      eax, 1
004e13e6  mov      esi, dword ptr [eax + 0x44]
004e1424  mulss    xmm0, dword ptr [ecx + 0x54]
004e1429  cvttss2si eax, xmm0
004e142d  add      eax, esi
004e0fb5  mov      esi, dword ptr [eax + 0x70]
004e0fda  mulss    xmm0, dword ptr [0x6d931c]    ; float 0.15
0055eb04  mov      ebx, dword ptr [eax + 0x38]
0055ebaa  movups   xmm0, xmmword ptr [esp + 0x78]
0055ebb7  movq     xmm0, qword ptr [esp + 0x30]
0055ebc6  call     0x55ee40
```

---

### M10.17 `ItemData.pck` (`0x70` Bytes) Binary Struct Layout & Battle/Camp Effect Pairs

**Binary VA(s):** `0x55b170..0x55b433`, `0x55b550..0x55b6c2`
**Calls:** `0x55b730` (map insert into `[0x7389f4]`), `0x507310` (`std::map::find`), `0x5c5b30` (heap alloc)
**CalledBy:** Master parameter loader (`0x501ee0`), battle & camp item execution (`0x55b550`, `0x55b5b0`)

**Typed Pseudocode:**
```text
// Archive: backups/ItemData.pck (576 records: ItemData_0000.bin ..)
// Loader:  0x55b170 -> map [0x7389f4] (node base offset: mem = file + 0x18)
// Fixed struct copy: rep movsd ecx = 0x1c at 0x55b2fd..0x55b309 -> 0x1c * 4 = 0x70 (112) bytes!
//
// Exact Field Map (fileOffset / memOffset = fileOffset + 0x18):
//   file+0x00 (mem+0x18): u32   itemId               (map key)
//   file+0x08 (mem+0x20): u32->char* name            (icon prefix 0x68c734 or 0x68c738 when flags bit 11 set)
//   file+0x18 (mem+0x30): u32   flags                (verified getters:
//                                                     bit  4 -> 0x55b640 [battle-usable],
//                                                     bit  5 -> 0x55b670 [camp-usable],
//                                                     bit 11 -> 0x55b361 [icon prefix selector])
//   // Dual 2-slot Effect Pairs (stride 8 = { i32 cmdId, f32 cmdVal }; -1 means unused):
//   // Selected by bool isModeA (dl in 0x55b550 count getter, [esp+0x1c] in 0x55b5b0 pair getter):
//   file+0x24..+0x33 (mem+0x3c..+0x4b): ModeA effects[2]:
//       slot 0: file+0x24 (mem+0x3c) i32 cmdId, file+0x28 (mem+0x40) f32 cmdVal
//       slot 1: file+0x2c (mem+0x44) i32 cmdId, file+0x30 (mem+0x48) f32 cmdVal
//   file+0x34..+0x43 (mem+0x4c..+0x5b): ModeB effects[2]:
//       slot 0: file+0x34 (mem+0x4c) i32 cmdId, file+0x38 (mem+0x50) f32 cmdVal
//       slot 1: file+0x3c (mem+0x54) i32 cmdId, file+0x40 (mem+0x58) f32 cmdVal
//   file+0x5c (mem+0x74): u32   targetOrPriceField   (getter 0x55b6a0)
//   file+0x60 (mem+0x78): u32->char* description     (relocated string at 0x55b284..0x55b2e1)
//   file+0x68 (mem+0x80): char* formattedDisplayName (stored at 0x55b413)
//   Total fixed record size: 0x70 (112) bytes. RNG calls: 0.
```

**Program Evidence:**
```asm
0055b284  mov      ebx, dword ptr [eax + 0x60]
0055b2fd  mov      ecx, 0x1c
0055b309  rep movsd dword ptr es:[edi], dword ptr [esi]
0055b318  call     0x55b730
0055b361  mov      eax, dword ptr [eax + 0x30]
0055b364  shr      eax, 0xb
0055b578  cmp      dword ptr [edx + 0x44], -1
0055b581  cmp      dword ptr [edx + 0x3c], -1
0055b590  cmp      dword ptr [edx + 0x54], -1
0055b599  cmp      dword ptr [edx + 0x4c], -1
0055b5e6  mov      eax, dword ptr [eax + esi*8 + 0x3c]
0055b5ec  mov      eax, dword ptr [eax + esi*8 + 0x4c]
0055b618  movss    xmm0, dword ptr [eax + esi*8 + 0x40]
0055b629  movss    xmm0, dword ptr [eax + esi*8 + 0x50]
0055b65c  mov      eax, dword ptr [eax + 0x30]
0055b65f  shr      eax, 4
0055b68c  mov      eax, dword ptr [eax + 0x30]
0055b68f  shr      eax, 5
0055b6bc  mov      eax, dword ptr [eax + 0x74]
```

---

### M10.18 `SummonData.bin` (`0xc8` Bytes) & `NPCData.bin` (`0xd8` Bytes) Binary Struct Layouts

**Binary VA(s):** `0x572f70..0x5730c0`, `0x5732f0..0x573320`, `0x5002e0..0x500360`, `0x55cfa0..0x55d160`, `0x55d340..0x55d370`, `0x4fedb0..0x4feef0`, `0x4ff290..0x4ff310`
**Calls:** `0x507310` (`std::map::find` on `[0x738a70]` Summon and `[0x738a04]` NPC), `0x5c5b30` (heap string alloc)
**CalledBy:** `0x464a79` (`Summon.pck` loader), `0x463cd9` (`NPC.pck` loader), `CBattleAI2` (`0x4347a0`, `0x431aa0` opcode `15`), Summon/NPC status builders

**Typed Pseudocode:**
```text
// 1. SummonData.bin (backups/Summon/Summon.pck: 105 nested <id>.pck files)
//    Loader: 0x572f70 -> map [0x738a70] (node base offset: mem = file + 0x18)
//    Fixed struct copy: rep movsd ecx = 0x32 at 0x572fb9..0x572fc2 -> 0x32 * 4 = 0xc8 (200) bytes!
//
//    Exact Field Map (fileOffset / memOffset = fileOffset + 0x18):
//      file+0x00 (mem+0x18): u32   summonId          (map key; stored at CGamePlayerStatusSummon+0x170)
//      file+0x08 (mem+0x20): u32->char* name         (relocated string at 0x572fb6..0x57301e)
//      file+0x14 (mem+0x2c): u32   baseEnemyId       (source enemy template)
//      file+0x18 (mem+0x30): u32   minLevel
//      file+0x24..+0x38 (mem+0x3c..+0x50): f32 statMultipliers[6]  (ATK/DEF/INT/RES/AGI/DEX scales)
//      file+0x3c (mem+0x54): u32   attackCount       (0..10)
//      file+0x40..+0x8f (mem+0x58..+0xa7): { i32 attackId, u32 useLimit }[10]  (stride 8;
//                                                     slot 0 attackId at mem+0x58 read by 0x4347d8;
//                                                     useLimit at mem+0x5c read by 0x5732f0 for AI opcode 15)
//      file+0x98 (mem+0xb0): u32   passiveCount      (read at 0x5002e0)
//      file+0x9c.. (mem+0xb4..): i32 passiveIds[]    (stride 4)
//    Total fixed record size: 0xc8 (200) bytes.
//
// 2. NPCData.bin (backups/NPC/NPC.pck: 107 nested <id>.pck files)
//    Loader: 0x55cfa0 -> map [0x738a04] (node base offset: mem = file + 0x18)
//    Fixed struct copy: rep movsd ecx = 0x36 at 0x55cfe9..0x55cff2 -> 0x36 * 4 = 0xd8 (216) bytes!
//
//    Exact Field Map (fileOffset / memOffset = fileOffset + 0x18):
//      file+0x00 (mem+0x18): u32   npcId             (map key; stored at CGamePlayerStatusNPC+0x170)
//      file+0x08 (mem+0x20): u32->char* name         (relocated string at 0x55cfe6..0x55d04e)
//      file+0x1c (mem+0x34): u32   weaponRank        (read at 0x4feeb0)
//      file+0x20..+0x34 (mem+0x38..+0x4c): u32 baseStats[6] (read at 0x4fedb0..0x4fee29)
//      file+0x38 (mem+0x50): u32   attackCount       (0..10)
//      file+0x3c..+0x8b (mem+0x54..+0xa3): { i32 attackId, u32 useLimit }[10]  (stride 8;
//                                                     slot 0 attackId at mem+0x54 read by 0x43480e;
//                                                     useLimit at mem+0x58 read by 0x55d340 for AI opcode 15)
//      file+0x94 (mem+0xac): u32   passiveCount      (read at 0x4ff290)
//      file+0x98.. (mem+0xb0..): i32 passiveIds[]    (stride 4)
//    Total fixed record size: 0xd8 (216) bytes. RNG calls: 0.
```

**Program Evidence:**
```asm
00572f80  mov      esi, dword ptr [0x738a70]
00572fb6  mov      ebx, dword ptr [ebx + 8]
00572fb9  mov      ecx, 0x32
00572fc2  rep movsd dword ptr es:[edi], dword ptr [esi]
0057300d  mov      dword ptr [esp + 0x28], esi
0055cfb0  mov      esi, dword ptr [0x738a04]
0055cfe6  mov      ebx, dword ptr [ebx + 8]
0055cfe9  mov      ecx, 0x36
0055cff2  rep movsd dword ptr es:[edi], dword ptr [esi]
0055d03d  mov      dword ptr [esp + 0x28], esi
```

---

### M10.19 `CharacterData.pck`, `PlayerStatusData.bin` (`0x90` B), `CommandData.pck` (`0x40` B) & `EnchantData.pck` (`0x38` B)

**Binary VA(s):** `0x5530b0..0x553150`, `0x55d700..0x55d930`, `0x554940..0x554a72`, `0x556590..0x556860`, `0x4f5470..0x4f54c5`
**Calls:** `0x507310` (`std::map::find`), `0x55d930` (PlayerStatus map insert), `0x554780` / `0x554b60` (Command loader & insert), `0x5551a0` (Enchant map insert)
**CalledBy:** Master parameter loader (`0x501ee0`), `Character/Character.pck` loader, `CGamePlayerStatus` enchant stack counter (`0x4f5470`)

**Typed Pseudocode:**
```text
// 1. CharacterData.pck (250 records) -> map [0x7389b4] (4-byte-aligned map: node size 0x1c, value at mem+0x14):
//    Record size: 0x08 (8) bytes = { u32 charId, u32 flags }
//      file+0x00 (mem+0x14): u32 charId  (map key at node+0x10)
//      file+0x04 (mem+0x18): u32 flags   (bit 1 -> 0x5530f0, bit 2 -> 0x553120)
//
// 2. PlayerStatusData.bin (backups/Character/Character.pck: 19 nested <id>.pck files)
//    Loader: 0x55d700 -> map [0x738a08] (4-byte-aligned map: node size 0xa4 = 0x14 + 0x90, mem = file + 0x14!)
//    Fixed struct copy: rep movsd ecx = 0x24 at 0x55d740..0x55d749 -> 0x24 * 4 = 0x90 (144) bytes!
//      file+0x00 (mem+0x14): u32 playerId            (returned as base ptr by 0x55d8a0: add eax, 0x14)
//      file+0x30 (mem+0x44): u32 roleOrVoiceType     (getter 0x55d810 returns true iff == 2 or == 4)
//      file+0x3c.. (mem+0x50..): f32 growthOrResist[] (indexed getter 0x55d870: movss xmm0, [eax + idx*4 + 0x50])
//
// 3. CommandData.pck (364 records: CommandData_0000.bin ..)
//    Loader: 0x554940 (calls 0x554780) -> map [0x7389c4] (node size 0x58 = 0x18 + 0x40, mem = file + 0x18)
//    Fixed struct copy: 4x movups at 0x55497e..0x5549c0 -> 0x40 (64) bytes!
//      file+0x00 (mem+0x18): u32 commandId           (base ptr getter 0x554a50: add eax, 0x18)
//      file+0x10.. (mem+0x28..): { u32 subParam, ... }[] (stride 8 getter 0x554a20: [eax + idx*8 + 0x28])
//
// 4. EnchantData.pck (280 records: EnchantData_0000.bin ..)
//    Loader: 0x556590 -> map [0x7389d0] (node base offset: mem = file + 0x18)
//    Fixed struct copy: 3x movups (0x30) + 1x movq (0x08) at 0x556710..0x55675a -> 0x38 (56) bytes!
//      file+0x00 (mem+0x18): u32   enchantId         (map key)
//      file+0x08 (mem+0x20): u32->char* name         (prefixed by category icon string at 0x5567a0..0x556860)
//      file+0x20 (mem+0x38): u32   flags             (bit 0 = stackable! Read at 0x4f5499:
//                                                     if bit 0 == 0, CGamePlayerStatus enchant count loop
//                                                     at 0x4f54b4..0x4f54bb stops at 1; if bit 0 == 1, sums all)
//      file+0x24 (mem+0x3c): u32   iconCategory      (0..10 jump table at 0x5568f4 -> prefix 0x68c0d4..0x68c2b0)
//    RNG calls: 0.
```

**Program Evidence:**
```asm
0055310c  mov      eax, dword ptr [eax + 0x18]
0055310f  shr      eax, 1
00553111  and      al, 1
0055d740  mov      ecx, 0x24
0055d749  rep movsd dword ptr es:[edi], dword ptr [esi]
0055d831  cmp      dword ptr [eax + 0x44], 4
0055d852  cmp      dword ptr [eax + 0x44], 2
0055d891  movss    xmm0, dword ptr [eax + esi*4 + 0x50]
0055d8bc  add      eax, 0x14
0055497e  movups   xmm0, xmmword ptr [esp + 0x60]
005549c0  movups   xmmword ptr [esp + 0x60], xmm0
00554a41  mov      eax, dword ptr [eax + esi*8 + 0x28]
00554a6c  add      eax, 0x18
0055674c  movups   xmmword ptr [esp + 0xa8], xmm0
0055675a  movq     qword ptr [esp + 0xb8], xmm0
005567a0  mov      eax, dword ptr [ecx + 0x3c]
004f5499  mov      bl, byte ptr [eax + 0x38]
004f54a2  and      bl, 1
```
