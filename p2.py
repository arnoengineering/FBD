import numpy as np


class Force:
    def __init__(self, x = 0, y=0,z=0, name='v1'):
        self.vect = np.array([x,y,z])
        self.x = 1
        self.name = name

    def __add__(self, other):
        print(f'add self: {self.__str__()}, other: {other}')
        if isinstance(other, Force):  # todo if super or other or subclass  # araay add...
             return self.x + other.x
        return self.x+other

    def __radd__(self, other):
        print(f'radd other: {other}, self: {self.__str__()}')
        return self.__add__(other)

    def __repr__(self):
        return f'Force {self.vect}'

    def __str__(self):
        return self.name +' '+ str(self.x)


if __name__ == '__main__':
    v1 = Force(1,1,2)
    v2 = Force(2,1,1)
    one = np.ones(3)
    # v11 = v1+one
    #
    # print(f'\nv1+numpy: {v1}+{one}={v11}\n-----------------\n')
    # v13 = one + v1
    # print(f'\nnumpy+v1{one}+{v1}={one+v13}\n-----------------\n')
    v12 = v1 + v2
    print(f'\nv1+v2: {v1}+{v2}={v12}')

