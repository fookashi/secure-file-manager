from math import ceil, log
from random import randint

from ..interfaces import IPrimalityTester
from .initial_check import initial_check


class MillerRabinTester(IPrimalityTester):
    def __init__(self):
        self.r = None
        self.d = None

    def _single_iteration(self, n: int) -> bool:
        # Вычислить параметры n-1 = 2^r * d, где d - нечётное
        a = randint(2, n - 2)
        x = pow(a, self.d, n)

        if x == 1 or x == n - 1:
            return True

        for _ in range(self.r - 1):
            x = (x * x) % n
            if x == n - 1:
                return True

        return False

    @initial_check
    def is_prime(self, n: int, p: float) -> bool:
        error_p = 1 - p
        k = ceil(log(error_p, 0.25))

        self.r, self.d = 0, n - 1
        while self.d % 2 == 0:
            self.r += 1
            self.d //= 2

        for _ in range(k):
            if not self._single_iteration(n):
                return False
        return True
