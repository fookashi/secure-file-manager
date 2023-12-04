from math import ceil, log
from random import randint

from ..interfaces import IPrimalityTester
from ..utils.symbol_calculator import SymbolCalculator
from ..utils.gcd import extended_gcd
from .initial_check import initial_check


class SolovayStrassenTester(IPrimalityTester):
    def __init__(self):
        self.symbol_calculator = SymbolCalculator()

    def _single_iteration(self, n: int) -> bool:
        a = randint(2, n - 2)
        if extended_gcd(a, n)[0] > 1:
            return False
        leg = self.symbol_calculator.legendre(a, n)
        temp = pow(a, (n - 1) // 2, n)
        if leg == 0 or temp != leg % n:
            return False
        return True

    @initial_check
    def is_prime(self, n: int, p: float):
        error_p = 1 - p
        k = ceil(log(error_p, 0.5))
        for _ in range(k):
            if not self._single_iteration(n):
                return False
        return True
