
from asyncua import Client
import asyncio
from queue import Queue
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal


class SubAlarmHandler(object):
    def __init__(self,alarm_signal):
        self.alarm_signal = alarm_signal
        
    async def datachange_notification(self, node, val, data):
        if val >0:
            self.alarm_signal.emit(('alarm', (node.nodeid.Identifier, val)))

class SubIoHandler(object):
    def __init__(self,data_signal):
        self.data_signal = data_signal

    async def datachange_notification(self, node, val, data):
        self.data_signal.emit((node.nodeid.Identifier, val))

class SubVarHandler(object):
    def __init__(self,monitored_dict,count):
        self.monitored_node = monitored_dict
        self.count_node=count
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        if val >0:
            value = self.monitored_node[node_identifier]
            await self.count_node((value[0], value[1], val)) #(namespace, node id, amount)



class OpcClientThread(QObject):
    data_signal=pyqtSignal(tuple)
    ui_refresh_signal=pyqtSignal()
    server_logger_signal=pyqtSignal(tuple)
    def __init__(self,input_q,current_file_path,endpoint,label_dict, alarm_dict,parent=None,**kwargs):
        super().__init__(parent, **kwargs)
        self.input_queue = input_q
        self.url = endpoint
        self.io_list = list(label_dict.keys())
        self.alarm_list = list(alarm_dict.keys())
        self.sub_time = 50

    def run(self):
        asyncio.run(self.client())


    async def client(self):
        url = f"opc.tcp://{self.url}"
        await asyncio.sleep(5)
        async with Client(url=url) as client:

            io_handler = SubIoHandler(self.data_signal)
            io_sub = await client.create_subscription(self.sub_time, io_handler)
            for nodes in self.io_list:
                io_var = client.get_node(f"ns=2;i={nodes}")
                await io_sub.subscribe_data_change(io_var,queuesize=1)

            alarm_handler = SubAlarmHandler(self.server_logger_signal)  
            alarm_sub = await client.create_subscription(self.sub_time, alarm_handler) 
            for node in self.alarm_list:
                alarm_var = client.get_node(f"ns=2;i={node}")
                await alarm_sub.subscribe_data_change(alarm_var,queuesize=1)

            server_var_obj = await client.nodes.root.get_child(["0:Objects", "2:server_variables"])
            server_var_list = await server_var_obj.get_children()
            self.server_logger_signal.emit((('log',server_var_list)))
            
            #for node in server_var_list:
            #    await var_sub.subscribe_data_change(node,queuesize=1)

            while True:
                await asyncio.sleep(0.5)
                self.ui_refresh_signal.emit()
