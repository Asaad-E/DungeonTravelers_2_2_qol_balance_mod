# Plan de Expansión de Mecánicas Avanzadas
## Dungeon Travelers 2-2: The Fallen Maidens & the Book of Beginnings

Este documento detalla las mecánicas profundas y sistemas del juego que carecen de claridad en el juego base y el plan para hacerlas 100% transparentes e integradas.

---

### 1. Sistema de Reclassing y Reseteo de Nivel (Level Reset / Reclass)
* **El Problema Original:**
  El juego permite cambiar de clase y resetear a niveles clave (Lv 1, 15, 30, 50), pero nunca explica con exactitud cuántos puntos de estadística permanente (`Bonus Stat Points`) otorga cada reseteo ni cómo se acumulan hasta el límite máximo.
* **Solución de Transparencia:**
  - Integrar la tabla exacta de bonificación en la lección `CheatsTeaching_18.adv.bin` (Level Resetting):
    - Reset en Lv 30: +X puntos base.
    - Reset en Lv 50: +Y puntos base.
    - Reset en Lv 99: Bonificación máxima de atributos.
  - Documentar en los textos de selección de clase los requisitos exactos y las ramas permitidas para evitar elecciones irreversibles erróneas.

---

### 2. Libros de Gran Sello (Grand Sealbooks)
* **El Problema Original:**
  Los sellos de jefes (Grand Seals) otorgan auras globales al grupo, pero sus descripciones son ambiguas respecto a los multiplicadores reales (aumento de EXP, tasa de caída de ítems, regeneración de TP, mitigación elemental).
* **Solución:**
  - Editar `SealScrollData.pck` para detallar:
    - *Ghast:* +20% EXP grupal.
    - *Eros:* Regeneración pasiva de 3% TP por turno.
    - *Deep Slapyon:* Mitigación de 25% de daño de agua y hielo.

---

### 3. Sistema de Coronas (Crowns & Mastery)
* **El Problema Original:**
  Las coronas son el pináculo de la progresión de cada heroína, pero el juego no aclara qué estadísticas incrementa cada corona ni sus sinergias con habilidades únicas.
* **Solución:**
  - Expandir `CheatsTeaching_25.adv.bin` (Crowns) explicando el incremento porcentual a los atributos base y el impacto en la tasa de críticos y resistencia a estados.

---

### 4. Habilidades Conjuntas (Joint Skills)
* **El Problema Original:**
  Las habilidades conjuntas (`JoinSkillData.pck`) requieren combinaciones específicas de clases o posiciones (vanguardia/retaguardia) que el jugador desconoce hasta que casualmente las desbloquea.
* **Solución:**
  - Modificar `JoinSkillData.pck` indicando exactamente los requisitos en la descripción (ej: *"Requiere 3 miembros en primera línea con armas cortas"* o *"Requiere Paladín + Curandera"*).

---

### 5. Zonas Elementales y Dominancia de Terreno
* **El Problema Original:**
  Las zonas de mazmorra potencian o anulan magias, pero no se detallan los multiplicadores reales (+50% daño de fuego en zona ígnea, -50% al opuesto).
* **Solución:**
  - Actualizar `CheatsTeaching_20.adv.bin` (Zones) con las cifras matemáticas reales de bono y penalización por afinidad elemental.

---

### 6. Forja y Sellado de Equipo (Blacksmith / Enchants)
* **El Problema Original:**
  El herrero (`ShopBlacksmith.pck` y `EnchantData.pck`) no aclara los límites de encantamiento ni cómo se calculan las probabilidades de infligir estados alterados al engarzar sellos de monstruos.
* **Solución:**
  - Documentar en los diálogos del herrero y en las descripciones de sellos la probabilidad real de activación (+10% sueño, +15% veneno) y las reglas de compatibilidad de ranuras.
