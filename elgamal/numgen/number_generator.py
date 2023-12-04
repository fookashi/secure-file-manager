import os

from ..utils.transform import bytes2int
from ..interfaces import INumberGenerator



class NumberGenerator(INumberGenerator):

    def _read_random_bits(self, nbits: int) -> bytes:
        nbytes, rbits = divmod(nbits, 8)

        randomdata = os.urandom(nbytes)

        if rbits > 0:
            randomvalue = ord(os.urandom(1))
            randomvalue >>= 8 - rbits
            randomdata = bytes(randomvalue) + randomdata

        return randomdata

    def generate_number(self, nbits: int) -> int:
        randomdata = self._read_random_bits(nbits)
        value = bytes2int(randomdata)

        value |= 1 << (nbits - 1)

        return value | 1