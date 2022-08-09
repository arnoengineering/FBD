
import sympy as sy

import numpy as np
from numpy.linalg import norm


class dim:
    pass


class circ:
    # pi/4*r^4
    # pol: pi/2 r^4

    pass


class section:
    def __init__(self, n):
        self.neg=False
        # self.cent =
        self.partial_pos = sy.symbols(f'{n}x {n}y')
        self.c = sy.symbols(f'c_{n}x c_{n}y')
        self.pos = sy.symbols(f'C_{n}x C_{n}y')
        self.I = sy.symbols(f'I_{n}x I_{n}y J_{n}')
        self.a = sy.symbols(f'A_{n}')
        self.pos_cen = sy.symbols(f'Cp_{n}x Cp_{n}y')
        self.k = sy.symbols("k_"+n)
        keq = self.k - sy.sqrt(self.k/self.a)

    def area(self, *bounds):
        # todo find centroid of a, partial inertia

        a = sy.integrate(1, *bounds)
        # c = self.centroid_p(a)
        return self.a-a

    def inertia(self, d, *bounds):
        if d == 2:
            r = self.partial_pos[0]**2 + self.partial_pos[1]**2
        else:
            r = self.partial_pos[d]**2
        eq = sy.integrate(r, *bounds)
        return self.I[d]-eq

    def centroid(self, d, a, *bounds):
        c = sy.integrate(self.partial_pos[d] ** 2, *bounds)

        return self.c[d] - c/a


class rect(section):
    def __init__(self, n):
        super().__init__(n)
        self.bd = (1, 2)

    def area(self,*bounds):
        return self.a - bounds[0]*bounds[1]

    def inertia(self, d, *bounds):  # add local i
        return self.I[d] - bounds[d] ** 3*bounds[(d+1)%2] / 12

    def centroid(self, d, *bounds):
        pass

    def partial(self,d, r):
        # r is dis from center of beam pos_cen is dis from cent to bem cent
        b1 = r - self.pos_cen[d]  # todo greater
        bound = np.array((-1,1),(-1,1))
        bound[0] *= self.bd[0]/2
        bound[1] *= self.bd[1]/2

        if b1<-self.bd[d]/2:
            p_i = self.I[d]
            p_c = self.pos_cen[d]
            p_a = self.a
        elif b1 <= self.bd[d]/2:
            bound[d, b1 <= 0] = b1
            p_c = np.mean(bound[d]) + self.pos_cen[d]
            bd = bound[:,0] - bound[:,1]
            p_i = self.inertia(d,*bd.T)
            p_a = self.area(*bd.T)
        else:
            p_i = 0
            p_c = 0
            p_a = 0
        return p_c, p_i, p_a


class arc(section):
    # Ix = (th-sin(th))*r^4/8
    pass