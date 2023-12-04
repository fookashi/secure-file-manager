from abc import ABC, abstractmethod


class IRSAEncrypter(ABC):
    @abstractmethod
    def encrypt(self, data):
        raise NotImplementedError

    @abstractmethod
    def decrypt(self, data):
        raise NotImplementedError