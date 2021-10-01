import asyncio
from asyncua import ua, Server
from datetime import timedelta, datetime
from asyncua.server.history_sql import HistorySQLite
from asyncua.ua.uaprotocol_auto import TimeZoneDataType

import pandas as pd
import sqlite3
from io_layout_map import node_structure
import collections
import time
#io_dict standard dictionary: {variables_id:[device_ip, variables_ns, device_name, category_name,variable_name,0]}
#hmi_signal standard: (namespace, node_id, data_value)


class SubHmiHandler(object):
    def __init__(self,hmi_dictionary,plc_tcp_socket_request):
        self.hmi_structure = hmi_dictionary
        self.plc_send = plc_tcp_socket_request
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        relay_name= self.hmi_structure[node_identifier]['name']
        device = self.hmi_structure[node_identifier]['node_property']['device']
        #print(f"from server {relay_name},{val},{device}")
        await self.plc_send(relay_name,val,device,'write')

class SubVarHandler(object):
    def __init__(self,monitored_dict,count):
        self.monitored_node = monitored_dict
        self.count_node=count
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        namespace_index = node.nodeid.NamespaceIndex
        corr_var_node = [key for key,value in self.monitored_node.items() if value['monitored_node']==node_identifier][0]
        data_type = self.monitored_node[corr_var_node]['node_property']['data_type']
        data_value = int(val)
        asyncio.create_task(self.count_node(namespace_index, corr_var_node, data_value, data_type)) #(namespace, node id, amount)

class SubTimerHandler(object):
    def __init__(self,time_dict,update_time_dict):
        self.time_dict = time_dict
        self.update_time_dict = update_time_dict
    
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        namespace_index = node.nodeid.NamespaceIndex
        corr_time_node = [key for key,value in self.time_dict.items() if value['monitored_node']==node_identifier][0]
        value = self.time_dict[corr_time_node]
        time_trigger = data.monitored_item.Value.SourceTimestamp
        time_trigger = time_trigger.strftime("%Y-%d-%m %H:%M:%S.%f")
        value['node_property']['initial_value'] = time_trigger
        value.update({'monitored_node_status':val})        
        await self.update_time_dict(namespace_index, corr_time_node, value)

