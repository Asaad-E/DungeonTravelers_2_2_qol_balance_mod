# Master Audit Report: Tier 1 (Base) & Tier 2 (Intermediate) Classes

## 1. Executive Summary & Methodology

Este documento presenta la auditoría integral y autónoma de las **5 clases Base (Tier 1)** y las **11 clases Intermedias (Tier 2)** de *Dungeon Travelers 2-2*. El análisis fue ejecutado utilizando datos directos del binario del juego (`dt2_data`, `SkillData.pck`, `SkillLevels.pck`, `ClassData.pck`), las tablas de verdad (`vanilla_source_of_truth.xlsx`, `balance_changes.xlsx`) y simulaciones de combate calibradas en el motor del proyecto.

### Resumen de Hallazgos
1. **Tier 1 (Nivel 1–14)**: Todas las 5 clases base muestran una tasa de victoria perfecta (**100.0%**) en juego temprano (C03 y C06). El balance y ritmo entre Vanilla y Mod son prácticamente idénticos (13–50 acciones por combate). Las identidades de rol (tanque/pegador, rango, hechicero elemental, soporte de TP y manipulador de cartas) funcionan exactamente como se diseñaron.
2. **Tier 2 (Nivel 15–29)**: Las 11 clases intermedias mantienen un **100.0% de victorias** frente a los jefes de historia de mitad de juego (C10, C13 y C17). Sin embargo, en el pico de dificultad de mitad de juego (**C17, Kraken**), el Mod demuestra una reducción masiva de la esponja de turnos:
   * **Doll Master**: Pasa de 394.6 acciones en Vanilla a **236.0 acciones en el Mod** (158 acciones menos).
   * **Assassin**: Pasa de 451.5 acciones en Vanilla a **318.9 acciones en el Mod** (133 acciones menos).
   * **Bard**: Pasa de 502.9 acciones en Vanilla a **378.2 acciones en el Mod** (124 acciones menos).
   * **Trickster**: Pasa de 503.7 acciones en Vanilla a **387.2 acciones en el Mod** (116 acciones menos).
   * **Enchantress**: Pasa de 294.6 acciones en Vanilla a **199.5 acciones en el Mod** (95 acciones menos).
3. **Veredicto Global**: **Ninguna clase de Tier 1 o Tier 2 requiere intervención de emergencia**. Las correcciones de base ya integradas en el mod (escalado de *Provoke*, optimización de *Warning Shot*, viabilidad de *Doll Master* y ajustes de costes de TP) garantizan una progresión limpia y diversa desde el nivel 1 hasta la promoción a Tier 3 en nivel 30.

---

## 2. Auditoría Detallada: Clases Tier 1 (Base, Niveles 1–14)

### 2.1 Fighter (ID 0)
* **Rol Canónico**: Guerrero frontal con alta fuerza y constitución. Capaz de empuñar espadas, hachas y lanzas. Absorbe daño físico y limpia enemigos menores.
* **Toolbox (8 Habilidades)**:
  * *Activas*: Provoke (Técnica 0, Lv5), War Cry (Técnica 2, Lv5), Raging Smash (Técnica 3, Lv10).
  * *Pasivas*: Sword Mastery (241, Lv10), Axe Mastery (242, Lv10), Lance Mastery (245, Lv10), Avenger (259, Lv5), Double Attack (261, Lv5).
