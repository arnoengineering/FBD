# import sympy as sy
from PyQt5.QtGui import QPainter, QPen
from numpy import cos, sin, arctan, sqrt, pi, linspace, arange
# import os
from PyQt5.QtCore import Qt, QTimer, QSize  # , QPointF, QPoint

import pyqtgraph as pg
import numpy as np

# from numpy.linalg import norm

from PyQt5.QtWidgets import *
from functools import partial

import sys

"""draw mode
animation 
self update, 
self add 
plots
draw rect"""


class HandlePlots(pg.PlotWidget):
    def __init__(self, parent=None, pf=None):
        super().__init__(parent)
        self.paren = pf

        self.time = True  # vs theta, # todo x, y, dist, alfpa, x v y

        # when not image
        self.plot_ls = []
        for i in 'crg':
            self.plot_ls.append(self.plot(pen=i, width=3, title=i))

    def update(self, data):
        print('set plot')
        print('data:' , data)
        for n, i in enumerate(data):
            print('pls,', n)
            self.plot_ls[n].setData(i[1],i[0]*10**n)

    def reset(self):
        # todo reset names, axis
        pass


# def err(func):
#     def inner_function(*args, **kwargs):
#         try:
#             fun = func(*args, **kwargs)
#         except:
#             print(f"{func.__name__} wrong data types. enter numeric")
#         return fun
#     return inner_function


def diff(x, y):
    dy = np.diff(y) / np.diff(x)
    return np.insert(dy, 0,0)


