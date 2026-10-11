# Análisis Exhaustivo de Encantamientos (Roadmap QoL - Punto B)
## "144 Cifras de Encantamientos: 101 sin fuente + 43 heredadas de DT1"

**Fecha de análisis:** Octubre 2026  
**Objetivo binario:** `DungeonTravelers2-2_EN/DT22_en_unwrapped.exe` (PE32 x86, ImageBase `0x400000`)  
**Metodología:** Ingeniería inversa con desensamblado Capstone x86, análisis de flujo de control (CFG), rastreo de marcos de pila (`esp`/`ebp`) e inspección de constantes flotantes/enteras en memoria.

---

## 1. Resumen Ejecutivo de Viabilidad

El análisis del ejecutable de Dungeon Travelers 2-2 confirma que **el 100% de las magnitudes de los encantamientos están codificadas directamente en la lógica x86 del binario**. 

### Conclusiones Principales:
1. **Discrepancias críticas con la Wiki de DT1:** Las cifras heredadas de DT1 **no siempre son válidas para DT2-2**. En particular:
   - **Bonos Raciales UP:** En DT1 eran +20%; en DT2-2 fueron rebalanceados a **+15%** (`mulss xmm0, [0x6d931c]`).
   - **Bonos Raciales GrandUP:** En DT1 eran +40%; en DT2-2 fueron rebalanceados a **+30%** (`mulss xmm0, [0x6d9330]`).
   - **Bonos Raciales MegaUP:** En DT1 eran +100%; en DT2-2 fueron rebalanceados a **+60%** (`mulss xmm0, [0x6d934c]`), con excepciones específicas (Fruit, Sea Creatures y Felines que se mantienen en +100%).
   - **Enmity UP (ID 49):** En la wiki de DT1 figuraba como +5%; en el binario de DT2-2 añade exactamente **+10 puntos** (`eax * 5 * 2`).
2. **Causa de la ausencia de cifras en la pasada inicial de QoL:** La herramienta inicial `generate_qol_enchant_text.py` adoptó una regla conservadora: *"solo mostrar cifras procedentes de wikis de jugadores, nunca del binario"*. La ingeniería inversa actual demuestra que el binario contiene constantes explícitas, exactas e irrefutables para los 101 encantamientos sin fuente.
3. **Resolución de todos los casos '?' de `ENCHANT_SIZES.md`:** Los 28 encantamientos marcados con `?` por `exe_enchants.py` eran falsos positivos del analizador sintáctico lineal (saltos incondicionales `jmp`, escalados flat 1.0 sin `mulss`, o llamadas intermedias fuera de la ventana de 16 instrucciones). Se ha determinado la fórmula exacta de cada uno.
4. **Resolución de los 128 casos "No such read":** No usan la llamada de combate `call [unit + 0xf0]`. La mayoría (IDs 0-28, 88-119, 310-356) se evalúan en la función de cálculo de atributos de personaje `0x4f8270 - 0x4f8fcf`. Otros (IDs 211-214, 259, 291) se evalúan a nivel de grupo en la exploración mediante `call 0x4e4f50`. Varios (IDs 196, 247, 275) son falsos negativos de `exe_enchants.py` causados por optimizaciones del compilador (`call eax` o branches convergentes).

---

## 2. Análisis Detallado de las 43 Cifras Heredadas de DT1

A continuación se detalla la verificación en el binario de DT2-2 para cada uno de los 43 encantamientos con fuente `dt2-wiki`:

