class RSAPrivateKey:
    def __init__(self, n, d):
        self.n = n  # модуль
        self.d = d  # закрытая экспонента
    def __str__(self):
        return f"Private Key with N = {self.n}, D = {self.d}"
class RSAPublicKey:
    def __init__(self, n, e):
        self.n = n  # модуль
        self.e = e  # открытая экспонента
    def __str__(self):
        return f"Public Key with N = {self.n}, E = {self.e}"
    
class ElGamalPublicKey:
    def __init__(self, p, g, y):
        self.p = p  # модуль
        self.g = g  # открытая экспонента
        self.y = y

    @staticmethod
    def from_json(json_dict: dict):
        if not all(key in json_dict for key in ('p', 'g', 'y')):
            raise ValueError("Неверный открытый ключ был загружен!")
        return ElGamalPublicKey(json_dict['p'], json_dict['g'], json_dict['y'])

class ElGamalPrivateKey:
    def __init__(self, p, g, x):
        self.p = p  # модуль
        self.g = g
        self.x = x  # закрытая экспонента
        
    @staticmethod
    def from_json(json_dict: dict):
        if not all(key in json_dict for key in ('p', 'g', 'x')):
            raise ValueError("Неверный приватный ключ был загружен!")
        return ElGamalPrivateKey(json_dict['p'], json_dict['g'], json_dict['x'])