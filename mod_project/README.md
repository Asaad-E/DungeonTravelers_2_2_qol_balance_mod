# Dungeon Travelers 2-2: Mechanics Transparency & QoL Mod Project

Proyecto integral de Calidad de Vida (QoL) y Transparencia de Mecánicas para *Dungeon Travelers 2-2: The Fallen Maidens & the Book of Beginnings* (PC).

---

## 📁 Estructura del Proyecto

```text
DungeonTraveler2-2/
├── mod_project/
│   ├── backups/                 <- Copias originales limpias de todos los archivos .pck
│   ├── data_tables/             <- Tablas Excel para edición rápida y directa
│   │   ├── skills.xlsx          <- 330 habilidades con descripciones y escalas por nivel
│   │   ├── items.xlsx           <- 576 consumibles con curación exacta y efectos
│   │   └── equipment.xlsx       <- 551 armas, armaduras y accesorios
│   ├── tools/                   <- Toolchain automatizada en Python
│   │   ├── pck_handler.py       <- Motor de lectura y empaquetado bit-exact de PCKs
│   │   ├── excel_sync.py        <- Exportador/Importador entre Excel y binarios PCK
│   │   ├── apply_mod.py         <- Compilador que aplica los cambios directo al juego
│   │   └── audit_tool.py        <- Auditor automatizado de límites de líneas y caracteres
│   └── docs/                    <- Documentación y planes de expansión
│       └── MECHANICS_EXPANSION_PLAN.md
├── Data/                        <- Guías y datos matemáticos de GameFAQs (.mhtml)
└── DungeonTravelers2-2_EN/      <- Instalación del juego
```

---

## 🚀 Cómo Modificar y Aplicar Cambios

1. **Abrir y Editar Excel:**
   - Abre `mod_project/data_tables/skills.xlsx` (o `items.xlsx`).
   - Modifica las columnas `Modded_Desc` y `Modded_LvUp`.
   - Cambia la columna `Status` a `Approved`.
2. **Compilar y Aplicar al Juego:**
   ```bash
   python mod_project/tools/apply_mod.py
   ```
3. **Auditar Límites de Texto:**
   ```bash
   python mod_project/tools/audit_tool.py
   ```

---

## 📌 Control de Versiones (Git)
Se utiliza la convención de commits `prefix: content`:
- `feat: ...` para nuevas adiciones de clases, tablas o herramientas.
- `fix: ...` para corrección de límites de caracteres o cifras.
- `docs: ...` para actualizaciones de documentación.
