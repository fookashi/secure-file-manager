from math import ceil, log
from random import randint

from ..interfaces import IPrimalityTester
from .initial_check import initial_check


class FermatTester(IPrimalityTester):
    def _single_iteration(self, n: int) -> bool:
        a = randint(2, n - 2)
        return pow(a, n - 1, n) == 1

    @initial_check
    def is_prime(self, n: int, p: float) -> bool:
        error_p = 1 - p
        k = ceil(log(error_p, 0.5))
        for _ in range(k):
            if not self._single_iteration(n):
                return False
        return True
