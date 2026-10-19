# Class identity (vanilla)

What each class of Dungeon Travelers 2-2 is for, as the game presents it. It is a soft standard for phase 2
(asked on 2026-10-07): every change to a skill or a class (themes T02, T04,
T05, T06, T07) and every effect added is checked against the entry of the class it touches, so that a class gains
viability while keeping its flavour.

It describes the **intent**, not whether the class achieves it. Many classes fall short of their intent in vanilla,
and the register of complaints (sheet `Criticisms` of `balance_criteria.xlsx`) says where; that judgement belongs to
the themes, not to this page.

**Sources.** The "概要" (overview) and "特徴" (character) paragraphs of the class pages of the Japanese wiki (atwiki
dt2-2, pages 117 to 148), which quote or paraphrase the in-game class description; the skills each class learns,
read from the skill tree of the game (`gamedata/data.py`, `tools/skill_tree_data.py`); and the class tree, read from the
growth rows of the executable (`tools/class_data.py`: an advanced class reached from two classes has one growth row
per route). The GameFAQs guide is not used here: its verdicts are the register's business.

**Tree.** A character changes class at level 15 (intermediate) and level 30 (advanced). The five lines:

| Base | Intermediate | Advanced |
|---|---|---|
| Fighter | Paladin, Berserker | Valkyrie (Paladin), Samurai (Paladin or Berserker), Dark Lord (Berserker) |
| Magic User | Sorceress, Enchantress, Priestess | Witch (Sorceress), Magical Princess (Sorceress or Enchantress), Sage (Enchantress or Priestess), Bishop (Priestess) |
| Scout | Archer, Assassin | Sniper (Archer), Treasure Hunter (Archer or Assassin), Kunoichi (Assassin) |
| Maid | Bard, Dancer | Diva (Bard), Mistress (Bard or Dancer), Etoile (Dancer) |
| Spieler | Doll Master, Trickster | Soul Summoner (Doll Master), Papillon (Doll Master or Trickster), Joker (Trickster) |

Each entry: **role** (what it does in a party), **niche** (when it is the right pick), **unique** (what no other class
offers), **own tools** (the skills it learns, from the game data).

---

## Fighter line

### Fighter (base)
- **Role:** front-line warrior with high strength and stamina who handles many short-range weapons; the shield of
  the party and a physical attacker at once (wiki p117).
- **Niche:** standing in front, drawing and absorbing physical attacks while clearing enemies.
- **Unique:** the widest choice of melee weapons among the base classes, each with its mastery.
- **Own tools:** Provoke, War Cry, Raging Smash, Double Attack, Avenger, Sword / Axe / Lance Mastery.

### Paladin (intermediate)
- **Role:** holy knight who stands in front and uses herself as the shield of the party; protecting allies matters
  more to her than defeating enemies (p122).
- **Niche:** the sturdiest front member, clearly harder than a Berserker even with a two-handed weapon.
- **Unique:** taking hits meant for others (Cover, Parry, Auto-Guard) and a little healing.
- **Own tools:** Cover, Parry, Auto-Guard, Defender, Shield Bash, Cross Slash, Heal, Mini Auto-Recovery.

### Berserker (intermediate)
- **Role:** expert of melee combat with two-handed swords and axes; shrugs off small hits and fells enemies with one
  strong blow; indispensable to an attacking party (p123).
- **Niche:** raw physical damage, with a wider job than it seems: Berserk for power, water and earth (axe) attacks,
  and removing enemy buffs.
- **Unique:** Berserk, and the dispel on a blow (Aura Eliminate).
- **Own tools:** Berserk, Aura Eliminate, Frost Slash, Geo Break, Blood Rage, Dark Aura, Preparation, Adaptation.

### Valkyrie (advanced, from Paladin)
- **Role:** the most stable melee fighter; a war angel who protects her allies and lands the decisive blow (p133).
- **Niche:** either a shield tank using her guard skills or an all-out attacker with a two-handed lance.
- **Unique:** party-wide guard buffs (Spell Guard, Material Guard, Imperial Guard, Moon Curtain) beside a top
  physical nuke (Daedalus Attack).
