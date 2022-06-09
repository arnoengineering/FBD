from PyQt5.QtGui import QFont, QTextCharFormat, QPalette, QPainter  # QPainter, QPen,QBrush,
from PyQt5.QtCore import Qt, QDate, QSettings, QRect  # QTimer, QSize,

from PyQt5.QtWidgets import *

import pandas as pd
import numpy as np
import sys

from functools import partial
from medgoogle import SchedualOptomizer


def sort_day(ls):
    ls.sort(key=lambda x: x.toString(Qt.TextDate))


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Call Schedule Optimizer')
        self.settings = QSettings('Claassens Software', 'Calling LLB_2022')  # todo change
        self.start_up_promt()
        self._update_set()
        self._set_list()
        self._set_empty()

        self._set_dataframes()

        self.test_doc()
        self._set_center()
        self._set_clinic()
        self._create_tools()

        self._creat_toolbar()

    def start_up_promt(self):
        # todo add dialog with load defults or user, show on startup?
        pass

    def _set_list(self):
        self.docs = [{'Name': 'Dehlen', 'status': 'away', 'ontime delta': '-', 'patients behind': 0},
                     {'Name': 'lategan', 'status': 'here', 'ontime delta': 't+30', 'patients behind': 2}]

        self.cmd_ls = {'Mode': ['Single', 'Range'],
                       'Weekday Start': ['Sun', 'Mon'],
                       'Setting Mode': ['Call', 'WI', 'Away', 'Here']}

        self.wn = 'Show/Hide Weeknumbers'
        self.button_list = ['solve', self.wn, 'Today', 'Apply', 'Save', 'Load']

        self.date_n = ['StartDate', 'EndDate']

    def _set_empty(self):
        self.set_mode = None
        self.active_col = Qt.black
        self.active_doc = self.docs[0]['Name']
        self.date_list = {}
        self.av = {}
        self.list_v = {}
        self.action_list = {}
        self.typ_c = {}

    def _set_dataframes(self):
        self.schedul = pd.DataFrame(columns=['Date', 'Call', 'WI'])
        self.doc_data = pd.DataFrame.from_records(self.docs)
        self.cmd_ls['doc'] = self.doc_data['Name']
        # self.av = {columns=['Date']+self.cmd_ls['doc'])
        # add 'avail': {'pacient':'arno', 'room':4}

    def set_combo(self, in_ls, out_ls, n=0, m=0, func=None):
        if not func:
            func = self.run_cmd
        for wig_name, opt in in_ls.items():
            lab = QLabel(wig_name)
            print('i', wig_name)
            k = QComboBox()
            k.addItems(opt)
            k.setCurrentText(opt[0])
            k.currentTextChanged.connect(lambda x: func(wig_name, x))
            out_ls[wig_name] = k
            self.tool_layout.addWidget(lab, m, n)
            self.tool_layout.addWidget(k, m + 1, n)
            n += 1
            if n > 4:
                m += 2
                n = 0
        return n, m

    def solve_doc(self):
        pass

    def set_norm(self, in_ls, out_ls, n=0, m=0, func=None, ty='but'):

        if not func:
            func = self.run_cmd
        if ty == 'but':
            for wig_name in in_ls:
                k = QPushButton(wig_name)
                out_ls[wig_name] = k
                self.tool_layout.addWidget(k, m, n)
                k.clicked.connect(partial(func, wig_name))
                n += 1
                m_max = m
                if n > 4:
                    m += 1
                    n = 0

        elif ty == 'da':
            for wig_name in in_ls:
                lab = QLabel(wig_name)
                print('i', wig_name)
                da = QDateEdit()
                da.setDate(QDate.currentDate())
                da.setCalendarPopup(True)
                da.dateChanged.connect(lambda x: func(x))
                # da.bud
                out_ls[wig_name] = da
                self.tool_layout.addWidget(lab, m, n)
                self.tool_layout.addWidget(da, m + 1, n)
                n += 1

                if n > 4:
                    m += 2
                    n = 0
        return n, m

    def _creat_toolbar(self):
        self.font_sizes = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
        # self.img_loc = self.file_loc + '/img/'
        self.tool_bar = QToolBar('Main toolbar')
        self.cal_tool_bar = QToolBar('Calendar')  # todo add swap
        self.table_tool = QToolBar('Tables')
        self.col = QColorDialog()

        self.font_wig = {'Font': QFontComboBox(), 'Size': QComboBox(),'Capital': QComboBox()}
        self.font_op = []
        self.but_edit = {}
        # view set by status
        self.font_ty = {'Call': QFont.Times, 'WI': QFont.Times}
        self.font_ty_wig = {}
        tb_op = ['save', 'load', 'add', 'B', 'I', 'U']

        for it in tb_op:
            j = QPushButton(it)
            # j.setIcon(self.img_loc+it)
            # todo add hotkey, add to menu with icon
            self.but_edit[it] = j
            self.tool_bar.addWidget(j)
        self.addToolBar(self.tool_bar)
        self.but_edit['color'] = ColorButton('Color', self)
        self.tool_bar.addWidget(self.but_edit['color'])

        # todo bold underline, italic, save load, dload lego
        # self.but_edit['color'].clicked.connect(self.color)

        self.cap_op = ['As Entered', 'UPPERCASE', 'lowercase' 'Capitalize', 'SurName']
        self.font_wig['Capital'].addItems(self.cap_op)
        self.font_wig['Capital'].currentIndexChanged.connect(self.set_cap)

        self.font_wig['Font'].currentFontChanged.connect(self.set_active_font)
        self.font_wig['Size'].addItems([str(x) for x in self.font_sizes])  # todo add user val check if int and user val

        for i in self.font_wig.values():
            self.tool_bar.addWidget(i)

        # for selectic cal or walkin to edit, disable if not on cal, add conditional to tables
        self.font_edit = QComboBox()
        self.font_edit.addItems(['Call', 'WI'])

    def set_active_font(self,font):
        print('running activefont')
        if self.font_edit.isEnabled():
            print('font_enabled')
            self.font_ty[self.font_edit.currentText()] = font
            print('set font: ', font)
        else:
            print('font_disabled')
            c = self.is_focus()
            self.font_ty_win[c] = font

    def is_focus(self):  # todo on focuscanged

        c = self.findChild(Calendar)
        print('loaded cal')
        if c.hasFocus():
            print('cal focus')
            return 'Cal'
        else:
            print('no cal')
            for i in self.findChildren(QDockWidget):
                print('i test focus')
                if i.hasFocus():
                    j = i.windowTitle()
                    print('i had focus: ', j)
                    return j

    def sur_cap(self, st):
        st = st.lower()
        pass # split sr bsased on if van in group of peplename, then caps each and join

    def set_cap(self, i):
        ty = self.font_edit.currentText()
        if i < 5:  #enum
            self.font_style[ty] = i
        else:   # todo return func, but thewn have to run on calendar loop
            pass

    def color(self):
        # c = self.col.exec()
        self.col.setCurrentColor(self.active_col)
        self.active_col = QColorDialog().getColor()

    def _update_set(self):  # onpopup combo
        # open file set to these, then run normal
        print('loading_all')
        self.call_op = {'Font': [QFont.Times, QFont.Times], 'Size': [12, 11], 'Italics': [False, True],
                        'bold': [True, False], 'Capital': ['Upper','lower', 'as endered', 'capital', 'surname']}
        self.setting_keys = ['Date Format',# y-m-d,y-d-m,d-m-y,m-d-y
                             'Weekday Format',# long,sort,,let
                             'Start Week Format',
                             'Call Font',
                             'call Size',
                             'call color',
                             'call capital',  # todo itterate
                             'walk in Font',
                             'walk in Size',
                             'walk in color',
                             'Week Number',
                             'Doc File Loc',  # todo all file locs
                             'Window Size',
                             'Window Loc',  # todo active widgets, size, loc
                             ]
        for ke in self.settings.allKeys():
            val = self.settings.value(ke,10)  # todo add others add functions on soime vals_ try....
            ke_new = ke.lower().replace(' ', '_')  # todo change  so defalt vas in dict
            print(f'key, val: {ke}, {val}')
            # todo save special, load on default or last, use create settings dialog based on initial creation
            # self.__setattr__(ke_new, val)
        self.week_mum = False
        self.default_scedule_loc = ''  # file_path
        self.default_doc_list_loc = ''  # file_path
        self.default_doc_pref_loc = ''  # file_path
        self.default_wins = ''

    def _set_center(self):
        self.cal_wig = Calendar(self)
        self.solver = SchedualOptomizer()
        self.setCentralWidget(self.cal_wig)

    def _set_clinic(self):
        self.doc_stat = DocStatus(self, 'Doc Stats')  # for docter clinic
        self.day_stat = DocStatus(self, 'Dayly Stats')
        self.clinic_wig = DocStatus(self, 'Live Clinic', Qt.LeftDockWidgetArea)

    def _create_tools(self):
        self.tool_wig = QWidget()
        self.tool_dock = QDockWidget('Tools')
        self.tool_dock.setWidget(self.tool_wig)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.tool_dock)

        self.tool_layout = QGridLayout()

        self.tool_wig.setLayout(self.tool_layout)

        # ___________comboboxes_______
        self.doc_select_box = QComboBox()
        self.selet_mode = QComboBox()

        n = 0
        m = 0

        n, m = self.set_norm(self.button_list, self.typ_c, n, m)
        n, m = self.set_combo(self.cmd_ls, self.typ_c, n, m)

        self.set_norm(self.date_n, self.date_list, n, m, self.cal_wig.update_date, ty='da')

    def run_cmd(self, i, ex=None):
        print('cmd', i)
        if i == 'doc away':
            print('date, doc away')
            # set doc away
        elif i == 'Mode':
            self.cal_wig.swap_select_mode(self.typ_c[i].currentText())
        elif i == 'solve':
            self.solver.run_scedual()

        elif i == 'Setting Mode':
            self.set_mode = ex
        elif i == 'doc':
            self.active_doc = ex
            self.cen.update_active(ex)
        elif i == self.wn:
            # QCalendarWidget.noVer
            self.cal_wig.set_wig_2()
        elif i == 'Weekday Start':
            self.cal_wig.week_start(ex)
        elif i == "Today":
            self.cal_wig.set_today()
        elif i == "Apply":
            self.run_doc_solve()

    def run_doc_solve(self):
        for day in self.cal_wig.full_date_list:
            print(f'Day {day}, doc {self.typ_c["doc"].currentText()}, status {self.set_mode}')
            # self.av[day][self.active_doc]['Status'] = self.set_mode
        # doc_on_day()

    def doc_on_day(self, date):
        if isinstance(date, list):
            scd = self.schedul.loc[self.schedul['Date'].isin(date)]
            doc = list(scd['Call'])
            doc_wi = list(scd['WI'])
        else:
            scd = self.schedul.loc[self.schedul['Date'] == date]
            doc = list(scd['Call'])[0]
            doc_wi = list(scd['WI'])[0]
        return doc, doc_wi

    def test_doc(self):
        doc_l = ['Dehlen', 'DeRider', 'Lategan']
        l_doc_l = len(doc_l)
        for i in range(1, 30):
            date = QDate(2022, 6, i)
            da = i % l_doc_l
            da_w = (i - 1) % l_doc_l
            df_l = [date, doc_l[da], doc_l[da_w]]
            df = pd.DataFrame([df_l], columns=['Date', 'Call', 'WI'])
            self.schedul = pd.concat([self.schedul, df], ignore_index=True)

    def closeEvent(self, event):  # todo load settings
        self.settings.setValue("Geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        for child in self.children():
            self.settings.beginGroup(child.objectName())  # todo correcxt?
            self.settings.setValue("Geometry", child.saveGeometry())
            self.settings.setValue("windowState", child.saveState())
            self.settings.endGroup()
        self.settings.sync()
        event.accept()


class Calendar(QCalendarWidget):
    def __init__(self, par):
        super().__init__()
        self.par = par
        self.st_h = 1
        # self.less = 5
        # self.startdate = None
        # self.endate = None
        self.sel = 'Single'

        self.full_date_list = [QDate.currentDate(), QDate.currentDate()]
        self.clicked.connect(lambda checked: self.on_cl(checked))
        self.setGridVisible(True)

        self.set_wig_2()
        self._init_calendar()
        self._init_high()

    def _init_high(self):
        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(self.palette().brush(QPalette.Highlight))
        self.highlight_format.setForeground(self.palette().color(QPalette.HighlightedText))

    def _init_calendar(self):
        self.calendar_view = self.findChild(QTableView, "qt_calendar_calendarview")
        self.calendar_delegate = CalendarDayDelegate(par=self)
        self.calendar_view.setItemDelegate(self.calendar_delegate)

    def set_wig_2(self):
        self.st_h = (self.st_h + 1) % 2

        i3 = self.VerticalHeaderFormat(self.st_h)
        self.setVerticalHeaderFormat(i3)

    def week_start(self, j):
        k = 1 if j == 'Mon' else 7
        self.setFirstDayOfWeek(Qt.DayOfWeek(k))

    def set_today(self):
        self.showToday()

    def on_cl(self, date):
        def fr_ls(in_date, xv, yv):
            if yv:
                date_v_l = []
                dt = self.full_date_list[-1].daysTo(in_date)

                sn = np.sign(dt)
                for n in range(0, dt + sn, sn):
                    date_v_l.append(self.full_date_list[-1].addDays(n))
            else:
                date_v_l = [in_date]

            if xv:
                if len(date_v_l) <= 1 and date_v_l[0] in self.full_date_list:
                    self.full_date_list.remove(date_v_l)
                else:
                    self.full_date_list.extend(date_v_l)
            else:
                self.full_date_list = date_v_l

        if self.sel == 'Range':
            self.update_date(date)
        else:
            self.print_selected(QTextCharFormat())
            ap1 = [False, False]

            mo = QApplication.instance().keyboardModifiers()

            for ni, ij in enumerate([Qt.ControlModifier, Qt.ShiftModifier]):
                if mo & ij:
                    ap1[ni] = True

            fr_ls(date, *ap1)

        self.print_selected(self.highlight_format)

    def update_date(self, date):
        self.print_selected(QTextCharFormat())
        self.full_date_list.append(date)
        sort_day(self.full_date_list)

        day_l = [self.full_date_list[0], self.full_date_list[-1]]
        self.full_date_list = []

        dt = day_l[0].daysTo(day_l[1])
        for n in range(dt + 1):
            self.full_date_list.append(day_l[0].addDays(n))

        for n, i in enumerate(self.par.date_list.keys()):
            self.par.date_list[i].setDate(self.full_date_list[n])  # widgits froom list
        self.print_selected(self.highlight_format)

    def print_selected(self, form):
        for date in self.full_date_list:
            self.setDateTextFormat(date, form)

    def swap_select_mode(self, mo):
        self.sel = mo
        if mo == 'Range':
            en = True

        else:
            en = False
        for i in self.par.date_list.keys():
            self.par.date_list[i].setEnabled(en)

    def set_d(self):
        for dat in self.full_date_list:
            self.docs[self.active_doc][self.condition].append(dat)


class DocStatus(QTableWidget):  # self.doc_dataframe_items
    def __init__(self, par, ti='Clinic', pos=Qt.RightDockWidgetArea):
        super().__init__()
        self.ti = ti
        self.sort_ascend = True
        self.sort_col = 'Name'
        self.par = par
        self.pos = pos
        #
        self.horizontalHeader().sectionClicked.connect(self.sort_by)
        self.cellClicked.connect(self.tab_s)
        self.cellDoubleClicked.connect(self.set_popup)
        self.dia = None
        self._init_dock()
        self.reset_table()

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

    def reset_table(self):  # todo add filters,
        self.clear()

        r, c = self.par.doc_data.shape

        self.setRowCount(r)
        self.setColumnCount(c)
        self.setHorizontalHeaderLabels(list(self.par.doc_data.columns))
        for n in range(r):
            for m in range(c):
                self.setItem(n, m, QTableWidgetItem(str(self.par.doc_data.iloc[n, m])))

    def tab_s(self, row_n, col_n):
        if row_n == 0:
            self.sort_by(col_n)
        r_n = self.item(row_n, 0).text()
        self.par.typ_c['doc'].setCurrentText(r_n)

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


class docPopup(QDialog):
    def __init__(self, par, res=None):
        super().__init__()
        self.res = res
        self.par = par
        self.doc_op = ['Baby', 'Sur', 'Anestetics', 'locum']  # todo caps
        self.doc_data = {}
        self.setModal(False)
        self._init_layout()

        # self.show()

    def _init_layout(self):
        print('show wigit')
        self.dia_lay = QVBoxLayout()
        self.horizontalLayout = QHBoxLayout()
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout = QVBoxLayout()

        self.name_lay = QLabel('Name')
        self.name_edit = QLineEdit()
        if self.res:
            self.name_edit.setText(self.res)

        # self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addWidget(self.name_lay)
        self.verticalLayout_2.addWidget(self.name_edit)
        # self.verticalLayout_2.addItem(self.verticalSpacer)

        self.doc_op_check = {}
        for op in self.doc_op:
            op_box = QCheckBox(op)
            self.doc_op_check[op] = op_box
            self.verticalLayout.addWidget(op_box)
            # j.clicked.connect(self)

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.accepted.connect(self.acc)
        self.buttonBox.rejected.connect(self.rej)

        self.dia_lay.addWidget(self.buttonBox)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.dia_lay.addLayout(self.horizontalLayout)
        self.setLayout(self.dia_lay)

    def acc(self):  # todo par doc data
        print('accet')
        if self.res:
            del self.doc_data[self.res]

        kk = []
        for i, k in self.doc_op_check.items():
            if k:
                kk.append(i)
        self.doc_data[self.name_edit.text()] = kk
        print('doc d', self.doc_data)
        # todo save
        self.accept()

    def rej(self):
        print('reject')
        self.reject()


class CalendarDayDelegate(QItemDelegate):
    def __init__(self, parent=None, projects=None, par=None):
        super(CalendarDayDelegate, self).__init__(parent=parent)

        self.projects = projects
        self.par = par
        self.last_month = True

        self.call_font = QFont()
        self.call_font.setPixelSize(11)
        self.call_font.setBold(True)

        self.wi_font = QFont()
        self.wi_font.setPixelSize(9)  # todo set color
        self.wi_font.setItalic(True)

    def paint(self, painter, option, index):

        painter._date_flag = index.row() > 0
        super(CalendarDayDelegate, self).paint(painter, option, index)

        if painter._date_flag:

            date_num_full = index.data()  # todo is index correct
            index_loc = (index.row(), index.column())
            year = self.par.yearShown()
            month = self.par.monthShown()
            if date_num_full > 7 and index_loc[0] == 1:
                if month == 1:
                    year -= 1
                    month = 12
                else:
                    month -= 1
            elif date_num_full < 15 and index_loc[0] > 4:
                if month == 12:
                    year += 1
                    month = 1
                else:
                    month += 1

            date = QDate(year, month, date_num_full)

            if date in list(self.par.par.schedul['Date']):
                doc, doc_wi = self.par.par.doc_on_day(date)

                rect = option.rect  # todo caps
                painter.save()
                painter.setPen(self.par.par.active_col)
                painter.setFont(self.call_font)
                painter.drawText(rect, Qt.AlignCenter | Qt.AlignVCenter, doc)

                painter.setFont(self.wi_font)
                painter.drawText(rect, Qt.AlignRight | Qt.AlignBottom, doc_wi)

                painter.restore()

    def drawDisplay(self, painter, option, rect, text):
        if painter._date_flag:
            option.displayAlignment = Qt.AlignTop | Qt.AlignLeft
        super(CalendarDayDelegate, self).drawDisplay(painter, option, rect, text)


class ColorButton(QPushButton):
    def __init__(self, col='', par=None):  # todo empty space
        super().__init__(col)

        self.par = par
        self.clicked.connect(self.par.color)

    def paintEvent(self, event):
        super().paintEvent(event)
        r_w = self.width() // 3
        r_h = self.height() // 2

        rect = QRect(0, 0, r_w, r_h)
        rect.moveTo(self.rect().bottomRight() - rect.bottomRight())

        painter = QPainter(self)
        painter.setBrush(self.par.active_col)
        painter.drawRect(rect)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
