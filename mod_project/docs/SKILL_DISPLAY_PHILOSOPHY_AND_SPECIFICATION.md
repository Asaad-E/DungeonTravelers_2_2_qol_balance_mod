# Dungeon Travelers 2-2: Filosofía y Especificación de Presentación de Habilidades

Este documento define la **filosofía de diseño**, los **principios de legibilidad** y la **especificación técnica estricta** acordada para la presentación de habilidades en *Dungeon Travelers 2-2*. Sirve como estándar unificado y guía definitiva tanto para la edición manual como para cualquier script de automatización del mod.

---

## 1. Filosofía de Diseño: Los Principios Rectores

### Principio 1: Cero "Fricción de Calculadora" (El Síndrome de la Hoja de Excel)
* **La Regla de Oro:** *Un jugador en mitad de una mazmorra no debe verse obligado a jugar con una calculadora al lado.*
* **El Problema:** Expresiones estadísticas abstractas como `(avg +3.33%/Lv)` o fórmulas crípticas con abreviaciones condensadas saturan la mente del jugador y rompen la inmersión. 
* **La Solución:** El jugador debe poder consultar el menú, mirar la habilidad y entender **en medio segundo**:
  1. ¿Cuánto hace la habilidad ahora mismo?
  2. ¿Cuánto ganará si gasta 1 SP en el siguiente nivel?
  3. ¿Cuánto maná (TP) le va a costar usarla?

---

### Principio 2: Preservación del Alma y Nomenclatura Original (Línea 1 Intacta)
* **La Regla de Oro:** *El texto de los desarrolladores originales de Aquaplus/Sting se respeta al 100%.*
* **Implementación:** La **Línea 1** de cada recuadro de habilidad debe conservar la descripción original en inglés sin alteraciones, sin recortes y sin añadir notas de desarrollo. 
* **Justificación:** Mantiene la atmósfera del juego original intacta y evita que el mod se sienta como un producto tosco o no oficial.

---

### Principio 3: Respuesta a la Limitación del Motor (Texto Estático Único)
* **La Limitación Técnica:** El motor de *Dungeon Travelers 2-2* no dispone de textos dinámicos por nivel. Lee una única cadena fija para toda la habilidad tanto en la pantalla de aprendizaje como en combate.
* **El Dilema:** Si solo se mostrara el valor del nivel 1, el jugador a nivel 8 no sabría qué hace su técnica. Si solo se mostrara el nivel máximo, un jugador a nivel 1 no sabría qué tiene en ese momento.
* **La Solución Acordada:** Mostrar la progresión directa secuencial mediante flechas (`->`) para que el jugador identifique de inmediato su nivel actual y el salto al siguiente nivel.

---

### Principio 4: Verdad Binaria Absoluta (Anti-Placebo)
* **La Regla de Oro:** *Cada cifra mostrada debe existir realmente en el binario del juego.*
* **Lección Aprendida:** Jamás se deben escribir en el texto mecánicas que el motor no ejecuta (por ejemplo, afirmar que una magia tiene *"penetración elemental 50"* o que una técnica otorga *"inmunidad a críticos"* cuando el código binario no tiene esa función). Si el motor no lo hace, no se pone en el texto.

---

### Principio 5: Restricciones Físicas Infranqueables del Motor Gráfico
Para garantizar que el juego jamás sufra desbordamientos de interfaz ni textos cortados:
1. **Límite de Líneas:** Máximo **3 líneas** por caja de texto (Línea 1: Descripción vanilla; Línea 2: Efecto y escalado; Línea 3: Costes y turnos).
2. **Límite de Longitud:** Máximo **85 caracteres por línea** (medido píxel a píxel sobre la caja de diálogo de la interfaz en inglés).
3. **Seguridad de Fuentes:** **Cero tildes (`~`)**. La fuente original de DT2-2 en inglés tiene caracteres reservados y el uso de la tilde provoca glitcheos y caracteres corruptos. En su lugar se utilizan flechas (`->`) o guiones (`-`).

---

## 2. Especificación Técnica de Formato

### Estructura Estándar de 3 Líneas

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [Línea 1] Vanilla Description (Intacta de fábrica)                                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [Línea 2] Efecto Principal: [Valor L1] -> [L2] -> [L3] -> [L4] -> [Valor Máx]          │
│ [Línea 3] Turns: [L1] -> [Máx] | TP Cost: [L1] -> [L2] -> [L3] -> [Máx] | Speed: [X]  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Reglas de Presentación para 5 Niveles vs. 10 Niveles

#### A. Habilidades de 5 Niveles (Buffs, Pasivas y Técnicas intermedias)
Dado que tienen pocos niveles, **siempre se escriben todos los números explícitos** separados por flechas:
* `ATK: +8% -> +10% -> +12% -> +14% -> +18% (L1-5 Max)`
* `Turns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 5 -> 7 -> 9 -> 11 -> 13`

#### B. Habilidades de 10 Niveles (Ataques físicos principales y Hechizos)
1. **Caso 1 (Caben los 10 valores en $\le 85$ caracteres):** Se escriben los 10 valores completos:
   * `TP Cost: 5 -> 8 -> 11 -> 14 -> 17 -> 20 -> 22 -> 24 -> 26 -> 28`
   * `Pwr: 70 -> 105 -> 140 -> 175 -> 220 -> 270 -> 320 -> 380 -> 450 -> 520`
