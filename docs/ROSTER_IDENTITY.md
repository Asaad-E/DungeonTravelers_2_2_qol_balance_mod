# Roster identity: summons and mercenaries

What each summon of a grand sealbook and each mercenary of the tavern is for, as the game presents it. It is the soft
standard for their tuning, as `docs/CLASS_IDENTITY.md` is for the classes: a change of a summon or a mercenary is checked
against her entry, so that she reaches her niche without losing her identity.

**What may change.** Only the stats of a summon's forms and of a mercenary's stages, and the weights of their scripts
(the share of each attack in a set). Their attack lists are not changed, and neither are their passives.

**Sources.** The kit (attacks, their effects and scopes, the script weights) is read from the game files
(`SummonData`, `NPCData`, `EnemyAttackData`, `EnemyAIData`; `gamedata/data.py`). The personality comes from the game's
own text: the two-line profile of each mercenary in `NPC.pck`, the advice of the tavern keeper (`Script/ShopBar.pck`),
and the scene where each mutant is beaten and sealed (the dungeon packs `Dungeon/stNN`). The personality weighs little
in a decision: it decides only between two tunings that reach the niche equally, and says which kind of change would
feel wrong (a lazy summon made tireless, a support made a striker). The measured state lives in the generated reports:
`docs/generated/SEALBOOK_BATTERY.md`, `docs/generated/MERCENARY_BATTERY.md` and their charts.

**Three facts of the program that shape every entry** (`docs/FORMULAS.md` 16.5, 12.9, 12.13):

* The summon (unit 3000) and a mercenary (unit 3001) stand together; neither can be targeted, healed or hurt by the
  other side, and neither is a candidate of an ally's skill. They are free extra actions, never a body.
* Their actions start no answer of the other side: no Counter, Reprisal, Dark Aura, Slow Target or Support Shot
  follows an action of theirs, and they get none of the after-hit answers of their own side either.
