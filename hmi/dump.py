import sys
import os
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog,QApplication, QMainWindow, QStackedWidget,QWidget

from asyncua.common import node
from asyncua import Client, Node
import asyncio

from multiprocessing import Process, Queue, Event

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
class button_window(QMainWindow):
    def __init__(self):
        super(button_window,self).__init__()
        loadUi("button_test.ui",self)

        self._inputs_queue = Queue()
        self._outputs_queue = Queue()

        
        client_process = Process(target=start_client, args=(self._inputs_queue, self._outputs_queue,1)) #background
        



        self.pushButton_1.clicked.connect(self.data_test1)
        self.pushButton_1.setCheckable(True)
        self.pushButton_2.clicked.connect(self.data_test2)
        self.pushButton_2.setCheckable(True)
        self.pushButton_3.clicked.connect(self.data_test3)
        self.pushButton_3.setCheckable(True)
        #self.pushButton_32.clicked.connect(self.client_start(client_process))
        #Eself.pushButton_33.clicked.connect(self.client_shutdown)
        

    def data_test1(self):
        if self.pushButton_1.isChecked():
            self._inputs_queue.put(["R500",1])
        else:
            self._inputs_queue.put(["R500",0])

    def data_test2(self):
        if self.pushButton_2.isChecked():
            self._inputs_queue.put(["R501",1])
        else:
            self._inputs_queue.put(["R501",0])

    def data_test3(self):
        if self.pushButton_3.isChecked():
            self._inputs_queue.put(["R501",1])
        else:
            self._inputs_queue.put(["R501",0])


    def client_start(self,client_process):
        print("Starting Client")
        self._inputs_queue.put("client_start")

    def client_shutdown(self):
        self._inputs_queue.put("client_kill")


def start_client(inputs_queue, outputs_queue, proc_id):
    asyncio.run(opc_client(inputs_queue, outputs_queue, proc_id))

async def read_opc_2(input_nodes,ivn,io_type):
    data = await input_nodes.read_value()
    #asyncio.create_task(print(data))
    #print(data)
async def transfer_data(msg):
        print(msg)
async def read_opc(input_nodes,ivn,io_type):
    asyncio.gather(*(read_opc_2(input_nodes[i],ivn[i],io_type) for i in range(len(input_nodes))))
async def opc_client(inputs_queue, outputs_queue, proc_id):#-------------------------------------------------------------------------------------------------------OPC HMI Starts here
    
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

        input_obj=await client.nodes.root.get_child(["0:Objects", "2:plc1_hmi_input"])
        input_nodes=await input_obj.get_children()
        ovn=[]
        for i in range(len(input_nodes)):
            hmi_display_name = await input_nodes[i].read_display_name()
            ovn.append(hmi_display_name.Text)

            
        while True:
            await asyncio.sleep(0.1)
            if not inputs_queue.empty():
                message = inputs_queue.get()
                print(message)
                #asyncio.create_task(transfer_data(message))
            for i in range(len(nodes)):
                try:
                    tasks = await asyncio.create_task(read_opc(nodes[i],input_variable_name[i],io_type[i]))
                except KeyboardInterrupt as e:
                    tasks.cancel()
                    tasks.exception()

            

    
if __name__ == '__main__':
    #quit_event = Event()
    app = QApplication(sys.argv)
    home = button_window()
    widget = QStackedWidget()
    widget.addWidget(home)
    #widget.setFixedHeight(600)
    #widget.setFixedWidth(400)
    widget.show()
    try:
        sys.exit(app.exec_())
    except:

        print("exiting")
