
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import *


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
        print('New Doctor acepted')
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
        print('New Doctor reject')
        self.reject()

    # def _init_page_1(self):
    #     self.p1 = QWizardPage()
    #     self.p1_grid = QVBoxLayout()
    #     b1 = QRadioButton('New')
    #     b2 = QRadioButton('Edit')
    #     on next qbut neet to be checked forb page