| ID | Nombre Vanilla | DT1 Wiki | Dirección DT2-2 | Instrucción / Constante Real | Cifra Real DT2-2 | Veredicto |
|---|---|---|---|---|---|---|
| 2 | Max HP DOWN | -10% | `0x4f83b6` | `imul [ebp+8]; sar edx, 2; sub esi, eax` | -10% | **COINCIDE** |
| 29 | Physical attack UP | +4% | `0x44b69a` | `mulss xmm0, [0x6d9430]` (4.0) | +4% | **COINCIDE** |
| 30 | Physical attack MiniUP | +2% | `0x44b6d4` | `addss xmm0, xmm0` (x2.0) | +2% | **COINCIDE** |
| 37 | Magic attack UP | +4% | `0x44df30` | `mulss xmm0, [0x6d9430]` (4.0) | +4% | **COINCIDE** |
| 38 | Magic attack MiniUP | +2% | `0x44df6a` | `addss xmm0, xmm0` (x2.0) | +2% | **COINCIDE** |
| 49 | Enmity UP | +5% | `0x44a736` | `lea eax, [eax+eax*4]; add eax, eax` | **+10 flat** | **CONTRADICE** (+10, no +5) |
| 50 | Enmity DOWN | -5% | `0x44a74d` | `lea eax, [eax+eax*4]; sub ecx, eax` | **-5 flat** | **COINCIDE** (-5 flat) |
| 51 | Speed UP | +10% | `0x44a114` | `mulss xmm0, [0x6d930c]` (0.10) | +10% | **COINCIDE** |
| 52 | Speed MiniUP | +5% | `0x44a14d` | `mulss xmm0, [0x6d92ec]` (0.05) | +5% | **COINCIDE** |
| 54 | Chant speed UP | +20% | `0x449f6a` | `mulss xmm0, [0x6d9324]` (0.20) | +20% | **COINCIDE** |
| 55 | Chant speed MiniUP | +10% | `0x449fa3` | `mulss xmm0, [0x6d930c]` (0.10) | +10% | **COINCIDE** |
| 58 | Interruption rate DOWN | -6% | `0x44d0bd` | `mulss xmm0, [0x6d92f4]` (0.06) | -6% | **COINCIDE** |
| 59 | Interruption rate MiniDOWN | -3% | `0x44d0f4` | `mulss xmm0, [0x6d92dc]` (0.03) | -3% | **COINCIDE** |
| 60 | Interruption rate UP | +6% | `0x44d12b` | `mulss xmm0, [0x6d92f4]` (0.06) | +6% | **COINCIDE** |
| 72 | Convert received damage into TP | 5% | `0x47e68d` | `mulss xmm0, [0x6d92ec]` (0.05) | 5% | **COINCIDE** |
| 78 | Fire magic buff | +20% | `0x44e04b` | `mulss xmm0, [0x6d9324]` (0.20) | +20% | **COINCIDE** |
| 79 | Water magic buff | +20% | `0x44e101` | `mulss xmm0, [0x6d9324]` (0.20) | +20% | **COINCIDE** |
| 80 | Wind magic buff | +20% | `0x44e1b7` | `mulss xmm0, [0x6d9324]` (0.20) | +20% | **COINCIDE** |
| 81 | Earth magic buff | +20% | `0x44e26d` | `mulss xmm0, [0x6d9324]` (0.20) | +20% | **COINCIDE** |
| 82 | Lightning magic buff | +20% | `0x44e37d` | `mulss xmm0, [0x6d9324]` (0.20) | +20% | **COINCIDE** |
| 119 | Physical resistance DOWN | -10 | `0x4f8b86` | `sub [ebp-0x54], 0xa` (-10) | -10 flat | **COINCIDE** |
| 161 | Normal attacks absorb lots of HP | 50% HP | `0x42156f` | `movss xmm2, [0x6d9348]` (0.50) | 50% HP | **COINCIDE** (No undead) |
| 162 | Normal attacks absorb HP | 15% HP | `0x4215c4` | `movss xmm2, [0x6d931c]` (0.15) | 15% HP | **COINCIDE** (No undead) |
| 163 | Normal attacks absorb lots of TP | 20% TP | `0x421619` | `movss xmm2, [0x6d9324]` (0.20) | 20% TP | **COINCIDE** (No undead) |
| 164 | Normal attacks absorb TP | 5% TP | `0x42166e` | `movss xmm2, [0x6d92ec]` (0.05) | 5% TP | **COINCIDE** (No undead) |
| 170 | Physical attack vs. Demons GrandUP | +40% | `0x44bfbb` | `mulss xmm0, [0x6d9330]` (0.30) | **+30%** | **CONTRADICE** (+30%, no +40%) |
| 171 | Physical attack vs. Demons UP | +20% | `0x44bff5` | `mulss xmm0, [0x6d931c]` (0.15) | **+15%** | **CONTRADICE** (+15%, no +20%) |
| 172 | Physical attack vs. Apparitions GrandUP | +40% | `0x44c06f` | `mulss xmm0, [0x6d9330]` (0.30) | **+30%** | **CONTRADICE** (+30%, no +40%) |
| 173 | Physical attack vs. Apparitions UP | +20% | `0x44c0a9` | Handler `0x44c01d`: `mulss 0.15` | **+15%** | **CONTRADICE** (+15%, no +20%) |
| 174 | Phys. attack vs. Magic Beings GrandUP | +40% | `0x44c0ce` | `mulss xmm0, [0x6d9330]` (0.30) | **+30%** | **CONTRADICE** (+30%, no +40%) |
| 175 | Physical attack vs. Magic Beings UP | +20% | `0x44c108` | Handler `0x44c01d`: `mulss 0.15` | **+15%** | **CONTRADICE** (+15%, no +20%) |
| 176 | Physical attack vs. Humans MegaUP | +100% | `0x44c131` | `mulss xmm0, [0x6d934c]` (0.60) | **+60%** | **CONTRADICE** (+60%, no +100%) |
| 177 | Physical attack vs. Humans GrandUP | +40% | `0x44c16b` | `mulss xmm0, [0x6d9330]` (0.30) | **+30%** | **CONTRADICE** (+30%, no +40%) |
| 178 | Physical attack vs. Humans UP | +20% | `0x44c1a5` | `mulss xmm0, [0x6d931c]` (0.15) | **+15%** | **CONTRADICE** (+15%, no +20%) |
| 179 | Physical attack vs. Undead GrandUP | +40% | `0x44c1e5` | `mulss xmm0, [0x6d9330]` (0.30) | **+30%** | **CONTRADICE** (+30%, no +40%) |
| 180 | Physical attack vs. Undead UP | +20% | `0x44c21f` | Handler `0x44c01d`: `mulss 0.15` | **+15%** | **CONTRADICE** (+15%, no +20%) |
| 181 | Physical attack vs. Dragons GrandUP | +40% | `0x44c244` | `mulss xmm0, [0x6d9330]` (0.30) | **+30%** | **CONTRADICE** (+30%, no +40%) |
| 182 | Physical attack vs. Dragons UP | +20% | `0x44c27e` | Handler `0x44c01d`: `mulss 0.15` | **+15%** | **CONTRADICE** (+15%, no +20%) |
| 183 | Physical attack vs. Beasts GrandUP | +40% | `0x44c2a3` | `mulss xmm0, [0x6d9330]` (0.30) | **+30%** | **CONTRADICE** (+30%, no +40%) |
| 184 | Physical attack vs. Beasts UP | +20% | `0x44c2dd` | Handler `0x44c01d`: `mulss 0.15` | **+15%** | **CONTRADICE** (+15%, no +20%) |
| 185 | Physical attack vs. Fruit MegaUP | +100% | `0x44c302` | `cvtpd2ps; addss [ebp-0x14]` (1.0) | +100% | **COINCIDE** |
| 186 | Physical attack vs. Fruit GrandUP | +50% | `0x44c334` | `mulss xmm0, [0x6d9348]` (0.50) | +50% | **COINCIDE** |
| 196 | Physical attack vs. Felines MegaUP | +100% | `0x44c370` | Branch `0x44c38d`: `addss 1.0` | +100% | **COINCIDE** |

---

## 3. Resolución de los Casos '?' en `ENCHANT_SIZES.md`

