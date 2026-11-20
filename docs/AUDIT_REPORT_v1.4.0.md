# Auditoría Integral — Dungeon Travelers 2-2: QoL & Balance Mod (`v1.4.0`, `2f3f042`)

Fecha de auditoría: `2026-11-20`

---

## 1. Resumen ejecutivo

El repositorio presenta una **tubería de construcción, verificación de datos binarios y empaquetado muy sólida**: los 214 tests de Python, los 23 tests de C#, la comprobación de conformidad (`107 items: MATCH 64, FIXED 40, MODEL-LIMIT 3, N/A 0; 0 failing`), la compilación de `qol` y `balance`, el empaquetado de `dist/` y la regeneración de `docs/guide/` pasan con código de salida `0` y sin diferencias semánticas en archivos rastreados (`git diff --stat` vacío). Las 3.586 filas activas de `data_tables/balance_changes.xlsx` están en estado `built` (`0` bloqueadas/pendientes) y coinciden byte a byte con los `.pck` construidos y con `gamedata/variant.py`, y los `.zip` previos de `dist/` (`2026-11-15`) eran idénticos en SHA-256 contenido a contenido a los regenerados (`2026-11-20`).

Sin embargo, la auditoría profunda detectó **4 hallazgos críticos en `engine_cs/src/DtEngine/`** (todos re-evaluados y confirmados al 100% contra desensamblado directo de `DT22_en_unwrapped.exe`) junto con hallazgos altos/medios en `Policy.cs`, el instalador/empaquetado, los tutoriales de Balance (`Teaching.pck`), el estado del balance y la documentación.

### Resultados exactos de la batería de comandos (Sección 1)

| Comando | Resultado | Detalle exacto |
|---|---|---|
| `python -m unittest discover -s tests -p "test_*.py" -v` | **OK (`exit 0`)** | `Ran 214 tests in 44.436s`, `0` fallos, `0` omitidos. |
| `dotnet test -c Release engine_cs/tests/DtEngine.Tests` | **OK (`exit 0`)** | `Passed: 23, Failed: 0, Skipped: 0, Total: 23` (`Duration: 3 s`). |
| `python tools/engine_conformity.py --check` | **OK (`exit 0`)** | `107 items: MATCH 64, FIXED 40, MODEL-LIMIT 3, N/A 0; 0 failing`. |
| `python tools/build_variant.py qol --no-install` | **OK (`exit 0`)** | 12 PCKs en `Parameter/` + `Teaching.pck` (1 corrección en `ScriptFixes`); `270` skills modificadas, `2779` textos verificados sin palabras fuera de universo; `1` nota manual no ligada a tabla (`Star Dust Arrow: 1-3 hits`). |
| `python tools/build_variant.py balance --no-install` | **OK (`exit 0`)** | `3586` filas vivas (`3674` campos en `16` de `39` packs, `6210` bytes distintos de original); readback idéntico al simulador; `74` cajas de `Lesson.pck`/`Teaching.pck` reescritas (`10` con voz), `9` mantenidas; `2` notas manuales (`Star Dust Arrow`, `Heal`). |
| `python tools/package_all.py` | **OK (`exit 0`)** | `DT22_qol_2026-11-20.zip` (`89,694 bytes`, 13 archivos) y `DT22_balance_2026-11-20.zip` (`118,182 bytes`, 22 archivos). Todos los archivos internos coinciden en SHA-256 con los `.zip` previos del `2026-11-15`. |
| `python tools/build_guide.py` | **OK (`exit 0`)** | Regenera 12 archivos en `docs/guide/`. `git diff --stat` y `git diff -w --stat` resultan **vacíos** (solo aviso de Git por CRLF -> LF en Windows al escribir sin `newline='\n'`). |
| `python tools/exe_patch.py status` | **OK (`exit 0`)** | `X01`–`X17` todos `patched` en `DT22_en.exe` y `DT22_en_unwrapped.exe`. |
| `python tools/floor_patch.py status` | **OK (`exit 0`)** | `166 rows; 21 packs`: `st00`–`st15` y `st20`–`st23` en estado `variant`; `st99` en `game` (esperado: `zones` no tiene filas para `st99`). |

---

## 2. Hallazgos ordenados por severidad

### Crítico (todos re-evaluados, confirmados contra `DT22_en_unwrapped.exe` y **CORREGIDOS**)