class cam:
    def __init__(self, par, **main_v):
        self.par = par
        self.main_v = main_v
        self.omega = main_v['Omega']
        self.r_b = main_v['r_b']
        # self.ty = main_v['Type Motion']

        self.xy = main_v['x']  # SWAP NAMES ON ver
        # self.r_r = main_v['r_r'] if main_v['r_r'] else None

        self.out = {'Trans': 'y', 'rot': 'alpha'}

        self.motions = []
        self.partial_motion = {}
        self.s0 = self.r_b
        self.th_0 = 0
        self.ds = 0
        self.s, self.theta = [], []
        self.repl = {}
        self.point_dencity = 500
        self.space = 2 * pi / self.point_dencity

        self.follow_vals = {}

    def define_mot(self, ty, beta):  # todo recalc all if one?
        if ty == 'Const V':
            print('cv')
            theta = arange(0, beta, self.space)
            eq = theta / beta
        else:
            print('dv')
            gamma = 2  # todo rep gamma
            theta1 = arange(0, beta / gamma * (gamma - 1), self.space)
            theta2 = arange(beta / gamma * (gamma - 1), beta / gamma, self.space)
            theta3 = arange(beta / gamma, beta, self.space)
            theta = np.concatenate((theta1, theta2, theta3))
            thb1 = theta1 / beta
            thb2 = theta2 / beta
            thb3 = theta3 / beta
            thb = theta / beta

            if ty == 'Harmonic':
                eq = 0.5 - cos(pi * thb) / 2
            elif ty == 'Cycloidal':
                eq = thb - 1 / (2 * pi) * sin(2 * pi * thb)
            else:
                eq1 = gamma ** 2 / (2 * (gamma - 1)) * thb1 ** 2
                eq2 = gamma * thb2 + (1 - gamma) / 2
                eq3 = 1 - gamma ** 2 / (2 * (gamma - 1)) * (0.5 - thb3 + 0.5 * thb3 ** 2)
                eq = np.concatenate((eq1, eq2, eq3))
        return eq, theta

    def load_eq(self, ind, replace, fol_vals, rep=False):
        fol_vals[0] = np.deg2rad(fol_vals[0])
        s, theta = self.define_mot(fol_vals[2], fol_vals[0])
        partial_motion = {}
        for n, i in enumerate(['Beta', 'H', 'Type']):
            partial_motion[i] = fol_vals[n]

        partial_motion['s'] = s * fol_vals[1]
        partial_motion['theta'] = theta
        if rep:
            self.repl = partial_motion
        else:
            if ind:
                if replace:
                    self.motions[ind] = partial_motion
                else:
                    self.motions.insert(ind, partial_motion)
            else:
                self.motions.append(partial_motion)

        self.res()

    def res(self):
        print('res')
        if self.main_v['Type Motion'] == 'Trans':
            self._set_trans()

        else:
            self._set_rot()

    def xi(self):
        print('motions')
        print(self.motions)
        s = [0]
        theta = [0]

        for i in self.motions:
            s0, th0 = s[-1], theta[-1]
            # print('theta n ', theta[-1])
            s.extend(i['s'] + s0)
            theta.extend(i['theta'] + th0)
        if self.repl:
            s.extend(self.repl['s'] + s[-1])
            theta.extend(self.repl['theta'] + theta[-1])
            self.repl = {}
        s = np.array(s[1:])
        theta = np.array(theta[1:])
        # print('theta')
        # print(theta)
        if theta[-1] < 2 * pi - 1:
            # print('theta: ', theta[-1])
            d_th = np.rad2deg(2 * pi - theta[-1])
            # todo calc last
            self.load_eq(False, False, [d_th, -s[-1], 'Const V'], True)
            return None, None
        else:

            self.s, self.theta = s, theta
            return s, theta

    def _set_trans(self):
        s, theta = self.xi()
        if s is not None:
            # s =self.r_b
            self.xy = self.main_v['x']
            if self.main_v['Type follow'] == 'needle':
                r_0 = sqrt(self.r_b ** 2 - self.xy ** 2)
                self.th_0 = np.arctan2(r_0, self.xy)
                self.ds = int(np.argwhere(theta > self.th_0)[0])

                dst = np.roll(s, -self.ds)
                print(f'\nso:{s}, sf:{dst}')
                r = dst + r_0
                self.r_c = sqrt(self.xy ** 2 + r ** 2),
                self.gamma_c = pi / 2 + arctan(self.xy / r),
                # phi = pi / 2 + gamma_c + atan(R * s.diff(theta) / r_c ** 2)  # todo diff t ot theta
            elif self.main_v['Type follow'] == 'plate':
                # r_0 = self.r_b
                self.th_0 = pi/2
                self.ds = int(np.argwhere(theta > self.th_0)[0])
                r = np.roll(s, -self.ds) + self.r_b

                self.r_c = sqrt(r ** 2 +  np.diff(theta, s)** 2)
                self.gamma_c = pi / 2 - arctan(diff(theta, s) / r)
                # delta_c = s.diff(theta) - S
            else:
                r_0 = sqrt((self.r_b + self.r_r) ** 2 - self.xy ** 2)
                self.th_0 = np.arctan2(r_0, self.xy) // (2 * pi)
                self.ds = int(np.argwhere(theta > self.th_0)[0])
                r = np.roll(s, -self.ds)+self.r_b
                phi = - arctan((diff(theta, s) - self.xy) / r)
                self.r_c = sqrt((r - self.r_r * cos(phi)) ** 2 - (self.xy + self.r_r * sin(phi)) ** 2)
                self.gamma_c = pi / 2 - arctan((self.xy + self.r_r * sin(phi)) / (r - self.r_r * cos(phi)))
                # ]

            # dis = np.array(cos(self.gamma_c), sin(self.gamma_c)) * self.r_c
            t = theta / self.omega
            y = r
            # y = sin(self.gamma_c)*self.r_c
            # y = y.flatten()
            self.follow_vals['R'] = y
            # for i in range(2):  # todo add vals to partial
            v = diff(t, y)
            self.follow_vals['v'] = v
            self.follow_vals['a'] = diff(t, v)
            print(f'r0: {r}, rb: {self.r_b}, x {self.xy}')
            # todo plot anim xy, r
            # r, v, a vs t, th

    def _set_rot(self):
        s, theta = self.xi()
        if s is not None:
            Y, X = self.main_v['Y'], self.main_v['x']
            e, l = self.main_v['e'], self.main_v['L']  # r_b, r_r
            if self.main_v['Type follow'] == 'needle':
                gamma_0 = arctan(Y / X) + np.arccos(
                    (X ** 2 + Y ** 2 + self.r_b ** 2 - l ** 2 - e ** 2) / (2 * self.r_b * sqrt(X ** 2 + Y ** 2)))
                alpha_0 = arctan(e / l) - arctan((self.r_b * sin(gamma_0 - Y)) / (X - self.r_b * cos(gamma_0)))
                alpha = alpha_0 - diff(theta, s)

                x_c = -X - l * cos(alpha) - e * sin(alpha),
                y_c = l * sin(alpha) - e * cos(alpha),
                # phi = pi / 2 + gamma_c + alpha - atan(s.diff(theta)
                # / r_c ** 2 * (X_c * (length * sin(alpha) - e * cos(alpha))
                # + Y_c * (length * cos(alpha) + e * sin(alpha))))

            elif self.main_v['Type follow'] == 'roller':
                self.r_r = self.main_v['r_r']
                alpha_0 = np.arccos(
                    (l ** 2 + X ** 2 + Y ** 2 - (self.r_r + self.r_b) ** 2) / (2 * l * sqrt(X ** 2 + Y ** 2))) + arctan(
                    X / Y)
                alpha = alpha_0 - diff(theta, s)
                chi = arctan((Y + l * (1 + diff(theta, s)) * sin(alpha)), (X - l * (1 + diff(theta, s)) * cos(alpha)))
                x_c = - X - l * cos(alpha) - self.r_r * sin(chi)
                y_c = -l * sin(alpha) - self.r_r * cos(chi)
                # phi - pi / 2 + alpha + chi,
            else:
                alpha_0 = - arctan(Y / X) - np.arccos((self.r_b + e) / sqrt(X ** 2 + Y ** 2))
                alpha = alpha_0 - diff(theta, s)
                delta_c = (X * cos(alpha) - Y * sin(alpha)) / (1 + diff(theta, s))
                x_c = - X - delta_c * cos(alpha) - e * sin(alpha)
                y_c = Y - delta_c * sin(alpha) - e * cos(alpha)

            self.r_c = sqrt(x_c ** 2 + y_c ** 2)
            self.gamma_c = arctan(x_c / y_c)
            # todo useful v, a
            t = theta / self.omega
            self.follow_vals['theta'] = alpha
            v_rot = diff(t, alpha)
            self.follow_vals['omega'] = v_rot
            self.follow_vals['alpha'] = diff(t[1:], v_rot)
            self.follow_vals['alpha_norm'] = v_rot ** 2 / np.linalg.norm((e, l))
            dis = np.array((x_c, y_c))
            for i, n in enumerate('xy'):
                x = dis[i]  # todo for a, v
                vx = diff(t, x)
                self.follow_vals['a' + n] = diff(t[1:], vx)
                self.follow_vals['v' + n] = vx
                self.follow_vals[n] = x

    def rot(self, th, painter, sca, off_s):

        if len(self.theta) == 0:
            s, th2 = np.ones(50) * self.r_b, np.linspace(0, 2 * pi)
            if self.main_v['Type Motion'] == 'Trans':
                self.follow_vals['R'] = sqrt(self.r_b ** 2 - self.xy ** 2) * np.ones(50)
                self.follow_vals['v'] = np.zeros(50)
                self.follow_vals['a'] = np.zeros(50)
            else:
                self.follow_vals['y'] = sin(th2) * s
                self.follow_vals['x'] = cos(th2) * s
                self.follow_vals['alpha'] = np.zeros(50)

        else:
            s = np.array(self.s) + self.r_b
            th2 = (np.array(self.theta) + th) % (2 * pi)
        cs = cos(th2) * s
        si = sin(th2) * -s
        xy = np.array((cs, si))
        self.follow(th, painter, sca, off_s)
        return xy.T * sca + off_s

    def follow(self, th, painter, sca, off_s):
        def transform_point_locals(*n):
            print('n :', n)
            xi = np.array(n).reshape((2, 2))
            # print('xi: ', xi)
            xis = xi * sca * np.array((1, -1))
            # print('xis: ', xis)
            xik = xis + off_s
            print('xik: ', xik)

            return [int(i) for i in xik.flatten()]

        def circular_transform_point_locals(c1, c2, r):
            ri = r * sca
            cen = np.array((c1, c2)) * sca * np.array((1, -1)) + off_s - ri
            return [int(i) for i in [*cen, 2 * ri, 2 * ri]]

        if self.main_v['Type Motion'] == 'Trans':
            y = self.follow_vals['R']  # assuming theta_0
            x = self.main_v['x']

        else:
            y = self.follow_vals['y']
            x = self.follow_vals['x']
        # print('y: ', y)
        # print('x: ', x)
        d_ns = (self.th_0 + th) % (2 * pi)
        print(d_ns)
        if len(self.theta) == 0:
            d_n = 0
        else:
            d_n = int(np.argwhere(np.array(self.theta) > d_ns)[0]) - self.ds
        print(f'th, {th};; dn,{d_n}')
        # print(f'y_dn {y[d_n-1:d_n+1]}::: y_-dn{y[-d_n-1:-d_n+1]}, y[0]:{y[0]}')
        y = np.roll(y, d_n)
        line_l = 30
        width_l = 2

        if self.main_v['Type Motion'] == 'Trans':
            y_cur = y[0]

            painter.setPen(QPen(Qt.red, width_l))
            pp = transform_point_locals(x, y_cur, x, y_cur + line_l)
            # print(pp)
            painter.drawLine(*pp)  # todo roller offset, roller cant gointo small hol
            # x+=r_rol*cos(theta_cur)
            if self.main_v['Type follow'] == 'roller':
                painter.setPen(QPen(Qt.blue, min(width_l - 2, 2)))
                pp = circular_transform_point_locals(x, y_cur, self.r_r)
                painter.drawEllipse(*pp)
            elif self.main_v['Type follow'] == 'plate':
                print('plate')
                pp = transform_point_locals(x - line_l*np.sign(x), y_cur, x, y_cur)
                painter.drawLine(*pp)

        else:

            x = np.roll(x, d_n)
            al = np.roll(self.follow_vals['alpha'], d_n)
            al_c = al[0]
            d_xy = np.array((sin(al_c), cos(al_c))) * self.main_v['e']

            painter.setPen(QPen(Qt.red, width_l))
            x_c = x[0]
            y_c = y[0]
            x_p, y_p = self.main_v['Y'], self.main_v['x']
            if self.main_v['Type follow'] == 'needle':
                x_cur = x_c + d_xy[0]
                y_cur = y_c + d_xy[1]
                pp = transform_point_locals(x_c, y_c, x_cur, y_cur)
                pp2 = transform_point_locals(x_cur, y_cur, x_p, y_p)
                painter.drawLine(*pp)
                painter.drawLine(*pp2)

            elif self.main_v['Type follow'] == 'roller':
                # todo put
                pp = transform_point_locals(x_c, y_c, x_p, y_p)
                pp2 = circular_transform_point_locals(x_c, y_c, self.r_r)
                painter.drawLine(*pp)
                painter.setPen(QPen(Qt.blue, min(width_l - 2, 2)))
                painter.drawEllipse(*pp2)

            elif self.main_v['Type follow'] == 'plate':

                x_cur = x_p - d_xy[0]
                y_cur = y_p - d_xy[1]
                pp = transform_point_locals(x_cur, y_cur, x_p, y_p)
                pp2 = transform_point_locals(x_c, y_c, x_cur, y_cur)
                painter.drawLine(*pp)
                painter.drawLine(*pp2)
            #
            #
        self.set_plot_d(d_n)
        # at theta = th, n*dtheta = th, y = roll n, if rot, x roll n

    def set_plot_d(self, roll_fact):
        pv = {}
        for i in 'Rva':
            pv[i] = np.roll(self.follow_vals[i],roll_fact)
        da = [[x,self.theta] for x in pv.values()]
        print('set da')
        # #plot(pv)
        # for i in ['theta', 'omega', 'alpha', 'alpha_norm']:
        #     pv[i] = np.roll(self.follow_vals[i], d_n)
        #
        # for i in 'xy':
        #     for ii in ["", "a", "v"]:
        #
        #         pv[ii+i] = np.roll(self.follow_vals[ii+i], d_n)
        # thus y at len m, dtheta = m/2pi
        #plot(pv)
        self.par.plot_w.update(da)

    def re(self, i, v):
        self.main_v[i] = v
        # todo recalc
        self.omega = self.main_v['Omega']
        self.r_b = self.main_v['r_b']
        # self.ty = main_v['Type Motion']

        self.xy = self.main_v['x']  # SWAP NAMES ON ver
        # self.r_r = main_v['r_r'] if main_v['r_r'] else None
        self.s0 = self.r_b

        self.res()
        # self.par.set_plot(self.partial_motion)


