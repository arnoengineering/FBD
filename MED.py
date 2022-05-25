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
from medgoogle import SchedualOptomizer
import sys


docs_list = {'delin':{'status':'away','ontime delta':'-', 'patients behind': 0},
             'lategan': {'status':'here','ontime delta':'t+30', 'patients behind': 2}}
             # add 'avail': {'pacient':'arno', 'room':4}

# todo save, read from list

patient_time = {'claassens': 30, 'dehlen':20,'lategan': 15}
# todo add stats, here vs away for each doc, and for group and anitetist, surgion
# todo table view, only one call per day
call_list = {}
walk_in_list = {}
"""test for demend can put weeends diff, then check for no call on weekends"""



def doc_behind(doc):
    td = patient_time[doc]*docs_list[doc]['patients behind']
    si = '-' if td < 0 else '+' # todo hour format
    docs_list[doc]['ontime delta'] = f't {si} {abs(td)}'

#
# def walk_in(date):
#     if weekday(date) <=1: # sunday or monday
#         n_d = date-1
#     else:
#         n_d = date
#     walk_in_list[date-1] = call_list[n_d]


# minimize cost where call = 1-n, and call != people away
class Window(QMainWindow):
    def __init__(self):
        super().__init__()  # todo set max size, add disp for cam
        # todo fill rest of cam
        self.setWindowTitle('Shedualer')
        self.cmd_ls = ['hello', 'gbfn', 'solve']
        self._create_tools()
        self.solver = SchedualOptomizer()

    # tool-list: add prefernce, add away, force update, split into two docs per day,
    # run solver, rerun solver, save solver, export solver,
    # doc time behind

    def _create_tools(self):
        self.cen = QTableWidget()  # for docter clinic
        self.clinic_wig = QTableWidget()
        self.cal_wig = QCalendarWidget()
        self.tool_wig = QWidget()

        self.clinic_dock = QDockWidget('Status Clinic')
        self.cal_dock = QDockWidget('cal')
        self.tool_dock = QDockWidget('Tools')
        # add rem move up move down, single drag, selct, doble edit

        self.clinic_dock.setWidget(self.clinic_wig)
        self.cal_dock.setWidget(self.cal_wig)
        self.tool_dock.setWidget(self.tool_wig)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.clinic_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.cal_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tool_dock)

        self.tool_layout = QGridLayout()

        self.tool_wig.setLayout(self.tool_layout)
        self.list_v = {}
        self.action_list = {}

        for add_comand in self.cmd_ls:
            j = QPushButton(add_comand)

            j.clicked.connect(partial(self.run_cmd, add_comand))
            self.list_v[add_comand] = j

        self.in_p = {}

    def run_cmd(self, i):
        print('cmd', i)
        if i == 'doc away':
            print('date, doc away')
            # set doc away
        elif i == 'solve':
            self.solver.run_scedual()
        # self.data_ls = {'Main': QWidget(), 'Current': QWidget()}
        # self.w_v = {}
        # self.cons_w = {}
        # self.typ_c = {}
        # self.curr_d = {}
        # self.lay_2 = QGridLayout()
        #
        # n = 0
        # m = 0
        #
        # self.data_ls['Current'].setLayout(self.lay_2)
        #
        # for i, j in self.data_ls.items():
        #     self.data_w.addTab(j, i)
        #
        # for i, j in self.curr.items():
        #     lab = QLabel(i)
        #     if isinstance(j, list):
        #         k = QComboBox()
        #         k.addItems(j)
        #         k.setCurrentText(j[0])
        #         k.currentTextChanged.connect(partial(self.set_curr, i))
        #     else:
        #         k = QDoubleSpinBox()
        #         k.setSingleStep(round(j * 0.1, 2))
        #         k.setValue(j)
        #         k.setRange(-100, 100)
        #
        #         k.valueChanged.connect(partial(self.set_curr, i))
        #     self.curr_d[i] = k
        #     self.lay_2.addWidget(lab, m, n)
        #     self.lay_2.addWidget(k, m + 1, n)
        #     n += 1
        #     if n > 4:
        #         m += 2
        #
        # n = 0
        # m = 0
        #
        # for i, j in self.typ.items():
        #     lab = QLabel(i)
        #     print('i', i)
        #     k = QComboBox()
        #     k.addItems(j)
        #     k.setCurrentText(j[0])
        #     k.currentTextChanged.connect(partial(self.set_ty, i))
        #     self.typ_c[i] = k
        #     self.datalay.addWidget(lab, m, n)
        #     self.datalay.addWidget(k, m + 1, n)
        #     n += 1
        #     if n > 4:
        #         m += 2
        #
        # # todo add n
        # for i, j in self.va.items():
        #     lab = QLabel(i)
        #     k = QDoubleSpinBox()
        #     k.setSingleStep(round(j * 0.1, 2))
        #     k.setValue(j)
        #     k.valueChanged.connect(partial(self.dv, i))
        #     self.cons_w[i] = k
        #     self.datalay.addWidget(lab, m, n)
        #     self.datalay.addWidget(k, m + 1, n)
        #
        #     n += 1
        #     if n > 4:
        #         m += 2
        # # self.data_ls['Main'].setLayout(self.datalay)

class Calendar(QCalendarWidget):
    def __init__(self):
        super().__init__()
        self.less = 5
        self.startdate = None
        self.endate = none

    def paintCell(self, painter, rect, date):
        super(Calendar, self).paintCell(painter, rect, date)

        # checking if date is selected date
        if date == self.selectedDate():
            # saving the painter
            painter.save()

            # creating a QFont object
            font = QFont()

            # setting pixel size of the font
            font.setPixelSize(11)

            # making font bold
            font.setBold(True)

            # making font italic
            font.setItalic(True)

            # setting font to the painter
            painter.setFont(font)

            # drawing text
            painter.drawText(
                rect.topLeft() + QPoint(10, 10),
                "{}".format("Geek"),
            )

            # restoring the painter
            painter.restore()
    # method for components
    def UiComponents(self):
        # creating a QCalendarWidget object
        # as Calendar class inherits QCalendarWidget
        self.calendar = Calendar(self)

        # setting cursor
        self.calendar.setCursor(Qt.PointingHandCursor)

        # setting size of the calendar
        self.calendar.resize(350, 240)

        # setting font to the calendar
        self.calendar.setFont(QFont('Times', 5))

        # move the calendar
        self.calendar.move(10, 10)
        # lower bound date
        l_date = QDate(2020, 6, 5)

        # upper bound date
        u_date = QDate(2020, 6, 15)

        # setting date range
        calendar.setDateRange(l_date, u_date)


        grid

    def update_date(self,date):  # todo main window
        self.date_range.append(date)
        self.date_range.sort()
        if self.selectionMode() == 'Range':
            for i in range(len(self.date_wig)):
                self.date_wig[i] = self.date_range[i] # widgits froom list
            self.setDateRange(*self.date_range)

        else:
            for i in range(len(self.date_wig)):
                self.date_wig[i].setClickable(False) # widgits froom list

    def set_d(self):

        for dat in self.date_range:
            self.docs[self.active_doc][self.condition].append(dat)  # todo remove option, order to store
        if self.active_doc:
            pass
        else:
            print('select doctor')



    def set_start_day(self,d):
        self.firstDayOfWeek()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
"""

}"""