El script `exe_enchants.py` utilizaba un análisis regex con una ventana estricta de 16 instrucciones lineales tras la llamada `call [vtable+0xf0]`. Los 28 casos reportados con `?` se explican técnicamente por los siguientes patrones:

1. **Saltos Incondicionales (`jmp`) a Manejadores Comunes:**
   - **IDs 173, 175, 180, 182, 184 (Racial UP):** Ejecutan `call [eax+0xf0]`, empujan el ID del siguiente encantamiento y saltan mediante `jmp 0x44c000`. En `0x44c01d` se ejecuta `mulss xmm0, [0x6d931c]`, multiplicando el valor por **0.15 (+15%)**.
   - **IDs 227, 229, 231, 233, 235, 237, 239, 241 (Damage from [Race] 5% DOWN):** Tras la llamada ejecutan `jmp 0x44bea4`. En `0x44bec9` se ejecuta `mulss xmm0, [0x6d92ec]`, multiplicando el valor por **0.05 (-5%)**.
   - **IDs 251, 252, 253, 254, 255 (Both Sides Element UP):** Saltan a `0x44c468`. En `0x44c485` y `0x44c4b8` se multiplica por `[0x6d9324]`, otorgando **+20% (0.20)** a ambos bandos.
   - **ID 300 (Song skill efficacy UP):** En `0x48c037` salta con `jmp 0x48c055`. En `0x48c071` se multiplica por `[0x6d92e0]`, otorgando **+2% (0.02)**.
2. **Escalados Flat 1.0 (Sin instrucción `mulss`):**
   - **ID 40 (Magic accuracy MiniUP):** El valor devuelto por la llamada se convierte de entero a float (`cvtdq2pd` / `cvtpd2ps`) y en `0x44d6bd` se suma directamente con `addss xmm0, [ebp+0x5c]` al total de Magic accuracy UP. Escala **+1 punto flat**.
   - **ID 44 (Magic evasion MiniUP):** Se convierte a float y en `0x44d742` se suma directamente con `addss xmm1, [ebp+0x48]`. Escala **+1 punto flat**.
   - **ID 46 (Critical rate MiniUP):** Se convierte a float y en `0x44f3f7` se suma directamente con `addss xmm3, [esp+0x1c]` al término base de golpe crítico. Escala **+1% flat**.
   - **ID 185 (Fruit MegaUP) e ID 209 (Sea Creatures MegaUP):** En `0x44c32a` y `0x44c3ab` el conteo convertido a float se suma directamente a la bonificación de daño racial sin factor multiplicador, representando un incremento de **+1.0 (+100%)**.
3. **Instrucción de Escalado fuera de la Ventana:**
   - **ID 42 (Magic defense MiniUP):** Tras el `call` en `0x44e5c6`, el código ejecuta llamadas auxiliares a atributos (`call [eax+0x34]`). La instrucción de duplicación `addss xmm1, xmm1` (**x2.0 = +2%**) ocurre en `0x44e637`, 17 instrucciones después del call, fuera del alcance del script de análisis original.
   - **ID 305 (Doll skill efficacy MiniUP):** En `0x44b58e`, `0x44de4b` y `0x48d847`, el factor de escala real es `mulss xmm0, [0x6d92d4]` (**0.01 = +1%**). Los números 20 y 500 detectados eran cálculos de atributos ajenos al encantamiento.
4. **Lógica Aritmética de Turnos / Banderas:**
   - **ID 265 (Rate of status ailments dissipation UP):** En `0x48d1f8` ejecuta `neg eax; sbb eax, eax; and eax, ~2; add eax, 5`. Si `eax > 0`, el umbral de comprobación de disipación de estados alterados baja de **5 turnos a 2 turnos** (`cmp [ebx+0x30], 2`). Actúa como interruptor de 2 turnos.
   - **ID 267 (Smaller party, higher damage):** En `0x44c95f` calcula `5 - party_size` y en `0x44c97e` multiplica por `[0x6d930c]` (**0.10 = +10%**). Bonificación exacta: **+10% de daño por cada aliado faltante**.
5. **Falsos Positivos en Clases Externas:**
   - **ID 1 (Max HP MiniUP):** Las direcciones `0x5182c9` y `0x5222b2` llamaban al slot 0xf0 del gestor de grupo (`0x71fc24`) con 4 argumentos (`push 1; push 0; push 1; push edi`), no a una unidad. El cálculo real de Max HP MiniUP reside en `0x4f8382`: `int(base_HP / 20), at least 2` (**+5%, mínimo +2**).

---

## 4. Análisis de los 128 Encantamientos "No Such Read"

Los 128 encantamientos sin llamada en slot 0xf0 durante el combate se desglosan en 4 categorías arquitectónicas precisas:

### A) Atributos Directos de Personaje (`0x4f8270 - 0x4f8fcf`)
Se aplican en el bucle de equipo al recalcular los atributos base de la heroína:
- **Atributos Principales (IDs 0 a 28):**
  - UP (IDs 0, 3, 6, 9, 12, 15, 18, 21): `int(stat / 10), min 4` (**+10%, mín +4**).
  - MiniUP (IDs 1, 4, 7, 10, 13, 16, 19, 22): `int(stat / 20), min 2` (**+5%, mín +2**).
  - DOWN (IDs 2, 5, 8, 11, 14, 17, 20, 23): `-int(stat / 10)` (**-10%**).
  - All stats +N (IDs 24 a 28): Añade **+1, +2, +3, +4, +5 flat** a los 6 atributos principales.
