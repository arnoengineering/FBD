from PyQt5.QtGui import QFont, QTextCharFormat, QPalette, QPainter, QColor, QIcon, QPen  # QPainter, QPen,QBrush,
from PyQt5.QtCore import Qt, QDate, QSettings, QRect  # , QByteArray  # QTimer, QSize,
# from logging import exception
# color pallette-color
# user medical, user doc gen
# folder-open-document-text
# disk
# document-excel table
from data_view import DataFrameViewer
from PyQt5.QtWidgets import *

import numpy as np
import pandas as pd
import sys

from functools import partial
from medgoogle import SchedualOptomizer
from piv_edit import pivotDialog
from saload import saveLoad
from docWiz import docPopup

from cal_exp import calendarEdit
from super_bc import SuperCombo, SuperButton

# from email_doc import login

'''exe
mail
full settings
load
multiple groupby
add doc new info
add compair
settings:  # todo unsaved changes, todo overwrite, todo menu, user show
cal select output
capital
font
fil
color
size
widits
pivot
info button
tables
settings
widgits close open
# todo user email list
 # todo add doc op# todo to par main, read main# todo do we Have?
  # todo run next# todo style
'''


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

            print(f'\n{string_break}\n|| Init Doc Window ||\n{string_break}\n')

            # init items
            self._set_list()
            self._set_tooltip()
            self._set_empty()

            self.set_date_format()
            self._setup_load()
            self._set_dataframes()

            self._creat_toolbar()
            self._create_tools()
            self._set_center()

            self._set_clinic()
            self._update_set()
            super().showEvent(event)

    def _set_list(self):
        """inits butons"""
        # init SaveLoad Option
        self.save_l = saveLoad(self, False)
        self.wn = 'Show/Hide Weeknumbers'

        # init all combo cmds, name_icon
        self.cmd_ls = {'Mode': ['Single_calendar-select', 'Range_calendar-select-days-span'],
                       'Start Week Format': ['Sun', 'Mon'],
                       'Setting Mode': ['Call', 'Walkin', 'Away', 'Off'],
                       'Want Shift': ['Yes', 'No'],
                       'Pref': ['1', '2', '3', '4', '5'],
                       'Date Format': [],
                       'Weekday Format': ['let', '3let', 'Full'],
                       'Editing': ['Active Schedule_calendar-task', 'Preferences_calendar_pencil']}

        self.button_list = ['solve_calculator--arrow', self.wn + '_eye-half',
                            'Today_calendar-day', 'Save_disk-black',
                            'Apply',
                            'Load_document-excel-table',
                            'Add_calendar--plus', 'Cal Exp_calendar--arrow',
                            'Email_mail-send']

        self.date_n = ['StartDate', 'EndDate']  # calselect days

    def _set_tooltip(self):
        """sets the tooltips for all butons"""

        self.tool_tip = {'solve': 'Uses Linear optimization to solve current schedule using active preferences\n'
                                  'currently working to add compair',
                         self.wn: 'Show/Hide Weeknumbers on calendar',
                         'Today': 'focus on today in calendar',
                         'Save': 'save items to csv, jason, excel',
                         'Load': 'Load items from csv, jason, excel:  WIP',
                         'Add': 'all current dates are added with doc and pref to date',
                         'Apply': 'applies all active edits to current schedule',
                         'Cal Exp': 'export all to .ics format\ncal can be imported to excel',
                         'Email': 'email selected docs with selected cals: WIP',
                         'Date Start': 'if mode = range, from date start to end',
                         'Mode': 'Single: add multiple dates based on selections\n'
                                 'Range: add all dates in selected range',
                         'Start Week Format': 'start week on sunday or monday',
                         'Setting Mode': 'current shift to edit',
                         'Want Shift': 'if current pref is posive or negative',
                         'Pref': 'how much is opinion worth (1-4): or 5 = garentied',
                         'Date Format': 'how dates showup in all locations',
                         'Weekday Format': 'how days of week are formated',
                         'Editing': 'editing the curret scedule with direct effects or editing the prefernces to solve',
                         'bold': 'current widget text: Bold',
                         'underline': 'current widget text: Underline',
                         'italic': 'current widget text: Italic',
                         'Left': 'align text left',
                         'Center': 'align text center',
                         'Right': 'align text right',
                         'Top': 'align text vertically top',
                         'CenterV': 'align text vertically center',
                         'Bottom': 'align text vertically bottom'
                         }

    def _set_menu_bar(self):
        self.men = QMenuBar()
        men_op = {'File': ['Save', 'load', 'Cal Exp', 'Solve'],
                  'Edit': ['Editing', 'Setting mode_s', 'Vert', 'Horizon'],
                  'View': [self.wn, 'Shifts', 'Windows', 'Today']}
        # self.men.addMenu()
        pass

    def _set_empty(self):
        """sets empty lists"""

        self.shifts = ['Call', 'Walkin', 'Off', 'Away']
        self.schedules = ['Current', 'Edited']

        self.set_mode = None
        self.active_col = {'Color': Qt.black, 'Fill': Qt.black}
        self.font_style = ['Bold', 'Italic', 'Underline']
        # self.active_doc = self.doc_data[0]['Name']
        self.date_list = {}
        self.av = {}
        # self.schedules = []
        self.active_sch = ['Current']
        self.avalible_sch = ['Current']
        self.list_v = {}
        self.action_list = {}
        self.combo = {}
        self.sch_ls = {}
        self.active_shifts = []
        self.align_op = {'H': {'Left': Qt.AlignLeft, 'Center': Qt.AlignCenter, 'Right': Qt.AlignRight},
                         'V': {'Top': Qt.AlignTop, 'CenterV': Qt.AlignVCenter, 'Bottom': Qt.AlignBottom}}

        self.default_files = {'Doc Info': 'docInfoN.xlsx',
                              'Preferences': 'docDays.xlsx',
                              'Current Dayly Stats': 'DocSchedule.xlsx'}

    def _set_dataframes(self):
        self.cmd_ls['Active Doc'] = list(self.doc_data['Doc'])

    def load_doc(self):
        """loads data from file currently not working"""
        # assume overrite for now
        # at end do save default or change
        # load popup
        # edit schedule vs prefewrnces
        # edit date list
        self.avalible_sch.append('Edited')

        pass

    def _setup_load(self):
        """loads default scedual last pref"""

        def qdate_from_date(x):
            if isinstance(x, pd.DatetimeTZDtype):
                return QDate(x.year, x.month, x.day)
            elif isinstance(x, int):
                return QDate(1900, 1, 1).addDays(x)
            else:
                return QDate.fromString(x, self.day_f)

        # loading info for each doc
        self.save_l.on_load_fin(self.default_files['Doc Info'], 1)
        print('Loaded Doc info')

        self.save_l.on_load_fin(self.default_files['Preferences'], 0)
        self.doc_preferences['Days'] = self.doc_preferences['Days'].apply(qdate_from_date)

        try:
            self.save_l.on_load_fin(self.default_files['Current Dayly Stats'], 2)
            self.current_schedule['Days'] = self.current_schedule['Days'].apply(qdate_from_date)

            self.current_schedule.fillna("", inplace=True)
            print('current schedule')
            print(self.current_schedule.head())
            self.sch_ls['Current'] = self.current_schedule
        except ValueError:
            print('error loading doc')

    def _creat_toolbar(self):
        self.font_sizes = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
        self.tool_bar = QToolBar('Main toolbar')
        self.cal_tool_bar = QToolBar('Calendar')

        self.table_tool = QToolBar('Tables')
        self.col = QColorDialog()

        self.cap_op = ['As Entered', 'UPPERCASE', 'lowercase', 'Capitalize', 'SurName']

        self.font_op = []
        self.but_edit = {}
        self.font_ty_win = {}

        self.save_op = SuperButton('File Options', self, vals=self.button_list)
        va = [f'{i}_edit-{i.lower()}' for i in self.font_style]
        self.font_head = SuperButton('Style Options', self, vals=va)

        align_h = ['Left_edit-alignment', 'Center_edit-alignment-center', 'Right_edit-alignment-right']
        align_v = ['Top_edit-vertical-alignment-top', 'CenterV_edit-vertical-alignment-middle',
                   'Bottom_edit-vertical-alignment']

        self.font_align = {'H': SuperButton('Horizontal Align', self, vals=align_h),
                           'V': SuperButton('Vertical Align', self, vals=align_v)}

        self.tool_bar.addWidget(self.save_op)
        self.tool_bar.addWidget(self.font_head)

        self.font_wig = {'Font': QFontComboBox(),
                         'Size': SuperCombo('Size', self, vals=[str(x) for x in self.font_sizes], run=False),
                         'Capital': SuperCombo('Capital', self, vals=self.cap_op, run=False)}

        self.but_edit['color'] = ColorButton('Color', self)
        self.but_edit['color_fill'] = ColorButton('Color Fill', self, 'Fill')
        self.tool_bar.addWidget(self.but_edit['color'])
        self.tool_bar.addWidget(self.but_edit['color_fill'])

        # noinspection PyUnresolvedReferences
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
        self.day_stat = DocStatus(self, self.doc_preferences, ti='Preferences')
        self.day_stat2 = DocStatus(self, self.current_schedule, ti='Current Dayly Stats', pos=Qt.LeftDockWidgetArea)

        self.ti_info = {'Doc Info': self.doc_stat, 'Preferences': self.day_stat, 'Current Dayly Stats': self.day_stat2}

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
        print(f'Running Command: {i}  ||\n')
        if i == 'Mode':
            self.cal_wig.swap_select_mode(self.combo[i].currentText())
            self.day_stat2.reset_table()
        elif i in self.font_style:
            self.set_active_font(ty=i)
        elif i in self.font_align['H'].but:
            self.set_align(i, 'H')
        elif i in self.font_align['V'].but:
            self.set_align(i, 'V')
        elif i == 'solve':
            self._solve_doc()
        elif i == 'Load':
            self.load_doc()

        elif i == 'Date Format':
            for r in self.date_list.values():
                r.setDisplayFormat(ex)

        elif i == 'Save':

            self._save_user_settings()
        elif i == 'Add':
            self.add_doctor_pref()

        elif i == 'Settings':
            self.run_set()
        elif i == 'Active':

            self.cen.update_active(ex)
        elif i == self.wn:
            # QCalendarWidget.noVer
            self.cal_wig.set_wig_2()
        elif i == 'Weekday Start':
            self.cal_wig.week_start(ex)
        elif i == "Today":
            self.cal_wig.set_today()
        elif i == "Apply":
            self._apply_edits()

        elif i == 'Cal Exp':
            self._c_exp()
        elif i == 'Email':
            self._run_email()

    def set_align(self, i, di):
        if self.font_edit.isEnabled():
            tty = self.font_edit.currentText()

        else:
            tty = self.active_wig
        self.font_ty[tty]['Align' + di] = self.align_op[di][i]

    def _c_exp(self):
        cal = calendarEdit(self, self.sch_ls)
        self.file_ls = cal.doc_save()

    def _run_email(self):
        print(f'\n{string_break}\n Running email')
        # QIcon('icons/mail-open-table.png')
        QMessageBox.information(self, 'Email Info',
                                'Sending Email is still a WIP:\n'
                                'Please send documents manually')

    def add_doctor_pref(self):
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
            if 'Edited' not in self.sch_ls:
                self.sch_ls['Edited'] = self.current_schedule.copy()
            data = self.sch_ls['Edited']
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

    def _apply_edits(self):
        # assuming on main schedule for now

        accept = QMessageBox.warning(self, 'SaveInfo',
                                     "The document has been modified.\nDo you want to save your changes?",
                                     QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)

        if accept != QMessageBox.Cancel:
            print('Apling edits')
            self.avalible_sch.remove('Edited')
            self.active_sch.remove('Edited')

            if accept == QMessageBox.Save:
                self.sch_ls['Current'] = self.sch_ls['Edited']
                del self.sch_ls['Edited']
                print('edit replaced')

    def _dia_ax(self):
        self.val = int(self.wi.text())
        if not self.dia.wig_o.isChecked():
            self.val *= -1
        self.dia.accept()

    def _solve_doc(self):
        # self.schedul
        self.solver.set_constraints(self.doc_preferences, QDate.currentDate())
        self.solver.solve_shift_scheduling()
        print('Finished Solving')
        self.sch_ls['Edited'] = self.solver.sch_data
        self.save_l.sa = True
        self.save_l.on_save_fin('DocSchedule.xlsx', 2)
        # self.save_l.on_save_fin('docDays.xlsx', 0)

    def doc_on_day(self, date, cfd=None, da='Current'):
        def xvx() -> list:
            doc_x = []
            for x in cfd:
                dy = list(scd[scd['Shift'] == x]['Doc'])
                if len(dy) == 0:
                    dy = [""]
                doc_x.append(dy)
            return doc_x

        data = self.sch_ls[da]
        if cfd is None:
            cfd = ['Call', 'Walkin']
        if isinstance(date, list):
            scd = data.loc[data['Days'].isin(date)]
            dyx = xvx()
        else:
            scd = data.loc[data['Days'] == date]
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
        if wig == 'Cal':
            tty = self.font_edit.currentText()
            self.active_col['Fill'] = self.font_ty[tty]['Fill']

        else:
            tty = self.active_wig
        self.active_col['Color'] = self.font_ty[tty]['Color']
        # self.c

    def set_active_font(self, font=None, ty='Font'):
        if self.font_edit.isEnabled():
            tty = self.font_edit.currentText()

        else:
            tty = self.active_wig

        if ty == 'Capital':
            if font < 5:  # enum
                self.font_ty[tty][ty] = self.cap_op[font]
        elif ty in ['Bold', 'Underline', 'Italic']:
            self.font_ty[tty][ty] = not self.font_ty[tty][ty]
        else:
            if ty in ['Color', 'Fill']:
                self.col.setCurrentColor(self.font_ty[tty][ty])
                font = QColorDialog().getColor()
            elif ty == 'Size':
                font = int(font)

            self.font_ty[tty][ty] = font

    def _update_set(self):
        print(f'\n{string_break}\n Loading Settings')
        self.setting_keys_combo = {'Date Format': 'dd-MMM-yyyy',  # y-m-d,y-d-m,d-m-y,m-d-y
                                   'Weekday Format': 'let',  # long,sort,,let
                                   'Start Week Format': 'Sun',
                                   'Mode': 'Single',
                                   'Active Doc': 'Dehlen',
                                   'Setting Mode': 'Call',
                                   }

        self.font_ty_default = {'Call': {'Font': QFont("Times"), 'Size': self.font_sizes[3],
                                         'Capital': self.cap_op[3], 'Color': QColor(Qt.blue),
                                         'Fill': QColor(Qt.green), 'AlignH': Qt.AlignHCenter,
                                         'AlignV': Qt.AlignVCenter, 'Bold': False,
                                         'Italic': False, 'Underline': False
                                         },

                                'Walkin': {'Font': QFont("Times"), 'Size': self.font_sizes[0],
                                           'Capital': self.cap_op[0], 'Color': QColor(Qt.black),
                                           'Fill': QColor(Qt.yellow), 'AlignH': Qt.AlignHCenter,
                                           'AlignV': Qt.AlignVCenter, 'Bold': False,
                                           'Italic': False, 'Underline': False},

                                'Doc Info': {'Font': QFont("Times"), 'Size': self.font_sizes[2],
                                             'Capital': self.cap_op[0], 'Color': QColor(Qt.black),
                                             'AlignH': Qt.AlignHCenter, 'AlignV': Qt.AlignVCenter, 'Bold': False,
                                             'Italic': False, 'Underline': False},

                                'Current Dayly Stats': {'Font': QFont("Times"), 'Size': self.font_sizes[2],
                                                        'Capital': self.cap_op[0], 'Color': QColor(Qt.black),
                                                        'AlignH': Qt.AlignHCenter, 'AlignV': Qt.AlignVCenter,
                                                        'Bold': False, 'Italic': False, 'Underline': False},

                                'Preferences': {'Font': QFont("Times"), 'Size': self.font_sizes[2],
                                                'Capital': self.cap_op[0], 'Color': QColor(Qt.black),
                                                'AlignH': Qt.AlignHCenter, 'AlignV': Qt.AlignVCenter, 'Bold': False,
                                                'Italic': False, 'Underline': False},
                                }

        for shift in self.shifts:
            if shift not in self.font_ty_default:
                self.font_ty_default[shift] = {'Font': QFont("Times"), 'Size': self.font_sizes[1],
                                               'Capital': self.cap_op[0], 'Color': QColor(Qt.black),
                                               'Fill': QColor(Qt.blue),
                                               'AlignH': Qt.AlignRight, 'AlignV': Qt.AlignVCenter,
                                               'Bold': False,
                                               'Italic': False, 'Underline': False}
        self.settings.beginGroup('combo')

        for ke, v in self.setting_keys_combo.items():
            val = self.settings.value(ke, v)
            self.combo[ke].setCurrentText(val)
            # ke_new = ke.lower().replace(' ', '_')  #
            print(f'Loaded {ke} = {val}')

        self.settings.endGroup()

        self.font_ty = {}
        self.set_op = {'font', 'fill', 'taps open', 'tab local'}

        self.settings.beginGroup('font')
        for ke, v in self.font_ty_default.items():
            val = {}
            self.settings.beginGroup(ke)
            for vi in v.keys():
                if isinstance(v[vi], bool):
                    val[vi] = self.settings.value(vi, v[vi], type=bool)
                else:
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

        self.settings.beginGroup('File Locals')
        for i in self.default_files.keys():
            self.default_files[i] = self.settings.value(i, self.default_files[i])
        self.settings.endGroup()

        k = self.settings.allKeys()

        for i, j in [(self.restoreGeometry, "Geometry"), (self.restoreState, "windowState")]:
            if j in k:
                va = self.settings.value(j)
                i(va)

        print(f'Finished Loading Settings\n{string_break}\n')

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
                                stir = [f'{di}{co}d{co}{mo}',
                                        f'{di}{co}{mo}{co}d']
                            else:
                                stir = [f'{f[i]}{co}{f[(i + 1) % 2]}']
                            if yf == 0:
                                j.extend(f'{y}{co}{si}' for si in stir)
                            else:
                                j.extend(f'{si}{co}{y}' for si in stir)

        self.cmd_ls['Date Format'] = j

    def _save_user_settings(self):
        self.settings = QSettings('Claassens Software', 'User Saved')
        self.user_settings()

    def user_settings(self, last_ses=True):
        print(f'\n{string_break}\nSaving Settings')
        self.settings.setValue("Geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        if last_ses:
            self.settings.beginGroup('combo')

            for ke in self.setting_keys_combo.keys():
                val = self.combo[ke].currentText()
                self.settings.setValue(ke, val)
                print(f'Saving{ke} = {val}')
            self.settings.endGroup()

            self.settings.beginGroup('font')
            for ke, v in self.font_ty.items():
                self.settings.beginGroup(ke)
                for vi in v.keys():
                    self.settings.setValue(vi, v[vi])
                self.settings.endGroup()
            self.settings.endGroup()

            self.settings.beginGroup('ActiveShift')
            for i in self.shifts:
                self.settings.setValue(i, i in self.active_shifts)
            self.settings.endGroup()

            self.settings.beginGroup('File Locals')
            for i, j in self.default_files.items():
                self.settings.setValue(i, j)
            self.settings.endGroup()

            setting = QSettings('Claassens Software', 'Calling LLB_2022_open')
            setting.setValue('Load Last Session', self.load_d)
            setting.setValue('Show on Startup', self.on_start)
            print(f'Finished Saving Settings\n{string_break}\n')

    def closeEvent(self, event):
        print(f'\n{string_break}\nClosing Doc\n{string_break}\n')
        self.user_settings(self.load_d)
        super().closeEvent(event)

        for i in self.ti_info.values():
            i.close_dia()

    def legend(self):
        print('legend')

    def ret_font(self, na):
        font_in = self.font_ty[na]
        font = font_in['Font']
        font.setPixelSize(font_in['Size'])

        font.setCapitalization(self.cap_op.index(font_in['Capital']))
        for i, j in {'Bold': font.setBold, 'Italic': font.setItalic, 'Underline': font.setUnderline}.items():
            j(font_in[i])  # true false

        align = [font_in['AlignH'], font_in['AlignV']]
        return font, font_in['Color'], align


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
        self.par.legend()

    def add_sch(self, ite):
        xi = self.menu_item[ite].isChecked()
        if xi:
            self.par.active_sch.append(ite)
        else:
            self.par.active_sch.remove(ite)
        self.par.legend()

    def _add_menu(self, pos):
        self.menu_item = {}
        print('Context Menu opened')
        self.context_menu = QMenu("Show Events", self)
        # self.context_menu.addSection('Shifts')
        for ite in self.par.shifts:

            action = QAction(ite)
            action.setCheckable(True)
            if ite in self.par.active_shifts:
                action.setChecked(True)
            action.triggered.connect(partial(self.add_text, ite))
            self.menu_item[ite] = action
            self.context_menu.addAction(action)

        print('next sec')
        self.context_menu.addSeparator()
        for i in self.par.schedules:
            action = QAction(i)

            action.setCheckable(True)
            if i in self.par.active_sch:
                action.setChecked(True)
            if i not in self.par.avalible_sch:
                action.setEnabled(False)

            action.triggered.connect(partial(self.add_sch, i))
            self.menu_item[i] = action
            self.context_menu.addAction(action)
            print('add action sch')

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
            self.dialog.close()

    def _init_dock(self):
        self.dock = QDockWidget(self.ti)
        self.dock.setWidget(self)
        self.par.addDockWidget(self.pos, self.dock)

    def reset_table(self):
        print('update df')
        self.set_data()
        print(self.df.head())
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

    def set_popup(self, ind, data=False):

        # ind = (x, y)
        if data:
            print(f'seting doc of: {ind}')
            xy = ind
            self.dia = docPopup(self, xy)
            self.dia.show()
        else:
            print('index at({},{})'.format(*ind))
            xy = self.df.iloc[0, ind[1]]
            if ind[0] == 0:
                self.dia = docPopup(self, xy)
                self.dia.show()
        print('popup')


class SideDoc(QDockWidget):
    def __init__(self, par, loc, name):
        super().__init__(loc)
        self.par = par
        self.name = name

    def closeEvent(self, event):
        self.par.settings.beginGroup('Docks')
        self.par.settings.beginGroup(self.name)

        self.par.settings.setValue('isOpen', False)
        self.par.settings.setValue('Area', self.area)  # is undocked?

        self.par.settings.endGroup()
        self.par.settings.endGroup()

        self.settings.setValue("Geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        pass


class dataPopup(QDialog):
    # noinspection PyArgumentList
    def __init__(self, par, res=None):
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


class CalendarDayDelegate(QItemDelegate):
    def __init__(self, parent=None, projects=None, par=None):
        super(CalendarDayDelegate, self).__init__(parent=parent)

        self.projects = projects
        # self.items_ls = {'Call': '', }
        self.par = par
        self.labs = []
        self.space = {'Current': 0.6, 'Edited': 0.3}
        self.space_ver = 0.15
        self.board_size = 1
        self.v_off = 0.4
        self.board_col = {'Current': Qt.red, 'Edited': Qt.black}
        self.v_space = 2
        self.last_month = True

    # def draw_rect(self):
    def paint(self, painter: QPainter, option, index):

        painter._date_flag = index.row() > 0
        super(CalendarDayDelegate, self).paint(painter, option, index)

        # only calls on date
        if painter._date_flag:

            # find month and year of date
            date_num_full = index.data()
            index_loc = (index.row(), index.column())

            year = self.par.yearShown()
            month = self.par.monthShown()

            # check if previous or next month
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

            # converts to QDate
            date = QDate(year, month, date_num_full)
            active_shifts = self.par.par.active_shifts
            painter.save()

            # rectangle of current date
            rect = option.rect
            x, y, w, h = rect.getRect()

            # loop through schedules
            for da in self.par.par.active_sch:
                for n, i in enumerate(active_shifts):  # loop throw shifts
                    doc = self.par.par.doc_on_day(date, [i], da)[0]

                    # back_color = Qt.red
                    siz = int(w * self.space[da])  # todo sort
                    size_v = int(w * self.space_ver)
                    if i == 'Call':
                        size_v += 10
                    if da == 'Current':
                        x0 = x + w - siz - self.v_space
                        y_off = 0
                    else:
                        x0 = self.v_space
                        y_off = self.v_off

                    if doc != "":
                        rect2 = QRect(x0, y + self.v_space + y_off, siz, size_v)

                        font, color, align = self.par.par.ret_font(i)
                        painter.setFont(font)
                        # align = self.op[n]

                        back_color = self.par.par.font_ty[i]['Fill']
                        y += size_v + self.v_space + self.board_size * 2

                        painter.setPen(QPen(self.board_col[da], self.board_size))
                        painter.setBrush(back_color)
                        painter.drawRect(rect2)

                        painter.setPen(color)
                        painter.drawText(rect2, align[0] | align[1], doc)  # , option=)

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
        painter.setBrush(self.par.active_col[self.ty])
        painter.drawRect(rect)


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
        print('Loading Last Session')
        j = 'Calling LLB_2022'
    else:
        print('Loading user Saved')
        j = 'User Saved'
    win.settings = QSettings('Claassens Software', j)
    win.on_start = again
    win.load_d = load_d
    win.show()
    st.close()


string_break = '_' * 10
if __name__ == '__main__':
    strs = ' ___     ____     ____\n' \
           '|   \\   |    |   |    |\n' \
           '|    )  |    |   |\n' \
           '|___/   |____|   |____|\n\n'
    print(strs)
    print(string_break)
    app = QApplication(sys.argv)
    win = Window()
    st = StartupDialog()
    _start_up_promt()
    sys.exit(app.exec_())
