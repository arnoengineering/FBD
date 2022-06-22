from PyQt5.QtWidgets import *
import pandas as pd
import sys


class saveLoad(QFileDialog):
    def __init__(self):
        super().__init__()
        self.setModal(True)
        self._set_f_t()
        self.load_settings()

    def ui(self):
        if user selects string from dropdown, change to update
        pass
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

    def on_save(self,fun,ty):
        name = 'Shedual.xslm'  # todo ical
        file = self.getSaveFileName(directory=name)
        f = ty(file)
        fun(f,file)  # todo wtf am i writing., maype cgange by end

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
        # self.setDefaultName()
        # if save test data, and end
        # list all
        pass

    def save_ex(self,file, data):  # todo save open multy type
        writer = pd.ExcelWriter(file)
        pd.DataFrame.to_excel(data, file)
        pass

    def save_jsn(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = saveLoad()
    win.show()
    sys.exit(app.exec_())
