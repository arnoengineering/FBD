
from PyQt5.Qt import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import QDate, Qt

from PyQt5.QtGui import QIcon, QPixmap

from PyQt5.QtWidgets import *

import numpy as np
import pandas as pd
import sys

from functools import partial

import smtplib
import mimetypes

from email import encoders
from email.utils import formatdate

from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class login(QDialog):
    def __init__(self, par):
        super().__init__()
        print('loading email host')
        self.par = par
        self.email_op = {'Outlook':'office365', 'Gmail':'gmail'}

        self._init_ui()

    def _init_ui(self):
        print('loading email host ui')
        self.layout = QGridLayout()

        self.clients = {}
        self.top_lab = QLabel('Login')
        n = 2
        m = 0

        self.layout.addWidget(self.top_lab,0,0,1,2)
        for mi, i in enumerate(self.email_op.keys()):
            self.clients[i] = QRadioButton(i + " Mail")
            self.layout.addWidget(self.clients[i], 1,mi)

        # e = [self.live, self.gmail, self.yahoo]

        # for i in e:
        #     i.clicked.connect(self.Email)

        self.user_data = {}
        for i in ['Email', 'Password']:
            self.layout.addWidget(QLabel(i+':'), n,0)
            self.user_data[i] = QLineEdit(self)
            self.layout.addWidget(self.user_data[i],n,1)
            n += 1

        self.user_data['Password'].setEchoMode(2)
        self.user_data['Password'].returnPressed.connect(self.login)

        self.go = QPushButton("login", self)
        self.go.clicked.connect(self.login)
        self.layout.addWidget(self.go, n, 1)

        self.setGeometry(300, 300, 350, 200)
        self.setWindowTitle("PyMail login")
        self.setLayout(self.layout)
        # self.setWindowIcon(QIcon("PyMail"))
        # self.setStyleSheet("font-size:15px;")

    def login(self):
        print('logging in')
        curr_user_data = [i.text() for i in self.user_data.values()]
        select_serv = 'gmail' if self.clients['gmail'].isChecked() else 'outlook'
        if '@' in curr_user_data[0]:  # user full
            user_server = curr_user_data[0].split('@')[1].replace('.com', '')
            if user_server in self.email_op:
                select_serv = user_server
        else:
            curr_user_data[0] += f'@{select_serv}.com'

        server = smtplib.SMTP(f'smtp.{self.email_op[select_serv]}.com', 587)

        try:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(*curr_user_data)

            self.hide()

            main = Main(curr_user_data[0], self.par)
            main.show()

        except smtplib.SMTPException:
            msg = QMessageBox.critical(self, 'login Failed',
                                             "Username/Password combination incorrect", QMessageBox.Ok |
                                             QMessageBox.Retry, QMessageBox.Ok)

            if msg == QMessageBox.Retry:
                self.login()


