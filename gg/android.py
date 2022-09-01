from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtSensors import *
from PyQt5.QtPositioning import *
# lookQtBluetooth QtNetwork, nfc


class cameraApp(QCamera):
    def __init__(self):
        super.__init__()