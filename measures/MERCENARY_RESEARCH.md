# Investigación sobre el Sistema de Mercenarios ("Mercenary Buddy" / 傭兵バディ) en *Dungeon Travelers 2-2*

Este documento responde con evidencia verificada en el ejecutable (`DT22_en_unwrapped.exe`), los paquetes de datos del juego (`Data/ENG/NPC/NPC.pck`, `Parameter/StringData.pck`, `Parameter/QuestRankData.pck`, `Script/ShopBar.pck`) y guías de referencia a las 7 preguntas sobre cómo funcionan los mercenarios (*guest allies* / `NPC` / 傭兵バディ), y detalla los cambios exactos que requiere el simulador (`engine_cs/src/DtEngine/` y `tools/npc_data.py`).

---

## 1. Resumen

* **Hipótesis previa (a) — "¿El mercenario ocupa el mismo hueco que la invocación del grand sealbook y la sustituye?"**: **FALSA (`Leído en código` + `Dicho por una guía`)**. La invocación del gran sello (`CGamePlayerStatusETCSummon`, unidad de batalla `3000` / `0xbb8`) y el mercenario (`CGamePlayerStatusETCNPC`, unidad de batalla `3001` / `0xbb9`) ocupan punteros distintos en `CGameWork`, casillas distintas en el HUD de combate y se instancian simultáneamente al inicio de la batalla junto con las muñecas (*dolls*, unidades `2000..2999`).
* **Hipótesis previa (b) — "¿Se usa la etapa de nivel más alto que no supera el nivel de la party (`UnitFactory.GuestStage`)?"**: **FALSA (`Leído en código` + `Dicho por una guía`)**. El nivel de la party jamás se consulta; cada etapa de `NPCData.bin` tiene su propio **flag de desbloqueo** en el offset `0xB4` (memoria `+0xCC`), y el menú del bar (`0x58adb0`) ofrece **una única etapa por mercenario**: la de mayor nivel entre aquellas cuyo flag esté activo (por progreso de capítulos, jefes derrotados o Rango de Misiones 19).

1. **¿Cómo se contrata un mercenario y desde qué punto de la historia?** (`Leído en código` + `Dicho por una guía`)
   Se contrata en la taberna (**Tavern** -> menú **Hire**, clase `Shop::CShopMenuBar`, `0x589b70`), que se desbloquea en el mapa del mundo a mitad del **Capítulo 7** durante el Templo de Wrappl (flag `135`, `StringData` `0x16e`: *"The Tavern has been added to the World Map."*), después de que Michelle acompaña temporalmente al grupo como invitada de historia (`id=10`, coste `0`, duración `-1`). Contratar cuesta oro (`NPCData` offset `0xAC`, **no** es HP máximo como asumía `tools/npc_data.py`), reducido por la pasiva *Negotiation* (`交渉`, efecto `0x11a`, función `0x4762c0`) de Treasure Hunter; solo puede haber 1 mercenario contratado a la vez y contratar a otro reemplaza el contrato activo tras confirmación (`0x58b750`).
2. **¿Qué decide qué etapa (nivel/estadísticas) de un mercenario se ofrece o se usa?** (`Leído en código` + `Dicho por una guía`)
   Cada registro de etapa en `NPCData.bin` almacena un ID de flag global en el offset `0xB4` (memoria `[eax+0xcc]`). Al abrir el menú *Hire* (`0x58adb0`–`0x58b060`), el juego filtra los registros cuyo flag está activo (`vtable[0x200](flag) != 0`), agrupa por `CharacterID` (`0x10`, memoria `[eax+0x28]`) y conserva **únicamente el registro con mayor `level` (`0x18`, memoria `[eax+0x30]`)** (`0x58af86`). Los flags se activan al avanzar capítulos (Cap. 7 a 11, Post-game 異章1 y 異章2), derrotar ciertos jefes (Octopunch, 8 dioses, etc.) o alcanzar el **Quest Rank 19** (`QuestRankData_19.bin`, 840 pts -> flag `1419`, *"Several mercenary's levels increased."*).
3. **¿Un mercenario contratado cambia de etapa o sube de nivel solo al avanzar? ¿Cuánto dura el contrato?** (`Leído en código` + `Dicho por una guía`)
   **No sube de nivel ni cambia de etapa mientras está contratado**: el `npc_id` exacto queda guardado en `CGamePlayerStatusETCNPC+0x170` (`0x4fef40`) hasta que termina el contrato o se contrata otro. El contrato dura el número de **combates ganados** indicado en `NPCData` offset `0xB0` (memoria `[eax+0xc8]`: `1` para Peggy & Beard, `5..30` para el resto, `-1` infinito para Michelle): el contador `+0x174` sube en +1 al ganar una batalla (`0x446554`), huir no consume contrato, salir de la mazmorra o guardar/cargar partida no lo cancela (`0x47371a`), y en batallas contra jefes (`byte [ebx+0xc] != 0` en `0x447146`) se omite la comprobación de expiración para que nunca abandone tras un jefe.
4. **¿Comparte hueco con la invocación del grand sealbook? ¿Pueden estar a la vez? ¿Y con las muñecas (dolls)?** (`Leído en código` + `Dicho por una guía`)
   **No comparten hueco y pueden estar todos a la vez en combate**: las 5 miembros de la party (`0..4`), las muñecas del Doll Master (`2000..2999`, `0x7d0..0xbb7`), la invocación del gran sello (**unidad `3000` / `0xbb8`**, creada en `0x449771`) y el mercenario (**unidad `3001` / `0xbb9`**, creada inmediatamente después en `0x449839`). Además, las mercenarias Doll Master (Marion y las DLC Nekone y Hatsune) invocan sus propias muñecas en el rango `2000..2999`. `docs/FORMULAS.md` §16.5 decía que ambos usaban `3000` porque vio `0x4497ce` (summon) y el filtro `sub eax, 0xbb8; cmp eax, 0x3e7; jbe` (`3000..3999`), pero el mercenario es `3001` (`0x449896`).
5. **¿Cómo actúa en combate (IA propia, NPCAIData), recibe daño, puede morir, se le puede curar, cuenta para victoria/derrota?** (`Leído en código` + `Dicho por una guía`)
   Actúa de forma autónoma según su máquina de estados en `NPCAIData.bin` (`0x430460`, `0x430f10`–`0x431206`, idéntica a la de enemigos y summons, con pesos por ranura y reglas condicionales pre/post turno) y ejecuta habilidades pasivas (`0x94` = nº de pasivas `0..2`, `0x98..` = IDs en `EnemyAttackData`, cargadas en `0x4ff2bb`–`0x4ff446`). **No tiene HP ni TP** (`0x4fec90` solo inicializa nivel y las 6 estadísticas `ATK..AGI`), **nunca puede ser elegido como objetivo** (el filtro `0x43e6d0` excluye `2000..2999` y `3000..3999` de cualquier selección individual, fila o grupo), **no sufre daño ni veneno** (`0x43662c` salta `3000..3999`), **no puede morir** y **no cuenta para victoria/derrota**.
6. **¿Qué son los registros 101, 102 y 103 de NPC.pck (ids 0–2, personajes 300–302)? ¿Y los registros 10 (Michelle) y 15 (Peggy & Beard)?** (`Leído en código` + `Dicho por una guía`)
   Los registros `0000.pck` (`id=0`, `ch=300`, `"101"`, flag `1000`), `0001.pck` (`id=1`, `ch=301`, `"102"`, flag `1001`) y `0002.pck` (`id=2`, `ch=302`, `"103"`, flag `1002`) son **registros de prueba/desarrollo** (nombrados por sus texturas internas `N0101`–`N0103`): el código los excluye explícitamente del trofeo de contratación (`0x47731e`: `cmp edi, 0xa; jle`) y usa `id=0` ("101") como *fallback* de seguridad si se abre el menú de la taberna sin ningún flag de mercenario activo (`0x58b027`). `0010.pck` (**Michelle**, `id=10`, `ch=411`, coste `0`, duración `-1`) es una **invitada de historia** en el Cap. 7 añadida/quitada por script (`opcodes` `0x81`/`0x82`, `0x4c979f`/`0x4c97ba`). `0015.pck` (**Peggy & Beard**, `id=15`, `ch=488`, coste `1000`, duración `1`, flag `1106`) es un **mercenario temporal de broma** contratable en la taberna solo entre el 9.º evento de charla (Cap. 8) y el 10.º (Cap. 9).
7. **Lista de todos los mercenarios contratables con sus etapas y disponibilidad:** (`Leído en código` + `Dicho por una guía`)
   En `NPC.pck` del juego base hay **87 registros** repartidos en **27 personajes** (`CharacterID`): 3 de prueba (`101`, `102`, `103`), 1 invitada de historia (`Michelle`), 1 temporal de broma (`Peggy & Beard`), **17 mercenarios estándar** de 2, 3 o 5 etapas (`Euphemia`, `Tatiana`, `Luzie`, `Natalia`, `Carol`, `Sasha`, `Priscilla`, `Neya`, `Estelle`, `Rebecca`, `Chloe`, `Marion`, `Riesco`, `Paracas`, `Medved`, `Mekelle`, `Momona`, `Azmaria`, `Miranda`, `Euthys`, `Lolo` — 21 en total contando reclutables por eventos secundarios/post-game) y **5 dioses del post-game** de 2 etapas (`Three Fates`, `Yoshitsune`, `Marduk`, `Citlalinicue`, `Arjuna`). Además, el ejecutable soporta **9 mercenarios DLC** (`Marie`, `Setsuna`, `Kazusa`, `Nekone`, `Anju`, `Kleito`, `Tarte`, `Hatsune`, `Chizuru`, de 5 etapas cada uno) si existen sus carpetas DLC (`0x463578`). La tabla completa se detalla en la Sección 2.8.

---

## 2. Evidencia del código (`DT22_en_unwrapped.exe` y archivos `.pck`)

**Método de verificación:** Desensamblado directo de `DungeonTravelers2-2_EN/DT22_en_unwrapped.exe` (base `0x400000`) mediante `tools/exe_dis.py`, búsqueda de referencias con `tools/exe_who_calls.py` y `tools/exe_find_const.py`, e inspección binaria de `Data/ENG/NPC/NPC.pck`, `Data/ENG/Parameter/StringData.pck`, `Data/ENG/Parameter/QuestRankData.pck` y `Data/ENG/Script/ShopBar.pck` mediante `tools/pck_handler.py`.

### 2.1. Estructura real de `NPCData.bin` (corrección de `tools/npc_data.py` y `record_layouts.json`)

