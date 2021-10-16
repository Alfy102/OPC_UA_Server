import asyncio
from asyncua import ua, Server
from datetime import timedelta, datetime
from asyncua.server.history_sql import HistorySQLite
from pathlib import Path
import pandas as pd
import sqlite3
from io_layout_map import node_structure
import collections
import time
from comm_protocol import (plc_tcp_socket_read, 
                           plc_tcp_socket_write, 
                           ua_variant_data_type, 
                           data_type_conversion)
#io_dict standard dictionary: {variables_id:[device_ip, variables_ns, device_name, category_name,variable_name,0]}
#hmi_signal standard: (namespace, node_id, data_value)

class SubHmiHandler(object):
    
    def __init__(self,hmi_dictionary,plc_ip_address,port_number):
        """initialise SubHmiHandler 

        Args:
            hmi_dictionary (dictionary): dictionary containing the values associated with hmi nodes
            plc_ip_address (string): string of ipaddress 
            port_number ([type]): port number in string
        """
        self.hmi_structure = hmi_dictionary
        self.plc_adress = plc_ip_address
        self.port_number = port_number
    async def datachange_notification(self, node, val, data):
        """This will be called whenever a datachange happens on the subscribed node

        Args:
            node (node object): [description]
            val (int or string): [description]
            data (monitored_data object): [description]
        """
        node_identifier = node.nodeid.Identifier
        relay_name= self.hmi_structure[node_identifier]['name']
        await plc_tcp_socket_write(self.plc_adress,self.port_number,relay_name,val)

class SubVarHandler(object):
    def __init__(self,monitored_dict,count,get_node,yield_calculation,write_to_opc):
        self.monitored_node = monitored_dict
        self.count_node=count
        self.get_node = get_node
        self.yield_calculation = yield_calculation
        self.write_to_opc = write_to_opc
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        corr_var_node = [key for key,value in self.monitored_node.items() if value['monitored_node']==node_identifier][0]
        data_type = self.monitored_node[corr_var_node]['node_property']['data_type']
        data_value = int(val)
        new_value = asyncio.create_task(self.count_node(corr_var_node, data_value, data_type)) #(namespace, node id, amount)
        new_value = await self.count_node(corr_var_node, data_value, data_type) #(namespace, node id, amount)
        if corr_var_node == 10004: #if the node is lot total pass
            out_value = new_value
            in_value_node = self.get_node(10002)
            in_value_data = await in_value_node.read_value()
            data_type = self.monitored_node[10011]['node_property']['data_type']
            total_yield = self.yield_calculation(in_value_data, out_value)
            asyncio.create_task(self.write_to_opc(10011, total_yield, data_type))

class SubShiftVarHandler(object):
    def __init__(self,monitored_dict,count,get_node,yield_calculation,write_to_opc):
        self.monitored_node = monitored_dict
        self.count_node=count
        self.get_node = get_node
        self.yield_calculation = yield_calculation
        self.write_to_opc = write_to_opc
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        corr_var_node = [key for key,value in self.monitored_node.items() if value['monitored_node']==node_identifier][0]
        data_type = self.monitored_node[corr_var_node]['node_property']['data_type']
        data_value = int(val)
        new_value = await self.count_node(corr_var_node, data_value, data_type) #(namespace, node id, amount)
        if corr_var_node == 10022: #if the node is shift total pass
            out_value = new_value
            in_value_node = self.get_node(10020) #get value of qty in for shift variables
            in_value_data = await in_value_node.read_value()
            data_type = self.monitored_node[10028]['node_property']['data_type'] #get yield data type
            total_yield = self.yield_calculation(in_value_data, out_value)
            asyncio.create_task(self.write_to_opc(10028, total_yield, data_type))

class SubDeviceModeHandler(object):
    def __init__(self,mode_dict,mode_update):
        self.device_mode = mode_dict
        self.mode_update = mode_update
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        asyncio.create_task(self.mode_update(node_identifier, val))