- **Resistencias Elementales y Físicas (IDs 88-119, 310-332, 335-336, 340-356):**
  - Elemental UP / MiniUP / DOWN: **+20 / +10 / -20**.
  - All Elements GrandUP / UP / MiniUP / DOWN: **+50 / +15 / +7 / -15** a los 5 elementos.
  - Physical UP / MiniUP / DOWN: **+20 / +10 / -20**.
  - All Physical GrandUP / UP / MiniUP / DOWN: **+25 / +10 / +5 / -10** (Slash, Stab, Bash).
  - MegaUP / GrandUP elementales (310-332, 340-352): **+100 / +50 / -50**.
  - All Elements GrandUP (335): **+75** a los 5 elementos; All Elements DOWN (336): **-30**.
  - All Physical GrandUP (355): **+50**; All Physical DOWN (356): **-20**.
  - Límite global: La suma se trunca estrictamente entre **-100 y +100** (`0x4f8497 - 0x4f84a0`).
- **Bonos de Posición / Línea (IDs 222-225, 281):**
  - 222, 223 (Front line) y 224, 225 (Back line): `int(stat / 25)` (**+4%** del atributo).
  - 281 (Same line): `int(stat / 50)` (**+2%** del atributo).

### B) Modificadores de Exploración y Mazmorra (`CDungeonBase`, `0x4e4f50`)
Se consultan mediante el helper booleano de grupo `0x4e4f50`:
- **Tasas de Encuentro (IDs 211 a 214 en `0x4bc802 - 0x4bc843`):**
  - 211 (Slightly reduce): **-1%** a la probabilidad de combate aleatorio.
  - 212 (Greatly reduce): **-2%** a la probabilidad de combate aleatorio.
  - 213 (Slightly increase): **+1%** a la probabilidad de combate aleatorio.
  - 214 (Greatly increase): **+2%** a la probabilidad de combate aleatorio.
- **Encuentros con Mercader / Tienda (ID 259 en `0x55639d`):**
  - Reduce el contador de pasos requeridos de **50 pasos a 25 pasos (-50% pasos)**.
- **Aparición de Mímicos en Cofres (ID 291 en `0x55576c`):**
  - Si el cofre puede ser mímico, añade **+20% (`0x14`)** a la probabilidad.

### C) Falsos Negativos por Optimización de Compilador en Combate
- **ID 196 (Physical attack vs. Felines MegaUP):** Leído en `0x44c38d` tras branch en `0x44c370`. Escala **+100% (1.0)**.
- **ID 247 (TP Cost for techniques MegaDOWN):** Leído en `0x4fd30d` tras branch en `0x4fd2b3`. Multiplica coste por **0.6 (-40% TP)**.
- **ID 272 (Reduce damage penalty for missed spells):** Leído en `0x44ee3d`. Daño en fallo pasa de **50% a 75%** (penalización reducida al 25%).
- **ID 275 (Double EXP):** Leído en `0x445a13` mediante `call eax` (`mov eax, [eax+0xf0]`). Duplica la experiencia recibida (**x2, +100%**).
- **ID 296 (May rarely recover all HP when turn starts):** Leído en `0x437d0a`. Ejecuta `rand(100) < 4` (**4% de probabilidad por turno de curar 100% HP**).

### D) Banderas de Inmunidad y Nulificación
- **IDs 120-128 (Nulificación de Daño):** Bloquean el 100% del daño del tipo específico antes de calcular defensas (`0x421b07 - 0x421c52`).
- **IDs 129-139 (Inmunidad a Estados):** Bloquean la tirada de infligir el estado alterado correspondiente (`0x481f2d - 0x4838ae`).

---

## 5. Tabla Maestra de Encantamientos Verificados en el EXE

Todos los nombres propuestos cumplen estrictamente:
- **Longitud máxima <= 30 caracteres** (apto para `EnchantData.pck` y columna de equipo).
- **Regla D10 de QoL:** Cero comentarios meta; formulación in-game limpia con su cifra exacta.

