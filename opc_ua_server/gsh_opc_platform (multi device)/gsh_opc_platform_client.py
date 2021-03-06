from asyncua import Client, ua
import asyncio
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from asyncua.ua.uatypes import Boolean
from io_layout_map import node_structure
from datetime import datetime,timedelta
from comm_protocol import ua_variant_data_type

class SubAlarmHandler(object):
    def __init__(self,alarm_signal):
        self.alarm_signal = alarm_signal
        
    async def datachange_notification(self, node, val, data):
        if val >0:
            self.alarm_signal.emit(['logger_handler',('ALARM', datetime.now(), val)])#data.monitored_item.Value.SourceTimestamp, val))

class SubIoHandler(object):
    def __init__(self,data_signal):
        self.data_signal = data_signal
    async def datachange_notification(self, node, val, data):
        node_id = node.nodeid.Identifier
        self.data_signal.emit(['io_handler',(int(val),node_id)])

class SubInfoHandler(object):
    def __init__(self,info_signal):
        self.info_signal = info_signal
    async def datachange_notification(self, node, val, data):
        node_id = node.nodeid.Identifier
        self.info_signal.emit(['info_handler',(val, node_id)])
        

class SubTimerHandler(object):
    def __init__(self,time_signal):
        self.time_signal = time_signal
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        #time_label = self.time_dict[node_identifier]['label_point']
        self.time_signal.emit(['time_label_update',(node_identifier, val)])

class SubUPHHandler(object):
    def __init__(self,uph_signal,uph_dict):
        self.uph_signal = uph_signal
        self.uph_dict = uph_dict
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        node_property = self.uph_dict[node_identifier]
        initial_value = node_property['node_property']['initial_value']
        if val != initial_value:
            node_property['node_property']['initial_value'] = val
            self.uph_dict.update({node_identifier:node_property})
            self.uph_signal.emit(['update_uph_dict',(node_identifier, val)])

class SubDeviceModeHandler(object):
    def __init__(self,machine_mode_update):
        self.machine_update = machine_mode_update
    async def datachange_notification(self, node, val, data):
        node_id = node.nodeid.Identifier
        #self.data_signal.emit(['update_settings_dictionary',(node_id, val)])
        #print(node_id, val)
        await self.machine_update(node_id,val)

class SubSettingsHandler(object):
    def __init__(self,data_signal):
        self.data_signal = data_signal
    async def datachange_notification(self, node, val, data):
        node_id = node.nodeid.Identifier
        self.data_signal.emit(['update_settings_dictionary',(node_id, val)])



