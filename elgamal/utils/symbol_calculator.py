class SymbolCalculator:
    def legendre(self, a, p):
        if p <= 0 or (p % 2 == 0 and p != 2):
            raise ValueError("p должно быть простым числом или 2")

        a = a % p
        if a < 0:
            a += p  # a to [0, p)
        if a == 0:
            return 0
        if a == 1:
            return 1
        if a % 2 == 0:
            return self.legendre(a // 2, p) * (-1) ** ((p ** 2 - 1) // 8)
        else:
            return self.legendre(p % a, a) * (-1) ** ((a - 1) * (p - 1) // 4)

    def jacobi(self, a, n ):
        if a == 0:
            if n == 1:
                return 1
            else:
                return 0

        elif a == -1:
            if n % 2 == 0:
                return 1
            else:
                return -1

        elif a == 1:
            return 1

        elif a == 2:
            if n % 8 == 1 or n % 8 == 7:
                return 1
            elif n % 8 == 3 or n % 8 == 5:
                return -1

        elif a >= n:
            return self.jacobi( a%n, n)
        elif a%2 == 0:
            return self.jacobi(2, n)*self.jacobi(a//2, n)

        else:
            if a % 4 == 3 and n%4 == 3:
                return -1 * self.jacobi( n, a)
            else:
                return self.jacobi(n, a )