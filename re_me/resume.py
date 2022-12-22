import sys
from functools import partial
import copy
import pandas as pd
from PyQt5.QtCore import Qt, QDate, QSettings, QRect, QIODevice, QByteArray, \
    QDataStream, QSizeF  # , QByteArray  # QTimer, QSize,
from PyQt5.QtGui import QFont, QPainter, QColor, QIcon, QDrag, \
    QTextDocument  # QPainter, QPen,QBrush,
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup as bs

from re_me.res_info import *
from saload import saveLoad
from super_bc import SuperCombo, SuperButton


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
            self._setup_load()

            self._creat_toolbar()
            self._create_tools()
            self._set_center()
            self._update_set()
            self._setup_load()
            super().showEvent(event)

    def _set_list(self):
        """inits butons"""
        # init SaveLoad Option
        self.save_l = saveLoad(self, False)
        self.button_list = [
            'Save_disk-black',
            'Apply',
            'Load_document-excel-table',
            'Save Job'
        ]

        self.date_n = ['StartDate', 'EndDate']  # calselect days

    def _set_empty(self):
        """sets empty lists"""

        self.shifts = ['Detail', 'Date', 'Company', 'Title']
        self.cmd_ls = {'Setting Mode': self.shifts, 'Mode': ['Live', 'item']}
        # todo for each class and ech item if overrul
        self.schedules = ['Current', 'Edited']
        self.jobs = []

        self.active_col = {'Color': Qt.black, 'Fill': Qt.black}
        self.font_style = ['Bold', 'Italic', 'Underline']
        # self.active_doc = self.doc_data[0]['Name']

        self.list_v = {}
        self.action_list = {}  # todo categories skill
        self.job_df = None
        self.combo = {}
        self.sch_ls = {}
        self.active_shifts = []
        self.align_op = {'H': {'Left': Qt.AlignLeft, 'Center': Qt.AlignCenter, 'Right': Qt.AlignRight},
                         'V': {'Top': Qt.AlignTop, 'CenterV': Qt.AlignVCenter, 'Bottom': Qt.AlignBottom}}

        # self.default_tem = {'Cover': '../docInfoN.xlsx',
        #                     'resume': 'docDays.xlsx', }
        self.defualt_res_data = {'resume': 'test.xlsx', 'resume2': 'test.json'}

    def qdate_from_date(self, x):
        if isinstance(x, pd.DatetimeTZDtype):
            return QDate(x.year, x.month, x.day)
        elif isinstance(x, int):
            return QDate(1900, 1, 1).addDays(x)
        else:
            return QDate.fromString(x, self.day_f)

    def _setup_load(self):
        """loads default scedual last pref"""

        # loading info for each doc

        self.save_l.on_load_fin(self.defualt_res_data['resume2'], 'info')
        print('Loaded Doc info')

    def load_x(self, ty, data):
        if ty == 'info':
            if self.job_df is None:
                self.job_df = data
            else:
                self.job_df = pd.concat((self.job_df, data), ignore_index=True)

            print('info loaded = ')
            print(self.job_df.head())

    def _set_center(self):
        self.cv = MainResume(self)
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
        self.date_format = 'dd-MMM-yyyy'

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
        elif i == 'Save Job':
            self.save_job()

    def save_job(self):
        if self.job_df is None:
            self.job_df = pd.DataFrame(self.jobs)
        else:
            self.job_df = pd.concat((self.job_df, pd.DataFrame(self.jobs)), ignore_index=True)
        self.save_l.sa = True
        self.save_l.over = False
        self.save_l.on_save_fin(self.defualt_res_data['resume2'], 'info')

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

    def add_items(self, title):
        # if left or center, open, but treat as loc on right for rename too
        # if rem{
        # do left remove}
        # else{add right-->left}
        # update center:::keep formating
        pass

    def sort_items(self, title):
        # sort item was done, then do uther two
        # posibly update center
        pass


class SideDoc(QDockWidget):
    def __init__(self, par, loc, name):
        super().__init__(name, parent=par)
        self.par = par
        self.name = name
        self.par.addDockWidget(loc, self)
        self.setObjectName(self.name)


