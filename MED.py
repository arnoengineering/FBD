from PyQt5.QtGui import QFont, QTextCharFormat, QPalette, QPainter, QColor, QIcon  # QPainter, QPen,QBrush,
from PyQt5.QtCore import Qt, QDate, QSettings, QRect  # QTimer, QSize,
# from logging import exception
from data_view import DataFrameViewer
from PyQt5.QtWidgets import *

import numpy as np
import pandas as pd
import sys

from functools import partial
from medgoogle import SchedualOptomizer
from piv_edit import pivotDialog
from saload import saveLoad

from cal_exp import calendarEdit


# todo mail
# todo exe
# todo y
# todo typehint
# todo sdave settigs
# atribute
# bold italics, calendar--pluss, better piviot
# doc user
# # mail send
# call off conditional
# groupby months


def sort_day(ls):
    ls.sort(key=lambda x: x.toString(Qt.TextDate))


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.first_show = True
        self.setWindowTitle('Call Schedule Optimizer')
        self.setWindowIcon(QIcon('icons/calendar-blue.png'))

        # self.settings = QSettings('Claassens Software', 'Calling LLB_2022')

    def showEvent(self, event):
        if self.first_show:
            self.first_show = False
            # self._start_up_promt()

            self._set_list()
            self._set_empty()
            self.set_date_format()

            self._setup_load()

            self._set_dataframes()

            # self.test_doc()
            self._creat_toolbar()
            self._create_tools()
            self._set_center()
            self._set_clinic()

            self._update_set()
            super().showEvent(event)

    def _set_list(self):
        # self.doc_data = {}
        self.save_l = saveLoad(self, False)
        self.cmd_ls = {'Mode': ['Single_calendar-select', 'Range_calendar-select-days-span'],
                       'Start Week Format': ['Sun', 'Mon'],
                       'Setting Mode': ['Call', 'Walkin', 'Away', 'Off'],
                       'Want Shift': ['Yes', 'No'],
                       'Pref': ['1', '2', '3', '4', '5'],
                       'Date Format': [],
                       'Weekday Format': ['let', '3let', 'Full'],
                       'Editing': ['Active Schedule_calendar-task', 'Preferences_calendar_pencil']}

        self.wn = 'Show/Hide Weeknumbers_eye-half'
        self.button_list = ['solve_calculator--arrow', self.wn,
                            'Today_calendar-day', 'Save_disk-black',
                            'Load_document-excel-table',
                            'Add_calendar--plus', 'Cal Exp']  # todo add icon

        self.date_n = ['StartDate', 'EndDate']  # calselect days

    def _set_empty(self):
        self.shifts = ['Call', 'Walkin', 'Off', 'Away']
        self.set_mode = None
        self.active_col = Qt.black
        # self.active_doc = self.doc_data[0]['Name']
        self.date_list = {}
        self.av = {}
        self.list_v = {}
        self.action_list = {}
        self.combo = {}
        self.active_shifts = []
        self.default_file = 'docInfoN.xlsx'

    def _set_dataframes(self):
        self.cmd_ls['Active Doc'] = list(self.doc_data['Doc'])

    def load_doc(self):
        # assume overrite for now
        # at end do save default or change
        # load popup
        # todo add compair
        # todo chainge default userload
        # edit schedule vs prefewrnces
        # edit date list

        pass

    def _setup_load(self):
        def l2(x):
            # print('x =', type(x))
            if isinstance(x, pd.DatetimeTZDtype):
                return QDate(x.year, x.month, x.day)
            elif isinstance(x, int):
                return QDate(1900, 1, 1).addDays(x)
            else:
                return QDate.fromString(x, self.day_f)

        if self.default_file:
            self.save_l.on_load_fin(self.default_file, 1)
            print('iiiio')
        self.save_l.on_load_fin('docDays.xlsx', 0)
        self.doc_preferences['Days'] = self.doc_preferences['Days'].apply(l2)

        try:
            self.save_l.on_load_fin('DocSchedule.xlsx', 2)  # todo try
            self.current_schedule['Days'] = self.current_schedule['Days'].apply(l2)
            print('fill na')
            print(self.current_schedule.head())
            self.current_schedule.fillna("", inplace=True)  # todo days
            print('fill')
            print(self.current_schedule.head())
        except ValueError:
            print('error loading doc')

    def _creat_toolbar(self):
        self.font_sizes = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
        # self.img_loc = self.file_loc + '/img/'
        self.tool_bar = QToolBar('Main toolbar')
        self.cal_tool_bar = QToolBar('Calendar')

        self.table_tool = QToolBar('Tables')
        self.col = QColorDialog()

        self.cap_op = ['As Entered', 'UPPERCASE', 'lowercase', 'Capitalize', 'SurName']

        self.font_op = []
        self.but_edit = {}
        self.font_ty_win = {}

        self.save_op = SuperButton('File Options', self, vals=self.button_list)
        va = [f'{i}_edit-{j}' for i, j in [('B', 'bold'), ('I', 'italic'), ('U', 'underline')]]
        self.font_head = SuperButton('Style Options', self, vals=va)

        self.tool_bar.addWidget(self.save_op)
        self.tool_bar.addWidget(self.font_head)
        self.font_wig = {'Font': QFontComboBox(),
                         'Size': SuperCombo('Size', self, vals=[str(x) for x in self.font_sizes], run=False),
                         'Capital': SuperCombo('Capital', self, vals=self.cap_op, run=False)}
        # for it in tb_op:
        #     j = QPushButton(it)
        #     # j.setIcon(self.img_loc+it)
        #
        #     self.but_edit[it] = j
        #     self.tool_bar.addWidget(j)

        self.but_edit['color'] = ColorButton('Color', self)
        self.but_edit['color_fill'] = ColorButton('Color Fill', self, 'Fill')
        self.tool_bar.addWidget(self.but_edit['color'])
        self.tool_bar.addWidget(self.but_edit['color_fill'])

        self.font_wig['Capital'].currentIndexChanged.connect(lambda x: self.set_active_font(x, 'Capital'))
        self.font_wig['Size'].currentTextChanged.connect(lambda x: self.set_active_font(x, 'Size'))
        self.font_wig['Font'].currentFontChanged.connect(self.set_active_font)

        for k, i in self.font_wig.items():
            if k == 'Font':
                self.tool_bar.addWidget(i)
            else:
                self.tool_bar.addWidget(i.wig)

        # for selectic cal or walkin to edit, disable if not on cal, add conditional to tables
        self.font_edit = SuperCombo('FontEdit', self, vals=self.shifts)
        self.tool_bar.addWidget(self.font_edit.wig)

        self.addToolBar(self.tool_bar)

    def _set_center(self):
        self.cal_wig = Calendar(self)
        self.solver = SchedualOptomizer()
        self.setCentralWidget(self.cal_wig)
        self.active_wig = 'Cal'

    def _set_clinic(self):

        self.doc_stat = DocStatus(self, self.doc_data, 'Doc Info')  # for docter clinic
        self.day_stat = DocStatus(self, self.doc_preferences, ti='Prefernces')
        self.day_stat2 = DocStatus(self, self.current_schedule, ti='Current Dayly Stats', pos=Qt.LeftDockWidgetArea)
        # self.day_stat2.piv_kwargs = {'index': ['Days'], 'columns': ['Doc'], 'values':'Shift','aggfunc': lambda x:','.join(x),
        # 'fill_value': 0}
        self.ti_info = {'Doc Info': self.doc_stat, 'Prefernces': self.day_stat, 'Current Dayly Stats': self.day_stat2}
        # self.clinic_wig = DocClinic(self, ti='Live Clinic', pos=Qt.LeftDockWidgetArea)

    # noinspection PyArgumentList
    def _create_tools(self):
        self.tool_bar2 = QToolBar()

        self.addToolBar(self.tool_bar2)
        self.addToolBar(self.cal_tool_bar)

        # ___________comboboxes_______

        for wig_name, opt in self.cmd_ls.items():
            k = SuperCombo(wig_name, self, vals=opt)
            self.combo[wig_name] = k
            self.tool_bar2.addWidget(k.wig)

        for wig_name in self.date_n:
            lab = QLabel(wig_name)
            print('i', wig_name)
            da = QDateEdit()
            da.setDate(QDate.currentDate())
            da.setCalendarPopup(True)
            da.dateChanged.connect(lambda x: self.cal_wig.update_date(x))
            self.date_list[wig_name] = da
            tool_layout = QVBoxLayout()
            wig = QWidget()
            wig.setLayout(tool_layout)
            tool_layout.addWidget(da)
            tool_layout.addWidget(lab)
            self.cal_tool_bar.addWidget(wig)

    def run_cmd(self, i, ex=None):
        print('cmd', i)
        if i == 'doc away':
            print('date, doc away')
            # set doc away
        elif i == 'Mode':
            self.cal_wig.swap_select_mode(self.combo[i].currentText())
            self.day_stat2.reset_table()
        elif i == 'solve':
            self._solve_doc()
        elif i == 'Load':
            self.load_doc()
            # self.solver.run_scedual()

        # elif i == 'Setting Mode':
        #     self.set_mode = ex
        elif i == 'Date Format':
            for r in self.date_list.values():
                r.setDisplayFormat(ex)
                # self.doc_stat.reset_table()
                # self.day_stat.reset_table()
        elif i == 'Save':

            self._save_user_settings()
        elif i == 'Add':
            self.add_doc()

        elif i == 'Settings':
            self.run_set()
        elif i == 'Active':
            # self.active_doc = ex
            self.cen.update_active(ex)
        elif i == self.wn:
            # QCalendarWidget.noVer
            self.cal_wig.set_wig_2()
        elif i == 'Weekday Start':
            self.cal_wig.week_start(ex)
        elif i == "Today":
            self.cal_wig.set_today()
        elif i == "Apply":
            self._run_doc_solve()

        elif i == 'Cal Exp':
            self.c_exp()

    def c_exp(self):
        cal = calendarEdit(self,self.current_schedule)
        file_ls = cal.doc_save() # todo user email list

    def run_set(self):
        pass

    def add_doc(self):
        doc = self.combo['Active Doc'].currentText()
        pre = self.combo['Pref'].currentText()
        want = self.combo['Want Shift'].currentText()
        shift = self.combo['Setting Mode'].currentText()
        edit_type = self.combo['Editing'].currentText()
        df_p = {'Days': [], 'Doc': [doc], 'Shift': [shift]}
        if want == 'No':
            pre *= -1
        if edit_type == 'Preferences':
            data = self.doc_prefernces
            df_p['Pref'] = [pre]
            tx = 'Preferences'
        else:
            data = self.current_schedule
            tx = 'sched'

        for ii in self.cal_wig.full_date_list:
            print(f'{tx}: val: {ii},doc:{doc}, shift:{shift}')
            df_p['Days'] = [ii]
            if edit_type == 'Active Schedule':
                data.loc[(data['Shift'] == shift) & (data['Days'] == ii), 'Doc'] = doc
            elif ii in data.loc[data['Doc'] == doc, ['Days']]:
                print('overwrite')
                data.loc[(data['Doc'] == doc) & (data['Days'] == ii)] = pd.DataFrame(df_p)
            else:
                data = pd.concat((data, pd.DataFrame(df_p)))
    def _dia_ax(self):
        self.val = int(self.wi.text())
        if not self.dia.wig_o.isChecked():
            self.val *= -1
        self.dia.accept()

    def _solve_doc(self):
        # self.schedul
        self.solver.set_constraints(self.doc_preferences, QDate.currentDate())
        self.solver.solve_shift_scheduling()
        print('yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
        self.current_schedule = self.solver.sch_data  # todo overrite ask
        self.save_l.sa = True
        self.save_l.on_save_fin('DocSchedule.xlsx', 2)  # todo if user asks
        # self.save_l.on_save_fin('docDays.xlsx', 0)

    def doc_on_day(self, date, cfd=None):
        def xvx() -> list:
            doc_x = []
            for x in cfd:
                dy = list(scd[scd['Shift'] == x]['Doc'])
                if len(dy) == 0:
                    dy = [""]
                doc_x.append(dy)
            return doc_x

        if cfd is None:
            cfd = ['Call', 'Walkin']
        if isinstance(date, list):
            scd = self.current_schedule.loc[self.current_schedule['Days'].isin(date)]
            dyx = xvx()
        else:
            scd = self.current_schedule.loc[self.current_schedule['Days'] == date]
            dyx = xvx()
            for n in range(len(dyx)):
                dyx[n] = dyx[n][0]
        return dyx

    def set_active_wig(self, wig):
        if self.active_wig in self.ti_info:
            self.ti_info[self.active_wig].close_dia()
        self.active_wig = wig
        print(f'Window ({wig}) is now active')
        self.font_edit.setEnabled(wig == 'Cal')

    def set_active_font(self, font=None, ty='Font'):

        print('running activefont')

        if self.font_edit.isEnabled():
            tty = self.font_edit.currentText()

        else:
            tty = self.active_wig
        if ty == 'Capital':
            if font < 5:  # enum
                self.font_ty[tty][ty] = self.cap_op[font]
        else:
            if ty in ['Color', 'Fill']:
                self.col.setCurrentColor(self.font_ty[tty][ty])
                font = QColorDialog().getColor()
            elif ty == 'Size':
                font = int(font)

            self.font_ty[tty][ty] = font

    def _update_set(self):
        print('loading_all')
        self.setting_keys_combo = {'Date Format': 'dd-MMM-yyyy',  # y-m-d,y-d-m,d-m-y,m-d-y
                                   'Weekday Format': 'let',  # long,sort,,let
                                   'Start Week Format': 'Sun',
                                   'Mode': 'Single',
                                   'Active Doc': 'Dehlen',
                                   'Setting Mode': 'Call',
                                   }

        self.font_ty_default = {'Call': {'Font': QFont("Times"), 'Size': self.font_sizes[3],
                                         'Capital': self.cap_op[3], 'Color': QColor(Qt.blue), 'Fill': QColor(Qt.green)},
                                'Walkin': {'Font': QFont("Times"), 'Size': self.font_sizes[0],
                                           'Capital': self.cap_op[0], 'Color': QColor(Qt.black),
                                           'Fill': QColor(Qt.yellow)},
                                'Doc Stats': {'Font': QFont("Times"), 'Size': self.font_sizes[1],
                                              'Capital': self.cap_op[0], 'Color': QColor(Qt.black)},
                                'Dayly Stats': {'Font': QFont("Times"), 'Size': self.font_sizes[0],
                                                'Capital': self.cap_op[0], 'Color': QColor(Qt.black)},
                                'Live Clinic': {'Font': QFont("Times"), 'Size': self.font_sizes[2],
                                                'Capital': self.cap_op[0], 'Color': QColor(Qt.black)}
                                }

        for shift in self.shifts:  # todo add fill, add alignmen
            if shift not in self.font_ty_default:
                self.font_ty_default[shift] = {'Font': QFont("Times"), 'Size': self.font_sizes[0],
                                               'Capital': self.cap_op[0], 'Color': QColor(Qt.black),
                                               'Fill': QColor(Qt.blue)}
        self.settings.beginGroup('combo')

        for ke, v in self.setting_keys_combo.items():
            val = self.settings.value(ke, v)
            self.combo[ke].setCurrentText(val)
            # ke_new = ke.lower().replace(' ', '_')  #
            print(f'key, val: {ke}, {val}')

        self.settings.endGroup()

        self.font_ty = {}
        self.settings.beginGroup('font')
        for ke, v in self.font_ty_default.items():
            val = {}
            self.settings.beginGroup(ke)
            for vi in v.keys():
                val[vi] = self.settings.value(vi, v[vi])

            self.font_ty[ke] = val
            self.settings.endGroup()
        self.settings.endGroup()
        self.settings.beginGroup('ActiveShift')
        for i in self.shifts:
            j = self.settings.value(i, True)
            if j:
                self.active_shifts.append(i)
        self.settings.endGroup()
        k = self.settings.allKeys()
        print('res')
        for i, j in [(self.restoreGeometry, "Geometry"), (self.restoreState, "windowState")]:
            if j in k:
                i(self.settings.value(j))

    def set_date_format(self):
        conect = ['.', '/', ',', '-', ' ']
        y = 'yyyy'
        j = []
        for co in conect:
            for yf in range(2):
                for day in range(2, 4):
                    di = "d" * day
                    for mon in range(2, 5):
                        mo = "M" * mon
                        f = [di, mo]
                        for i in range(2):
                            if day == 3 and i == 0:
                                st = [f'{di}{co}d{co}{mo}',
                                      f'{di}{co}{mo}{co}d']
                            else:
                                st = [f'{f[i]}{co}{f[(i + 1) % 2]}']
                            if yf == 0:
                                j.extend(f'{y}{co}{si}' for si in st)
                            else:
                                j.extend(f'{si}{co}{y}' for si in st)
        print(j)

        self.cmd_ls['Date Format'] = j

    def _save_user_settings(self):
        self.settings = QSettings('Claassens Software', 'User Saved')
        self.user_settings()

    def user_settings(self, last_ses=True):
        self.settings.setValue("Geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        if last_ses:
            self.settings.beginGroup('combo')

            for ke in self.setting_keys_combo.keys():
                val = self.combo[ke].currentText()
                self.settings.setValue(ke, val)
                print(f'key, val: {ke}, {val}')
            self.settings.endGroup()

            self.settings.beginGroup('font')
            for ke, v in self.font_ty_default.items():
                self.settings.beginGroup(ke)
                for vi in v.keys():
                    self.settings.setValue(vi, v[vi])
                self.settings.endGroup()
            self.settings.endGroup()

            self.settings.beginGroup('ActiveShift')
            for i in self.shifts:
                j = self.settings.setValue(i, i in self.active_shifts)
            self.settings.endGroup()

            setting = QSettings('Claassens Software', 'Calling LLB_2022_open')
            setting.setValue('Load Last Session', self.load_d)
            setting.setValue('Show on Startup', self.on_start)

    def closeEvent(self, event):

        self.user_settings(self.load_d)
        super().closeEvent(event)  # todo unsaved changes, todo overwrite, todo menu, user show

        for i in self.ti_info.values():
            i.close_dia()


class Calendar(QCalendarWidget):
    def __init__(self, par):
        super().__init__()
        self.par = par
        self.st_h = 1

        self.sel = 'Single'

        self.full_date_list = [QDate.currentDate(), QDate.currentDate()]
        self.clicked.connect(lambda checked: self.on_cl(checked))
        self.setGridVisible(True)
        self.set_menu()

        self.set_wig_2()
        self._init_calendar()
        self._init_high()

    def mousePressEvent(self, event):
        print('clicked cal')
        self.par.set_active_wig('Cal')
        super().mousePressEvent(event)

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

        if self.par.combo['Mode'].currentText() == 'Range':
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
        self.par.set_active_wig('Cal')

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
        if mo == 'Range':
            en = True

        else:
            en = False
        for i in self.par.date_list.keys():
            self.par.date_list[i].setEnabled(en)

    def add_text(self, ite):
        xi = self.menu_item[ite].isChecked()
        if xi:
            self.par.active_shifts.append(ite)
        else:
            self.par.active_shifts.remove(ite)

    def _add_menu(self, pos):
        self.menu_item = {}
        print('wig')
        self.context_menu = QMenu("Show Events", self)
        print('qmen')
        for ite in self.par.shifts:
            print('ite', ite)
            action = QAction(ite)
            action.setCheckable(True)
            if ite in self.par.active_shifts:
                action.setChecked(True)
            action.triggered.connect(partial(self.add_text, ite))
            self.menu_item[ite] = action
            self.context_menu.addAction(action)
            print('loaded action:', action.text())

        self.context_menu.exec(self.mapToGlobal(pos))

    def set_menu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # def setContextMenuPolicy(self):
        self.customContextMenuRequested.connect(self._add_menu)


# class DStat
class DocStatus(DataFrameViewer):  # self.doc_dataframe_items
    def __init__(self, par, df, ti='Clinic', pos=Qt.RightDockWidgetArea):
        super().__init__(df)
        self.df_init = df.copy()
        self.ti = ti
        self.sort_ascend = True
        self.sort_col = 'Name'
        self.par = par
        self.pos = pos
        self.d_r = 30
        self.dialog = pivotDialog(self.df_init, self)
        self.dia_act = False
        #
        # self.horizontalHeader().sectionClicked.connect(self.sort_by)
        # self.cellClicked.connect(self.tab_s)
        # self.cellDoubleClicked.connect(self.set_popup)
        self.dia = None
        self._init_dock()
        # self.reset_table()

    def mousePressEvent(self, event):
        if self.par.active_wig != self.ti:
            self.dialog.show()
            self.dia_act = True
            self.par.set_active_wig(self.ti)

    def close_dia(self):
        if self.dia_act:
            # todo check position, last columns, todo load doc
            self.dialog.close()

    def _init_dock(self):
        self.dock = QDockWidget(self.ti)
        self.dock.setWidget(self)
        self.par.addDockWidget(self.pos, self.dock)

    def reset_table(self):
        print('update df')
        self.setData()
        print(self.df.head())
        print('hello')
        print(self.dataView.print())
        # self.dataView.model().beginResetModel()
        # self.update()
        self.dataView.model().layoutChanged.emit()

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


class DocClinic(DocStatus):  # self.doc_dataframe_items
    def __init__(self, par, df, **kwargs):
        super().__init__(par, df, **kwargs)

    # def reset_table(self):
    #     dd = self.par.doc_data
    #     r, c = dd.shape
    #     self.reset_table_main(dd, r, c)

    # def reset_table_main(self, dd, r, c):
    #     self.setHorizontalHeaderLabels(list(dd.columns))
    #     self.setRowCount(c)
    #     self.setColumnCount(r)
    #     for n in range(r):
    #         for m in range(c):
    #             self.setItem(m,n, QTableWidgetItem(str(dd.iloc[n, m])))


class DayStatus(DocStatus):
    def __init__(self, par, df, **kwargs):
        self.day_range = 30
        self.piv_kwargs = {'index': ['Doc'], 'columns': ['Shift'], 'values': 'Days', 'aggfunc': 'count',
                           'fill_value': 0}
        super().__init__(par, df, **kwargs)

    def reset_table(self):
        # self.clear()
        # dd = self.par.current_schedule
        # self.df = pd.pivot_table(self.df_init, **self.piv_kwargs)
        # self.dataView.model()._data = self.df
        pass


class docPopup(QDialog):
    def __init__(self, par, res=None):
        super().__init__()
        self.res = res
        self.par = par
        self.doc_op = ['Baby', 'Sur', 'Anestetics', 'Locum']
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

        self.verticalLayout_2.addWidget(self.name_lay)
        self.verticalLayout_2.addWidget(self.name_edit)
        # self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # self.verticalLayout_2.addItem(self.verticalSpacer)

        self.doc_op_check = {}
        for op in self.doc_op:
            op_box = QCheckBox(op)
            self.doc_op_check[op] = op_box
            self.verticalLayout.addWidget(op_box)

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

    def acc(self):
        print('accet')
        if self.res:
            del self.doc_data[self.res]

        kk = []
        for i, k in self.doc_op_check.items():
            if k:
                kk.append(i)
        self.doc_data[self.name_edit.text()] = kk
        print('doc d', self.doc_data)

        self.accept()

    def rej(self):
        print('reject')
        self.reject()


class CalendarDayDelegate(QItemDelegate):
    def __init__(self, parent=None, projects=None, par=None):
        super(CalendarDayDelegate, self).__init__(parent=parent)

        self.projects = projects
        # self.items_ls = {'Call': '', }
        self.par = par
        self.labs = []
        self.space = 0.7
        self.space_ver = 0.15
        self.op = [Qt.AlignCenter | Qt.AlignVCenter,
                   Qt.AlignRight | Qt.AlignBottom,
                   Qt.AlignLeft | Qt.AlignBottom,
                   Qt.AlignRight | Qt.AlignTop]
        self.last_month = True  # todo reset and if overlap

    def paint(self, painter: QPainter, option, index):

        painter._date_flag = index.row() > 0
        super(CalendarDayDelegate, self).paint(painter, option, index)

        if painter._date_flag:

            date_num_full = index.data()
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
            print('labs= ', self.labs)
            active_shifts = self.par.par.active_shifts
            painter.save()
            rect = option.rect
            x, y, w, h = rect.getRect()
            for n, i in enumerate(active_shifts):
                doc = self.par.par.doc_on_day(date, [i])[0]

                # back_color = Qt.red
                siz = int(w * self.space)
                size_v = int(w * self.space_ver)
                if i == 'Call':
                    size_v += 10
                x0 = x + w - siz - 2
                if doc != "":
                    rect2 = QRect(x0, y + 2, siz, size_v)
                    d = self.par.par.font_ty

                    font = d[i]['Font']
                    font.setPixelSize(d[i]['Size'])
                    # QFont()
                    font.setCapitalization(self.par.par.cap_op.index(d[i]['Capital']))
                    painter.setFont(font)
                    align = self.op[n]
                    # te = doc[n]
                    doc_col = d[i]['Color']
                    back_color = d[i]['Fill']
                    y += size_v + 2

                    painter.setBrush(back_color)
                    painter.drawRect(rect2)
                    painter.setPen(doc_col)
                    painter.drawText(rect2, align, doc)  # , option=)

            painter.restore()

    def drawDisplay(self, painter, option, rect, text):
        if painter._date_flag:
            option.displayAlignment = Qt.AlignTop | Qt.AlignLeft
        super(CalendarDayDelegate, self).drawDisplay(painter, option, rect, text)


class ColorButton(QPushButton):
    def __init__(self, col='', par=None, ty='Color'):
        if ty == 'color':
            tx = 'icons/edit-color.png'
        else:
            tx = 'icons/paint-can-color.png'
        super().__init__(QIcon(tx), col)
        self.ty = ty
        self.par = par
        self.clicked.connect(lambda _: self.par.set_active_font(ty=self.ty))

    def paintEvent(self, event):
        super().paintEvent(event)
        w, h = self.width(), self.height()
        r_w = w // 3
        r_h = h // 4

        rect = QRect((w - r_w) // 2, h - r_h - 2, r_w, r_h)
        # rect.moveTo(self.rect().bottomRight() - rect.bottomRight())

        painter = QPainter(self)
        painter.setBrush(self.par.active_col)
        painter.drawRect(rect)


class dataPopup(QDialog):
    # noinspection PyArgumentList
    def __init__(self, par: Window, res=None):
        super().__init__()
        self.res = res
        self.par = par
        self.table_op = [self.par.day_stat, self.par.day_stat2, self.par.doc_stat]
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

        # noinspection PyArgumentList
        self.verticalLayout_2.addWidget(self.name_lay)
        # noinspection PyArgumentList
        self.verticalLayout_2.addWidget(self.name_edit)
        # self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # self.verticalLayout_2.addItem(self.verticalSpacer)

        self.doc_op_check = {}
        for op in self.doc_op:
            op_box = QCheckBox(op)
            self.doc_op_check[op] = op_box
            # noinspection PyArgumentList
            self.verticalLayout.addWidget(op_box)

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.accepted.connect(self.acc)
        self.buttonBox.rejected.connect(self.rej)

        # noinspection PyArgumentList
        self.dia_lay.addWidget(self.buttonBox)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.dia_lay.addLayout(self.horizontalLayout)
        self.setLayout(self.dia_lay)

    def acc(self):
        print('accet')
        if self.res:
            del self.doc_data[self.res]

        kk = []
        for i, k in self.doc_op_check.items():
            if k:
                kk.append(i)
        self.doc_data[self.name_edit.text()] = kk
        print('doc d', self.doc_data)

        self.accept()

    def rej(self):
        print('reject')
        self.reject()


class SuperCombo(QComboBox):
    def __init__(self, name, par, orient_v=True, vals=None, show_lab=True, run=True):
        super().__init__()

        self.par = par
        self.orient_v = orient_v
        self.show_lab = show_lab
        self.name = name
        self.item_ls = []
        self.wig = QWidget()

        self.lab = QLabel(self.name)

        self._layout_set()

        if vals is not None:
            for v in vals:
                if '_' in v:
                    v, ic = v.split('_', 1)
                    self.addItem(QIcon(f'icons/{ic}.png'), v)
                    self.item_ls.append(v)
                else:
                    self.addItem(v)
                    self.item_ls.append(v)

        if run:
            self.currentTextChanged.connect(lambda x: self.par.run_cmd(self.name, x))  # todo if docs or if no text

    # noinspection PyArgumentList
    def _layout_set(self):
        if self.orient_v:
            self.layout = QVBoxLayout()
        else:
            self.layout = QHBoxLayout()
        self.layout.addWidget(self)
        self.layout.addWidget(self.lab)
        self.wig.setLayout(self.layout)

    def reset_show(self, show_lab=False, flip=False):
        if flip:
            self.orient_v = not self.orient_v
            self._layout_set()
        if show_lab:
            self.show_lab = not self.show_lab
            if self.show_lab:
                self.layout.addWidget(self.lab)
            else:
                self.layout.removeWidget(self.lab)


# color pallette-color
# user medical, user doc gen
# folder-open-document-text
# disk
# document-excel table
class SuperButton(QWidget):
    def __init__(self, name, par, orient_v=True, vals=None, show_lab=True):
        super().__init__()

        self.par = par
        self.orient_v = orient_v
        self.show_lab = show_lab
        self.name = name
        self.but = {}
        self.lab = QLabel(self.name)

        if vals:
            for i in vals:
                if '_' in i:
                    i, ic = i.split('_', 1)
                    j = QPushButton(QIcon(f'icons/{ic}.png'), "")
                else:
                    j = QPushButton(i)
                j.clicked.connect(partial(self.par.run_cmd, i))
                self.but[i] = j

        self._layout_set()

    def _layout_set(self):
        self.layout = QGridLayout()
        n = 0
        if self.orient_v:

            for i in self.but.keys():
                self.layout.addWidget(self.but[i], 0, n)
                n += 1
            self.layout.addWidget(self.lab, 1, 0, 1, n)
        else:
            for i in self.but.keys():
                self.layout.addWidget(self.but[i], n, 0)
                n += 1
            self.layout.addWidget(self.lab, 0, 1, n, 1)
        self.setLayout(self.layout)

    def reset_show(self, show_lab=False, flip=False):
        if flip:
            self.orient_v = not self.orient_v
            self._layout_set()
        if show_lab:
            self.show_lab = not self.show_lab
            if not self.show_lab:
                self.layout.removeWidget(self.lab)


class StartupDialog(QDialog):
    # noinspection PyArgumentList
    def __init__(self):
        super().__init__()
        self.setModal(True)
        self.setWindowTitle("Settings Load")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.head = QLabel('Calling Open')
        self.head.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.head)

        self.checkBox = QCheckBox("show on startup?")
        self.checkBox.setChecked(True)

        self.layout.addWidget(self.checkBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.layout.addItem(self.verticalSpacer)

        self.ques = QLabel("Load Last session values")
        self.layout.addWidget(self.ques)

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.No | QDialogButtonBox.Yes)

        self.layout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.finished.connect(self.closes)

    def loadr(self, fun):
        def wr():
            self.par.reshow = self.checkBox.isChecked()
            return fun

        return wr

    def closes(self, x):
        load_win(x == 1, self.checkBox.isChecked())


def _start_up_promt():
    setting = QSettings('Claassens Software', 'Calling LLB_2022_open')
    print('loaded startup')
    show_startup = setting.value('Show on Startup', True, type=bool)  # .toBool()
    if show_startup:
        print('show startup')
        st.show()
        print('loaded')
    else:
        print('show startup not')
        load_d = setting.value('Load Last Session', True, type=bool)  # per user, load last session
        load_win(load_d, False)


def load_win(load_d, again):
    if load_d:
        print('show j')
        j = 'Calling LLB_2022'
    else:
        print('show jnot')
        j = 'User Saved'
    win.settings = QSettings('Claassens Software', j)
    win.on_start = again
    win.load_d = load_d
    win.show()
    st.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    st = StartupDialog()
    _start_up_promt()
    sys.exit(app.exec_())
