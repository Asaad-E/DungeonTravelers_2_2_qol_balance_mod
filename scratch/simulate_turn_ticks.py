"""
High-Fidelity Tick-Based Turn Simulation & Red Team Stress Test for DT2-2
Models exact AGI ticks, Weapon Rank Delays, Status Ailments, and Boss Multi-Turn Rotations.
"""
import random
import math

class CombatUnit:
    def __init__(self, name, u_type, max_hp, base_def, agi, weapon_delay, role, resists=50):
        self.name = name
        self.u_type = u_type
        self.max_hp = max_hp
        self.hp = max_hp
        self.base_def = base_def
        self.agi = agi
        self.weapon_delay = weapon_delay
        self.role = role
        self.resists = resists
        self.gauge = random.randint(0, 30) # initial roll
        self.status = None # 'stun', 'freeze', 'paralysis'
        self.buffs = {}
        self.chanting = False
        self.chant_ticks_remaining = 0
        self.spell_target = None
        self.is_defending = False

def run_deep_combat_sim(comp_name, party_units_builder, num_trials=500):
    wipes = 0
    clears = 0
    turn_counts = []
    wipe_turn_counts = []
    
    # Superboss profile: Creator God / Dark Mutant Avatar
    # HP: 180,000 | AGI: 150 | Weapon Delay: 1.0x | ATK: 900
    for _ in range(num_trials):
        party = party_units_builder()
        boss = CombatUnit("Superboss", "boss", 180000, 500, 150, 1.0, "boss", resists=100)
        
        # Consumable bag for Comp C
        bag = {'apple': 6, 'root': 6, 'croissant': 6}
        
        sim_ticks = 0
        max_ticks = 10000
        battle_over = False
        
        while sim_ticks < max_ticks and not battle_over:
            # Advance tick: find who acts next
            # Tick rate proportional to AGI
            # Let's advance ticks in discrete steps of 5 ticks
            sim_ticks += 5
            
            # Update gauges
            if boss.hp > 0:
                boss.gauge += (boss.agi / 100.0) * 5
                
            for u in party:
                if u.hp > 0:
                    u.gauge += (u.agi / 100.0) * 5
                    if u.chanting:
                        u.chant_ticks_remaining -= 5
            
            # Check if any unit ready to act (gauge >= 100)
            # Find unit with highest gauge >= 100
            candidates = []
            if boss.hp > 0 and boss.gauge >= 100:
                candidates.append(boss)
            for u in party:
                if u.hp > 0 and u.gauge >= 100 and not u.chanting:
                    candidates.append(u)
                elif u.hp > 0 and u.chanting and u.chant_ticks_remaining <= 0:
                    candidates.append(u)
                    
            if not candidates:
                continue
                
            # Highest gauge acts
            actor = max(candidates, key=lambda x: x.gauge)
            
            # --- ACTOR ACTIONS ---
            if actor.u_type == "boss":
                actor.gauge -= 100 # recovery delay for boss action = 100 * 1.0 = 100
                
                # Check living targets
                living_party = [u for u in party if u.hp > 0]
                if not living_party:
                    wipes += 1
                    wipe_turn_counts.append(sim_ticks // 100)
                    battle_over = True
                    break
                    
                # Boss selects action:
                # 1. 4-Hit Physical Multi-Strike (60% chance)
                # 2. Grand AoE Cataclysm (30% chance)
                # 3. Status Sweep / Stun Breath (10% chance)
                roll = random.random()
                if roll < 0.60:
                    # Multi-strike: 4 hits
                    tank = next((u for u in living_party if u.role == "tank"), None)
                    for h in range(4):
                        living = [u for u in party if u.hp > 0]
                        if not living:
                            break
                        # Cover mechanics: Paladin with Cover intercepts 70% of physical hits
                        if tank and tank.hp > 0 and random.random() < 0.70:
                            tgt = tank
                            is_intercept = True
                        else:
                            tgt = random.choice(living)
                            is_intercept = False
                            
                        # Damage calculation
                        is_crit = random.random() < 0.30
                        crit_m = 1.5 if is_crit else 1.0
                        def_val = tgt.base_def
                        if tgt.is_defending:
                            def_val *= 1.5
                            
                        raw_dmg = max(100, 900 - def_val) * crit_m
                        if is_intercept and tank.role == "tank":
                            # Modded Cover: 60% mitigation
                            raw_dmg *= 0.40
                        if getattr(tgt, 'two_handed_mitigation', False):
                            raw_dmg *= 0.85 # +15% passive 2H mitigation
                        if tgt.is_defending:
                            raw_dmg *= 0.50
                            
                        # Holy Shield check on Paladin (40% proc to absorb 75%)
                        if tgt.role == "tank" and random.random() < 0.40:
                            raw_dmg *= 0.25
                            
                        tgt.hp -= int(raw_dmg)
                        
                        # Chant interruption check
                        if tgt.chanting and tgt.hp > 0:
                            # Modded Concentrate: 6.6% crit interrupt check
                            if is_crit and random.random() < 0.066:
                                tgt.chanting = False
                            elif not is_crit and random.random() < (raw_dmg / tgt.max_hp):
                                tgt.chanting = False
                                
                elif roll < 0.90:
                    # Grand AoE Cataclysm
                    for tgt in living_party:
                        elem_dmg = 1100 * (1.0 - (tgt.resists * 0.005))
                        if tgt.is_defending:
                            elem_dmg *= 0.50
                        tgt.hp -= int(elem_dmg)
                        if tgt.chanting and tgt.hp > 0:
                            if random.random() < 0.066:
                                tgt.chanting = False
                else:
                    # Status / Stun Breath
                    for tgt in living_party:
                        if random.random() < 0.45:
                            tgt.status = 'stun'
                            
                # Clear defend stance after boss acts
                for u in party:
                    u.is_defending = False
                    
            else:
                # PARTY MEMBER ACTS
                # Check status
                if actor.status == 'stun':
                    actor.status = None
                    actor.gauge -= 60
                    continue
                    
                # If spell finished chanting
                if actor.chanting:
                    actor.chanting = False
                    actor.gauge -= int(100 * actor.weapon_delay)
                    # Cast Master Spell (Crimson Flare / Gaia Crush)
                    # 50 Res Pierce: boss effective res = 50 -> 0.75x dmg
                    spell_dmg = random.randint(7500, 11000)
                    boss.hp -= spell_dmg
                    if boss.hp <= 0:
                        clears += 1
                        turn_counts.append(sim_ticks // 100)
                        battle_over = True
                        break
                    continue
                    
                # Regular action selection based on role:
                if actor.role == "caster":
                    # Start chanting Master Spell (60 frames chant = 60 ticks)
                    actor.chanting = True
                    actor.chant_ticks_remaining = 60
                    actor.gauge = 0 # stays in chant
                    continue
                    
                elif actor.role == "healer":
                    # Bishop Circle Heal
                    actor.gauge -= int(100 * actor.weapon_delay)
                    for u in party:
                        if u.hp > 0:
                            u.hp = min(u.max_hp, u.hp + 900)
                            u.status = None # cleanse
                            
                elif actor.role == "tank":
                    # Paladin: either Defend if HP low or boss enrage, or Shield Bash / Cover
                    actor.gauge -= int(100 * actor.weapon_delay)
                    if actor.hp < actor.max_hp * 0.40:
                        actor.is_defending = True
                    else:
                        # Bash / chip damage
                        boss.hp -= random.randint(1200, 2200)
                        
                elif actor.role == "berserker":
                    # Heavy 2H Axe attack: Rank E delay = 2.15x
                    actor.gauge -= int(100 * 2.15) # 215 recovery!
                    # Moon Drop / Bone Crusher
                    dmg = random.randint(5500, 8500)
                    boss.hp -= dmg
                    # Blood Drain: heal 15% of damage
                    actor.hp = min(actor.max_hp, actor.hp + int(dmg * 0.15))
                    
                elif actor.role == "dps":
                    # Physical DPS (Samurai / Sniper / Kunoichi)
                    actor.gauge -= int(100 * actor.weapon_delay)
                    # Swallow Return / Armor Pierce
                    dmg = random.randint(4500, 7500)
                    boss.hp -= dmg
                    
                elif actor.role == "item_user":
                    actor.gauge -= 100
                    # Emergency item use
                    dead_allies = [u for u in party if u.hp <= 0]
                    if dead_allies and bag['root'] > 0:
                        target = dead_allies[0]
                        bag['root'] -= 1
                        target.hp = int(target.max_hp * 0.60) # 60% Mandragora
                    else:
                        injured = [u for u in party if u.hp > 0 and u.hp < u.max_hp * 0.50]
                        if injured and bag['croissant'] > 0:
                            bag['croissant'] -= 1
                            injured[0].hp = min(injured[0].max_hp, injured[0].hp + 500)
                        else:
                            boss.hp -= random.randint(2500, 4000)
                            
                if boss.hp <= 0:
                    clears += 1
                    turn_counts.append(sim_ticks // 100)
                    battle_over = True
                    break
                    
        # Check timeout or party dead
        if not battle_over:
            wipes += 1
            wipe_turn_counts.append(sim_ticks // 100)
            
    clear_rate = (clears / num_trials) * 100
    wipe_rate = (wipes / num_trials) * 100
    avg_clear_time = (sum(turn_counts) / len(turn_counts)) if turn_counts else 0
    avg_wipe_time = (sum(wipe_turn_counts) / len(wipe_turn_counts)) if wipe_turn_counts else 0
    return clear_rate, wipe_rate, avg_clear_time, avg_wipe_time

def test_all_compositions():
    print("=" * 65)
    print("SIMULATION 5 (DEEP TICK-BASED ENGINE): 4 EXTREME COMPOSITIONS")
    print("=" * 65)
    
    # Comp A: 5 Mages (Witch, Sage, Bishop, MagPrincess, Sorceress)
    def build_comp_a():
        return [
            CombatUnit("Witch", "party", 950, 220, 110, 1.2, "caster", resists=70),
            CombatUnit("Sage", "party", 1050, 240, 115, 1.2, "caster", resists=75),
            CombatUnit("Bishop", "party", 1100, 260, 110, 1.3, "healer", resists=80),
            CombatUnit("MagPrincess", "party", 1200, 310, 120, 1.3, "caster", resists=70),
            CombatUnit("Sorceress", "party", 920, 210, 110, 1.2, "caster", resists=70),
        ]
        
    # Comp B: 5 Berserkers (5x 2H Axe, 0 Tanks, 0 Healers)
    def build_comp_b():
        party = []
        for i in range(5):
            u = CombatUnit(f"Berserker_{i+1}", "party", 1650, 320, 95, 2.15, "berserker", resists=50)
            u.two_handed_mitigation = True
            party.append(u)
        return party
        
    # Comp C: 0 Healer, 0 Maid (Paladin, Dark Lord, Samurai, Sniper, Kunoichi)
    def build_comp_c():
        return [
            CombatUnit("Paladin", "party", 2200, 650, 105, 1.6, "tank", resists=75),
            CombatUnit("DarkLord", "party", 2400, 420, 100, 1.95, "berserker", resists=60),
            CombatUnit("Samurai", "party", 1400, 350, 125, 1.3, "dps", resists=55),
            CombatUnit("Sniper", "party", 1300, 280, 130, 1.45, "dps", resists=50),
            CombatUnit("Kunoichi", "party", 1250, 310, 155, 1.0, "item_user", resists=60),
        ]
        
    # Comp D: Non-Valkyrie Standard Balanced (Paladin, Samurai, Sage, Bishop, Sniper)
    def build_comp_d():
        return [
            CombatUnit("Paladin", "party", 2200, 650, 105, 1.6, "tank", resists=75),
            CombatUnit("Samurai", "party", 1400, 350, 125, 1.3, "dps", resists=55),
            CombatUnit("Sage", "party", 1050, 240, 115, 1.2, "caster", resists=75),
            CombatUnit("Bishop", "party", 1100, 260, 110, 1.3, "healer", resists=80),
            CombatUnit("Sniper", "party", 1300, 280, 130, 1.45, "dps", resists=50),
        ]

    trials = 300
    for name, builder in [
        ("Composition A: 5-Mage Party (All Casters, 0 Tanks)", build_comp_a),
        ("Composition B: 5-Berserker Party (All 2H Axes, 0 Healers, 0 Tanks)", build_comp_b),
        ("Composition C: 0-Healer, 0-Maid Party (Items & Leech Only)", build_comp_c),
        ("Composition D: Non-Valkyrie Balanced (Paladin, Samurai, Sage, Bishop, Sniper)", build_comp_d)
    ]:
        cr, wr, ct, wt = run_deep_combat_sim(name, builder, num_trials=trials)
        print(f"\n{name}:")
        print(f"  Clear Rate: {cr:5.1f}% | Wipe Rate: {wr:5.1f}%")
        if cr > 0:
            print(f"  Avg Victory Time: {ct:.1f} turn cycles")
        if wr > 0:
            print(f"  Avg Wipe Time: {wt:.1f} turn cycles")

if __name__ == '__main__':
    test_all_compositions()
