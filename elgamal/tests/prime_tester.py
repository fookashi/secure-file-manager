import unittest
from prime_checkers import SolovayStrassenTester, FermatTester, MillerRabinTester


class TestPrimalityCheckers(unittest.TestCase):

    def setUp(self) -> None:
        self.simple_numbers = [3, 13, 103]
        self.composite_numbers = [4, 8, 102, 100, 1000]

    def test_simple_numbers_fermat(self):
        tester = FermatTester()
        for number in self.simple_numbers:
            self.assertTrue(tester.is_prime(number,0.99))


    def test_simple_numbers_miller(self):
        tester = MillerRabinTester()
        for number in self.simple_numbers:
            self.assertTrue(tester.is_prime(number,0.99))

    def test_simple_numbers_solovay(self):
        tester = SolovayStrassenTester()
        for number in self.simple_numbers:
            self.assertTrue(tester.is_prime(number,0.99))


    def test_composite_number_fermat(self):
        tester = FermatTester()
        for number in self.composite_numbers:
            self.assertFalse(tester.is_prime(number,0.99))

    def test_composite_number_miller(self):
        tester = MillerRabinTester()
        for number in self.composite_numbers:
            self.assertFalse(tester.is_prime(number,0.99))

    def test_composite_number_solovay(self):
        tester = SolovayStrassenTester()
        for number in self.composite_numbers:
            self.assertFalse(tester.is_prime(number,0.99))

