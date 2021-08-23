import os
from asyncua import Client
import asyncio
from queue import Queue

from asyncua.ua.uaprotocol_auto import TrustListDataType
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
alarm_devices_group=[]
alarm_data_group=[]


class SubAlarmHandler(object):
    async def datachange_notification(self, node, val, data):
        index =  alarm_devices_group.index(node)
        alarm_data_group[index]=val
        #print(node, val, index)
           




class opc_client_thread(QObject):
    client_signal=pyqtSignal(str)
    scan_signal=pyqtSignal(dict)
    alarm_signal=pyqtSignal(int)
    def __init__(self,input_q,parent=None,**kwargs):
        super().__init__(parent, **kwargs)
        self.input_queue = input_q

    def run(self):
        self.client_signal.emit("Client Starting")
        asyncio.run(self.client())

    async def transfer_data(self,message,input_nodes,ovn):
        index = ovn.index(message[0])
        await input_nodes[index].write_value(int(message[1]))

    @pyqtSlot(dict)
    async def client_scan_loop(self,devices_group, devices_name):
        devices_data = [(await devices_group[i].read_value()) for i in range(len(devices_group))]
        #devices_zip = zip(devices_name,devices_data)
        self.scan_signal.emit(dict(zip(devices_group,zip(devices_name,devices_data))))

    async def transfer_data(message,input_nodes,ovn):
        index = ovn.index(message[0])
        await input_nodes[index].write_value(int(message[1]))

    @pyqtSlot(int)
    async def alarm_notification_loop(self,alarm_data):
        for i in range(len(alarm_data_group)):
            if alarm_data_group[i]!=0:
                self.alarm_signal.emit(alarm_data[i])

    @pyqtSlot(str)
    async def client(self):
        url = "opc.tcp://127.0.0.1:4840/gshopcua/server"
        global alarm_devices_group
        global alarm_data_group
        await asyncio.sleep(5)
        self.client_signal.emit("Connecting to server")
        async with Client(url=url) as client:
            #logger.info('Children of root are: %r', await client.nodes.root.get_children())
            idx = await client.get_namespace_index(uri="Keyence_PLC_Server")
            main_folder = await client.nodes.objects.get_child(f"{idx}:Device")
            devices = await main_folder.get_children()
            main_devices = [await devices[i].get_children() for i in range(len(devices))]
            """
            Create node subscription for Alarm Trigger
            """
            alarm_handler = SubAlarmHandler()
            alarm_sub = await client.create_subscription(100, alarm_handler)

            """
            Create node subscription for relays and memory data
            """
            #sub_handler = SubHandler()
            #sub = await client.create_subscription(100, sub_handler)

            hmi_devices_group=[]
            #alarm_devices_group=[]
            devices_group=[]
            for i in range(len(main_devices)):
                for k in range(len(main_devices[i])):
                    device_category=main_devices[i][k]
                    device_category_name=(await  device_category.read_display_name()).Text
                    if device_category_name=='alarm':
                        alarm_devices = await device_category.get_children()
                        [await alarm_sub.subscribe_data_change(alarm_devices[i],queuesize=1) for i in range(len(alarm_devices))]
                        alarm_devices_group.extend(alarm_devices)
                    elif device_category_name=='hmi':
                        hmi_devices = await device_category.get_children()
                        hmi_devices_group.append(hmi_devices)
                    else:
                        mnemonic_device = await device_category.get_children()
                        devices_group.extend(mnemonic_device)
            alarm_data_group=[0 for i in  range(len(alarm_devices_group))]
            
            devices_name = [(await devices_group[i].read_display_name()).Text for i in range(len(devices_group))]
            #print(devices_name)
            while True:
                await asyncio.sleep(2)
                self.client_signal.emit("Client Alive")
                alarm_tasks = asyncio.create_task(self.alarm_notification_loop(alarm_data_group))
                client_task = asyncio.create_task(self.client_scan_loop(devices_group,devices_name))
                if not self.input_queue.empty():
                    hmi_signal = self.input_queue.get()
                    print(hmi_signal)
                    #asyncio.create_task(self.transfer_data(hmi_signal,devices_group,devices_name))


            
