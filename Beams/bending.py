
import sympy as sy
from sympy import init_printing
from sympy import integrate
from sympy import SingularityFunction as sf
from sympy.physics.vector import *
import matplotlib.pyplot as plt
# from sympy.printing import *
# from IPython.display import display, Latex
from numpy import sin, cos, tan, norm, pi, zeros
from sympy.printing import latex
from beam_tables import *

import os
from PyQt5.QtCore import Qt, QTimer, QSize  # , QPointF, QPoint
from PyQt5.QtGui import QPainter, QPen, QImage  # QPixmap,

import numpy as np
from numpy.linalg import norm

from PyQt5.QtWidgets import *
from functools import partial

import sys

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica"]})
"""add solution and relation equations, add relivant tables from
add logical vars and prints
plot track, plot sigularty, solve for stresses, add database"""
# car,
g = 9.81
kr_val = {}
e_r = [205, 7.85]
init_printing()
E = 504e9
x = sy.Symbol('x', positive=True)
c = np.array([sy.Symbol('c1y c2y'), sy.Symbol('c1z c2z')])


def tot(jj):
    return sy.sqrt(jj[0] ** 2 + jj[1] ** 2)


# def print_l(st):
#     ai = latex(st)
#     ax = plt.subplot(111)  # left,bottom,width,height
#     ax.set_xticks([])
#     # plt.ylabel()
#     ax.axis('off')
#     te = f'${ai}$'
#     plt.text(0.4, 0.4, te, size=50, color="g")
#     plt.show()


def it(f):
    return integrate(f, x)


def gen_st(va, cnt):
    st = ""
    for ii in range(cnt):
        st += va + str(ii) + " "
    return sy.symbols(st)


def sol_v(ar, tf):
    return [float(ar.subs(x, tt)) for tt in tf]
    # display(Latex())


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


