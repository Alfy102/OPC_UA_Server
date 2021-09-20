
from asyncua import Client, ua
import asyncio
from queue import Queue
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal
from io_layout_map import monitored_time_node
from datetime import datetime, timedelta


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
        node_id = node.nodeid.Identifier
        self.data_signal.emit((node_id, val))


class SubInfoHandler(object):
    def __init__(self,info_signal):#,time_node):
        self.info_signal = info_signal
        #self.time_node = time_node
    async def datachange_notification(self, node, val, data):
        node_id = node.nodeid.Identifier
        #if node_id not in self.time_node.keys():
        self.info_signal.emit((node_id, val))
        #elif node_id in self.time_node.keys():
        #    test = data.monitored_item.Value.SourceTimestamp
        #    print(f"{node_id}, {val}: {test}")


class OpcClientThread(QObject):
    data_signal=pyqtSignal(tuple)
    info_signal = pyqtSignal(tuple)
    ui_refresh_signal=pyqtSignal()
    server_logger_signal=pyqtSignal(tuple)
    def __init__(self,input_q,start_time,endpoint,label_dict, alarm_dict,parent=None,**kwargs):
        super().__init__(parent, **kwargs)
        self.input_queue = input_q
        self.url = endpoint
        self.io_list = list(label_dict.keys())
        self.alarm_list = list(alarm_dict.keys())
        self.sub_time = 50
        self.time_node = monitored_time_node
        #self.start_time = start_time
        url = f"opc.tcp://{self.url}"
        self.client = Client(url=url)
    def run(self):
        asyncio.run(self.client_start())


    async def time_logic(self, test_node_id,var_node,var2_node):
        trigger = await test_node_id.read_value()

        if trigger == 1:
            test_time = await test_node_id.read_data_value()
            point_time = test_time.SourceTimestamp
            test1 = await var2_node.read_value()
            t = datetime.strptime(test1,"%H:%M:%S")
            delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            duration = datetime.utcnow() - point_time + delta
            time_string = str(duration).split(".")[0]
            await var_node.write_value(ua.Variant(time_string, ua.VariantType.String))
        elif trigger == 0:
            test1 = await var_node.read_value()
            #t = datetime.strptime(test1,"%H:%M:%S")
            #delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            await var2_node.write_value(ua.Variant(test1, ua.VariantType.String))
            #print(type(datetime.utcnow()))


    async def client_start(self):
        await asyncio.sleep(5)

        

        async with self.client as client:

            io_handler = SubIoHandler(self.data_signal)
            io_sub = await client.create_subscription(self.sub_time, io_handler)
            for nodes in self.io_list:
                var = client.get_node(f"ns=2;i={nodes}")
                await io_sub.subscribe_data_change(var,queuesize=1)

            alarm_handler = SubAlarmHandler(self.server_logger_signal)  
            alarm_sub = await client.create_subscription(self.sub_time, alarm_handler) 
            for node in self.alarm_list:
                var = client.get_node(f"ns=2;i={node}")
                await alarm_sub.subscribe_data_change(var,queuesize=1)

            server_var_obj = await client.nodes.root.get_child(["0:Objects", "2:server_variables"])
            server_var_list = await server_var_obj.get_children()
            #self.server_logger_signal.emit((('log',server_var_list)))
            
            info_handler = SubInfoHandler(self.info_signal)
            info_sub = await client.create_subscription(self.sub_time, info_handler) 

            for node in server_var_list:
                await info_sub.subscribe_data_change(node,queuesize=1)

            time_list={}


            var_node = self.client.get_node(ua.NodeId(10100, 2))
            test_node_id = self.client.get_node(ua.NodeId(2048,2))
            var2_node = self.client.get_node(ua.NodeId(2119, 2))
            init_delta = timedelta(hours=0, minutes=0, seconds=0)
            await var_node.write_value(ua.Variant(str(init_delta), ua.VariantType.String))
            await var2_node.write_value(ua.Variant(str(init_delta), ua.VariantType.String))
            while True:
                self.ui_refresh_signal.emit()
                await asyncio.sleep(0.5)
                asyncio.create_task(self.time_logic(test_node_id,var_node,var2_node))
                if not self.input_queue.empty():
                    hmi_signal = self.input_queue.get()
                    test_node = self.client.get_node(ua.NodeId(hmi_signal[1], 2))
                    await test_node.write_value(ua.Variant(hmi_signal[2], ua.VariantType.Int64))
                

