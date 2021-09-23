
from asyncua import Client, ua
import asyncio
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from io_layout_map import node_structure
from datetime import datetime, timedelta


class SubAlarmHandler(object):
    def __init__(self,alarm_signal):
        self.alarm_signal = alarm_signal
        
    async def datachange_notification(self, node, val, data):
        if val >0:
            self.alarm_signal.emit(('ALARM', datetime.now(), val))#data.monitored_item.Value.SourceTimestamp, val))

class SubIoHandler(object):
    def __init__(self,data_signal,io_dict):
        self.data_signal = data_signal
        self.io_dict = io_dict
    async def datachange_notification(self, node, val, data):
        node_id = node.nodeid.Identifier
        label_list = self.io_dict[node_id]['label_point']
        self.data_signal.emit((int(val), label_list))

class SubInfoHandler(object):
    def __init__(self,info_signal,info_dict):#,time_node):
        self.info_signal = info_signal
        self.info_dict = info_dict
    async def datachange_notification(self, node, val, data):
        node_id = node.nodeid.Identifier
        label_list = self.info_dict[node_id]['label_point']
        self.info_signal.emit((val,label_list))

class OpcClientThread(QObject):
    data_signal=pyqtSignal(tuple)
    time_data_signal=pyqtSignal(dict)
    info_signal = pyqtSignal(tuple)
    ui_refresh_signal=pyqtSignal()
    logger_signal=pyqtSignal(tuple)
    def __init__(self,input_q,endpoint,uri,parent=None,**kwargs):
        super().__init__(parent, **kwargs)
        self.input_queue = input_q
        self.sub_time = 50
        self.monitored_node = {key:value for key,value in node_structure.items() if value['node_property']['category']=='server_variables'}
        self.io_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='relay'}
        self.alarm_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='alarm'}
        self.hmi_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='hmi'}
        self.time_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='time_variables'}
        url = f"opc.tcp://{endpoint}"
        self.client = Client(url=url)
        self.uri = uri
    def run(self):
        asyncio.run(self.client_start())

    async def watch_timer(self, time_dict, namespace_index):
        for key,value in time_dict.items():
            node_ns = namespace_index
            time_var_node = key
            flag_node = value['monitored_node']
            flag_node_id = self.client.get_node(ua.NodeId(flag_node, node_ns)) #the trigger flag relay
            time_var_node_id = self.client.get_node(ua.NodeId(time_var_node, node_ns)) #the stored pasued time in OPC
            flag_value = await flag_node_id.read_value()
            if flag_value == 1:
                t = await time_var_node_id.read_data_value()
                t2 = t.SourceTimestamp #get time the flag triggered
                last_known_time = await time_var_node_id.read_value()
                time_var = datetime.strptime(last_known_time,"%H:%M:%S")
                delta = timedelta(hours=time_var.hour, minutes=time_var.minute, seconds=time_var.second)
                duration = datetime.utcnow() - t2 + delta
                time_string = str(duration).split(".")[0]
                time_dict.update ({flag_node: (node_ns, time_var_node, time_string)})
            elif flag_value == 0:
                current_time_value = value[2]
                await time_var_node_id.write_value(ua.Variant(current_time_value, ua.VariantType.String))
        return time_dict

    @pyqtSlot()
    async def client_start(self):
        await asyncio.sleep(1.5)
        
        async with self.client as client:
            namespace_index = await client.get_namespace_index(self.uri)

            io_handler = SubIoHandler(self.data_signal,self.io_dict)
            io_sub = await client.create_subscription(self.sub_time, io_handler)
            for node in self.io_dict.keys():
                var = client.get_node((ua.NodeId(node, namespace_index)))
                await io_sub.subscribe_data_change(var,queuesize=1)

            info_handler = SubInfoHandler(self.info_signal,self.monitored_node)
            info_sub = await client.create_subscription(self.sub_time, info_handler) 
            for node in self.monitored_node.keys():
                var = client.get_node((ua.NodeId(node, namespace_index)))
                await info_sub.subscribe_data_change(var,queuesize=1)

            alarm_handler = SubAlarmHandler(self.logger_signal)  
            alarm_sub = await client.create_subscription(self.sub_time, alarm_handler) 
            for node in self.alarm_dict.keys():
                var = client.get_node((ua.NodeId(node, namespace_index)))
                await alarm_sub.subscribe_data_change(var,queuesize=1)

            while True:
                await asyncio.sleep(0.2)
                #self.time_dict = await self.watch_timer(self.time_dict, namespace_index)
                #self.time_data_signal.emit(self.time_node)
                if not self.input_queue.empty():
                    hmi_signal = self.input_queue.get()
                    test_node = client.get_node(ua.NodeId(hmi_signal[1], 2))
                    await test_node.write_value(ua.Variant(hmi_signal[2], ua.VariantType.Int64))
                

