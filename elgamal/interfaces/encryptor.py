from abc import ABC, abstractmethod
from ..keys import ElGamalPrivateKey, ElGamalPublicKey


class IRSAEncrypter(ABC):
    
    @abstractmethod
    def encrypt(self, data: bytes, public_key: ElGamalPublicKey):
        raise NotImplementedError
    
    @abstractmethod
    def decrypt(self, data: bytes, private_key: ElGamalPrivateKey):
        raise NotImplementedError