class aniWig(QWidget):
    def __init__(self, par):
        super().__init__()  # todo set max size, add disp for cam, offset for each from last?
        self.setMinimumSize(250, 250)
        self.scale_m = 10
        self.th = 0
        self.pix_sc = 0.02
        self.ang_sc = 3 / 32
        self.par = par

    def cen(self):
        return np.array((self.width(), self.height())) // 2

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.eraseRect(self.rect())
        points = self.par.cam.rot(self.th, painter, self.scale_m, self.cen())
        painter.setPen(QPen(Qt.cyan, 1, Qt.DashLine))
        ri = int(self.par.cam.r_b * self.scale_m)

        c2 = self.cen() - ri
        painter.drawEllipse(*c2, 2 * ri, 2 * ri)
        painter.setPen(QPen(Qt.darkMagenta, 2))
        painter.drawPoint(*self.cen())

        painter.setPen(Qt.green)
        for i in range(points.shape[0] - 1):
            painter.drawLine(int(points[i, 0]), int(points[i, 1]), int(points[i + 1, 0]), int(points[i + 1, 1]))

    def wheelEvent(self, event):
        mo = QApplication.keyboardModifiers()
        sca = event.angleDelta().y()

        if mo == Qt.ControlModifier:
            mod_sc = self.ang_sc * sca
            print(f'sca={sca},mod_scale={mod_sc}')
            self.th += np.deg2rad(mod_sc)
        else:
            self.scale_m += self.pix_sc * sca
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            self.th = 0


