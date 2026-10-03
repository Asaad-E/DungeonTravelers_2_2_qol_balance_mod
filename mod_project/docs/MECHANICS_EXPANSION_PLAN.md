# Plan de Expansión de Mecánicas Avanzadas
## Dungeon Travelers 2-2: The Fallen Maidens & the Book of Beginnings

Este documento detalla el análisis técnico y el plan de implementación para las mecánicas profundas del juego que carecen de transparencia en el juego base.

---

### 1. Sistema de Reseteo de Nivel y Reclassing (Level Resetting)
* **Archivos Binarios Implicados:**
  - `Teaching.pck` -> `CheatsTeaching_18.adv.bin` (Tutorial general en Base)
  - `Lesson.pck` -> `BattleTeacher_Sp03.adv.bin` (Lección especial de Instructor)
  - `ClassData.pck` y `ClassLevelData.pck` (Requisitos de nivel y ramas de clase)
* **Diagnóstico Técnico:**
  El juego permite resetear de nivel para reasignar puntos o cambiar de clase. Sin embargo, no documenta la fórmula matemática de ganancia de estadísticas permanentes (`Bonus Stats`).
* **Datos Matemáticos Extraídos de las Guías:**
  - Solo se obtienen puntos de estadísticas permanentes si la brecha entre el nivel anterior y el nivel al que se resetea es **$\ge 59$ niveles**.
  - A brecha $\ge 59$: Todas las estadísticas base aumentan en **+1**.
  - Cada umbral de 10 niveles adicionales ($\ge 69$, $\ge 79$, $\ge 89$, $\ge 99$): Otorga un bono acumulativo adicional (+1 a todos los atributos y resistencias).
  - Límite máximo acumulativo: Bono total de atributos base que culmina en el estado de **Corona (Crown)**.
* **Plan de Implementación:**
  - Inyectar en `CheatsTeaching_18.adv.bin` la tabla exacta de bonos por brecha de nivel.
  - Documentar en la interfaz de selección de clase (`ClassData.pck`) las transiciones válidas para evitar reseteos accidentales.

---

### 2. Libros de Gran Sello (Grand Sealbooks)
* **Archivos Binarios Implicados:**
  - `Parameter/SealScrollData.pck` (35 sellos mutantes de jefes)
  - Interfaz de Libra (ranura de Gran Sello)
* **Diagnóstico Técnico:**
  Los 35 Grandes Sellos actualmente tienen una descripción genérica idéntica:
  `"Grand Sealbook created from a mutant's spirit."`
  No informan qué aura grupal otorgan ni sus multiplicadores.
* **Datos Matemáticos Extraídos (`Data/Grand Sealbooks.mhtml`):**
  - **Ghast:** +20% EXP grupal en batalla.
  - **Eros:** Regeneración pasiva de 3% TP por turno para todo el grupo.
  - **Deep Slapyon:** -25% de daño recibido de afinidad Agua e Hielo.
  - **Overdue:** +15% velocidad de acción (AGI) a toda la retaguardia.
  - **Scanner:** +30% probabilidad de revelar debilidades de enemigos automáticamente.
  - **Kaguya:** +25% daño de ataques físicos y técnicas en luna llena.
* **Plan de Implementación:**
  - Crear tabla Excel `mod_project/data_tables/grand_seals.xlsx` con los 35 sellos de mutantes.
  - Extender `apply_mod.py` para compilar las 35 descripciones directas en `SealScrollData.pck`.

---

### 3. Sistema de Coronas y Habilidad EX (Crowns & EX Skills)
* **Archivos Binarios Implicados:**
  - `Teaching.pck` -> `CheatsTeaching_25.adv.bin`
  - `Lesson.pck` -> `BattleTeacher_Sp03.adv.bin`
  - `UniqueSkillData.pck` (Habilidades Únicas)
* **Diagnóstico Técnico:**
  La Corona es el nivel maestro final de cada heroína. Eleva la habilidad única a **Nivel EX**, independientemente del nivel actual del personaje.
* **Plan de Implementación:**
  - Describir en `CheatsTeaching_25.adv.bin` el multiplicador exacto de la habilidad única en nivel EX (+50% respecto a Lv 9) y el tope de estadísticas de la corona.
  - Agregar en `UniqueSkillData.pck` una nota sobre la mejora al alcanzar el rango EX.

---

### 4. Habilidades Conjuntas (Joint Skills)
* **Archivos Binarios Implicados:**
  - `Parameter/JoinSkillData.pck` (52 habilidades conjuntas)
  - `Teaching.pck` -> `CheatsTeaching_17.adv.bin`
* **Diagnóstico Técnico:**
  Las habilidades conjuntas requieren condiciones estrictas:
  1. Turnos consecutivos en el orden de acción.
  2. Coste de TP individual en cada miembro participante.
  3. Nivel de Pep (ánimo) requerido.
  4. Formación específica (ej. 3 miembros en primera línea) o combinaciones de clases/armas.
  Actualmente, las 52 habilidades solo describen el ataque pero ocultan los requisitos de formación.
* **Plan de Implementación:**
  - Crear `mod_project/data_tables/joint_skills.xlsx`.
  - Inyectar en cada una de las 52 entradas de `JoinSkillData.pck` la línea de requisitos previa al efecto:
    Ejemplo: `[Req: 3 Front-row with Short/1H weapons] | Deal heavy physical damage to an enemy row.`

---

### 5. Zonas de Mazmorra (Elemental & Boost Zones)
* **Archivos Binarios Implicados:**
  - `Teaching.pck` -> `CheatsTeaching_20.adv.bin`
* **Diagnóstico Técnico:**
  Las zonas potencian o anulan magia, pero el tutorial dice vagamente *"aumenta considerablemente"*.
* **Datos Matemáticos Extraídos:**
  - Zona Elemental: **+50% de daño** al elemento potenciado, **-50% de daño** al elemento opuesto.
  - Zona Anti-Magia: Anula 100% de magias (a excepción de las muñecas de Doll Master).
  - Zonas de Impulso (Boost Zones): **+25% a la estadística correspondiente** (ATK, DEF, M.ATK, M.DEF).
* **Plan de Implementación:**
  - Actualizar `CheatsTeaching_20.adv.bin` con los porcentajes reales (+50% / -50% / +25%).

---

### 6. Sistema de Herrero y Encantamientos (Blacksmith & Enchants)
* **Archivos Binarios Implicados:**
  - `Parameter/EnchantData.pck` (280 tipos de encantamiento)
  - `Parameter/EquipmentData.pck` (551 armas y armaduras)
* **Diagnóstico Técnico:**
  Al forjar o engarzar sellos en el herrero, el juego no muestra las probabilidades de activación de estados alterados (+10% Sueño, +15% Veneno).
* **Plan de Implementación:**
  - Actualizar `equipment.xlsx` con los efectos ocultos de armas legendarias y accesorios.
  - Documentar en los textos de `EnchantData.pck` las tasas numéricas de cada prefijo/sufijo forjado.
