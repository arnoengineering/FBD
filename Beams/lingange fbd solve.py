import sympy as sy
# from sympy.physics.vector import *
from sympy import symbols
from sympy.physics.mechanics import *
import numpy as np
from numpy import sin, cos
# t = dynamicsymbols('t')
# q = dynamicsymbols('q')
# qd = dynamicsymbols('q', 1)
inert_f = ReferenceFrame('I')
origen = Point('O')  # ref frame has no start only dirs

def rot(r, ang):
    return np.array(cos(ang), sin(ang))*r


class force:
    def __init__(self, n=1):
        self.n = n
        self.pos = Point(f'F_{self.n}_p')
        # self.dir_ang = 45
        self.dir = inert_f.orientnew(f'F_{self.n}_d', 'Axis', self.pos, inert_f.x)
        self.val = self.mag*self.dir  # todo maybe add each,

    def rotate(self,ang):
        self.dir.rotate(self.pos, ang)

class moment:
    def __init__(self):
        self.pos = (0,0)  # pos for step function
        self.dir = 1  # or -1 for cw

class rigidbody(RigidBody):
    def __init__(self, n=1, r=None,cg_r=None,mass=None):
        self.n = n  # beam num
        self.r_val = r # todo rep
        self.cg_r_val = cg_r
        self.mass_val = mass # todo uniform by geometry or predefined mass center
        self.I_val = None
        self.st = f'Beam_{self.n}_'
        self._set_sym()
        super().__init__(self.st[:-1], self.cg, self.frame, self.mass, (self.I, self.cg))

    def _set_sym(self):
        self.st = f'Beam_{self.n}_'

        # variable
        self.theta = dynamicsymbols('theta'+str(self.n))
        self.omega = dynamicsymbols('omega'+str(self.n))
        self.alpha = dynamicsymbols('alpha'+str(self.n))

        # global
        self.pa = symbols(f'{self.st}p_ax {self.st}p_ay')
        self.pb = symbols(f'{self.st}p_bx {self.st}p_by')

        self.va = symbols(f'{self.st}v_ax {self.st}v_ay')
        self.vb = symbols(f'{self.st}v_bx {self.st}v_by')

        self.aa = symbols(f'{self.st}a_ax {self.st}a_ay')
        self.ab = symbols(f'{self.st}a_bx {self.st}a_by')

        self.a_b = [[self.pa, self.va, self.aa], [self.pb, self.vb, self.ab]]


        # const
        self.mass, self.r, self.cg_r= symbols(f'{self.st}m {self.st}r {self.st}cg_r')
        self.frame = inert_f.orientnew(self.st + 'frame', 'Axis', [self.theta, inert_f.z])

        self.a = Point(self.st + 'a')
        self.cg = self.a.locatenew(self.st +'cg', self.cg_r*self.frame.x)  # todo at angle
        self.b = self.a.locatenew(self.st + 'b',
                                  self.r * self.frame.x)  # todo calc, replace f_1,f_2 for f_1,2 and -f_1,2

        self.I = outer(self.frame.x,self.frame.x)

        self.diff_eq = [self.omega - self.theta.diff(),
                        self.alpha - self.omega.diff(),
                        ]

        self.diff_lin = []
        for n in range(2):
            for ni in range(1,3):
                for nii in range(2):
                    self.diff_lin.append(self.a_b[n][ni][nii]-self.a_b[n][ni - 1][nii].diff())

        self.eq_ab = [self.vb - self.b.v2pt_theory(self.a, inert_f, self.frame),
                      self.ab - self.b.a2pt_theory(self.a, inert_f, self.frame)]

        # self.a.set_vel(inert_f, self.va * inert_f.x)  # todo vx, vy,
        #         self.a.set_acc(inert_f, self.aa * inert_f.x)

class rod(rigidbody):
    def __init__(self, n, r):
        super().__init__(n,r,r/2)
        self.I_s = '1/3m*length**2'


class disk(rigidbody):
    def __init__(self):
        super().__init__()

class joint:
    def __init__(self,free):
        self.freedom = free
        self.forces = [1,1]# norm tan
        self.pos = (0,0)
        self.ic = self.pos

class roler(joint):
    def __init__(self):
        super().__init__(1)
        self.forces = [1, 1]  # norm tan
        self.pos = (0, 0)
        self.ic = self.pos
class pin(joint):
    def __init__(self):
        super().__init__(1)
        self.forces = [1, 1]  # norm tan
        self.pos = (0, 0)
        self.ic = self.pos

class slider(joint):
    def __init__(self):
        super().__init__(1)
        self.forces = [1, 0]  # norm tan
        self.pos = (0, 0)
        self.ic = self.pos + [1000,0]  # add inf at norm dir, ie along norm line

class roleSlide(joint):
    def __init__(self):
        super().__init__(2)
        self.forces = [1, 0]  # norm tan
        self.pos = (0, 0)
        self.ic = self.pos + [1000, 0]  # add inf at norm dir, ie along norm line


j_1 = 3  # 1deg_freed
j_2 = 2  # 2 deg dreedom
redundant = 0
m = 4  # links
freedom = 3* (m-1) - 2*j_1-j_2+redundant
eq = []
def create_beam(self):
    beam = rod()
    m+= 1 # todo count at end?

def sum_forces(self):
    sum_f = 0  # todo f unknown pos, force,angle, sympy add f_{beam_num}_{x or y}, then repace with known vals
    # todo add step function for shear bend
    mom_sum = 0
    ref_pos = (0,0)
    for f in self.forces:
        sum_f += f.val
        mom_sum += cross(f.pos-ref_pos, f.val)
    for m in self.mom:
        mom_sum += m.val

def gen_eqalf(self):
    for b,b1 in combinations(self.beams):
        if b.pin == b1.pin:  # if share connection, and no muvement
            for i in 'xy':
            eq.append(f'f_{b.n}_{i}-f_{b1.n}_{i}') # fx = fx2
            eq.append(f'v_{b.n.a}_{i}-v_{b1.n.a}_{i}') # fx = fx2)

#  todo kenedys therom


 # todo solve boundary for deflection step function