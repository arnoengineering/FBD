from functools import partial

from PyQt5.QtGui import QPainter
from matplotlib import pyplot as plt

from Beams.Loadings import *
from beam_tables import *

from PyQt5.QtWidgets import *

import sys
from beam import beam
from sections import *


plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica"]})
"""add solution and relation equations, add relivant tables from
add logical vars and prints
plot track, plot sigularty, solve for stresses, add database"""
# car,


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


class Dispsuport(QWidget):
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


class DispMF(QWidget):
    def __init__(self):
        super().__init__()
        self.pix_per_N = 5
        self.pos = np.zeros(2)
        self.r = 5
        self.m = -1  # dir, isomet


class BeamWidget(QWidget):
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
        self.cen = BeamWidget(None,None)
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