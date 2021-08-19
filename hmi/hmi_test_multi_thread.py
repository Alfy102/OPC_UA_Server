import sys
import os
from PyQt5.QtCore import QTimer
from PyQt5.uic import loadUi
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from asyncua import Client
import asyncio
from threading import Thread
from queue import Queue
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_list=[]
node_list=[]
import datetime

stop_thread=False
#from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256



class button_window(QMainWindow):

    def __init__(self):
        super(button_window,self).__init__()
        ui_path="C:/Users/aliff/Documents/OPC_UA_Server/hmi/button_test.ui"
        loadUi(ui_path,self)
        self._inputs_queue = Queue()
        

        self.pushButton_32.clicked.connect(lambda:self.client_start(self._inputs_queue))
        self.pushButton_33.clicked.connect(self.client_quit)

    def client_start(self,input_q):
        global stop_thread
        stop_thread=False
        self.client_process = Thread(target=start_client, args=(input_q,1)) #background
        self.client_process.daemon = True
        self.client_process.start()
        print("Client Started")

        

    def client_quit(self):
        global stop_thread
        stop_thread=True
        #self.client_start.join()
        print("Client Terminated")

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
        widget.setFixedWidth(600)
        widget.show()

        timer = QTimer()
        timer.timeout.connect(hmi.update_label)
        timer.start(200)
        sys.exit(app.exec_())

if __name__ == '__main__':
    user_hmi.main()


