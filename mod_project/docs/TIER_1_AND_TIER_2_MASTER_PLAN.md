# Master Evaluation Plan: Tier 1 (Base) & Tier 2 (Intermediate) Classes

## 1. Executive Summary & Objectives
Este plan define la metodología técnica para auditar de forma autónoma y exhaustiva las **5 clases Base (Tier 1)** y las **11 clases Intermedias (Tier 2)** de *Dungeon Travelers 2-2*. El análisis se basa estrictamente en datos binarios (`dt2_data`, `SkillData.pck`, `ClassData.pck`), tablas de verdad (`vanilla_source_of_truth.xlsx`, `balance_changes.xlsx`) y simulaciones calibradas contra los jefes de historia y encuentros de mazmorra.

El objetivo es evaluar si alguna clase de juego temprano o medio presenta problemas de viabilidad, inanición de recursos, redundancia o trampas de diseño antes de llegar al Tier 3.

---

## 2. Universe of Classes Under Evaluation (16 Classes Total)

### A. Tier 1: Base Classes (Level 1–14)
1. **Fighter** (ID 0) — Tanque y atacante frontal; Provoke, War Cry, Raging Smash, maestrías de espada/hacha/lanza.
2. **Scout** (ID 6) — Agilidad y ataques a distancia; Shoot, Danger Shoot, Shadow Stitch, maestrías de arco/daga.
3. **Magic User** (ID 12) — Magia elemental y curación básica; Fireball, Ice Edge, Air Cutter, Stone Hammer, Thunderbolt, Heal, Poison.
4. **Maid** (ID 20) — Soporte y batería de TP; Cheer, Cook, Generous Heart, Maid Mastery, Cleanse.
5. **Spieler** (ID 26) — Suerte, daño híbrido y muñecas; Card Throw, Roulette Circus, Puppet, Escape.

### B. Tier 2: Intermediate Classes (Level 15–29)
* **Fighter Line**:
  6. **Paladin** (ID 1) — Tanque protector y sagrado; Cover, Parry, Auto-Guard, Defender, Shield Bash, Heal.
  7. **Berserker** (ID 2) — Atacante puro a dos manos; Berserk, Aura Eliminate, Frost Slash, Geo Break, Blood Rage.
* **Scout Line**:
  8. **Archer** (ID 7) — Atacante físico a distancia; Warning Shot, Spiral Arrow, Arrow Rain, Star Dust Arrow.
  9. **Assassin** (ID 8) — Agilidad, críticos y dagas; Shadow Clone, Assassinate, Sneak Attack, Poison Sting.
* **Magic User Line**:
  10. **Sorceress** (ID 13) — Magia de ataque por filas; Fire Blast, Ice Storm, Thunder Chain, Concentrate, Magic Mastery.
  11. **Enchantress** (ID 14) — Soporte de armas elementales; Fire/Water/Earth/Wind/Lightning Weapon, Disenchant, Element Guard.
  12. **Priestess** (ID 15) — Curandera y purificadora; Circle Heal, Nurse, Resurrection, Sun Veil, Holy Protection.
* **Maid Line**:
  13. **Bard** (ID 21) — Cantos de grupo y recuperación; Replenishing Carol, Joyful Aria, Magic Rondo, Echo.
  14. **Dancer** (ID 22) — Danzas de alteración de combate; Boogie Woogie, Samba, Mazurka, Polka, Waltz.
* **Spieler Line**:
  15. **Doll Master** (ID 27) — Invocadora de muñecas de ataque/apoyo; Doll Making, Spartan Doll, Golem Doll, Doll Heal.
  16. **Trickster** (ID 28) — Manipulación de azar y cartas; Trump Card, Deal, Shuffle, Poker Face, Lucky Seven.

---

## 3. The 6-Pillar Evaluation Framework

Cada una de las 16 clases será examinada a través de seis dimensiones cuantitativas y cualitativas:

| Pilar | Criterio de Evaluación | Fuentes de Datos |
| :--- | :--- | :--- |
| **1. Win Rate & Pacing** | Simulación empírica de combate frente a jefes canónicos y combates aleatorios (Vanilla vs Mod). | Simulador (`scenario.play`, 15 seeds por checkpoint). |
| **2. Class Identity & Niche** | Coherencia de su rol dentro del equipo y propuesta de valor único. | `CLASS_IDENTITY.md`, Japanese Atwiki (`dt2-2` p117–130). |
| **3. Toolbox & Skill Tree** | Eficiencia de habilidades activas y pasivas, progresión por nivel, costos de TP y SP. | `SkillLevels.pck`, `vanilla_source_of_truth.xlsx`. |
| **4. Equipment & Access** | Restricciones de equipo (acceso a escudos, armas 1H vs 2H, penalizaciones de velocidad). | `Equipment.pck`, `WeaponRanks`. |
| **5. Unique Synergies** | Sinergias con los personajes de la historia disponibles en ese momento del juego. | `UniqueSkills` de personajes que pueden tomar la clase. |
| **6. Criticisms & Verdict** | Quejas históricas de la comunidad (`balance_criteria.xlsx`), estado en el mod y veredicto final. | `balance_criteria.xlsx` (hojas `Criticisms`, `Levers`). |

---

## 4. Checkpoints de Prueba Seleccionados

### Tier 1 (Base Classes)
* **C03** (Nivel 5, Ruined Shrine Cave — Jefe *Aradia/Minotaur*): Test del equipo inicial de 3 miembros.
* **C05** (Nivel 6, Temple of Light — Jefe *Belphegor*): Desafío de curación y daño elemental básico.
* **C06** (Nivel 9, Holy Empire Borders — Jefe *Treant*): Techo del Tier 1 previo a la primera promoción.

### Tier 2 (Intermediate Classes)
* **C10** (Nivel 15, Abandoned Fortress — Jefe *Vampire Lady*): Puerta de entrada al Tier 2; primera prueba de los kits Lv15.
* **C13** (Nivel 18, Underground Tomb — Jefe *Dulahan*): Desafío físico y de control de estados.
* **C17** (Nivel 25, Subterranean Canal — Jefe *Kraken*): Pico de dificultad del juego medio (daño de área, disipación).
* **C18** (Nivel 27, Capital Sewers — Jefe *Hraesvelgr*): Último gran desafío antes de la transición a Tier 3.

---

## 5. Fases de Ejecución

1. **Fase 1: Extracción de Datos de Habilidades y Rango de Armas**: Compilar los árboles de habilidades de las 16 clases directamente desde el binario.
2. **Fase 2: Ejecución de Batería de Simulación**: Correr combates automáticos de 15 semillas por cada clase en sus checkpoints respectivos (Vanilla vs Mod).
3. **Fase 3: Diagnóstico de Clases y Toolboxes**: Evaluar quejas comunitarias, costos de TP, disponibilidad de equipo y sinergias de habilidades únicas.
4. **Fase 4: Generación del Reporte Maestro**: Crear el documento de auditoría final detallado con conclusiones y propuestas de intervención si fueran necesarias.
5. **Fase 5: Actualización de Documentos Markdown del Mod**: Actualizar `DIFFICULTY_CURVE.md`, `CLASS_STAGES.md` y otros documentos desactualizados, verificando que los 196 tests sigan pasando.
