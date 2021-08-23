import sys
import os
from PyQt5.QtCore import QCoreApplication,QTimer
from PyQt5.uic import loadUi
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from queue import Queue

from queue import Queue
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import gsh_platform_client as gsh_client
import gsh_opc_platform_server as gsh_server
data_list=[]
import logging
import time
#from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256

logger = logging.getLogger('EVENT')
logger_alarm = logging.getLogger('ALARM')



class QTextEditLogger(logging.Handler):
    def __init__(self,textEdit):
        super(QTextEditLogger, self).__init__()
        self.widget = textEdit
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

class QTextEditLoggerAlarm(logging.Handler):
    def __init__(self,textEdit):
        super(QTextEditLoggerAlarm, self).__init__()
        self.widget = textEdit
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class button_window(QMainWindow):

    def __init__(self):
        super(button_window,self).__init__()

        ui_path="C:/Users/aliff/Documents/OPC_UA_Server/opc_ua_server/gsh_opc_platform (multi device)/button_test.ui"
        loadUi(ui_path,self)
        self._inputs_queue = Queue()
        self._outputs_queue = Queue()
        input_q = self._inputs_queue
        output_q = self._outputs_queue
        
        logTextBox_1 = QTextEditLogger(self.plainTextEdit_1)
        logTextBox_1.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(logTextBox_1)
        logger.setLevel(logging.INFO)

        logTextBox_2 = QTextEditLogger(self.plainTextEdit_2)
        logTextBox_2.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
        logger_alarm.addHandler(logTextBox_2)
        logger_alarm.setLevel(logging.INFO)

        self.server_thread=QThread()
        self.server_worker = gsh_server.opc_server_thread()
        self.server_worker.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.server_worker.run)
        self.server_worker.server_signal.connect(self.server_logger_bridge)
        #self.server_worker.server_signal.connect(self.alarm_logger_bridge)

        self.client_thread=QThread()
        self.queue = Queue()
        self.client_worker = gsh_client.opc_client_thread(input_q)
        self.client_worker.moveToThread(self.client_thread)
        self.client_thread.started.connect(self.client_worker.run)
        self.client_worker.client_signal.connect(self.client_logger_bridge)
        self.client_worker.scan_signal.connect(self.client_scan_bridge)
        self.client_worker.alarm_signal.connect(self.alarm_logger_bridge)

        logger.info("Launching Server!")
        self.server_thread.start()
        logger.info("Launching Client!")
        self.client_thread.start()

        self.pushButton_1.clicked.connect(lambda: self.send_data(self.pushButton_1))
        self.pushButton_1.setCheckable(True)


    def server_logger_bridge(self, msg):
        logger.info(msg)

    def client_scan_bridge(self, package_data):
        print("package_data received")
    
    def client_logger_bridge(self, msg):
        logger.info(msg)

    def alarm_logger_bridge(self, msg):
        alert_code = f"Alarm raised with code {msg}"
        logger_alarm.info(alert_code)


    def client_start(self):
        client_thread = gsh_client.opc_client_thread(self)
        client_thread.start()

    def send_data(self,button_number):
        Relay = button_number.text()
        if button_number.isChecked():
            message = [Relay,1]
            self._inputs_queue.put(message)
            logger.info(message) #HMI input logger info
        else:
            message = [Relay,0]
            self._inputs_queue.put(message)
            logger.info(message) #HMI input logger info
             
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    hmi = button_window()
    widget = QStackedWidget()
    widget.addWidget(hmi)
    widget.setFixedHeight(800)
    widget.setFixedWidth(1055)
    widget.show()
    sys.exit(app.exec_())

