import sys
from PyQt5.uic import loadUi
from PyQt5.QtCore import  QThread,QEvent, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication
from queue import Queue
from pathlib import Path
import gsh_opc_platform_server as gsh_server
from io_layout_map import all_label_dict, all_hmi_dict
import logging
from datetime import datetime
import qtqr
import pandas as pd
import sqlite3

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
        self.database_file = "variable_history.sqlite3"
        self.io_dict = {}
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
        self.start_time = datetime.now()

        self.server_worker = gsh_server.OpcServerThread(self.input_queue,self.file_path,self.endpoint)
        self.server_worker.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.server_worker.run)
        self.server_worker.server_logger_signal.connect(self.server_logger_handler)
        self.server_worker.data_signal.connect(self.io_handler)
        self.server_worker.data_signal_2.connect(self.io_handler_init)
        self.server_worker.exit_signal.connect(self.server_close)


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
        
        #main motor module signals
        self.module_1_motor_1_button.clicked.connect(lambda: self.main_motor_control_stacked_widget.setCurrentIndex(0))
        self.module_1_motor_2_button.clicked.connect(lambda: self.main_motor_control_stacked_widget.setCurrentIndex(1))

        self.hmi_dict = dict(filter(lambda elem: ('y' in elem[1][0]) , self.label_dict.items()))
        for labels in self.hmi_dict.values():
            for items in labels:
                label_1 = items
                indicator_label_1 = eval(f"self.{label_1}")
                indicator_label_1.installEventFilter(self)

    def server_start(self):
        self.server_thread.start()

    def server_close(self):
        self.server_thread.exit()
        sys.exit()

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonDblClick:
            for labels in self.hmi_dict.values():
                for items in labels:
                    label = items
                    indicator_label = eval(f"self.{label}")
                    if source is indicator_label:
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
        self.main_motor_control_stacked_widget.setCurrentIndex(0)

    def send_data(self,label_text):
        from_hmi_label = self.hmi_label[label_text]
        current_value = self.io_dict[from_hmi_label[1]]
        current_value = 1-current_value
        self.input_queue.put((2,from_hmi_label[0], current_value))
        msg = str((from_hmi_label[0], current_value))
        self.logger.info(msg)

    def server_logger_handler(self, emit_data):
        if emit_data[0] =='log':
            msg = emit_data[1]
            self.logger.info(msg)
        elif emit_data[0] == 'alarm':
            msg = emit_data[1]
            self.logger_alarm.info(msg)

    def io_handler_init(self, data):
        for key,value in data.items():
            self.io_dict.update({key:int(value[4])})

    def io_handler(self, data):
        self.io_dict.update({data[0]:data[1]})

    def uptime(self):
        uptime = datetime.now() - self.start_time
        uptime_text = (str(uptime).split('.', 2)[0])
        self.system_uptime_label.setText(uptime_text)


    def info_updater(self):
        self.conn = sqlite3.connect(self.file_path.joinpath(self.database_file))
        variable_list=[]

        for i in range(1,13):
            try:
                variable = pd.read_sql_query(f"SELECT Value FROM '2_100{i:02d}' ORDER BY _Id DESC LIMIT 1", self.conn)
                variable_list.append(variable.iloc[0]['Value'])
            except: 
                variable_list.append(str(0))
        self.conn.close()
        self.error_count_label.setText(variable_list[0])
        self.barcode_fail_count_label.setText(variable_list[1])
        self.barcode_pass_count_label.setText(variable_list[2])
        self.total_quantity_in_label.setText(variable_list[3])
        self.total_quantity_out_label.setText(variable_list[4])
        self.total_passed_label.setText(variable_list[5])
        self.total_failed_label.setText(variable_list[6])
        self.soft_jam_label.setText(variable_list[7])
        self.hard_jam_label.setText(variable_list[8])
        self.mtbf_label.setText(variable_list[9])
        self.mtba_label.setText(variable_list[10])
        self.total_yield_label.setText(variable_list[11])

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
    hmi.server_start() #Disable comment to start server
    ms100_timer = QTimer()
    ms1000_timer = QTimer()
    ms100_timer.timeout.connect(hmi.label_updater)
    ms100_timer.timeout.connect(hmi.info_updater)
    ms1000_timer.timeout.connect(hmi.uptime)
    ms100_timer.start(100)
    ms1000_timer.start(1000)
    sys.exit(app.exec_())