En `CContentsManager::_InitializeNPC` (`0x463420`–`0x464180`), cada archivo `NNNN.pck` dentro de `NPC/NPC.pck` (y opcionalmente en paquetes DLC mediante `0x463578` `/NPC/%s`) se carga y se inserta en el mapa global `0x738a04` (`Contents::CNPCData`, `0x55cfa0`). Cuando se accede a un nodo del mapa `0x738a04` mediante `0x507310(&iter, &npc_id)` y se desreferencia `eax = *iter`, los campos de `NPCData.bin` quedan desplazados **`+0x18` bytes** en memoria (`mem_offset = file_offset + 0x18`).

| Offset archivo | Offset memoria (`[eax + ...]`) | Tipo | Nombre real | Uso verificado en el ejecutable y correcciones respecto al repo actual |
|---|---|---|---|---|
| `0x00` | `+0x18` | `int32` | `id` (`NPCID`) | Clave primaria del mapa `0x738a04` (`0..195`). |
| `0x08` | `+0x20` | `uint64` / `char*` | `name_ptr` | En archivo es el offset al nombre (`0xD4`, precedido en `0xD3` por un `uint8` con la longitud). En `0x55d08f` se convierte en puntero a string. |
| `0x10` | `+0x28` | `int32` | `character_id` | ID de modelo/personaje compartido por todas las etapas de un mismo mercenario (`300..330`, `411`, `488`). Leído en `0x55d340` y `0x58af18`. |
| `0x14` | `+0x2C` | `int32` | `dlc` | `0` en los 87 registros base (`Data.txt` tiene `DLC = 0`). Comprobado con `test byte ptr [eax+0x2c], 1` en `0x58aef1` (menú del bar), `0x476e32` y `0x477344` (trofeo de contratar a todos los mercenarios no-DLC). |
| `0x18` | `+0x30` | `int32` | `level` | Nivel fijo de la etapa. Leído en `0x4fed2d` y comparado en `0x58af86` para elegir la etapa de mayor nivel. |
| `0x1C` | `+0x34` | `int32` | `weapon_rank` | Índice (`0..11`) en la tabla `WeaponRankData` (`0x738a94`). Leído en `0x4feeb0` (`CGamePlayerStatusETCNPC::GetWeaponRankSpeed`) para obtener el multiplicador de retardo de turno tras actuar. |
| `0x20..0x34` | `+0x38..+0x4C` | `int32[6]` | `stats[6]` | `ATK`, `DEF`, `INT`, `RES`, `DEX`, `AGI` base de la etapa. Copiados en `0x4fed59`–`0x4fee27`. |
| `0x38` | `+0x50` | `int32` | `attack_count` | Número de habilidades activas (`1..11`). |
| `0x3C..0x93` | `+0x54..+0xAB` | `(int32, int32)[11]` | `attacks[11]` | Pares `(enemy_attack_id, 0)` de 8 bytes cada uno. |
| **`0x94`** | **`+0xAC`** | `int32` | **`passive_count`** | **CORRECCIÓN:** `tools/npc_data.py` lo llamaba `kind`. Es el **número de habilidades pasivas** (`0`, `1` o `2`). En `0x4ff2bb`–`0x4ff446` y `0x4a33f0`–`0x4a3453` es el límite del bucle `for (i = 0; i < [eax+0xac]; i++)`. |
| **`0x98..0xAB`** | **`+0xB0..+0xC3`** | `int32[5]` | **`passive_ids[5]`** | **CORRECCIÓN:** Array de hasta 5 IDs de `EnemyAttackData` (4 bytes cada uno; `-1` si vacío). `tools/npc_data.py` solo leía el primero (`0x98`), perdiendo la **segunda pasiva** en los registros con `passive_count == 2`: Three Fates (`0027`, `0028`: `[1526, 2648]`), Chloe Lv68 (`0136`: `[2681, 1538]`), Azmaria Lv93 (`0177`: `[1524, 1526]`) y Miranda (`0180..0184`: `[1538, 2682]`). |
| **`0xAC`** | **`+0xC4`** | `int32` | **`hire_cost`** | **CORRECCIÓN CRÍTICA:** `tools/npc_data.py` y `Units.cs` lo llamaban `hp` / `MaxHp`. **¡NO ES EL HP MÁXIMO!** Es el **coste de contratación en oro (Gold)** (`0` para Michelle, `100..9999` para los demás). Leído por el getter `0x55d390` (`mov eax, [eax+0xc4]`) en `0x58a620`, `0x58b651` (muestra `"Cost"` en el bar) y `0x58b799` (cobra el oro al contratar). |
| **`0xB0`** | **`+0xC8`** | `int32` | **`contract_battles`** | **Duración del contrato en combates ganados** (`-1` infinito para Michelle; `1` para Peggy & Beard; `3..30` para los demás). Leído en `0x58b521` (muestra `"%number times"` con `StringData` `0x22c`) y en `0x447188` / `0x4471cb` (comprobación de fin de contrato tras ganar una batalla). |
| **`0xB4`** | **`+0xCC`** | `int32` | **`unlock_flag`** | **ID del flag global de progreso (`135..1419`)** que habilita esta etapa en la taberna. Comprobado en `0x58ae86` mediante `CGameWork::CheckFlag` (`vtable[0x200]`). |
| `0xB8..0xD2` | `+0xD0..+0xEA` | `int32[6]` + `u8[3]` | `bustup_rect` | Dimensiones y desplazamiento del retrato (`width`, `0`, `height`, `0`, `offset_x`, `offset_y`, `0`). |

---

### 2.2. Pregunta 1 y Pregunta 2: Menú del Bar (`Shop::CShopMenuBar`), Selección de Etapa, Coste y Descuento

La clase `Shop::CShopMenuBar` (vtable `0x6d6d9c`, constructor en `0x589b70`) gestiona el menú **Hire** de la Taberna (`Tavern`).

#### A. Construcción de la lista de mercenarios disponibles y elección de etapa (`0x58adb0`–`0x58b060`)

Cuando se abre el menú de contratación (`0x589c8f -> call 0x58adb0`), el juego recorre todos los registros de `0x738a04` (`NPCData`):

```c
// Pseudocódigo exacto de Shop::CShopMenuBar::BuildMercenaryList (0x58adb0 - 0x58b060)
void CShopMenuBar::BuildMercenaryList(CShopMenuBar* this) {
    int current_npc_id = g_GameWork->pETCNPC->npc_id; // [0x71fc24]->0x1424->0x170 (0x58add6)
    int current_char_id = -1;
    if (current_npc_id != -1) {
        NPCData* cur = g_NPCDataMap->Find(current_npc_id);
        if (cur != NULL)
            current_char_id = cur->character_id; // [eax+0x28] (0x58ae15)
    }

    std::vector<int> candidates; // [ebp-0x28]
    for (auto it = g_NPCDataMap->begin(); it != g_NPCDataMap->end(); ++it) {
        NPCData* npc = it->second;
        // 1. Excluye el mercenario que ya está contratado actualmente (por CharacterID)
        if (current_char_id != -1 && npc->character_id == current_char_id)
            continue; // 0x58ae64

        // 2. Comprueba si el flag de desbloqueo de esta etapa (offset 0xB4 / mem +0xCC) está activo
        int flag_id = npc->unlock_flag; // mov eax, [eax+0xcc] en 0x58ae77
        if (!g_GameWork->GetFlag(flag_id)) // call dword ptr [edx+0x200] en 0x58ae86
            continue;

        // 3. Si es DLC (bit 0 de offset 0x14 / mem +0x2C), verifica que el DLC esté instalado
        if ((npc->dlc & 1) != 0) { // test byte ptr [eax+0x2c], 1 en 0x58aef1
            if (!g_DLCManager->IsInstalled(npc->character_id)) // call 0x467940 en 0x58af03
                continue;
        }

        // 4. Busca si ya hay otra etapa del mismo CharacterID en 'candidates' (0x58af0c - 0x58af5b)
        int existing_idx = -1;
        for (size_t i = 0; i < candidates.size(); ++i) {
            NPCData* other = g_NPCDataMap->Find(candidates[i]);
            if (other->character_id == npc->character_id) { // cmp [eax+0x28], edi en 0x58af47
                existing_idx = (int)i;
                break;
            }
        }

        if (existing_idx == -1) {
            // Primera etapa encontrada para este CharacterID: la añade (0x58af9b)
            candidates.push_back(npc->id);
        } else {
            // Ya había una etapa de este CharacterID: compara sus niveles (offset 0x18 / mem +0x30)
            NPCData* prev = g_NPCDataMap->Find(candidates[existing_idx]);
            int prev_level = prev->level; // mov edi, [eax+0x30] en 0x58af71
            if (prev_level < npc->level) { // cmp edi, [eax+0x30]; jge 0x58afad en 0x58af86
                candidates[existing_idx] = npc->id; // Sustituye por la etapa de MAYOR nivel (0x58af8b)
            }
        }
    }

    // 5. Fallback de seguridad (0x58b023): si ningún flag está activo y la lista quedó vacía,
    // inserta por defecto el npc_id = 0 ("101")
    if (candidates.empty()) {
        candidates.push_back(0); // mov [ebp-0x18], 0 en 0x58b027
    }
}
```

**Conclusiones probadas por `0x58adb0`–`0x58b060`:**
1. **No existe ninguna comparación con el nivel de la party.**
2. **El jugador no puede elegir entre distintas etapas de un mismo mercenario**: el bucle `0x58af0c`–`0x58af8b` colapsa todas las etapas desbloqueadas de un mismo `character_id` y deja únicamente la de mayor `level` (`[eax+0x30]`).
3. **El mercenario actualmente contratado no aparece en la lista del bar** (`0x58ae64`), por lo que no se puede renovar su contrato hasta que expire o se contrate a otro mercenario distinto.

#### B. Coste en oro, descuento por *Negotiation* (`0x4762c0`) y contratación (`0x58b750`, `0x4772e0`)

* **Visualización en el menú del bar (`0x58b430`–`0x58b745`)**:
  * En `0x58b521` obtiene `contract_battles` (`[eax+0xc8]`, archivo `0xB0`) y lo formatea con el string `0x22c` (`"%number times"`).
  * En `0x58b651` obtiene `hire_cost` (`call 0x55d390` -> `[eax+0xc4]`, archivo `0xAC`), aplica `0x4762c0` (descuento) y lo muestra bajo la etiqueta `0x22d` (`"Cost"`).
