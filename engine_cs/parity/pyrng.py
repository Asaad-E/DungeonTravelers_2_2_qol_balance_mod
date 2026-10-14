"""
A random.Random that counts the 32-bit words it consumes and can log every draw, for the traces of the parity tests.
It changes nothing of what the generator returns: the methods of the standard library run on top of getrandbits() and
random() exactly as they do for a plain random.Random.
"""
import math
import random


def fmt_num(x):
    """The number format shared with the C# traces (Fmt.Num): integral values below 1e15 as integers."""
    if isinstance(x, bool):
        return str(int(x))
    if isinstance(x, int):
        return str(x)
    if x != x:
        return 'nan'
    if x in (math.inf, -math.inf):
        return 'inf' if x > 0 else '-inf'
    if x == int(x) and abs(x) < 1e15:
        return str(int(x))
    return repr(x)


class CountingRandom(random.Random):
    def __init__(self, seed=None):
        self.words = 0
        self.log = None
        super().__init__(seed)

    def random(self):
        value = super().random()
        self.words += 2
        if self.log is not None:
            self.log.append('random -> ' + fmt_num(value))
        return value

    def getrandbits(self, k):
        value = super().getrandbits(k)
        if k > 32:
            raise NotImplementedError('more than 32 bits')
        if k > 0:
            self.words += 1
            if self.log is not None:
                self.log.append(f'bits({k}) -> {value}')
        return value
