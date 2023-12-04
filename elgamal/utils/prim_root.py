import random


# TODO: http://modular.math.washington.edu/edu/2007/spring/ent/ent-html/node31.html
def find_primitive_root( p ):
    if p == 2:
            return 1

    p1 = 2
    p2 = (p-1) // p1

    while True:
        g = random.randint( 2, p-1 )

        if not (pow( g, (p-1)//p1, p ) == 1):
            if not pow( g, (p-1)//p2, p ) == 1:
                return g