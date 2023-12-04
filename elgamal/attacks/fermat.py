from utils.gcd import calculate_mod_inverse
from utils.newtons_root import isqrt
from interfaces import IAttacker
from keys import RSAPublicKey, RSAPrivateKey

class FermatAttacker(IAttacker):

    # TODO: https://eprint.iacr.org/2023/026.pdf
    
    def attack(self, public_key: RSAPublicKey):
        e, n = public_key.e, public_key.n

        a = isqrt(n)
        temp = a**2 - n
        b = isqrt(temp)
        
        while b**2 != temp:
            a = a + 1
            temp = a**2 - n
            b = isqrt(temp)
            
        bsq = a**2 - n
        b = isqrt(bsq)
        p = a + b
        q = a - b
        
        phi_n = (p - 1) * (q - 1)
        d = calculate_mod_inverse(e, phi_n)
        return RSAPrivateKey(n = n, d = d)