class ItemObj(QTreeWidgetItem):
    op_n = ['title', 'start', 'end', 'type', 'company', 'description', 'location']

    def __init__(self, sup_par, par, **kwargs):
        super().__init__(sup_par)
        self.list_op = list(kwargs.keys())
        self.par = par

        self.sup_par = sup_par
        self.start = ''
        self.end = ''
        self.name = ''
        self.type = ''
        self.company = ''
        self.description = ''

        for i, j in kwargs.items():
            self.__setattr__(i, j)

        self.font = QFont("Times")
        self.size = self.par.font_sizes[2]
        self.cap = self.par.cap_op[0]
        self.col = QColor(Qt.black)
        self.alignH = Qt.AlignHCenter
        self.alignV = Qt.AlignVCenter
        self.b = False
        self.i = False
        self.u = False
        self.des_it = []
        self.add_x(self.list_op, False)
        self.add_des()

    # def text_2(self):
    #     print('\nadd x')
    #     # normal
    #     cnt = self.childCount()
    #     self.par.cv.append(self.text(0))
    #     html = """<div class="Job">
    # <p class="title">{title}</p>
    # <table>
    #     <tr>
    #         <td>company</td> <td>whitespace</td>
    #         <td>start</td> <td>-</td> <td>end</td>
    #     </tr>
    # </table>
    # <p class="loc">place loc</p>
    # <ul class = "description">
    #     """
    #     cnt = self.childCount()
    #     for i in range(cnt):
    #         jk = self.child(i)
    #         html += f"< li >{jk.text(0)} < / li >"
    #
    #     html += "</ul></div>"
    #     return html

    # def print_d(self):
    #     print('\nadd x')
    #     cnt = self.childCount()
    #     self.par.cv.append(self.text(0))
    #     if cnt != 0:
    #         for x in range(cnt):
    #             ite = self.child(x)
    #             ite.print_d()

    def run_x(self, x, j):  # todo save for current sel in chart, todo descrip
        self.setText(x, j)

    def add_x(self, list_op, new_ord=True):
        self.list_op = list_op
        for n, i in enumerate(list_op):
            if i != 'description':
                xi = n if new_ord else ItemObj.op_n.index(i)
                self.setText(xi, self.__getattribute__(i))

    def add_des(self):
        if not isinstance(self.description, list):
            self.description = [self.description]
        for i in self.description:
            j = QTreeWidgetItem(self)
            j.setText(0, i)
            self.des_it.append(j)

    def ret_text(self):
        jkn = {}
        for n, i in enumerate(self.list_op):
            if i != 'description':
                jkn[i] = self.text(n)

        jkn['description'] = [self.child(i).text(0) for i in range(self.childCount())]
        return jkn

    def date_x(self,x):  # todo class varible, run inverse
        j = self.__getattribute__(self.list_op[x])
        # fliplf if text
        return j


    def __lt__(self, other):
        col = self.treeWidget().sortColumn()  # todo if left block ie signal, sort other
        col_n = self.list_op[col]  # todo day format:::todo default sort
        data = self.text(col)
        data2 = other.text(col)
        gg = [data, data2]
        if col_n in ['start', 'end']:
            for i in range(2):  # todo date
                if gg[i] in ['present', 'current','']:
                    gg[i] = QDate.currentDate().toString(self.par.date_format)

        return gg[0]<gg[1]

# class block(QTextBlock):
#     def __init__(self):
#         super(block, self).__init__()

class doc(QTextDocument):
    def __init__(self):
        super(doc, self).__init__()
        self.point_inch = 72
        self.setPageSize((8.5,11))

    def setPageSize(self, size) -> None:
        si = QSizeF(self.point_inch*size[0],self.point_inch*size[0])
        super().setPageSize(si)
    # def sel_bloc(self,typ,con):
    #     for b in self.blocks():
    #         b.edit format, all items with b edit aswell, slide at top for align