class beam:
    # todo bolt connect, bolt stress, bolt bear, bolt shear
    def __init__(self):
        self.secs = []
        self.forces = []
        self.moments = []

        self.ke = 0.897
        self.kc = 1
        self.kaf = 2
        self.kf, self.kfs = sy.symbols('kf kfs')  # todo solve
        self.nf = 2

        self.cycles = sy.symbols('cyc')
        self.temp = sy.symbols('T')
        self.length = 2

    def _solve_prop(self):
        self.tau_max = sy.symbols(f'tau_m')
        self.sig_vm = sy.symbols('sigma_vm')
        self.se = sy.symbols('se')
        self.sig_a = sy.symbols('sigma_a')
        self.sig_m = sy.symbols('sigma_m')
        self.safty = {}

        # self.titlel = ['Q', 'v', 'M', 'th', 'del']

    def _material_prop(self):  # todo per material
        self.alpha = sy.symbols('alpha')

        self.E = 100
        self.G = 100  # todo var; poisopn ratio

        self.yield_stress = 120
        self.ultimate = 1400

        self.v = sy.symbols('nu')
        self.strain = sy.symbols('epsilon')
        self.percent_EL = sy.symbols('EL')
        self.percent_RA = sy.symbols('RA')

    def _geometry_prop(self):
        self.cen = zeros(2)
        self.I = sy.symbols(f'I_x I_y J_')
        self.b = 0

    def off_02(self, eq):
        strain = np.linspace(0, 1)
        sig1 = self.E * (strain - 0.002)
        return sig1-eq

    def _solve_c(self, d):
        self.cen[d] = np.sum(i.pos[d]*i.a for i in self.secs)/np.sum(i.a for i in self.secs)
        for xi in self.secs:
            xi.pos_cen[d] = xi.pos[d] - self.cen[d]

    def solve_c_q(self, d, r):
        return np.sum(s.area(d, s.pos_cen[d] - r) for s in self.secs)

    def i_sol(self, d):
        np.sum(i.I[d] + i.a * i.pos_cen[d]**2 for i in self.secs)

    def mom(self, d, r, m):
        return m * r/self.I[d]

    def tau(self, d, r, f):
        return f * self.solve_c_q(d, r) / self.I / self.b

    def i_vs_l(self):
        pass

    def stress(self):  # todo do in plane
        # sig = []
        # sig.append(bend(!=d), f(d))
        # tau = []
        # tau.append(f(!=d), T(!=d))
        pass

    def priciple_stress(self, sig, tau):
        sig_mean_par = np.mean(sig)
        d_sig = np.diff(sig)
        sig_min_max = 0.5*(d_sig + np.array((-1, 1))*norm((sig_mean_par, 2*tau)))

        sig_del = np.diff(sig_min_max)
        return [self.sig_a - sig_del/2, self.sig_m - np.mean(sig_min_max)]

    def mhors_circ(self, stress, painter):
        col_ls = [Qt.green, Qt.blue, Qt.red]
        prince = len(stress)
        stress.sort()
        for i in range(prince):
            d = np.array((stress[i],stress[(i+1)%prince]))
            r = 0.5*np.diff(d)
            ce = np.mean(d)
            painter.setPen(col_ls[i])
            painter.drawElipse(*ce, *r)

    def von_misies_full(self, sig, tau):
        le = len(sig)
        sig_sum = 0
        for i in range(le):
            sig_sum += (sig[i] - sig[(i + 1) % le]) ** 2 + 6 * tau[i] ** 2
        return self.sig_vm - np.sqrt(sig_sum/2)

    def fatuige_life(self):
        pass

    def stress_th(self, th, sig, tau):
        # todo stess from bending tension, shear, torsion at local x,y on sec and z on beam
        a_sig = np.mean(sig)
        d_sig = np.diff(sig)
        sig_x = 0.5 * a_sig + 0.5 * d_sig * cos(2 * th) + tau * sin(2 * th)  # todo ave dir
        # tau = nn
        # sig_y = nn
        return sig_x

    def therm(self, delta_t):
        return self.length * self.alpha * delta_t

    def calc_min_d(self, d, m, t):
        eps = 1e-4
        d_min = 30  # todo why 30
        cnt = 0
        kff = [self.kfs, self.kf]
        nnn = [np.mean, np.diff]
        sig_tau = [t, m]
        se = self.se_0*1
        mmm = [se, self.yield_stress]

        while abs(d_min - d) > eps:
            d = d_min
            kb_s = Kb[d > kb_r]  # todo argwhere
            kb = kb_s[0] * d ** -kb_s[1]
            dm = 0
            se = self.ka * kb * self.kc * self.kd * self.ke * self.kf * self.se_0
            for am in range(2):
                xi = 0
                for tm in range(2):
                    xi += (tm+3)*(kff[tm]*nnn[am](sig_tau[tm]))**2
                dm += xi/mmm[am]**2
            d_min = 16 * self.nf / pi * np.sqrt(dm)  # todo kf for mom, kfs for shear, se for ave sy for max
            cnt += 1
        self.d = d
        return se

    def endurence_strength(self):
        self.se_0 = 0.504*self.ultimate if self.ultimate <= 212 else 107  # todo units

    def _calc_f(self):
        plane = [0, 1]
        self.eqf = np.zeros(3)
        for f in self.forces:
            self.eqf += f.M

        self.feq = np.sum(f.single(plane) for f in self.forces)  # for x,y, z
        self.meq = np.sum(m.eq for m in self.moments) + sy.integrate(self.feq)
        self.bending = sy.integrate(self.meq) / (
                    self.E * self.I)  # todo bend, deflact conditions, ie cantelever no anfle, no deflect,
        # pin no deflact
        self.d_bound = [[0, 0], [1, 0]]
        self.bending_bound = [[0, 0], [1, 0.5]]
        self.deflection = sy.integrate(self.bending)
        sy.solve_bvp(self.deflection, self.bending, self.d_bound, self.bending_bound)

    def factors_safty(self):
        sig_g = np.array((self.sf / self.sig_a, self.yield_stress/ self.sig_m))
        nff = norm(sig_g)
        nyf = sum(sig_g)
        nfi = norm((self.se / self.sig_a, self.yield_stress / self.sig_m))
        nyi = self.yield_stress / self.sig_a + self.yield_stress / self.sig_m
        self.safty['nfi'] = min(nff, nfi,nyi, nyf)

        self.safty['n_MSSFT'] = self.yield_stress / (2*self.tau_max) # >=1
        self.safty['n_DE'] = self.yield_stress / self.sig_vm

    def notch_concen(self, ty):  # todo from data
        if ty == 'grove':
            pass

    def _stress_factors(self):  # todo const vs var

        self.kd = kdt(self.temp)
        # todo stress consent
        self.d_m = norm(self.d)
        self.th = norm
        self.ka = ab[self.kaf, 0] * self.ultimate ** ab[self.kaf, 1]

        f = val_t(aa, self.ultimate)
        al = (f * self.ultimate) ** 2 / self.se
        b = -np.log10(f * self.ultimate / self.se) / 3
        self.sf = al * self.cycles ** b


class dim:
    pass


class circ:
    # pi/4*r^4
    # pol: pi/2 r^4

    pass


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


class Force:
    def __init__(self, n, pos=None):
        self.n = n
        self.pix_per_m = 5
        self.default_size = 2
        self.M = sy.symbols(f'F_{n}x F_{n}y F_{n}z')
        self.loc = sy.symbols(f'l_{n}x l_{n}y l_{n}z')
        self.loc_x = pos if pos else np.zeros(3)
        self.order = -1
        self.lr = 5
        self.eq = []

    def single(self, plane):
        # 3 =
        return self.M[plane[1]]*sf(x[plane[0]],self.loc[plane[0]], self.order)

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


class dispsuport(QWidget):
    def __init__(self):
        super().__init__()
        self.pix_per_m = 20
        self.cnt=5

    def _fixed(self):  # asum horizontal  # todo rot mat, type realy qw, when col, witch rect print, add offset
        self.dx = np.array([(0,0), (1,0)])*self.pix_per_m
        self.fix_l = np.array([(0,0), (-0.2,-0.2)])*self.pix_per_m
        off_set = np.linspace(*self.dx[:,0],self.cnt)
        self.fix_lines = []
        for of in off_set:  # todo mult rot mat
            self.fix_lines.append(self.fix_l+np.array((of,0),(of,0)))

        # pin arc, circ, rect to gnd
        # ,roller = pin+3xcirc

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.eraseRect(self.rect())
        painter.setPen(Qt.black)
        painter.drawLine(*self.dx[0], *self.dx[1])
        for i in self.fix_lines:
            painter.drawLine(*i[0], *i[1])