* "Take Break" is an attack that does nothing. Every summon has it in its script: a summon idles part of the time by
  design (the game's own joke on summons), and so do the Three Fates.

Each entry: **role** (what it does), **niche** (when it is the right pick), **personality** (from the game's text),
**kit** (the attacks that carry the role), **keep** (what a change must not touch).

---

## Summons of the grand sealbooks

A grand sealbook gives the party its enchantment(s) and puts its summon in the battle; the summon takes the form the
party's mean level reaches. The niche of a book is the pair: what its enchantment does and what its summon does. The
books are listed by the level of their first form (the order the story offers them).

### Bigfoot (first form 7; enchantment: rate of status ailments dissipation UP)
- **Role:** early melee brute with a kick that delays turns.
- **Niche:** the first book; the plain extra hitter of the opening chapters.
- **Personality:** a mutant yeti with no scene of its own; the name is the identity.
- **Kit:** Attack, Bigfoot Kick (turn delay), Throwing Stone; Take Break three times (25 of 100).
- **Keep:** physical, simple, high ATK factor; the turn delay of the kick.

### Ghast (12; when at max HP, damage inflicted 10% UP)
- **Role:** heavy hitter with armour break and slow.
- **Niche:** an early damage book.
- **Personality:** no scene; a ghoul of the early dungeons.
- **Kit:** Attack, Solvent (DEF down), Slow (whole side, slow); Take Break 25.
- **Keep:** ATK the highest of the early forms; Slow as its support.

### Cupid (15; higher chance of shop encounters)
- **Role:** archer with a wide kit: two arrows, a sure shot, poison.
- **Niche:** an exploration book (shops) whose summon chips damage and poisons.
- **Personality:** no scene; the archer of love.
- **Kit:** Attack, Two Arrows, Guided Shot, Poison Shot; Take Break 30.
- **Keep:** a shooter, balanced stats, poison.

### Heqet (18; the smaller your party, the higher your damage)
- **Role:** water attacker, one target and a row.
- **Niche:** the book of small parties.
- **Personality:** "the distinguished frog", proud and theatrical, caught by her own frog-hood's tongue (st04).
- **Kit:** Attack, Water Gun, Waterjet Cutter (row); Take Break 35.
- **Keep:** water magic on a melee frame; a lazy summon (high Take Break).

### Eros (20; food likes and dislikes intensify)
- **Role:** charmer: kiss that silences, DEF and RES down, wind on a row.
- **Niche:** a food book whose summon disrupts casters.
- **Personality:** a seductive, insatiable mutant (st04); sealed at the Dragon Palace.
- **Kit:** Blow Kiss (silence), Pink Typhoon (row), Bra Unhooker (DEF and RES down); Take Break 35.
- **Keep:** debuffs and silence over raw damage.

### Molle (23; escape probability UP)
- **Role:** digger: paralysing claw and a drill on the back row.
- **Niche:** an escape book; the summon paralyses.
- **Personality:** a vain little mole proud of her digging gear ("I'm a Molle, not a Mole!", st05).
- **Kit:** Attack, Paralyzing Claw, Drill Rush (long reach); Take Break 35.
- **Keep:** paralysis as her trade.

### Serika (25; reduce damage penalty for missed spells)
- **Role:** witch of every element.
- **Niche:** a magic book: the only early summon that casts the five elements.
- **Personality:** no scene; a broom-riding witch.
- **Kit:** Fireball, Fire Blast, Thunderbolt, Thunder Chain, Air Cutter, Stone Hammer; Take Break 25.
- **Keep:** INT her best stat, the spread of elements.

### Deep Slapyon (28; damage from non-gas traps 90% DOWN)
- **Role:** stomper and curser (poison and silence on one).
- **Niche:** a trap book whose summon brings ailments.
- **Personality:** no scene; the deep cousin of the Slapyons.
- **Kit:** Attack, God Stamp, I'll Curse You (poison + silence); Take Break 35.
- **Keep:** the curse.

### Siesta (33; recover 3 TP every 10 steps)
- **Role:** sleeper: pillow that delays and puts to sleep, wind.
- **Niche:** an exploration book (TP on the map); the summon puts enemies to sleep.
- **Personality:** no scene; a sleepy pillow spirit.
- **Kit:** Attack, Pillow Toss (delay + sleep), Wind Fang, YES/NO Choice (script); Take Break 35.
- **Keep:** sleep; idle often (she is Siesta).

### Afanc (36; A-rank speed when no weapon is equipped)
- **Role:** clawed beast with every ailment of a claw: freeze, poison, paralysis, DEF down.
- **Niche:** the ailment brute of the middle story.
- **Personality:** no scene; a lake monster.
- **Kit:** Attack (freeze), Gnaw Armor, Poison Claw, Paralyzing Claw; Take Break 20.
- **Keep:** ailments on every blow.

### Martial Artist (38; attack vs. high lvl enemies UP)
- **Role:** the strongest fist of the middle story: strangle (stun), multi-hit punch, poison palm.
- **Niche:** a battle book for bosses above the party's level.
- **Personality:** no scene; a fighter of the Temple of Wrappl.
- **Kit:** Attack, Strangle (stun), Brawl Punch, Cinnabar Palm (poison); Take Break 30.
- **Keep:** ATK factor about 2, DEX high.

### Dragon Papi (42; gain more EXP from higher-level enemies)
- **Role:** dragon with claws, a small breath on a row and bashes that delay.
- **Niche:** the EXP book; the summon is a steady brute.
- **Personality:** no scene; the father of the Dragon Babies.
- **Kit:** Attack (paralysis), Dragon Claw, Mini Breath (row), Continuous Bash; Take Break 35.
- **Keep:** physical with fire on the side.

### Calliope (42; Pep decrease rate DOWN)
- **Role:** muse: a sleeping melody, a stunning song on a row, and Concentration Prelude for the party.
- **Niche:** a support summon (the only early one with a party song).
- **Personality:** no scene; the muse of epic poetry.
- **Kit:** Harpstring Melody (sleep), Alluring Song (row, stun), Concentration Prelude (party); Take Break 25.
- **Keep:** the song; her magic over her blows.

### Mangos Queen and Tres Durian (44; greatly increase / greatly reduce encounter rate)
- **Role:** fruit pair: Full Maturity raises their own ATK and DEF, then they hit with poison or paralysis.
- **Niche:** the two encounter-rate books; their summons are weak on purpose (the books are about the map).
- **Personality:** no scene; ripe fruit monsters of Mag Mell.
- **Kit:** Attack (poison / paralysis), Full Maturity (self), one hidden move each; Take Break 20.
- **Keep:** low stats: the book is chosen for its enchantment.

### Moby Dick (44; attack vs. low lvl enemies UP)
- **Role:** whale queen with a trident: silence sting, a sweep of all, an icicle to the back.
- **Niche:** a battle book for random battles (low-level enemies).
- **Personality:** "the proud queen of the whales", who despises humans and would rather die than yield (st12).
- **Kit:** Attack, Silence Sting, Bunmawashi (multi-target), Icicle Thrust (long, freeze); Take Break 30.
- **Keep:** proud and physical; silence.

### Death Cataphract (46; class weapon modifier 2% UP, attack vs. high lvl enemies UP)
- **Role:** war machine: protects the party (Circle Protect), sweeps a row, fires a cannon at the back.
- **Niche:** the tank-support summon of the late story.
- **Personality:** a calculating machine that refuses hopeless orders (st12: "Probability of victory: 0.00%").
- **Kit:** Attack, Circle Protect (party DEF up), Clean Sweep (row), Buster Cannon (long); Take Break 25.
- **Keep:** DEF its best factor, Circle Protect. Its own enchantment (+2% of a class weapon modifier) is small; the
  book carries a second one, Attack vs. high lvl enemies UP, for the bosses above the party's level.

### Sahohime (48; HP recovers while defending)
- **Role:** spring goddess at a kotatsu: stuns, fire on a row, fire scroll, Sun Veil for the party.
- **Niche:** defensive book; a summon that mixes damage and a party RES buff.
- **Personality:** no scene; the goddess of spring.
- **Kit:** Kotatsu Bash (stun), Heat Wave, Fire Scroll, Sun Veil, Nurse (script); Take Break 20.
- **Keep:** Sun Veil, the stun.

### Scanner (52; magic incantations go very fast... sometimes)
- **Role:** psychic: electric uppercut (stun), energy ball and wave.
- **Niche:** a magic book (chant speed) whose summon hits hard.
- **Personality:** reads hearts; lonely, she waited for someone whose heart is pure (st13).
- **Kit:** Attack, Electric Uppercut (stun), Energy Ball, Energy Wave (all); Take Break 25.
- **Keep:** ATK and INT both high.

### Iron Maiden (55; damage to enemies with status ailments UP)
- **Role:** torture device: crushers that lower AGI, DEX, ATK and DEF, stone shower on a row.
- **Niche:** the ailment party's book; the summon debuffs.
- **Personality:** no scene.
- **Kit:** Attack, Iron Crusher, Skull Crusher, Stone Shower; Take Break 25; a passive of her own.
- **Keep:** the debuffs.

### Kaguya (60; higher lvl equipment from treasure boxes)
- **Role:** moon princess: smash, a halving slice on a row, moonlight, Rainy Crescent (DEX down on all).
- **Niche:** a treasure book with a strong summon.
- **Personality:** a vain "monster idol", princess of the moon, who wants sweets and apologies (st03).
- **Kit:** Raging Smash, Halving Slice, Moonlight, Rainy Crescent, Harvest Moon (script); Take Break 25.
- **Keep:** high ATK and INT, low DEF and RES: a diva, not a wall.

### Iktomi (66; back line INT + RES 4% UP)
- **Role:** spider trickster: slow, paralysis, poison on all, a net that slows all.
- **Niche:** back-line casters' book; the summon controls.
- **Personality:** no scene; the spider of legends.
- **Kit:** Gotcha! (slow), Got Your Heart! (paralysis), Bat Spell (all, poison), Spider Net (all, AGI down);
  Take Break 20; a passive.
- **Keep:** control over damage.

### Sukuna-Hikona (68; back line DEX + AGI 2% UP)
- **Role:** the twin little gods: curse, stun needle, mallet that lowers ATK and DEF, petrifying arrow.
- **Niche:** the most varied ailment summon of the late story.
- **Personality:** two that are one ("Together, we are Sukuna-Hikona"), bickering and protective of each other (st20).
- **Kit:** Kunitsukami Curse, Stun Needle, Munchkin Mallet, Petrifying Arrow, Stone Shower; Take Break 20.
- **Keep:** the spread of ailments; small and quick (DEX, AGI).

### Overdue (68; increase Mimic appearance rate in chests)
- **Role:** the mimic: sleep, paralysis and slow on all, a surprise fist.
- **Niche:** a joke book (more Mimics); the summon is a disabler.
- **Personality:** no scene; an overdue library book.
- **Kit:** Surprise Fist, Sleep, I'll Torment Everyone, Dispel and Honey Great (script); Take Break 30.
- **Keep:** DEF and RES its best factors; the enchantment is a joke and stays one.

### Qitian Dasheng (70; critical rate UP)
- **Role:** the monkey king: chain club, wind scroll, rampage, piledriver (stun).
- **Niche:** the critical book; a fast physical summon.
- **Personality:** boastful ("the greatest, smartest, noblest person in the entire world"), sore loser (st21).
- **Kit:** Chain Club, Wind Scroll, Rampage, Ninja Piledriver; Take Break 25.
- **Keep:** ATK about 2, DEX high; a show-off.

### Azathoth (73; joint skill damage MegaUP)
- **Role:** outer god: purgatory flame on a row, paralysis on all, magical spark, slow.
- **Niche:** the joint-skill book (joint skills are out of the model); the summon is a caster.
- **Personality:** no scene.
- **Kit:** Purgatory Flame, Dark Whisper, Magical Spark, Slow; Take Break 35.
- **Keep:** INT its best; the book is chosen for joint skills.

### Kuchinawa (75; increase Mercenary Buddy stats by 30)
- **Role:** serpent: claw, a bite that ignores DEF, a three-ailment venom, a petrifying tail.
- **Niche:** the mercenary book: the one to carry beside a hired mercenary.
- **Personality:** no scene; the snake of the ruined shrine.
- **Kit:** Dragon Claw, Masticate, Cursevenom, Petrify Tail; Take Break 20; a passive.
- **Keep:** ATK the highest of its stretch; the venom.

### Genbu (76; front line ATK + DEF 4% UP and HP recovers while defending)
- **Role:** black tortoise: shields the party (Defensive Shielding), spins on all, curses with slow.
- **Niche:** the front line's book; a tank-support summon.
- **Personality:** no scene.
- **Kit:** Giant Rotation, Turtle's Curse, Defensive Shielding; scrolls in the script; Take Break 30.
- **Keep:** DEF high, AGI low; the shield.

### Nuwa (79; TP cost for techniques DOWN)
- **Role:** snake goddess: snake eyes (paralysis on a row), bladestorm, strangle, mince, shadow sew.
- **Niche:** the technique book; a disabling striker.
- **Personality:** "a proud snake god" who demands to be humiliated as the loser, then melts when examined (st22).
- **Kit:** Snake Eyes, Bladestorm, Strangle, Mince, Shadow Sew; Take Break 25.
- **Keep:** ATK above 2; shadow sew.

### Murasaki Shikibu (82; TP recovers slightly while defending and rate of ailments dissipation UP)
- **Role:** the poet: brushstrokes, a calligraphy on a row, Blissful Chorale for the party.
- **Niche:** a sustain book; the summon heals the party's TP with a song.
- **Personality:** no scene; the author of the Tale of Genji.
- **Kit:** Brushstroke, Kakizome, Blissful Chorale; Rumbling Thunder and Summon Shikigami in the script;
  Take Break 30.
- **Keep:** the chorale.

### Last Judgment (83; may rarely recover all HP when turn starts)
- **Role:** the judge: a stunning cry on a row, dark judgment, a hand that ignores DEF, prism dawn, paralysis on all.
- **Niche:** a postgame battle book.
- **Personality:** no scene.
- **Kit:** Great Cry, Dark Judgment, Shudderhand, Prism Dawn, Paralyze; Take Break 20.
- **Keep:** a mixed kit of damage and control.

### Hell's Angel (92; unique skill level +1)
- **Role:** biker angel: long-reach strikes, Full Throttle (self), Aura Eliminate (dispel).
- **Niche:** the unique-skill book of the end of the postgame; its first form (92) is above every checkpoint the
  battery plays, so it has no measured cell.
- **Personality:** no scene.
- **Kit:** Ether Strike, Screw Blast, Drill Lance Attack, Hell Runneth Over, Full Throttle, Aura Eliminate;
  Take Break 30.
- **Keep:** ATK the highest of all forms but the last two books; dispel.

### Samael (88; back line INT 8% UP)
- **Role:** the serpent of the fruit: inferno and godpoison on all, a fruit that sews shadows, overrun.
- **Niche:** the back line's book of the postgame; a summon that never idles.
- **Personality:** a temptress who wants to rule monsters and "reclaim our era of paradise and slaughter" (st13).
- **Kit:** Inferno, Forbidden Fruit, Godpoison, Overrun (no Take Break weight).
- **Keep:** her full-time activity and balanced high stats: a final book.

### Melek Taus (90; front line ATK 8% UP and critical rate UP)
- **Role:** the peacock angel: iron hammer (instant death), megaton press, attack with freeze.
- **Niche:** the front line's book of the postgame.
- **Personality:** proud, likes "a strong, smart man", serves only while not bored (st14).
- **Kit:** Attack, Iron Hammer of Death, Megaton Press; Take Break 25.
- **Keep:** the highest ATK factor of all summons.

### Default (42; TP cost for spells DOWN)
- A grand sealbook whose record is named "Default" in the game files; the battery measures it like the others. Its
  summon follows the record it points to; it is left as it is.

---

## Mercenaries of the tavern

A mercenary is hired for a number of battles and stands beside the summon (`docs/FORMULAS.md` 16.5). The bar offers,
of her stages whose story flag is open, the highest (sheet `MercenaryUnlocks`). Every mercenary but the Three Fates
must have a niche where she is worth her fee and none may dominate (decided 2026-10-17); the Three Fates are an
in-game joke and stay one. The battery measures each against a band of points (`mercenary_band` of
`data_tables/measure_config.json`).

### Euphemia (stages 26 - 67; from C25)
- **Role:** physical attacker with War Cry for the party.
- **Niche:** a physical party in the middle story ("she's sure to come in handy" with physical attackers, says the
  keeper); cheap.
- **Personality:** short, cute and hard-working; a militia police assistant who directs carriages and finds lost
  children.
- **Kit:** Raging Smash, Painful Strike, Bunmawashi, Cruciform Slash, Shock Spiral, Move Big Brother!, War Cry;
  Double Attack.
- **Keep:** War Cry; cheap and steady, never the strongest.

### Chloe (30 - 68; from C25)
- **Role:** archer of ailments: poison, freeze, slow, a sure shot; Support Shot and Warning Shot.
- **Niche:** an early mercenary for a party that wants ailments on the enemy.
- **Personality:** took up mercenary work to protect her village; searching for comrades lost in the chaos.
- **Kit:** Guided Shot, Poison Shot, Freeze Shot, Gravity Shot; Support Shot, Warning Shot.
- **Keep:** the ailment shots.

### Natalia (28 - 68; from C25)
- **Role:** combat nun: heals (Full Heal, Mini Circle Heal), hits with light and stuns, poisons and terrorises.
- **Niche:** the first healer for hire ("she knows Heal, so she's very useful").
- **Personality:** "a bonafide nun, in spite of her personality": moody, relegated to a frontier church.
- **Kit:** Electric Uppercut, Bloodbath, Prism Dawn, Poison, Terrorize; Full Heal and Mini Circle Heal by script.
- **Keep:** a healer who would rather fight: her heals by condition, her blows by weight.

### Estelle (30 - 70; from C25)
- **Role:** bard: songs (Spiritual Fantasia, Reading Requiem, Sacred Hymn, Replenishing Carol, Barrage Rondo) and two
  debuff dances.
- **Niche:** the party's songs without a Diva; her songs and dances cannot be stopped by enemy attacks (the keeper's
  advice).
- **Personality:** a wandering bard who collects stories and legends; caught in Romulea by chance.
- **Kit:** five songs, Gravitating Polka, Gloomy Tango, Wind Fang, String Serenade.
- **Keep:** support only; the unstoppable songs.

### Momona (32 - 58; from C27)
- **Role:** maid of the party's TP: Cook, Lullaby, ailment sweets, debilitating dances.
- **Niche:** sustain of TP and sleep ("rather than attacking, she helps out by healing everybody's TP with Cook").
- **Personality:** a housemaid of a merchant family who wants Romulea back so she can return to work; knows she is no
  fighter.
- **Kit:** Cook, Lullaby, Here's Some Suspicious Sweets, 2 a.m., Debilitating Salsa, Dumbing Mazurka.
- **Keep:** weak attack, strong support.

### Medved (33 - 59; from C27)
- **Role:** veteran swordsman: Cross Slash against undead, demons and apparitions; bear claw, armour gnaw.
- **Niche:** fights against undead and demons ("his standout skill is Cross Slash").
- **Personality:** a former Raiders Captain of the Band of the Bear; seasoned, with a sword bigger than he is, and
  "a certain musk".
- **Kit:** Tokatpuci, Cross Slash, It's a Road Roller!, Bear Claw, Gnaw Armor, Wait and See.
- **Keep:** Cross Slash and the race bonus.

### Peggy & Beard (35; from C28)
- **Role:** jack of all trades: Bible Thump, War Cry, Fireball, Honey, Wait and See.
- **Niche:** the game's own answer to Calliope (C29): the one boss she can be taken to, where her Fireball from INT 500
  passes the boss's heal wall (atwiki dt2-2 page 227). Offered at C28 - C29 only; she keeps the values of the game and
  is exempt from the band of the mercenaries.
- **Personality:** a penguin who can't communicate and a rare Libra Beard, "always up to no good".
- **Kit:** Bible Thump, War Cry, Fireball, Honey, Wait and See; Take Break 20.
- **Keep:** the mix and the idle share.

### Tatiana (36 - 72; from C30)
- **Role:** knight: dispel, shield bash, mince, Material Guard and Charge.
- **Niche:** against buffing enemies (Aura Eliminate) and as a guard for the party.
- **Personality:** a soldier of the Royal Order; Alisia's senpai from Knight Studies.
- **Kit:** Aura Eliminate, Shield Bash, Mince, Gust Thrust, Lifetaker Edge, Material Guard, Charge.
- **Keep:** dispel and the guard.

### Carol (37 - 91; from C30)
- **Role:** freelance mage: area spells of three elements, Energy Ball, paralysis, Loose Spirit.
- **Niche:** magic damage for hire through the late story.
- **Personality:** a freelance mage happy to hunt bounties or monsters; learned magic at a private school.
- **Kit:** Energy Ball, Lightning, Diamond Dust, Tornado, Loose Spirit; Muon Plasma, Gaia Crush, Paralyze by script.
- **Keep:** a caster: INT her best.

### Priscilla (39 - 78; from C34)
- **Role:** maid initiate: First Aid, Dust Up (party buffs), Carry Me!, Holy Gavel.
- **Niche:** a healer and buffer of the late story.
- **Personality:** a Royal Maid Squadron initiate with a homemade featherduster; likes washing, cleaning and
  milkshakes.
- **Kit:** Dust Up, Carry Me!, Boulder Toss, Holy Gavel; First Aid and Broom Attack by script.
- **Keep:** First Aid as her main gift.

### Rebecca (43 - 82; from C34)
- **Role:** treasure hunter: Gold Steal and Item Steal, quick stabs, nets.
- **Niche:** gold and drops (her steals are out of the fight's figures).
- **Personality:** "can't resist the smell of loot"; looking to profit from the chaos.
- **Kit:** Gold Steal, Item Steal, Got Your Heart!, Sharp Stab, Hard Whipping, Gotcha!.
- **Keep:** the steals at the top of her script.

### Paracas (42 - 62; from C35)
- **Role:** doll master: Oracles and Catalina, Double Puppet.
- **Niche:** dolls beside the party's own (a mercenary's dolls do not replace the party's, the keeper's "super useful
  tactic").
- **Personality:** a Therian puppeteer of a travelling circus, reduced to merc work by the gig shortage.
- **Kit:** Oracles, Catalina, Cinnabar Palm; Double Puppet.
- **Keep:** dolls first.

### Luzie (45 - 87; from C35)
- **Role:** lancer: poison, paralysis, death, long-reach charges; Circle Protect for the party.
- **Niche:** a front-line helper with a party DEF buff.
- **Personality:** a member of a frontier mercenary band, born in Actim, eager to save Romulea.
- **Kit:** Poison Spear, Backward Swing, Skewer, Let's Charge!, Ether Strike, Mach Stab, Circle Protect.
- **Keep:** Circle Protect, the reach.

### Mekelle (46 - 63; from C35)
- **Role:** Iga kunoichi: ailment strike, scrolls, Phoenix, piledriver; Double Attack.
- **Niche:** a fast mixed attacker of the late story.
- **Personality:** a kunoichi of the Iga style, "inexpressibly nimbler than her appearance would suggest".
- **Kit:** I'll Torment You, Light Scroll, Water Scroll, Earth Scroll, Ninja Piledriver, Phoenix.
- **Keep:** speed and the scrolls.

### Sasha (47 - 88; from C35)
- **Role:** royal mage: Bible Thump, Sun Veil, Sleep, Rainbow Flash, Tempest, Stab Smash; Circle Nurse by script.
- **Niche:** cures ("Sasha's Nurse skill is really powerful... well worth hiring" when no one knows Nurse).
- **Personality:** a high-ranking mage of the royal court, bored of peace and glad of the excitement.
- **Kit:** as above.
- **Keep:** the cure as her reason to be hired.

### Marion (48 - 86; from C36)
- **Role:** doll master: Spartan, Catalina, Musiy, Summon Slave; Absolutely No Freebies (gold steal).
- **Niche:** dolls beside the party's own, the strongest doll mercenary.
- **Personality:** a doll master whose dolls are "suspiciously cat-themed"; once a street performer in Actim.
- **Kit:** Spartan, Catalina, Musiy, Summon Slave, Absolutely No Freebies; Double Attack.
- **Keep:** dolls first.

### Riesco (49 - 65; from C36)
- **Role:** Therian with a morningstar and ice: chain club, frost slash, icy tentacle, freezing sigh.
- **Niche:** ice and freeze in the late story.
- **Personality:** fond of her morningstar; "here to make sure that the humans don't screw this up".
- **Kit:** Chain Club, Freezing Sigh, Icy Tentacle, Frost Slash.
- **Keep:** freeze.

### Neya (50 - 89; from C36)
- **Role:** elite battlemaid: scrolls of three elements, Bra Unhooker, Ultimate Maid Frenzy; Cook and Military
  Rations Pill by script; Triple Attack.
- **Niche:** a support who also fights; heals and cures the party.
- **Personality:** an elite of the Royal Maid Squadron, "from cooking to assassination, she can do it all".
- **Kit:** as above.
- **Keep:** both halves, maid and assassin.

### Azmaria (50 - 93; from C37)
- **Role:** self-proclaimed magical girl who fights with her fists: Fist of Justice, Air Throw, Justice, War Cry;
  Double and Triple Attack.
- **Niche:** a physical attacker of the end of the story and the postgame.
- **Personality:** "fights for love, justice, etc."; loud ("Destroy!" when she eats), painfully cringe.
- **Kit:** Fist of Justice, Painful Strike, Grit Your Teeth!, Air Throw, Miracle Azmaria Kick, War Cry, Justice,
  Faux Magical Spark.
- **Keep:** physical blows dressed as magic.

### Miranda (53 - 90; from C38)
- **Role:** gunner: gun attacks, Buster Cannon EX, Happy Trigger, Lock-On Snipe; Warning Shot and Support Shot.
- **Niche:** long-range damage of the late story and the postgame.
- **Personality:** a gunner from Tajar with a "mechanical deathtube", who gets angry when someone tries to pass her.
- **Kit:** as above.
- **Keep:** the gun.

### Euthys (74 - 99; from P08)
- **Role:** the combat instructor: Blood Carnival, Shock Spiral, Fiery Ring of Iron, Megingjoro, Fervent Discipline;
  Full Heal by script; Triple Attack.
- **Niche:** a strong all-rounder of the postgame.
- **Personality:** the strict, mysterious instructor of the Hall of Secrets ("That's 'Ms. Euthys' to you!"); must never
  be given alcohol.
- **Kit:** as above.
- **Keep:** discipline: a teacher who buffs and punishes.

### Lolo (86 - 93; from P24)
- **Role:** the fairy: jibes, Fairy Attack, Make Way for Lolo!, Tempest, Resurrect and Fairy Healing by script.
- **Niche:** the late postgame helper who heals and revives.
- **Personality:** a forest fairy who runs up debts at the casino, sides with whoever pays, and eats on Fried's bill.
- **Kit:** as above; Take Break 15.
- **Keep:** her revive; a little lazy.

### Three Fates (85 - 93; from P24)
- **Role:** three goddesses (?) with a little of everything and Take Break half the time.
- **Niche:** none by design: an in-game joke ("they take a LOT of breaks"); exempt from the band.
- **Personality:** "eat like pigs and smell like a barn"; three-for-one.
- **Keep:** the breaks.

### Arjuna, Citlalinicue, Marduk, Yoshitsune (95 - 99)
- **Role:** the four wandering warriors met as optional bosses; hired, each is a top fighter of her kind (archer, brute,
  war puppet, swordswoman).
- **Niche:** the strongest mercenaries of the postgame; not in the battery (they open after its last checkpoint).
- **Personality:** they abandon a job to chase a stronger monster (the keeper's complaint); Arjuna a mad archer,
  Citlalinicue soft-mannered but fond of brute force and baths, Marduk a destruction puppet who dozes in the sun,
  Yoshitsune a battle-lover who cooks anything.
- **Keep:** as they are.

### Michelle (30)
- A story guest of the Temple of Wrappl, not a mercenary of the tavern; out of the balance.
