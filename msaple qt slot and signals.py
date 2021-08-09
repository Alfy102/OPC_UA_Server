import sys
import serial


if sys.version > "3":
    import binascii
import minimalmodbus

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(632, 449)
        self.EXIT_btn = QtWidgets.QPushButton(Dialog)
        self.EXIT_btn.setGeometry(QtCore.QRect(530, 410, 75, 23))
        self.EXIT_btn.setObjectName("EXIT_btn")
        self.ComChoice = QtWidgets.QSpinBox(Dialog)
        self.ComChoice.setGeometry(QtCore.QRect(470, 26, 42, 22))
        self.ComChoice.setObjectName("ComChoice")
        self.Choice_label = QtWidgets.QLabel(Dialog)
        self.Choice_label.setGeometry(QtCore.QRect(506, 20, 101, 20))
        self.Choice_label.setObjectName("Choice_label")
        self.ComChoice_2 = QtWidgets.QSpinBox(Dialog)
        self.ComChoice_2.setGeometry(QtCore.QRect(470, 86, 42, 22))
        self.ComChoice_2.setObjectName("ComChoice_2")
        self.Meter_Id = QtWidgets.QLabel(Dialog)
        self.Meter_Id.setGeometry(QtCore.QRect(506, 80, 101, 20))
        self.Meter_Id.setObjectName("Meter_Id")
        self.Volt = QtWidgets.QLabel(Dialog)
        self.Volt.setGeometry(QtCore.QRect(28, 20, 60, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.Volt.setFont(font)
        self.Volt.setObjectName("Volt")
        self.lcdNumber = QtWidgets.QLCDNumber(Dialog)
        self.lcdNumber.setGeometry(QtCore.QRect(30, 50, 64, 23))
        self.lcdNumber.setObjectName("lcdNumber")
        self.lcdNumber_2 = QtWidgets.QLCDNumber(Dialog)
        self.lcdNumber_2.setGeometry(QtCore.QRect(30, 110, 64, 23))
        self.lcdNumber_2.setObjectName("lcdNumber_2")
        self.lcdNumber_3 = QtWidgets.QLCDNumber(Dialog)
        self.lcdNumber_3.setGeometry(QtCore.QRect(30, 80, 64, 23))
        self.lcdNumber_3.setObjectName("lcdNumber_3")
        self.Connect_Button = QtWidgets.QPushButton(Dialog)
        self.Connect_Button.setGeometry(QtCore.QRect(532, 160, 75, 23))
        self.Connect_Button.setObjectName("Connect_Button")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.EXIT_btn.setText(_translate("Dialog", "Exit"))
        self.Choice_label.setText(_translate("Dialog", "בחר יציאת COM"))
        self.Meter_Id.setText(_translate("Dialog", "כתובת מונה"))
        self.Volt.setText(_translate("Dialog", "מתחים"))
        self.Connect_Button.setText(_translate("Dialog", "התחבר"))


class Dialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.setupUi(self)
        self.Connect_Button.clicked.connect(self.start)
        self.EXIT_btn.clicked.connect(self.stop)

        self.m_thread = QtCore.QThread(self)
        self.m_thread.start()

        self.m_modbus_worker = ModbusWorker()
        self.m_modbus_worker.dataChanged.connect(self.on_dataChanged)
        self.m_modbus_worker.moveToThread(self.m_thread)

    @QtCore.pyqtSlot()
    def start(self):
        QtCore.QTimer.singleShot(0, self.m_modbus_worker.do_work)

    @QtCore.pyqtSlot()
    def stop(self):
        self.m_thread.requestInterruption()

    @QtCore.pyqtSlot(list)
    def on_dataChanged(self, values):
        for w, value in zip((self.lcdNumber, self.lcdNumber_2, self.lcdNumber_3), values):
            w.display(value)

    def closeEvent(self, event):
        super(Dialog, self).closeEvent(event)
        self.stop()
        self.m_thread.quit()
        self.m_thread.wait()


class ModbusWorker(QtCore.QObject):
    dataChanged = QtCore.pyqtSignal(list)

    @QtCore.pyqtSlot()
    def do_work(self):
        instrument = minimalmodbus.Instrument("com4", 1)  # port name, slave adress
        instrument.debug = True  # debug
        instrument.serial.baudrate = 19200  # Baud
        instrument.serial.bytesize = 8
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 0.05  # seconds
        instrument.mode = minimalmodbus.MODE_RTU  # rtu or ascii mode
        clear_buffers_before_each_transaction = "True"  # clear Buffers
        BYTEORDER_BIG = "True"

        while not QtCore.QThread.currentThread().isInterruptionRequested():
            data = [instrument.read_register(i + 1, 2, 3) for i in range(3)]
            self.dataChanged.emit(data)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = Dialog()
    w.show()
    sys.exit(app.exec_())