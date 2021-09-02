import sys
from PyQt5.uic import loadUi
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from queue import Queue
from pathlib import Path
from functools import partial
import gsh_opc_platform_server as gsh_server
from io_layout_map import all_button_dict
import logging
logger = logging.getLogger('EVENT')
logger_alarm = logging.getLogger('ALARM')
import qtrc

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
        self.inputs_queue = Queue()



        #-----------------------------------


        self.file_path = Path(__file__).parent.absolute()
        ui_path=self.file_path.joinpath("opc_ui.ui")
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
        self.server_worker = gsh_server.OpcServerThread(self.inputs_queue,self.file_path)
        self.server_worker.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.server_worker.run)
        self.server_worker.server_signal.connect(self.server_logger)
        self.server_worker.alarm_signal.connect(self.alarm_handler)
        self.server_worker.hmi_signal.connect(self.hmi_handler)
        self.server_worker.data_signal.connect(self.io_handler)
        logger.info("Launching Server!")
        self.server_thread.start()


        self.stackedWidget.setCurrentIndex(0)
        
        
        self.main_page_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(0))
        self.lot_entry_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(1))
        self.lot_info_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(2))
        self.event_log_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(3))
        self.show_event_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(3))
        

        self.main_motor_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(6))
        self.station_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(7))
        self.misc_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(8))
        self.vision_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(9))
        self.tower_light_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(10))
        self.life_cycle_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(11))
        self.user_area_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(12))
        self.user_access_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(13))
        self.settings_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(14))

        #IO List signals
        self.io_list_button.clicked.connect(self.io_list_page_behaviour)
        self.input_page_1_button.clicked.connect(lambda : self.input_stacked_widget.setCurrentIndex(0))
        self.input_page_2_button.clicked.connect(lambda : self.input_stacked_widget.setCurrentIndex(1))
        self.output_page_1_button.clicked.connect(lambda : self.output_stacked_widget.setCurrentIndex(0))
        self.output_page_2_button.clicked.connect(lambda : self.output_stacked_widget.setCurrentIndex(1))

        #IO module signal        
        self.io_module_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(5))
        self.io_module_button.clicked.connect(lambda :self.io_module_stacked_widget.setCurrentIndex(0))
        self.io_module_page_1_button.clicked.connect(lambda : self.io_module_stacked_widget.setCurrentIndex(0))
        self.io_module_page_2_button.clicked.connect(lambda : self.io_module_stacked_widget.setCurrentIndex(1))
        self.io_module_page_3_button.clicked.connect(lambda : self.io_module_stacked_widget.setCurrentIndex(2))
        self.io_module_page_4_button.clicked.connect(lambda : self.io_module_stacked_widget.setCurrentIndex(3))
        self.io_module_page_5_button.clicked.connect(lambda : self.io_module_stacked_widget.setCurrentIndex(4))
        self.io_module_page_6_button.clicked.connect(lambda : self.io_module_stacked_widget.setCurrentIndex(5))

  

    def io_list_page_behaviour(self):
        self.stackedWidget.setCurrentIndex(4)
        self.input_stacked_widget.setCurrentIndex(0)
        self.output_stacked_widget.setCurrentIndex(0)
        self.input_page_1_button.setChecked(True)
        self.output_page_1_button.setChecked(True)



    def on_button_clicked(self, button_group):
        print(button_group.checkedId())
        print(button_group.checkedButton().text())

                





    def server_logger(self, msg):
        logger.info(msg)

    def alarm_handler(self, msg):
        logger_alarm.info(msg)

    def hmi_handler(self,msg):
        logger.info(msg)

    def io_handler(self, data): 
        print(data)




             
    def update_io_list(self,key,data):
        for i in range(len(self.all_labels)):
            value = data[key[i+8]]
            if value[1]==1:
                self.all_labels[i].setStyleSheet("background-color: lightgreen")
            else:
                self.all_labels[i].setStyleSheet("background-color: gray")

    def send_data(self,data):
        button =  eval(f"self.{data[1][0]}")
        if button.isChecked():
            message = (data[0],1)
            self.inputs_queue.put(message)
        else:
            message = (data[0],0)
            self.inputs_queue.put(message)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    hmi = button_window()
    hmi.show()
    hmi.showMaximized()
    sys.exit(app.exec_())

