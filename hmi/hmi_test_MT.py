import sys
import os
from PyQt5.QtCore import QTimer
from PyQt5.uic import loadUi
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from asyncua import Client
import asyncio
from threading import Thread
from queue import Queue
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_list=[]
node_list=[]
import datetime
stop_thread=False


class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """
    def datachange_notification(self, node, val, data):
        print("New data change event", node, val)
        index = node_list.index(node)
        data_list[index] = val
        #print(data_list)
    def event_notification(self, event):
        print("New event", event)


def start_client(inputs_queue,proc_id):
    asyncio.run(client(inputs_queue,proc_id))

async def transfer_data(message,input_nodes,ovn):
    index = ovn.index(message[0])
    await input_nodes[index].write_value(int(message[1]))

async def client(inputs_queue, proc_id):#-------------------------------------------------------------------------------------------------------OPC HMI Starts here
    print("Initializing Input Nodes")
    client = Client(url='opc.tcp://localhost:4840/freeopcua/server/')
    async with client:

        obj=[]
        nodes = []
        io_type=[]
        obj.append(await client.nodes.root.get_child(["0:Objects", "2:plc1_relay_input"])) #obj[0]
        io_type.append("input")
        obj.append(await client.nodes.root.get_child(["0:Objects", "2:plc1_relay_output"])) #obj[1]
        io_type.append("output")
        input_variable_name = []

        handler = SubHandler()
        sub = await client.create_subscription(50, handler)


        for i in range(len(obj)):
            ivn=[]
            nodes.append(await obj[i].get_children())
            for k in range(len(nodes[i])):
                display_name = await nodes[i][k].read_display_name() #get the display name of the variables, will be use to send to plc socket
                data_list.append(await nodes[i][k].read_value())
                await sub.subscribe_data_change(nodes[i][k],queuesize=1)
                node_list.append(nodes[i][k])
                ivn.append(display_name.Text)
                
            input_variable_name.append(ivn)

        print("Initializing Output Nodes")
        input_obj=await client.nodes.root.get_child(["0:Objects", "2:plc1_hmi_input"])
        input_nodes=await input_obj.get_children()
        ovn=[]
        for i in range(len(input_nodes)):
            hmi_display_name = await input_nodes[i].read_display_name()
            ovn.append(hmi_display_name.Text)
        print("Client Running")
        while True:
            if stop_thread:
                break
            await asyncio.sleep(0.01)

            if not inputs_queue.empty():
                message = inputs_queue.get()

                asyncio.create_task(transfer_data(message,input_nodes,ovn))

        print("Client's fucking dead bro")


class button_window(QMainWindow):

    def __init__(self):
        super(button_window,self).__init__()
        loadUi("button_test.ui",self)
        self._inputs_queue = Queue()

        self.pushButton_1.clicked.connect(lambda: self.send_data(self.pushButton_1))
        self.pushButton_1.setCheckable(True)

        self.pushButton_2.clicked.connect(lambda: self.send_data(self.pushButton_2))
        self.pushButton_2.setCheckable(True)

        self.pushButton_3.clicked.connect(lambda: self.send_data(self.pushButton_3))
        self.pushButton_3.setCheckable(True)

        self.pushButton_4.clicked.connect(lambda: self.send_data(self.pushButton_4))
        self.pushButton_4.setCheckable(True)

        self.pushButton_5.clicked.connect(lambda: self.send_data(self.pushButton_5))
        self.pushButton_5.setCheckable(True)

        self.pushButton_6.clicked.connect(lambda: self.send_data(self.pushButton_6))
        self.pushButton_6.setCheckable(True)

        self.pushButton_7.clicked.connect(lambda: self.send_data(self.pushButton_7))
        self.pushButton_7.setCheckable(True)

        self.pushButton_8.clicked.connect(lambda: self.send_data(self.pushButton_8))
        self.pushButton_8.setCheckable(True)

        self.pushButton_9.clicked.connect(lambda: self.send_data(self.pushButton_9))
        self.pushButton_9.setCheckable(True)

        self.pushButton_10.clicked.connect(lambda: self.send_data(self.pushButton_10))
        self.pushButton_10.setCheckable(True)

        self.pushButton_11.clicked.connect(lambda: self.send_data(self.pushButton_11))
        self.pushButton_11.setCheckable(True)

        self.pushButton_12.clicked.connect(lambda: self.send_data(self.pushButton_12))
        self.pushButton_12.setCheckable(True)

        self.pushButton_13.clicked.connect(lambda: self.send_data(self.pushButton_13))
        self.pushButton_13.setCheckable(True)

        self.pushButton_14.clicked.connect(lambda: self.send_data(self.pushButton_14))
        self.pushButton_14.setCheckable(True)

        self.pushButton_15.clicked.connect(lambda: self.send_data(self.pushButton_15))
        self.pushButton_15.setCheckable(True)

        self.pushButton_16.clicked.connect(lambda: self.send_data(self.pushButton_16))
        self.pushButton_16.setCheckable(True)
        

        self.pushButton_32.clicked.connect(lambda:self.client_start(self._inputs_queue))
        self.pushButton_33.clicked.connect(self.client_quit)

    def client_start(self,input_q):
        global stop_thread
        stop_thread=False
        self.client_process = Thread(target=start_client, args=(input_q,1)) #background
        self.client_process.daemon = True
        self.client_process.start()
        print("Client Started")

        

    def client_quit(self):
        global stop_thread
        stop_thread=True
        #self.client_start.join()
        print("Client Terminated")

    def send_data(self,button_number):
        Relay = button_number.text()
        if button_number.isChecked():
            message = [Relay,1]
            self._inputs_queue.put(message)
        else:
            message = [Relay,0]
            self._inputs_queue.put(message)

    def update_label(self):
        if len(data_list)>15: #to update with better implementation
            user_hmi.hmi.label_1.setText(str(bool(data_list[0])))
            user_hmi.hmi.label_2.setText(str(bool(data_list[1])))
            user_hmi.hmi.label_3.setText(str(bool(data_list[2])))
            user_hmi.hmi.label_4.setText(str(bool(data_list[3])))
            user_hmi.hmi.label_5.setText(str(bool(data_list[4])))
            user_hmi.hmi.label_6.setText(str(bool(data_list[5])))
            user_hmi.hmi.label_7.setText(str(bool(data_list[6])))
            user_hmi. hmi.label_8.setText(str(bool(data_list[7])))
            user_hmi.hmi.label_9.setText(str(bool(data_list[8])))
            user_hmi.hmi.label_10.setText(str(bool(data_list[9])))
            user_hmi.hmi.label_11.setText(str(bool(data_list[10])))
            user_hmi.hmi.label_12.setText(str(bool(data_list[11])))
            user_hmi.hmi.label_13.setText(str(bool(data_list[12])))
            user_hmi.hmi.label_14.setText(str(bool(data_list[13])))
            user_hmi.hmi.label_15.setText(str(bool(data_list[14])))
            user_hmi.hmi.label_16.setText(str(bool(data_list[15])))






class user_hmi():
    def main():
        app = QApplication(sys.argv)
        hmi = button_window()
        widget = QStackedWidget()
        widget.addWidget(hmi)
        widget.setFixedHeight(800)
        widget.setFixedWidth(600)
        widget.show()

        timer = QTimer()
        timer.timeout.connect(hmi.update_label)
        timer.start(200)
        sys.exit(app.exec_())

    
        
if __name__ == '__main__':
    user_hmi.main()