* **Descuento por la habilidad pasiva *Negotiation* (`交渉`) de Treasure Hunter (`0x4762c0`–`0x47632e`)**:
  ```c
  // Pseudocódigo de CalcDiscountedPrice (0x4762c0)
  int CalcDiscountedPrice(int base_cost) {
      if (base_cost <= 0) return 0; // 0x4762c9
      // Obtiene el valor total del efecto pasivo 0x11a (282 = Negotiation / Mercenary & Shop Discount)
      // en los miembros activos de la party (call 0x4e4850 con push 0x11a en 0x4762d5)
      float discount_pct = GetPartyPassiveEffectSum(0x11a);
      int price = (int)((1.0f - discount_pct * 0.01f) * (float)base_cost); // 0x4762e6 - 0x47631b
      return (price < 1) ? 1 : price; // 0x47631f: mínimo 1G si base_cost > 0
  }
  ```
* **Ejecución del contrato (`0x58b750`–`0x58b891` y `0x4772e0`–`0x4773cb`)**:
  * Al pulsar contratar en `0x58b750`, calcula el coste con `0x55d390` + `0x4762c0` y lo compara con el oro del grupo (`vtable[0x4c]`). Si no alcanza, reproduce SE de error (`0x58b86d`).
  * Si ya hay un mercenario contratado (`[edi+0x40] != -1` en `0x58a660`), muestra el diálogo de confirmación `StringData` `0x20a`: *"Your current contract with %name will end. Is this okay?"*.
  * Al confirmar, `0x58b7b0` resta el coste en oro (`vtable[0x48](-cost)`) y llama a `HireNPC` (`0x4772e0`):
    ```c
    // Pseudocódigo de HireNPC (0x4772e0 - 0x4773cb)
    void HireNPC(CGameWork* work, int npc_id, int arg2) {
        // Pone el nuevo mercenario en CGamePlayerStatusETCNPC (+0x1424)
        // Esto fija npc_id en +0x170, resetea battles_fought (+0x174) a 0 y recalcula stats (0x4fec90)
        work->pETCNPC->SetNPC(npc_id, 1, 0, 0); // call 0x4fef40 en 0x47730c

        // Seguimiento para el trofeo "Veteran Employer" (contratar a todos los mercenarios)
        // Ignora los IDs <= 10 (0=101, 1=102, 2=103, 10=Michelle) y el ID 15 (Peggy & Beard)
        if (npc_id > 10 && npc_id != 15) { // cmp edi, 0xa; jle ... cmp edi, 0xf; je en 0x47731e-0x477328
            NPCData* data = g_NPCDataMap->Find(npc_id);
            if (data != NULL && (data->dlc & 1) == 0) { // excluye DLC (0x477344)
                // Marca el flag (character_id + 900) como contratado al menos una vez (flags 1205..1230)
                work->SetFlag(data->character_id + 900, 1); // lea eax, [esi+0x384]; call [edx+0x1fc] en 0x477350
                // Comprueba los 21 CharacterIDs estándar/dioses: si todos tienen su flag activo, da el trofeo 0x1e (30)
            }
        }
    }
    ```

---

### 2.3. Pregunta 3: Duración del Contrato, Contador de Batallas y Expiración

El objeto `Game::CGamePlayerStatusETCNPC` (tamaño `0x188`, creado en `0x472814` y guardado en `CGameWork+0x1424`) tiene dos campos de estado al final de su estructura (inicializados en `0x4febaf` y limpiados en `0x4fef00`):
* **`+0x170` (`int32 npc_id`)**: ID del registro `NPCData` contratado actualmente (`-1` si no hay ninguno).
* **`+0x174` (`int32 battles_fought`)**: Número de batallas ganadas desde que se contrató (`0` al contratar en `0x4fef7f`).

Ambos campos se guardan y cargan directamente en el archivo de guardado (`0x47371a` y `0x473ef0`), por lo que **salir de la mazmorra, volver a la base o apagar el juego NO consume ni cancela el contrato**.

#### Incremento al ganar una batalla (`0x44654f`–`0x446568`)
Al terminar una batalla con **victoria**, antes de reproducir el BGM de victoria (`BGM_0460.bgm`), `CBattleManager` ejecuta:
```nasm
0044654f  mov  eax, dword ptr [0x71fc24]      ; g_GameWork
00446554  mov  eax, dword ptr [eax + 0x1424]  ; pETCNPC
0044655a  cmp  dword ptr [eax + 0x170], -1    ; ¿hay mercenario contratado?
00446561  je   0x446569
00446563  inc  dword ptr [eax + 0x174]        ; battles_fought++
```
Si el grupo huye de la batalla, el flujo no pasa por `0x44654f` y `battles_fought` (`+0x174`) no se incrementa.

#### Comprobación de expiración tras la batalla (`0x4445e4`, `0x447120`–`0x4472c4`, `0x4446af`–`0x4446c5`)
En la secuencia post-batalla (después de los diálogos de subida de nivel y desbloqueo de trajes), el estado `3` llama a `0x447120`:
```c
// Pseudocódigo exacto de CBattleManager::CheckMercenaryExpiration (0x447120 - 0x4472c4)
bool CBattleManager::CheckMercenaryExpiration(CBattleManager* this) {
    // 1. Si es una batalla de jefe / evento (this->is_boss_battle en +0x0C != 0), NUNCA expira aquí
    if (this->is_boss_battle != 0) // cmp byte ptr [ebx+0xc], 0; jne 0x4472b4 en 0x447146
        return false;

    CGamePlayerStatusETCNPC* etcNpc = g_GameWork->pETCNPC; // [esi+0x1424]
    int npc_id = etcNpc->npc_id; // [edi+0x170]
    if (npc_id == -1)
        return false;

    NPCData* data = g_NPCDataMap->Find(npc_id);
    // Guarda los combates restantes (contract_battles - battles_fought) en la variable del sistema 0x250 (592)
    g_GameWork->SetSystemVar(0x250, data->contract_battles - etcNpc->battles_fought); // 0x447188 - 0x44719a

    // 2. Si contract_battles == -1 (Michelle), el contrato es infinito y nunca expira
    if (data->contract_battles == -1) // cmp dword ptr [eax+0xc8], -1; je 0x4472a1 en 0x4471cb
        return false;

    // 3. Si battles_fought >= contract_battles, muestra el mensaje 0x96:
    //    "%name's contract period expired. %name departed."
    if (etcNpc->battles_fought >= data->contract_battles) { // cmp esi, [eax+0xc8]; jl 0x4472a1 en 0x4471d9
        ShowBattlePopupMessage(0x96, etcNpc->GetName()); // 0x4471f0 - 0x447290
        return true; // pasa al estado 4 de post-batalla
    }
    return false;
}
```
Cuando `0x447120` devuelve `true` y el jugador cierra el mensaje emergente, `0x4446b4`–`0x4446c0` llama a `pETCNPC->Clear()` (`call 0x4fef00`), que pone `npc_id = -1` y `battles_fought = 0`.
*(Nota: Si en un combate normal el contador llega al límite o lo supera durante una batalla de jefe donde `this->is_boss_battle != 0`, el mercenario permanece hasta el siguiente combate normal o hasta que un script ejecute el opcode `0x82` en `0x4c97ba`).*

---

### 2.4. Pregunta 4: Coexistencia con la Invocación del Gran Sello (`3000`) y las Muñecas (`2000..2999`)

En `CGameWork` (`[0x71fc24]`), existen dos objetos completamente independientes (inicializados en `0x47279f`–`0x472840`):
* **`[CGameWork + 0x141c]`**: `Game::CGamePlayerStatusETCSummon*` (la invocación equipada mediante un Grand Sealbook).
* **`[CGameWork + 0x1424]`**: `Game::CGamePlayerStatusETCNPC*` (el mercenario contratado en el bar o unido por historia).

#### Creación simultánea al inicio del combate (`0x449750`–`0x4498f8`)
En la inicialización de unidades de `CBattleManager`, tras crear a las 5 miembros de la party (`0..4`), el código comprueba **ambos** punteros en secuencia:

```nasm
; --- 1. Creación de la Invocación del Gran Sello (Summon) -> Unidad 3000 (0xbb8) ---
00449755  mov   eax, dword ptr [0x71fc24]
0044975a  mov   ecx, dword ptr [eax + 0x141c]  ; pETCSummon
00449760  cmp   dword ptr [ecx + 0x170], -1    ; ¿hay Summon activo?
00449767  je    0x44981d                       ; si no hay Summon, salta al bloque del Mercenario
...
004497ce  mov   dword ptr [esi + 0x20], 0xbb8  ; Unit ID = 3000 (Summon)
004497d5  mov   ecx, dword ptr [eax + 0x141c]
004497db  push  ecx
004497dc  mov   ecx, esi
004497de  call  0x430410                       ; Inicializa SummonAIData (0x738a7c)

; --- 2. Creación del Mercenario (Guest / NPC) -> Unidad 3001 (0xbb9) ---
0044981d  mov   eax, dword ptr [0x71fc24]
00449822  mov   ecx, dword ptr [eax + 0x1424]  ; pETCNPC
00449828  cmp   dword ptr [ecx + 0x170], -1    ; ¿hay Mercenario activo?
0044982f  je    0x4498f8
...
00449896  mov   dword ptr [esi + 0x20], 0xbb9  ; Unit ID = 3001 (Mercenary)
0044989d  mov   ecx, dword ptr [eax + 0x1424]
004498a3  push  ecx
004498a4  mov   ecx, esi
004498a6  call  0x430460                       ; Inicializa NPCAIData (0x7389a8)
```

Además, en el renderizado del HUD de batalla (`0x4e7cb7`–`0x4e7f60`), las placas de estado se dibujan en posiciones fijas separadas:
* **Slot 6 (Mercenario)**: `[0x71fc24]+0x1424` en las coordenadas `(x = 24, y = 834)` (`0x4e7ce5`–`0x4e7d06`).
* **Slot 7 (Summon)**: `[0x71fc24]+0x141c` en las coordenadas `(x = 140, y = 834)` (`0x4e7d19`–`0x4e7d3a`).
* **Slots de Muñecas (Dolls)**: Unidades `2000..2999` (`0x7d0..0xbb7`), hasta 5 simultáneas en la fila de muñecas (`0x4e7d40`+).

---

### 2.5. Pregunta 5: Estadísticas, Pasivas, Inmunidad/Intargetabilidad e IA en Combate

#### A. Cálculo de estadísticas y bonos DLC (`0x4fec90`–`0x4fee42`, `0x4ff630`)
En `CGamePlayerStatusETCNPC::SetupStats` (`0x4fec90`), el objeto hereda de `CGamePlayerStatusBase` (`0x4f9f00`), pero **solo inicializa el nivel y las 6 estadísticas (`ATK`, `DEF`, `INT`, `RES`, `DEX`, `AGI`)**:
1. Si el DLC `0x129` (297, *"Mercenary Buddy Guide"* / bono plano de mercenario) está instalado (`0x4fecc0`), suma `+30` a cada una de las 6 estadísticas en `+0xd0..+0xe4`.
2. Copia `level` (`[eax+0x30]`) y suma `stats[0..5]` (`[eax+0x38..0x4c]`) a la base.
3. En el getter de cada estadística (`0x4ff630`), si el DLC `0x127` (295) está instalado (`0x4ff668`), multiplica la estadística por `1.1f` (`0x6d985c`, `+10%`).
4. **No inicializa ni modifica HP ni TP** (quedan en 0 y el HUD del mercenario en `0x4ff060`–`0x4ff28d` solo dibuja retrato, icono de estado y nivel `"Lv %d"`).

