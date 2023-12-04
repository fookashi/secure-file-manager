from abc import ABC, abstractmethod


class IPrimalityTester(ABC):

    @abstractmethod
    def _single_iteration(self, n: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_prime(self, n: int, p: float) -> bool:
        raise NotImplementedError