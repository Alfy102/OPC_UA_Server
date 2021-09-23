import asyncio
from collections import Counter
from asyncua import server, ua, Server
from datetime import timedelta, datetime
import asyncua
from asyncua.common import node
from asyncua.common.ua_utils import data_type_to_string
from asyncua.server.history_sql import HistorySQLite
from asyncua.ua.uatypes import Boolean, UInt16
import pandas as pd
import sqlite3
from io_layout_map import node_structure
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

class OpcServerThread(object):
    def __init__(self,plc_address,current_file_path,endpoint,uri,parent=None,**kwargs):
        self.plc_ip_address=plc_address
        self.file_path = current_file_path
        self.server = Server()
        self.endpoint = endpoint
        self.uri = uri

        self.monitored_node = {key:value for key,value in node_structure.items() if value['node_property']['category']=='server_variables'}
        self.io_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='relay'}
        self.alarm_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='alarm'}
        self.hmi_dict = {key:value for key,value in node_structure.items() if value['node_property']['category']=='hmi'}

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
            encapsulate = bytes(f"WR {start_device} {int(number_of_device)}\r\n",'utf-8')
        writer.write(encapsulate)
        await writer.drain()
        recv_value = await reader.readuntil(separator=b'\r\n') 
        recv_value = recv_value.decode("UTF-8").split()
        recv_value = [int(recv_value[i]) for i in range(len(recv_value))]
        writer.close()
        return recv_value

    async def scan_loop_plc(self,io_dict):
        group_list = [item[3] for item in list(io_dict.values())]
        group_item = list(set(group_list))
        io_dict_list = [dict(filter(lambda elem: elem[1][3]==group,io_dict.items())) for group in group_item]
        for io_dict in io_dict_list:
            lead_data = list(io_dict.values())[0]
            lead_device = lead_data[4]
            ip_address = lead_data[0]
            device_size = len(io_dict)
            #current_relay_list = await self.plc_tcp_socket_request(lead_device,device_size,ip_address,'read')
            i=0
            for key,value in io_dict.items():
                #alue[5]=current_relay_list[i]
                #asyncio.create_task(self.simple_write_to_opc(value[1],key,value[5]))
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
        self.source_time = datetime.utcnow()
        data_value = ua.DataValue(self.ua_variant_data_type(data_type, data_value),SourceTimestamp=self.source_time, ServerTimestamp=self.source_time)
        await self.server.write_attribute_value(node_id.nodeid, data_value)

    async def history_database_cleaner(self,database_file,table_name):
        conn = sqlite3.connect(self.file_path.joinpath(database_file))
        crsr = conn.cursor()
        crsr.execute(f"DELETE FROM '{table_name}';")
        conn.commit()
        conn.close()  

     
    def checkTableExists(self,dbcon, tablename):
        dbcur = dbcon.cursor()
        dbcur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tablename}';")

        if dbcur.fetchone()[0] == tablename:
            dbcur.close()
            return True

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
        
        node_category = [item['node_property']['category'] for item in node_structure.values()]
        node_category = list(set(node_category))
        for category in node_category:
            server_obj = await self.server.nodes.objects.add_object(namespace_index, category)
            for key, value in node_structure.items():
                if value['node_property']['category']==category:
                    node_id, variable_name, data_type, rw_status, historizing = key, value['name'], value['node_property']['data_type'], value['node_property']['rw'],value['node_property']['history']
                    
                    if historizing and self.checkTableExists(self.conn, f"{namespace_index}_{node_id}"):
                        previous_data = pd.read_sql_query(f"SELECT Value FROM '{namespace_index}_{node_id}' ORDER BY _Id DESC LIMIT 1", self.conn)
                        previous_value = previous_data.iloc[0]['Value']
                        initial_value = self.data_type_conversion(data_type, previous_value)
                    else:
                        initial_value = value['node_property']['initial_value']              
                    server_var = await server_obj.add_variable(ua.NodeId(node_id,namespace_index), variable_name, self.ua_variant_data_type(data_type,initial_value))
                    await server_var.set_writable()
                    if category == 'hmi':
                        await hmi_sub.subscribe_data_change(server_var,queuesize=1)
                    if historizing:
                        await self.server.historize_node_data_change(server_var, period=None, count=10000)

        self.conn.close()

        for key, value in self.monitored_node.items():
            node_id = value['monitored_node']
            if node_id != None:
                server_var = self.server.get_node(ua.NodeId(node_id, namespace_index))
                await var_sub.subscribe_data_change(server_var,queuesize=1)



        combined_dict = self.

        async with self.server:
            while True:
                await asyncio.sleep(0.1)
                #await asyncio.create_task(self.scan_loop_plc(combined_dict))






