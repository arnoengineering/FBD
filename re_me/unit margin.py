
from PyQt5.QtCore import Qt, QRect, QRectF, QPointF, QEvent, QSize
from PyQt5.QtGui import QFont, QPainter, QColor, QPen  # QPainter, QPen,QBrush,
from PyQt5.QtWidgets import *


def POINT_TO_CM(cm):
    return cm / 28.3465058


def POINT_TO_MM(mm):
    return mm / 2.83465058


def POINT_TO_DM(dm):
    return dm / 283.465058


def POINT_TO_INCH(inch):
    return inch / 72.0


def POINT_TO_PI(pi):
    return pi / 12


def POINT_TO_DD(dd):
    return dd / 154.08124


def POINT_TO_CC(cc):
    return cc / 12.840103


def MM_TO_POINT(mm):
    return mm * 2.83465058


def CM_TO_POINT(cm):
    return cm * 28.3465058


def DM_TO_POINT(dm):
    return dm * 283.465058


def INCH_TO_POINT(inch):
    return inch * 72.0


def PI_TO_POINT(pi):
    return pi * 12


def DD_TO_POINT(dd):
    return dd * 154.08124


def CC_TO_POINT(cc):
    return cc * 12.840103


def point_o(unit, unit_a):
    if unit_a == "cm":

        ri = POINT_TO_CM(unit)
    elif unit_a == "pt" or unit_a == "px":
        ri = unit
        return ri
    elif unit_a == "mm":
        ri = POINT_TO_MM(unit)
    elif unit_a == "dm":
        ri = POINT_TO_DM(unit)
    elif unit_a == "inch":
        ri = POINT_TO_INCH(unit)
    elif unit_a == "pi":
        ri = POINT_TO_PI(unit)
    elif unit_a == "dd":
        ri = POINT_TO_DD(unit)
    elif unit_a == "cc":
        ri = POINT_TO_CC(unit)
    else:
        ri = 10

    return ri


def FopInt(datain):
    ctmp = datain

    data = ctmp.replace(" ", "").trimmed()

    points = 0
    if data.size() < 1:
        return points

    if datain == "0":
        return points

    if data.endsWith("pt") or data.endsWith("px"):
        points = data.left(data.length() - 2).toDouble()
        return points
    elif data.endsWith("cm"):

        value = data.left(data.length() - 2).toDouble()
        points = CM_TO_POINT(value)
    elif data.endsWith("em"):
        points = data.left(data.length() - 2).toDouble()
    elif data.endsWith("mm"):

        value = data.left(data.length() - 2).toDouble()
        points = MM_TO_POINT(value)
    elif data.endsWith("dm"):

        value = data.left(data.length() - 2).toDouble()
        points = DM_TO_POINT(value)
    elif data.endsWith("in"):

        value = data.left(data.length() - 2).toDouble()
        points = INCH_TO_POINT(value)
    elif data.endsWith("inch"):

        value = data.left(data.length() - 4).toDouble()
        points = INCH_TO_POINT(value)
    elif data.endsWith("pi"):

        value = data.left(data.length() - 4).toDouble()
        points = PI_TO_POINT(value)
    elif data.endsWith("dd"):

        value = data.left(data.length() - 4).toDouble()
        points = DD_TO_POINT(value)
    elif data.endsWith("cc"):

        value = data.left(data.length() - 4).toDouble()
        points = CC_TO_POINT(value)
    else:
        points = 0

    return points


class QString:
    pass