- **Own tools:** Daedalus Attack, Gust Thrust, Ether Strike, Absolute Attack, Spell Guard, Material Guard, Imperial
  Guard, Moon Curtain, Protect, Circle Heal, Auto-Refresh, Guts.

### Samurai (advanced, from Paladin or Berserker)
- **Role:** swordswoman whose every cut is lethal; cleaves enemies in one stroke, and also dodges and counters
  (p134).
- **Niche:** attack-focused advanced swordsman with the katana.
- **Unique:** katana techniques with instant kills, armour piercing, and a dodge-and-counter stance.
- **Own tools:** Moonlight Purgatory, Onikagura, Halving Slice, Armor Penetration, Backward Swing, Flowing Water
  Stance, Mind's Eye, Last Stand, Triple Attack, Katana Mastery.

### Dark Lord (advanced, from Berserker)
- **Role:** a god of battle clad in dark aura who devours the life and spirit of enemies (p135).
- **Niche:** the Berserker raised further: area attacks and self buffs; can also tank by drawing every attack
  (Attract) and spread debuffs through Dark Aura while recovering TP.
- **Unique:** a self-contained loop of draw, debuff and drain; Power Charge.
- **Own tools:** Power Charge, Megaton Press, Shock Spiral, Attract, Brave, Blood Drain, Soul Drain, Life Bring,
  Grudge Accumulator, First Grid, Dark Quest.

## Magic User line

### Magic User (base)
- **Role:** the base mage, who handles every element and heals the wounded with Heal; one is wanted in any party
  (p118).
- **Niche:** basic spells of all elements; the player decides early whether she leans to attack or to support.
- **Unique:** the only base class with spells of every element and healing.
- **Own tools:** Fireball, Ice Edge, Air Cutter, Stone Hammer, Thunderbolt, Poison, Heal.

### Sorceress (intermediate)
- **Role:** area attack magic; weak in defence but with magic strong enough to make up for it; can spread over
  elements or master one (p124).
- **Niche:** the pure upgrade of the Magic User: row attack spells.
- **Unique:** row-wide elemental spells, Critical Magic and Concentrate for spellcasting.
- **Own tools:** Fire Blast, Ice Storm, Air Turbulence, Stone Shower, Thunder Chain, Blood Absorb, Critical Magic,
  Concentrate, Magic Mastery, Auto-Refresh.

### Enchantress (intermediate)
- **Role:** a caster who lends the power of the elements to weapons; hard to master because elements must be chosen
  by enemy, but an excellent support when she shines (p125).
- **Niche:** support through ailments on enemies and buffs on allies, reading enemy resistances.
- **Unique:** element enchantments on weapons; the status ailment spells.
- **Own tools:** Fire / Water / Wind / Earth / Lightning Enchant, Stun, Freeze, Silence, Paralyze, Circle Brave,
  Circle Protect, Divine Shield, Mini Circle Nurse, Holy Prayer, Return, Fast Cast, Heal Mastery.

### Priestess (intermediate)
- **Role:** rear support excelling at healing: party heals, reviving the fallen, and one kind of wide spell (p126).
- **Niche:** the core of the party's healing in long dungeon runs.
- **Unique:** the only class with both Circle Heal and Heal Mastery; Resurrect.
- **Own tools:** Circle Heal, Nurse, Resurrect, Heal Mastery, Fast Cast, Slow, Light, Return, Divine Shield, the row
  spells of the Sorceress, Mini Auto-Recovery / Refresh.

### Witch (advanced, from Sorceress)
- **Role:** the attack magic expert, with the strongest spell of every element; wipes groups with wide spells and
  single foes with the strongest elemental one (p136).
- **Niche:** the only class specialised in magic attack; also has non-elemental drains for enemies that resist
  elements.
