import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import  QThread,QEvent
from PyQt5.QtWidgets import QMainWindow
from queue import Queue
from pathlib import Path
import gsh_opc_platform_server as gsh_server
import gsh_opc_platform_client as gsh_client
from gsh_opc_platform_gui import Ui_MainWindow
from io_layout_map import node_structure
from datetime import datetime
import time
from multiprocessing import Process,Queue
#import qtqr

class MainWindow(Ui_MainWindow):
    
    def __init__(self):
        super(MainWindow,self).__init__()
        self.title = 'GSH OPC Software'
        self.database_file = "variable_history.sqlite3"
        self.uri = "PLC_Server"
        plc_address = {'PLC1':'127.0.0.1:8501'}
        self.start_time = datetime.now()
        self.input_queue = Queue()
        file_path = Path(__file__).parent.absolute()
        endpoint = "localhost:4840/gshopcua/server"       
        self.server_process = Process(target=gsh_server.OpcServerThread, args=(plc_address,file_path,endpoint,self.uri))
        self.server_process.daemon = True    
        

        self.client_thread=QThread()
        self.client_worker = gsh_client.OpcClientThread(self.input_queue,endpoint,self.uri)
        self.client_worker.moveToThread(self.client_thread)
        self.client_thread.started.connect(self.client_worker.run)
        self.client_worker.logger_signal.connect(self.logger_handler)
        self.client_worker.data_signal.connect(self.io_handler)
        self.client_worker.info_signal.connect(self.info_handler)
        self.client_worker.ui_refresh_signal.connect(self.uptime)
        self.client_worker.time_data_signal.connect(self.time_calc)
        

    def setupUi(self, MainFrame):
        super(MainWindow, self).setupUi(MainFrame)
        self.alarm_log_text_edit.setReadOnly(True)
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
        self.server_process.start()
        self.client_thread.start()

    def server_close(self):
        self.server_process.terminate()
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
        return super(MainWindow, self).eventFilter(source, event)

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
        current_value = 1- self.io_dict[from_hmi_label[1]]
        #self.input_queue.put((2,from_hmi_label[0], current_value))
        msg = str((from_hmi_label[0], current_value))
        self.logger_handler(('INFO', datetime.now(), msg))

    def logger_handler(self, data):
        handler_type = data[0]
        time = (data[1].strftime("%d-%m-%Y | %H:%M:%S.%f")).split('.')[0]
        data_value = data[2]
        msg = f"{time} | {handler_type} | {data_value}"
        if handler_type=='ALARM':
            self.alarm_log_text_edit.appendPlainText(msg)
        elif handler_type=='INFO':
            self.event_log_text_edit.appendPlainText(msg)

    def time_calc(self, data):
        for values in data.values():
            time_reading = values[2]
            label = self.time_info_layout[values[1]]
            time_label = eval(f"self.{label}")
            time_label.setText(values[2])

    def info_handler(self, data):
        data_value = data[0]
        info_label = eval(f"self.{data[1][0]}")
        if isinstance(data_value, int):
            info_label.setText(str(data_value))
        elif isinstance(data_value, float):
            info_label.setText(f"{data_value:.2f}")

    def uptime(self):
        uptime = datetime.now() - self.start_time
        uptime_text = (str(uptime).split('.', 2)[0])
        self.system_uptime_label.setText(uptime_text)

    def io_handler(self, data):
        label_list = data[1]
        data_value = data[0]
        for label in label_list:
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
    app = QtWidgets.QApplication(sys.argv)
    Main_UI = QtWidgets.QMainWindow()
    ui = MainWindow()
    ui.setupUi(Main_UI)
    ui.server_start() #Disable comment to start server
    Main_UI.show()
    Main_UI.showMaximized()
    sys.exit(app.exec_())
    