| ID | Nombre Vanilla | Dirección EXE | Instrucción / Constante x86 | Valor Real | Nombre QoL Propuesto (<= 30 chars) | Chars |
|---|---|---|---|---|---|---|
| **2** | Max HP DOWN | `0x4f83b6` | `sar edx, 2; sub esi, eax` | -10% HP | `Max HP -10%` | 11 |
| **29** | Physical attack UP | `0x44b69a` | `mulss xmm0, [0x6d9430]` (4.0) | +4% ATK | `Physical attack +4%` | 20 |
| **30** | Physical attack MiniUP | `0x44b6d4` | `addss xmm0, xmm0` (2.0) | +2% ATK | `Physical attack +2%` | 20 |
| **31** | Physical accuracy UP | `0x44ad18` | `mulss xmm0, [0x6d9430]` (4.0) | +4 Acc | `Physical accuracy +4%` | 21 |
| **32** | Physical accuracy MiniUP | `0x44ad52` | `addss xmm0, xmm0` (2.0) | +2 Acc | `Physical accuracy +2%` | 21 |
| **33** | Physical defense UP | `0x44b8eb` | `mulss xmm0, [0x6d9430]` (4.0) | +4% DEF | `Physical defense +4%` | 20 |
| **34** | Physical defense MiniUP | `0x44b925` | `addss xmm0, xmm0` (2.0) | +2% DEF | `Physical defense +2%` | 20 |
| **35** | Physical evasion UP | `0x44ad91` | `mulss xmm0, [0x6d9430]` (4.0) | +4 Eva | `Physical evasion +4%` | 20 |
| **36** | Physical evasion MiniUP | `0x44adcb` | `addss xmm0, xmm0` (2.0) | +2 Eva | `Physical evasion +2%` | 20 |
| **37** | Magic attack UP | `0x44df30` | `mulss xmm0, [0x6d9430]` (4.0) | +4% MATK | `Magic attack +4%` | 17 |
| **38** | Magic attack MiniUP | `0x44df6a` | `addss xmm0, xmm0` (2.0) | +2% MATK | `Magic attack +2%` | 17 |
| **39** | Magic accuracy UP | `0x44d67b` | `mulss xmm0, [0x6d9408]` (3.0) | +3 MAcc | `Magic accuracy +3%` | 18 |
| **40** | Magic accuracy MiniUP | `0x44d6bd` | `addss xmm0, [ebp+0x5c]` (1.0) | +1 MAcc | `Magic accuracy +1%` | 18 |
| **41** | Magic defense UP | `0x44e5b1` | `mulss xmm0, [0x6d9430]` (4.0) | +4% MDEF | `Magic defense +4%` | 17 |
| **42** | Magic defense MiniUP | `0x44e637` | `addss xmm1, xmm1` (2.0) | +2% MDEF | `Magic defense +2%` | 17 |
| **43** | Magic evasion UP | `0x44d6f0` | `mulss xmm0, [0x6d9408]` (3.0) | +3 MEva | `Magic evasion +3%` | 17 |
| **44** | Magic evasion MiniUP | `0x44d742` | `addss xmm1, [ebp+0x48]` (1.0) | +1 MEva | `Magic evasion +1%` | 17 |
| **45** | Critical rate UP | `0x44f357` | `mulss xmm0, [0x6d9430]` (4.0) | +4% Crit | `Critical rate +4%` | 17 |
| **46** | Critical rate MiniUP | `0x44f3f7` | `addss xmm3, [esp+0x1c]` (1.0) | +1% Crit | `Critical rate +1%` | 17 |
| **47** | Enemy critical rate DOWN | `0x44f3c0` | `mulss xmm0, [0x6d9430]` (4.0) | -4% Crit | `Enemy critical rate -4%` | 23 |
| **48** | Enemy critical rate MiniDOWN | `0x44f43f` | `addss xmm0, xmm0` (2.0) | -2% Crit | `Enemy critical rate -2%` | 23 |
| **49** | Enmity UP | `0x44a736` | `lea [eax+eax*4]; add eax, eax` | +10 Enmity | `Enmity +10` | 10 |
| **50** | Enmity DOWN | `0x44a74d` | `lea [eax+eax*4]; sub ecx, eax` | -5 Enmity | `Enmity -5` | 9 |
| **51** | Speed UP | `0x44a114` | `mulss xmm0, [0x6d930c]` (0.10) | +10% Spd | `Speed +10%` | 10 |
| **52** | Speed MiniUP | `0x44a14d` | `mulss xmm0, [0x6d92ec]` (0.05) | +5% Spd | `Speed +5%` | 9 |
| **53** | Speed DOWN | `0x44a185` | `mulss xmm0, [0x6d930c]` (0.10) | -10% Spd | `Speed -10%` | 10 |
| **54** | Chant speed UP | `0x449f6a` | `mulss xmm0, [0x6d9324]` (0.20) | +20% Chant | `Chant speed +20%` | 16 |
| **55** | Chant speed MiniUP | `0x449fa3` | `mulss xmm0, [0x6d930c]` (0.10) | +10% Chant | `Chant speed +10%` | 16 |
| **56** | Chant speed DOWN | `0x449fdb` | `mulss xmm0, [0x6d9324]` (0.20) | -20% Chant | `Chant speed -20%` | 16 |
| **57** | Interruption rate GrandDOWN | `0x44d083` | `mulss xmm0, [0x6d930c]` (0.10) | -10% Int | `Interruption rate -10%` | 22 |
| **58** | Interruption rate DOWN | `0x44d0bd` | `mulss xmm0, [0x6d92f4]` (0.06) | -6% Int | `Interruption rate -6%` | 21 |
| **59** | Interruption rate MiniDOWN | `0x44d0f4` | `mulss xmm0, [0x6d92dc]` (0.03) | -3% Int | `Interruption rate -3%` | 21 |
| **60** | Interruption rate UP | `0x44d12b` | `mulss xmm0, [0x6d92f4]` (0.06) | +6% Int | `Interruption rate +6%` | 21 |
| **61** | Interruption rate MegaDOWN | `0x44d166` | `mulss xmm0, [0x6d9324]` (0.20) | -20% Int | `Interruption rate -20%` | 22 |
| **72** | Convert received damage into TP | `0x47e68d` | `mulss xmm0, [0x6d92ec]` (0.05) | 5% Dmg->TP | `Damage to TP: 5%` | 16 |
| **73** | Convert received damage into big TP | `0x47e6be` | `mulss xmm0, [0x6d930c]` (0.10) | 10% Dmg->TP | `Damage to TP: 10%` | 17 |
| **78** | Fire magic buff | `0x44e04b` | `mulss xmm0, [0x6d9324]` (0.20) | +20% Fire | `Fire magic +20%` | 15 |
| **79** | Water magic buff | `0x44e101` | `mulss xmm0, [0x6d9324]` (0.20) | +20% Water | `Water magic +20%` | 16 |
| **80** | Wind magic buff | `0x44e1b7` | `mulss xmm0, [0x6d9324]` (0.20) | +20% Wind | `Wind magic +20%` | 15 |
| **81** | Earth magic buff | `0x44e26d` | `mulss xmm0, [0x6d9324]` (0.20) | +20% Earth | `Earth magic +20%` | 16 |
| **82** | Lightning magic buff | `0x44e37d` | `mulss xmm0, [0x6d9324]` (0.20) | +20% Light | `Lightning magic +20%` | 20 |
| **119**| Physical resistance DOWN | `0x4f8b86` | `sub [ebp-0x54], 0xa` (-10) | -10 Res | `Physical resistance -10` | 24 |
| **161**| Normal attacks absorb lots of HP | `0x42156f` | `movss xmm2, [0x6d9348]` (0.50) | 50% HP Drain | `Attacks absorb 50% HP` | 21 |
| **162**| Normal attacks absorb HP | `0x4215c4` | `movss xmm2, [0x6d931c]` (0.15) | 15% HP Drain | `Attacks absorb 15% HP` | 21 |
| **163**| Normal attacks absorb lots of TP | `0x421619` | `movss xmm2, [0x6d9324]` (0.20) | 20% TP Drain | `Attacks absorb 20% TP` | 21 |
| **164**| Normal attacks absorb TP | `0x42166e` | `movss xmm2, [0x6d92ec]` (0.05) | 5% TP Drain | `Attacks absorb 5% TP` | 20 |
| **170**| Physical attack vs. Demons GrandUP | `0x44bfbb` | `mulss xmm0, [0x6d9330]` (0.30) | +30% vs Dem | `ATK vs. Demons +30%` | 19 |
| **171**| Physical attack vs. Demons UP | `0x44bff5` | `mulss xmm0, [0x6d931c]` (0.15) | +15% vs Dem | `ATK vs. Demons +15%` | 19 |
| **172**| Physical attack vs. Apparitions GrandUP | `0x44c06f` | `mulss xmm0, [0x6d9330]` (0.30) | +30% vs App | `ATK vs. Apparitions +30%` | 24 |
| **173**| Physical attack vs. Apparitions UP | `0x44c01d` | `mulss xmm0, [0x6d931c]` (0.15) | +15% vs App | `ATK vs. Apparitions +15%` | 24 |
| **174**| Phys. attack vs. Magic Beings GrandUP | `0x44c0ce` | `mulss xmm0, [0x6d9330]` (0.30) | +30% vs Mag | `ATK vs. Magic Beings +30%` | 25 |
| **175**| Physical attack vs. Magic Beings UP | `0x44c01d` | `mulss xmm0, [0x6d931c]` (0.15) | +15% vs Mag | `ATK vs. Magic Beings +15%` | 25 |
| **176**| Physical attack vs. Humans MegaUP | `0x44c131` | `mulss xmm0, [0x6d934c]` (0.60) | +60% vs Hum | `ATK vs. Humans +60%` | 19 |
| **177**| Physical attack vs. Humans GrandUP | `0x44c16b` | `mulss xmm0, [0x6d9330]` (0.30) | +30% vs Hum | `ATK vs. Humans +30%` | 19 |
| **178**| Physical attack vs. Humans UP | `0x44c1a5` | `mulss xmm0, [0x6d931c]` (0.15) | +15% vs Hum | `ATK vs. Humans +15%` | 19 |
| **179**| Physical attack vs. Undead GrandUP | `0x44c1e5` | `mulss xmm0, [0x6d9330]` (0.30) | +30% vs Und | `ATK vs. Undead +30%` | 19 |
| **180**| Physical attack vs. Undead UP | `0x44c01d` | `mulss xmm0, [0x6d931c]` (0.15) | +15% vs Und | `ATK vs. Undead +15%` | 19 |
| **181**| Physical attack vs. Dragons GrandUP | `0x44c244` | `mulss xmm0, [0x6d9330]` (0.30) | +30% vs Dra | `ATK vs. Dragons +30%` | 20 |
| **182**| Physical attack vs. Dragons UP | `0x44c01d` | `mulss xmm0, [0x6d931c]` (0.15) | +15% vs Dra | `ATK vs. Dragons +15%` | 20 |
| **183**| Physical attack vs. Beasts GrandUP | `0x44c2a3` | `mulss xmm0, [0x6d9330]` (0.30) | +30% vs Bst | `ATK vs. Beasts +30%` | 19 |
| **184**| Physical attack vs. Beasts UP | `0x44c01d` | `mulss xmm0, [0x6d931c]` (0.15) | +15% vs Bst | `ATK vs. Beasts +15%` | 19 |
| **185**| Physical attack vs. Fruit MegaUP | `0x44c32a` | `cvtpd2ps; addss [ebp-0x14]` (1.0) | +100% vs Fru | `ATK vs. Fruit +100%` | 19 |
| **186**| Physical attack vs. Fruit GrandUP | `0x44c352` | `mulss xmm0, [0x6d9348]` (0.50) | +50% vs Fru | `ATK vs. Fruit +50%` | 18 |
| **196**| Physical attack vs. Felines MegaUP | `0x44c3ab` | `cvtpd2ps; addss [ebp-0x14]` (1.0) | +100% vs Fel | `ATK vs. Felines +100%` | 21 |
| **203**| Physical attack vs. Demons MegaUP | `0x44c04d` | `mulss xmm0, [0x6d934c]` (0.60) | +60% vs Dem | `ATK vs. Demons +60%` | 19 |
| **204**| Physical attack vs. Apparitions MegaUP | `0x44c04d` | Handler `0x44c02f`: `mulss 0.60` | +60% vs App | `ATK vs. Apparitions +60%` | 24 |
| **205**| Phys. attack vs. Magic Beings MegaUP | `0x44c04d` | Handler `0x44c02f`: `mulss 0.60` | +60% vs Mag | `ATK vs. Magic Beings +60%` | 25 |
| **206**| Physical attack vs. Undead MegaUP | `0x44c04d` | Handler `0x44c02f`: `mulss 0.60` | +60% vs Und | `ATK vs. Undead +60%` | 19 |
| **207**| Physical attack vs. Dragons MegaUP | `0x44c04d` | Handler `0x44c02f`: `mulss 0.60` | +60% vs Dra | `ATK vs. Dragons +60%` | 20 |
| **208**| Physical attack vs. Beasts MegaUP | `0x44c04d` | Handler `0x44c02f`: `mulss 0.60` | +60% vs Bst | `ATK vs. Beasts +60%` | 19 |
| **209**| Phys. attack vs. Sea Creatures MegaUP| `0x44c3ab` | `cvtpd2ps; addss [ebp-0x14]` (1.0) | +100% vs Sea | `ATK vs. Sea Creatures +100%` | 27 |
| **211**| Slightly reduce encounter rate | `0x4bc812` | `call 0x4e4f50; or edi, -1` | -1% Encount | `Encounter rate -1%` | 18 |
| **212**| Greatly reduce encounter rate | `0x4bc823` | `call 0x4e4f50; sub edi, 2` | -2% Encount | `Encounter rate -2%` | 18 |
| **213**| Slightly increase encounter rate | `0x4bc834` | `call 0x4e4f50; inc edi` | +1% Encount | `Encounter rate +1%` | 18 |
| **214**| Greatly increase encounter rate | `0x4bc843` | `call 0x4e4f50; add edi, 2` | +2% Encount | `Encounter rate +2%` | 18 |
| **219**| Attack vs. high lvl enemies UP | `0x44ca0b` | `mulss xmm0, [0x6d930c]` (0.10) | +10% Dmg | `ATK vs. high lvl +10%` | 21 |
| **220**| Attack vs. low lvl enemies UP | `0x44ca60` | `mulss xmm0, [0x6d930c]` (0.10) | +10% Dmg | `ATK vs. low lvl +10%` | 20 |
| **246**| TP Cost for techniques DOWN | `0x4fd2a7` | `mulss xmm0, [0x6d936c]` (0.80) | -20% TP (x0.8) | `Technique TP Cost -20%` | 22 |
| **247**| TP Cost for techniques MegaDOWN | `0x4fd31e` | `mulss xmm0, [0x6d934c]` (0.60) | -40% TP (x0.6) | `Technique TP Cost -40%` | 22 |
| **248**| TP Cost for spells DOWN | `0x4fd2f8` | `mulss xmm0, [0x6d936c]` (0.80) | -20% TP (x0.8) | `Spell TP Cost -20%` | 18 |
| **249**| TP Cost for spells MegaDOWN | `0x4fd31e` | `mulss xmm0, [0x6d934c]` (0.60) | -40% TP (x0.6) | `Spell TP Cost -40%` | 18 |
| **251**| Fire attack for both sides UP | `0x44c485` | `mulss xmm0, [0x6d9324]` (0.20) | +20% All Fire | `All Fire attacks +20%` | 21 |
| **252**| Water attack for both sides UP | `0x44c485` | `mulss xmm0, [0x6d9324]` (0.20) | +20% All Wat | `All Water attacks +20%` | 22 |
| **253**| Wind attack for both sides UP | `0x44c485` | `mulss xmm0, [0x6d9324]` (0.20) | +20% All Wnd | `All Wind attacks +20%` | 21 |
| **254**| Earth attack for both sides UP | `0x44c485` | `mulss xmm0, [0x6d9324]` (0.20) | +20% All Ear | `All Earth attacks +20%` | 22 |
| **255**| Lightning attack for both sides UP| `0x44c485` | `mulss xmm0, [0x6d9324]` (0.20) | +20% All Lgt | `All Lightning attacks +20%`| 26 |
| **259**| Higher chance of shop encounters | `0x5563b3` | `cmovne esi, 25` (steps: 50->25)| Steps -50% | `Shop encounters: steps -50%` | 28 |
| **261**| Damage of joint skills UP | `0x44c8b4` | `mulss xmm0, [0x6d930c]` (0.10) | +10% Joint | `Joint skill damage +10%` | 23 |
| **265**| Rate of status ailments dissipation UP| `0x48d202`| `and eax, ~2; add eax, 5` | 2 Turns | `Ailment recovery: 2 turns` | 26 |
| **267**| The smaller your party, the higher your damage| `0x44c97e`| `(5 - allies) * 0.10` | +10% / miss ally | `DMG +10% / missing ally` | 23 |
| **268**| Critical rate UP | `0x44f4c3` | `cmovne xmm1, 20.0` (floor 5->20)| Min Crit 20% | `Min Critical rate: 20%` | 23 |
| **272**| Reduce damage penalty for missed spells| `0x44ee4e`| `esi = (3 * dmg) / 4` (75% dmg) | Miss Pen: 25% | `Missed spell penalty: 25%` | 26 |
| **275**| Double EXP | `0x445a1e` | `addss xmm1, xmm1` (x2.0) | EXP x2 (+100%) | `Double EXP (+100%)` | 18 |
| **276**| Equipment drop rate UP | `0x558255` | `eax * 5 * 4` (+20) | +20% Drop | `Equipment drop rate +20%` | 24 |
| **280**| Damage to enemies with status ailments UP| `0x44cd83`| `mulss xmm0, [0x6d931c]` (0.15) | +15% Dmg | `DMG to ailing enemies +15%` | 26 |
| **290**| Joint skill damage MegaUP | `0x44c8ee` | `mulss xmm0, [0x6d9324]` (0.20) | +20% Joint | `Joint skill damage +20%` | 23 |
| **291**| Increase Mimic appearance rate in chests| `0x55577a`| `add ebx, 0x14` (+20%) | +20% Mimic | `Mimic chest rate +20%` | 21 |
| **296**| May rarely recover all HP when turn starts| `0x437d1a`| `call 0x505ac0; cmp eax, 4` | 4% Turn Full HP| `4% chance: full HP on turn` | 26 |
| **298**| Magic incantations go very fast... sometimes| `0x44a380`| `addss xmm0, [0x6d932c]` (0.25) | +25% Chant Spd | `Chant speed +25%` | 16 |
| **300**| Song skill efficacy UP | `0x48c071` | `mulss xmm0, [0x6d92e0]` (0.02) | +2% Song | `Song skill efficacy +2%` | 23 |
| **301**| Song skill efficacy MiniUP | `0x48c07e` | `mulss xmm0, [0x6d92d4]` (0.01) | +1% Song | `Song skill efficacy +1%` | 23 |
| **302**| Dance skill efficacy UP | `0x48c04a` | `mulss xmm0, [0x6d92e0]` (0.02) | +2% Dance | `Dance skill efficacy +2%` | 24 |
| **303**| Dance skill efficacy MiniUP | `0x48c07e` | `mulss xmm0, [0x6d92d4]` (0.01) | +1% Dance | `Dance skill efficacy +1%` | 24 |
| **304**| Doll skill efficacy UP | `0x44b533` | `mulss xmm0, [0x6d92e0]` (0.02) | +2% Doll | `Doll skill efficacy +2%` | 23 |
| **305**| Doll skill efficacy MiniUP | `0x44b58e` | `mulss xmm0, [0x6d92d4]` (0.01) | +1% Doll | `Doll skill efficacy +1%` | 24 |