#### B. Carga de habilidades pasivas (`0x4ff290`–`0x4ff46d`)
`CGamePlayerStatusETCNPC` sobrescribe el método virtual de pasivas (`0x4ff290`). Recorre el bucle `for (i = 0; i < npc->passive_count; ++i)` leyendo los IDs de `EnemyAttackData` desde `npc + 0xb0 + 4*i` (`0x4ff2bb`–`0x4ff446`, offset de archivo `0x98 + 4*i`) e instancia cada efecto pasivo en la lista de pasivas de la unidad.
Las pasivas usadas por los mercenarios en `NPCData.bin` son:
* `1522` / `1523`: Double Attack (`30%` / `60%`)
* `1524` / `1525`: Triple Attack (`25%` / `50%`)
* `1526` / `1527` / `1528`: Chain Attack / Ranged Multi-Attack
* `1538`: Interrupt Shot (`インターラプトショット`, disparo interruptivo al inicio de acción enemiga)
* `1561`: Maid's Help / Cierre post-batalla (Paracas)
* `2648`: Magical Barrier (`マジカルバリア`, Three Fates)
* `2680` / `2681` / `2682` / `2683`: Follow-up Attack / Ranged Follow-up (`チェイス` / `フォロー`, Chloe, Miranda, Arjuna)

#### C. Intargetabilidad, inmunidad a daño/estados y exclusión de victoria/derrota (`0x43e6d0`, `0x43662c`)
En `CBattleManager::IsTargetableUnit` (`0x43e6d0`):
```nasm
0043e6e5  mov   eax, dword ptr [esi + 0x20] ; unit_id
0043e6e8  sub   eax, 0x7d0                  ; unit_id - 2000 (Dolls: 2000..2999)
0043e6ed  cmp   eax, 0x3e7                  ; <= 999?
0043e6f2  jbe   0x43e727                    ; -> return 0 (no seleccionable)
0043e6f4  mov   eax, dword ptr [esi + 0x20]
0043e6f7  sub   eax, 0xbb8                  ; unit_id - 3000 (Summon 3000 y Mercenario 3001)
0043e6fc  cmp   eax, 0x3e7                  ; <= 999?
0043e701  jbe   0x43e727                    ; -> return 0 (no seleccionable)
```
Por tanto, ni los ataques enemigos (individuales, de fila o de área) ni los hechizos aliados que piden objetivo pueden apuntar a las unidades `3000` (Summon) o `3001` (Mercenario). Asimismo, en `0x43662c` el chequeo de daño por turno (veneno, etc.) salta cualquier unidad en `3000..3999`. Tampoco forman parte del bucle de miembros de la party (`0..4`) que comprueba la derrota (party wipe).

#### D. Máquina de estados de IA (`NPCAIData.bin`, `0x430460`, `0x430f10`–`0x431206`)
En `0x4498a6`, la unidad `3001` inicializa su controlador de IA mediante `0x430460`, que busca su `NPCAIData.bin` en el mapa global `0x7389a8`. Cuando llega el turno de la unidad `3001`, ejecuta exactamente la misma función `CBattleAI::SelectAction` (`0x430f10`) que los enemigos y las invocaciones:
1. Evalúa las reglas condicionales pre-acción del estado actual (`0x430f59 -> call 0x431aa0`), que pueden cambiar el estado activo (`[esi+8]`) o forzar una ranura de ataque (por ejemplo, Lolo comprueba si hay aliados muertos para usar *Resurrection* `772`, o Carol/Momona/Three Fates comprueban el HP de la party para curar).
2. Si ninguna regla fuerza una acción directa, elige aleatoriamente una de las ranuras de `NPCData.attacks` usando los **16 pesos de probabilidad** del estado actual (`0x431060`).
3. Tras ejecutar la acción, evalúa las reglas condicionales post-acción (`0x43118b -> call 0x431aa0`).
*(Nota: En el simulador actual `Battle.cs`, `StepNpc` ignoraba `NPCAIData.bin` y elegía una habilidad al azar con probabilidad uniforme entre todas las de `unit.Attacks`, lo cual distorsiona a mercenarios cuyas habilidades de resurrección, curación o buff están restringidas por pesos o condiciones en `NPCAIData.bin`).*

---

### 2.6. Pregunta 6: Registros `101`, `102`, `103` (`id=0..2`), `Michelle` (`id=10`) y `Peggy & Beard` (`id=15`)

1. **`0000.pck` (`id=0`, `ch=300`, `"101"`), `0001.pck` (`id=1`, `ch=301`, `"102"`), `0002.pck` (`id=2`, `ch=302`, `"103"`)**:
   * **Qué son:** Registros de prueba/desarrollo (*dummy records*) cuyos nombres (`"101"`, `"102"`, `"103"`) corresponden a los códigos internos de texturas de busto (`N0101`, `N0102`, `N0103`).
   * **Evidencia en código:**
     * Sus flags de desbloqueo (`1000`, `1001`, `1002`) nunca se activan en la historia normal.
     * En `0x47731e` (`HireNPC`), la instrucción `cmp edi, 0xa; jle 0x4773b9` excluye explícitamente todo `npc_id <= 10` del registro de mercenarios contratados para el trofeo.
     * En `0x58b023`–`0x58b027` (`CShopMenuBar::BuildMercenaryList`), si la lista de mercenarios desbloqueados está vacía al abrir el menú del bar, el código inserta `npc_id = 0` (`"101"`) como *fallback* para evitar un puntero nulo.
2. **`0010.pck` (`id=10`, `ch=411`, `"Michelle"`, Lv30, coste `0`, duración `-1`, flag `1003`)**:
   * **Qué es:** Invitada temporal de la historia principal durante el Capítulo 7 (Templo de Wrappl), justo antes de que se desbloquee la Taberna.
   * **Evidencia en código:** Tiene `hire_cost = 0` (`0xAC`), `contract_battles = -1` (`0xB0`, chequeado en `0x4471cb` para que nunca expire por combates) y está excluida del trofeo por `cmp edi, 0xa; jle` (`0x47731e`). Se une mediante el comando de script `0x81` (`0x4c979f`, que llama a `HireNPC`) y abandona el grupo mediante el comando de script `0x82` (`0x4c97ba`, que llama a `pETCNPC->Clear()`).
3. **`0015.pck` (`id=15`, `ch=488`, `"Peggy & Beard"`, Lv35, `INT=500`, coste `1000`, duración `1`, flag `1106`)**:
   * **Qué es:** Mercenario temporal de broma contratable en la Taberna únicamente entre el 9.º evento de conversación en la base (a mitad del Cap. 8, que activa el flag `1106`) y el 10.º evento de conversación (a mitad del Cap. 9, que desactiva el flag `1106`).
   * **Evidencia en código:** Dura `1` solo combate (`contract_battles = 1`) y está excluido explícitamente del trofeo en `0x477323` (`cmp edi, 0xf; je 0x4773b9`).

---

### 2.7. Cómo se desbloquean las etapas: Progreso de Capítulos y Quest Rank 19 (`flag 1419`)

Al cruzar los valores de `unlock_flag` (`0xB4`) de los 87 registros con `Parameter/QuestRankData.pck`, `Parameter/StringData.pck` y la wiki japonesa (`spoiler.jp`), se observa cómo el juego desbloquea las etapas:

1. **Etapas por progreso de capítulos (flags de historia)**:
   * **Flag `135`** (Cap. 7, apertura de la Taberna en el Templo de Wrappl): Desbloquea la Etapa 1 de **Euphemia** (`id=52`, Lv26), **Natalia** (`id=76`, Lv28), **Estelle** (`id=116`, Lv30) y **Chloe** (`id=132`, Lv30).
   * **Flag `136`** (Cap. 7, tras derrotar al jefe del 7.º capítulo / evento de Medved y Momona): Desbloquea la Etapa 1 de **Medved** (`id=158`, Lv33) y **Momona** (`id=168`, Lv32).
   * **Flag `151`** (Cap. 8, inicio): Desbloquea la Etapa 1 de **Tatiana** (`id=60`, Lv36) y **Carol** (`id=84`, Lv37).
   * **Flag `319`** (Cap. 9, inicio): Sube a Etapa 2 a **Euphemia** (`id=53`, Lv38), **Natalia** (`id=77`, Lv40), **Estelle** (`id=117`, Lv41) y **Chloe** (`id=133`, Lv42).
   * **Flag `320`** (Cap. 9, progreso): Desbloquea la Etapa 1 de **Priscilla** (`id=100`, Lv39) y **Rebecca** (`id=124`, Lv43).
   * **Flag `172`** (Cap. 10, inicio): Desbloquea la Etapa 1 de **Luzie** (`id=68`, Lv45), **Sasha** (`id=92`, Lv47), **Paracas** (`id=153`, Lv42) y **Mekelle** (`id=163`, Lv46), y sube a Etapa 2 a **Tatiana** (`id=61`, Lv43) y **Carol** (`id=85`, Lv44).
   * **Flag `197`** (Cap. 11, inicio): Desbloquea la Etapa 1 de **Neya** (`id=108`, Lv50), **Marion** (`id=140`, Lv48) y **Riesco** (`id=148`, Lv49).
   * **Flag `204`** (Cap. 10/11): Sube a Etapa 2 a **Medved** (`id=159`, Lv48) y **Momona** (`id=169`, Lv46).
   * **Flags `353`, `211`, `215`, `220`, `224`** (Cap. 11 tardío / Inicio de Post-game 異章1): Suben a Etapa 2 o Etapa 3 a los mercenarios iniciales.
   * **Flags `230`, `370`, `376`, `381`, `384`, `385`, `400`, `402`, `407`, `318`** (Progreso por las mazmorras del Post-game: 異章1 y 異章2): Suben a las etapas 3, 4 y 5.
