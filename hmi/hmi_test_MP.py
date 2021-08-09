from asyncio.runners import run
import sys
import os
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog,QApplication, QMainWindow, QStackedWidget,QWidget
from PyQt5.QtCore import QObject
from asyncua.common import node
from asyncua import Client, Node
import asyncio

from multiprocessing import Process, Queue, Event
BASE_DIR = os.path.dirname(os.path.abspath(__file__))



  

def start_client(inputs_queue, outputs_queue,instruct_queue, proc_id):
    asyncio.run(client(inputs_queue, outputs_queue,instruct_queue, proc_id))
async def read_opc(input_nodes,ivn,io_type,io_color):
    data = await input_nodes.read_value()

async def transfer_data(msg):
    print(msg)
async def gather_read_opc(input_nodes,ivn,io_type):
    if io_type=='input': io_color="Black on lime"
    elif io_type=='output': io_color="Black on red"
    asyncio.gather(*(read_opc(input_nodes[i],ivn[i],io_type,io_color) for i in range(len(input_nodes))))
async def client(inputs_queue, outputs_queue,instruct_queue, proc_id):#-------------------------------------------------------------------------------------------------------OPC HMI Starts here
    print("Initializing Input Nodes")
    client = Client(url='opc.tcp://localhost:4840/freeopcua/server/')
    
    async with client:

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
        print("Initializing Output Nodes")
        input_obj=await client.nodes.root.get_child(["0:Objects", "2:plc1_hmi_input"])
        input_nodes=await input_obj.get_children()
        ovn=[]
        for i in range(len(input_nodes)):
            hmi_display_name = await input_nodes[i].read_display_name()
            ovn.append(hmi_display_name.Text)
        instruct_cmd=''
        print("Client Running")
        while not instruct_cmd =='kill':
            await asyncio.sleep(0.2)
            print("Client is still kickin'")
            if not inputs_queue.empty():
                message = inputs_queue.get()
                print(message)
            if not instruct_queue.empty():
                instruct_cmd = instruct_queue.get()
                #asyncio.create_task(transfer_data(message))
            for i in range(len(nodes)):
                try:
                    tasks = await asyncio.create_task(gather_read_opc(nodes[i],input_variable_name[i],io_type[i]))
                except KeyboardInterrupt as e:
                    tasks.cancel()
                    tasks.exception()
        print("Client's fucking dead bro")


class button_window(QMainWindow):


    def __init__(self):
        super(button_window,self).__init__()
        loadUi("button_test.ui",self)

        #self.thread = QThread()
        #self.worker = Worker()
        #self.worker.moveToThread(self.thread)
        #self.thread.started.connect(self.worker.run)
        self._inputs_queue = Queue()
        self._outputs_queue = Queue()
        self._instructions_queue = Queue()

        self.client_process = Process(target=start_client, args=(self._inputs_queue, self._outputs_queue,self._instructions_queue,1)) #background
        

        self.pushButton_1.clicked.connect(self.data_test1)
        self.pushButton_1.setCheckable(True)
        self.pushButton_2.clicked.connect(self.data_test2)
        self.pushButton_2.setCheckable(True)
        self.pushButton_3.clicked.connect(self.data_test3)
        self.pushButton_3.setCheckable(True)
        self.pushButton_32.clicked.connect(lambda:self.client_start(self.client_process))
        self.pushButton_33.clicked.connect(self.client_quit)


    def data_test1(self):
        if self.pushButton_1.isChecked():
            message = ["R500",1]
            self._inputs_queue.put(message)
        else:
            message = ["R500",0]
            self._inputs_queue.put(message)

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



    def client_start(self,client_process):
        client_process.daemon = True
        client_process.start()
        print("Client Started")


    def client_quit(self):
        self._instructions_queue.put('kill')
        print("Client Terminated")



    
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.aboutToQuit.connect(button_window.client_quit())
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
