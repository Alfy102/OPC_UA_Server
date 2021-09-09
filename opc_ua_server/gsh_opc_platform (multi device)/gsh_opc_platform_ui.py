import sys
from PyQt5.uic import loadUi
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from queue import Queue
from pathlib import Path
import gsh_opc_platform_server as gsh_server
from io_layout_map import all_label_dict
import logging
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

        #-----------------------------------
        self.file_path = Path(__file__).parent.absolute()
        ui_path=self.file_path.joinpath("opc_ui.ui")
        loadUi(ui_path,self)


        self.stackedWidget.setCurrentIndex(0)
        self.main_page_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(0))
        self.lot_entry_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(1))
        self.lot_info_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(2))
        self.event_log_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(3))
        self.show_event_button.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(3))
        
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
        self.io_module_button.clicked.connect(self.io_module_page_behaviour)
        self.io_module_page_1_button.clicked.connect(lambda : self.io_module_stacked_widget.setCurrentIndex(0))
        self.io_module_page_2_button.clicked.connect(lambda : self.io_module_stacked_widget.setCurrentIndex(1))
        self.io_module_page_3_button.clicked.connect(lambda : self.io_module_stacked_widget.setCurrentIndex(2))
        self.io_module_page_4_button.clicked.connect(lambda : self.io_module_stacked_widget.setCurrentIndex(3))
        self.io_module_page_5_button.clicked.connect(lambda : self.io_module_stacked_widget.setCurrentIndex(4))
        self.io_module_page_6_button.clicked.connect(lambda : self.io_module_stacked_widget.setCurrentIndex(5))

        #main motor signals
        self.main_motor_button.clicked.connect(self.main_motor_page_behaviour)
        self.main_motor_page_1_button.clicked.connect(lambda: self.main_motor_station_stacked_widget.setCurrentIndex(0))
        self.main_motor_page_2_button.clicked.connect(lambda: self.main_motor_station_stacked_widget.setCurrentIndex(1))

    def io_list_page_behaviour(self):
        self.stackedWidget.setCurrentIndex(4)
        self.input_stacked_widget.setCurrentIndex(0)
        self.output_stacked_widget.setCurrentIndex(0)
        self.input_page_1_button.setChecked(True)
        self.output_page_1_button.setChecked(True)

    def io_module_page_behaviour(self):
        self.stackedWidget.setCurrentIndex(5)
        self.io_module_stacked_widget.setCurrentIndex(0)
        self.io_module_page_1_button.setChecked(True)

    def main_motor_page_behaviour(self):
        self.stackedWidget.setCurrentIndex(6)
        self.main_motor_page_1_button.setChecked(True)
        self.main_motor_station_stacked_widget.setCurrentIndex(0)


class server_start(object):   
    def __init__(self,gui):
        self.io_dict = {}
        self.hmi = button_window()
        self.label_dict =all_label_dict
        self.hmi = gui
        self.input_queue = Queue()
        self.server_thread=QThread()
        self.file_path = Path(__file__).parent.absolute()
        self.endpoint = "localhost:4840/gshopcua/server"
        self.logger = logging.getLogger('EVENT')
        self.logger_alarm = logging.getLogger('ALARM')
        logTextBox_1 = QTextEditLogger(self.hmi.plainTextEdit_1)
        logTextBox_1.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',"%d/%m/%Y %H:%M:%S%p"))
        self.logger.addHandler(logTextBox_1)
        self.logger.setLevel(logging.INFO)
        logTextBox_2 = QTextEditLogger(self.hmi.plainTextEdit_2)
        logTextBox_2.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s',"%d/%m/%Y - %H:%M:%S%p"))
        self.logger_alarm.addHandler(logTextBox_2)
        self.logger_alarm.setLevel(logging.INFO)

    def start_server(self):
        self.server_worker = gsh_server.OpcServerThread(self.input_queue,self.file_path,self.endpoint)
        self.server_worker.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.server_worker.run)
        self.server_worker.server_logger_signal.connect(self.server_logger)
        self.server_worker.hmi_signal.connect(self.user_input_handler)
        self.server_worker.data_signal.connect(self.io_handler)
        self.server_worker.alarm_signal.connect(self.alarm_handler)
        self.logger.info("Launching Server!")
        self.server_thread.start()

    def send_data(self):
        self.input_queue.put("Test")
        
    def server_logger(self, msg):
        self.logger.info(msg)

    def user_input_handler(self,msg):
        self.logger.info(msg)

    def alarm_handler(self, msg):
        self.logger_alarm.info(msg)


    def io_handler(self, data):
        self.io_dict.update({data[0]:data[1]})

    def label_updater(self):
         for key,value in self.io_dict.items():
            from_data = self.label_dict[key]
            data_value = value
            for label in from_data:
                indicator_label = eval(f"self.hmi.{label}")
                if data_value == 1:
                    if 'x' in label:
                        indicator_label.setStyleSheet("background-color: rgb(64, 255, 0);color: rgb(0, 0, 0);")
                    if 'y' in label:
                        indicator_label.setStyleSheet("background-color: rgb(255, 20, 20);color: rgb(0, 0, 0);")
                elif data_value == 0:
                    if 'x' in label:
                        indicator_label.setStyleSheet("background-color: rgb(0, 80, 0);color: rgb(200, 200, 200);")
                    if 'y' in label:
                        indicator_label.setStyleSheet("background-color: rgb(80, 0, 0);color: rgb(200, 200, 200);")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    hmi = button_window()
    hmi.show()
    hmi.showMaximized()
    server = server_start(hmi)
    server.start_server()
    timer = QTimer()
    timer.timeout.connect(server.label_updater)
    timer.start(100)
    hmi.pushButton.clicked.connect(server.send_data)
    sys.exit(app.exec_())

