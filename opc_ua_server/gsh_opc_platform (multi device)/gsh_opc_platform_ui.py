import sys
import os
from PyQt5.uic import loadUi
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from queue import Queue
import functools
from queue import Queue
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import gsh_platform_client as gsh_client
import gsh_opc_platform_server as gsh_server
from pathlib import Path
import logging
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
        self.device_structure={}


        self._inputs_queue = Queue()
        self._outputs_queue = Queue()
        self.file_path = Path(__file__).parent.absolute()
        ui_path=self.file_path.joinpath("button_test.ui")
        loadUi(ui_path,self)
        logTextBox_1 = QTextEditLogger(self.plainTextEdit_1)
        logTextBox_1.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(logTextBox_1)
        logger.setLevel(logging.INFO)

        logTextBox_2 = QTextEditLogger(self.plainTextEdit_2)
        logTextBox_2.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
        logger_alarm.addHandler(logTextBox_2)
        logger_alarm.setLevel(logging.INFO)

        self.server_thread=QThread()
        self.server_worker = gsh_server.OpcServerThread(self._inputs_queue,self.file_path)
        self.server_worker.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.server_worker.run)
        self.server_worker.server_signal.connect(self.server_logger)
        self.server_worker.alarm_signal.connect(self.alarm_handler)
        self.server_worker.hmi_signal.connect(self.hmi_handler)
        self.server_worker.data_signal.connect(self.io_handler)
        logger.info("Launching Server!")
        self.server_thread.start()
        self.all_labels = [self.label_1, self.label_2, self.label_3, self.label_4, self.label_5, self.label_6, self.label_7,
                            self.label_8, self.label_9, self.label_10, self.label_11, self.label_12, self.label_13, self.label_14,
                            self.label_15, self.label_16]
        self.all_pushbutton = [self.pushButton_1, self.pushButton_2, self.pushButton_3, self.pushButton_4, self.pushButton_5, self.pushButton_6, self.pushButton_7,
                            self.pushButton_8, self.pushButton_9, self.pushButton_10, self.pushButton_11, self.pushButton_12, self.pushButton_13, self.pushButton_14,
                            self.pushButton_15, self.pushButton_16]


        for push_button in self.all_pushbutton:
            push_button.clicked.connect(functools.partial(lambda: self.send_data(push_button)))
            push_button.setCheckable(True)

    def find_attributes(self, name_start):
        return [value for name, value in sorted(self.__dict__.items()) if name.startswith(name_start)]


    def server_logger(self, msg):
        logger.info(msg)

    def alarm_handler(self, msg):
        logger_alarm.info(msg)

    def hmi_handler(self,msg):
        logger.info(msg)

    def io_handler(self, data): 
        print(data)

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
             
    def get_hmi_list(self,package):
        self.hmi_dictionary = package

    def update_io_list(self,key,data):
        for i in range(len(self.all_labels)):
            value = data[key[i+8]]
            if value[1]==1:
                self.all_labels[i].setStyleSheet("background-color: lightgreen")
            else:
                self.all_labels[i].setStyleSheet("background-color: gray")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    hmi = button_window()
    widget = QStackedWidget()
    widget.addWidget(hmi)
    widget.setFixedHeight(800)
    widget.setFixedWidth(1055)
    widget.show()
    sys.exit(app.exec_())