class dispMF(QWidget):
    def __init__(self):
        super().__init__()
        self.pix_per_N = 5
        self.pos = np.zeros(2)
        self.r = 5
        self.m = -1  # dir, isomet




class beamWidget(QWidget):
    def __init__(self, par, th):
        super().__init__()
        self.pix_per_m = 20
        self.par = par
        self.th = th

    def paintEvent(self, event):
        h = 0.5
        rad = 2
        painter = QPainter(self)
        painter.eraseRect(self.rect())
        painter.setPen(Qt.black)
        painter.drawRect(0,0, self.par.beam.length, h)  # todo h, scale
        # hilite detail oh hove


        # self.eq_l =


class Window(QMainWindow):
    # noinspection PyArgumentList
    def __init__(self):
        super().__init__()
        self.setWindowTitle('QMainWindow')
        self.cen = beamWidget()
        self.setCentralWidget(self.cen)
        self._create_tools()
        self._create_beam()
        self.cen.ani()

    def _create_beam(self):
        self.beam = beam()
        m = [100, 0]
        mi = Moment(1)
        mi.Mv = (0, 0, m[0])
        mi.lv = (m[1], 0, 0)

        self.beam.moments = [mi]
        f = [(-50, 0), (50, 2)]
        for nix, fir in enumerate(f):
            firs = Force(nix)
            firs.Mv = (0, fir[0], 0)
            firs.lv = (fir[1], 0, 0)
            self.beam.forces.append(f)

    # noinspection PyArgumentList
    def _create_tools(self):
        self.tool_dock = QDockWidget('ToolBar')
        self.tools = QWidget(self)
        self.tool_dock.setWidget(self.tools)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tool_dock)
        self.tl = QVBoxLayout()
        self.tool_layout = QGridLayout()

        self.in_p = {}
        n = 0
        m = 0

        for i, k in self.cen.vals.items():
            la = QLabel(i)
            j = QLineEdit()
            if isinstance(k, list):
                j.setReadOnly(True)
                kk = ','.join(str(iii) for iii in k)
            else:
                kk = str(k)
            j.setText(kk)
            j.editingFinished.connect(partial(self.new_vals, i))
            # sl.valueChanged.connect(partial(self.up_vect, i))

            # if i == liist
            self.in_p[i] = j

            self.tool_layout.addWidget(j, m + 1, n)
            self.tool_layout.addWidget(la, m, n)
            n += 1
            if n > 3:
                n = 0
                m += 2

        # d_0= n == 0
        if n != 0:
            n = 0
            m += 2
        for i, k in self.cen.binary.items():

            if isinstance(k, bool):
                j = QCheckBox(i)
                j.setChecked(k)
                j.clicked.connect(partial(self.set_bin, i, 0))
            elif isinstance(k, list):
                j = QComboBox()
                j.addItems(k)
                j.setCurrentText(self.cen.f_vals['Type'])
                j.currentTextChanged.connect(partial(self.set_bin, i, 1))
            else:
                j = QPushButton(i)
                j.clicked.connect(partial(self.set_bin, i, 2))
            self.tool_layout.addWidget(j, m, n)

            self.in_p[i] = j
            n += 1
            if n > 3:
                n = 0
                m += 1

        if n == 0:
            m -= 1

        # mk = max(m - 2, 1)

        self.tl.addLayout(self.tool_layout)

        self.tl.addWidget(self.w)
        self.tools.setLayout(self.tl)

    def set_bin(self, i, x):
        if x == 0:
            self.cen.binary[i] = self.in_p[i].isChecked()
            if i == '3d':
                self.cen.d3()
        elif x == 1:
            # todo change _list
            self.cen.f_vals['Type'] = self.in_p[i].currentText()
        else:
            self.cen.clear_falc_ob()

    #
    #     self.op = {'Scatter': False, 'Kill falc': 'but', 'swap time'}

    # def swap_b(self, b):
    #     if falc.select:
    #         grey = ['Birds', 'Dimension', 'Cohesive Dist', 'Crowd Dist', 'Relative Weights']
    #     else:
    #         ungrey all
    #     pass
    #     or hame all

    def new_vals(self, v):
        val = self.in_p[v].text()
        self.cen.reset_v(v, val)

    def rel_v_set(self, v):
        self.in_p['Relative Weights'].setText(','.join(str(iii) for iii in v))
        self.cen.reset_v('Relative Weights', v)

    def mouseMoveEvent(self, event):
        pos = (event.x(), event.y())
        # todo in both
        for ob in self.beam.forces:
            # todo pos alowable along lines
            if all(ob.p1<= pos <= ob.p2):
                ob.col = 'orange'

    def mousePressEvent(self, event):
        for ob in self.beam.forces:
            if ob.col == 'orange':
                ob.selected()  # todo select object bring up dialog







if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())