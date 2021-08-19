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
#from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256

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
    client = Client(url='opc.tcp://127.0.0.1:4840/freeopcua/server/')
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