import sys
from functools import partial
import copy
import pandas as pd
from PyQt5.QtCore import Qt, QDate, QSettings, QRect, QIODevice, QByteArray, \
    QDataStream, QSizeF  # , QByteArray  # QTimer, QSize,
from PyQt5.QtGui import QFont, QPainter, QColor, QIcon, QDrag, QPageSize,QPdfWriter,\
    QTextDocument  # QPainter, QPen,QBrush,
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup as bs

from re_me.res_info import *
from saload import saveLoad
from super_bc import SuperCombo, SuperButton


class PDFDocument(QPdfWriter):
    def __init__(self):
        super(PDFDocument, self).__init__()
        self.setPageSize(QPageSize(QPageSize.Letter))