- **Unique:** top single and all-target spells of every element; Nirvana, Loose Spirit, Economy.
- **Own tools:** Inferno, Crimson Flare, Diamond Dust, Cocytus, Lightning, Muon Plasma, Tornado, Tempest, Meteor,
  Gaia Crush, Soul Absorb, Slow, Loose Spirit, Nirvana, Economy, Fast Cast.

### Magical Princess (advanced, from Sorceress or Enchantress)
- **Role:** magical girl who also fights hand to hand with love and courage; Magical Change raises her to the limit
  and her all-target attacks mow enemies down (p137).
- **Niche:** the all-rounder: physical and magic attacker, even a tank; with Enchantress behind her, element
  enchantments too.
- **Unique:** Magical Change and the mix of sword, magic and cover.
- **Own tools:** Magical Change, Magical Slash, Magical Spark, Rainbow Flash, Magic Barrier, Illusion, Accelerator,
  Cover, Guts, Double Attack, Sword Mastery.

### Sage (advanced, from Enchantress or Priestess)
- **Role:** support that raises allies' abilities, with skills that cure ailments by themselves; shows its worth in
  long fights and turns hard battles around (p138).
- **Niche:** ailment spells and party buffs; does many things, so SP and turns must be planned.
- **Unique:** the guard spells against each physical type, Prism Dawn, Esarhaddon (automatic cure), instant death
  and petrification spells, Dispel.
- **Own tools:** Stab / Slash / Bash Guard, Sun Veil, Amplify, Accelerator, Prism Dawn, Esarhaddon, Dispel, Sleep,
  Terrorize, Death, Petrify, Bible Thump, Identify, Economy.

### Bishop (advanced, from Priestess)
- **Role:** the healing specialist, with party-wide ailment cures, and strong blows (Holy Gavel, Justice) that make
  her attack worth noting (p139).
- **Niche:** keeps the party alive in any situation; also has a non-elemental all-target spell.
- **Unique:** Full Heal, Circle Nurse, Insurance; a healer with a mace.
- **Own tools:** Full Heal, Circle Nurse, Insurance, Moon Curtain, Shine Curse, Holy Gavel, Justice, Double Attack,
  Mace Mastery.

## Scout line

### Scout (base)
- **Role:** nimble fighter who attacks openings and can even steal money; uses daggers and bows, so she changes style
  to the situation (p119).
- **Niche:** speed, evasion and small utility.
- **Unique:** stealing gold; the dagger-or-bow switch.
- **Own tools:** Sharp Stab, Poison Shot, Gold Steal, Evade, Cleanse, Elusiveness, Lucky Me, Dagger Mastery.

### Archer (intermediate)
- **Role:** bow user who supports from afar; accurate, with arrows that cause ailments and a rain of arrows for groups
  (p127).
- **Niche:** back-row physical attacker who can specialise in damage because she is safe.
- **Unique:** ailment arrows from long range.
- **Own tools:** Arrow Rain, Freeze Shot, Paralysis Shot, Gravity Shot, Caution, Bow Mastery.

### Assassin (intermediate)
- **Role:** dagger user who toys with enemies through speed and lands critical blows; ailments for support and
  attack; can kill at a stroke (p128).
- **Niche:** fast support that stops enemies acting: sleep, stun, silence.
- **Unique:** Murder (instant kill on a critical) and the stings.
- **Own tools:** Sleep Sting, Stun Sting, Silence Sting, Murder, Awareness, Adaptation.

### Sniper (advanced, from Archer)
- **Role:** marksman who shoots her prey with godlike speed and kills with one shot; warning and support shots too
  (p140).
- **Niche:** back-row physical attacker with simple, strong skills; long range, so counters and Dark Aura do not
  reach her.
- **Unique:** Warning Shot and Support Shot; Star Dust Arrow; Divine Cannon.
- **Own tools:** Divine Cannon, Spiral Arrow, Chain Spike, Guided Shot, Star Dust Arrow, Warning Shot, Support Shot,
  Aim.