> **Estado tras corrección (`2026-11-20`):** C1, C2, C3 y C4 fueron re-evaluados contra el desensamblado real de `DT22_en_unwrapped.exe`, corregidos en `engine_cs/src/DtEngine/` (`Battle.cs`, `Units.cs`, `Ai.cs`, `Data.cs`, `Loader.cs`, `Policy.cs`), `gamedata/variant.py` y `tools/engine_export.py`, re-exportado `build/engine_snapshot.json`, y verificados con 4 pruebas unitarias nuevas en `engine_cs/tests/DtEngine.Tests/CriticalFixesTests.cs` (`27/27` tests C# OK, `214/214` tests Python OK, `107/107` `engine_conformity.py --check` OK). Queda pendiente re-ejecutar `python tools/full_suite.py` para regenerar los reportes y gráficas de balance bajo el motor corregido.

#### C1. La velocidad post-casteo de los hechizos de jugador se eleva al cuadrado (`action.Speed^2`)
- **Ubicación:** `engine_cs/src/DtEngine/Battle.cs` L368–L381.
- **Re-evaluación binaria (`0x449bf1`–`0x449ea3`):** Confirmado 100% real. `[esp+0x18]` (`F1`) se inicializa a `1.0` (`0x449c10`); los hechizos no existen en `TechniqueSkillData` (`0x738a64`) ni en `JoinSkillData` (`0x738a54`), por lo que `F1` **permanece en `1.0`**. Luego `0x449dbe`–`0x449df6` encuentra el hechizo en `MagicSkillData` (`0x738a58`) y escribe `[vtable+0x154]` en `F2` (`[esp+0x10]`), de modo que `F1 * F2 = 1.0 * action.Speed`. En `Battle.cs:370-371` se escribía `f1 = action.Speed + unique352` y `if (action.Skill.IsMagic) f2 = f1;`, produciendo `(action.Speed + unique352)^2`.
- **Impacto:** Afecta a **92 de 98 hechizos de jugador** (inflando `Fireball 2.25 -> 5.0625`, `Fire Blast 1.7 -> 2.89`, `Inferno 1.3 -> 1.69`; castigando `Terrorize 0.4 -> 0.16`, `Shadow Clone 0.85 -> 0.7225`) y distorsiona también `Policy.TimeOf` (que delega en `Battle.Wait`).
- **Corrección:** Para hechizos post-cast, asignar `f2 = f1; f1 = 1.0;` (producto `action.Speed + unique352`).

#### C2. Los parches ejecutables `X16` (Third Eye Wide dispel) y `X17` (Positive Trance Pep > 85) están hardcodeados activos también en vanilla
- **Ubicación:** `engine_cs/src/DtEngine/Battle.cs` L532 (`X16`), L1525–L1526 y L1619–L1620 (`X17`); `gamedata/variant.py` L234–L260; `tools/engine_export.py` L294–L329; `engine_cs/src/DtEngine/Data.cs` L315–L316; `engine_cs/src/DtEngine/Loader.cs` L293–L296.
- **Re-evaluación binaria (`0x47ee73`, `0x44ccd2`):** Confirmado 100% real. A diferencia de `X13` (`ArcaneChance`) y `X14` (`InterruptProduct`), ni `X16` ni `X17` viajaban parametrizados por lado en `build/engine_snapshot.json`, por lo que `vanilla` corría ambos parches de Balance (agravado por `Pep = 100.0` fijo en `Units.cs:98`, regalando a Alisia vanilla un bono inexistente). Además `gamedata/variant.py:259` buscaba `X13` solo por `lever == 'L38'`, que ahora comparten `X13`, `X16` y `X17`.
- **Corrección:** Parametrizar `third_eye_dispel` (`false` vanilla / `true` variant) y `positive_trance_threshold` (`100` vanilla / `85` variant) de extremo a extremo y buscar `X13`/`X16`/`X17` por `id`.

#### C3. Las invocaciones de muñecas enemigas son 100% no-op y rompen el comando `6` de `Ai.cs` y `Usurper of Souls`
- **Ubicación:** `engine_cs/src/DtEngine/Battle.cs` L2602–L2612; `engine_cs/src/DtEngine/Ai.cs` L176–L191.
- **Re-evaluación binaria (`0x4852ca`–`0x485c17`, `0x4fd3d0`, `0x432028`–`0x432156`):** Confirmado 100% real. `Command::CCommand_0146::AddTask` despacha los 30 ataques de invocación de `EnemyAttackData` (`690–735`, `1789–1791`) a través de una tabla exacta `attackId -> [actionAttackIds]` (`CGameEnemyStatusETCDoll`, `0x4fd3d0`) usando las stats del dueño y las acciones en `EnemyAttackData`. Además, el comando de IA `6` (`0x432028`–`0x432156`) comprueba explícitamente si el ataque tiene efecto `146` (`0x92`) y recorre las muñecas vivas comprobando `owner == self && summonAttackId == attackId`. En `DtEngine`, `MakeDoll` devolvía vacío para enemigos (71 enemigos/jefes afectados) y `Ai.cs` comando `6` nunca veía muñecas (120 comandos de script afectados).
- **Corrección:** Soportar los 30 ataques de invocación en `MakeDoll` usando la tabla exacta del binario, almacenar `SummonAttackId` y `Attacks` en la muñeca, ejecutarlos en `DollAction` vía `AKind.Enemy` y añadir la comprobación de muñecas vivas en `Ai.cs` comando `6`.

#### C4. `BuildDoll` descarta equipo/modificadores de clase del dueño; `MakeGuestDoll` mapea IDs erróneos, rompe `Double Puppet` de Paracas e ignora scripts
- **Ubicación:** `engine_cs/src/DtEngine/Units.cs` L659–L686; `engine_cs/src/DtEngine/Battle.cs` L2646–L2702 y L2724–L2757.
- **Re-evaluación binaria (`0x4f3290`, `0x4f3456`–`0x4f347d`, `0x4f7c00`, `0x4fe5f0`, `0x48490a`–`0x4852c0`, `0x43c83c`–`0x43c960`, `0x4fd630`):** Confirmado 100% real (con un hallazgo adicional en `+0xf4`!).
  1. En `PlayerDoll` (`0x4fd840` -> `0x4f3290` -> `0x4f7c00`), el `.exe` clona los 6 slots de equipo (`0x4f3456`–`0x4f347d`), pone a `0` `resetBonus` (`0x120`), `subEvent` (`0xdc`) y `sealbook` (`0xcc`), no copia pasivas (`0xc0` solo guarda la skill de acción), y recalcula con `0x4f5d60` (crecimiento base sin Crown) + `0x4f7c70` (modificadores de clase sin Yearning) + `0x4f6530` (stats de equipo sin Mastery ni Dual Wield) + `0x4f8270` (enchants de las 6 piezas) + `Soul Seal` (`314`). `Units.cs:662-668` solo copiaba `grown`, descartando todo el equipo y modificadores de clase.
  2. En `MakeGuestDoll` (`Battle.cs:2661-2668`), el switch confundió IDs de `EnemyAttackData` (`0x133..0x137` = `307, 308, 310, 311`) con IDs de `EnemyStatusData` (donde `307` no existe y `308/310/311` son `Grimoire`/`Magi`/`Vulgate`), confundió `231` (Mercidarian) con Catalina (`230`), borró todas las muñecas del dueño ignorando `Double Puppet` (`313`, presente en Paracas), compartió unicidad con party members en lugar de aislar `3000..3999` (`0x43c85a`), y `DollAction` ignoraba `unit.Attacks`/`unit.Script`.
  3. Hallazgo adicional verificado en `0x4fd630`: el getter de peso (`+0xf4`) de las tres clases de muñecas (`0x6d4768`, `0x6d4dd8`, `0x6d434c`) es `fldz; ret` (**peso `0.0`**, no `owner.Weight`).
- **Corrección:** Calcular `unit.DollBase` en `UnitFactory.BuildMember` reproduciendo `0x4f7c00` sobre las 6 piezas del dueño (sin Crown ni pasivas); usar `DollBase` + `Soul Seal` y `weight = 0.0` en `BuildDoll`; unificar `MakeGuestDoll` con la tabla exacta de 30 entradas de `0x48490a`/`0x4852ca`, respetando `owner.Has(313) ? 2 : 1` y aislando la unicidad por grupo (`member` vs `guest/summon` vs `enemy`, `0x43c83c`–`0x43c86e`).

---

### Alto

#### A1. Errores factuales y habilidades inexistentes en los tutoriales de Balance (`Teaching.pck`)
- **Ubicación:** `tools/class_tutorial_text.py` L65 (`Maid`: `Cheer` no existe y Maid no limpia estados), L66 (`Spieler`: atribuye bonus EXP y muñecas a la clase base), L83 (`Enchantress`: no aprende `Accelerator`), L107 (`Bishop`: `Holy Light` no existe), L111 (`Diva`: `Self Session` permite 2 canciones a la vez, no "cantar actuando libremente"), L113 (`Etoile`: `On Stage` permite 2 bailes a la vez).

#### A2. Divergencias en `MAGIC_ACCURACY_BUFFS`, `Double Puppet` (`316`) y `Barrage Rondo` (`210`)
- **Ubicación:** `engine_cs/src/DtEngine/Battle.cs` L82–L87, L102, L352, L1746–L1753.
  - `MAGIC_ACCURACY_BUFFS` omite `337` (`MAGIC_EVASION_BUFFS` omite `338`), aplica `278`/`353` a todos los hechizos y los duplica en `Lullaby`.
  - Efecto `316` (`Double Puppet` velocidad) es código muerto (`Battle.cs:352`).
  - `210` (`Barrage Rondo`) falta en `SONG_EFFECTS` (`Battle.cs:102`).

#### A3. Instalador: limpieza incompleta de `backup/` tras `balance -> qol` y bloqueo no verificado en `Undo-Pokes`
- **Ubicación:** `installer/mod_patch.ps1` L223, L336, L361–L372 y `installer/mod_patch.py` L286, L420, L448–L476.
  - Al cambiar `balance -> qol`, `$crossBack` se restaura pero no se elimina de `backup/`, mientras desaparece de `installed.txt`, permitiendo sobrescribir archivos actualizados del juego con copias viejas.
  - `Get-Locked` no incluye `$known` pokes cuando `$pokes` está vacío (cambio `balance -> qol`).

#### A4. Empaquetado Linux/Steam Deck: scripts `.sh` sin `create_system = 3` ni bit `0o100000`
- **Ubicación:** `tools/package_variant.py` L194–L200 (`create_system=0`, `mode=0o755` en lugar de `create_system=3`, `0o100755 << 16`).

#### A5. Sesgos y bugs deterministas en `Policy.cs`
- **Ubicación:** `engine_cs/src/DtEngine/Policy.cs` L158 (gating TP sin `Economy`/enchants), L432 (puntuación positiva a resultados dañinos de `RandomMove`), L680–L698 (`T.ALLY_ROW` suma toda la party y elige fila aleatoria), L833 (`Protect` busca `St[170]` en el tanque en vez del enemigo), L1057–L1077 (`HeavyRoles` excluye roles consumidores), y ~45 skills aprendibles inalcanzables por `Policies` (8/10 canciones Bard, 5/7 bailes Etoile, guards, enchants elementales, `Star Dust Arrow`, `Perdurabo`).

---

### Medio

#### M1. Combates/tramos más fáciles que vanilla (y `C24` más difícil) ocultos por `N=40` en `DIFFICULTY_CURVE.md`
- `measures/BOSS_ROWS_CHECK.md` (`N=200`): 3 jefes fuera de ventana por más fáciles (`C28 76%->87%`, `C39 60%->70%`, `P08 10.3->6.5t`) y 1 más difícil (`C36 33%->22%`).
- `measures/WIN_RATES.md` (`N=200`): `C28` Dual-Support (`+18`), Mage-Heavy (`+26`); `C29` Dual-Support (`+18`).
- `measures/POSTGAME_COMPARE.md`: 15/49 jefes de postgame >15 pts más fáciles, 0 más difíciles.
- `measures/RANDOM_BATTLES.md`: `41/42` en ventana; `C24` falla como `won harder` (`85%->72%`).

#### M2. Anomalías abiertas de balance
- `CLASS_BALANCE.md`: 2 parties dominantes (`C29a`), 39 caídas confirmadas (`EXPLOITS.md #12` abierto); `PARTY_BATTERY.md`: 14/85 pares bajo suelo (`C32` falla los 5 arquetipos).
- `SKILL_BATTERY.md` / `SKILL_BATTERY_VARIANTS.md`: 3 `dead` en batería base (`Full Heal`, `Halving Slice`, `Murder`) -> 3 `unclear` (`Evade`, `Halving Slice`, `Murder`) y 0 `dead` en ampliada.
- `UNIQUE_BATTERY.md`: `1 good` (`Shadow Heart`), `17 niche` (`Undaunted Spirit 1%`, `No Miracles Needed 2%`).
- `MERCENARY_BATTERY.md`: `Marion` debajo de banda (`3.4 pts`); `Euthys` (`13.8 pts`, contra `EXPLOITS.md:17` que decía `7.8`), `Momona` (`9.5`), `Euphemia` (`9.1`), `Riesco` (`9.1`) por encima de `[4.0, 8.0]`.
- `SEALBOOK_BATTERY.md`: `Iktomi` (`2.3 pts`) y `Genbu` (`3.7 pts`) muy débiles entre libros de combate.

#### M3. Errores factuales en documentación (`README_Balance.txt`, `README_QoL.txt`, `CONTRIBUTING.md`, `ROSTER_IDENTITY.md`, `VERDICTS.md`)
- `installer/README_Balance.txt:58` dice `+1 SP point` en vez de puntos de Crown/reset; `L95-96` dice `earlier contracts` en vez de contratos +30% más largos (`N158–N172`).
- `installer/README_QoL.txt:34-38` omite `.sh`/Linux en `Install`.
- `CONTRIBUTING.md:13` cita `etoile` como límite conocido cuando ambos límites en `CLASS_STAGES.md` son `dolls` (`advanced` y `late`).
- `docs/ROSTER_IDENTITY.md:284-285, 458-462` sigue describiendo a `Three Fates` como chiste sin tocar (fueron bufadas y `Take Break` bajó de `50` a `20`).
- `docs/generated/VERDICTS.md` (`L100`, `L192`, `L252`) mantiene cifras viejas (`Witch 70.0%`, `WIN_RATES 91%/96%`, oro de misiones `+40%` en vez de `+20%`) y citas a `tools/skill_worth.py`.

#### M4. Contradicciones internas en `docs/FORMULAS.md`
- Líneas `127`, `147`, `189`, `315–331`, `447`, `556–558`, `578`, `784–791`, `930–931`, `990`.

#### M5. Efectos enemigos no modelados (`319 Murder License`, `11`, `62`) y discrepancias menores en `Battle.cs` / `Ai.cs` / `engine_coverage.json`
- `engine_coverage.json:302` lista comando `15` no implementado en `Ai.cs`; `RaceGuard` mágica aditiva (`Battle.cs:1690-1692`); `Arcane Shield` sin comprobar `target.Alive` (`Battle.cs:2029`); `MeanHits` omite efecto `178`; `Ai.cs:199` usa `attack.Name` en vez de `attack.Id`; `Ai.cs:288-289` ignora severidad de estados.

---

### Bajo

#### B1. Higiene del repositorio
- `scratch/` contiene `1.806` archivos sin rastrear (`~549 MB`) no cubiertos por `.gitignore`; `EVAL_OPEN_ITEMS_PROMPT.md` y `RESULTADOS_REGLAS_COMBATE.md` obsoletos en raíz; `CLAUDE.md` con cifras desactualizadas.

#### B2. Detalles menores en scripts y tablas
- Falta `newline='\n'` en `build_variant.py:1222` y `build_guide.py`; `build_variant.py:1412-1415` ignora `Floors: REFUSED`; `package_all.py:45` reporta `len(old)` aunque borre `0`; `uninstall` con `balance.txt` presente imprime `0 file(s) put back`; `ExePatches` `X16` llama "unconditional jump" a `je` (`0F 84`); `sim_setup.xlsx` conserva `summon_hp = 9999` y `etoile` en `ClassLimits`; `README.md:131-132` omite prefijos `data_tables/` y `docs/`; `tools/engine_conformity.py:3` dice `99 items`.

---

## 3. Aspectos verificados sin errores, análisis `MODEL-LIMIT` y limitaciones

- **Sin errores:** 214/214 tests Python, 23/23 tests C#, `engine_conformity.py --check`, builds `qol`/`balance`, `package_all.py`, `build_guide.py`, `exe_patch.py status` (`X01–X17`), `floor_patch.py status` (`166` pokes en 20 packs; `st99` sin filas), 3.586/3.586 filas vivas sin conflictos ni bloqueos, aislamiento completo de textos QoL vs Balance, 0 tildes / 0 no-`latin-1` / 0 `OutOfGameWords` / 0 decimales `>=3` cifras / 100% límites de línea respetados.
- **3 `MODEL-LIMIT`:** `P5.1` (petrificación en 1 etapa en vez de 3) **sí afecta** valoración de petrificación y curas; `P5.3` (pick ponderado en `double`) es **aceptable**; `P11.7` (topes `MaxTime=400 / MaxActions=3000`, `1.07%` del banco golden) es **aceptable** salvo sesgo leve contra builds de desgaste extremo.
- **Limitaciones (requieren prueba en vivo en `DT22_en.exe`):** renderizado de fuente proporcional, sincronización de voz en 10 cajas `Voiced`, ejecución del intérprete de eventos en los 6 `.adv.bin` nuevos de `Teaching.pck`, mecánicas fuera del simulador (Joint/Party Skills, pasos `X15`, curva EXP/reset) y prueba real en Linux/Proton.
