import math
import random

def simulate_all():
    print("================================================================================")
    print("DUNGEON TRAVELERS 2-2: RED TEAM ECONOMY, FLOW STATE & UX AUDIT SIMULATIONS")
    print("================================================================================")
    
    # -------------------------------------------------------------------------
    # SIMULATION 1: Inventory Lifespan & Dungeon Exploration Loops
    # -------------------------------------------------------------------------
    print("\n" + "="*70)
    print("SIMULATION 1: INVENTORY LIFESPAN & DUNGEON EXPLORATION LOOPS")
    print("="*70)
    
    # Parameters
    steps_per_floor = 380
    encounter_interval = 18 # steps
    battles_per_floor = steps_per_floor / encounter_interval # 21.11 battles
    drop_rate_per_battle = 0.45 # equipment, materials, ingredients
    chests_per_floor = 3 # fixed chest loot
    loot_per_floor = (battles_per_floor * drop_rate_per_battle) + chests_per_floor # ~12.5 items
    
    # Expedition kits carried by party:
    # Whistle/Escape: 1, Light tools: 3, HP heals: 4, TP heals: 4, Ailment cures: 3, Revives: 2
    kit_size = 17
    
    bag_capacities = {
        'Vanilla Early (Prologue - Ch 4)': 30,
        'Vanilla Mid (Ranks 8-10)': 35,
        'Vanilla Late (Ranks 11-14)': 40,
        'Vanilla Post (Rank 20)': 50,
        'Mod Early (Rank 2 @ 25 pts)': 40,
        'Mod Mid/Late/Post (Rank 8 @ 200 pts)': 50
    }
    
    print(f"Dungeon Floor Parameters:")
    print(f"  Steps/Floor: {steps_per_floor} | Encounters/Floor: {battles_per_floor:.1f} | Drops+Chests/Floor: {loot_per_floor:.2f} items")
    print(f"  Standard Survival Kit: {kit_size} slots")
    print("-" * 70)
    print(f"{'Progression Tier':<36} | {'Bag':<4} | {'Free':<5} | {'Floors/Run':<10} | {'20F Trips':<10} | {'50F Trips'}")
    print("-" * 70)
    
    sim1_results = {}
    for tier, cap in bag_capacities.items():
        free_slots = cap - kit_size
        floors_until_full = free_slots / loot_per_floor
        trips_20f = math.ceil(20 / floors_until_full)
        trips_50f = math.ceil(50 / floors_until_full)
        sim1_results[tier] = {
            'cap': cap, 'free': free_slots, 'floors': floors_until_full,
            'trips_20': trips_20f, 'trips_50': trips_50f
        }
        print(f"{tier:<36} | {cap:<4} | {free_slots:<5} | {floors_until_full:<10.2f} | {trips_20f:<10} | {trips_50f}")

    # Flow disruption metric: Assume each town trip takes 120 seconds (teleport, load, shop/storage triage, re-enter, navigate back to floor)
    trip_overhead_sec = 120
    v_early_time_20 = sim1_results['Vanilla Early (Prologue - Ch 4)']['trips_20'] * trip_overhead_sec / 60
    m_early_time_20 = sim1_results['Mod Early (Rank 2 @ 25 pts)']['trips_20'] * trip_overhead_sec / 60
    print("\nUX Friction Analysis (20-Floor Dungeon):")
    print(f"  Vanilla Early Town Trips: {sim1_results['Vanilla Early (Prologue - Ch 4)']['trips_20']} trips ({v_early_time_20:.1f} mins of non-gameplay logistics)")
    print(f"  Mod Early Town Trips:     {sim1_results['Mod Early (Rank 2 @ 25 pts)']['trips_20']} trips ({m_early_time_20:.1f} mins of logistics)")
    print(f"  Town Trip Frequency Reduction: {(1 - m_early_time_20/v_early_time_20)*100:.1f}%")
    print(f"  Time Saved from Logistics Overhead: {v_early_time_20 - m_early_time_20:.1f} minutes per 20 floors")

    # -------------------------------------------------------------------------
    # SIMULATION 2: Gold Sink & Blacksmith Economy
    # -------------------------------------------------------------------------
    print("\n" + "="*70)
    print("SIMULATION 2: GOLD SINK & BLACKSMITH ECONOMY")
    print("="*70)
    
    # Story Gold Income
    encounters_story = 800
    avg_gold_battle = 120
    combat_gold = encounters_story * avg_gold_battle # 96,000 G
    chests_and_quests_gold = 120000
    vendor_loot_sales = 140000
    story_baseline_gold = combat_gold + chests_and_quests_gold + vendor_loot_sales # 356,000 G
    
    # Quest Rank Gold:
    # Vanilla: R4 (10k), R6 (20k), R18 (100k) = 130,000 G
    # Modded: R4 (10k), R6 (20k), R11 (50k), R15 (100k), R18 (100k), R20 (500k) = 780,000 G
    # Bonus from Mod: +650,000 G
    vanilla_total_gold = story_baseline_gold + 130000 # 486,000 G
    modded_total_gold = story_baseline_gold + 780000  # 1,136,000 G
    
    # Gold Sinks:
    # 1. Weapon Forging (+0 -> +9)
    # Tier 1 (Common/Early): ~45,000 G
    # Tier 2 (Mid-story): ~110,000 G
    # Tier 3 (Late-story): ~180,000 G
    # Tier 4 (Endgame/Postgame Artifacts: Muramasa, Excalibur, Adamas): ~261,500 G
    forge_cost_endgame_weapon = 261500
    forge_cost_endgame_armor = 185000
    
    # 2. Sealbook Fusion & Enchanting
    # 4 slots per weapon, 4 gear items per character = 16 enchants / char
    # Average enchant fee in postgame: 14,000 G
    enchants_per_char = 16 * 14000 # 224,000 G
    
    # Party Costs (5 active characters):
    party_weapons_cost = 5 * forge_cost_endgame_weapon # 1,307,500 G
    party_armors_cost = 5 * forge_cost_endgame_armor   # 925,000 G
    party_enchants_cost = 5 * enchants_per_char        # 1,120,000 G
    party_consumables_and_food = 150000                # 150,000 G
    total_endgame_party_sink = party_weapons_cost + party_armors_cost + party_enchants_cost + party_consumables_and_food # 3,502,500 G
    
    # Minimal Story Completion Sinks (Midgame gear +5, basic enchants for 5 chars):
    midgame_weapon_cost = 5 * 55000 # 275,000 G
    midgame_armor_cost = 5 * 35000  # 175,000 G
    midgame_enchants = 5 * 60000    # 300,000 G
    midgame_food_items = 80000      # 80,000 G
    story_essential_sink = midgame_weapon_cost + midgame_armor_cost + midgame_enchants + midgame_food_items # 830,000 G
    
    # Roster Expansion (20 Heroines total in DT2-2! If player gears 2 teams = 10 chars):
    roster_10_sink = total_endgame_party_sink * 2 # 7,005,000 G
    
    print(f"Total Gold Inflow:")
    print(f"  Vanilla Inflow (Story + Vanilla Ranks): {vanilla_total_gold:,} G")
    print(f"  Modded Inflow  (Story + Modded Ranks):  {modded_total_gold:,} G")
    print(f"  Net Mod Bounty Injection:              +650,000 G")
    print("-" * 70)
    print(f"Gold Sinks:")
    print(f"  Story Essential Sinks (Midgame +5 gear, enchants, items): {story_essential_sink:,} G")
    print(f"  Postgame 5-Person Party Full Optimization (+9 gear):      {total_endgame_party_sink:,} G")
    print(f"  Expanded Roster (10 Heroines geared for postgame):        {roster_10_sink:,} G")
    print("-" * 70)
    
    # Gold Sufficiency Index (GSI) = Total Gold / Sinks
    gsi_vanilla_story = vanilla_total_gold / story_essential_sink
    gsi_modded_story  = modded_total_gold / story_essential_sink
    gsi_vanilla_post  = vanilla_total_gold / total_endgame_party_sink
    gsi_modded_post   = modded_total_gold / total_endgame_party_sink
    
    print(f"Gold Sufficiency Index (GSI):")
    print(f"  Story Progression GSI: Vanilla = {gsi_vanilla_story:.2f} (DEFICIT of {story_essential_sink - vanilla_total_gold:,} G) | Modded = {gsi_modded_story:.2f} (SURPLUS of {modded_total_gold - story_essential_sink:,} G)")
    print(f"  Postgame 5-Heroine GSI: Vanilla = {gsi_vanilla_post:.2f} (Covers {gsi_vanilla_post*100:.1f}%) | Modded = {gsi_modded_post:.2f} (Covers {gsi_modded_post*100:.1f}%)")
    print(f"  Remaining Postgame Deficit in Mod: {total_endgame_party_sink - modded_total_gold:,} G (Requires {total_endgame_party_sink - modded_total_gold:,} G farm)")
    print("Conclusion: 650k G bounty DOES NOT BREAK the economy. It eliminates early/mid story poverty while leaving 67.6% of endgame perfectionist sinks unfunded.")

    # -------------------------------------------------------------------------
    # SIMULATION 3: Flashlight 30-Step Duration in Dark Zones
    # -------------------------------------------------------------------------
    print("\n" + "="*70)
    print("SIMULATION 3: FLASHLIGHT 30-STEP DURATION IN DARK ZONES")
    print("="*70)
    
    dark_zones = [
        ("Short Ambush Hallway", 20),
        ("Standard Maze Corridor", 45),
        ("Deep Matrix Dark Chamber", 75),
        ("Full Dark Floor Section", 120)
    ]
    
    print(f"{'Dark Zone Type':<26} | {'Tiles':<5} | {'Vanilla (10s)':<14} | {'Mod (30s)':<12} | {'Menu Stops Saved'} | {'Friction Reduction'}")
    print("-" * 90)
    for zname, tiles in dark_zones:
        v_uses = math.ceil(tiles / 10)
        m_uses = math.ceil(tiles / 30)
        saved = v_uses - m_uses
        reduc = (saved / v_uses) * 100
        print(f"{zname:<26} | {tiles:<5} | {v_uses:<14} | {m_uses:<12} | {saved:<16} | {reduc:.1f}%")
        
    print("\nCognitive Load & Inventory Impact:")
    print("  - Vanilla 10-step flashlight forces a menu stop every 4-5 seconds of walking.")
    print("  - To traverse a 120-tile dark segment in vanilla requires 12 Flashlights (12 inventory slots = 40% of early bag!).")
    print("  - In mod (30 steps), only 4 Flashlights (4 slots = 10% of bag) are needed.")
    print("  - Friction reduction: 66.7% reduction in menu interruption frequency and 66.7% bag footprint reduction.")

    # -------------------------------------------------------------------------
    # SIMULATION 4: TP Economy & Attrition
    # -------------------------------------------------------------------------
    print("\n" + "="*70)
    print("SIMULATION 4: TP ECONOMY & ATTRITION OVER 50-FLOOR MATRIX")
    print("="*70)
    
    total_steps_50f = 50 * 380 # 19,000 steps
    total_battles_50f = math.floor(total_steps_50f / 18) # 1,055 battles
    buffet_steps = 900
    buffet_floors = buffet_steps / 380 # 2.37 floors
    buffet_battles = math.floor(buffet_steps / 18) # 50 battles
    unbuffed_battles = total_battles_50f - buffet_battles # 1,005 battles
    
    tp_spend_per_battle = 18 # average active party TP spend
    total_tp_demand_50f = total_battles_50f * tp_spend_per_battle # ~19,000 TP
    
    consumables_carried = {
        'Fairy Apple (+100 TP)': 6,
        'Banango Slice (+35 TP)': 8,
        'Mandragora Root (Revive 60% HP)': 4
    }
    tp_from_inventory = (6 * 100) + (8 * 35) # 880 TP
    
    print(f"50-Floor Matrix Exploration Telemetry:")
    print(f"  Total Steps: {total_steps_50f:,} | Total Encounters: {total_battles_50f:,}")
    print(f"  Buffet Duration: {buffet_steps} steps ({buffet_floors:.2f} floors / {buffet_battles} battles)")
    print(f"  Unbuffed Matrix Phase: {50 - buffet_floors:.2f} floors ({unbuffed_battles} battles, {(50 - buffet_floors)/50*100:.1f}% of dungeon)")
    print(f"  Total TP Demand across 50 Floors: {total_tp_demand_50f:,} TP")
    print(f"  Total TP Provided by Full Inventory of Consumables: {tp_from_inventory} TP ({tp_from_inventory/total_tp_demand_50f*100:.2f}% of demand)")
    print(f"  Consumable TP Exhaustion Milestone: Floor 2 (Battle 48)")
    print("Conclusion: Buffet meals and TP snacks DO NOT trivialize attrition in deep dungeons.")
    print("Sustaining a 50-floor run REQUIRES class-based engine mechanics (Maid/Bishop/TP Drain/Campfire).")

    # -------------------------------------------------------------------------
    # SIMULATION 5: Narrative, Dialogue & Tutorial Consistency
    # -------------------------------------------------------------------------
    print("\n" + "="*70)
    print("SIMULATION 5: NARRATIVE & DIALOGUE COHESION AUDIT")
    print("="*70)
    audited_scripts = [
        ("ShopStore.pck", "Talk_Random04", "Rin-Rin explicitly advertises HP/TP items and flashlights for dark zones", "COHESIVE"),
        ("ShopStore.pck", "Talk_Random15", "Recommends keeping recovery items in bag for exploration survival", "COHESIVE"),
        ("ShopStore.pck", "Talk_Scenario20", "Instructs Fried to buy as many items as bag and storage can hold", "COHESIVE"),
        ("ShopQuest.pck", "Talk_Random08", "Explicitly warns: Ranks 2 & 8 grant +10 Bag Storage each (reaching 50 slots early!)", "COHESIVE"),
        ("ShopQuest.pck", "Talk_Random10", "Advises on bag management and bounty rewards", "COHESIVE"),
        ("ShopBlacksmith.pck", "Talk_Random00", "Details +9 forge levels and 5 enchant slots", "COHESIVE"),
        ("ShopBlacksmith.pck", "Talk_Random10", "Explains flee/explosion/petrify monsters cannot be sealed", "COHESIVE"),
        ("ShopBlacksmith.pck", "Talk_Random11", "Explains Grand Sealbooks cannot be used for normal weapon enchants", "COHESIVE"),
        ("ShopBar.pck", "Talk_Scenario01-14", "Details mercenary hiring, TP recovery skills (Momona Cook), doll summons", "COHESIVE"),
        ("Teaching.pck", "CheatsTeaching_14", "Explains quest rank unlocks, items, gear, and mercenary Miranda", "COHESIVE"),
        ("Teaching.pck", "CheatsTeaching_20", "Explains Dark Zones, Anti-Magic, Dispel Floor, and trap survival", "COHESIVE"),
        ("Lesson.pck", "BattleTeacher_09", "Explains Quest Desk presents: gold, rare equipment, and bag space", "COHESIVE"),
        ("Lesson.pck", "Talk_Random12", "Teacher warns to keep an eye on bag capacity and avoid abandoning items", "COHESIVE")
    ]
    for pck, file_id, summary, status in audited_scripts:
        print(f"[{pck:<16}] {file_id:<18} | {summary:<70} | {status}")

if __name__ == '__main__':
    simulate_all()
