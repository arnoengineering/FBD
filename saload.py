# import sympy as sy
from PyQt5.QtGui import QPainter, QPen, QFont, QBrush, QTextCharFormat, QPolygon, QPalette
from numpy import cos, sin, arctan, sqrt, pi, linspace, arange
# import os
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer, QSize, QDate, QPoint, QCalendar  # , QPointF, QPoint

from PyQt5.QtWidgets import *
import sys


class saveLoad(QFileDialog):
    def __init__(self):
        super().__init__()
        self.setModal(True)
        self._set_f_t()
        self.load_settings()

    def load_f_type(self, names):

        st = []

        for na in names:
            if self.acceptMode() == QFileDialog.AcceptOpen:
                st_2 = ', '.join([f'*.{ty}' for ty in self.f_t[na]])
                na_1 = f'{na} files: ({st_2})'
                st.append(na_1)
            else:
                print('ya')
                for ty in self.f_t[na]:
                    na_1 = f'{na} file: (*.{ty})'
                    st.append(na_1)
        return ';; '.join(st)

    def _set_f_t(self):
        self.combo = {'User Readable': ['exel', 'csv'], 'data frame': ['jason', 'exel', 'csv']}
        self.f_t = {'jason': ['jason'],'csv': ['csv'], 'excel': ['xmls', 'xslm'], 'text': 'txt'}

    # def load_func(self, func):
    #     def wrap():
    #         self.setDefaultSuffix('csv')  # todo run type ana
    #         self.setAcceptMode(QFileDialog.AcceptSave)
    #         func()
    #     return wrap
    def load_func(self):
        self.setDefaultSuffix('csv')  # todo run type ana
        self.setAcceptMode(QFileDialog.AcceptSave)

    # @load_func
    def load_settings(self):
        self.load_func()
        self.setNameFilter(['jason', 'csv','excel'])
        pass

    def setNameFilter(self, filters):
        super().setNameFilter(self.load_f_type(filters))

    def load_doc_preferences(self):
        pass

    def save_doc_preferences(self):
        pass

    def load_sedual(self):
        pass

    def save_secdual(self):
        pass

    def save_settings(self):
        self.setAcceptMode(QFileDialog.AcceptOpen)
        self.setNameFilter(self.load_f_type(['jason', 'csv', 'excel']))
        pass

    def save_ex(self):  # todo save open multy type
        pass

    def save_jsn(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = saveLoad()
    win.show()
    sys.exit(app.exec_())
