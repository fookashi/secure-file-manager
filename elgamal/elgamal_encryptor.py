import random
from math import ceil

from .interfaces import IRSAEncrypter
from .keys import ElGamalPrivateKey, ElGamalPublicKey



class ElGamalEncryptionService(IRSAEncrypter):

    def encrypt(self, data: bytes, public_key: ElGamalPublicKey):
        if len(data) == 0:
            return data
        key_size_bytes = ceil(public_key.p.bit_length() / 8)
        ciphertext = bytearray()
        for byte in data:
            k = random.randint(1, public_key.p - 2)
            c1 = pow(public_key.g, k, public_key.p)
            c2 = (pow(public_key.y, k, public_key.p) * byte) % public_key.p
            ciphertext.extend(c1.to_bytes(key_size_bytes))
            ciphertext.extend(c2.to_bytes(key_size_bytes))

        return ciphertext

    def decrypt(self, data: bytes, private_key: ElGamalPrivateKey):
        if len(data) == 0:
            return bytearray()
        
        plaintext = bytearray()
        key_size_bytes = ceil(private_key.p.bit_length() / 8)
        for i in range(0, len(data), key_size_bytes * 2):
            c1 = int.from_bytes(data[i:i + key_size_bytes], 'big')
            c2 = int.from_bytes(data[i + key_size_bytes:i + key_size_bytes * 2], 'big')
            s = pow(c1, private_key.x, private_key.p)
            plaintext_byte = (c2 * pow(s, -1, private_key.p)) % private_key.p
            plaintext.append(plaintext_byte)

        return plaintext


