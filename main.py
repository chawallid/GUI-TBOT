
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

clickStop = False
nextStep = False
# currentItemTable = []


class RunPlayBackThread(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    def run(self):
        global clickStop,nextStep
        count = 0
        while True:
            if not clickStop:
                if nextStep:
                    self.progress.emit(count)
                    count +=1
                    nextStep = False
            else:
                break
            time.sleep(0.1)
        self.finished.emit()
    pass

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

        self.runPlayback = False

        self.refresh = QTimer()
        self.refresh.setInterval(100)
        self.refresh.timeout.connect(self.update)
        self.refresh.start()

        # self.thread = QThread()
        # self.runPlayBackThread = RunPlayBackThread()
        # self.runPlayBackThread.moveToThread(self.thread)
        # self.thread.started.connect(self.runPlayBackThread.run)
        # self.runPlayBackThread.progress.connect(self.reportProgress)
        # self.runPlayBackThread.finished.connect(self.thread.quit)
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.thread.finished.connect(self.thread.deleteLater)

        self.serial = None
        self.is_open = False
        self.speed = 50 
        self.listPort = self.findChild(QComboBox, 'port') # Find Portlist
        self.toggleconnect = True
        self.listPlayback = ["",0,0,0,0,0,0,0,0]
        self.cuerrentData = []
        self.updateData = False
        self.runPlaybackCount  = False 
        self.lastRow = False


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

        self.X_Up = self.findChild(QLabel, 'X_Up') # Find the Image  X
        self.X_Up.clicked.connect(partial(self.sendData,data = "X+")) 
        self.X_Up.released.connect(partial(self.sendDataHome,data = "STOP")) 

        self.X_Down = self.findChild(QLabel, 'X_Down') # Find the Image  X
        self.X_Down.clicked.connect(partial(self.sendData,data = "X-")) 
        self.X_Down.released.connect(partial(self.sendDataHome,data = "STOP")) 

        self.Y_Up = self.findChild(QLabel, 'Y_Up') # Find the Image  Y
        self.Y_Up.clicked.connect(partial(self.sendData,data = "Y+")) 
        self.Y_Up.released.connect(partial(self.sendDataHome,data = "STOP")) 

        self.Y_Down = self.findChild(QLabel, 'Y_Down') # Find the Image  Y
        self.Y_Down.clicked.connect(partial(self.sendData,data = "Y-")) 
        self.Y_Down.released.connect(partial(self.sendDataHome,data = "STOP")) 

        self.Z_Up = self.findChild(QLabel, 'Z_Up') # Find the Image  Z
        self.Z_Up.clicked.connect(partial(self.sendData,data = "Z+")) 
        self.Z_Up.released.connect(partial(self.sendDataHome,data = "STOP")) 

        self.Z_Down = self.findChild(QLabel, 'Z_Down') # Find the Image  Z
        self.Z_Down.clicked.connect(partial(self.sendData,data = "Z-")) 
        self.Z_Down.released.connect(partial(self.sendDataHome,data = "STOP")) 

        self.R_Up = self.findChild(QLabel, 'R_Up') # Find the Image  R
        self.R_Up.clicked.connect(partial(self.sendData,data = "R+")) 
        self.R_Up.released.connect(partial(self.sendDataHome,data = "STOP")) 

        self.R_Down = self.findChild(QLabel, 'R_Down') # Find the Image  R
        self.R_Down.clicked.connect(partial(self.sendData,data = "R-")) 
        self.R_Down.released.connect(partial(self.sendDataHome,data = "STOP")) 

        self.slider = self.findChild(QSlider, 'speed')
        self.slider.valueChanged.connect(self.value_changed)

        self.insertRow = self.findChild(QLabel, 'insertRow')
        self.insertRow.clicked.connect(self.insertTable)

        self.deleteRow = self.findChild(QLabel, 'deleteRow')
        self.deleteRow.clicked.connect(self.deleteRowLastTable)


        self.play = self.findChild(QLabel, 'play')
        self.play.clicked.connect(self.clickRun) 

        self.pause = self.findChild(QLabel, 'pause')
        self.pause.clicked.connect(self.clickPause) 

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
        self.Emergency = self.findChild(QLabel, 'emer') # Find the Image  R
        self.Emergency.clicked.connect(self.test)
    
    def clickRun(self):
        if self.table.rowCount()>0:
            global clickStop ,nextStep
            print("runTable")
            nextStep = True
            clickStop = False
            self.lastRow = False
            self.thread = QThread()
            self.runPlayBackThread = RunPlayBackThread()
            self.runPlayBackThread.moveToThread(self.thread)
            self.thread.started.connect(self.runPlayBackThread.run)
            self.runPlayBackThread.progress.connect(self.reportProgress)
            self.runPlayBackThread.finished.connect(self.thread.quit)
            self.thread.start()
            self.runPlaybackCount = True
            self.play.setEnabled(False)
        

    def clickPause(self):
        global clickStop 
        print("pauseTable")
        self.thread.quit()
        clickStop = True
        self.play.setEnabled(True)


    def insertTable(self):
        rowCount = self.table.rowCount()
        self.table.insertRow(rowCount)
        for i in range(len(self.listPlayback)):
            self.table.setItem(rowCount,i, QTableWidgetItem(str(self.listPlayback[i])))

    def deleteRowLastTable(self):
        rowCount = self.table.rowCount()
        self.table.removeRow(rowCount-1)



    def keyPressEvent(self, event):
        print("press")

    def value_changed(self):
        self.speed = self.slider.value()

    def reportProgress(self,n):
        if self.table.rowCount()>0 and n < self.table.rowCount():
            self.cuerrentData = [self.table.item(n,1).text(),self.table.item(n,2).text(),self.table.item(n,3).text(),self.table.item(n,5).text(),self.table.item(n,6).text(),self.table.item(n,7).text(),str(n+1)]
            print("[Report] self.cuerrentData :",self.cuerrentData)
            self.updateData = True
            time.sleep(0.1)
        elif n == self.table.rowCount()+1:
            self.lastRow = True

        #     time.sleep(0.1)
    
    def sendPlayback(self,dataList):
        # if self.is_open:
        #     if len(dataList) == 7:
        data = "playback,"+str(dataList[0])+","+str(dataList[1])+","+str(dataList[2])+","+str(dataList[3])+","+str(dataList[4])+","+str(dataList[5])+","+str(self.speed)+","+str(dataList[6])+",\r"
        print("Send Playback Command :", str(data.encode()))
            # self.serial.write(data.encode())
        time.sleep(0.1)


    def sendData(self,data):
        if self.is_open:
            data = "control,"+str(data)+","+str(self.speed) +",\r"
            print("Send Data Command :", str(data.encode()))
            self.serial.write(data.encode())
        time.sleep(0.1)
        
    def sendDataHome(self,data):
        if self.is_open:
            data = "control,"+str(data)+",\r"
            print("Send Data Command :", str(data.encode()))
            self.serial.write(data.encode())
        time.sleep(0.1)

    def test(self):
        global nextStep 
        nextStep = True
        print("<< success")

    def update(self):
        global nextStep,clickStop
        rowCount = self.table.rowCount()
        nextStep = True
        if self.is_open:
            line = str(self.serial.readline(self.serial.in_waiting).decode())
            line = line.split(",")
            
            if(line[0] == 'feedback' and line[len(line)] == '\r'):
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
                if(line[7]=='success'):
                    print("<< success")
                    nextStep = True
        
        if not clickStop and len(self.cuerrentData) >0:
            # time.sleep(2.0)
            if int(self.cuerrentData[len(self.cuerrentData)-1]) <= self.table.rowCount() and not self.lastRow:
                if self.runPlaybackCount :
                    print("send 1st row >>")
                    self.sendPlayback(self.cuerrentData) #send First row in table 
                    self.runPlaybackCount = False #enable run playback count
                    self.updateData = False #enable update data 
            
                elif self.updateData : #when update data == True
                    print("send next >>")
                    self.sendPlayback(self.cuerrentData)
                    self.updateData = False
                elif int(self.cuerrentData[len(self.cuerrentData)-1]) >= self.table.rowCount():
                    self.lastRow = True
                    clickStop = True
        elif nextStep:
            self.clickPause()
            nextStep = False
                

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
            str_port = str(self.listPort.currentText())
            self.listPort.setCurrentText(str_port)
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