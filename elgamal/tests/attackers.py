import unittest
from attacks import FermatAttacker, WienerAttacker
from keygen.key_generator import RSAKeyGeneratorService
from prime_checkers import FermatTester
from numgen.number_generator import NumberGenerator


class TestAttacks(unittest.TestCase):

    def setUp(self) -> None:
        key_gen = RSAKeyGeneratorService(FermatTester(), NumberGenerator())
        self.public_key, self.private_key = key_gen.generate_keys(0.99,32)
    def test_fermat_attacker(self):
        attacker = FermatAttacker()
        attacked_key = attacker.attack(self.public_key)
        self.assertEqual(attacked_key.d, self.private_key.d)

    def test_wiener_attacker(self):
        attacker = WienerAttacker()
        attacked_key = attacker.attack(self.public_key)
        self.assertEqual(attacked_key.d, self.private_key.d)
