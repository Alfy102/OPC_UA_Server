import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import  QThread,QEvent
from PyQt5.QtWidgets import QMainWindow
from queue import Queue
from pathlib import Path
import gsh_opc_platform_server as gsh_server
import gsh_opc_platform_client as gsh_client
from gsh_opc_platform_gui import Ui_MainWindow as gui
from io_layout_map import node_structure,time_series_axis
from datetime import datetime
from multiprocessing import Process,Queue
import collections




class Ui_MainWindow(QMainWindow,gui):
    def __init__(self):
        super(Ui_MainWindow,self).__init__()
        self.title = 'GSH OPC Software'
        self.database_file = "variable_history.sqlite3"
        self.uri = "PLC_Server"
        plc_address = {'PLC1':'127.0.0.1:8501'}
        self.start_time = datetime.now()
        self.input_queue = Queue()
        file_path = Path(__file__).parent.absolute()
        endpoint = "localhost:4845/gshopcua/server"
        server_refresh_rate = 0.05
        client_refresh_rate = 0.1
        self.server_process = Process(target=gsh_server.OpcServerThread, args=(plc_address,file_path,endpoint,server_refresh_rate,self.uri))
        self.server_process.daemon = True    
        self.io_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='relay'}
        self.hmi_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='hmi'}
        self.ui_time_dict = {}
        self.client_thread=QThread()
        self.client_worker = gsh_client.OpcClientThread(self.input_queue,endpoint,self.uri,client_refresh_rate)
        self.client_worker.moveToThread(self.client_thread)
        self.client_thread.started.connect(self.client_worker.run)
        self.client_worker.logger_signal.connect(self.logger_handler)
        self.client_worker.data_signal.connect(self.io_handler)
        self.client_worker.info_signal.connect(self.info_handler)
        self.client_worker.ui_refresh_signal.connect(self.uptime)
        self.client_worker.uph_signal.connect(self.update_plot_data)

        self.client_worker.time_data_signal.connect(self.time_label_update)
        self.rgb_value_input_on = "64, 255, 0"
        self.rgb_value_input_off = "0, 80, 0"
        self.rgb_value_output_on = "255, 20, 20"
        self.rgb_value_output_off = "80, 0, 0"
        self.x = time_series_axis
        uph_filter = {key:value for key,value in node_structure.items() if value['node_property']['category']=='uph_variables'}
        self.uph_dict = collections.OrderedDict(sorted(uph_filter.items()))
        self.y = [0 for _ in self.uph_dict.values()] 
        self.plot_bar = ''
        self.setupUi(self)
        
    def setupUi(self, MainFrame):
        super(Ui_MainWindow, self).setupUi(MainFrame)
        self.alarm_log_text_edit.setReadOnly(True)
        self.event_log_text_edit.setReadOnly(True)
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

  
        self.MplWidget.canvas.plt.xticks(rotation=45)
        self.MplWidget.canvas.ax.spines['top'].set_visible(False)
        self.MplWidget.canvas.ax.spines['right'].set_visible(False)
        self.MplWidget.canvas.ax.set_axisbelow(True)
        self.MplWidget.canvas.ax.tick_params(axis='x', labelsize=8)
        self.MplWidget.canvas.ax.tick_params(axis='y', labelsize=6)
        self.MplWidget.canvas.ax.yaxis.grid(color='gray', linestyle='dashed')
        self.plot_bar = self.MplWidget.canvas.ax.bar(self.x,self.y,align='edge',width=1,color=(0.2, 0.4, 0.6, 0.6),  edgecolor='blue')
        self.MplWidget.canvas.draw()
        #for i, v in enumerate(self.y):
            #self.MplWidget.canvas.ax.text(i + 0.1, v + 0.25, str(v), color='red', fontsize=6)
        #self.MplWidget.canvas.draw()
        #self.MplWidget.canvas.flush_events()
        #print(self.plot_bar)
        for value in self.io_dict.values():
            if 'y' in value['label_point'][0]:
                for label in value['label_point']:                
                    indicator_label = eval(f"self.{label}")
                    indicator_label.installEventFilter(self)


    def update_plot(self):
        y = [value['node_property']['initial_value'] for value in self.uph_dict.values()]
        #print(y)

        for rect, h in zip(self.plot_bar, y):
            rect.set_height(h)
        self.MplWidget.canvas.ax.relim()# recompute the ax.dataLim
        # update ax.viewLim using the new dataLim
        self.MplWidget.canvas.ax.autoscale_view()
        self.MplWidget.canvas.draw()


    def update_plot_data(self, data):
        node_id = data[0]
        data_value = data[1]
        node_property = self.uph_dict[node_id]
        node_property['node_property']['initial_value']=data_value
        self.uph_dict.update({node_id:node_property})
        self.update_plot()


    def deltatime(self,start, end, delta):
        current = start
        while current < end:
            yield current
            current += delta

    def server_start(self):
        self.server_process.start()
        self.client_thread.start()

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonDblClick:
            label_object_name = source.objectName()
            label_object_text = source.text()
            stylesheet = source.styleSheet()
            rgb_value = self.stylesheet_extractor(stylesheet)
            if rgb_value == self.rgb_value_output_on:
                #if output label is ON, send OFF to OPC
                self.send_data(label_object_name, label_object_text, True)
            elif rgb_value == self.rgb_value_output_off:
                #if output label is OFF, send ON to OPC
                self.send_data(label_object_name, label_object_text, False)
        return super(Ui_MainWindow, self).eventFilter(source, event)

    def stylesheet_extractor(self, stylesheet_string):
        stylesheet_list = stylesheet_string.split(';')
        background_color_property = [elem for idx, elem in enumerate(stylesheet_list) if 'background' in elem][0]
        rgb_value = background_color_property[background_color_property.find("(")+1:background_color_property.find(")")]
        return rgb_value

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
        self.module_1_motor_1_button.setChecked(True)
        self.main_motor_station_stacked_widget.setCurrentIndex(0)
        self.main_motor_control_stacked_widget.setCurrentIndex(0)

    def send_data(self,label_object_name,label_object_text, data_value):
        print("trigger")
        hmi_node = [(key,value) for key,value in self.hmi_dict.items() if label_object_name in value['label_point']][0]
        hmi_node_id = hmi_node[0]
        data_type = hmi_node[1]['node_property']['data_type']
        current_value = 1- data_value
        self.input_queue.put((hmi_node_id, current_value, data_type))
        if current_value == 1:
            self.logger_handler(('INFO', datetime.now() , f"{label_object_text} is switched ON"))
        elif current_value == 0:
            self.logger_handler(('INFO', datetime.now() , f"{label_object_text} is switched OFF"))

    def logger_handler(self, data):
        handler_type = data[0]
        time = (data[1].strftime("%d-%m-%Y | %H:%M:%S.%f")).split('.')[0]
        data_value = data[2]
        msg = f"{time} | {handler_type} | {data_value}"
        if handler_type=='ALARM':
            self.alarm_log_text_edit.appendPlainText(msg)
        elif handler_type=='INFO':
            self.event_log_text_edit.appendPlainText(msg)

    def info_handler(self, data):
        data_value = data[0]
        label_list = data[1]
        if data_value:
            for label in label_list:
                info_label = eval(f"self.{label}")
                if isinstance(data_value, int):
                    info_label.setText(str(data_value))
                elif isinstance(data_value, float):
                    info_label.setText(f"{data_value:.2f}")

    def io_handler(self, data):
        label_list = data[1]
        data_value = data[0]
        for label in label_list:
            indicator_label = eval(f"self.{label}")
            if data_value == 1:
                if 'x' in label:
                    indicator_label.setStyleSheet(f"background-color: rgb({self.rgb_value_input_on});color: rgb(0, 0, 0);")
                if 'y' in label:
                    indicator_label.setStyleSheet(f"background-color: rgb({self.rgb_value_output_on});color: rgb(0, 0, 0);")
            elif data_value == 0:
                if 'x' in label:
                    indicator_label.setStyleSheet(f"background-color: rgb({self.rgb_value_input_off});color: rgb(200, 200, 200);")
                if 'y' in label:
                    indicator_label.setStyleSheet(f"background-color: rgb({self.rgb_value_output_off});color: rgb(200, 200, 200);")

    def uptime(self):
        uptime = datetime.now() - self.start_time
        uptime_text = (str(uptime).split('.', 2)[0])
        self.system_uptime_label.setText(uptime_text)

    def time_label_update(self,data):
        label = data[0]
        time_string = data[1].split('.')[0]
        for label in label:
            time_label = eval(f"self.{label}")
            time_label.setText(time_string)

    def closeEvent(self,event):
        print("Close event trigger")
        


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = Ui_MainWindow()
    main_window.setWindowFlags(QtCore.Qt.FramelessWindowHint)# | QtCore.Qt.WindowStaysOnTopHint)
    main_window.server_start()
    main_window.show()
    #main_window.showMaximized()
    main_window.showFullScreen()
    sys.exit(app.exec_())