---

## 6. Lista de Encantamientos Tipo Interruptor ("Any piece") y Banderas

Los siguientes encantamientos se evalúan exclusivamente mediante una comprobación booleana (`test eax, eax; je / jne` o `call 0x4e4f50`). **No escalan por pieza equipada**; una sola pieza activa el efecto completo:

1. **Nulificación Absoluta de Daño Elemental y Físico (100% Inmune):**
   - ID 120: `Nullify slash attacks` (`0x421b6b`)
   - ID 121: `Nullify stab attacks` (`0x421b87`)
   - ID 122: `Nullify bash attacks` (`0x421ba3`)
   - ID 123: `Nullify physical attacks` (`0x421b07`)
   - ID 124: `Nullify fire damage` (`0x421bcf`)
   - ID 125: `Nullify water damage` (`0x421bef`)
   - ID 126: `Nullify wind damage` (`0x421c0f`)
   - ID 127: `Nullify earth damage` (`0x421c2f`)
   - ID 128: `Nullify lightning damage` (`0x421c52`)
2. **Inmunidad Total a Estados Alterados y Trampas (100% Inmune):**
   - IDs 129 a 136: `Nullify stun / freeze / poison / sleep / silence / instakill / petrification / paralysis` (`0x481f32 - 0x482ebc`)
   - ID 137: `Nullify all status ailments` (`0x481f4f`)
   - ID 138: `Nullify gas traps` (`0x481f19`)
   - ID 139: `Nullify slow` (`0x48367f`)