"""rightclick to edit, open contect menu, format menu, popup
add sort"""
class AllItems(QTreeWidget):
    format = 'application/x-customTreeWidgetdata'
    all_items = {'des': 'all', 'date': ['job', 'vol'], 'com': ['job', 'vol']}

    def __init__(self, par, area=Qt.RightDockWidgetArea, title='AllItems'):
        super().__init__()
        # self.format = 'application/x-customTreeWidgetdata'
        self.par = par
        self.title = title
        # self.sort = PYQT_SIGNAL()
        self.view = ['All']  # todo if na, ''# hide on rightlick if no index# month to 1st day, date, sort subhead
        # todo resize
        self.menu = {}
        self.col_decend = [0, False]
        self.dock = SideDoc(self.par, area, title)
        self.dock.setWidget(self)
        self.col_lables = ItemObj.op_n

        # self.setHeader(headItem(self)),
        # self.columnCountChanged.connect(self.col_name)
        self.setHeaderLabels(self.col_lables)
        self.setSortingEnabled(True)

        self.cursor().pos()
        # self.header().clicked.connect(self.px)
        self.add_df()
        # self.in_i()
        self.on_init()

        self.set_menu()

    def col_name(self):

        for i in range(self.topLevelItemCount()):
            it = self.topLevelItem(i)
            for n in range(it.childCount()):
                j = it.child(n)
                j.add_x(self.col_lables)

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
            for xi in x:
                print(f'xi_list:{xi}')

                self.add_x(xi, top)
        else:  # now single
            print('x_sing')
            jk = QTreeWidgetItem(top)
            jk.setText(0, str(x))

    def add_df(self):
        df = self.par.job_df
        df.fillna("", inplace=True)

        df_dict = {sale_v: df[df['type'] == sale_v].reset_index() for sale_v in df['type'].unique()}
        for d, x in df_dict.items():
            top = QTreeWidgetItem(self)
            top.setText(0, str(d))

            row = x.shape[0]
            for r in range(row):
                dx = {v: x.loc[r, v] for v in x.columns if v != 'index'}
                ItemObj(top, self.par, **dx)
        self.col_name()

    # def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent) -> None:
    #     pass

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
            event.ignore()

    def add_text(self, ite, loc=None):  # todo sort cron
        print('ite:', ite)
        item = self.itemAt(loc)

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

        elif ite == 'type':
            self.item_ls(item)
        else:
            self.wiz = NewItem(self.par)
            self.wiz.exec()

    def _add_menu(self, pos):
        self.menu = {}
        self.context_menu = QMenu("edit", self)
        # self.context_menu.addSection('Shifts')
        for ite in ['edit', 'add', 'edit root', 'type']:
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
                print(self.title, ' ite', items)
                for it in items:
                    item = QTreeWidgetItem(parent)
                    self.fill_item(it, item)
                    self.fill_items(it, item)
                event.acceptProposedAction()

    def fill_item(self, in_item, out_item):
        for col in range(in_item.columnCount()):
            for key in range(Qt.UserRole):
                role = Qt.ItemDataRole(key)
                out_item.setData(col, role, in_item.data(col, role))

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

    def item_ls(self, pos, layer=0, ob=0):
        print(f'item ({layer}, {ob})-->{type(pos)}::{pos.text(0)}')
        cnt = pos.childCount()
        print('cnt = ', cnt)
        if cnt > 0:
            layer += 1
            ob = 0
            for n in range(cnt):
                x = pos.child(n)
                self.item_ls(x, layer, ob)
                ob += 1

    def sortItems(self, col, order):
        le = self.topLevelItemCount()
        for i in range(le):
            xi = self.topLevelItem(i)
            # sort coll
            xi.sortChildren(col, order)


