
from asyncua import Client, ua
import asyncio
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from io_layout_map import node_structure
from datetime import datetime


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
    def __init__(self,info_signal,info_dict):
        self.info_signal = info_signal
        self.info_dict = info_dict
    async def datachange_notification(self, node, val, data):
        node_id = node.nodeid.Identifier
        label_list = self.info_dict[node_id]['label_point']
        self.info_signal.emit((val,label_list))

class SubTimerHandler(object):
    def __init__(self,time_signal,time_dict,read_time):
        self.time_signal = time_signal
        self.time_dict = time_dict
        self.read_time = read_time
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        namespace_index = node.nodeid.NamespaceIndex
        SourceTime = data.monitored_item.Value.SourceTimestamp
        corr_time_node = [key for key,value in self.time_dict.items() if value['monitored_node']==node_identifier][0]
        stored_time = await self.read_time(namespace_index, corr_time_node)
        label = self.time_dict[corr_time_node]['label_point'][0]
        #self.time_signal.emit((corr_time_node, val ,SourceTime, stored_time,label))



class OpcClientThread(QObject):
    data_signal=pyqtSignal(tuple)
    time_data_signal=pyqtSignal(tuple)
    info_signal = pyqtSignal(tuple)
    ui_refresh_signal=pyqtSignal()
    logger_signal=pyqtSignal(tuple)
    def __init__(self,input_q,endpoint,uri,client_refresh_rate,parent=None,**kwargs):
        super().__init__(parent, **kwargs)
        self.input_queue = input_q
        self.sub_time = 50
        self.client_refresh_rate = client_refresh_rate
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

    def ua_variant_data_type(self, data_type, data_value):
        if data_type == 'UInt16':
            ua_var = ua.Variant(int(data_value), ua.VariantType.UInt16)
        elif data_type == 'UInt32':
            ua_var = ua.Variant(int(data_value), ua.VariantType.UInt32)
        elif data_type == 'UInt64':    
            ua_var = ua.Variant(int(data_value), ua.VariantType.UInt64)
        elif data_type == 'String':
            ua_var = ua.Variant(str(data_value), ua.VariantType.String)
        elif data_type == 'Boolean':
            ua_var = ua.Variant(bool(data_value), ua.VariantType.Boolean)
        elif data_type == 'Float':
            ua_var = ua.Variant(float(data_value), ua.VariantType.Float)
        return ua_var

    async def read_time(self, namespace_index, node_id):
        var = self.client.get_node((ua.NodeId(node_id, namespace_index)))
        data_value = await var.read_value()
        return data_value

    @pyqtSlot()
    async def client_start(self):
        await asyncio.sleep(2)
        
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

            
            timer_handler = SubTimerHandler(self.time_data_signal,self.time_dict,self.read_time)  
            time_sub = await client.create_subscription(self.sub_time, timer_handler) 

            for node,value in self.time_dict.items():
                #var = client.get_node((ua.NodeId(node, namespace_index)))
                #opc_stored_time = await var.read_value()
                #value['node_property']['initial_value'] = opc_stored_time
                self.time_dict.update({node:value})
                node = value['monitored_node']
                var_2 = client.get_node((ua.NodeId(node, namespace_index)))
                await time_sub.subscribe_data_change(var_2,queuesize=1)





            while True:
                await asyncio.sleep(self.client_refresh_rate)
                self.ui_refresh_signal.emit()
                if not self.input_queue.empty():
                    hmi_signal = self.input_queue.get()
                    hmi_node_id = hmi_signal[0]
                    data_value = hmi_signal[1]
                    data_type = hmi_signal[2]
                    input_node = client.get_node(ua.NodeId(hmi_node_id, namespace_index))
                    await input_node.write_value(self.ua_variant_data_type(data_type,data_value))
                

