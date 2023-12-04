import unittest
from utils.symbol_calculator import SymbolCalculator

class TestSymbolCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = SymbolCalculator()

    def test_legendre_1(self):
        self.assertEqual(self.calculator.legendre(2, 7), 1)

    def test_legendre_2(self):
        self.assertEqual(self.calculator.legendre(3, 7), -1)

    def test_legendre_3(self):
        self.assertEqual(self.calculator.legendre(6, 7), -1)

    def test_legendre_4(self):
        self.assertEqual(self.calculator.legendre(4, 7), 1)

    def test_legendre_5(self):
        self.assertEqual(self.calculator.legendre(5, 7), -1)

    def test_jacobi_1(self):
        self.assertEqual(self.calculator.jacobi(2, 15), 1)

    def test_jacobi_2(self):
        self.assertEqual(self.calculator.jacobi(3, 15), 0)

    def test_jacobi_3(self):
        self.assertEqual(self.calculator.jacobi(4, 15), 1)

    def test_jacobi_4(self):
        self.assertEqual(self.calculator.jacobi(6, 15), 0)

    def test_jacobi_5(self):
        self.assertEqual(self.calculator.jacobi(7, 15), -1)

    def test_jacobi_6(self):
        self.assertEqual(self.calculator.jacobi(8, 15), 1)

    def test_jacobi_7(self):
        self.assertEqual(self.calculator.jacobi(9, 15), 0)

    def test_jacobi_8(self):
        self.assertEqual(self.calculator.jacobi(10, 15), 0)

    def test_jacobi_9(self):
        self.assertEqual(self.calculator.jacobi(11, 15), -1)


