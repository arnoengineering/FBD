
import sympy as sy
from sympy import init_printing
from sympy import integrate
from sympy import SingularityFunction as sf

from numpy import sin, cos, tan, pi, zeros


import os
from PyQt5.QtCore import Qt

import numpy as np
from numpy.linalg import norm

g = 9.81
kr_val = {}
e_r = [205, 7.85]
init_printing()
E = 504e9
x = sy.Symbol('x', positive=True)
c = np.array([sy.Symbol('c1y c2y'), sy.Symbol('c1z c2z')])


def unit(vect):
    return vect/norm(vect)


class Vector:
    def __init__(self, *com):  # todo if mag
        self.vect = np.array(com)

    @property
    def x(self):
        return self.vect[0]

    @x.setter
    def x(self, val):
        self.vect[0] = val

    @property
    def y(self):
        return self.vect[1]

    @y.setter
    def y(self, val):
        self.vect[1] = val

    @property
    def z(self):
        return self.vect[2]

    @z.setter
    def z(self, val):
        self.vect[2] = val


class Force:
    def __init__(self, n, pos=None):
        self.n = n
        self.pix_per_m = 5
        self.default_size = 2
        self.M = sy.symbols(f'F_{n}x F_{n}y F_{n}z')
        self.loc = sy.symbols(f'l_{n}x l_{n}y l_{n}z')
        self.loc_x = pos if pos else np.zeros(3)
        self.order = -1
        self.x_ind = ['x','y','z']
        self.M2 = []
        self.lr = 5
        self.eq = []

    def single(self, plane):
        # 3 =
        return self.M[plane[1]]*sf(x[plane[0]],self.loc[plane[0]], self.order)

    def _mag(self):
        if len(self.M2) >0:
            return self.M2
        else:
            return self.M

    def __abs__(self):
        # if m is solvable andhas values
        m = self._mag()
        return norm(m)

    def __mul__(self, other):
        if isinstance(other, np.Array):  # todo return on dot
            return np.cross(self._mag(),other)

    def __getitem__(self, item):  # self.x?
        m2 = self._mag()
        if isinstance(item, str):
            return m2[self.x_ind.index(item.lower())]

        return m2[item]

    def __setitem__(self, key, value):
        m2 = self._mag()
        if isinstance(key, str):
            key = self.x_ind.index(key.lower())
        m2[key] = value  # todo hold?




    def _force(self,ri):  # todo gess force

        if isinstance(ri, sy.Symbol):
            li = (0, self.default_size, 0)
        else:
            li = ri
        poi = np.array(((0.5, 0.866, 0), (-0.5, 0.866, 0))) * self.lr*li/norm(li)
        return self.loc_x-poi, self.loc_x-li*self.pix_per_m

    def paint(self, painter):
        painter.setPen(Qt.black)
        l2 = self._force(self.M)
        for i in l2:
            painter.drawLine(*self.loc_x[:2], *i[:2])

    def rot(self, func):
        theta = np.arctan2(self.M[1],self.M[0])
        r_mat = np.array([[cos(theta), -sin(theta), 0],
                          [sin(theta), cos(theta), 0],
                          [0, 0, 1]])
        func -= self.loc_x
        return r_mat @ func + self.loc_x


class Moment(Force):
    def __init__(self, n):
        super().__init__(n)
        self.order = -2
        self.ty = 2

    def single(self, plane):
        # 3 =
        n_p = 3
        return self.M[n_p] * sf(x[plane[0]], self.loc[plane[0]], self.order)

    def _mom(self,painter):

        loc_x, l2x = self._force(self.M)
        points_2 = np.vstack((loc_x, self.loc_x))+np.array((0, 1, 0))
        for i in points_2[:2]:
            print(i[:2],points_2[2][:2])
            for i in self.l2:
                painter.drawLine(*self.lin_dir, *i)
            for i in l2:
                painter.drawLine(*self.loc_x[:2], *i[:2])

    def _m_t2(self, painter):
        if isinstance(self.M, sy.Symbol):  # todo replace with solved M, add var on hgover
            li = (0, self.default_size, 0)
        else:
            li = ri
        poi = np.array(((0,1,0), (0.5, 1.866, 0), (-0.5, 1.866, 0))) * self.lr * li / norm(li)
        painter.drawArc(self.loc_x, self.loc_x + (self.r * self.lr, 0), self.lin_dir)
        return self.loc_x - poi, self.loc_x - li * self.pix_per_m

    def paint(self, painter):
        painter.setPen(Qt.black)
        if self.ty == 2:
            self._m_t2(painter)
        else:
            self._mom(painter)


class DisLoadRamp(Force):
    def __init__(self, n):
        super().__init__(n)
        self.order = 1
        self.loc_e = sy.symbols(f'l_{n}x_2 l_{n}y_2 l_{n}z_2')

    def single(self, plane):
        a, b = self.loc[plane[0]], self.loc_e[plane[0]]
        ave_f = self.M[plane[1]] / (a - b)
        return ave_f * sf(x, a, 1) - ave_f * sf(x, b, 1) - self.M[plane[1]]  * sf(x, b, 0)


class DisLoadConst(Force):
    def __init__(self, n):
        super().__init__(n)
        self.space = 10
        self.cnt = 5
        self.eq = x  # todo bx, diff var
        self.eq_ac = 50
        self.loc_e = sy.symbols(f'l_{n}x_2 l_{n}y_2 l_{n}z_2')

        self.order = 0

    def single(self,plane):
        self.M[plane[1]] * sf(x, self.loc[plane[0]], 0) - self.M[plane[1]] * sf(x, self.loc_e[plane[0]], 0)

    def _draw(self,painter):

        if (self.loc_e[0]-self.loc[0])/self.cnt<self.space:
            ps = np.arange(self.loc[0], self.loc_e[0], self.space)
        else:
            ps = np.linspace(self.loc[0], self.loc_e[0], self.cnt)

        for i in ps:  # todo dim i
            r = self.pix_per_m*self.eq.subs(i-self.loc[0])
            lr = np.sign(r)
            xr = ((0.5,0.866*lr), (-0.5,0.866*lr))
            painter.drawLine(*i, *(i+r))
            for rr in xr:
                painter.drawLine(*i,*(i+rr))

        eqa = np.linspace(self.loc[0], self.loc_e[0], self.eq_ac)

        # todo change effecincy
        for ii in range(eqa.size-1):
            painter.drawLine(eqa[ii], self.eq.subs(eqa[ii]), eqa[ii + 1], self.eq.subs(eqa[ii + 1]))


    # def dim x
    # check for fixed x,y, both if all er else chech if h or v:
    #   dialog for dim then movew non fixed so dim = true


class DisLoadEq(DisLoadConst):
    def __init__(self, n):
        super().__init__(n)
        self.eq = x*5+6*x**2
        self.eq_n = sy.Poly(self.eq)
        self.order = len(self.eq_n)
    """for each creat"""
    def single(self,plane):  # todo inverse

        eq_f = 0
        for n, i in enumerate(self.eq_n):  # ie order and
            eq_f += i*(sf(x, self.loc[plane[0]], n)-sf(x, self.loc[plane[1]], n))
        fin = self.eq.subs(x,self.loc[plane[1]]-self.loc[plane[0]])
        eq_f -= fin*sf(x, self.loc[plane[1]], 0)