class SubUPHCalculation(object):
    def __init__(self,uph_dict,get_node,write_to_opc):
        self.get_node = get_node
        self.write_to_opc = write_to_opc
        self.uph_list = [0,0]
        self.uph_dict = uph_dict
        self.uph_array = []
    async def datachange_notification(self, node, val, data):
        current_value_node = self.get_node(10021) #get current value of qty out
        current_value = await current_value_node.read_value()
        production_uph_data_type = node_structure[10030]['node_property']['data_type']
        operation_device_mode = self.get_node(10070)
        operation_flag = await operation_device_mode.read_value()
        if sum(self.uph_list) == 0:
            self.uph_list.pop(0)
            self.uph_list.append(current_value)
        self.uph_list.pop(0)
        self.uph_list.append(current_value)
        uph = self.uph_calculation(self.uph_list[0],self.uph_list[1])
        if operation_flag == True:
            self.uph_array.append(uph)
        asyncio.create_task(self.write_to_opc(10030, uph, production_uph_data_type)) #write to production uph

        if (val == 0 or val==30) and operation_flag == True:
            average_uph = self.average_uph(self.uph_array)
            self.uph_array.clear()
            current_hour_node = self.get_node(10063) 
            current_hour = await current_hour_node.read_value()
            self.update_uph_plot(average_uph,current_hour,val)
            
    def update_uph_plot(self,average_uph,hour,minute):
        slot_name = f"uph_{hour:02}_{minute:02}"
        node_id = [key for key,value in self.uph_dict.items() if value['name']==slot_name][0]
        print(f"slotname {slot_name} {node_id}")
        data_type = self.uph_dict[node_id]['node_property']['data_type']
        asyncio.create_task(self.write_to_opc(node_id, average_uph, data_type))

    def average_uph(self,uph_hour):
        average_uph = sum(uph_hour) / len(uph_hour)
        return average_uph
    def uph_calculation(self,initial_value, current_value):
        uph = (current_value-initial_value)*60 
        return uph