2. **Etapa final por Rango de Misiones — Quest Rank 19 (`flag 1419`)**:
   * En `Data/ENG/Parameter/QuestRankData.pck`, el archivo `QuestRankData_19.bin` (Rango 19, requiere `840` puntos de misión, `reward_param = 20`) muestra el mensaje:
     `"Several mercenary's levels increased."` (`StringData` / `QuestRankData_19.bin`).
   * Ese rango activa el **flag `1419`** (`1400 + 19`), que es exactamente el `unlock_flag` (`0xB4`) de la **Etapa 5 (nivel máximo)** de 5 mercenarias:
     * **Luzie** Etapa 5 (`id=72`, Lv87, flag `1419`)
     * **Sasha** Etapa 5 (`id=96`, Lv88, flag `1419`)
     * **Rebecca** Etapa 5 (`id=128`, Lv82, flag `1419`)
     * **Marion** Etapa 5 (`id=144`, Lv86, flag `1419`)
     * **Miranda** Etapa 5 (`id=184`, Lv90, flag `1419`)
3. **Mercenarios desbloqueados por jefes opcionales o eventos secundarios**:
   * **Azmaria** (`ch=327`): Etapa 1 (`id=173`, Lv50, flag `1089`) al derrotarla en su evento secundario; Etapa 5 (`id=177`, Lv93, flag `359`) tras derrotar a los Ocho Dioses (*Eight Gods*).
   * **Miranda** (`ch=328`): Etapa 1 (`id=180`, Lv53, flag `1094`) al encontrarla en la mazmorra (Templo de Wrappl / evento).
   * **Euthys** (`ch=329`): Etapa 1 (`id=187`, Lv74, flag `928`) tras derrotar a Kakinuhito en el Santuario Subterráneo de Serul; Etapa 5 (`id=191`, Lv99, flag `365`) tras derrotar a los Ocho Dioses.
   * **Lolo** (`ch=330`): Etapa 1 (`id=194`, Lv86, flag `1104`) tras derrotar a Octopunch en el Casino Esperanto; Etapa 2 (`id=195`, Lv93, flag `388`) al avanzar en el post-game (異章2).
   * **Los 5 Dioses del Post-game** (`Three Fates` `ch=305`, `Yoshitsune` `ch=306`, `Marduk` `ch=307`, `Citlalinicue` `ch=308`, `Arjuna` `ch=309`): Etapa 1 (flags `1004`, `1006`, `1008`, `1010`, `1012`) al derrotar a cada dios respectivo en el post-game; Etapa 2 (`flag 412` para Three Fates, `flag 386` para los otros 4 dioses) al avanzar en el post-game tardío (異章2).

---

### 2.8. Pregunta 7: Tabla Completa de los 87 Registros de `NPC.pck`

Todos los datos siguientes han sido extraídos directamente de `DungeonTravelers2-2_EN/Data/ENG/NPC/NPC.pck` (`NPCData.bin`) y cruzados con las condiciones de desbloqueo de la guía japonesa (`spoiler.jp`).

* **Columna `W.Rank`**: índice `0x1C` en `WeaponRankData` (`0..11`).
* **Columna `Coste (G)`**: offset `0xAC` (en oro, antes del descuento de *Negotiation*).
* **Columna `Combates`**: offset `0xB0` (combates ganados de contrato; `-1` = infinito).
* **Columna `Flag`**: offset `0xB4` (`unlock_flag`).
* **Columna `Pasivas`**: offset `0x94` (cantidad) y `0x98..` (IDs en `EnemyAttackData`).