class Main(QMainWindow):

    def __init__(self,data, par=None):
        super().__init__()
        print('looading main')
        self.data = data
        self.par = par
        self.place_hold = 'Hold please'
        self._init_ui()

    def _init_ui(self):
        print('looading main ui')
        self.labels = []
        self.user_grid = QHBoxLayout()
        self.grid = QVBoxLayout()

        doc_ls = self.par.doc_data['Email'].unique()
        self.send_2 = {}
        n = 0
        for d in doc_ls:
            self.send_2[d] = QCheckBox()
            self.send_2[d].clicked.connect(self._send_2_up)
            self.user_grid.addWidget(self.send_2[d])
            n+= 1
        self.grid.addWidget(QLabel('Send to: '))
        self.grid.addLayout(self.user_grid)



        self.labels = {}
        self.lab_ls = ['Send', 'From', 'To', 'Subject']
        self.to_addr = []

        for i in self.lab_ls:
            self.labels[i] = QLabel(i)
            if i == 'Send':
                 j = QPushButton()
                 j.clicked.connect(self.send_mail)
            elif i == 'Body':
                j = QTextEdit()
            else:
                j = QLineEdit()

            self.but_ls[i] = j
            self.grid.addWidget(self.labels[i])
            self.grid.addWidget(self.but_ls[i])
            # add wigit
            # add widit lined edit unless body or  send

        self.but_ls['From'].setText(self.data)
        self.but_ls['Subject'].setPlaceholderText(self.place_hold)
        self.but_ls['To'].setPlaceholderText("example@gmail.com, example2@gmail.com")
        # todo option for file send, csv, excel, ical

        self.image = QPushButton("Attach file", self)
        self.image.clicked.connect(self.add_image)
        self.cen = QWidget()

        self.cen.setLayout(self.grid)

        self.setCentralWidget(self.cen)

        # ---------Window settings --------------------------------

        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle("PyMail")
        self.setWindowIcon(QIcon("PyMail"))
        self.setStyleSheet("font-size:15px")

    def _send_2_up(self):
        print('send_2_u')
        self.to_addr = []
        for x,j in self.send_2.items():
            if j.isChecked():
                self.to_addr.append(x)
        self.but_ls['To'].setText(', '.join(self.to_addr))


    def ContextMenu(self):
        global sender
        print('context')
        sender = self.sender()

        self.menu = QMenu(self)

        remove = QAction("Remove", self)
        remove.triggered.connect(self.Remove)

        self.menu.addAction(remove)

        self.menu.show()

    def Remove(self):
        global sender
        global pos
        global labels
        global attachments

        print('removed')

        pos -= 1

        ind = labels.index(sender)

        attachments.remove(attachments[ind])

        labels.remove(sender)

        sender.setParent(None)

    def add_image(self):
        print('add img')

        path = QFileDialog.getOpenFileName(self)

        if path:

            self.attachments.append(path)

            self.filetype = path[path.rindex(".") + 1:]
            # todo seperate file per user
            # if filetype == "png":
            #     pic = QPixmap(path)
            # else:
            #     if filetype + ".png" in os.listdir("C:/Python32/python/pyqt/PyMail/48px/"):
            #         print("normal")
            #         pic = QPixmap("C:/Python32/python/pyqt/PyMail/48px/" + filetype + ".png")
            #     else:
            #         print("weird")
            #         pic = QPixmap("C:/Python32/python/pyqt/PyMail/48px/_blank.png")

            a = QLabel(path, self)
            a.setScaledContents(True)
            a.setFixedSize(50, 50)
            # a.setPixmap(pic)
            a.setToolTip(path)

            a.setContextMenuPolicy(Qt.CustomContextMenu)
            a.customContextMenuRequested.connect(self.ContextMenu)

            self.labels.append(a)

            print(self.attachments, labels)

            pos = len(attachments)

            l = [self.from_label, self.from_addr, self.to_label, self.to_addr, self.subject_label, self.subject,
                 self.image, self.text, self.send]

            for index, i in enumerate(l):
                self.grid.addWidget(i, index, 0, 1, pos + 1)

                if i in l[-2:]:
                    self.grid.addWidget(i, index + 1, 0, 1, pos + 1)

            self.grid.addWidget(a, 7, pos - 1)
            self.setGeometry(300, 300, 500, 550)

    def send_mail(self):  # todo drag, todo per doc
        print('send mail')
        server = self.par.server  # todo one up

        # self.filetype
        # global l

        msg = MIMEMultipart()

        for ite,j in self.but_ls.items():
            if ite not in ['Send', 'Body']:
                msg[ite] = j.text()
        msg['Date'] = QDate.today().toString('yyyy-MM-dd')

        body = self.but_ls['Body'].toPlainText()
        msg.attach(MIMEText(body, "plain"))

        if self.attachments:
            for file in self.attachments:
                ctype, encoding = mimetypes.guess_type(file)

                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'

                maintype, subtype = ctype.split('/', 1)

                if maintype == 'text':
                    fp = open(file)
                    att = MIMEText(fp.read(), _subtype=subtype)
                    fp.close()
                elif maintype == 'image':
                    fp = open(file, 'rb')
                    att = MIMEImage(fp.read(), _subtype=subtype)
                    fp.close()
                elif maintype == 'audio':
                    fp = open(file, 'rb')
                    att = MIMEAudio(fp.read(), _subtype=subtype)
                    fp.close()
                else:
                    fp = open(file, 'rb')
                    att = MIMEBase(maintype, subtype)  # todo default
                    att.set_payload(fp.read())
                    fp.close()
                    encoders.encode_base64(att)

                att.add_header('Content-Disposition', 'attachment', filename=file[file.rindex("/"):])
                msg.attach(att)

        text = msg.as_string()

        try:
            server.sendmail(self.but_ls['From'], self.but_ls['To'], text)

            msg = QMessageBox.information(self, 'Message sent',
                                                "Message sent successfully, clear everything?", QMessageBox.Yes |
                                                QMessageBox.No, QMessageBox.Yes)

            if msg == QMessageBox.Yes:
                self.to_addr.clear()
                self.subject.clear()
                self.text.clear()

                if self.attachments:
                    for i in self.attachments:
                        self.attachments.remove(i)

                    for i in reversed(range(self.grid.count())):
                        self.grid.itemAt(i).widget().setParent(None)

                    for index, i in enumerate(l):
                        self.grid.addWidget(i, index, 0)

        except smtplib.SMTPException:

            msg = QMessageBox.critical(self, 'Error',
                                             "The message could not be sent, retry?", QMessageBox.Yes |
                                             QMessageBox.No, QMessageBox.Yes)

            if msg == QMessageBox.Yes:
                self.send_mail()


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#
#     objectt = window()
#
#
#     sys.exit(app.exec_())