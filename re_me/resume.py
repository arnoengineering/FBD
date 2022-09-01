from functools import partial

from PyQt5 import QtGui
from PyQt5.QtGui import QFont, QTextCharFormat, QPalette, QPainter, QColor, QIcon, QPen, QDrag  # QPainter, QPen,QBrush,
from PyQt5.QtCore import Qt, QDate, QSettings, QRect, QMimeData, QIODevice, QByteArray, \
    QDataStream  # , QByteArray  # QTimer, QSize,
# from logging import exception
# color pallette-color
# user medical, user doc gen
# folder-open-document-text
# disk
# document-excel table
from re_me.res_info import *
from PyQt5.QtWidgets import *

import pandas as pd
import sys

from saload import saveLoad

from super_bc import SuperCombo, SuperButton

# from email_doc import login
"""later
mail"""

'''exe

load
multiple groupby
add doc new info

settings:  # todo unsaved changes, todo overwrite, todo menu, user show
pivot
tables
settings
widgits close open
'''


def sort_day(ls):
    ls.sort(key=lambda x: x.toString(Qt.TextDate))


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.first_show = True
        self.settings = QSettings('Resume', 'Test1')
        self.setWindowTitle('Call Schedule Optimizer')
        self.setWindowIcon(QIcon('../icons/calendar-blue.png'))
        self.tool_tip = {}

        # self.settings = QSettings('Claassens Software', 'Calling LLB_2022')

    def showEvent(self, event):
        if self.first_show:
            self.first_show = False

            print(f'\n{string_break}\n|| Init Doc Window ||\n{string_break}\n')

            # init items
            self.initial_set()
            self._set_list()
            self._set_empty()

            self._creat_toolbar()
            self._create_tools()
            self._set_center()
            self._update_set()
            super().showEvent(event)

    def _set_list(self):
        """inits butons"""
        # init SaveLoad Option
        self.save_l = saveLoad(self, False)
        self.button_list = [
            'Save_disk-black',
            'Apply',
            'Load_document-excel-table',
        ]

        self.date_n = ['StartDate', 'EndDate']  # calselect days

    def _set_empty(self):
        """sets empty lists"""

        self.shifts = ['Detail', 'Date', 'Company', 'Title']
        self.cmd_ls = {'Setting Mode': self.shifts, 'Mode': ['Live', 'item']}
        # todo for each class and ech item if overrul
        self.schedules = ['Current', 'Edited']

        self.active_col = {'Color': Qt.black, 'Fill': Qt.black}
        self.font_style = ['Bold', 'Italic', 'Underline']
        # self.active_doc = self.doc_data[0]['Name']

        self.list_v = {}
        self.action_list = {}
        self.combo = {}
        self.sch_ls = {}
        self.active_shifts = []
        self.align_op = {'H': {'Left': Qt.AlignLeft, 'Center': Qt.AlignCenter, 'Right': Qt.AlignRight},
                         'V': {'Top': Qt.AlignTop, 'CenterV': Qt.AlignVCenter, 'Bottom': Qt.AlignBottom}}

        # self.default_tem = {'Cover': '../docInfoN.xlsx',
        #                     'resume': 'docDays.xlsx', }
        self.defualt_res_data = {'resume': 'test.xlsx'}

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

    def _set_center(self):
        self.cv = MainResume()
        self.active_wig = 'Main'  # todo fill edit option on click, drag optionedit asiciated value
        self.setCentralWidget(self.cv)
        self.all_ite = AllItems(self)
        self.current = CurrentView(self)

    def _creat_toolbar(self):
        self.font_sizes = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
        self.tool_bar = QToolBar('Main toolbar', self)
        self.cal_tool_bar = QToolBar('Calendar', self)
        self.cal_tool_bar.setObjectName('CalTools')

        self.table_tool = QToolBar('Tables', self)
        self.table_tool.setObjectName('TableToolbar')
        self.tool_bar.setObjectName('MainToolbar')
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

    # noinspection PyArgumentList
    def _create_tools(self):
        self.tool_bar2 = QToolBar(self)
        self.tool_bar2.setObjectName('ComboTools')

        self.addToolBar(self.tool_bar2)
        self.addToolBar(self.cal_tool_bar)

        # ___________comboboxes_______

        for wig_name, opt in self.cmd_ls.items():
            k = SuperCombo(wig_name, self, vals=opt)
            self.combo[wig_name] = k
            self.tool_bar2.addWidget(k.wig)

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

        elif i == 'Load':
            self.load_doc()

        elif i == 'Save':
            self._save_user_settings()

        elif i == 'Add':
            self.add_doctor_pref()

        elif i == 'Settings':
            self.run_set()

    def set_align(self, i, di):
        if self.font_edit.isEnabled():
            tty = self.font_edit.currentText()

        else:
            tty = self.active_wig
        self.font_ty[tty]['Align' + di] = self.align_op[di][i]

    def set_active_font(self, font=None, ty='Font'):
        if self.active_wig == 'Main':  # todo find
            self.cv.redo_font(ty, font)

        else:
            tty = self.combo['Setting Mode'].text()

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
                                   'Setting Mode': 'Call',
                                   }

        self.font_ty_default = {'Detail': {'Detail': QFont("Times"), 'Size': self.font_sizes[3],
                                           'Capital': self.cap_op[3], 'Color': QColor(Qt.blue),
                                           'Fill': QColor(Qt.green), 'AlignH': Qt.AlignHCenter,
                                           'AlignV': Qt.AlignVCenter, 'Bold': False,
                                           'Italic': False, 'Underline': False
                                           },

                                'Date': {'Font': QFont("Times"), 'Size': self.font_sizes[0],
                                         'Capital': self.cap_op[0], 'Color': QColor(Qt.black),
                                         'Fill': QColor(Qt.yellow), 'AlignH': Qt.AlignHCenter,
                                         'AlignV': Qt.AlignVCenter, 'Bold': False,
                                         'Italic': False, 'Underline': False},

                                'Company': {'Font': QFont("Times"), 'Size': self.font_sizes[2],
                                            'Capital': self.cap_op[0], 'Color': QColor(Qt.black),
                                            'AlignH': Qt.AlignHCenter, 'AlignV': Qt.AlignVCenter, 'Bold': False,
                                            'Italic': False, 'Underline': False},

                                'Title': {'Font': QFont("Times"), 'Size': self.font_sizes[2],
                                          'Capital': self.cap_op[0], 'Color': QColor(Qt.black),
                                          'AlignH': Qt.AlignHCenter, 'AlignV': Qt.AlignVCenter,
                                          'Bold': False, 'Italic': False, 'Underline': False},
                                }

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

        # self.settings.beginGroup('File Locals')
        # for i in self.default_files.keys():
        #     self.default_files[i] = self.settings.value(i, self.default_files[i])
        # self.settings.endGroup()

        print(f'Finished Loading Settings\n{string_break}\n')

    def initial_set(self):
        k = self.settings.allKeys()  # todo save other enteties, cal before or after
        for i, j in [(self.restoreGeometry, "Geometry"), (self.restoreState, "windowState")]:
            if j in k:
                va = self.settings.value(j)
                i(va)

    def _save_user_settings(self):

        self.user_settings()

    def user_settings(self):
        print(f'\n{string_break}\nSaving Settings')
        self.settings.setValue("Geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

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

    def closeEvent(self, event):

        self.user_settings()
        super().closeEvent(event)


# class settings(QSettings):
#     def __init__(self):
#         super().__init__('Resume', 'Test1')


class SideDoc(QDockWidget):
    def __init__(self, par, loc, name):
        super().__init__(name, parent=par)
        self.par = par
        self.name = name
        self.par.addDockWidget(loc, self)
        self.setObjectName(self.name)


class ItemObj(QTreeWidgetItem):  # todo just font, todo load mime
    def __init__(self, par):
        super().__init__()
        self.par = par
        self.font = QFont("Times")
        self.size = self.par.font_sizes[2]
        self.cap = self.par.cap_op[0]
        self.col = QColor(Qt.black)
        self.alignH = Qt.AlignHCenter
        self.alignV = Qt.AlignVCenter
        self.b = False
        self.i = False
        self.u = False

    def print_d(self):
        print('\nadd x')
        cnt = self.childCount()
        self.par.cv.append(self.text(0))
        if cnt != 0:
            for x in range(cnt):
                ite = self.child(x)  # todo remove bellow
                ite.print_d()


class JobItem:
    def __init__(self):
        self.start = ''
        self.end = ''
        self.name = ''  # todo other super with no name
        self.type = 'job'
        self.company = ''
        self.description = ''


class AllItems(QTreeWidget):
    format = 'application/x-customTreeWidgetdata'
    all_items = {'des': 'all', 'date': ['job', 'vol'], 'com': ['job', 'vol']}

    def __init__(self, par, area=Qt.RightDockWidgetArea,title='AllItems'):
        super().__init__()
        # self.format = 'application/x-customTreeWidgetdata'
        self.par = par
        self.title = title
        self.menu = {}
        self.dock = SideDoc(self.par, area, title)
        self.dock.setWidget(self)
        self.in_i()
        self.on_init()

        self.set_menu()

    def in_i(self):
        self.import_x()

    def import_x(self):
        self.add_x(all_work)
        pass

    def add_x(self, x, top=None):
        print('\nadd x', x)
        if top is None:
            print('top none')
            top = self

        if isinstance(x, dict):
            print('x_dict')
            for xi, j in x.items():
                print(f'xi:{xi}, j:{j}')

                jk = QTreeWidgetItem(top)
                jk.setText(0, xi)
                self.add_x(j, jk)
        elif isinstance(x, list):
            print('x_ls')
            for xi in x:  # todo list of list
                print(f'xi_list:{xi}')

                self.add_x(xi, top)
        else:  # now single
            print('x_sing')
            jk = QTreeWidgetItem(top)
            jk.setText(0, str(x))

    # def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
    #     pass

    def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent) -> None:
        pass

    def on_init(self):
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        # self.setDefaultDropAction(Qt.CopyAction)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        # self.set_menu()

    def dragEnterEvent(self, event):
        print(self.title, 'drag enter')
        if event.mimeData().hasFormat(AllItems.format):
            event.accept()
        else:
            event.ignore()

    # def supportedDropActions(self):
    #     return Qt.MoveAction| Qt.CopyAction

    def dragMoveEvent(self, event):

        if event.mimeData().hasFormat(AllItems.format):
            # event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()  # todo drop from center

    def add_text(self, ite, loc=None):  # todo sort cron
        print('ite:', ite)
        item = self.itemAt(loc)
        print('item = ', item.text(0))

        if ite == 'add':
            print('+++')
            par = item.parent()

            if par is None:
                par = self
                index = par.indexOfTopLevelItem(item)

                print('par = self')
            else:
                index = par.indexOfChild(item)
                print('par = ', par.text(0))
            print('index =', index)

            # todo if new item
            # par.insertChild(index + 1, item)

    def _add_menu(self, pos):
        self.menu = {}
        self.context_menu = QMenu("edit", self)
        # self.context_menu.addSection('Shifts')
        for ite in ['edit', 'add', 'edit root']:
            action = QAction(ite)
            self.menu[ite] = action
            action.triggered.connect(partial(self.add_text, ite, pos))

            self.context_menu.addAction(action)

        self.context_menu.exec(self.mapToGlobal(pos))

    def set_menu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # def setContextMenuPolicy(self):
        self.customContextMenuRequested.connect(self._add_menu)

    def mimeTypes(self):
        mimetypes = QTreeWidget.mimeTypes(self)
        mimetypes.append(AllItems.format)
        return mimetypes

    def startDrag(self, supported_actions):
        drag = QDrag(self)
        mimedata = self.model().mimeData(self.selectedIndexes())

        encoded = QByteArray()
        stream = QDataStream(encoded, QIODevice.WriteOnly)
        self.encode_data(self.selectedItems(), stream)
        mimedata.setData(AllItems.format, encoded)

        drag.setMimeData(mimedata)
        drag.exec_(supported_actions)

    def dropEvent(self, event):
        if event.source() == self:
            event.setDropAction(Qt.MoveAction)
            QTreeWidget.dropEvent(self, event)
            # if in aceptible drop else
        elif isinstance(event.source(), (QTreeWidget, AllItems)):
            print(self.title, ' xxx', event.mimeData().formats())

            if event.mimeData().hasFormat(AllItems.format):
                encoded = event.mimeData().data(AllItems.format)
                parent = self.itemAt(event.pos())
                if parent is None:
                    parent = self
                items = self.decode_data(encoded, event.source())
                print(self.title,' ite', items)
                for it in items:
                    item = QTreeWidgetItem(parent)
                    self.fill_item(it, item)
                    self.fill_items(it, item)
                event.acceptProposedAction()

    def fill_item(self, in_item, out_item):
        for col in range(in_item.columnCount()):
            for key in range(Qt.UserRole):
                role = Qt.ItemDataRole(key)
                out_item.setData(col,role, in_item.data(col,role))

    def fill_items(self, it_from, it_to):
        for ix in range(it_from.childCount()):
            it = QTreeWidgetItem(it_to)
            ch = it_from.child(ix)
            self.fill_item(ch, it)
            self.fill_items(ch, it)

    def encode_data(self, items, stream):
        stream.writeInt32(len(items))
        for item in items:
            p = item
            rows = []
            while p is not None:
                rows.append(self.indexFromItem(p).row())
                p = p.parent()
            stream.writeInt32(len(rows))
            for row in reversed(rows):
                stream.writeInt32(row)
        return stream

    def decode_data(self, encoded, tree):
        items = []
        rows = []
        stream = QDataStream(encoded, QIODevice.ReadOnly)
        while not stream.atEnd():
            nItems = stream.readInt32()
            for i in range(nItems):
                path = stream.readInt32()
                row = []
                for j in range(path):
                    row.append(stream.readInt32())
                rows.append(row)

        for row in rows:
            it = tree.topLevelItem(row[0])
            for ix in row[1:]:
                it = it.child(ix)
            items.append(it)
        return items