| Archivo | NPCID | CharID | Nombre | Etapa | Lv | W.Rank | ATK | DEF | INT | RES | DEX | AGI | Coste (G) | Combates | Flag (`0xB4`) | Pasivas (`0x98+`) | Condición de desbloqueo / Notas |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `0000` | 0 | 300 | **101** | 1 | 32 | 10 | 102 | 88 | 6 | 12 | 32 | 29 | 400 | 10 | 1000 | `[1522]` | Dummy de prueba / Fallback si lista vacía (`0x58b027`) |
| `0001` | 1 | 301 | **102** | 1 | 30 | 5 | 46 | 57 | 54 | 41 | 25 | 27 | 500 | 10 | 1001 | `[]` | Dummy de prueba (inaccesible) |
| `0002` | 2 | 302 | **103** | 1 | 28 | 6 | 87 | 65 | 35 | 32 | 36 | 33 | 100 | 3 | 1002 | `[]` | Dummy de prueba (inaccesible) |
| `0010` | 10 | 411 | **Michelle** | 1 | 30 | 10 | 85 | 83 | 34 | 55 | 42 | 37 | 0 | -1 | 1003 | `[]` | Invitada de historia en Cap. 7 (Templo de Wrappl, opcodes `0x81`/`0x82`) |
| `0015` | 15 | 488 | **Peggy & Beard** | 1 | 35 | 5 | 114 | 96 | 500 | 41 | 52 | 39 | 1000 | 1 | 1106 | `[]` | Temporal: en el bar solo entre la 9.ª charla (Cap. 8) y la 10.ª charla (Cap. 9) |
| `0027` | 27 | 305 | **Three Fates** | 1 | 85 | 7 | 412 | 362 | 258 | 261 | 111 | 78 | 9000 | 20 | 1004 | `[1526, 2648]` | Post-game (異章1): derrotar al jefe Three Fates (フォルトゥナ) |
| `0028` | 28 | 305 | **Three Fates** | 2 | 93 | 6 | 443 | 405 | 333 | 352 | 139 | 87 | 9999 | 20 | 412 | `[1526, 2648]` | Post-game (異章2): progreso en los calabozos finales |
| `0032` | 32 | 306 | **Yoshitsune** | 1 | 98 | 3 | 605 | 412 | 247 | 371 | 182 | 130 | 9999 | 14 | 1006 | `[1527]` | Post-game (異章2): derrotar a Yoshitsune |
| `0033` | 33 | 306 | **Yoshitsune** | 2 | 99 | 2 | 675 | 512 | 272 | 421 | 192 | 150 | 9999 | 16 | 386 | `[1528]` | Post-game (異章2): progreso tras los 8 dioses |
| `0037` | 37 | 307 | **Marduk** | 1 | 97 | 7 | 565 | 2150 | 261 | 408 | 147 | 98 | 9999 | 15 | 1008 | `[1538]` | Post-game (異章2): derrotar a Marduk |
| `0038` | 38 | 307 | **Marduk** | 2 | 99 | 6 | 615 | 2250 | 286 | 458 | 157 | 118 | 9999 | 17 | 386 | `[1538]` | Post-game (異章2): progreso tras los 8 dioses |
| `0042` | 42 | 308 | **Citlalinicue** | 1 | 96 | 9 | 633 | 441 | 272 | 302 | 153 | 109 | 9999 | 16 | 1010 | `[1524]` | Post-game (異章2): derrotar a Citlalinicue |
| `0043` | 43 | 308 | **Citlalinicue** | 2 | 99 | 7 | 703 | 541 | 297 | 352 | 163 | 129 | 9999 | 18 | 386 | `[1525]` | Post-game (異章2): progreso tras los 8 dioses |
| `0047` | 47 | 309 | **Arjuna** | 1 | 95 | 5 | 578 | 421 | 294 | 345 | 168 | 126 | 9999 | 16 | 1012 | `[2683]` | Post-game (異章2): derrotar a Arjuna |
| `0048` | 48 | 309 | **Arjuna** | 2 | 99 | 4 | 648 | 521 | 319 | 395 | 188 | 146 | 9999 | 18 | 386 | `[2683]` | Post-game (異章2): progreso tras los 8 dioses |
| `0052` | 52 | 310 | **Euphemia** | 1 | 26 | 6 | 91 | 58 | 18 | 21 | 44 | 35 | 400 | 25 | 135 | `[1522]` | Cap. 7: apertura de la Taberna |
| `0053` | 53 | 310 | **Euphemia** | 2 | 38 | 5 | 138 | 118 | 27 | 38 | 52 | 43 | 700 | 26 | 319 | `[1522]` | Cap. 9: progreso de historia |
| `0054` | 54 | 310 | **Euphemia** | 3 | 46 | 4 | 163 | 132 | 36 | 51 | 61 | 53 | 1400 | 27 | 353 | `[1522]` | Cap. 11: progreso de historia |
| `0055` | 55 | 310 | **Euphemia** | 4 | 55 | 3 | 186 | 154 | 44 | 60 | 72 | 62 | 2200 | 28 | 230 | `[1523]` | Post-game (異章1): progreso de historia |
| `0056` | 56 | 310 | **Euphemia** | 5 | 67 | 3 | 249 | 173 | 57 | 82 | 88 | 71 | 3000 | 30 | 385 | `[1523]` | Post-game (異章2): progreso de historia |
| `0060` | 60 | 311 | **Tatiana** | 1 | 36 | 8 | 152 | 116 | 28 | 37 | 48 | 33 | 1000 | 23 | 151 | `[]` | Cap. 8: inicio del capítulo |
| `0061` | 61 | 311 | **Tatiana** | 2 | 43 | 7 | 178 | 132 | 35 | 46 | 55 | 39 | 1400 | 24 | 172 | `[]` | Cap. 10: inicio del capítulo |
| `0062` | 62 | 311 | **Tatiana** | 3 | 52 | 7 | 212 | 162 | 49 | 55 | 64 | 44 | 2400 | 25 | 215 | `[]` | Post-game (異章1): inicio |
| `0063` | 63 | 311 | **Tatiana** | 4 | 63 | 6 | 258 | 191 | 63 | 64 | 71 | 53 | 3300 | 26 | 376 | `[]` | Post-game (異章1/2): progreso |
| `0064` | 64 | 311 | **Tatiana** | 5 | 72 | 5 | 302 | 235 | 72 | 75 | 82 | 61 | 4400 | 27 | 407 | `[]` | Post-game (異章2): progreso |
| `0068` | 68 | 312 | **Luzie** | 1 | 45 | 8 | 171 | 166 | 35 | 41 | 50 | 35 | 1700 | 20 | 172 | `[]` | Cap. 10: inicio del capítulo |
| `0069` | 69 | 312 | **Luzie** | 2 | 54 | 11 | 218 | 192 | 44 | 53 | 63 | 44 | 3000 | 22 | 220 | `[]` | Post-game (異章1): progreso |
| `0070` | 70 | 312 | **Luzie** | 3 | 65 | 11 | 264 | 224 | 61 | 72 | 79 | 59 | 3800 | 24 | 384 | `[]` | Post-game (異章2): inicio |
| `0071` | 71 | 312 | **Luzie** | 4 | 78 | 10 | 327 | 294 | 70 | 81 | 92 | 67 | 4800 | 26 | 318 | `[]` | Post-game (異章2): progreso |
| `0072` | 72 | 312 | **Luzie** | 5 | 87 | 9 | 377 | 338 | 82 | 94 | 113 | 82 | 5600 | 28 | 1419 | `[]` | **Quest Rank 19** (`QuestRankData_19.bin`, 840 pts) |
| `0076` | 76 | 313 | **Natalia** | 1 | 28 | 10 | 105 | 48 | 44 | 70 | 24 | 24 | 700 | 18 | 135 | `[]` | Cap. 7: apertura de la Taberna |
| `0077` | 77 | 313 | **Natalia** | 2 | 40 | 6 | 138 | 99 | 63 | 141 | 41 | 37 | 1400 | 20 | 319 | `[]` | Cap. 9: progreso de historia |
| `0078` | 78 | 313 | **Natalia** | 3 | 49 | 6 | 186 | 150 | 77 | 174 | 54 | 46 | 3000 | 22 | 353 | `[]` | Cap. 11: progreso de historia |
| `0079` | 79 | 313 | **Natalia** | 4 | 57 | 5 | 217 | 163 | 102 | 212 | 67 | 55 | 3800 | 24 | 230 | `[]` | Post-game (異章1): progreso de historia |
| `0080` | 80 | 313 | **Natalia** | 5 | 68 | 5 | 269 | 197 | 118 | 255 | 79 | 63 | 4600 | 26 | 402 | `[]` | Post-game (異章2): progreso de historia |
| `0084` | 84 | 314 | **Carol** | 1 | 37 | 7 | 22 | 64 | 81 | 47 | 44 | 38 | 1200 | 18 | 151 | `[]` | Cap. 8: inicio del capítulo |
| `0085` | 85 | 314 | **Carol** | 2 | 44 | 6 | 31 | 73 | 119 | 56 | 53 | 43 | 1900 | 20 | 172 | `[]` | Cap. 10: inicio del capítulo |
| `0086` | 86 | 314 | **Carol** | 3 | 53 | 6 | 42 | 87 | 146 | 64 | 59 | 47 | 3200 | 22 | 215 | `[]` | Post-game (異章1): inicio |
| `0087` | 87 | 314 | **Carol** | 4 | 64 | 5 | 57 | 101 | 201 | 82 | 65 | 54 | 4200 | 24 | 376 | `[]` | Post-game (異章1/2): progreso |
| `0088` | 88 | 314 | **Carol** | 5 | 91 | 4 | 68 | 138 | 276 | 91 | 78 | 70 | 7200 | 26 | 358 | `[]` | Post-game (異章2): derrotar a los Ocho Dioses |
| `0092` | 92 | 315 | **Sasha** | 1 | 47 | 6 | 13 | 84 | 94 | 128 | 61 | 43 | 2300 | 18 | 172 | `[]` | Cap. 10: inicio del capítulo |
| `0093` | 93 | 315 | **Sasha** | 2 | 55 | 6 | 27 | 106 | 113 | 153 | 66 | 51 | 3500 | 20 | 220 | `[]` | Post-game (異章1): progreso |
| `0094` | 94 | 315 | **Sasha** | 3 | 66 | 5 | 53 | 124 | 140 | 181 | 74 | 63 | 4400 | 22 | 384 | `[]` | Post-game (異章2): inicio |
| `0095` | 95 | 315 | **Sasha** | 4 | 79 | 5 | 72 | 155 | 177 | 233 | 85 | 72 | 5300 | 24 | 318 | `[]` | Post-game (異章2): progreso |
| `0096` | 96 | 315 | **Sasha** | 5 | 88 | 4 | 87 | 183 | 213 | 286 | 97 | 88 | 6200 | 26 | 1419 | `[]` | **Quest Rank 19** (`QuestRankData_19.bin`, 840 pts) |
| `0100` | 100 | 316 | **Priscilla** | 1 | 39 | 5 | 94 | 73 | 51 | 59 | 49 | 41 | 1400 | 24 | 320 | `[]` | Cap. 9: progreso de historia |
| `0101` | 101 | 316 | **Priscilla** | 2 | 51 | 5 | 138 | 94 | 72 | 75 | 57 | 48 | 2500 | 25 | 211 | `[]` | Post-game (異章1): inicio |
| `0102` | 102 | 316 | **Priscilla** | 3 | 60 | 4 | 159 | 122 | 88 | 92 | 68 | 57 | 3100 | 26 | 370 | `[]` | Post-game (異章1): progreso |
| `0103` | 103 | 316 | **Priscilla** | 4 | 69 | 3 | 193 | 147 | 107 | 109 | 76 | 66 | 4200 | 27 | 400 | `[]` | Post-game (異章2): progreso |
| `0104` | 104 | 316 | **Priscilla** | 5 | 78 | 2 | 232 | 173 | 139 | 143 | 84 | 75 | 5000 | 28 | 418 | `[]` | Post-game (異章2): progreso |
| `0108` | 108 | 317 | **Neya** | 1 | 50 | 3 | 164 | 134 | 40 | 43 | 77 | 67 | 3000 | 20 | 197 | `[1526]` | Cap. 11: inicio del capítulo |
| `0109` | 109 | 317 | **Neya** | 2 | 57 | 3 | 201 | 148 | 53 | 60 | 84 | 76 | 3800 | 21 | 224 | `[1526]` | Post-game (異章1): progreso |
| `0110` | 110 | 317 | **Neya** | 3 | 69 | 2 | 241 | 167 | 66 | 76 | 116 | 89 | 4900 | 22 | 385 | `[1526]` | Post-game (異章2): inicio |
| `0111` | 111 | 317 | **Neya** | 4 | 80 | 2 | 298 | 202 | 75 | 84 | 138 | 106 | 5500 | 23 | 318 | `[1526]` | Post-game (異章2): progreso |
| `0112` | 112 | 317 | **Neya** | 5 | 89 | 1 | 351 | 231 | 87 | 106 | 153 | 121 | 7000 | 24 | 334 | `[1527]` | Post-game (異章2): progreso avanzado |
| `0116` | 116 | 318 | **Estelle** | 1 | 30 | 11 | 68 | 54 | 28 | 31 | 35 | 26 | 500 | 20 | 135 | `[]` | Cap. 7: apertura de la Taberna |
| `0117` | 117 | 318 | **Estelle** | 2 | 41 | 7 | 89 | 85 | 53 | 49 | 48 | 37 | 1100 | 20 | 319 | `[]` | Cap. 9: progreso de historia |
| `0118` | 118 | 318 | **Estelle** | 3 | 50 | 7 | 106 | 112 | 61 | 67 | 63 | 50 | 2400 | 22 | 353 | `[]` | Cap. 11: progreso de historia |
| `0119` | 119 | 318 | **Estelle** | 4 | 58 | 6 | 133 | 134 | 76 | 83 | 75 | 56 | 3500 | 22 | 230 | `[]` | Post-game (異章1): progreso de historia |
| `0120` | 120 | 318 | **Estelle** | 5 | 70 | 5 | 168 | 155 | 88 | 94 | 82 | 64 | 4700 | 25 | 402 | `[]` | Post-game (異章2): progreso de historia |
| `0124` | 124 | 319 | **Rebecca** | 1 | 43 | 4 | 161 | 117 | 36 | 41 | 72 | 56 | 2100 | 22 | 320 | `[]` | Cap. 9: progreso de historia |
| `0125` | 125 | 319 | **Rebecca** | 2 | 53 | 3 | 195 | 150 | 61 | 63 | 89 | 69 | 2800 | 23 | 211 | `[]` | Post-game (異章1): inicio |
| `0126` | 126 | 319 | **Rebecca** | 3 | 62 | 3 | 220 | 189 | 71 | 77 | 112 | 80 | 3800 | 24 | 370 | `[]` | Post-game (異章1): progreso |
| `0127` | 127 | 319 | **Rebecca** | 4 | 71 | 2 | 281 | 216 | 85 | 99 | 131 | 94 | 4700 | 25 | 400 | `[]` | Post-game (異章2): progreso |
| `0128` | 128 | 319 | **Rebecca** | 5 | 82 | 2 | 354 | 244 | 99 | 109 | 153 | 107 | 5600 | 26 | 1419 | `[]` | **Quest Rank 19** (`QuestRankData_19.bin`, 840 pts) |
| `0132` | 132 | 320 | **Chloe** | 1 | 30 | 9 | 112 | 64 | 22 | 27 | 47 | 33 | 500 | 20 | 135 | `[]` | Cap. 7: apertura de la Taberna |
| `0133` | 133 | 320 | **Chloe** | 2 | 42 | 8 | 157 | 91 | 33 | 34 | 64 | 48 | 900 | 21 | 319 | `[]` | Cap. 9: progreso de historia |
| `0134` | 134 | 320 | **Chloe** | 3 | 52 | 7 | 199 | 108 | 45 | 47 | 73 | 60 | 2600 | 22 | 353 | `[2680]` | Cap. 11: progreso de historia |
| `0135` | 135 | 320 | **Chloe** | 4 | 59 | 6 | 236 | 131 | 52 | 55 | 92 | 71 | 3700 | 23 | 230 | `[2681]` | Post-game (異章1): progreso de historia |
| `0136` | 136 | 320 | **Chloe** | 5 | 68 | 6 | 283 | 155 | 61 | 70 | 123 | 79 | 4500 | 25 | 385 | `[2681, 1538]` | Post-game (異章2): progreso de historia |
| `0140` | 140 | 321 | **Marion** | 1 | 48 | 4 | 143 | 120 | 61 | 72 | 55 | 38 | 2280 | 22 | 197 | `[]` | Cap. 11: inicio del capítulo |
| `0141` | 141 | 321 | **Marion** | 2 | 56 | 4 | 168 | 142 | 72 | 86 | 69 | 45 | 3480 | 23 | 220 | `[]` | Post-game (異章1): progreso |
| `0142` | 142 | 321 | **Marion** | 3 | 67 | 3 | 201 | 171 | 98 | 116 | 83 | 60 | 4280 | 24 | 384 | `[]` | Post-game (異章2): inicio |
| `0143` | 143 | 321 | **Marion** | 4 | 73 | 3 | 242 | 194 | 128 | 131 | 91 | 72 | 5680 | 25 | 407 | `[]` | Post-game (異章2): progreso |
| `0144` | 144 | 321 | **Marion** | 5 | 86 | 2 | 294 | 229 | 167 | 174 | 115 | 85 | 6780 | 26 | 1419 | `[1523]` | **Quest Rank 19** (`QuestRankData_19.bin`, 840 pts) |
| `0148` | 148 | 322 | **Riesco** | 1 | 49 | 7 | 209 | 172 | 88 | 125 | 49 | 51 | 1900 | 21 | 197 | `[]` | Cap. 11: inicio del capítulo |
| `0149` | 149 | 322 | **Riesco** | 2 | 55 | 6 | 232 | 194 | 101 | 145 | 57 | 57 | 2700 | 23 | 220 | `[]` | Post-game (異章1): progreso |
| `0150` | 150 | 322 | **Riesco** | 3 | 65 | 5 | 265 | 214 | 152 | 172 | 73 | 69 | 4000 | 25 | 381 | `[]` | Post-game (異章2): progreso |
| `0153` | 153 | 323 | **Paracas** | 1 | 42 | 6 | 129 | 105 | 84 | 62 | 55 | 54 | 2300 | 22 | 172 | `[]` | Cap. 10: inicio del capítulo |
| `0154` | 154 | 323 | **Paracas** | 2 | 53 | 5 | 161 | 124 | 117 | 75 | 61 | 62 | 3400 | 23 | 215 | `[1561]` | Post-game (異章1): inicio |
| `0155` | 155 | 323 | **Paracas** | 3 | 62 | 4 | 192 | 153 | 130 | 82 | 67 | 67 | 4200 | 24 | 376 | `[1561]` | Post-game (異章1/2): progreso |
| `0158` | 158 | 324 | **Medved** | 1 | 33 | 9 | 137 | 102 | 3 | 21 | 39 | 22 | 800 | 22 | 136 | `[]` | Cap. 7: tras completar el evento de historia del capítulo |
| `0159` | 159 | 324 | **Medved** | 2 | 48 | 7 | 177 | 131 | 9 | 36 | 55 | 43 | 1600 | 24 | 204 | `[]` | Cap. 10/11: progreso de historia |
| `0160` | 160 | 324 | **Medved** | 3 | 59 | 4 | 231 | 144 | 10 | 42 | 61 | 51 | 2600 | 26 | 224 | `[]` | Post-game (異章1): progreso |
| `0163` | 163 | 325 | **Mekelle** | 1 | 46 | 3 | 151 | 95 | 46 | 57 | 68 | 57 | 2000 | 21 | 172 | `[]` | Cap. 10: inicio del capítulo |
| `0164` | 164 | 325 | **Mekelle** | 2 | 54 | 3 | 183 | 135 | 61 | 73 | 91 | 69 | 3200 | 23 | 215 | `[1523]` | Post-game (異章1): inicio |
| `0165` | 165 | 325 | **Mekelle** | 3 | 63 | 2 | 217 | 157 | 77 | 85 | 108 | 83 | 4200 | 25 | 376 | `[1523]` | Post-game (異章1/2): progreso |
| `0168` | 168 | 326 | **Momona** | 1 | 32 | 6 | 26 | 54 | 31 | 53 | 41 | 30 | 600 | 20 | 136 | `[]` | Cap. 7: tras completar el evento de historia del capítulo |
| `0169` | 169 | 326 | **Momona** | 2 | 46 | 5 | 66 | 87 | 54 | 82 | 57 | 39 | 1200 | 22 | 204 | `[]` | Cap. 10/11: progreso de historia |
| `0170` | 170 | 326 | **Momona** | 3 | 58 | 4 | 80 | 94 | 67 | 104 | 72 | 45 | 2700 | 24 | 224 | `[]` | Post-game (異章1): progreso |
| `0173` | 173 | 327 | **Azmaria** | 1 | 50 | 5 | 201 | 142 | 1 | 87 | 63 | 55 | 4000 | 20 | 1089 | `[1523]` | Evento secundario: derrotar a Azmaria |
| `0174` | 174 | 327 | **Azmaria** | 2 | 62 | 4 | 262 | 178 | 1 | 96 | 81 | 66 | 5000 | 20 | 263 | `[1523]` | Post-game (異章1): progreso |
| `0175` | 175 | 327 | **Azmaria** | 3 | 72 | 4 | 324 | 197 | 1 | 125 | 97 | 78 | 6000 | 20 | 384 | `[1523]` | Post-game (異章2): inicio |
| `0176` | 176 | 327 | **Azmaria** | 4 | 84 | 3 | 397 | 212 | 1 | 143 | 112 | 85 | 7000 | 20 | 374 | `[1524]` | Post-game (異章2): progreso |
| `0177` | 177 | 327 | **Azmaria** | 5 | 93 | 2 | 478 | 251 | 1 | 166 | 138 | 96 | 8000 | 20 | 359 | `[1524, 1526]` | Post-game (異章2): derrotar a los Ocho Dioses |
| `0180` | 180 | 328 | **Miranda** | 1 | 53 | 7 | 204 | 117 | 40 | 61 | 68 | 49 | 3700 | 24 | 1094 | `[1538, 2682]` | Evento secundario en mazmorra (Templo de Wrappl / historia) |
| `0181` | 181 | 328 | **Miranda** | 2 | 64 | 6 | 243 | 146 | 61 | 77 | 92 | 57 | 4300 | 24 | 284 | `[1538, 2682]` | Post-game (異章1): progreso |
| `0182` | 182 | 328 | **Miranda** | 3 | 70 | 6 | 278 | 165 | 72 | 92 | 113 | 76 | 5200 | 24 | 381 | `[1538, 2682]` | Post-game (異章2): inicio |
| `0183` | 183 | 328 | **Miranda** | 4 | 80 | 5 | 351 | 189 | 91 | 104 | 124 | 82 | 6300 | 24 | 400 | `[1538, 2682]` | Post-game (異章2): progreso |
| `0184` | 184 | 328 | **Miranda** | 5 | 90 | 4 | 422 | 212 | 103 | 129 | 148 | 93 | 7400 | 24 | 1419 | `[1538, 2682]` | **Quest Rank 19** (`QuestRankData_19.bin`, 840 pts) |
| `0187` | 187 | 329 | **Euthys** | 1 | 74 | 5 | 359 | 318 | 238 | 226 | 116 | 87 | 4000 | 5 | 928 | `[1527]` | Post-game (異章1): derrotar a Kakinuhito (Santuario de Serul) |
| `0188` | 188 | 329 | **Euthys** | 2 | 82 | 4 | 427 | 341 | 267 | 248 | 138 | 96 | 4500 | 5 | 250 | `[1527]` | Post-game (異章1): progreso |
| `0189` | 189 | 329 | **Euthys** | 3 | 88 | 3 | 495 | 402 | 314 | 302 | 155 | 112 | 5000 | 5 | 374 | `[1527]` | Post-game (異章2): inicio |
| `0190` | 190 | 329 | **Euthys** | 4 | 95 | 3 | 576 | 449 | 362 | 358 | 179 | 125 | 6000 | 5 | 412 | `[1527]` | Post-game (異章2): progreso |
| `0191` | 191 | 329 | **Euthys** | 5 | 99 | 2 | 631 | 483 | 401 | 402 | 197 | 138 | 9000 | 10 | 365 | `[1527]` | Post-game (異章2): derrotar a los Ocho Dioses |
| `0194` | 194 | 330 | **Lolo** | 1 | 86 | 1 | 345 | 113 | 172 | 192 | 155 | 122 | 7777 | 16 | 1104 | `[]` | Post-game (異章1): derrotar a Octopunch (Casino Esperanto) |
| `0195` | 195 | 330 | **Lolo** | 2 | 93 | 0 | 432 | 138 | 236 | 221 | 176 | 138 | 7777 | 18 | 388 | `[]` | Post-game (異章2): progreso |

