from abc import ABC, abstractmethod

class INumberGenerator(ABC):

    @abstractmethod
    def generate_number(self, nbits: int) -> int:
        raise NotImplementedError

    