### Treasure Hunter (advanced, from Archer or Assassin)
- **Role:** uses dagger, whip and bow, steals treasure from enemies and appraises items; the party's purse keeper
  (p141).
- **Niche:** a fast supporter built on items, which act at once unlike spells.
- **Unique:** Item Steal, Treasure Hunt, Item Mastery, Identify, Negotiate, Recycle.
- **Own tools:** Pursuit Stab, Chain Spike, Hard Whipping, Triple Attack, Item Steal, Item Mastery, Recycle,
  Treasure Hunt, Negotiate, Identify, Trap / Treasure Search, Light, Whistle, Fleet Foot.

### Kunoichi (advanced, from Assassin)
- **Role:** female ninja who fights with speed: shadow clones void enemy attacks, she dual-wields, throws shuriken
  and uses many ninja arts (p142).
- **Niche:** a high-speed debuffer spreading ailments.
- **Unique:** Shadow Clone, Shadow Sew, Dual Wield and the element scrolls.
- **Own tools:** Shadow Clone, Shadow Sew, Light / Fire / Water / Lightning / Wind / Earth Scroll, Ninja Piledriver,
  Barrage, Phoenix, Dual Wield, Katana and Projectile Mastery.

## Maid line

### Maid (base)
- **Role:** good at neither blows nor spells, but produces special effects without TP and without chanting; the
  unsung pillar of the party (p120).
- **Niche:** healing and support with skills and items; a dagger hit when idle; a gun from the instructor gives some
  firepower early.
- **Unique:** support at no TP cost (Cook, First Aid), recovery after battle (Generous Heart).
- **Own tools:** First Aid, Cook, Self-Sacrifice, Clean, Lullaby, Generous Heart, Maid Mastery.

### Bard (intermediate)
- **Role:** singer who strengthens the whole party with her voice; weak in battle and protected at the back, but her
  songs inspire and heal (p129).
- **Niche:** songs that keep buffing every ally while she sings.
- **Unique:** sustained party-wide songs (healing, TP, magic, EXP).
- **Own tools:** Replenishing Carol, Blissful Chorale, Spiritual Fantasia, Sacred Hymn, Experience Paean, Song
  Mastery.

### Dancer (intermediate)
- **Role:** dancer who charms enemies with her whole body; her dances curse and weaken those who see them (p130).
- **Niche:** debuffer: while she dances, enemies keep a debuff; a dance starts at once and switching is immediate.
- **Unique:** sustained enemy debuffs that need no chant.
- **Own tools:** Fascinating Waltz, Alluring Samba, Gloomy Tango, Gravitating Polka, Warm-Up, Dance Mastery.

### Diva (advanced, from Bard)
- **Role:** support specialised in songs that strengthen allies; her voice gives courage to all who hear it (p143).
- **Niche:** the Bard raised: two songs at once with Self Session, and helpers (Fast Talk, Concentrate) that make
  songs much easier to use.
- **Unique:** Self Session (two songs), the speed song.
- **Own tools:** Lightning March, Concentration Prelude, Reading Requiem, Sorcerous Ballad, Barrage Rondo, Panic Voice,
  Self Session, Fast Talk, Concentrate, Auto-Recovery.

### Mistress (advanced, from Bard or Dancer)
- **Role:** once a maid, she rose to be the mistress; slightly sadistic, loves to punish with her whip (p144).
- **Niche:** sub-attacker who supports with her Bard or Dancer skills and attacks physically; not sturdy, so in the
  back row.
- **Unique:** the whip as a class weapon, and the mix of maid support with punishment (Carrot and Stick, Absolute
  Obedience).
- **Own tools:** Hard Whipping, Enticing Love, Absolute Obedience, Carrot and Stick, Counter Whip, Knock Down, Ecstasy,
  Provoke, War Cry, Resurrect, Auto-Refresh, Whip Mastery.