2. **Caso 2 (No caben los 10 valores por cifras largas):** Se utiliza la notación de incremento exacto por nivel indicando claramente el valor base, el paso y el tope máximo:
   * **CORRECTO:** `ATK: 125% (+8%/Lv) -> 200% (L10 Max) | Hit Rate: +20% (+2%/Lv)`
   * **PROHIBIDO:** `ATK: 80% -> 110% (avg +3.33%/Lv, L1-10)` *(Los promedios confusos están estrictamente vetados).*

---

## 3. Muestrario de Referencia por Clase (Los Mockups Aprobados)

### 1. ⚔️ Fighter: `War Cry` (Buff Grupal de 5 Niveles)
```text
Raise the party's ATK.
ATK: +8% -> +10% -> +12% -> +14% -> +18% (L1-5 Max)
Turns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 5 -> 7 -> 9 -> 11 -> 13
```
* **Lectura al instante:** Sabes que en Lv 1 da +8% ATK por 4 turnos (5 TP), y en Lv 2 pasa a +10% ATK por 5 turnos (7 TP).

### 2. ⚔️ Fighter: `Raging Smash` (Ataque Físico de 10 Niveles)
```text
Short-range skill. Powerful strike to one enemy.
ATK: 125% -> 133 -> 141 -> 150 -> 158 -> 166 -> 175 -> 183 -> 191 -> 200%
TP Cost: 5 -> 8 -> 11 -> 14 -> 17 -> 20 -> 22 -> 24 -> 26 -> 28 | Speed: 0.8x -> 0.9x
```
* **Lectura al instante:** Ves cada incremento de daño y cada salto de coste de TP sin calcular nada.

### 3. 🔮 Magic User: `Fireball` (Magia Elemental de 10 Niveles)
```text
Deal fire damage to one enemy.
Pwr: 70 -> 105 -> 140 -> 175 -> 220 -> 270 -> 320 -> 380 -> 450 -> 520 (L10)
TP Cost: 5 -> 7 -> 9 -> 11 -> 14 -> 17 -> 20 -> 24 -> 28 -> 32 (Max)
```
* **Lectura al instante:** El poder base real del motor se visualiza escalón por escalón.

### 4. 🏹 Scout: `Evade` (Buff Personal de Evasión)
```text
Increase own physical evasion rate.
EVA: +15% -> +20% -> +25% -> +30% -> +35% (L1-5 Max)
Turns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 4 -> 6 -> 8 -> 10 -> 12
```

### 5. ☕ Maid: `First Aid` (Curación Porcentual)
```text
Heal one ally's HP.
Heal: 12% Max HP -> 15% -> 18% -> 21% -> 25% (L1-5 Max)
TP Cost: 2 -> 4 -> 6 -> 8 -> 10 | Affected by Maid Mastery
```

### 6. 🎲 Spieler: `Coffee Break` (Recuperación y Turnos Rápidos)
```text
Take a break to heal own HP and raise Pep. Fast turn recovery.
Heal: 20% Max HP -> 25% -> 30% -> 35% -> 40% (L1-5 Max)
TP Cost: 6 -> 7 -> 8 -> 9 -> 10 | Action delay: 1.50x
```

### 7. 🔵 Pasiva: `Sword Mastery`
```text
Increases equipped sword base ATK.
ATK: +3% (L1) -> +5% -> +7% -> +9% -> +11% -> +12% -> +13% -> +14% -> +15% (L10)
```

---

## 4. Comparativa: Lo Aprobado vs. El Enfoque del Script Automatizado

| Aspecto | Formato Aprobado por el Usuario | Formato Automatizado (`qol_skill_text.xlsx`) |
| :--- | :--- | :--- |
| **Escalado no lineal** | Progresión directa nivel por nivel (`70 -> 105 -> 140...`) | Promedios matemáticos comprimidos (`avg +3.33%/Lv`) |
| **Experiencia de usuario** | Inmediata y cómoda; no requiere pensar | Mentalmente agotadora; obliga a calcular aumentos |
| **Línea 1** | 100% Original del juego | 100% Original del juego |
| **Separadores** | Flechas limpias `->` con saltos de línea ordenados | Barras verticales saturadas `\|` en bloque denso |
| **Límite de caracteres** | $\le 85$ caracteres estrictos | $\le 85$ caracteres estrictos |
| **Tildes** | 0 tildes (`~`) | 0 tildes (`~`) |

---

## 5. Directriz para el Futuro del Proyecto

1. **Si el mod es una versión QoL (Solo Transparencia):**
   * Se toman los números **reales extraídos del binario original** (`vanilla_source_of_truth.xlsx`).
   * Se formatea el texto utilizando **exclusivamente el estándar de este documento** (flechas directas, sin fórmulas `avg`).
2. **Si el mod es una versión Balance:**
   * Primero se parchean los structs y bytes en el archivo `.pck` de destino.
   * Luego se escribe en el Excel el texto que refleje con total fidelidad esos nuevos números modificados.
   * Nunca jamás se escribe en el texto un número que el motor no tenga en su código.
