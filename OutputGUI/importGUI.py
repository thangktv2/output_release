############################# IMPORT PYQT LIBRARY ########################################
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QLabel
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QThreadPool, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtMultimedia import *

############################# IMPORT OTHER FILES #########################################
import sys
import time
from imgLib import *
from frameGUI import Ui_MainWindow
from threadGUI import *