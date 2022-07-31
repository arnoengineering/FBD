
from PyQt5.QtGui import QFont, QTextCharFormat, QPalette, QPainter, QColor  # QPainter, QPen,QBrush,
from PyQt5.QtCore import Qt, QDate, QSettings, QRect  # QTimer, QSize,
# from logging import exception
from PyQt5.QtWidgets import *
import numpy as np
import pandas as pd
import sys
from PyQt5.Qt import QSound
from saload import saveLoad


class DocStatus(QTableWidget):  # self.doc_dataframe_items
    def __init__(self, par, ti='Clinic', pos=Qt.RightDockWidgetArea):
        super().__init__()
        self.ti = ti
        self.sort_ascend = True
        self.sort_col = 'Name'
        self.par = par
        self.pos = pos
        self.d_r = 30
        #
        self.horizontalHeader().sectionClicked.connect(self.sort_by)
        self.cellClicked.connect(self.tab_s)
        self.cellDoubleClicked.connect(self.set_popup)
        self.dia = None
        self._init_dock()
        self.reset_table()

    def mousePressEvent(self, event):
        self.par.set_active_wig(self.ti)

    def _init_dock(self):
        self.dock = QDockWidget(self.ti)
        self.dock.setWidget(self)
        self.par.addDockWidget(self.pos, self.dock)

    def handle_sum(self, x, ty):
        ave_x = np.mean(x)
        cnt_x = x.size
        if ty == 'ave':
            re_c = ave_x
        elif ty == 'sd':
            re_c = np.sqrt(np.sum((x - ave_x) ** 2) / cnt_x)
        elif ty == 'cnt' or ty == 'sum':
            re_c = np.sum(x)
        else:  # ty == 'per': # todo in ty
            re_c = x / np.sum(x)  # for each
        return re_c  # for row: {for col:{handle_sum(row.head,col[:row.num()])}}

    def reset_table(self):
        self.clear()
        dd = self.par.doc_preferences

        r, c = dd.shape

        da = QDate.currentDate()
        for d in range(self.d_r):
            day = da.addDays(d)
            if day not in dd['Days']:
                dd = pd.concat([dd, pd.DataFrame([day], columns=['Days'])])

        dd.fillna(0)
        self.reset_table_main(dd, r, c)

    def reset_table_main(self, dd, r, c):

        # r += 1
        self.setHorizontalHeaderLabels(list(dd.columns))
        self.setRowCount(r)
        self.setColumnCount(c)
        for n in range(r):
            for m in range(c):
                tx = dd.iloc[n, m]
                if isinstance(tx, QDate):
                    j = tx.toString(self.par.combo['Date Format'].currentText())
                else:
                    j = str(tx)
                self.setItem(n, m, QTableWidgetItem(j))

    def tab_s(self, row_n, col_n):
        if row_n == 0:
            self.sort_by(col_n)
        r_n = self.item(row_n, 0).text()
        self.par.combo['doc'].setCurrentText(r_n)

    def sort_by(self, col):
        new_col = self.horizontalHeaderItem(col).text()
        if new_col == self.sort_col:
            self.sort_ascend = not self.sort_ascend
        else:
            self.sort_ascend = True
            self.sort_col = new_col
        print(f'column {self.sort_col}:  ascend {self.sort_ascend}')

    def update_active(self, doc):
        na = list(self.par.doc_data['Name']).index(doc)
        for r in range(self.rowCount()):
            for i in range(self.columnCount()):
                if r != na:
                    col = Qt.white
                else:
                    col = Qt.cyan
                self.item(r, i).setBackground(col)

    def set_popup(self, x, y):

        ind = (x, y)
        if ind[0] == 0:
            self.dia = docPopup(self, self.currentItem().text())
            self.dia.show()
        print('popup')
        pass

    # def read_date(self):
    #     for d in doc[doc]['dates']:
    #         qdate from str


class sound(QTableWidgetItem):
    def __init__(self,tex,snd):
        super().__init__()
        self.tex = tex
        self.snd_file = snd
        self.audio = QSound(self.snd_file)

    def play(self):
        self.audio.play()

    def stop(self):
        self.audio.stop()

    def show(self):
        self.setText(self.tex)

    def hide(self):
        self.setText('')
        