class MainResume(QTextEdit):
    def __init__(self,par):
        super().__init__()
        self.par=par
        # todo on text changed chech if part of item then update or overwrite, edit block, insert
        print('llload x')
        self.doc = doc()
        self.setDocument(self.doc)
        # self.margin  # todo vewctor

        self.set_menu()

    def redo_font(self, x, val=None):
        if x == 'Size':
            self.setFontPointSize(int(val))  # todo start tabs
        elif x == 'Font':
            self.setFontFamily(val.toString())
        elif x == 'Color':
            self.setTextColor(val)

    # def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
    #     pass
    #
    # def dragLeaveEvent(self, e: QtGui.QDragLeaveEvent) -> None:
    #     pass
    #
    # def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
    #     pass
    #
    # def dropEvent(self, e: QtGui.QDropEvent) -> None:  # todo check if is data then add
    #
    #     pass
    #
    # def print_data(self):
    #     pass

    def add_text(self, dbl_clk, pos):  # todo add drag, add edit, block layer, block clicked, currtent check
        self.par.current.set_txt_init()
        bct = self.doc.blockCount()
        # curs = self.cursorForPosition(pos)
        # blc = curs.block()
        # # wile class = none
        # # soup.up_n till class
        # if dbl_clk:
        #     tex = QInputDialog()  # todo note: same for left
        #     text = tex.getText(self, 'Rename','renamemenu', blc.text())  # todo all or just this button
        #     curs.insertText(text)  # todo remove text, then insert use bs to filer and select text
        # if ite == 'block cnt':
        #
        #
        #     print('block cnt: ', bct)
        #      # if update iterate all blocks and set to x
        #     blc = curs.block()  # todo check if update
        #     print(f'block {blc}<<-->>: {self.doc.findBlockByNumber(blc).text()}')
        #     for i in range(bct):
        #         block = self.doc.findBlockByNumber(i)
        #
        #         print(f'block:{i}--> {block.text()}')
        #     block.setUserData()
            # self.QTextCursor::block()

    def _add_menu(self, pos):
        self.menu = {}
        self.context_menu = QMenu("edit", self)
        # self.context_menu.addSection('Shifts')
        for ite in ['block cnt']:
            action = QAction(ite)
            self.menu[ite] = action
            action.triggered.connect(partial(self.add_text, ite, pos))

            self.context_menu.addAction(action)

        self.context_menu.exec(self.mapToGlobal(pos))

    def set_menu(self):  # todo with default
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # def setContextMenuPolicy(self):
        self.customContextMenuRequested.connect(self._add_menu)

    # def add_to_text(self):
    #     for i in current:
    #         self.add_to_text()#


class CurrentView(AllItems):
    '''in resume now, can drag drop in self or others, can add new at bottom, and can edit on doublclic
    maybe add super to other '''

    def __init__(self, par):
        super().__init__(par, Qt.LeftDockWidgetArea, 'Current')
        self.space = "<p></p><p></p>"

    def in_i(self):
        pass

    def print_dd(self):
        tex = ""
        for x in range(self.topLevelItemCount()):
            tex += self.space

            ite = self.topLevelItem(x)
            ite_text = ite.text()
            tex += f'<div class={ite_text}><p class="title">{ite_text}</p>'  # todo.join
            re = ite.childCount()
            for i in range(re):
                tex += "<p></p>"
                ite_sub = ite.child(i)
                tex += ite_sub.text_2()  # todo sort on change, update css, add space,
                # maybe only hold infor and replace v
                # items get differant layouts depending on ite? calculate
        self.par.cv.setText(tex)

    def set_txt_init(self):
        with open('re_me/test.html') as fp:
            soup = bs(fp, 'html.parser')
        print('\n------------\nsoup\n------------\n')
        # print(soup)
        # soup_titles = soup.find_all('div', 'title')
        for x in range(self.topLevelItemCount()):  # check if only tags or all soup is edited
            ite = self.topLevelItem(x)

            ite_text = ite.text(0)
            try:
                soup_sub = soup.find('h1',text=ite_text).parent
                print('soupsub')
                print(soup_sub)

                soup_sub_ls = soup_sub.find_all('div', ite_text)[0]  # todo copy, replace
            except AttributeError:
                print('error opening ', ite_text)
                continue
            re = ite.childCount()
            for i in range(re):
                ss = copy.copy(soup_sub_ls)
                soup_sub.append(ss)
                ite_sub = ite.child(i)
                # sup_des = ss.find(attr={'class': 'description'})
                it_t = ite_sub.ret_text()
                for j, k in it_t.items():
                    try:
                        sup_des = ss.find(attrs={'class': j})
                        print(sup_des,end=" ")
                        if j == "description":
                            sk = sup_des.contents[0]
                            for si in k:
                                skk = copy.copy(sk)
                                sup_des.append(skk)
                                skk.string.replace_with(si)

                            del sk
                        else:
                            sup_des.string.replace_with(k)

                        print("-->", sup_des)
                    except AttributeError:
                        print(f'error opening sub {ite_text}-->({it_t["title"]}:{j}) ')
                        continue
            del soup_sub_ls    # todo description...

        print('\n------------\nFinal soup\n------------\n')
        print(soup)
        self.par.cv.setText(soup.prettify())
        print('ext')
        print(soup.prettify())
        print('ext')
        print(self.par.cv.toHtml())
        print('yo')

