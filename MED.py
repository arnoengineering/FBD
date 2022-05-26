# import sympy as sy
from PyQt5.QtGui import QPainter, QPen, QFont
from numpy import cos, sin, arctan, sqrt, pi, linspace, arange
# import os
from PyQt5.QtCore import Qt, QTimer, QSize, QDate  # , QPointF, QPoint
import pandas as pd
import pyqtgraph as pg
import numpy as np

# from numpy.linalg import norm


from PyQt5.QtWidgets import *
from functools import partial
from medgoogle import SchedualOptomizer
import sys

# todo save, read from list

patient_time = {'claassens': 30, 'dehlen': 20, 'lategan': 15}
# todo add stats, here vs away for each doc, and for group and anitetist, surgion
# todo table view, only one call per day
call_list = {}
walk_in_list = {}
"""test for demend can put weeends diff, then check for no call on weekends"""


def doc_behind(doc):
    td = patient_time[doc] * docs_list[doc]['patients behind']
    si = '-' if td < 0 else '+'  # todo hour format
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

        self.docs = [{'Name': 'Dehlen', 'status': 'away', 'ontime delta': '-', 'patients behind': 0},
                     {'Name': 'lategan', 'status': 'here', 'ontime delta': 't+30', 'patients behind': 2}]
        self.cmd_ls = {'Mode': ['Single', 'Range']}
        # todo etit doc properties ie anestetics..surgery, add rm doc, save configs
        self.button_list = ['solve']

        self.doc_data = pd.DataFrame.from_records(self.docs)
        self.cmd_ls['doc'] = self.doc_data['Name']
        self.active_doc = self.docs[0]['Name']
        # add 'avail': {'pacient':'arno', 'room':4}
        self._create_tools()
        self.solver = SchedualOptomizer()

    # tool-list: add prefernce, add away, force update, split into two docs per day,
    # run solver, rerun solver, save solver, export solver,
    # doc time behind

    def _create_tools(self):
        self.cen = DocStatus(self)  # for docter clinic
        self.setCentralWidget(self.cen)
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
        self.doc_select_box = QComboBox()
        self.selet_mode = QComboBox()
        self.cen.reset_table()

        #
        # for i in self.docs.keys():  # todo set default secondart
        #     self.doc_select_box.addItem(i)
        #
        # self.doc_select_box.currentTextChanged.connect(self.cen.reset_outputs)

        n = 0
        m = 0
        self.typ_c = {}
        for wig_name, opt in self.cmd_ls.items():
            lab = QLabel(wig_name)
            print('i', wig_name)
            k = QComboBox()
            k.addItems(opt)
            k.setCurrentText(opt[0])
            k.currentTextChanged.connect(partial(self.run_cmd, wig_name))
            self.typ_c[wig_name] = k
            self.tool_layout.addWidget(lab, m, n)
            self.tool_layout.addWidget(k, m + 1, n)
            n += 1
            if n > 4:
                m += 2

        self.in_p = {}

    def run_cmd(self, i):
        print('cmd', i)
        if i == 'doc away':
            print('date, doc away')
            # set doc away
        elif i == 'solve':
            self.solver.run_scedual()

        #     lab = QLabel(i) todo prefernce 0-4 foe each option, away, not work...

        #         m += 2
        elif i == 'doc':
            self.active_doc = self.typ_c[i].currentText()
            self.cen.update_active(self.active_doc)

    def load_settings(self):
        pass

    def load_doc_preferences(self):
        pass

    def save_doc_preferences(self):
        pass

    def load_sedual(self):
        pass

    def save_secdual(self):
        pass

    def save_settings(self):
        pass


class Calendar(QCalendarWidget):
    def __init__(self):
        super().__init__()
        self.less = 5
        self.startdate = None
        self.endate = None

    # def paintCell(self, painter, rect, date):
    #     super(Calendar, self).paintCell(painter, rect, date)
    #
    #     # checking if date is selected date
    #     if date == self.selectedDate():
    #         # saving the painter
    #         painter.save()
    #
    #         # creating a QFont object
    #         font = QFont()
    #
    #         # setting pixel size of the font
    #         font.setPixelSize(11)
    #
    #         # making font bold
    #         font.setBold(True)
    #
    #         # making font italic
    #         font.setItalic(True)
    #
    #         # setting font to the painter
    #         painter.setFont(font)
    #
    #         # drawing text
    #         painter.drawText(
    #             rect.topLeft() + QPoint(10, 10),
    #             "{}".format("Geek"),
    #         )
    #
    #         # restoring the painter
    #         painter.restore()
    # method for components

    def UiComponents(self):
        # creating a QCalendarWidget object

        # setting cursor
        self.setCursor(Qt.PointingHandCursor)

        # setting size of the calendar
        self.resize(350, 240)

        # setting font to the calendar
        self.setFont(QFont('Times', 5))

        # move the calendar
        self.calendar.move(10, 10)
        # lower bound date
        l_date = QDate(2020, 6, 5)

        # upper bound date
        u_date = QDate(2020, 6, 15)

        # setting date range
        self.setDateRange(l_date, u_date)

    def update_date(self, date):  # todo main window
        self.date_range.append(date)
        self.date_range.sort()
        if self.selectionMode() == 'Range':
            for i in range(len(self.date_wig)):
                self.date_wig[i] = self.date_range[i]  # widgits froom list
            self.setDateRange(*self.date_range)

        else:
            for i in range(len(self.date_wig)):
                self.date_wig[i].setClickable(False)  # widgits froom list

    def set_d(self):

        for dat in self.date_range:
            self.docs[self.active_doc][self.condition].append(dat)  # todo remove option, order to store
        if self.active_doc:
            pass
        else:
            print('select doctor')

    def set_start_day(self, d):
        self.firstDayOfWeek()


class DocStatus(QTableWidget):
    def __init__(self, par):
        super().__init__()
        self.par = par
        # active_doc.setItemNum
        self.cellClicked.connect(self.tab_s)
        self.reset_table()

    def reset_table(self):  # todo sort by n, add filters, add wigit for current doctor stats, day week month
        self.clear()
        # sort in pd then pass
        r, c = self.par.doc_data.shape
        # r = max(len(x) for x in self.current_data.values())
        self.setRowCount(r)
        self.setColumnCount(c)
        self.setHorizontalHeaderLabels(list(self.par.doc_data.columns))
        for n in range(r):
            for m in range(c):
                self.setItem(n, m, QTableWidgetItem(str(self.par.doc_data.iloc[n, m])))

    # todo add process so click to add step and move, add add x
    def tab_s(self):
        col_n = self.currentRow()
        r_n = self.item(col_n, 0).text()
        print('doc selected, ', r_n)

        self.par.typ_c['doc'].setCurrentText(r_n)

    def update_active(self, doc):
        na = list(self.par.doc_data['Name']).index(doc)
        for r in range(self.rowCount()):
            for i in range(self.columnCount()):
                if r != na:
                    col = Qt.white
                else:
                    col = Qt.cyan
                self.item(r, i).setBackground(col)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
"""

}"""
