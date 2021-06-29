
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
        self.listPlayback = ["",0,0,0,0,0,0,0,0]
        self.checkStep = False

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
        self.X.setText("0")
        self.Y = self.findChild(QLineEdit, 'Y_value')
        self.Y.setText("0")
        self.Z = self.findChild(QLineEdit, 'Z_value')
        self.Z.setText("0")
        self.R = self.findChild(QLineEdit, 'R_value')
        self.R.setText("0")

        self.J1 = self.findChild(QLineEdit, 'J1_value')
        self.J1.setText("0")
        self.J2 = self.findChild(QLineEdit, 'J2_value')
        self.J2.setText("0")
        self.J3 = self.findChild(QLineEdit, 'J3_value')
        self.J3.setText("0")
        self.J4 = self.findChild(QLineEdit, 'J4_value')
        self.J4.setText("0")

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

        self.insertRow = self.findChild(QLabel, 'insertRow')
        self.insertRow.clicked.connect(self.insertTable)

        self.play = self.findChild(QLabel, 'play')
        self.play.clicked.connect(self.runPlayback) 

        self.pause = self.findChild(QLabel, 'pause')
        self.pause.clicked.connect(self.pausePlayback) 

        self.deleteRow = self.findChild(QLabel, 'deleteRow')

        self.joy1 = self.findChild(QGroupBox, 'JOY1') # Find the Image J+
        self.joy1.setStyleSheet("QGroupBox {border-image: url(./img/GG_2.png);} ")

        self.joy2 = self.findChild(QGroupBox, 'JOY2') # Find the Image J+
        self.joy2.setStyleSheet("QGroupBox {border-image: url(./img/GG_2.png);} ")

        self.joy3 = self.findChild(QGroupBox, 'JOY3') # Find the Image J+
        self.joy3.setStyleSheet("QGroupBox {border-image: url(./img/GG_2.png);} ")

        self.joy4 = self.findChild(QGroupBox, 'JOY4') # Find the Image J+
        self.joy4.setStyleSheet("QGroupBox {border-image: url(./img/GG_2.png);} ")

        self.slider.setValue(50)

        self.table = self.findChild(QTableWidget, 'tableWidget')
        # self.table.clear()
        self.table.setRowCount(0)
    def runPlayback(self):
        print("runPlayback")
        rowCount = self.table.rowCount()
        count = 0
        while True:
            if(rowCount >0):
                # print(self.table.item(count,1).text(),self.table.item(count,2).text(),self.table.item(count,3).text(),self.table.item(count,4).text(),self.table.item(count,5).text(),self.table.item(count,6).text(),self.table.item(count,7).text(),self.table.item(count,8).text(),count+1)
                # if self.checkStep:
                data = [self.table.item(count,1).text(),self.table.item(count,2).text(),self.table.item(count,3).text(),self.table.item(count,5).text(),self.table.item(count,6).text(),self.table.item(count,7).text(),str(count+1)]
                self.sendPlayback(data)
                count += 1
                if count == rowCount:
                    break

    def pausePlayback(self):
        print("pausePlayback")
        pass

    def insertTable(self):
        rowCount = self.table.rowCount()
        self.table.insertRow(rowCount)
        # self.listPlayback = [0,0,0,0,0,0,0,0]
        for i in range(len(self.listPlayback)):
            self.table.setItem(rowCount,i, QTableWidgetItem(str(self.listPlayback[i])))

        pass

    def keyPressEvent(self, event):
        print("press")
        # return super().keyPressEvent(a0)
    def value_changed(self):
        self.speed = self.slider.value()
    
    def sendPlayback(self,dataList):
        # if self.is_open:
        if len(dataList) == 7:
            data = "playback,"+str(dataList[0])+","+str(dataList[1])+","+str(dataList[2])+","+str(dataList[3])+","+str(dataList[4])+","+str(dataList[5])+","+str(self.speed)+","+str(dataList[6])+",\r"
        print("Send Playback Command :", str(data.encode()))
            # self.serial.write(data.encode())
        time.sleep(0.1)

    def sendData(self,data):
        if self.is_open:
            data = "control"+str(data)+","+str(self.speed) +",\r"
            print("Send Data Command :", str(data.encode()))
            self.serial.write(data.encode())
        time.sleep(0.1)
        
    def sendDataHome(self,data):
        if self.is_open:
            data = "control"+str(data)+",\r"
            print("Send Data Command :", str(data.encode()))
            self.serial.write(data.encode())
        time.sleep(0.1)

    def test(self):
        print("TEST")

    def update(self):
        if self.is_open:
            line = str(self.serial.readline(self.serial.in_waiting).decode())
            line = line.split(",")
            if(line[0] == 'feedback' and line[-1] == '\r'):
                self.X.setText(line[1])
                self.Y.setText(line[2])
                self.Z.setText(line[3])
                self.J1.setText(line[4])
                self.J2.setText(line[5])
                self.J3.setText(line[6])
                self.listPlayback[1] = line[1]
                self.listPlayback[2] = line[2]
                self.listPlayback[3] = line[3]
                self.listPlayback[5] = line[4]
                self.listPlayback[6] = line[5]
                self.listPlayback[7] = line[6]
                if(line[7]=='succes'):
                    self.checkStep = True
                else:
                    self.checkStep = False

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
        self.serial = serial.Serial(str(self.listPort.currentText()),
                                baudrate=115200, 
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS,
                                timeout=1)
        self.is_open = self.serial.isOpen()
        if self.is_open:
            self.toggleconnect = False
            pixmap = QPixmap('./img/disconnect_template.png')
            self.btnConnect.setPixmap(pixmap)
            self.listPort.currentText(str(self.listPort.currentText()))
            self.listPort.setEnabled(False)
        else:
            self.serial.close()
            self.is_open = False
            self.toggleconnect = True
            self.listPort.setEnabled(True)
            pixmap = QPixmap('./img/connect.png')
            self.btnConnect.setPixmap(pixmap)

app = QApplication(sys.argv)
window = UI()
window.show()
sys.exit(app.exec_())