class OpcClientThread(QObject):
    upstream_signal = pyqtSignal(list)
    init_plot = pyqtSignal(dict)

    def __init__(self,input_q,endpoint,uri,parent=None,**kwargs):
        """Initialise Client

        Args:
            input_q (Queue Object): used for sending data to the client.
            endpoint (string): address of the OPC Server to be connected
            uri (string): name of the OPC Server
        """
        super().__init__(parent, **kwargs)
        self.input_queue = input_q
        self.sub_time = 50
        self.monitored_node = {key:value for key,value in node_structure.items() if (value['node_property']['category']=='server_variables') or (value['node_property']['category']=='shift_variables')}
        self.io_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='relay'}
        self.alarm_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='alarm'}
        self.hmi_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='client_input_1'}
        self.time_dict = {key:value for key,value in node_structure.items() if (value['node_property']['category']=='time_variables') or (value['node_property']['category']=='shift_time_variables')}
        self.uph_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='uph_variables'}


        self.light_tower_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='light_tower_setting'}
        self.user_access_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='user_access'}
        self.user_info_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='user_info'}
        self.lot_info_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='lot_input'}
        self.device_mode_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='device_status'}
        url = f"opc.tcp://{endpoint}"        
        self.client = Client(url=url)
        self.uri = uri
    
    def run(self):
        """
        Runs the client in asyncion mode
        """
        asyncio.run(self.client_start())



    async def machine_mode_update(self, mode_node:int, mode_data:bool):
        """light tower control share the same input with HMI control

        Args:
            mode_node (bool): data value of node
        """
        light_tower_settings_node = self.device_mode_dict[mode_node]['monitored_node']
        if mode_data == True and light_tower_settings_node!=None:
            settings_data = await self.read_from_opc(light_tower_settings_node, 2)
            #settings_data = bin(settings_data)#
            settings_data = format(settings_data, '06b')
            await self.light_tower_output(settings_data)

        
    async def read_from_opc(self, node:int, namespace_index:int):
        """read from OPC using the address and namespace index to get the stored value

        Args:
            node (int): node address
            namespace_index (int): namespace index

        Returns:
            any: returns the stored data value inside the corresponding node address
        """
        mode_var = self.client.get_node(ua.NodeId(node, namespace_index))
        data = await mode_var.read_value()
        return data



    async def light_tower_output(self, input_data:int):
        """outputs the light tower condition

        Args:
            input_data (string): a 6 dimension list of 0's and 1's in correspond for light tower on/off condition
        """
        #print(input_data)
        input_data = [int(d) for d in str(input_data)]
        await self.write_to_opc(13000,2,input_data[0],'Boolean')
        await self.write_to_opc(13001,2,input_data[1],'Boolean')
        await self.write_to_opc(13002,2,input_data[2],'Boolean') 
        await self.write_to_opc(13003,2,input_data[3],'Boolean')
        await self.write_to_opc(13004,2,input_data[4],'Boolean')
        await self.write_to_opc(13005,2,input_data[5],'Boolean')
        

    async def write_to_opc(self, node_id: int, namespace_index: int, data_value: any, data_type: str):
        input_node = self.client.get_node(ua.NodeId(node_id, namespace_index))
        #self.source_time = datetime.now()
        #print(data_value, data_type)
        await input_node.write_value(ua_variant_data_type(data_type,data_value))

    @pyqtSlot()
    async def client_start(self):        
        async with self.client as client:
            namespace_index = await client.get_namespace_index(self.uri)
     
            io_handler = SubIoHandler(self.upstream_signal)
            io_sub = await client.create_subscription(self.sub_time, io_handler)
            for node in self.io_dict.keys():
                var = client.get_node(ua.NodeId(node, namespace_index))
                await io_sub.subscribe_data_change(var,queuesize=1)

            info_handler = SubInfoHandler(self.upstream_signal)
            info_sub = await client.create_subscription(self.sub_time, info_handler) 
            for node in self.monitored_node.keys():
                var = client.get_node(ua.NodeId(node, namespace_index))
                await info_sub.subscribe_data_change(var,queuesize=1)

            alarm_handler = SubAlarmHandler(self.upstream_signal)  
            alarm_sub = await client.create_subscription(self.sub_time, alarm_handler) 
            for node in self.alarm_dict.keys():
                var = client.get_node(ua.NodeId(node, namespace_index))
                await alarm_sub.subscribe_data_change(var,queuesize=1)

            timer_handler = SubTimerHandler(self.upstream_signal)  
            time_sub = await client.create_subscription(self.sub_time, timer_handler) 
            for node in self.time_dict.keys():
                var = client.get_node(ua.NodeId(node, namespace_index))
                await time_sub.subscribe_data_change(var,queuesize=1)

            for node,value in self.uph_dict.items():
                var = client.get_node(ua.NodeId(node, namespace_index))
                current_value = await var.read_value()
                value['node_property']['initial_value'] = current_value
                self.uph_dict.update({node:value})

            self.init_plot.emit(self.uph_dict)

            uph_handler = SubUPHHandler(self.upstream_signal,self.uph_dict)  
            uph_sub = await client.create_subscription(self.sub_time, uph_handler) 
            for node,value in self.uph_dict.items():
                var = client.get_node(ua.NodeId(node, namespace_index))
                await uph_sub.subscribe_data_change(var,queuesize=1)
         
            device_mode_handler = SubDeviceModeHandler(self.machine_mode_update)
            device_mode_sub =  await client.create_subscription(self.sub_time, device_mode_handler) 
            for node in self.device_mode_dict.keys():
                var = client.get_node(ua.NodeId(node, namespace_index))
                await device_mode_sub.subscribe_data_change(var,queuesize=1)
            
            settings_dict = self.light_tower_dict | self.device_mode_dict | self.user_info_dict | self.user_access_dict | self.lot_info_dict
            settings_handler = SubSettingsHandler(self.upstream_signal)
            settings_sub = await client.create_subscription(self.sub_time, settings_handler)
            for node in settings_dict.keys():
                var = client.get_node(ua.NodeId(node, namespace_index))
                await settings_sub.subscribe_data_change(var, queuesize= 1)

            while True:
                await asyncio.sleep(0.01)#self.client_refresh_rate)             
                if not self.input_queue.empty():
                    hmi_signal = self.input_queue.get()
                    hmi_node_id = hmi_signal[0]
                    data_value = hmi_signal[1]
                    data_type = hmi_signal[2]
                    await self.write_to_opc(hmi_node_id, namespace_index,data_value,data_type)

                