class NewItem(QWizard):  # todo add date back
    def __init__(self, par):
        super().__init__()

        print('hiiii')
        self.par = par
        self.pages = {}
        self.va = {}
        self.init_page_ls = ['choose', 'date', 'name', 'description']
        self.info = [['job', 'volunteer', 'skill', 'interest'], ['name', 'start', 'end', 'description']]
        self._set_page()
        self.set_ch()
        self.set_date()
        self.set_des()

    def _set_page(self):
        print('sp')
        for i in self.init_page_ls:
            j = QWizardPage(self)
            j.setTitle(i)
            self.addPage(j)
            self.pages[i] = j

    def nextId(self):
        ind = self.currentId()
        if ind == 'choose':
            if self.field('choose.button') in ['job', 'volunteer']:
                return self.init_page_ls.index('date')
            return self.init_page_ls.index('name')
        else:
            return super().nextId()

    def initializePage(self, p_int):
        if self.init_page_ls[p_int] == 'name':
            self.set_name(self.hasVisitedPage(self.init_page_ls.index('date')))  # todo programly n
        else:
            super().initializePage(p_int)

    def set_ch(self):
        print('choose')
        but = QComboBox(self.pages['choose'])
        self.pages['choose'].registerField('button', but, but.currentText())

        but.addItems(self.info[0])
        self.va['type'] = but

    def set_name(self, xi):

        but_box = QGridLayout(self.pages['name'])
        li = QLineEdit('', self.pages['name'])
        but_box.addWidget(QLabel('Title'), 0, 0)
        but_box.addWidget(li, 0, 1)
        self.pages['name'].registerField('name*', li, li.text())
        self.va['name'] = li
        if xi:
            but_box.addWidget(QLabel('Company'), 1, 0)
            li2 = QLineEdit('', self.pages['name'])
            but_box.addWidget(li2, 1, 1)
            self.va['company'] = li2
            self.pages['name'].registerField('com*', li, li.text())
        # todo company

    def set_date(self):  # note only if job,vol
        def d2x(dat):
            def rr(xi):
                dat.setEnabled(not xi)

            return rr

        print('date')
        l2 = QVBoxLayout(self.pages['date'])  # todo click

        but_box = QHBoxLayout(self.pages['date'])
        for i in ['Full', 'Month']:
            hb1 = QRadioButton(i, self.pages['date'])
            self.va['Date_' + i] = hb1
            but_box.addWidget(hb1)
        self.va['Date_Full'].setChecked(True)

        n = 0
        date_box = QGridLayout(self.pages['date'])

        for i in ['Start', 'End']:
            lab = QLabel(i, self.pages['date'])
            date = QDateEdit(self.pages['date'])
            date.setDate(QDate.currentDate())
            current = QCheckBox('current', self.pages['date'])
            ri = d2x(date)
            current.clicked.connect(ri)
            self.va['Date_' + i] = date
            date_box.addWidget(lab, n, 0, 1, 2)
            date_box.addWidget(date, n + 1, 0)
            date_box.addWidget(current, n + 1, 1)
            n += 2
        l2.addLayout(but_box)
        l2.addLayout(date_box)

    def set_des(self):
        but_box = QVBoxLayout(self.pages['description'])
        li = QTextEdit(self.pages['description'])
        but_box.addWidget(QLabel('descrip'))
        but_box.addWidget(li)
        # li.deleteLater(), cut,paset,

        self.pages['description'].registerField('des', li, li.toPlainText())  # textchaged = complete
        self.va['des'] = li
        pass

    def accept(self):
        # QWizardPage.field
        x = self.va['des'].toPlainText()  # li.toPlainText()
        des_line = x.splitlines()
        xi = {'description': des_line[0], 'type': self.va['type'].currentText(),
              # todo fix zero on exp, on edit jubp topage
              'title': self.va['name'].text(), }
        if 'company' in self.va:
            xi['company'] = self.va['company'].text()

        if self.hasVisitedPage(self.init_page_ls.index('date')):
            for i in ['Start', 'End']:
                if self.va['Date_' + i].isEnabled():

                    xi[i] = self.va['Date_' + i].date()
                else:
                    xi[i] = QDate.currentDate()

        self.par.jobs.append(xi)
        print('Jobs: ', self.par.jobs)
        super().accept()

    def htm(self, des):
        ht = '<ul>'
        for x in des:
            ht += f'<li>{x}<\\li>'
        ht += '<\\ul>\frac '


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
