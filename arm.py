# todo date widewt
import numpy as np
from numpy import sin, cos, sqrt, deg2rad, zeros, linspace
import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from functools import partial
from scipy.integrate import cumtrapz

import sys


class gearPlot(pg.PlotWidget):
    def __init__(self, p):
        super().__init__()
        self.par = p
        self.p_i = self.getPlotItem()
        self.p_i.addLegend()
        self.p_i.setLabels(**{'title':  'Force, E, P of arm, vs angle from anatomical',
                            'left': 'F E P', 'bottom': 'angle rad'})

        self.pl = self.plot(pen='c', width=3, name='Force')
        self.pow = self.plot(pen='b', width=3, name='Pow')
        self.en = self.plot(pen='g', width=3, name='Energy')

    def set_v(self, v, c,e, p):
        self.pl.setData(v,c)
        self.pow.setData(v, p)
        self.en.setData(v, e)

class Window(QMainWindow):
    # noinspection PyArgumentList

    def __init__(self):
        # todo run scale
        super().__init__()
        self.gear = [[50, 34], [10, 12, 14, 15, 28]]
        self.active_g = np.zeros(2)

        self.setWindowTitle('QMainWindow')
        self.cen = QWidget()
        self.scale_n = [[10,2], [10, 3]]
        self.layout = QGridLayout()
        self.cen.setLayout(self.layout)
        self.setCentralWidget(self.cen)
        self.running = False

        self.pl = gearPlot(self)
        self.p_dock = QDockWidget('plots')
        self.p_dock.setWidget(self.pl)
        self.addDockWidget(Qt.RightDockWidgetArea, self.p_dock)
        self._set_tool()
        self.sol()
        # self._set_data()
        # self._set_tar()

    def _set_tool(self):
        # scale
        self.indi = {}
        self.bicon = {'Bicep Connect Ulna': 3., 'Bicep Connect Humor': 4., 'Ulna': 30.,
                      'Humor':40., 'Mass':10., 'Time': 1}
        n = 0
        m = 0
        for v in self.bicon.keys():
            if m > 2:
                m = 0
                n += 2
            la = QLabel(v)
            j = QLineEdit()
            j.setText(str(self.bicon[v]))
            j.editingFinished.connect(partial(self.new_d, v))
            self.indi[v] = j
            self.layout.addWidget(la, n, m)
            self.layout.addWidget(j, n + 1, m)
            m += 1

        self.out = {}
        for ni, i in enumerate(['Energy', 'Power']):
            lab = QLabel(i)
            lab_n = QLabel('0')
            self.layout.addWidget(lab, n+2, ni)
            self.layout.addWidget(lab_n, n + 3, ni)
            self.out[i] = lab_n

    def new_d(self, v):
        val = self.indi[v].text()
        v2 = float(val)
        self.bicon[v] = v2
        self.sol()

    def sol(self):
        lh = self.bicon['Humor'] - self.bicon['Bicep Connect Humor']
        th =np.deg2rad(np.linspace(5, 170))
        force_g = 9.81*self.bicon['Mass']*sin(th)
        th2 = np.pi-th
        len_bi = sqrt(lh**2 + self.bicon['Bicep Connect Ulna']**2 - 2 * self.bicon['Bicep Connect Ulna']*lh*cos(th2))
        th3 = np.arcsin(sin(th2)*lh/len_bi)
        mom_fact_b = sin(th3)*self.bicon['Bicep Connect Ulna']
        mom_g = force_g * self.bicon['Ulna']
        bi_f = mom_g/mom_fact_b / 9.81

        enrg = cumtrapz(mom_fact_b, th, initial=0)

        power = cumtrapz(enrg,dx=(th[-1]-th[0])/self.bicon['Time'], initial=0)
        self.out['Energy'].setText(str(enrg[-1]))
        self.out['Energy'].setText(str(power[-1]))
        self.pl.set_v(th,bi_f,enrg, power)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    audio_app = Window()
    audio_app.show()
    sys.exit(app.exec_())
