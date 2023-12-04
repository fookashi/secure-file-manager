import unittest
from keygen.key_generator import RSAKeyGeneratorService
from prime_checkers import SolovayStrassenTester, FermatTester, MillerRabinTester
from numgen.number_generator import NumberGenerator


def is_prime(n):
    if n == 2 or n == 3: return True
    if n < 2 or n%2 == 0: return False
    if n < 9: return True
    if n%3 == 0: return False
    r = int(n**0.5)
    for f in range(5,r+1, 6):
        if n % f == 0: return False
        if n % (f+2) == 0: return False
    return True

class TestPrimalityCheckers(unittest.TestCase):
    def test_fermat_high_prob(self):
        keygen = RSAKeyGeneratorService(FermatTester(), NumberGenerator())
        keygen.generate_keys(0.99, 32)
        self.assertTrue(is_prime(keygen.p) and is_prime(keygen.q))

    def test_solovay_high_prob(self):
        keygen = RSAKeyGeneratorService(SolovayStrassenTester(), NumberGenerator())
        keygen.generate_keys(0.99, 32)
        self.assertTrue(is_prime(keygen.p) and is_prime(keygen.q))

    def test_miller_high_prob(self):
        keygen = RSAKeyGeneratorService(MillerRabinTester(), NumberGenerator())
        keygen.generate_keys(0.99, 32)
        self.assertTrue(is_prime(keygen.p) and is_prime(keygen.q))

    def test_fermat_low_prob(self):
        keygen = RSAKeyGeneratorService(FermatTester(), NumberGenerator())
        keygen.generate_keys(0.5, 32)
        self.assertTrue(is_prime(keygen.p) and is_prime(keygen.q))

    def test_solovay_low_prob(self):
        keygen = RSAKeyGeneratorService(SolovayStrassenTester(), NumberGenerator())
        keygen.generate_keys(0.5, 32)
        self.assertTrue(is_prime(keygen.p) and is_prime(keygen.q))

    def test_miller_low_prob(self):
        keygen = RSAKeyGeneratorService(MillerRabinTester(), NumberGenerator())
        keygen.generate_keys(0.5, 32)
        self.assertTrue(is_prime(keygen.p) and is_prime(keygen.q))