class MainResume(QTextEdit):
    def __init__(self):
        super().__init__()
        # todo on text changed chech if part of item then update or overwrite, edit block, insert
        print('llload x')

    def redo_font(self, x, val=None):
        if x == 'Size':
            self.setFontPointSize(int(val))  # todo start tabs
        elif x == 'Font':
            self.setFontFamily(val.toString())
        elif x == 'Color':
            self.setTextColor(val)

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        pass

    def dragLeaveEvent(self, e: QtGui.QDragLeaveEvent) -> None:
        pass

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        pass

    def dropEvent(self, e: QtGui.QDropEvent) -> None:  # todo check if is data then add

        pass

    def print_data(self):
        pass


class CurrentView(AllItems):
    '''in resume now, can drag drop in self or others, can add new at bottom, and can edit on doublclic
    maybe add super to other '''

    def __init__(self, par):
        super().__init__(par, Qt.LeftDockWidgetArea,'Current')

    def in_i(self):
        pass

    def print_data(self):
        self.print_dd(self)

    def print_dd(self, x):
        print('\nadd x', x)

        if x.children() is not None:
            print('x_dict')
            for xi in x.children():
                print(f'xi:{xi}')
                self.add_x(xi)
        else:  # now single
            x.paint_d()


class NewItem(QWizard):  # todo add date back
    def __init__(self):
        super().__init__()
        self.pages = {}
        self.info = [['job', 'volunteer', 'skill', 'interest'], ['name', 'start', 'end', 'description']]

    def _set_page(self):
        for i in ['choose', 'date', 'name', 'description']:
            j = QWizardPage(self)
            j.setTitle(i)
            self.addPage(j)

    def set_ch(self):
        but = QComboBox(self.pages['choose'])
        self.pages['choose'].registerField('button', but, but.currentText())

        but.addItems(self.info[0])

    def set_date(self):  # note only if job,vol
        but_box = QHBoxLayout(self.pages['date'])
        for i in ['Full', 'Month']:
            hb1 = QRadioButton(i, self.pages['date'])
            but_box.addWidget(hb1)

        n = 0
        date_box = QGridLayout(self.pages['date'])
        for i in ['Start', 'End']:
            lab = QLabel(i, self.pages['date'])
            date = QDateEdit(self.pages['date'])
            current = QCheckBox('current', self.pages['date'])
            current.clicked.connect(lambda x: date.setEnabled(not x))

            date_box.addWidget(lab, n, 0, 1, 2)
            date_box.addWidget(date, n + 1, 0)
            date_box.addWidget(current, n + 1, 1)
        # self.pages['choose'].registerField('button', but, but.currentText())

    def set_name_com(self):
        pass

    def set_des(self):
        pass


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


string_break = '_' * 10
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
