import os.path
import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import pandas as pd
import sys


def save_csv(file, data):
    # todo add extra data to tell wat option
    print('load csv')
    data.to_csv(file)


def save_json(file, data):
    data.to_json(file)
    print('load json')


def save_ex(file, data):  # todo save open multy type
    print('oad ex')
    writer = pd.ExcelWriter(file)
    data.to_excel(writer)


def load_csv(file):
    print('load csv')
    data = pd.read_csv(file)
    return data


def load_json(file):
    data = pd.read_json(file)
    print('load json')
    return data


def load_ex(file):  # todo save open multy type
    print('oad ex')
    data = pd.read_excel(file)
    return data


class saveLoad(QFileDialog):
    def __init__(self, sa=True):
        super().__init__()
        self.setModal(True)
        self._set_f_t()
        self.accepted.connect(self.end_fun)

        # self.load_settings()
        self.func = [self.save_doc_preferences,  # of day,
                     self.save_doc_info,  # of properties and delta t, ]
                     self.save_secdual]

        self.func_load = [self.load_doc_preferences,  # of day,
                          self.load_doc_info,  # of properties and delta t, ]
                          self.load_secdual]

        self.save_fucs = {'excel': save_ex, 'csv': save_csv, 'json': save_json}
        self.load_fucs = {'excel': load_ex, 'csv': load_csv, 'json': load_json}
        self.sa = sa
        self._on_save_load()
        # self.currentChanged.connect(self._on_pox)
        # self._on_pox()
        # self._on_start()
        # self.save_settings()

    def _on_start(self):
        self.dia = QDialog(self)
        self.dia_lay = QVBoxLayout()
        self.name_lay = QLabel('Name')
        self.box = QComboBox()
        self.box.addItems(['prefernces', 'info', 'Scedule'])
        self.dia_lay.addWidget(self.name_lay)
        self.dia_lay.addWidget(self.box)

        # if dia not load breack else load

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.accepted.connect(self._dia_acc)
        self.buttonBox.rejected.connect(self.dia.reject)
        self.dia_lay.addWidget(self.buttonBox)
        self.dia.setLayout(self.dia_lay)
        self.on_save()

        self.dia.exec()

    def _dia_acc(self):
        setting_type = self.box.currentIndex()
        self.dia.accept()
        self.fun = self.func[setting_type]
        #

    def _on_save_load(self):
        if self.sa:
            self.end_fun = self.on_save_fin
            self.save_settings()
        else:
            self.end_fun = self.on_load_fin
            self.load_settings()

    def on_save_fin(self):
        file = self.selectedFiles()[0]
        if '.' not in file[-5:]:
            print('not in')
            filter_sel = self.selectedNameFilter()
            fil = re.search('\((.+?)\)', filter_sel).group(1).replace('*', '')
            # fil =   # todo oither suffic if selected
            # fil.replace('(','').replace(')', "").replace('*','')
            file += fil

        ex = os.path.splitext(file)[-1]
        data = self.fun()
        type1 = 'excel'

        for i, j in self.f_t.items():
            if ex in j:
                type1 = i
        fi = self.save_fucs[type1]
        fi(file,data)

    def on_load_fin(self):
        file = self.selectedFiles()[0]

        ex = os.path.splitext(file)[-1]

        type1 = 'excel'

        for i, j in self.f_t.items():
            if ex in j:
                type1 = i

        fi = self.load_fucs[type1]
        data = fi(file)
        # if 'doc' in data[0]:
        #     load = pref
        lo = self.func_load[0]
        lo(data)

    def ff(self):
        print('hi')
        f = self.children()
        print(f)

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

    def on_save(self):  # ,fun,ty):
        name = 'Shedual.xslm'  # todo ical
        self.setDirectory(name)
        # file = self.getSaveFileName(directory=name)
        # f = ty(file)
        # fun(f,file)  # todo wtf am i writing., maype cgange by end

    def _set_f_t(self):
        self.combo = {'User Readable': ['exel', 'csv'], 'data frame': ['json', 'exel', 'csv']}
        self.f_t = {'json': ['json'], 'csv': ['csv'], 'excel': ['xmls', 'xslm'], 'text': 'txt'}

    # def load_func(self, func):
    #     def wrap():
    #         self.setDefaultSuffix('csv')  # todo run type ana
    #         self.setAcceptMode(QFileDialog.AcceptSave)
    #         func()
    #     return wrap
    def load_func(self):
        self.setDefaultSuffix('csv')  # todo run type ana
        self.setAcceptMode(QFileDialog.AcceptOpen)

    # @load_func
    def load_settings(self):
        self.load_func()
        self.setNameFilter(['json', 'csv', 'excel'])
        pass

    def setNameFilter(self, filters):
        super().setNameFilter(self.load_f_type(filters))

    def load_doc_preferences(self, data):
        print(data)
        pass

    def load_secdual(self, data):
        print(data)
        pass

    def load_doc_info(self, data):
        print(data)
        pass

    def save_doc_preferences(self):
        print('save_doc pref')
        df = {'d': 20, 'x': 50}
        print('data = ', df)
        return df

    def save_doc_info(self):
        print('save_doc_iinfo')
        df = {'d': 20, 'x': 50}
        print('data = ', df)
        return df


    def save_secdual(self):
        print('save_doc_sch')
        df = {'d': 20, 'x': 50}
        print('data = ', df)
        return df

    def save_settings(self):
        name = 'Shedual.csv'  # todo ical
        self.setDirectory(name)
        self.setDefaultSuffix('csv')  # todo run type ana
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.setNameFilter(['json', 'csv', 'excel'])

    # def _on_pox(self):
    #     self.lay = super().layout()
    #     print(super().__dir__())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = saveLoad()
    win.show()
    sys.exit(app.exec_())
