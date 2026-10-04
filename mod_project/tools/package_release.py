import os
import zipfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(BASE_DIR, 'dist')
os.makedirs(DIST_DIR, exist_ok=True)

GAME_DIR = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN')
PARAM_DIR = os.path.join(GAME_DIR, 'Data', 'ENG', 'Parameter')
SCRIPT_DIR = os.path.join(GAME_DIR, 'Data', 'ENG', 'Script')

MODIFIED_PARAM_PCKS = [
    'TechniqueSkillData.pck', 'PassiveSkillData.pck', 'MagicSkillData.pck', 'UniqueSkillData.pck',
    'ItemData.pck', 'EquipmentData.pck', 'SealScrollData.pck', 'JoinSkillData.pck',
    'EnchantData.pck', 'PartySkillData.pck', 'FoodMenuData.pck', 'EnemyAttackData.pck',
    'ClassData.pck', 'StringData.pck', 'TrapData.pck', 'TrophyData.pck',
    'QuestRankData.pck', 'LvExpSkptData.pck'
]

MODIFIED_SCRIPT_PCKS = [
    'Teaching.pck', 'Lesson.pck', 'ShopQuest.pck', 'ShopBlacksmith.pck', 'ShopBar.pck', 'ShopStore.pck'
]

README_CONTENT = """============================================================
DUNGEON TRAVELERS 2-2: DEFINITIVE BALANCE & QoL MOD (v1.0)
============================================================

COMO INSTALAR EN CUALQUIER PC:
1. Asegurate de tener Dungeon Travelers 2-2 instalado en esa PC.
2. Abre la carpeta principal del juego (donde esta DT22_en.exe).
3. Descomprime o arrastra el contenido de este archivo ZIP
   directamente a la carpeta principal del juego.
4. Cuando Windows pregunte, selecciona:
   "Reemplazar los archivos en el destino" (Sobrescribir).
5. Inicia el juego normalmente desde DT22_en.exe.

CONTENIDO DEL MOD:
- Transparencia Total de Formulas y Datos en combate, equipo y habilidades.
- Curva de EXP Rebalanceada: Progresion fluida y alivio del Crown Grind (Lv 70-99).
- Sistema Catch-Up: Slave's Torc (Doble EXP) y Gran Sello Dragon Papi (+50% EXP).
- Almacenamiento Anticipado: Bolsa de 40 slots en Rango 2 y 50 slots en Rango 8.
- Reduccion de Delay de Armas Pesadas (F 2.35x en vez de 2.9x).
- Master Spells con 50 de penetracion de resistencia elemental.
- Clases de Tanque, Muniecas de Soul Summoner y Consumibles rebalanceados.
- Linterna de exploracion ampliada a 30 pasos (3x).
============================================================
"""

def package_mod():
    zip_filename = 'DT22_Definitive_QoL_Balance_Mod_v1.0.zip'
    zip_path = os.path.join(DIST_DIR, zip_filename)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('INSTRUCCIONES_INSTALACION.txt', README_CONTENT)
        for pck in MODIFIED_PARAM_PCKS:
            src = os.path.join(PARAM_DIR, pck)
            if os.path.exists(src):
                arcname = os.path.join('Data', 'ENG', 'Parameter', pck)
                zf.write(src, arcname)
        for pck in MODIFIED_SCRIPT_PCKS:
            src = os.path.join(SCRIPT_DIR, pck)
            if os.path.exists(src):
                arcname = os.path.join('Data', 'ENG', 'Script', pck)
                zf.write(src, arcname)

    sz = os.path.getsize(zip_path)
    print(f"Packaged successfully: {zip_path}")
    print(f"ZIP Size: {sz:,} bytes ({sz / 1024:.1f} KB / {sz / (1024*1024):.2f} MB)")
    return zip_path

if __name__ == '__main__':
    package_mod()
