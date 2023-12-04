from ..interfaces import IRSAKeyGenerator, IPrimalityTester, INumberGenerator
from ..utils.gcd import calculate_mod_inverse
from ..utils.prim_root import find_primitive_root
from ..keys import RSAPrivateKey, RSAPublicKey, ElGamalPrivateKey, ElGamalPublicKey
from random import randint


class RSAKeyGeneratorService(IRSAKeyGenerator):
    def __init__(self, prime_checker: IPrimalityTester, number_generator: INumberGenerator):
        self.prime_checker = prime_checker
        self.number_generator = number_generator




    def generate_keys(self, min_probability: float, key_length: int):
        if key_length % 8 != 0:
            raise ValueError("Key length must be power of 2 and more or equal 8")

        while p := self.number_generator.generate_number(key_length//2):
            if self.prime_checker.is_prime(p, min_probability):
                break

        while q := self.number_generator.generate_number(key_length//2):
            if self.prime_checker.is_prime(q, min_probability):
                break

        n = p * q
        phi_n = (p - 1) * (q - 1)
        e = 65537
        d = calculate_mod_inverse(e, phi_n)
        public_key = RSAPublicKey(n, e)
        private_key = RSAPrivateKey(n, d)
        return public_key, private_key


class ElGamalKeyGeneratorService(IRSAKeyGenerator):
    def __init__(self, prime_checker: IPrimalityTester, number_generator: INumberGenerator):
        self.prime_checker = prime_checker
        self.number_generator = number_generator

    def generate_keys(self, min_probability: float, key_length: int):
        if key_length % 8 != 0:
            raise ValueError("Key length must be a multiple of 8")

        # Choose a large prime p
        while p := self.number_generator.generate_number(key_length//2):
            if self.prime_checker.is_prime(p, min_probability):
                break
            
        # Choose a generator g
        g = find_primitive_root(p)
        # Choose a private key x
        x = randint(1, p - 1)

        # Compute public key y
        y = pow(g, x, p)
        
        public_key = ElGamalPublicKey(p, g, y)
        private_key = ElGamalPrivateKey(p, g, x)
        return public_key, private_key

