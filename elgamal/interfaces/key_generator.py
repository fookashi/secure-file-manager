from abc import ABC, abstractmethod

class IRSAKeyGenerator(ABC):
    @abstractmethod
    def generate_keys(self, min_probability: float, key_length: int):
        raise NotImplementedError
