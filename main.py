
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


from PyQt5 import uic
from functools import partial
import serial 
from serial.tools import list_ports

import sys
import time
import glob

class QLabel_alterada(QLabel):
    clicked=pyqtSignal()
    released=pyqtSignal()
    def mousePressEvent(self, ev):
        self.clicked.emit()
    def mouseReleaseEvent(self, ev):
        self.released.emit()

class UI(QMainWindow):
    
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("mainUI.ui", self)

        self.refresh = QTimer()
        self.refresh.setInterval(100)
        self.refresh.timeout.connect(self.update)
        self.refresh.start()

        self.serial = None
        self.is_open = False
        self.speed = 50 
        self.listPort = self.findChild(QComboBox, 'port') # Find Portlist
        self.toggleconnect = True

        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        for i in range(len(ports)):
            self.listPort.addItem(str(ports[i]))
        self.tmp = list(serial.tools.list_ports.comports())
        for p in self.tmp : print(p)

        self.btnConnect = self.findChild(QLabel, 'btnconnect') # Find the btnconnect
        self.btnConnect.clicked.connect(self.connectPort) 

        self.X = self.findChild(QLineEdit, 'X_value')
        self.X.setText("15")
        self.Y = self.findChild(QLineEdit, 'Y_value')
        self.Y.setText("15")
        self.Z = self.findChild(QLineEdit, 'Z_value')
        self.Z.setText("15")
        self.R = self.findChild(QLineEdit, 'R_value')
        self.R.setText("15")

        self.J1 = self.findChild(QLineEdit, 'J1_value')
        self.J1.setText("15")
        self.J2 = self.findChild(QLineEdit, 'J2_value')
        self.J2.setText("15")
        self.J3 = self.findChild(QLineEdit, 'J3_value')
        self.J3.setText("15")
        self.J4 = self.findChild(QLineEdit, 'J4_value')
        self.J4.setText("15")

        self.btnHome = self.findChild(QLabel, 'btnHome') # Find the Image J+
        self.btnHome.clicked.connect(partial(self.sendDataHome,data = "HOME")) 
        self.btnHome.released.connect(partial(self.sendDataHome,data = "STOP")) 


        self.J1_Up = self.findChild(QLabel, 'J1_Up') # Find the Image J+
        self.J1_Up.clicked.connect(partial(self.sendData,data = "J1+")) 
        self.J1_Up.released.connect(partial(self.sendDataHome,data = "STOP")) 

        self.J1_Down = self.findChild(QLabel, 'J1_Down') # Find the Image J-
        self.J1_Down.clicked.connect(partial(self.sendData,data = "J1-"))
        self.J1_Down.released.connect(partial(self.sendDataHome,data = "STOP")) 
 
        # self.J1_Down.pressed.connect(partial(self.sendData,data = "J1-TT")) 
        # self.J1_Down.released.connect(partial(self.sendData,data = "J1-GG")) 

        self.J2_Up = self.findChild(QLabel, 'J2_Up') # Find the Image J+
        self.J2_Up.clicked.connect(partial(self.sendData,data = "J2+"))
        self.J2_Up.released.connect(partial(self.sendDataHome,data = "STOP")) 
 
        self.J2_Down = self.findChild(QLabel, 'J2_Down') # Find the Image J-
        self.J2_Down.clicked.connect(partial(self.sendData,data = "J2-")) 
        self.J2_Down.released.connect(partial(self.sendDataHome,data = "STOP")) 


        self.J3_Up = self.findChild(QLabel, 'J3_Up') # Find the Image J+
        self.J3_Up.clicked.connect(partial(self.sendData,data = "J3+"))
        self.J3_Up.released.connect(partial(self.sendDataHome,data = "STOP")) 
 
        self.J3_Down = self.findChild(QLabel, 'J3_Down') # Find the Image J-
        self.J3_Down.clicked.connect(partial(self.sendData,data = "J3-")) 
        self.J3_Down.released.connect(partial(self.sendDataHome,data = "STOP")) 


        self.J4_Up = self.findChild(QLabel, 'J4_Up') # Find the Image J+
        self.J4_Up.clicked.connect(partial(self.sendData,data = "J4+")) 
        self.J4_Up.released.connect(partial(self.sendDataHome,data = "STOP")) 

        self.J4_Down = self.findChild(QLabel, 'J4_Down') # Find the Image J-
        self.J4_Down.clicked.connect(partial(self.sendData,data = "J4-")) 
        self.J4_Down.released.connect(partial(self.sendDataHome,data = "STOP")) 

        self.slider = self.findChild(QSlider, 'speed')
        self.slider.valueChanged.connect(self.value_changed)


        self.joy1 = self.findChild(QGroupBox, 'JOY1') # Find the Image J+
        self.joy1.setStyleSheet("QGroupBox {border-image: url(./img/GG_2.png);} ")

        self.joy2 = self.findChild(QGroupBox, 'JOY2') # Find the Image J+
        self.joy2.setStyleSheet("QGroupBox {border-image: url(./img/GG_2.png);} ")

        self.joy3 = self.findChild(QGroupBox, 'JOY3') # Find the Image J+
        self.joy3.setStyleSheet("QGroupBox {border-image: url(./img/GG_2.png);} ")

        self.joy4 = self.findChild(QGroupBox, 'JOY4') # Find the Image J+
        self.joy4.setStyleSheet("QGroupBox {border-image: url(./img/GG_2.png);} ")

        self.slider.setValue(50)

    def keyPressEvent(self, event):
        if()
        print("press")
        # return super().keyPressEvent(a0)
    def value_changed(self):
        self.speed = self.slider.value()

    def sendData(self,data):
        if self.is_open:
            data = str(data)+","+str(self.speed) +",\r"
            print("Send Data Command :", str(data.encode()))
            self.serial.write(data.encode())
        time.sleep(0.1)
        
    def sendDataHome(self,data):
        if self.is_open:
            data = str(data)+",\r"
            print("Send Data Command :", str(data.encode()))
            self.serial.write(data.encode())
        time.sleep(0.1)

    def test(self):
        print("TEST")

    def update(self):
        if not(self.toggleconnect):
            self.listPort.clear()
            if sys.platform.startswith('win'):
                ports = ['COM%s' % (i + 1) for i in range(256)]
            elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                ports = glob.glob('/dev/tty[A-Za-z]*')
            elif sys.platform.startswith('darwin'):
                ports = glob.glob('/dev/tty.*')
            else:
                raise EnvironmentError('Unsupported platform')

            for i in range(len(ports)):
                self.listPort.addItem(str(ports[i]))

        

    def connectPort(self):
        if self.toggleconnect:
            for ports in self.tmp:
                ports = str(ports)
                # print("TTTT",ports)
            # if ports.find("uart") ==False :
        self.serial = serial.Serial(str(self.listPort.currentText()),
                                baudrate=9600, 
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS,
                                timeout=1)
        self.is_open = self.serial.isOpen()
        if self.is_open:
            self.toggleconnect = False
            pixmap = QPixmap('./img/disconnect_template.png')
            self.btnConnect.setPixmap(pixmap)
            self.listPort.setEnabled(False)
        else:
            self.serial.close()
            self.is_open = self.serial.isOpen() 
            self.toggleconnect = True
            self.listPort.setEnabled(True)
            pixmap = QPixmap('./img/connect.png')
            self.btnConnect.setPixmap(pixmap)

app = QApplication(sys.argv)
window = UI()
window.show()
sys.exit(app.exec_())