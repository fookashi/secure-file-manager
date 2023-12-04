from math import sqrt
from utils.newtons_root import isqrt
from interfaces import IAttacker
from keys import RSAPublicKey, RSAPrivateKey
from typing import Iterator, Iterable
from utils.gcd import calculate_mod_inverse
import fractions
def is_perfect_square(n):
    '''
    If n is a perfect square it returns sqrt(n),

    otherwise returns -1
    '''
    h = n & 0xF  # last hexadecimal "digit"

    if h > 9:
        return -1  # return immediately in 6 cases out of 16.

    # Take advantage of Boolean short-circuit evaluation
    if (h != 2 and h != 3 and h != 5 and h != 6 and h != 7 and h != 8):
        # take square root if you must
        t = isqrt(n)
        if t * t == n:
            return t
        else:
            return -1

    return -1
class WienerAttacker(IAttacker):

    def cf_expansion(self, n, d):
        e = []

        q = n // d
        r = n % d
        e.append(q)

        while r != 0:
            n, d = d, r
            q = n // d
            r = n % d
            e.append(q)

        return e
            
    def convergents(self, e):
        n = [] # Nominators
        d = [] # Denominators

        for i in range(len(e)):
            if i == 0:
                ni = e[i]
                di = 1
            elif i == 1:
                ni = e[i]*e[i-1] + 1
                di = e[i]
            else: # i > 1
                ni = e[i]*n[i-1] + n[i-2]
                di = e[i]*d[i-1] + d[i-2]

            n.append(ni)
            d.append(di)
            yield (ni, di)

    def calculate_roots(self, a, b, c):
        # Вычисление дискриминанта
        discriminant = b**2 - 4*a*c

        if discriminant > 0:
            t = is_perfect_square(discriminant)
            if t != -1 and (b + t) % 2 == 0:
                root1 = (-b + isqrt(discriminant)) // (2*a)
                root2 = (-b - isqrt(discriminant)) // (2*a)
                return root1, root2
        return None

    def attack(self, public_key: RSAPublicKey):
        e, n = public_key.e, public_key.n
        cf_expansion = self.cf_expansion(e, n)
        convergents = self.convergents(cf_expansion)
        for pk, pd in convergents: # pk - possible k, pd - possible d
            if pk == 0:
                continue;

            possible_phi = (e*pd - 1) // pk

            a = 1
            b = n - possible_phi + 1
            c = n

            roots = self.calculate_roots(a, b, c)

            if roots is not None:
                pp, pq = roots # pp - possible p, pq - possible q
                if pp*pq == n:
                    return pp, pq
                phi_n = (pp - 1) * (pq - 1)
                d = calculate_mod_inverse(e, phi_n)
                print(pp, pq)
                return RSAPrivateKey(n=n, d=d)
        return None