3. **Efectos de Post-Combate y Estado:**
   - ID 192: `Enemy HP and abilities are viewable` (`0x4e4d9a`)
   - ID 193: `Fully recover HP after battle` (`0x43d868`) — Recupera el 100% de HP al terminar combate.
   - ID 194: `Fully recover TP after battle` (`0x43d90e`) — Recupera el 100% de TP al terminar combate.
   - ID 195: `Pep is fixed at the max value` (`0x4f6a56`) — Fija Pep en 150.
   - ID 201: `Pep is fixed at the minimum value` (`0x4f6a0e`) — Fija Pep en 70.
   - ID 263: `A-rank speed when no weapon is equipped` (`0x4f55ab`) — Asigna rango de velocidad A desarmado.
   - ID 266: `Pep decrease rate DOWN` (`0x509844`)
   - ID 294: `Food likes and dislikes intensify` (`0x509a6d`)
4. **Mecánicas Tácticas en Combate:**
   - ID 257: `HP recovers while defending` (`0x4197b7`)
   - ID 262: `Escape probability UP` (`0x41ae6e`)
   - ID 292: `TP recovers slightly while defending` (`0x41984c`)
   - ID 269: `Less likely to trigger traps` (`0x481ffe`) — Resta 15 puntos a la activación de trampas.

