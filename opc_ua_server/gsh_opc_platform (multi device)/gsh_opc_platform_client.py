import os
from asyncua import Client
import asyncio
from queue import Queue

from asyncua.ua.uaprotocol_auto import TrustListDataType
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
class SubIoHandler(object):
    def __init__(self,data_signal,io_dictionary):
        self.data_signal = data_signal
        self.io_dictionary = io_dictionary
    async def datachange_notification(self, node, val, data):
        #self.data_signal.emit((node.nodeid.Identifier, val))
        print(node,val)
class OpcClientThread(QObject):
    data_signal = pyqtSignal(dict)
    def __init__(self,input_q,current_file_path,endpoint,io_dict,parent=None,**kwargs):
        super().__init__(parent, **kwargs)
        self.input_queue = input_q
        self.file_path = current_file_path
        self.endpoint = endpoint
        self.io_dict = io_dict

    def run(self):
        asyncio.run(self.client())

    
    async def client(self):
        url = f"opc.tcp://{self.endpoint}"

        async with Client(url=url) as client:
            io_handler = SubIoHandler(self.data_signal,self.io_dict)
            io_sub = await client.create_subscription(1, io_handler)
            io_client_dict = dict(filter(lambda elem: (elem[1][2]!='alarm') ,self.io_dict.items()))
            for key in io_client_dict.keys():
                io_var = client.get_node(f"ns={io_client_dict[key][0]};i={key}")
                await io_sub.subscribe_data_change(io_var,queuesize=1)

            while True:
                await asyncio.sleep(10)
                #self.data_signal.emit(self.io_dict)



            
