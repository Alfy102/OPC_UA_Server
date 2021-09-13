import sys
from PyQt5.uic import loadUi
from PyQt5.QtCore import  QThread,QEvent, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication
from queue import Queue
from pathlib import Path
import gsh_opc_platform_server as gsh_server
from io_layout_map import all_label_dict, all_hmi_dict
import logging
from datetime import timedelta, datetime
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
        self.file_path = Path(__file__).parent.absolute()
        ui_path=self.file_path.joinpath("opc_ui.ui")
        loadUi(ui_path,self)
        
        self.io_dict = {}
        #self.hmi = button_window()
        self.hmi_label = all_hmi_dict
        self.label_dict =all_label_dict
        self.input_queue = Queue()
        self.server_thread=QThread()
        self.file_path = Path(__file__).parent.absolute()
        self.endpoint = "localhost:4840/gshopcua/server"
        self.logger = logging.getLogger('EVENT')
        self.logger_alarm = logging.getLogger('ALARM')
        logTextBox_1 = QTextEditLogger(self.plainTextEdit_1)
        logTextBox_1.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',"%d/%m/%Y %H:%M:%S%p"))
        self.logger.addHandler(logTextBox_1)
        self.logger.setLevel(logging.INFO)
        logTextBox_2 = QTextEditLogger(self.plainTextEdit_2)
        logTextBox_2.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s',"%d/%m/%Y - %H:%M:%S%p"))
        self.logger_alarm.addHandler(logTextBox_2)
        self.logger_alarm.setLevel(logging.INFO)

        self.server_worker = gsh_server.OpcServerThread(self.input_queue,self.file_path,self.endpoint)
        self.server_worker.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.server_worker.run)
        self.server_worker.server_logger_signal.connect(self.server_logger)
        self.server_worker.hmi_signal.connect(self.user_input_handler)
        self.server_worker.data_signal.connect(self.io_handler)
        self.server_worker.data_signal_2.connect(self.io_handler_init)
        self.server_worker.alarm_signal.connect(self.alarm_handler)
        self.logger.info("Launching Server!")
        

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
        
        self.hmi_dict = dict(filter(lambda elem: ('y' in elem[1][0]) , self.label_dict.items()))
        for labels in self.hmi_dict.values():
            label_1 = labels[0]
            indicator_label_1 = eval(f"self.{label_1}")
            indicator_label_1.installEventFilter(self)

        self.server_thread.start()

    def eventFilter(self, source, event):
        for labels in self.hmi_dict.values():
            label = labels[0]
            indicator_label = eval(f"self.{label}")
            if (event.type() == QEvent.MouseButtonDblClick and source is indicator_label):
                msg = source.text()
                self.send_data(msg)
        return super(button_window, self).eventFilter(source, event)

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

    def send_data(self,label_text):
        from_hmi_label = self.hmi_label[label_text]
        current_value = self.io_dict[from_hmi_label[1]]
        current_value = 1-current_value
        self.input_queue.put((2,from_hmi_label[0], current_value))
        
    def server_logger(self, msg):
        self.logger.info(msg)

    def user_input_handler(self,msg):
        self.logger.info(msg)

    def alarm_handler(self, msg):
        self.logger_alarm.info(msg)
    
    def io_handler_init(self, data):
        for key,value in data.items():
            self.io_dict.update({key:int(value[4])})

    def io_handler(self, data):
        self.io_dict.update({data[0]:data[1]})

    def history_db_updater(self,data):
        print(data)

    def label_updater(self):
         for key,value in self.io_dict.items():
            from_data = self.label_dict[key]
            data_value = value
            for label in from_data:
                indicator_label = eval(f"self.{label}")
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
    current_time = datetime.now()#.replace(microsecond=0, second=0, minute=0)
    added_time = current_time + timedelta(minutes=1)
    label_refresh_timer = QTimer()
    label_refresh_timer.timeout.connect(hmi.label_updater)
    label_refresh_timer.start(100)
    sys.exit(app.exec_())

