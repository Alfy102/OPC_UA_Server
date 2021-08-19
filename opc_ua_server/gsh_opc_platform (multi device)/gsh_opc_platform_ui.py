import sys
import os
from PyQt5.QtCore import QTimer
from PyQt5.uic import loadUi
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from threading import Thread
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
    def __init__(self, parent,textEdit):
        super().__init__()
        self.widget = textEdit
        #self.widget.setCenterOnScroll(True)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
        #self.widget.ensureCursorVisible()

class QTextEditLoggerAlarm(logging.Handler):
    def __init__(self, parent,textEdit):
        super().__init__()
        self.widget = textEdit
        #self.widget.setCenterOnScroll(True)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
        #self.widget.ensureCursorVisible()


class button_window(QMainWindow):

    def __init__(self):
        super(button_window,self).__init__()
        ui_path="C:/Users/aliff/Documents/OPC_UA_Server/opc_ua_server/gsh_opc_platform (multi device)/button_test.ui"
        loadUi(ui_path,self)
        self._inputs_queue = Queue()
        input_q = self._inputs_queue
        logTextBox_1 = QTextEditLogger(self,self.plainTextEdit_1)
        logTextBox_1.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(logTextBox_1)
        logger.setLevel(logging.INFO)

        logTextBox_2 = QTextEditLogger(self,self.plainTextEdit_2)
        logTextBox_2.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
        logger_alarm.addHandler(logTextBox_2)
        logger_alarm.setLevel(logging.INFO)




        self.server_process = Thread(target=gsh_server.start_opc_server)#,args=(input_q,2))#background
        self.server_process.daemon = True
        logger.info("Launching OPC Server!")

        #self.client_process = Thread(target=gsh_client.start_client, args=(input_q,1)) #background
        #self.client_process.daemon = True
        
        logger.info("Launching OPC Client")

        time.sleep(2)
        self.server_process.start()
        #self.client_process.start()

    def send_data(self,button_number):
        Relay = button_number.text()
        if button_number.isChecked():
            message = [Relay,1]
            self._inputs_queue.put(message)
        else:
            message = [Relay,0]
            self._inputs_queue.put(message)

    def update_label(self):
        if len(data_list)>15: #to update with better implementation
            user_hmi.hmi.label_1.setText(str(bool(data_list[0])))
            user_hmi.hmi.label_2.setText(str(bool(data_list[1])))
            user_hmi.hmi.label_3.setText(str(bool(data_list[2])))
            user_hmi.hmi.label_4.setText(str(bool(data_list[3])))
            user_hmi.hmi.label_5.setText(str(bool(data_list[4])))
            user_hmi.hmi.label_6.setText(str(bool(data_list[5])))
            user_hmi.hmi.label_7.setText(str(bool(data_list[6])))
            user_hmi. hmi.label_8.setText(str(bool(data_list[7])))
            user_hmi.hmi.label_9.setText(str(bool(data_list[8])))
            user_hmi.hmi.label_10.setText(str(bool(data_list[9])))
            user_hmi.hmi.label_11.setText(str(bool(data_list[10])))
            user_hmi.hmi.label_12.setText(str(bool(data_list[11])))
            user_hmi.hmi.label_13.setText(str(bool(data_list[12])))
            user_hmi.hmi.label_14.setText(str(bool(data_list[13])))
            user_hmi.hmi.label_15.setText(str(bool(data_list[14])))
            user_hmi.hmi.label_16.setText(str(bool(data_list[15])))

            
class user_hmi():
    def main():
        app = QApplication(sys.argv)
        hmi = button_window()
        widget = QStackedWidget()
        widget.addWidget(hmi)
        widget.setFixedHeight(800)
        widget.setFixedWidth(1055)
        widget.show()

        timer = QTimer()
        timer.timeout.connect(hmi.update_label)
        timer.start(200)
        sys.exit(app.exec_())

if __name__ == '__main__':
    user_hmi.main()


