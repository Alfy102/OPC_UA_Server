import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import  QThread,QEvent
from PyQt5.QtWidgets import QDateTimeEdit, QMainWindow
from queue import Queue
import gsh_opc_platform_client as gsh_client
from gsh_opc_platform_gui import Ui_MainWindow as gui
from io_layout_map import node_structure,time_series_axis
from datetime import datetime
from multiprocessing import Queue
import collections



class Ui_MainWindow(QMainWindow,gui):
    def __init__(self):
        super(Ui_MainWindow,self).__init__()
        self.title = 'GSH OPC Software'
        self.database_file = "variable_history.sqlite3"
        self.uri = "PLC_Server"
        self.start_time = datetime.now()
        self.input_queue = Queue()
        endpoint = "localhost:4845/gshopcua/server"
        client_refresh_rate = 0.1   
        self.io_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='relay'}
        self.hmi_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='client_input_1'}
        self.lot_input = {key:value for key,value in node_structure.items() if value['node_property']['category']=='lot_input'}
        self.ui_time_dict = {}
        self.client_thread=QThread()
        self.client_worker = gsh_client.OpcClientThread(self.input_queue,endpoint,self.uri,client_refresh_rate)
        self.client_worker.moveToThread(self.client_thread)
        self.client_thread.started.connect(self.client_worker.run)
        self.client_worker.logger_signal.connect(self.logger_handler)
        self.client_worker.data_signal.connect(self.io_handler)
        self.client_worker.info_signal.connect(self.info_handler)
        self.client_worker.uph_signal.connect(self.update_plot)
        self.client_worker.init_plot.connect(self.init_bar_plot)

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
        self.plot_text =''
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

  


        #------------bar graph initialization------------------
        self.MplWidget.canvas.plt.xticks(rotation=45)
        self.MplWidget.canvas.ax.spines['top'].set_visible(False)
        self.MplWidget.canvas.ax.spines['right'].set_visible(False)
        self.MplWidget.canvas.ax.set_axisbelow(True)
        self.MplWidget.canvas.ax.tick_params(axis='x', labelsize=8)
        self.MplWidget.canvas.ax.tick_params(axis='y', labelsize=6)
        self.MplWidget.canvas.ax.yaxis.grid(color='gray', linestyle='dashed')
        self.plot_bar = self.MplWidget.canvas.ax.bar(self.x,self.y,align='center',width=1,color=(0.2, 0.4, 0.6, 1),  edgecolor='blue')
        self.MplWidget.canvas.draw()

        for value in self.io_dict.values():
            if 'y' in value['label_point'][0]:
                for label in value['label_point']:                
                    indicator_label = eval(f"self.{label}")
                    indicator_label.installEventFilter(self)

        #------------lot_entry_section-------------------------
        self.lot_entry_page_setup(False)
        dt = datetime.now()
        dt = dt.replace(second=0, microsecond=0)
        self.lot_start_date_time.setDateTime(dt)
        self.shift_start_date_time.setDateTime(dt)
        self.lot_entry_edit_button.clicked.connect(lambda: self.lot_entry_page_setup(True))
        self.lot_entry_save_button.clicked.connect(lambda: self.lot_entry_page_setup(False))
        self.lot_entry_save_button.clicked.connect(lambda: self.lot_entry_info('save'))
        self.lot_entry_cancel_button.clicked.connect(lambda: self.lot_entry_info('cancel'))





    def lot_entry_info(self,action):
        if action=='save':
            for key, value in self.lot_input.items():
                label = value['label_point'][0]
                label_object = eval(f"self.{label}")
                if value['name']=='lot_id':
                    data_value= label_object.text()
                if value['name']=='operator_id':
                    data_value = label_object.text()
                if value['name']=='package_name':
                    data_value = label_object.text()
                if value['name']=='device_id':
                    data_value = label_object.text()
                if value['name']=='lot_start_time':
                    lot_start_datetime = label_object.dateTime()
                    lot_start_datetime = lot_start_datetime.toPyDateTime()
                    data_value = lot_start_datetime.strftime("%d.%m.%Y %H:%M")
                if value['name']=='shift_start_time':
                    shift_start_datetime = label_object.dateTime()
                    shift_start_datetime = shift_start_datetime.toPyDateTime()
                    data_value = shift_start_datetime.strftime("%d.%m.%Y %H:%M")
                value['node_property']['initial_value'] = data_value
                data_type = value['node_property']['data_type']
                self.lot_input.update({key:value})
                self.send_data_to_opc(key,data_value,data_type)

        if action=='cancel':
            self.lot_entry_page_setup(False)
            for key, value in self.lot_input.items():
                label = value['label_point'][0]
                data_value = value['node_property']['initial_value']
                if data_value == 'Null':
                    data_value == ''
                if key == 10054 or key == 10055:
                    label_object = eval(f"self.{label}")
                    old_dt = datetime.strptime(data_value, "%d.%m.%Y %H:%M")
                    label_object.setDateTime(old_dt)
                else:
                    label_object = eval(f"self.{label}")
                    label_object.setText(data_value)






    def init_bar_plot(self, uph_dict):
        self.uph_dict = uph_dict
        self.update_plot()

    def update_plot(self):
        y = [value['node_property']['initial_value'] for value in self.uph_dict.values()]
        

        for rect, h in zip(self.plot_bar, y):
            rect.set_height(h)
        if len(self.plot_text) !=0:
            for text in self.plot_text:
                del text
        for i, v in enumerate(y):
            self.plot_text = self.MplWidget.canvas.ax.text(i - 0.3 , v + 0.25, str(v), color='red', fontsize=6)
        
        self.MplWidget.canvas.ax.relim()# recompute the ax.dataLim
        # update ax.viewLim using the new dataLim
        self.MplWidget.canvas.ax.autoscale_view()
        self.MplWidget.canvas.draw()  

    def deltatime(self,start, end, delta):
        current = start
        while current < end:
            yield current
            current += delta

    def client_start(self):
        self.client_thread.start()

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonDblClick:
            label_object_name = source.objectName()
            label_object_text = source.text()
            stylesheet = source.styleSheet()
            rgb_value = self.stylesheet_extractor(stylesheet)
            if rgb_value == self.rgb_value_output_on:
                #if output label is ON, send OFF to OPC
                self.get_data_response(label_object_name, label_object_text, True)
            elif rgb_value == self.rgb_value_output_off:
                #if output label is OFF, send ON to OPC
                self.get_data_response(label_object_name, label_object_text, False)
        return super(Ui_MainWindow, self).eventFilter(source, event)

    def stylesheet_extractor(self, stylesheet_string):
        stylesheet_list = stylesheet_string.split(';')
        background_color_property = [elem for idx, elem in enumerate(stylesheet_list) if 'background' in elem][0]
        rgb_value = background_color_property[background_color_property.find("(")+1:background_color_property.find(")")]
        return rgb_value

    def lot_entry_page_setup(self, data):
        self.operator_id_input.setEnabled(data)
        self.lot_id_input.setEnabled(data)
        self.package_name_input.setEnabled(data)
        self.device_id_input.setEnabled(data)
        self.lot_start_date_time.setEnabled(data)
        self.shift_start_date_time.setEnabled(data)
        self.lot_entry_save_button.setEnabled(data)
        self.lot_entry_cancel_button.setEnabled(data)


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

    def send_data_to_opc(self,node_id, data_value, data_type):
        self.input_queue.put((node_id, data_value, data_type))

    def get_data_response(self,label_object_name,label_object_text, data_value):
        hmi_node = [(key,value) for key,value in self.hmi_dict.items() if label_object_name in value['label_point']][0]
        hmi_node_id = hmi_node[0]
        data_type = hmi_node[1]['node_property']['data_type']
        current_value = 1- data_value
        self.send_data_to_opc(hmi_node_id, current_value, data_type)
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
    #w = 1920; h = 1080

    app = QtWidgets.QApplication(sys.argv)
    main_window = Ui_MainWindow()
    main_window.setWindowFlags(QtCore.Qt.FramelessWindowHint)# | QtCore.Qt.WindowStaysOnTopHint)
    #main_window.client_start()
    main_window.show()
    main_window.showFullScreen()
    sys.exit(app.exec_())