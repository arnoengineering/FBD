from email.mime.multipart import MIMEMultipart
from PyQt5.Qt import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
from email.mime.text import MIMEText
import smtplib
import sys


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


class login(QDialog):
    def __init__(self, par):
        super().__init__(self)
        self.par = par
        self.email_op = {'Outlook':'office365', 'Gmail':'gmail'}

        self._init_ui()

    def _init_ui(self):
        self.layout = QGridLayout()
        self.clients = {}
        self.top_lab = QLabel('Login')
        n = 2
        m = 0

        self.layout.addWidget(self.top_lab,0,0)
        for mi, i in enumerate(self.email_op.keys()):
            self.clients[i] = QRadioButton(i + " Mail")
            self.layout.addWidget(self.clients[i], 1,mi)

        self.live = QRadioButton("Windows Live", self)
        self.gmail = QRadioButton("Google Mail", self)

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
        self.setWindowIcon(QIcon("PyMail"))
        self.setStyleSheet("font-size:15px;")

    def login(self):
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

            main = Main(self.par)
            main.show()

        except smtplib.SMTPException:
            msg = QMessageBox.critical(self, 'login Failed',
                                             "Username/Password combination incorrect", QMessageBox.Ok |
                                             QMessageBox.Retry, QMessageBox.Ok)

            if msg == QMessageBox.Retry:
                self.login()


class Main(QMainWindow):

    def __init__(self,par=None):
        super().__init__(self)
        self.par = par
        self._init_ui()

    def _init_ui(self):
        self.grid = QGridLayout()
        doc_ls = self.par.doc_data.loc[self.par.doc_data['Doc'] == doc, 'Email']

        self.labels = {}
        self.lab_ls = ['Send', 'From', 'To', 'Subject']

        for i in self.lab_ls:
            self.labels[i] = QLabel(i)
            # add wigit
            # add widit lined edit unless body or  send


        self.send = QPushButton("S", self)
        self.send.clicked.connect(self.Send)

        self.from_label = QLabel("", self)

        self.to_label = QLabel("", self)

        self.subject_label = QLabel("", self)

        self.from_addr = QLineEdit(self)
        self.from_addr.setText(user)

        self.to_addr = QLineEdit(self)
        self.to_addr.setPlaceholderText("example@gmail.com")  # todo option for file send, csv, excel, ical

        self.subject = QLineEdit(self)
        self.subject.setPlaceholderText("I got an offer you can't refuse")

        self.image = QPushButton("Attach file", self)
        self.image.clicked.connect(self.Image)

        self.text = QTextEdit(self)

        centralwidget = QWidget()



        self.grid.addWidget(self.from_label, 0, 0)
        self.grid.addWidget(self.from_addr, 1, 0)
        self.grid.addWidget(self.to_label, 2, 0)
        self.grid.addWidget(self.to_addr, 3, 0)
        self.grid.addWidget(self.subject_label, 4, 0)
        self.grid.addWidget(self.subject, 5, 0)
        self.grid.addWidget(self.image, 6, 0)
        self.grid.addWidget(self.text, 8, 0)
        self.grid.addWidget(self.send, 9, 0)

        centralwidget.setLayout(self.grid)

        self.setCentralWidget(centralwidget)

        # ---------Window settings --------------------------------

        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle("PyMail")
        self.setWindowIcon(QIcon("PyMail"))
        self.setStyleSheet("font-size:15px")

    def ContextMenu(self):
        global sender
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

        pos -= 1

        ind = labels.index(sender)

        attachments.remove(attachments[ind])

        labels.remove(sender)

        sender.setParent(None)

    def Image(self):
        global path
        global attachments
        global labels
        global filetype
        global l

        path = QFileDialog.getOpenFileName(self, "Attach file", "/home/")

        if path:

            attachments.append(path)

            filetype = path[path.rindex(".") + 1:]

            if filetype == "png":
                pic = QPixmap(path)
            else:
                if filetype + ".png" in os.listdir("C:/Python32/python/pyqt/PyMail/48px/"):
                    print("normal")
                    pic = QPixmap("C:/Python32/python/pyqt/PyMail/48px/" + filetype + ".png")
                else:
                    print("weird")
                    pic = QPixmap("C:/Python32/python/pyqt/PyMail/48px/_blank.png")

            a = QLabel(path, self)
            a.setScaledContents(True)
            a.setFixedSize(50, 50)
            a.setPixmap(pic)
            a.setToolTip(path)

            a.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            a.customContextMenuRequested.connect(self.ContextMenu)

            labels.append(a)

            print(attachments, labels)

            pos = len(attachments)

            l = [self.from_label, self.from_addr, self.to_label, self.to_addr, self.subject_label, self.subject,
                 self.image, self.text, self.send]

            for index, i in enumerate(l):
                self.grid.addWidget(i, index, 0, 1, pos + 1)

                if i in l[-2:]:
                    self.grid.addWidget(i, index + 1, 0, 1, pos + 1)

            self.grid.addWidget(a, 7, pos - 1)
            self.setGeometry(300, 300, 500, 550)

    def Send(self):
        global server
        global attachments
        global filetype
        global l

        fromaddr = self.from_addr.text()
        toaddr = self.to_addr.text()
        subject = self.subject.text()

        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = subject
        msg['Date'] = formatdate()

        body = self.text.toPlainText()
        msg.attach(MIMEText(body, "plain"))

        if attachments:
            for file in attachments:

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
                    att = MIMEBase(maintype, subtype)
                    att.set_payload(fp.read())
                    fp.close()
                    encoders.encode_base64(att)

                att.add_header('Content-Disposition', 'attachment', filename=file[file.rindex("/"):])
                msg.attach(att)

        text = msg.as_string()

        try:
            server.sendmail(fromaddr, toaddr, text)

            msg = QMessageBox.information(self, 'Message sent',
                                                "Message sent successfully, clear everything?", QMessageBox.Yes |
                                                QMessageBox.No, QMessageBox.Yes)

            if msg == QMessageBox.Yes:
                self.to_addr.clear()
                self.subject.clear()
                self.text.clear()

                if attachments:
                    for i in attachments:
                        attachments.remove(i)

                    for i in reversed(range(self.grid.count())):
                        self.grid.itemAt(i).widget().setParent(None)

                    for index, i in enumerate(l):
                        self.grid.addWidget(i, index, 0)

        except smtplib.SMTPException:

            msg = QMessageBox.critical(self, 'Error',
                                             "The message could not be sent, retry?", QMessageBox.Yes |
                                             QMessageBox.No, QMessageBox.Yes)

            if msg == QMessageBox.Yes:
                self.Send()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    objectt = window()


    sys.exit(app.exec_())