### Etoile (advanced, from Dancer)
- **Role:** the star of the battlefield whose dance captivates any enemy; and at times she saves her allies at the
  cost of her own life (p145).
- **Niche:** the Dancer raised: two dances at once (On Stage); strong exclusive dances, especially against bosses.
- **Unique:** On Stage and the stat-draining dances; Primevil.
- **Own tools:** Debilitating Salsa, Dumbing Mazurka, Emaciating Hopak, On Stage, Primevil, Magnificent Steps,
  Concentrate, Auto-Recovery, Guts.

## Spieler line

### Spieler (base)
- **Role:** the gambler's base class (the wiki page has no overview text; its role comes from its skills): luck-based
  and odd moves.
- **Niche:** a fast, unpredictable fighter with a dash of support.
- **Unique:** random-result skills (Roulette Circus), Present for Me, Coffee Break.
- **Own tools:** Danger Shoot, Roulette Circus, Coffee Break, Present for Me, Fleet Foot, Weapon Mastery.

### Doll Master (intermediate)
- **Role:** breathes life into dolls that act on their own without orders, so the master can do something else
  (p131).
- **Niche:** a summoner who shines in long fights such as bosses; dolls are techniques, not magic, so they work in
  anti-magic zones; healing through Catalina matters.
- **Unique:** autonomous allies (dolls).
- **Own tools:** Spartan, Oracles, Catalina, Doll Mastery, Mini Auto-Refresh.

### Trickster (intermediate)
- **Role:** loves the unpredictable over the stable; may turn a crisis around with one move (p132).
- **Niche:** a fast physical attacker: much more AGI than the Spieler, among the best of all intermediate classes,
  hitting like a fighter, where the Doll Master relies on dolls.
- **Unique:** High Risk High Return, Magic Box, Anti-Dark Aura, Pretend.
- **Own tools:** Checkmate, Surprise Fist, Magic Box, High Risk High Return, Pretend, Anti-Dark Aura, Mini
  Auto-Recovery.

### Soul Summoner (advanced, from Doll Master)
- **Role:** the highest doll user: stronger dolls, two at once, and power drawn from the monster sealbook she wears
  and given to her dolls (p146).
- **Niche:** the Doll Master raised (Double Puppet); her main skills split by ATK or INT build.
- **Unique:** Double Puppet, Soul Seal, the strongest dolls (Mercidarian, Musiy, Perdurabo).
- **Own tools:** Mercidarian, Musiy, Perdurabo, Double Puppet, Soul Seal, Soul Eater, Destiny Line, Divine Shield,
  Adaptation.

### Papillon (advanced, from Doll Master or Trickster)
- **Role:** fights near or far with the fan, a special weapon; her skills are unusual too, even one that turns a
  weakened enemy into food (p147).
- **Niche:** a fast physical attacker with odd effects.
- **Unique:** the fan, Rose Queen, Materialize, Limit Field.
- **Own tools:** Rose Queen, Graceful Rose, Tinker Squash, Materialize, Limit Field, Illusion, Insurance, Esarhaddon,
  Elegant Dancing, Double Attack, Fan Mastery.

### Joker (advanced, from Trickster)
- **Role:** the reaper of the battlefield, wandering in search of blood, who offers her own blood to become a
  destroyer (p148).
- **Niche:** a physical attacker built on buffs and chance skills; unstable, overwhelming when it lands.
- **Unique:** Trump Card, Heaven or Hell, Showtime, Triple Joker, Life Bringer.
- **Own tools:** Trump Card, Heaven or Hell, Showtime, Mad Zapper, Life Bringer, Beast Binder, Murder, Avenger,
  Triple Joker, Axe Mastery.

---

## Using this page

For a change to a class or skill, the check is in words, beside the figures of the simulator:

1. Does the class still do what its **role** says, in its **niche**?
2. Is what makes it **unique** still its own, or does the change hand it to another class?
3. Does the change work through its **own tools** (fixing what is broken), rather than by giving it the tools of
   another class?