class Window(QMainWindow):
    def __init__(self):
        super().__init__()  # todo set max size, add disp for cam
        # todo fill rest of cam
        self.setWindowTitle('QMainWindow')
        self.full_c_v = []
        self.curr_type = 'Const V'
        self.curr = {'beta': 10, 'H': 1, 'Type': ['Const V', 'Harmonic', 'Cycloidal', 'Const A']}
        self.typ = {'Type Motion': ['Trans', 'rot'], 'Type follow': ['needle', 'roller', 'plate']}
        self.va = {'r_b': 5, 'x': 1, 'Omega': 2}

        self.cases = {'Roller': {'r_r': 0.1}, 'rot': {'e': 0.3, 'l': 1, 'y': 0}}

        # self.vst = {'Type': 'trans', 'RB':2, 'Omega':2, 'x':1,''beta': 5, 'H': 0.5}
        self._create_tools()
        self.cam = cam(self, **self.va)
        self.cam.main_v['Type Motion'], self.cam.main_v['Type follow'] = 'Trans', 'needle'
        self._set_data()
        self.list_index = 0
        self.cen = aniWig(self)
        self.setCentralWidget(self.cen)
        self.insert_list_wig_vals('+')
        self._set_p()

    def _set_p(self):
        self.plot_dock = QDockWidget('Plot')
        # add rem move up move down, single drag, selct, doble edit
        self.plot_w = HandlePlots()
        self.plot_dock.setWidget(self.plot_w)
        self.addDockWidget(Qt.RightDockWidgetArea, self.plot_dock)

    def _create_temp(self, ti='Type Motion'):
        self.in_p = {}  # todo check both
        self.lay_x = QGridLayout()
        mi = 0
        ni = 0
        ty = self.typ_c[ti].currentText()  # todo cleasr from layout
        if ti == 'Roller':
            self.lay_x.addWidget(QLabel('r_r'), mi, ni)
            j = QDoubleSpinBox()
            k = self.cases['Roller']['r_r']
            j.setValue(k)
            j.setSingleStep(round(0.1 * k, 2))
            self.lay_x.addWidget(j, mi + 1, ni)
            self.in_p['r_r'] = j
            j.valueChanged.connect(partial(self.dv, 'r_r'))
        # for li in range(3):
        #     self.o_lab[li].setText(self.out[ti][li])
        if ty == 'rot':
            for i, j in self.cases['rot'].items():
                self.lay_x.addWidget(QLabel('r_r'), mi, ni)
                k = QDoubleSpinBox()
                k.setValue(j)
                k.setSingleStep(round(0.1 * j, 2))
                self.lay_x.addWidget(j, mi + 1, ni)
                ni += 1
                if ni > 3:
                    ni = 0
                    mi += 2
                pass

        self.reset_lay()

    def dv(self, i):
        if i in ['r_r', 'e', 'l', 'y']:
            x = self.in_p
        else:
            x = self.cons_w
        v = x[i].value()
        self.cam.re(i, v)

    def _create_tools(self):
        def add_push_button(i):
            if i == '=':
                kk = '+'
            else:
                kk = i
            print('action I')
            j = QPushButton(kk)
            k = QAction(i)
            k.triggered.connect(partial(self.insert_list_wig_vals, i))
            j.clicked.connect(partial(self.insert_list_wig_vals, i))
            self.list_v[i] = j

            self.action_list[i] = k
            return j, k

        self.tool_dock = QDockWidget('list widget')
        # add rem move up move down, single drag, selct, doble edit
        self.tools = QWidget()
        self.ls_w = QListWidget()
        self.tool_dock.setWidget(self.tools)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.tool_dock)
        self.tl = QVBoxLayout()
        self.tool_layout = QGridLayout()
        self.pm_l = QHBoxLayout()
        self.lr_l = QVBoxLayout()
        self.tools.setLayout(self.tool_layout)
        self.list_v = {}
        self.action_list = {}

        self.ls_w.itemClicked.connect(self.item_swap)

        for add_comand in '=-':
            ji, ki = add_push_button(add_comand)
            self.pm_l.addWidget(ji)
            ki.setShortcut(f"ctrl+{add_comand}")

        for add_comand in ['Up', 'Down']:
            ji, ki = add_push_button(add_comand)
            self.lr_l.addWidget(ji)
            ki.setShortcut(add_comand)

        self.tool_layout.addWidget(self.ls_w, 0, 0, 1, 2)
        self.tool_layout.addLayout(self.lr_l, 1, 0)
        self.tool_layout.addLayout(self.pm_l, 1, 1)
        self.in_p = {}

    def item_swap(self, item):
        self.ls_w.setCurrentItem(item)
        self.list_index = self.ls_w.currentRow()

    def add_motion(self, replace=False):
        print('add motion')
        gg = [self.curr['beta'], self.curr['H'], self.curr_type]
        if replace:
            self.full_c_v[self.list_index] = gg
            jk = self.ls_w.currentItem()
            jk.setText(self.curr_type)
        else:
            self.full_c_v.insert(self.list_index, gg)
        self.cam.load_eq(self.list_index, replace, gg)
        self.update()

    def insert_list_wig_vals(self, input_command):
        print('I', input_command)
        self.list_index = self.ls_w.currentRow()
        if input_command == '+' or input_command == '=':  # todo add to menu
            # remove

            self.add_motion()  # todo maybe listitem? and check change motion
            # self.mo.insert(ind)
            self.ls_w.insertItem(self.list_index, self.curr_type)
            # remove dict
        elif input_command == '-':
            # remove
            self.ls_w.removeItem(self.list_index)
            self.full_c_v.remove(self.list_index)
            # remove dict
            # todo rem from cam
            pass
        elif input_command == 'Up':
            print('up')
            self.ls_w.currentItem.moveUp()
        else:
            print('down')
            self.ls_w.currentItem.moveDown()

    def _set_plots(self):
        pass

    def _set_diagram_anim(self):
        pass

    def set_curr(self, i):  # todo on swap, load new Values without updating
        j = self.curr_d[i]
        if isinstance(j, QComboBox):
            self.curr_type = j.currentText()
        else:
            self.curr[i] = j.value()

        self.add_motion(True)
        self.update()

    def set_ty(self, i):
        self.cam.re(i, self.typ_c[i].currentText())
        self._create_temp(i)
        self.update()

    def _set_data(self):
        self.data_dock = QDockWidget('DataWidget')
        # add rem move up move down, single drag, selct, doble edit
        self.data_w = QTabWidget()
        self.data_dock.setWidget(self.data_w)
        self.addDockWidget(Qt.RightDockWidgetArea, self.data_dock)

        self.datalay = QGridLayout()
        self.lay_m = QVBoxLayout()
        self.lay_x = QGridLayout()

        self.data_ls = {'Main': QWidget(), 'Current': QWidget()}
        self.w_v = {}
        self.cons_w = {}
        self.typ_c = {}
        self.curr_d = {}
        self.lay_2 = QGridLayout()

        n = 0
        m = 0

        self.data_ls['Current'].setLayout(self.lay_2)

        for i, j in self.data_ls.items():
            self.data_w.addTab(j, i)

        for i, j in self.curr.items():
            lab = QLabel(i)
            if isinstance(j, list):
                k = QComboBox()
                k.addItems(j)
                k.setCurrentText(j[0])
                k.currentTextChanged.connect(partial(self.set_curr, i))
            else:
                k = QDoubleSpinBox()
                k.setSingleStep(round(j * 0.1, 2))
                k.setValue(j)
                k.setRange(-100, 100)

                k.valueChanged.connect(partial(self.set_curr, i))
            self.curr_d[i] = k
            self.lay_2.addWidget(lab, m, n)
            self.lay_2.addWidget(k, m + 1, n)
            n += 1
            if n > 4:
                m += 2

        n = 0
        m = 0

        for i, j in self.typ.items():
            lab = QLabel(i)
            print('i', i)
            k = QComboBox()
            k.addItems(j)
            k.setCurrentText(j[0])
            k.currentTextChanged.connect(partial(self.set_ty, i))
            self.typ_c[i] = k
            self.datalay.addWidget(lab, m, n)
            self.datalay.addWidget(k, m + 1, n)
            n += 1
            if n > 4:
                m += 2

        # todo add n
        for i, j in self.va.items():
            lab = QLabel(i)
            k = QDoubleSpinBox()
            k.setSingleStep(round(j * 0.1, 2))
            k.setValue(j)
            k.valueChanged.connect(partial(self.dv, i))
            self.cons_w[i] = k
            self.datalay.addWidget(lab, m, n)
            self.datalay.addWidget(k, m + 1, n)

            n += 1
            if n > 4:
                m += 2
        # self.data_ls['Main'].setLayout(self.datalay)
        self._create_temp()

    def reset_lay(self):
        print('resetLay')
        self.lay_m = QVBoxLayout()
        self.lay_m.addLayout(self.datalay)
        self.lay_m.addLayout(self.lay_x)
        self.data_ls['Main'].setLayout(self.lay_m)

    def an(self):
        if self.ani:
            self.time.start()
        else:
            self.time.stop()
            self.th = 0
        self.time.timout.connect(self.up)

    def up(self):
        self.th += self.dt
        self.cam.rot(self.th)


# class mainWig(QWizard):
#     def __init__(self):
#         super().__init__()
#         self.ty = QComboBox()
#         # todo add condition to swap ui for all, save cam, save part
#
#     def page_2(self):
#         if self.ty.currentText() == 'Trans':
#             # vals
#             pass
#         else:
#             # vals
#             pass
#
# class funWig(QWizard):
#     def __init__(self):
#         super().__init__()
#         self.ty = QComboBox()
#         # todo add condition to swap ui for all, save cam, save part
#
#     def page_2(self):
#         if self.ty.currentText() == 'Trans':
#             # vals
#             pass
#         else:
#             # vals
#             pass
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