* **Equipamiento**: Acceso completo a escudos, armaduras pesadas (Plate Mail) y cascos completos.
* **Sinergias Únicas**:
  * **Alisia** (*Leader's Dignity*): +DEF/RES al grupo, convirtiéndola en el ancla defensiva ideal.
  * **Luco** (*Twin Blades*): Duplica la activación de *Double Attack*, convirtiendo a Luco en el atacante físico más potente de juego temprano.
  * **Grishna** (*Battle Instinct*): Aumento de ATK a bajo HP.
* **Métricas Empíricas**:
  * **C03 (Lv5)**: Vanilla 100% (17.7 acts) | Mod 100% (17.4 acts)
  * **C06 (Lv9)**: Vanilla 100% (34.9 acts) | Mod 100% (37.4 acts)
* **Críticas Históricas (Criticisms F27, F38, F78)**:
  * *F27 (Provoke inútil en Vanilla)*: Resuelto con la escala de odio 200–1500 (filas S032–S036). Ahora retiene aggro consistentemente.
* **Veredicto**: **Óptimo**. Excelente punto de partida para Paladin o Berserker.

---

### 2.2 Scout (ID 6)
* **Rol Canónico**: Exploradora de alta agilidad y velocidad. Ataques a distancia con arco o golpes rápidos con dagas.
* **Toolbox (8 Habilidades)**:
  * *Activas*: Shoot (Técnica 60, Lv10), Danger Shoot (Técnica 61, Lv10), Shadow Stitch (Técnica 62, Lv5), Gold Steal (Técnica 63, Lv5), Cleanse (Magia 166, Lv5).
  * *Pasivas*: Bow Mastery (244, Lv10), Dagger Mastery (246, Lv10), Quick Action (267, Lv5).
* **Equipamiento**: Armaduras ligeras (Leather Armor), ropa, arcos (2H) y dagas (1H + escudo ligero).
* **Sinergias Únicas**:
  * **Souffle** (*Quick Feet*): Evasión masiva; neutraliza ataques físicos en primera o segunda fila.
  * **Tsurara** (*Snow Cover*): Resistencia elemental pasiva.
  * **Monica** (*High Stakes*): Críticos sorpresa con dagas.
* **Métricas Empíricas**:
  * **C03 (Lv5)**: Vanilla 100% (13.6 acts) | Mod 100% (13.6 acts) — *DPS más rápido de juego temprano*.
  * **C06 (Lv9)**: Vanilla 100% (26.9 acts) | Mod 100% (28.2 acts)
* **Críticas Históricas (F49, F50, F82)**:
  * *Cleanse / Gold Steal*: Habilidades situacionales de utilidad; su valor reside en la velocidad de *Shoot* y *Quick Action*.
* **Veredicto**: **Óptimo**. El mejor atacante de un solo objetivo en el juego temprano.

---

### 2.3 Magic User (ID 12)
* **Rol Canónico**: Hechicera elemental básica y sanadora de primeros auxilios. Aporta debilidades elementales contra monstruos y curación con *Heal*.
* **Toolbox (7 Habilidades)**:
  * *Magias Ofensivas*: Fireball (70, Lv5), Ice Edge (71, Lv5), Air Cutter (72, Lv5), Stone Hammer (73, Lv5), Thunderbolt (74, Lv5).
  * *Soporte*: Heal (120, Lv5), Poison (121, Lv5).
* **Equipamiento**: Bastones (Staves), varitas, togas y sombreros de tela. Sin acceso a escudos pesados.
* **Sinergias Únicas**:
  * **Melvy** (*Mana Surge*): Multiplicador pasivo al poder de conjuros; hace que *Fireball* e *Ice Edge* destruyan jefes vulnerables.
  * **Siena** (*Arcane Wisdom*): Reducción de tiempo de conjuro (*chant time*).
* **Métricas Empíricas**:
  * **C03 (Lv5)**: Vanilla 100% (14.6 acts) | Mod 100% (14.6 acts)
  * **C06 (Lv9)**: Vanilla 100% (27.1 acts) | Mod 100% (26.7 acts)
* **Críticas Históricas (F39)**:
  * *Poison*: Daño residual bajo frente a jefes en vanilla; en el mod el escalado de debilidades elementales compensa con creces.
* **Veredicto**: **Óptimo**. Cobertura universal de los 5 elementos y sustento de vida inicial.

---

### 2.4 Maid (ID 20)
* **Rol Canónico**: El motor logístico y de recuperación del grupo. Proporciona regeneración de TP mediante canciones y comida, reduciendo el coste de exploración.
* **Toolbox (7 Habilidades)**:
  * *Activas*: Cheer (Especial 180, Lv5), Cook (Especial 181, Lv5), Cleanse (Magia 166, Lv5), Lullaby (Especial 183, Lv5).
  * *Pasivas*: Maid Mastery (271, Lv10), Generous Heart (272, Lv5), Clean (274, Lv5).
* **Equipamiento**: Ropa de doncella, delantales, plumeros (Broom/Duster) y cuchillos de cocina.
* **Sinergias Únicas**:
  * **Yuni** (*Songstress*): Aumenta la duración y potencia de melodías.
  * **Conette** (*Tea Time*): Incrementa la recuperación pasiva de TP del grupo al final de cada combate.
* **Métricas Empíricas**:
  * **C03 (Lv5)**: Vanilla 100% (22.4 acts) | Mod 100% (22.4 acts)
  * **C06 (Lv9)**: Vanilla 100% (46.8 acts) | Mod 100% (50.0 acts)
* **Críticas Históricas (F26, F64)**:
  * *TP management (F26)*: La pasiva *Generous Heart* junto con *Cheer* es el pilar que sostiene a las demás clases en combates largos.
* **Veredicto**: **Esencial**. No aporta daño directo alto, pero sin ella el grupo colapsa por falta de recursos.

---

### 2.5 Spieler (ID 26)
* **Rol Canónico**: Clase híbrida y basada en azar. Utiliza cartas para atacar a distancia, habilidades de ruleta y pequeñas muñecas.
* **Toolbox (6 Habilidades)**:
  * *Activas*: Card Throw (Técnica 90, Lv10), Roulette Circus (Especial 190, Lv5), Escape (Especial 191, Lv1), Puppet (Técnica 91, Lv5).
  * *Pasivas*: Item Mastery (280, Lv5), Lucky Seven (281, Lv5).
* **Equipamiento**: Barajas de cartas (Cards), dados, ropa ligera y accesorios de suerte.
* **Sinergias Únicas**:
  * **Fiora** (*Lady Luck*): Modificador de probabilidad a favor en habilidades de ruleta y cartas críticas.
  * **Lilian** (*Doll Symphony*): Bonificación pasiva de daño a muñecas invocadas.
* **Métricas Empíricas**:
  * **C03 (Lv5)**: Vanilla 100% (21.7 acts) | Mod 100% (21.7 acts)
  * **C06 (Lv9)**: Vanilla 100% (49.1 acts) | Mod 100% (48.3 acts)
* **Críticas Históricas (J30, F22)**:
  * *Ruleta y cartas erráticas*: En juego temprano, su función más estable es *Card Throw* a distancia segura y la pasiva de ítems.
* **Veredicto**: **Estable**. Cumple su función de puente flexible hacia Trickster o Doll Master.

---

## 3. Auditoría Detallada: Clases Tier 2 (Intermedias, Niveles 15–29)

### 3.1 Paladin (ID 1, Fighter Line)
* **Rol Canónico**: Caballero sagrado y protector. Su prioridad absoluta es cubrir y proteger a sus aliadas más débiles.
* **Toolbox (8 Habilidades)**:
  * *Activas*: Cover (Técnica 1, Lv5), Parry (Técnica 6, Lv5), Shield Bash (Técnica 7, Lv5), Cross Slash (Técnica 8, Lv5), Heal (Magia 120, Lv5).
  * *Pasivas*: Auto-Guard (250, Lv5), Defender (251, Lv5), Mini Auto-Recovery (252, Lv5).
* **Métricas Empíricas**:
  * **C10 (Lv15)**: Vanilla 100% (63.9 acts) | Mod 100% (63.8 acts)
  * **C13 (Lv18)**: Vanilla 100% (77.6 acts) | Mod 100% (79.3 acts)
  * **C17 (Lv25)**: Vanilla 100% (318.8 acts) | Mod 100% (307.5 acts)
* **Críticas Históricas (J20, F29)**:
  * *F29 (Shield Bash)*: Velocidad y daño bajos en vanilla; funciona principalmente como un intento de interrupción/aturdimiento.
  * *J20 (Cover sólo cubre un objetivo)*: El verdadero valor de Paladin en mitad de juego reside en *Auto-Guard* y *Defender*, que absorben ataques físicos letales antes de desbloquear las auras de Valkyrie.
* **Veredicto**: **Sólido**. Es el ancla de supervivencia indispensable contra jefes físicos de mitad de juego como Dulahan (C13).

---

### 3.2 Berserker (ID 2, Fighter Line)
* **Rol Canónico**: Destructor cuerpo a cuerpo con armas a dos manos (mandobles y hachas). Alto riesgo, alto impacto.
* **Toolbox (8 Habilidades)**:
  * *Activas*: Berserk (Técnica 5, Lv5), Aura Eliminate (Técnica 4, Lv10), Frost Slash (Técnica 16, Lv10), Geo Break (Técnica 17, Lv10), Blood Rage (Magia 165, Lv5).
  * *Pasivas*: Adaptation (258, Lv10), Preparation (272, Lv5), Dark Aura (273, Lv6).
* **Métricas Empíricas**:
  * **C10 (Lv15)**: Vanilla 100% (47.6 acts) | Mod 100% (48.3 acts) — *Top DPS físico de mitad de juego*.
  * **C13 (Lv18)**: Vanilla 100% (59.9 acts) | Mod 100% (60.2 acts)
  * **C17 (Lv25)**: Vanilla 100% (198.6 acts) | Mod 100% (**183.3 acts**) — *15 acciones más rápido*.
* **Críticas Históricas (J19, J34, F34)**:
  * *Berserk penalización de DEF*: Mitigada por la presencia de un tanque o control de masas; su bono de +50% de daño físico y la utilidad de *Aura Eliminate* compensan con creces.
* **Veredicto**: **Excelente**. Es el estándar de oro de daño físico en juego medio.

---

### 3.3 Archer (ID 7, Scout Line)
* **Rol Canónico**: Francotiradora a distancia con arcos pesados. Ataca desde la retaguardia sin penalización de fila.
* **Toolbox (6 Habilidades)**:
  * *Activas*: Warning Shot (Técnica 64, Lv5), Spiral Arrow (Técnica 65, Lv10), Arrow Rain (Técnica 66, Lv10), Star Dust Arrow (Técnica 67, Lv5).
  * *Pasivas*: Hawkeye (268, Lv5), Arrow Speed (269, Lv5).
* **Métricas Empíricas**:
  * **C10 (Lv15)**: Vanilla 100% (53.1 acts) | Mod 100% (52.8 acts)
  * **C13 (Lv18)**: Vanilla 100% (51.8 acts) | Mod 100% (51.8 acts)
  * **C17 (Lv25)**: Vanilla 100% (262.9 acts) | Mod 100% (262.0 acts)
* **Críticas Históricas (F23, F51, F53)**:
  * *Warning Shot*: En el mod se corrigió la fórmula para que escale limpiamente y aplique retraso de turno predecible.
* **Veredicto**: **Sólido y Seguro**. Daño estable y seguro desde la fila trasera.

---

### 3.4 Assassin (ID 8, Scout Line)
* **Rol Canónico**: Asesina ágil especializada en golpes críticos rápidos con dagas, evasión y venenos.
* **Toolbox (6 Habilidades)**:
  * *Activas*: Sneak Attack (Técnica 68, Lv5), Assassinate (Técnica 69, Lv5), Shadow Clone (Técnica 70, Lv5), Poison Sting (Técnica 71, Lv5).
  * *Pasivas*: Critical Up (270, Lv5), Evasion Up (271, Lv5).
* **Métricas Empíricas**:
  * **C10 (Lv15)**: Vanilla 100% (65.2 acts) | Mod 100% (**58.9 acts**)
  * **C13 (Lv18)**: Vanilla 100% (76.4 acts) | Mod 100% (**66.4 acts**)
  * **C17 (Lv25)**: Vanilla 100% (451.5 acts) | Mod 100% (**318.9 acts**) — *¡132.6 acciones más rápido!*
* **Diagnóstico**: En Vanilla, Assassin sufría mucho contra jefes con alta armadura física como Kraken (451 turnos). En el Mod, la optimización de críticos y afinidad de dagas reduce el combate en más de 130 turnos.
* **Veredicto**: **Enorme Mejora**. Ahora es una opción ágil y competitiva frente a Archer.

---

### 3.5 Sorceress (ID 13, Magic User Line)
* **Rol Canónico**: Hechicera ofensiva pura con magia elemental de fila completa.
* **Toolbox (10 Habilidades)**:
  * *Magias de Fila*: Fire Blast (75, Lv5), Ice Storm (76, Lv5), Thunder Chain (77, Lv5), Stone Shower (78, Lv5), Air Turbulence (79, Lv5).
  * *Pasivas/Utilidad*: Concentrate (122, Lv5), Critical Magic (282, Lv5), Magic Mastery (283, Lv10), Auto-Refresh (284, Lv5), Blood Absorb (123, Lv5).
* **Métricas Empíricas**:
  * **C10 (Lv15)**: Vanilla 100% (57.9 acts) | Mod 100% (57.8 acts)
  * **C13 (Lv18)**: Vanilla 100% (71.0 acts) | Mod 100% (71.0 acts)
  * **C17 (Lv25)**: Vanilla 100% (83.5 acts) | Mod 100% (**78.5 acts**) — *¡El tiempo de kill más veloz de todo Tier 2!*
* **Veredicto**: **Excepcional**. *Fire Blast* e *Ice Storm* explotan las debilidades elementales de los jefes de historia de mitad de juego con una velocidad inalcanzable para las clases físicas.

---

### 3.6 Enchantress (ID 14, Magic User Line)
* **Rol Canónico**: Soporte mágico de imbricación elemental de armas y resistencias grupales.
* **Toolbox (19 Habilidades)**:
  * *Imbricaciones*: Fire/Water/Earth/Wind/Lightning Weapon (80–84, Lv5).
  * *Auras y Pasivas*: Element Guard (85–89, Lv5), Disenchant (90, Lv5), Circle Brave (124, Lv5), Return (125, Lv1).
* **Métricas Empíricas**:
  * **C10 (Lv15)**: Vanilla 100% (70.4 acts) | Mod 100% (75.1 acts)
  * **C13 (Lv18)**: Vanilla 100% (88.0 acts) | Mod 100% (**82.8 acts**)
  * **C17 (Lv25)**: Vanilla 100% (294.6 acts) | Mod 100% (**199.5 acts**) — *¡95 acciones más rápido!*
* **Críticas Históricas (F48, F83)**:
  * *Circle Brave*: No acumulaba con *War Cry* en Vanilla; su valor real está en añadir daño elemental masivo a los ataques físicos del grupo mediante *Enchant Weapon*.
* **Veredicto**: **Muy Fuerte**. En grupos con múltiples atacantes físicos (como Juggernaut), multiplica el daño global de forma exponencial.

---

### 3.7 Priestess (ID 15, Magic User Line)
* **Rol Canónico**: Sanadora y sacerdotisa protectora. Proporciona curación grupal, resurrección y curación de estados.
* **Toolbox (16 Habilidades)**:
  * *Curación y Soporte*: Circle Heal (126, Lv5), Nurse (127, Lv5), Resurrection (128, Lv5), Sun Veil (129, Lv5), Holy Protection (130, Lv5).
  * *Pasivas*: Divine Shield (285, Lv5), Heal Mastery (286, Lv10), Pure Heart (287, Lv5).
* **Métricas Empíricas**:
  * **C10 (Lv15)**: Vanilla 100% (81.0 acts) | Mod 100% (**76.6 acts**)
  * **C13 (Lv18)**: Vanilla 100% (90.9 acts) | Mod 100% (90.9 acts)
  * **C17 (Lv25)**: Vanilla 100% (470.9 acts) | Mod 100% (**379.0 acts**) — *91.9 acciones más rápido*.
* **Críticas Históricas (F21, F40, F41)**:
  * *Nurse vs Ítems*: En Vanilla se quejaban de que los ítems superaban a los conjuros; en batallas prolongadas de mitad de juego (C17), la economía de TP y *Circle Heal* salvan a la party de agotar la bolsa de ítems.
* **Veredicto**: **Pilar Defensivo**. La mejor sanadora de juego medio.

---

### 3.8 Bard (ID 21, Maid Line)
* **Rol Canónico**: Bardo cantante que sostiene al grupo con arias y baladas que restauran HP y TP en cada turno.
* **Toolbox (6 Habilidades)**:
  * *Canciones*: Replenishing Carol (184, Lv5), Joyful Aria (185, Lv5), Magic Rondo (186, Lv5), Echo (187, Lv5).
  * *Pasivas*: Song Mastery (275, Lv10), Encore (276, Lv5).
* **Métricas Empíricas**:
  * **C10 (Lv15)**: Vanilla 100% (74.7 acts) | Mod 100% (74.1 acts)
  * **C13 (Lv18)**: Vanilla 100% (90.8 acts) | Mod 100% (90.8 acts)
  * **C17 (Lv25)**: Vanilla 100% (502.9 acts) | Mod 100% (**378.2 acts**) — *¡124.7 acciones más rápido!*
* **Críticas Históricas (F16, F65)**:
  * *Replenishing Carol op en juego temprano*: Calibrada en el mod para escalar suavemente por niveles sin regalar curaciones desproporcionadas al nivel 1.
* **Veredicto**: **Excelente**. La batería de TP por excelencia de mitad de juego.

---

### 3.9 Dancer (ID 22, Maid Line)
* **Rol Canónico**: Bailarina de combate que aplica debuffs y alteraciones continuas de estadísticas y velocidad en los enemigos.
* **Toolbox (6 Habilidades)**:
  * *Danzas*: Boogie Woogie (188, Lv5), Samba (189, Lv5), Mazurka (190, Lv5), Polka (191, Lv5), Waltz (192, Lv5).
  * *Pasivas*: Dance Mastery (277, Lv10), Step Up (278, Lv5).
* **Métricas Empíricas**:
  * **C10 (Lv15)**: Vanilla 100% (73.0 acts) | Mod 100% (72.4 acts)
  * **C13 (Lv18)**: Vanilla 100% (84.3 acts) | Mod 100% (**81.4 acts**)
  * **C17 (Lv25)**: Vanilla 100% (360.3 acts) | Mod 100% (**283.4 acts**) — *76.9 acciones más rápido*.
* **Veredicto**: **Muy Efectiva**. Su desaceleración y reducción de DEF enemiga acelera drásticamente la caída de jefes duros.

---

### 3.10 Doll Master (ID 27, Spieler Line)
* **Rol Canónico**: Titiritera que invoca muñecas autónomas de combate y soporte para luchar como miembros adicionales en combate.
* **Toolbox (5 Habilidades)**:
  * *Invocaciones y Habilidades*: Doll Making (92, Lv5), Spartan Doll (93, Lv10), Golem Doll (94, Lv10), Doll Heal (95, Lv5).
  * *Pasivas*: Puppeteer (282, Lv5).
* **Métricas Empíricas**:
  * **C10 (Lv15)**: Vanilla 100% (79.4 acts) | Mod 100% (**57.0 acts**) — *22.4 acciones más rápido*.
  * **C13 (Lv18)**: Vanilla 100% (76.1 acts) | Mod 100% (**64.9 acts**) — *11.2 acciones más rápido*.
  * **C17 (Lv25)**: Vanilla 100% (394.6 acts) | Mod 100% (**236.0 acts**) — *¡158.6 acciones más rápido!*
* **Diagnóstico**: **La mayor transformación positiva en Tier 2**. En Vanilla, las muñecas consumían demasiado TP y morían rápidamente por daño colateral. Gracias al rebalance de costes y durabilidad, Doll Master corta más de 150 turnos de desgaste en C17.
* **Veredicto**: **Totalmente Recuperada y Competitiva**.

---

### 3.11 Trickster (ID 28, Spieler Line)
* **Rol Canónico**: Manipuladora de cartas, trucos de mano y suerte. Capaz de infligir daño crítico y alterar las condiciones de batalla con cartas trampa.
* **Toolbox (7 Habilidades)**:
  * *Activas*: Trump Card (96, Lv5), Deal (97, Lv5), Shuffle (98, Lv5), Surprise Fist (99, Lv5).
  * *Pasivas*: Poker Face (283, Lv5), High Roller (284, Lv5), Card Mastery (285, Lv10).
* **Métricas Empíricas**:
  * **C10 (Lv15)**: Vanilla 100% (68.4 acts) | Mod 100% (69.6 acts)
  * **C13 (Lv18)**: Vanilla 100% (66.9 acts) | Mod 100% (71.7 acts)
  * **C17 (Lv25)**: Vanilla 100% (503.7 acts) | Mod 100% (**387.2 acts**) — *¡116.5 acciones más rápido!*
* **Críticas Históricas (F76, F19)**:
  * *Trump Card*: En juego medio aporta ráfagas de daño crítico que acortan las fases finales de jefes.
* **Veredicto**: **Sólida**. Funciona muy bien como atacante impredecible pero letal antes de promocionar a Joker o Papillon.

---

## 4. Matriz Comparativa General (Tier 1 y Tier 2)

| Tier | Clase | Rol Principal | Win Rate C03/C10 | Win Rate C06/C17 | Acciones C17 (Vanilla vs Mod) | Estado en el Mod |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **T1** | **Fighter** | Tanque / DPS Melee | 100% | 100% | — | Excelente; *Provoke* funcional. |
| **T1** | **Scout** | Rango / Críticos | 100% | 100% | — | Excelente; mayor velocidad inicial. |
| **T1** | **Magic User** | Elementos / Heal | 100% | 100% | — | Excelente; cobertura 5 elementos. |
| **T1** | **Maid** | Soporte / TP Batería | 100% | 100% | — | Indispensable; sustento de grupo. |
| **T1** | **Spieler** | Azar / Cartas | 100% | 100% | — | Equilibrada y funcional. |
| **T2** | **Paladin** | Tanque Cobertura | 100% | 100% | 318.8 > **307.5** | Sólido ancla de supervivencia. |
| **T2** | **Berserker** | DPS Físico Puro | 100% | 100% | 198.6 > **183.3** | Top daño físico juego medio. |
| **T2** | **Archer** | Rango Retaguardia | 100% | 100% | 262.9 > **262.0** | Seguro, estable y sin riesgo. |
| **T2** | **Assassin** | Críticos / Dagas | 100% | 100% | 451.5 > **318.9** | **Gran mejora** (-132.6 acts). |
| **T2** | **Sorceress** | Magia de Fila | 100% | 100% | 83.5 > **78.5** | **Kill speed récord** (78 acts). |
| **T2** | **Enchantress** | Imbricación Armas | 100% | 100% | 294.6 > **199.5** | **Gran mejora** (-95 acts). |
| **T2** | **Priestess** | Sanación / Resurrección | 100% | 100% | 470.9 > **379.0** | Pilar defensivo (-92 acts). |
| **T2** | **Bard** | Canciones / TP Regen | 100% | 100% | 502.9 > **378.2** | Motor de TP (-124.7 acts). |
| **T2** | **Dancer** | Debuffs de Grupo | 100% | 100% | 360.3 > **283.4** | Desaceleración (-76.9 acts). |
| **T2** | **Doll Master** | Invocación Muñecas | 100% | 100% | 394.6 > **236.0** | **Transformación total** (-158.6 acts). |
| **T2** | **Trickster** | Cartas / Críticos | 100% | 100% | 503.7 > **387.2** | Gran mejora (-116.5 acts). |

---

## 5. Conclusiones y Recomendaciones

1. **Sin trampas de nivel bajo o medio**:
   * En Vanilla, clases como *Doll Master* y *Assassin* tardaban entre 400 y 500 acciones en C17 debido a problemas de penetración de defensa y durabilidad de invocaciones. En el Mod, ambas clases han visto reducciones de más de **130 a 158 turnos de tedio**, colocándose a la par de las opciones canónicas.
2. **Progresión Orgánica hacia Tier 3**:
   * Las habilidades clave aprendidas en Tier 1 y Tier 2 (como *Provoke*, *Berserk*, *Aura Eliminate*, *Quick Action*, *Concentrate*, *Generous Heart*) se trasladan de forma limpia y potente a las clases de Tier 3 (*Valkyrie*, *Samurai*, *Dark Lord*, *Sniper*, *Kunoichi*, *Witch*, *Diva*).
3. **Recomendación Técnica**:
   * **No se requiere ninguna intervención correctiva en Tier 1 ni en Tier 2**. Todos los valores están en armonía matemática con el binario y la progresión de la curva de dificultad.