*(Nota sobre DLC: Los 9 mercenarios DLC — **Marie, Setsuna, Kazusa, Nekone, Anju, Kleito, Tarte, Hatsune y Chizuru** — tienen 5 etapas cada uno que escalan con el progreso de capítulos desde Lv30 hasta Lv75..88, coste `500G` en todas sus etapas y `25` combates de duración, pero no están incluidos en el `NPC.pck` base de la versión PC inglesa).*

---

## 3. Evidencia de Internet (Citas Textuales y URLs)

1. **Wiki japonesa de estrategia (`spoiler.jp`) — Reglas generales de 傭兵バディ (Mercenary Buddy)**:
   * **URL**: https://www.spoiler.jp/game/dt2-2/index.php?%E5%82%AD%E5%85%B5%E3%83%90%E3%83%87%E3%82%A3
   * **Cita textual**:
     > 「7章中盤から利用可能になる『酒場』にて、お金を払うことで傭兵を雇う事ができる。」
     > 「同時に雇えるのは一人だけで、雇った時点から規定の戦闘回数をこなすまでパーティに同行する。」
     > 「逃走時には戦闘回数は消費しない。ボス戦では契約期間満了による自動離脱は発生しない。」
     > 「戦闘中は敵味方問わずターゲットにならず（全体回復・補助は有効）、独立して行動する。」
     > 「物語の進行度合いによって傭兵はレベルアップし、習得スキルやステータスが上昇していく（雇用金額も上がる）。」
     *(Traducción: "En la 'Taberna', disponible desde mediados del Capítulo 7, puedes contratar a un mercenario pagando dinero. Solo se puede contratar a uno a la vez, y acompaña al grupo desde el momento de su contratación hasta completar el número estipulado de combates. Al huir no se consumen combates. En las batallas contra jefes no se produce el abandono automático por fin de contrato. Durante el combate no puede ser elegido como objetivo ni por aliados ni por enemigos (las curaciones y buffs globales sí le afectan) y actúa de forma independiente. Según el grado de progreso de la historia, el mercenario sube de nivel y aumentan sus habilidades y estadísticas (también sube su coste de contratación)").*

2. **Wiki japonesa (`spoiler.jp`) — Mercenarios especiales (`ミシェル` / Michelle y `ペギー＆ビアード` / Peggy & Beard)**:
   * **URL**: https://www.spoiler.jp/game/dt2-2/index.php?%E5%82%AD%E5%85%B5%E3%83%90%E3%83%87%E3%82%A3/%E7%89%B9%E6%AE%8A01
   * **Cita textual**:
     > 「ミシェル：7章のラップル神殿攻略中に一時的に同行する。酒場での雇用は不可。」
     > 「ペギー＆ビアード：8章中盤（9回目の会話イベント発生後）～9章中盤（10回目の会話イベント発生前）までの期間限定で雇用可能。契約戦闘回数は1回のみ。」
     *(Traducción: "Michelle: acompaña temporalmente durante la exploración del Templo de Wrappl en el Cap. 7. No se puede contratar en la taberna. Peggy & Beard: contratable por tiempo limitado desde mediados del Cap. 8 (tras el 9.º evento de charla) hasta mediados del Cap. 9 (antes del 10.º evento de charla). Su contrato dura solo 1 combate").*