class OpcServerThread(object):
    def __init__(self,plc_address,current_file_path,endpoint,server_refresh_rate,uri,parent=None,**kwargs):
        ip_address = plc_address.split(':')
        self.plc_ip_address=ip_address[0]
        self.port_number = ip_address[1]
        self.file_path = current_file_path
        self.server = Server()
        self.endpoint = endpoint
        self.uri = uri
        self.namespace_index = 0
        self.server_refresh_rate = server_refresh_rate
        self.monitored_node = {key:value for key,value in node_structure.items() if value['node_property']['category']=='server_variables'}
        self.shift_monitored_node = {key:value for key,value in node_structure.items() if value['node_property']['category']=='shift_variables'}
        self.shift_time_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='shift_time_variables'}
        self.io_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='relay'}
        self.alarm_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='alarm'}
        self.hmi_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='hmi'}
        self.lot_time_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='time_variables'}
        self.uph_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='uph_variables'}
        self.mode_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='device_mode'}
        self.plc_clock_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='plc_clock'}
        self.node_structure = node_structure
        self.system_clock = 0

        #delay of subscribtion time in ms. reducing this value will cause server lag.
        self.sub_time = 50
        self.hmi_sub = 10
        asyncio.run(self.opc_server())

    async def count_node(self,node_id,data_value, data_type):
        node = self.server.get_node(self.get_node(node_id)) 
        current_value = await node.read_value()
        new_value = current_value + data_value
        asyncio.create_task(self.simple_write_to_opc(node_id, new_value, data_type))
        return new_value
    


    def yield_calculation(self,in_value, out_value):
        if in_value == 0 or out_value==0:
            total_yield=0.0
        else:
            total_yield = (out_value/in_value)*100
            total_yield = round(total_yield, 2)       
        return total_yield

    async def mode_update(self,node_id, data_value):
        node_property = self.mode_dict[node_id]
        node_property['node_property']['initial_value'] = data_value
        node_property.update({'flag_time':datetime.now()})
        self.mode_dict.update({node_id:node_property})
        for key,value in self.lot_time_dict.items():
            if value['monitored_node']==node_id:
                if data_value == True:
                    node_id = self.get_node(key)
                    value['node_property']['initial_value']= await node_id.read_value()     
                self.lot_time_dict.update({key:value})
        for key,value in self.shift_time_dict.items():
            if value['monitored_node']==node_id and data_value == True:
                if data_value == True:
                    node_id = self.get_node(key)
                    value['node_property']['initial_value']= await node_id.read_value()         
                self.lot_time_dict.update({key:value})
 
    def timer_function(self, time_dict):
        for node_id,value in time_dict.items():
            corr_flag_node = value['monitored_node']
            if corr_flag_node != None:
                device_mode = self.mode_dict[corr_flag_node]['node_property']['initial_value']
                if device_mode == True:
                    data_type = value['node_property']['data_type']
                    flag_time = self.mode_dict[corr_flag_node]['flag_time']
                    delta_time = self.convert_string_to_time(value['node_property']['initial_value'])
                    duration = self.duration(flag_time, delta_time)
                    asyncio.create_task(self.simple_write_to_opc(node_id,duration,data_type))
    
    async def system_uptime(self):    
        lot_start_node = self.get_node(10054)
        lot_start_datetime = await lot_start_node.read_value()
        current_device_mode = self.mode_dict[10070]['node_property']['initial_value']
        if lot_start_datetime != 'Null' and current_device_mode == True:
            uptime = self.uptime(lot_start_datetime)
            uptime = str(uptime).split('.')[0]
            asyncio.create_task(self.simple_write_to_opc(10044, uptime, 'String')) #write to lot_uptime

        shift_start_node = self.get_node(10055)
        shift_start_datetime = await shift_start_node.read_value()
        if shift_start_datetime != 'Null':
            uptime = self.uptime(shift_start_datetime)
            uptime = str(uptime).split('.')[0]
            asyncio.create_task(self.simple_write_to_opc(10040, uptime, 'String')) #write to shift_uptime

    def duration(self,start_time, delta_time):
        if isinstance(start_time, str):
            start_time = self.convert_string_to_time(start_time)
        if isinstance(delta_time, str):
            delta_time = self.convert_string_to_time(delta_time)
        duration = datetime.now() - start_time + delta_time
        return duration

    def uptime(self, start_datetime):
        if isinstance(start_datetime, str):
                start_time = self.convert_string_to_datetime(start_datetime)
        uptime = datetime.now() - start_time
        return uptime


    def convert_string_to_datetime(self,time_string):
        try:
            date_time = datetime.strptime(time_string,"%d.%m.%Y %H:%M:%S")
        except:
            date_time = datetime.strptime(time_string,"%d.%m.%Y %H:%M")
        return date_time

    def convert_string_to_time(self,time_string):
        try:
            delta_time = datetime.strptime(time_string,"%H:%M:%S.%f")
        except:
            delta_time = datetime.strptime(time_string,"%H:%M:%S")
        delta_time = timedelta(hours=delta_time.hour, minutes=delta_time.minute, seconds=delta_time.second, microseconds=delta_time.microsecond)
        return delta_time

    def get_node(self, node_id):
        node =  self.server.get_node(ua.NodeId(node_id, self.namespace_index))
        return node
    
    def checkTableExists(self,dbcon, tablename):
        dbcur = dbcon.cursor()
        dbcur.execute(f"SELECT * FROM sqlite_master WHERE type='table' AND name='{tablename}';")
        table = dbcur.fetchone()
        if table is not None:
            if tablename in table:
                dbcur.close()
                return True
        else:   
            dbcur.close()
            return False

    async def scan_loop_plc(self,io_dict):
        lead_data = io_dict[list(io_dict.keys())[0]]
        lead_device = lead_data['name']
        device_size = len(io_dict)
        current_relay_list = await plc_tcp_socket_read(self.plc_ip_address,self.port_number,lead_device,device_size)
        
        for i,(key,value) in enumerate(io_dict.items()):
            node_id = key
            data_type = value['node_property']['data_type']
            asyncio.create_task(self.simple_write_to_opc(node_id, current_relay_list[i], data_type))
            

    async def simple_write_to_opc(self, node_id, data_value, data_type):
        node_id=self.get_node(node_id)
        self.source_time = datetime.now()
        data_value = ua.DataValue(ua_variant_data_type(data_type, data_value),SourceTimestamp=self.source_time, ServerTimestamp=self.source_time)
        await self.server.write_attribute_value(node_id.nodeid, data_value)

    async def node_creation(self,database_file,node_category_list):
        hmi_handler = SubHmiHandler(self.hmi_dict,self.plc_ip_address,self.port_number)
        hmi_sub = await self.server.create_subscription(self.hmi_sub, hmi_handler)

        mode_handler = SubDeviceModeHandler(self.mode_dict,self.mode_update)
        device_mode_sub = await self.server.create_subscription(self.sub_time, mode_handler)
        conn = sqlite3.connect(self.file_path.joinpath(database_file))
        for category in node_category_list:
                    server_obj = await self.server.nodes.objects.add_object(self.namespace_index, category)
                    for key, value in node_structure.items():
                        if value['node_property']['category']==category:
                            node_id, variable_name, data_type, rw_status, historizing = key, value['name'], value['node_property']['data_type'], value['node_property']['rw'],value['node_property']['history']
                            
                            if historizing==True and self.checkTableExists(conn, f"{self.namespace_index}_{node_id}"):
                                previous_data = pd.read_sql_query(f"SELECT Value FROM '{self.namespace_index}_{node_id}' ORDER BY _Id DESC LIMIT 1", conn)
                                if not previous_data.empty:
                                    previous_value = previous_data.iloc[0]['Value']
                                    initial_value = data_type_conversion(data_type, previous_value)
                                else:
                                    initial_value = value['node_property']['initial_value']
                            else:
                                initial_value = value['node_property']['initial_value']           
                            server_var = await server_obj.add_variable(ua.NodeId(node_id,self.namespace_index), str(variable_name), ua_variant_data_type(data_type,initial_value))
                            if rw_status:
                                await server_var.set_writable()
                            if category == 'client_input':
                                await hmi_sub.subscribe_data_change(server_var,queuesize=1)
                            if category == 'device_mode':
                                await device_mode_sub.subscribe_data_change(server_var,queuesize=1)
                            if historizing and category == 'time_variables':
                                await self.server.historize_node_data_change(server_var, period=None, count=10)
                            if historizing and category != 'time_variables':
                                await self.server.historize_node_data_change(server_var, period=None, count=100)
        conn.close()


    async def opc_server(self):
        database_file = "variable_history.sqlite3"
        

        #Configure server to use sqlite as history database (default is a simple memory dict)
        self.server.iserver.history_manager.set_storage(HistorySQLite(self.file_path.joinpath(database_file)))
        await self.server.init()

        #populate the server with the defined nodes imported from io_layout_map
        self.server.set_endpoint(f"opc.tcp://{self.endpoint}")
        
        self.namespace_index = await self.server.register_namespace(self.uri)

        
        node_category = [item['node_property']['category'] for item in node_structure.values()]
        node_category = list(set(node_category))
        await self.node_creation(database_file,node_category)
        

        #subscribed to minute interval activity for UPH Calculation
        minute_handler = SubUPHCalculation(self.uph_dict,self.get_node,self.simple_write_to_opc)
        minute_var_sub = await self.server.create_subscription(self.sub_time, minute_handler)
        await minute_var_sub.subscribe_data_change(self.get_node(10064),queuesize=1)


        var_handler = SubVarHandler(self.monitored_node,self.count_node,self.get_node,self.yield_calculation,self.simple_write_to_opc)
        var_sub = await self.server.create_subscription(self.sub_time, var_handler)
        for value in self.monitored_node.values():
            node_id = value['monitored_node']
            if node_id != None:
                server_var = self.server.get_node(self.get_node(node_id))
                await var_sub.subscribe_data_change(server_var,queuesize=1)

        shift_var_handler = SubShiftVarHandler(self.shift_monitored_node,self.count_node,self.get_node,self.yield_calculation,self.simple_write_to_opc)
        shift_var_sub = await self.server.create_subscription(self.sub_time, shift_var_handler)
        
        for value in self.shift_monitored_node.values():
            node_id = value['monitored_node']
            if node_id != None:
                server_var = self.server.get_node(self.get_node(node_id))
                await shift_var_sub.subscribe_data_change(server_var,queuesize=1)

        alarm_dict = collections.OrderedDict(sorted(self.alarm_dict.items()))
        io_dict = collections.OrderedDict(sorted(self.io_dict.items()))
        mode_dict = collections.OrderedDict(sorted(self.mode_dict.items()))
        plc_clock_dict = collections.OrderedDict(sorted(self.plc_clock_dict.items()))
        async with self.server:
            while True:
                #tic = time.time()
                await self.scan_loop_plc(plc_clock_dict)
                await asyncio.sleep(self.server_refresh_rate)
                await self.scan_loop_plc(alarm_dict)
                await self.scan_loop_plc(io_dict)
                await self.scan_loop_plc(mode_dict)
                self.timer_function(self.lot_time_dict | self.shift_time_dict)
                asyncio.create_task(self.system_uptime())
                #toc = time.time()
                #print(f"{toc - tic- self.server_refresh_rate :.9f}")

def main():
    uri = "PLC_Server"
    plc_address = '127.0.0.1:8501'
    file_path = Path(__file__).parent.absolute()
    endpoint = "localhost:4840/gshopcua/server"
    server_refresh_rate = 0.1
    OpcServerThread(plc_address,file_path,endpoint,server_refresh_rate,uri)

if __name__ == "__main__":
    main()