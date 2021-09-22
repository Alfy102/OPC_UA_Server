
from asyncua import Client, ua
import asyncio
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import io_layout_map as iomp
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
    async def datachange_notification(self, node, val, data):
        node_id = node.nodeid.Identifier
        self.info_signal.emit((node_id, val))



class OpcClientThread(QObject):
    data_signal=pyqtSignal(tuple)
    time_data_signal=pyqtSignal(dict)
    info_signal = pyqtSignal(tuple)
    ui_refresh_signal=pyqtSignal()
    server_logger_signal=pyqtSignal(tuple)
    def __init__(self,input_q,endpoint,label_dict,parent=None,**kwargs):
        super().__init__(parent, **kwargs)
        self.input_queue = input_q
        self.url = endpoint
        self.io_list = list(label_dict.keys())
        self.alarm_list = iomp.all_alarm_list
        self.sub_time = 50
        self.time_node = iomp.monitored_time_node
        self.info_node = iomp.info_layout_node

        url = f"opc.tcp://{self.url}"
        self.client = Client(url=url)
    def run(self):
        asyncio.run(self.client_start())

    async def watch_timer(self, time_dict):
        for key,values in time_dict.items():
            node_ns = values[0]
            time_var_node = values[1]
            flag_node = key
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
                current_time_value = values[2]
                await time_var_node_id.write_value(ua.Variant(current_time_value, ua.VariantType.String))
        return time_dict

    @pyqtSlot()
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
            
            info_handler = SubInfoHandler(self.info_signal)
            info_sub = await client.create_subscription(self.sub_time, info_handler) 
            for node in self.info_node.keys():
                var = client.get_node(f"ns=2;i={node}")
                await info_sub.subscribe_data_change(var,queuesize=1)

            for key,values in self.time_node.items():
                node_ns = values[0]
                node_identifier = values[1]
                node_id = self.client.get_node(ua.NodeId(node_identifier, node_ns))
                #test_node_id = self.client.get_node(ua.NodeId(2048,2))
                init_delta = timedelta(hours=0, minutes=0, seconds=0)
                await node_id.write_value(ua.Variant(str(init_delta), ua.VariantType.String))
                self.time_node.update({key:(node_ns, node_identifier, str(init_delta))})


            while True:
                self.ui_refresh_signal.emit()
                await asyncio.sleep(0.05)
                self.time_node = await self.watch_timer(self.time_node)
                self.time_data_signal.emit(self.time_node)
                if not self.input_queue.empty():
                    hmi_signal = self.input_queue.get()
                    test_node = self.client.get_node(ua.NodeId(hmi_signal[1], 2))
                    await test_node.write_value(ua.Variant(hmi_signal[2], ua.VariantType.Int64))
                