class OpcServerThread(object):
    def __init__(self,plc_address,current_file_path,endpoint,server_refresh_rate,uri,parent=None,**kwargs):
        self.plc_ip_address=plc_address
        self.file_path = current_file_path
        self.server = Server()
        self.endpoint = endpoint
        self.uri = uri
        self.uph_list = [0,0]
        self.uph_array = []

        self.server_refresh_rate = server_refresh_rate
        self.monitored_node = {key:value for key,value in node_structure.items() if value['node_property']['category']=='server_variables'}
        self.io_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='relay'}
        self.alarm_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='alarm'}
        self.hmi_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='hmi'}
        self.time_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='time_variables'}
        self.uph_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='uph_variables'}

        self.node_structure = node_structure
        #the scheduled database full cleanup
        self.time_cleanup = timedelta(days=7)
        #the schedule database reset
        self.stats_reset = timedelta(days=1)
        #delay of subscribtion time in ms. reducing this value will cause server lag.
        self.sub_time = 50
        self.hmi_sub = 10
        asyncio.run(self.opc_server())

    async def count_node(self, name_space,node_id,data_value, data_type):
        node = self.server.get_node(ua.NodeId(node_id, name_space)) 
        current_value = int(await node.read_value())
        new_value = current_value + data_value
        asyncio.create_task(self.simple_write_to_opc(name_space, node_id, new_value, data_type))
        if self.monitored_node[node_id]['name']=='total_pass':
            await self.yield_calculation(new_value,name_space)

    async def update_time_dict(self, namespace_index, key, value):
        time_var_node_id = self.server.get_node(ua.NodeId(key, namespace_index))
        delta_time = await time_var_node_id.read_value()
        delta_time = datetime.strptime(delta_time,"%H:%M:%S.%f")
        delta_time = timedelta(hours=delta_time.hour, minutes=delta_time.minute, seconds=delta_time.second, microseconds=delta_time.microsecond)
        value.update({'delta_time':delta_time})
        self.time_dict.update({key:value})
    
    async def watch_timer(self, namespace_index):
        for key,value in self.time_dict.items():
            time_var_node = key
            data_type = value['node_property']['data_type']
            flag_node_status = value['monitored_node_status']
            flag_time = value['node_property']['initial_value']
            flag_time = datetime.strptime(flag_time,"%Y-%d-%m %H:%M:%S.%f")
            delta_time = value['delta_time']
            if flag_node_status == True:
                duration = datetime.now() - flag_time + delta_time
                asyncio.create_task(self.simple_write_to_opc(namespace_index,time_var_node,duration,data_type))
    
    async def uph_calculation(self, qty_in_var, namespace_index):
        qty_in_value = await qty_in_var.read_value()
        self.uph_list.append(qty_in_value)
        self.uph_list.pop(0)
        current_hour = datetime.now().replace(microsecond=0, second=0)
        slot_name = f"uph_{current_hour.hour:02}_{current_hour.minute:02}"

        uph = (self.uph_list[1]-self.uph_list[0])*60
        asyncio.create_task(self.simple_write_to_opc(namespace_index,10016,uph,'UInt16'))
        self.uph_array.append(uph)
        print(self.uph_array)
        for key, value in self.uph_dict.items():
            if slot_name == value['name']:
                average_uph = sum(self.uph_array) / len(self.uph_array)
                data_type = value['node_property']['data_type']
                self.uph_array.clear()
                asyncio.create_task(self.simple_write_to_opc(namespace_index, key, average_uph, data_type))
    
    async def yield_calculation(self,new_value,name_space):
        qty_in_node_id = [key for key,value in self.monitored_node.items() if value['name']=='total_quantity_in'][0]
        yield_node = [key for key,value in self.monitored_node.items() if value['name']=='total_yield'][0]
        yield_data_type = self.monitored_node[yield_node]['node_property']['data_type']
        qty_in_node_id = self.server.get_node(ua.NodeId(qty_in_node_id, name_space)) 
        qty_in_value = int(await qty_in_node_id.read_value())
        if qty_in_value == 0 or new_value==0:
            total_yield=0.0
        else:
            total_yield = (new_value/qty_in_value)*100
            total_yield = round(total_yield, 2)       
        asyncio.create_task(self.simple_write_to_opc(name_space, yield_node, total_yield, yield_data_type))

    async def plc_tcp_socket_request(self,start_device,number_of_device,device,mode):
        ipaddress = self.plc_ip_address[device]
        ipaddress = ipaddress.split(':')
        reader, writer = await asyncio.open_connection(ipaddress[0], ipaddress[1])
        if mode == 'read':
            encapsulate = bytes(f"RDS {start_device} {number_of_device}\r\n","utf-8")
        elif mode == 'write':
            message = f"WR {start_device} {int(number_of_device)}\r\n"
            encapsulate = bytes(message,'utf-8')
        writer.write(encapsulate)
        await writer.drain()
        recv_value = await reader.readuntil(separator=b'\r\n') 
        recv_value = recv_value.decode("UTF-8").split()
        recv_value = [int(recv_value[i]) for i in range(len(recv_value))]
        writer.close()
        return recv_value

    async def scan_loop_plc(self,io_dict,namespace_index):
        lead_data = io_dict[list(io_dict.keys())[0]]
        lead_device = lead_data['name']
        hardware_name = lead_data['node_property']['device']
        device_size = len(io_dict)
        current_relay_list = await self.plc_tcp_socket_request(lead_device,device_size,hardware_name,'read')
        i=0
        for key,value in io_dict.items():
            node_id = key
            data_type = value['node_property']['data_type']
            asyncio.create_task(self.simple_write_to_opc(namespace_index, node_id, current_relay_list[i], data_type))
            i+=1

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

    def data_type_conversion(self, data_type, data_value):
        if data_type == 'UInt16':
            data_value = int(data_value)
        elif data_type == 'UInt32':
            data_value = int(data_value)
        elif data_type == 'UInt64':    
            data_value = int(data_value)
        elif data_type == 'String':
            data_value = str(data_value)
        elif data_type == 'Boolean':
            data_value = bool(data_value)
        elif data_type == 'Float':
            data_value = float(data_value)
        return data_value

    async def simple_write_to_opc(self, namespace, node_id, data_value, data_type):
        node_id=self.server.get_node(ua.NodeId(node_id, namespace))
        self.source_time = datetime.now()
        data_value = ua.DataValue(self.ua_variant_data_type(data_type, data_value),SourceTimestamp=self.source_time, ServerTimestamp=self.source_time)
        await self.server.write_attribute_value(node_id.nodeid, data_value)


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

    async def opc_server(self):
        self.database_file = "variable_history.sqlite3"
        self.conn = sqlite3.connect(self.file_path.joinpath(self.database_file))

        #Configure server to use sqlite as history database (default is a simple memory dict)
        self.server.iserver.history_manager.set_storage(HistorySQLite(self.file_path.joinpath(self.database_file)))
        await self.server.init()

        #populate the server with the defined nodes imported from io_layout_map
        self.server.set_endpoint(f"opc.tcp://{self.endpoint}")
        
        namespace_index = await self.server.register_namespace(self.uri)

        hmi_handler = SubHmiHandler(self.hmi_dict,self.plc_tcp_socket_request)
        hmi_sub = await self.server.create_subscription(self.hmi_sub, hmi_handler)

        var_handler = SubVarHandler(self.monitored_node,self.count_node)
        var_sub = await self.server.create_subscription(self.sub_time, var_handler)
        
        timer_handler = SubTimerHandler(self.time_dict,self.update_time_dict)  
        time_sub = await self.server.create_subscription(self.sub_time, timer_handler) 

        node_category = [item['node_property']['category'] for item in node_structure.values()]
        node_category = list(set(node_category))
        for category in node_category:
            server_obj = await self.server.nodes.objects.add_object(namespace_index, category)
            for key, value in node_structure.items():
                if value['node_property']['category']==category:
                    node_id, variable_name, data_type, rw_status, historizing = key, value['name'], value['node_property']['data_type'], value['node_property']['rw'],value['node_property']['history']
                    
                    if historizing and self.checkTableExists(self.conn, f"{namespace_index}_{node_id}"):
                        previous_data = pd.read_sql_query(f"SELECT Value FROM '{namespace_index}_{node_id}' ORDER BY _Id DESC LIMIT 1", self.conn)
                        if not previous_data.empty:
                            previous_value = previous_data.iloc[0]['Value']
                            initial_value = self.data_type_conversion(data_type, previous_value)
                        else:
                            initial_value = value['node_property']['initial_value']
                    else:
                        initial_value = value['node_property']['initial_value']           
                    server_var = await server_obj.add_variable(ua.NodeId(node_id,namespace_index), str(variable_name), self.ua_variant_data_type(data_type,initial_value))
                    if rw_status:
                        await server_var.set_writable()
                    if category == 'hmi':
                        await hmi_sub.subscribe_data_change(server_var,queuesize=1)
                    if historizing and category == 'time_variables':
                        await self.server.historize_node_data_change(server_var, period=None, count=10)
                    if historizing and category != 'time_variables':
                        await self.server.historize_node_data_change(server_var, period=None, count=1000)
                    if key == 10003:
                        qty_in_var = server_var#UPH calculation based on Qty out rate
                        last_in_value = await qty_in_var.read_value()
                        self.uph_list.append(last_in_value)
                        self.uph_list.pop(0)


        test_array = await server_obj.add_variable(ua.Nodeid(5000,namespace_index),'array_test',ua.Variant(None, ua.VariantType.UInt16, is_array = True))
        await test_array.set_writable()

        self.conn.close()
        for value in self.time_dict.values():
            monitored_node = value['monitored_node']
            time_var = self.server.get_node((ua.NodeId(monitored_node, namespace_index)))
            await time_sub.subscribe_data_change(time_var,queuesize=1)


        for key, value in self.monitored_node.items():
            node_id = value['monitored_node']
            if node_id != None:
                server_var = self.server.get_node(ua.NodeId(node_id, namespace_index))
                await var_sub.subscribe_data_change(server_var,queuesize=1)
        
        alarm_dict = collections.OrderedDict(sorted(self.alarm_dict.items()))
        io_dict = collections.OrderedDict(sorted(self.io_dict.items()))
        next_minute = (datetime.now().replace(microsecond=0, second=0)) + timedelta(minutes=1)
        async with self.server:
            while True:
                #tic = time.perf_counter()
                current_time = datetime.now().replace(microsecond=0, second=0)
                if current_time == next_minute:
                    await self.uph_calculation(qty_in_var,namespace_index)
                    next_minute = current_time + timedelta(minutes=1)
                await asyncio.sleep(self.server_refresh_rate)
                await self.scan_loop_plc(alarm_dict,namespace_index)
                await self.scan_loop_plc(io_dict,namespace_index)
                asyncio.create_task(self.watch_timer(namespace_index))
                #toc = time.perf_counter()
                #print(f"{toc - tic:.9f}")




