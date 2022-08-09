
import sympy as sy
from numpy import sin, cos, tan, pi, zeros
from numpy.linalg import norm
from sympy.printing import latex
from beam_tables import *

from PyQt5.QtCore import Qt

import numpy as np
from numpy.linalg import norm

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

    # def signularity(self):
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
