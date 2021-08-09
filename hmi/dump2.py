from asyncio.runners import run
import sys
import os
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog,QApplication, QMainWindow, QStackedWidget,QWidget
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from asyncua.common import node
from asyncua import Client, Node
import asyncio


BASE_DIR = os.path.dirname(os.path.abspath(__file__))



  
class opc_client_worker(QObject):
    input_q = pyqtSignal()

    def start_client(self):
        print("Success thread")
        asyncio.run(self.client())
    async def read_opc(self,input_nodes,ivn,io_type,io_color):
        data = await input_nodes.read_value()
        #asyncio.create_task(print(data))
        #print(data)
    async def transfer_data(self,msg):
        print(msg)
    async def gather_read_opc(self,input_nodes,ivn,io_type):
        if io_type=='input': io_color="Black on lime"
        elif io_type=='output': io_color="Black on red"
        asyncio.gather(*(self.read_opc(input_nodes[i],ivn[i],io_type,io_color) for i in range(len(input_nodes))))
    async def client(self):#-------------------------------------------------------------------------------------------------------OPC HMI Starts here
        print("Init Client")
        client = Client(url='opc.tcp://localhost:4840/freeopcua/server/')
        async with client:
            message = self.input_q.get()
            print(message)
            obj=[]
            init_value = []
            nodes = []
            io_type=[]
            obj.append(await client.nodes.root.get_child(["0:Objects", "2:plc1_relay_input"])) #obj[0]
            io_type.append("input")
            obj.append(await client.nodes.root.get_child(["0:Objects", "2:plc1_relay_output"])) #obj[1]
            io_type.append("output")
            input_variable_name = []
            for i in range(len(obj)):
                ivn=[]
                nodes.append(await obj[i].get_children())
                for k in range(len(nodes[i])):
                    display_name = await nodes[i][k].read_display_name() #get the display name of the variables, will be use to send to plc socket
                    ivn.append(display_name.Text)
                    init_value.append(await nodes[i][k].read_value())
                input_variable_name.append(ivn)

            input_obj=await client.nodes.root.get_child(["0:Objects", "2:plc1_hmi_input"])
            input_nodes=await input_obj.get_children()
            ovn=[]
            for i in range(len(input_nodes)):
                hmi_display_name = await input_nodes[i].read_display_name()
                ovn.append(hmi_display_name.Text)
            
            print("Start client")
            while not QThread.currentThread().isInterruptionRequested():
                print("Loop alive")
                await asyncio.sleep(0.2)
                    #self.transfer_data(message)
                    #asyncio.create_task(transfer_data(message))
                    #print(message)
                for i in range(len(nodes)):
                    try:
                        tasks = await asyncio.create_task(self.gather_read_opc(nodes[i],input_variable_name[i],io_type[i]))
                    except KeyboardInterrupt as e:
                        tasks.cancel()
                        tasks.exception()



class button_window(QMainWindow):
    

    def __init__(self):
        super(button_window,self).__init__()
        loadUi("button_test.ui",self)

        self.thread_client = QThread()

        self.worker_client = opc_client_worker() #main worker
        self.worker_client.moveToThread(self.thread_client)

        self.thread_client.started.connect(self.worker_client.start_client)
        
        self.worker_client.input_q.connect(print)


        self.pushButton_1.clicked.connect(self.data_test1)
        self.pushButton_1.setCheckable(True)
   
        self.pushButton_2.clicked.connect(self.data_test2)
        self.pushButton_2.setCheckable(True)
        self.pushButton_3.clicked.connect(self.data_test3)
        self.pushButton_3.setCheckable(True)
        self.pushButton_32.clicked.connect(lambda:self.client_start_button(self.thread_client))
        self.pushButton_33.clicked.connect(lambda: self.client_stop_button(self.thread_client))


    def data_test1(self):
        if self.pushButton_1.isChecked():
            message = ["R500",1]
            self.input_q.emit(message)
        else:
            message = ["R500",0]
            self.input_q.emit(message)

    def data_test2(self):
        if self.pushButton_2.isChecked():
            message = ["R501",1]
            self._inputs_queue.put(message)
        else:
            message = ["R501",0]
            self._inputs_queue.put(message)

    def data_test3(self):
        if self.pushButton_3.isChecked():
            message = ["R501",1]
            self._inputs_queue.put(message)
        else:
            message = ["R501",0]
            self._inputs_queue.put(message)

    def client_start_button(self,thread):
        thread.start()
        print("Start Thread")

    def client_stop_button(self,thread):
        thread.requestInterruption()
        thread.quit()
        print("Stop Thread")


    
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.aboutToQuit.connect(button_window.client_quit) #not correct, need to rework
    hmi = button_window()
    widget = QStackedWidget()
    widget.addWidget(hmi)
    widget.setFixedHeight(600)
    widget.setFixedWidth(400)
    widget.show()
    try:
        sys.exit(app.exec_())
    except:

        print("exiting")