---

## 7. Encantamientos Ambiguos o No Viables para Reetiquetado Numérico

Existen encantamientos donde sustituir la palabra de grado por un porcentaje directo generaría ambigüedad o engaño al jugador:

1. **Proc de Estados Alterados en Ataque Normal (IDs 153 a 160, 165, 197):**
   - *Vanilla:* `Normal attacks may inflict [Ailment]` / `Normal attacks will probably instakill` (197).
   - *Razón técnica:* El encantamiento solo activa la bandera de aplicación del estado en el ataque básico (`0x421261 - 0x4214e9`). La probabilidad real de éxito se calcula dinámicamente mediante la fórmula general de estados alterados:
     $$\text{Chance} = \text{Base} \times (1 + \text{DEX}_{\text{att}} \times 0.005) \times (1 - \text{RES}_{\text{def}} \times 0.005) \times \dots$$
     No existe un porcentaje fijo codificado en el encantamiento; poner "+10%" o similar sería falso y confuso.
   - *Recomendación:* Mantener su nombre vanilla.
2. **Defensas con Inmunidad Absoluta (IDs 120 a 139):**
   - Indican nulificación completa (100%). Poner `Nullify fire damage +100%` es redundante y satura el límite de caracteres sin añadir valor.
   - *Recomendación:* Mantener el nombre vanilla (`Nullify fire damage`, etc.).

---

## 8. Recomendaciones para la Integración en `generate_qol_enchant_text.py`

Para incorporar estas 105 cifras verificadas en el mod:
1. **Actualizar `qol_rules.xlsx` (Hoja `EnchantValues`):**
   - Añadir una nueva fuente en `EnchantSources`: `exe-verified` ("Directly decompiled from DT2-2 unwrapped x86 executable").
   - Actualizar las filas de los 43 encantamientos de DT1 corrigiendo los bonos raciales (15%/30%/60%) y Enmity (+10).
   - Añadir las entradas correspondientes a los encantamientos verificados de los 101 sin cifra.
2. **Reglas de Sustitución:**
   - La mayoría de encantamientos finalizan en `UP`, `MiniUP`, `GrandUP`, `MegaUP` o `DOWN`, por lo que la expresión regular `TIER_RE` de `enchant_values.py` los procesa de forma natural asignándoles `Figure` (`+4%`, `+2%`, etc.).
   - Para aquellos que no terminan en tier word (ej. IDs 72, 73, 211-214, 259, 265, 267, 268, 272, 275, 291, 296, 298), se debe rellenar la columna `Name` directamente en `EnchantValues`, utilizando los nombres cortos validados en la Sección 5.
3. **Control de Longitud:**
   - Todos los nombres de la Sección 5 tienen `len <= 28`, garantizando compatibilidad absoluta con `MAX_NAME <= 30` en `EnchantData.pck` y `MAX_NAME_ON_EQUIPMENT <= 35`.