class un(QWidget):
    def __init__(self, parent, MaximumCollisionPermission=200, units="mm",
                 dimfontsize=8, Cursor_1_X=15, Cursor_2_X=600, actual_x=15):
        super().__init__()
        self.lastMove = None
        self.AreaCursor_2 = None
        self.AreaCursor_1 = None
        self.parent = parent
        self.dimfontsize = dimfontsize
        self.Cursor_1_X = Cursor_1_X
        self.Cursor_2_X = Cursor_2_X
        self.actual_x = actual_x
        self.units = units
        self.ColText = Qt.black
        self.MaximumCollisionAllowed = MaximumCollisionPermission
        self.setMaximumHeight(26)

    def paintEvent(self, event):
        self.paintScale(event)
        self.paintCursor()

    def HandleMouse(self, point):
        pointer_x = point.rx()
        if self.actual_x == pointer_x:
            return

        if self.AreaCursor_1.contains(point):
            self.Cursor_1_X = self.qBound(1., pointer_x, self.Cursor_2_X - self.MaximumCollisionAllowed - 1.0)
            self.update()

        if self.AreaCursor_2.contains(point):
            self.Cursor_2_X = self.qBound(self.Cursor_1_X + self.MaximumCollisionAllowed + 1.0, pointer_x,
                                          self.width() - 1.0)
            self.update()

        # // // / qDebug() << "### cursor pair " << Cursor_1_X << "," << Cursor_2_X
        self.emit(self.CursorMove(self.Cursor_1_X, self.Cursor_2_X))
        self.actual_x = point.rx()

    def resizeEvent(self, e):
        self.emit(self.CursorMove(self.Cursor_1_X, self.Cursor_2_X))
        return super().resizeEvent(e)

    def HandleMove(self, point):
        self.AreaCursor_1 = QRectF(self.Cursor_1_X - 5, 0, 10, self.height())
        self.AreaCursor_2 = QRectF(self.Cursor_2_X - 5, 0, 10, self.height())
        if self.AreaCursor_2.contains(point) or self.AreaCursor_1.contains(point):
            self.lastMove = point.x()
            self.HandleMouse(point)
        else:
            pointer_x = point.x()

            if pointer_x < (self.width() / 2):

                copy1 = self.Cursor_1_X
                if pointer_x < copy1:
                    self.HandleMouse(QPointF(copy1 - 1, 2))
                else:
                    self.HandleMouse(QPointF(copy1 + 1, 2))
            else:

                copy2 = self.Cursor_2_X
                if pointer_x < copy2:
                    self.HandleMouse(QPointF(copy2 - 1, 2))
                else:
                    self.HandleMouse(QPointF(copy2 + 1, 2))

    def event(self, e):
        if e.type() == QEvent.MouseMove or e.type() == QEvent.MouseMove or e.type() == QEvent.MouseButtonPress:
            self.HandleMove(e.posF())
            e.setAccepted(True)
        elif e.type() == QEvent.MouseButtonDblClick:

            if e.posF().x() < (self.width() / 2):
                self.Cursor_1_X = self.qBound(1.0, e.posF().rx(), self.Cursor_2_X - self.MaximumCollisionAllowed - 1.0)
            else:
                self.Cursor_2_X = self.qBound(self.Cursor_1_X + self.MaximumCollisionAllowed + 1.0, e.posF().rx(),
                                              self.width() - 1.0)

            self.HandleMove(e.posF())
            e.setAccepted(True)

        return super().event(e)

    def paintCursor(self):
        painter = QPainter(self)
        large = self.width()
        painter.setWindow(0, 0, large, 22)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.red)

        self.cursor(self.Cursor_1_X, 12, 5, 18)
        painter.setPen(QPen(Qt.red, 1.5))
        painter.drawLine(self.Cursor_1_X, 1, self.Cursor_1_X, 21)
        painter.drawLine(self.Cursor_2_X, 1, self.Cursor_2_X, 21)

        painter.setPen(QPen(Qt.darkRed, 1))

        rectangle_0 = QRect(self.Cursor_1_X - 5, 18, 10, 15)

        rectangle_1 = QRect(self.Cursor_1_X - 5, -10, 10, 15)

        brectangle_0 = QRect(self.Cursor_2_X - 5, 18, 10, 15)

        brectangle_1 = QRect(self.Cursor_2_X - 5, -10, 10, 15)

        painter.drawEllipse(rectangle_0)
        painter.drawEllipse(rectangle_1)

        painter.drawEllipse(brectangle_0)
        painter.drawEllipse(brectangle_1)

    def paintScale(self, units):

        large = self.width()

        self.scaleMesure = point_o(large, units)

        lineseparator_0 = FopInt(QString("10%1").arg(units))

        lineseparator_1 = lineseparator_0 / 10

        painter = QPainter(self)
        painter.setWindow(0, 0, large, 22)

        painter.setBrush(QColor("#ece4c7"))
        painter.drawRect(self.rect())
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(0, 1, large, 1)

        linessumme_0 = large / lineseparator_0

        linessumme_1 = large / lineseparator_1
        PressUnit = -1
        painter.setPen(QPen(self.ColText, 0.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for i in range(linessumme_1):
            self.strnu = QString("%1").arg(i)

            LeftPointer1 = i * lineseparator_1 - 0.4
            if 0 < PressUnit < 10:
                painter.drawLine(LeftPointer1, 5, LeftPointer1, 6)
            elif PressUnit == 5:  # todo 5
                painter.drawLine(LeftPointer1, 5, LeftPointer1, 8)

            if PressUnit == 9:
                PressUnit = -1

        painter.setPen(QPen(self.ColText, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        valFont = QFont("Arial", self.dimfontsize, QFont.Normal)
        painter.setFont(valFont)
        for i in range(linessumme_0):
            LeftPointer0 = i * lineseparator_0 - 0.5
            painter.drawLine(LeftPointer0, 5, LeftPointer0, 10)
            if i > 0:
                val = QString("%1").arg(i)
                valR = QRectF(LeftPointer0 - (lineseparator_0 / 2), 11, lineseparator_0, self.dimfontsize + 2)
                painter.drawText(valR, Qt.
                                 AlignCenter, val)

                painter.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(0, 21, large, 21)

                painter.end()
                self.minimumSizeHint()
                return QSize(100, 45)
        self.sizeHint()

        return QSize(700, 45)
