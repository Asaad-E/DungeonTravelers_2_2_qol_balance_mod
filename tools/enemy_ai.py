"""
Enemy behaviour: decoder of EnemyAIData.bin (one per enemy inside Enemy.pck).

Layout and meaning are read from the executable (docs/FORMULAS.md 9): parser 0x431690, value reader 0x4319d0,
check 0x431aa0, result 0x432fd0, sources 0x432690, target change 0x433350, runner 0x430f10.

    script   = enemy id (u16, big endian), commands, 0xFF
    command  = id byte, arguments, result word (u16, big endian), two tail bytes
               command 0 (a set of weights) and command 1 (target change) have no result and no tail
               a command chained by a result word has no id byte and no tail

    python tools/enemy_ai.py [enemy name ...]     prints the decoded script of those enemies
"""
import sys

END = 0xFF
SET, TARGET = 0, 1
WEIGHTS = 16
# arguments before the result word: 'w' a word (u16, big endian), 'b' a byte
ARGUMENTS = {1: 'wb', 2: 'w', 3: 'bb', 4: 'b', 5: 'w', 6: 'w', 7: 'wb', 9: '', 10: 'bb', 11: 'b', 12: 'bb', 13: 'bb',
             14: 'bb', 15: 'w'}
COMMANDS = {0: 'set of weights', 1: 'change the target of a skill', 2: 'turns taken + 1 <= N', 3: 'source <= N',
            4: 'source', 5: 'last skill used is this one', 6: 'this skill is active',
            7: 'this skill was used N times or more', 9: 'an ally is dead', 10: 'source > N', 11: 'source',
            12: 'source >= N', 13: 'source < N', 14: 'source == N', 15: 'this skill reached its use limit'}
# jump table 0x432fa0
SOURCES = ('own HP ratio', 'lowest HP ratio among allies', 'lowest HP ratio among opponents',
           'lowest TP ratio among allies', 'lowest TP ratio among opponents', 'an ally has an ailment',
           'an opponent has an ailment', 'an opponent is chanting', 'an opponent is in the back row',
           'an opponent is in the front row', 'an opponent has a buff', 'an ally has a debuff')
# jump table 0x434754
TARGETS = ('ally with the lowest HP ratio', 'opponent with the lowest HP ratio', 'ally with the lowest TP ratio',
           'opponent with the lowest TP ratio', 'ally with the heaviest ailment', 'opponent with the heaviest ailment',
           'chanting opponent', 'opponent in the back row', 'ally without the effect of the skill',
           'ally with a more serious ailment', 'opponent in the front row', 'opponent with a buff',
           'ally with a debuff', 'ally with an ailment', 'opponent with an ailment', 'dead ally')
# flags of a result word and of a skill word
CHAIN, TO_SET, SLOT, ATTACK_ID = 0x1000, 0x2000, 0x4000, 0x8000
USES_SOURCE = (3, 4, 10, 11, 12, 13, 14)


def _command(b, pos, cid=None):
    top = cid is None
    if top:
        cid = b[pos]
        pos += 1
    if cid == SET:
        return {'cmd': SET, 'set': b[pos], 'weights': list(b[pos + 1:pos + 1 + WEIGHTS])}, pos + 1 + WEIGHTS
    if cid not in ARGUMENTS:
        raise ValueError(f'not an AI command: {cid} at byte {pos - 1}')
    args = []
    for kind in ARGUMENTS[cid]:
        size = 2 if kind == 'w' else 1
        args.append(int.from_bytes(b[pos:pos + size], 'big'))
        pos += size
    out = {'cmd': cid, 'args': args}
    if cid == TARGET:
        return out, pos
    out['result'] = int.from_bytes(b[pos:pos + 2], 'big')
    pos += 2
    if out['result'] & CHAIN:
        out['and'], pos = _command(b, pos, out['result'] & 0x0FFF)
    if top:
        out['once'], out['stop'] = bool(b[pos]), bool(b[pos + 1])
        pos += 2
    return out, pos


def decode(blob):
    """The script of an enemy: {'id', 'opening': commands before the first set, 'sets': {number: {'weights',
    'commands'}}}. The commands after a set belong to it (the parser files them under the set it read last)."""
    b = bytes(blob)
    script = {'id': int.from_bytes(b[:2], 'big'), 'opening': [], 'sets': {}}
    pos, current = 2, None
    while b[pos] != END:
        command, pos = _command(b, pos)
        if command['cmd'] == SET:
            current = script['sets'].setdefault(command['set'], {'weights': command['weights'], 'commands': []})
        elif current is None:
            script['opening'].append(command)
        else:
            current['commands'].append(command)
    if pos != len(b) - 1:
        raise ValueError(f'the script ends at byte {pos} of {len(b)}')
    return script


def commands_of(script):
    """Every command of a script, chained ones included."""
    stack = list(script['opening']) + [c for s in script['sets'].values() for c in s['commands']]
    while stack:
        command = stack.pop()
        yield command
        if 'and' in command:
            stack.append(command['and'])


def skill(word):
    if word & SLOT:
        return f'slot {word & 0x3FFF}'
    if word & ATTACK_ID:
        return f'attack {word & 0x3FFF}'
    return f'word {word:#06x}'


def describe(command):
    cid, args = command['cmd'], command.get('args', [])
    if cid == TARGET:
        return f'{skill(args[0])} aims at: {TARGETS[args[1]]}'
    text = COMMANDS[cid]
    if cid in USES_SOURCE:
        text = text.replace('source', SOURCES[args[0]])
        if len(args) > 1:
            text = text.replace('N', str(args[1]))
    elif cid in (5, 6, 7, 15):
        text = text.replace('this skill', skill(args[0])).replace('this one', skill(args[0]))
        if len(args) > 1:
            text = text.replace('N', str(args[1]))
    elif cid == 2:
        text = text.replace('N', str(args[0]))
    result = command['result']
    if result & CHAIN:
        return f'{text} and {describe(command["and"])}'
    then = f'set {result & 0x0FFF}' if result & TO_SET else skill(result)
    notes = [n for n, on in (('once', command.get('once')), ('stop', command.get('stop'))) if on]
    return f'{text} -> {then}' + (f' ({", ".join(notes)})' if notes else '')


def describe_script(script):
    lines = [f'  if {describe(c)}' for c in script['opening']]
    for number, entry in sorted(script['sets'].items()):
        weights = {slot: w for slot, w in enumerate(entry['weights']) if w}
        lines.append(f'  set {number}: ' + ', '.join(f'slot {slot} {w}' for slot, w in weights.items()))
        lines += [f'    {describe(c)}' if c['cmd'] == TARGET else f'    if {describe(c)}' for c in entry['commands']]
    return lines


def main():
    import enemy_data
    sys.stdout.reconfigure(encoding='utf-8')
    for enemy in enemy_data.enemies():
        if enemy['name'] in sys.argv[1:]:
            print(f"{enemy['name']} (id {enemy['id']}, attacks {enemy['attacks']})")
            print('\n'.join(describe_script(decode(enemy['ai']))))


if __name__ == '__main__':
    main()