3. **Wiki japonesa (`spoiler.jp`) — Subpáginas de etapas y condiciones de desbloqueo (`その01` a `その06`, `特殊02`, `特殊03`)**:
   * **URLs**:
     * https://www.spoiler.jp/game/dt2-2/index.php?%E5%82%AD%E5%85%B5%E3%83%90%E3%83%87%E3%82%A3/%E3%81%9D%E3%81%AE01 (Euphemia, Tatiana, Luzie, Natalia)
     * https://www.spoiler.jp/game/dt2-2/index.php?%E5%82%AD%E5%85%B5%E3%83%90%E3%83%87%E3%82%A3/%E3%81%9D%E3%81%AE02 (Carol, Sasha, Priscilla, Neya)
     * https://www.spoiler.jp/game/dt2-2/index.php?%E5%82%AD%E5%85%B5%E3%83%90%E3%83%87%E3%82%A3/%E3%81%9D%E3%81%AE03 (Estelle, Rebecca, Chloe, Marion)
     * https://www.spoiler.jp/game/dt2-2/index.php?%E5%82%AD%E5%85%B5%E3%83%90%E3%83%87%E3%82%A3/%E3%81%9D%E3%81%AE04 (Riesco, Paracas, Medved, Mekelle)
     * https://www.spoiler.jp/game/dt2-2/index.php?%E5%82%AD%E5%85%B5%E3%83%90%E3%83%87%E3%82%A3/%E3%81%9D%E3%81%AE05 (Momona, Azmaria, Miranda)
     * https://www.spoiler.jp/game/dt2-2/index.php?%E5%82%AD%E5%85%B5%E3%83%90%E3%83%87%E3%82%A3/%E3%81%9D%E3%81%AE06 (Euthys, Lolo)
     * https://www.spoiler.jp/game/dt2-2/index.php?%E5%82%AD%E5%85%B5%E3%83%90%E3%83%87%E3%82%A3/%E7%89%B9%E6%AE%8A02 (Three Fates, Yoshitsune, Marduk, Citlalinicue, Arjuna)
   * **Cita textual (ejemplo de Euthys / Lolo / Carol)**:
     > 「キャロル Lv91：八大神撃破後」「エウティス：セルル地下聖堂のカキヌヒト撃破後（Lv74）…八大神撃破後（Lv99）」「ロロ：エスペラントカジノのオクトパンチ撃破後（Lv86）」

4. **Siliconera — Presentación oficial del sistema "Mercenary Buddy" (enero 2017)**:
   * **URL**: https://www.siliconera.com/dungeon-travelers-2-2-gets-new-gameplay-footage-new-mercenary-buddy-system/
   * **Cita textual**:
     > *"With the 'Mercenary Buddy' system, you can go to the tavern and pay gold to hire various mercenaries to help out as a guest character in battle. They'll take action independently during battle, and can also level up by progressing through the story."*

---

## 4. Contradicciones o Dudas que Quedan y Prueba Mínima en el Juego

No queda ninguna contradicción entre el código desensamblado y las guías sobre las mecánicas del sistema (ambos coinciden al 100%). Las únicas dos dudas menores sobre datos de mapeo y cómo resolverlas son:

1. **Correspondencia exacta entre los flags de progreso del post-game (`230`, `370`, `374`, `376`, `381`, `384`, `385`, `400`, `402`, `407`, `412`, `318`, `334`) y cada piso/jefe concreto de 異章1 y 異章2 (`Checkpoints` del simulador)**:
   * *Por qué ocurre:* Esos flags (< 1000) los activan los scripts de eventos de mazmorra (`.adv.bin` en `Data/ENG/Script/`). Aunque sabemos a qué capítulo/tramo pertenecen y el nivel exacto de la etapa (`Lv51..Lv95`), mapear cada flag al nombre exacto del `cid` (checkpoint) en `Scenario.cs` requeriría cruzar los scripts de cada mapa de post-game o mirar en una partida guardada qué etapa vende el bar antes de cada jefe.
   * *Prueba mínima en el juego (o por script):* Cargar un save al inicio de 異章1 y otro en 異章2 y anotar los niveles mostrados en la Taberna, o bien buscar los enteros `230, 370, 376, 384, 385, 400, 402` en los `.adv.bin` de `Data/ENG/Script/`.
2. **Interacción de los buffs/curas de área aliados con la unidad `3001` (Mercenario)**:
   * *Estado:* La wiki japonesa indica que los buffs/curas globales afectan al mercenario, pero como el mercenario no tiene HP ni TP (`0x4fec90`), solo los buffs de estadísticas (`ATK..AGI` / velocidad) a toda la party tienen efecto real sobre sus acciones.

---

## 5. Qué Cambiar en el Modelo (`tools/npc_data.py`, `Units.cs`, `Jobs.cs`, `Scenario.cs`, `Battle.cs`)

Para que el simulador modele los mercenarios exactamente igual que el juego, se deben realizar los siguientes cambios concretos:

### 5.1. `data_tables/record_layouts.json` y `tools/npc_data.py`
1. **Renombrar `hp` (`0xAC`) a `cost` (o `hire_cost`)** y documentar que **los mercenarios no tienen HP** (son inmortales e intargetables).
2. **Añadir `contract_battles` (`0xB0`) y `unlock_flag` (`0xB4`)** al layout de `NPCData`.
3. **Leer todas las pasivas (`0x94` y `0x98..0xAB`)**:
   * Reemplazar `'kind': i(0x94)` y `'extra_attack': i(0x98)` por:
     ```python
     passive_count = max(0, min(i(0x94), 5))
     passives = [i(0x98 + 4 * k) for k in range(passive_count) if i(0x98 + 4 * k) != -1]
     ```
   * Esto corrige la pérdida de la segunda pasiva en **Three Fates** (`[1526, 2648]`), **Chloe Lv68** (`[2681, 1538]`), **Azmaria Lv93** (`[1524, 1526]`) y **Miranda** (`[1538, 2682]`).

### 5.2. `engine_cs/src/DtEngine/Units.cs` (`GuestRec`, `GuestStage`, `BuildGuest`)
1. **Soportar múltiples pasivas en `GuestRec` y `BuildGuest`**:
   * Cambiar `public int Passive = T.NONE;` en `GuestRec` por `public int[] Passives = Array.Empty<int>();` (o aplicar en `BuildGuest` el bucle sobre todas las pasivas de `stage.Passives`, igual que hace `0x4ff2bb`–`0x4ff446`).
2. **Ignorar `stage.Hp` (que en realidad era el coste en oro `0xAC`)**:
   * En `BuildGuest`, fijar un HP simbólico (`1`) ya que `Kind.Npc` nunca recibe daño ni puede ser objetivo (`Battle.cs` ya excluye `Kind.Npc` e `Kind.Summon` de `Targetable`).
3. **Corregir `UnitFactory.GuestStage` (`Units.cs` líneas 561–579)**:
   * **Cómo funciona hoy (`GuestStage`)**: Elige la etapa con mayor `stage.Level <= partyLevel`. Como varias etapas de mercenarios tienen un `level` ligeramente superior al nivel medio de la party en el capítulo en que se desbloquean (por ejemplo, Carol Lv91 tras los Ocho Dioses, Euthys Lv74 en 異章1, Lolo Lv86 tras Octopunch, o los 5 dioses Lv95–98), `stage.Level <= partyLevel` selecciona una etapa inferior a la que realmente ofrece la Taberna o ni siquiera encuentra la etapa correcta.
   * **Cómo debe funcionar**:
     * Permitir pasar el `npc_id` exacto o el índice de etapa (`stageIndex` / `unlock_flag`), o bien seleccionar la etapa desbloqueada según el **checkpoint/capítulo** del escenario (mapeando los flags de capítulo `135, 136, 151, 319, 320, 172, 197, 353, 211..230, 370..418, 1419` al progreso del checkpoint en lugar de `stage.Level <= partyLevel`).
     * Excluir de los mercenarios contratables los registros `id = 0, 1, 2` (`"101"`, `"102"`, `"103"`, dummies de desarrollo).

### 5.3. `engine_cs/src/DtEngine/Jobs.cs` y `Scenario.cs` (Coexistencia de Summon + Mercenario)
1. **Permitir que Summon (`Kind.Summon`, unidad `3000`) y Mercenario (`Kind.Npc`, unidad `3001`) coexistan en la misma batalla**:
   * **Cómo funciona hoy (`Scenario.cs` línea 256)**:
     ```csharp
     var companion = !string.IsNullOrEmpty(guest)
         ? UnitFactory.BuildGuest(Data, guest, level)
         : sealbook != null ? UnitFactory.BuildSummon(Data, sealbook, members) : null;
     ```
     El operador ternario en `Scenario.cs` impide que haya invocación del gran sello cuando se especifica `guest`, asumiendo erróneamente la hipótesis (a).
   * **Cómo debe funcionar**:
     Construir **ambos** de forma independiente si ambos están presentes (`summonUnit = sealbook != null ? UnitFactory.BuildSummon(...) : null;` y `guestUnit = !string.IsNullOrEmpty(guest) ? UnitFactory.BuildGuest(...) : null;`) y pasar ambos a `Battle` (en el juego van en ese orden: primero `3000` Summon en `0x449771` y luego `3001` Mercenario en `0x449839`).

### 5.4. `engine_cs/src/DtEngine/Battle.cs` (IA del Mercenario y Muñecas de Marion)
1. **Separar o permitir múltiples acompañantes en `Battle` (`Summon` + `Npc`)**:
   * En `Battle.cs`, si el motor guarda un único campo `Summon` para la unidad acompañante, separarlo en `Summon` (unidad `3000`, `Kind.Summon`) y `Guest` / `Npc` (unidad `3001`, `Kind.Npc`), o mantener una lista de acompañantes inmortales para que ambos reciban turnos en la cola de velocidad.
2. **Evaluar `NPCAIData.bin` (`unit.Script`) en `StepNpc` en lugar de elección aleatoria uniforme**:
   * **Cómo funciona hoy (`Battle.cs` `StepNpc`)**: Elige `Rng.Choice(unit.Attacks)` de forma uniforme, ignorando `unit.Script` (`NPCAIData.bin`, que ya es decodificado por `tools/npc_data.py` usando `enemy_ai.decode`).
   * **Cómo debe funcionar**: Usar el mismo evaluador de máquina de estados (`unit.Script`, con sus pesos `sets[state]` y condiciones pre/post acción) que usa `StepEnemy` / `StepSummon` (`0x430f10` es literalmente la misma función en el ejecutable para enemigos, summons y mercenarios).
3. **Permitir que las habilidades de creación de muñecas (*Dolls*) funcionen cuando las lanza un `Kind.Npc` (Marion)**:
   * Verificar que cuando Marion (`ch=321`) ejecuta sus habilidades de invocación de muñecas (`718/719` Spartan, `725/726` Oracles, `734/735` Catalina, `2661..2663` Mercidarian, `2530..2532` Musiy), las muñecas se añadan a la fila de muñecas aliadas (`2000..2999`) heredando las estadísticas de Marion.
