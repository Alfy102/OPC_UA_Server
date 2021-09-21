import asyncio
from collections import Counter
from asyncua import ua, Server
from datetime import timedelta, datetime
from asyncua.server.history_sql import HistorySQLite
import pandas as pd
import sqlite3
import io_layout_map as iomp
import time
#io_dict standard dictionary: {variables_id:[device_ip, variables_ns, device_name, category_name,variable_name,0]}
#hmi_signal standard: (namespace, node_id, data_value)


class SubHmiHandler(object):
    def __init__(self,hmi_dictionary,plc_tcp_socket_request):
        self.hmi_structure = hmi_dictionary
        self.plc_send = plc_tcp_socket_request
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        from_hmi_struct = self.hmi_structure[node_identifier]
        ip_address = from_hmi_struct[0]
        await self.plc_send(from_hmi_struct[4],val,ip_address,'write')

class SubVarHandler(object):
    def __init__(self,monitored_dict,count,write_to_opc):
        self.monitored_node = monitored_dict
        self.write_to_opc = write_to_opc
        self.count_node=count
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        items = self.monitored_node[node_identifier]
        asyncio.create_task(self.count_node(items[0], items[1], val)) #(namespace, node id, amount)

class OpcServerThread(object):
    def __init__(self,plc_address,current_file_path,endpoint,parent=None,**kwargs):
        self.plc_ip_address=plc_address
        self.file_path = current_file_path
        self.server = Server()
        self.endpoint = endpoint
        #node dictionary pointing which node will connect to which node
        #{R100:Total quantity in, R101: Total Passed, R102: Total Failed, R103: Total Quantity Out}
        self.monitored_node = iomp.monitored_node
        self.time_node = iomp.monitored_time_node
        self.io_list = list(iomp.all_label_dict.keys())
        self.alarm_list = list(iomp.all_alarm_list)
        self.hmi_list = [item[0] for item in list(iomp.all_hmi_dict.values())]
        #the scheduled database full cleanup
        self.time_cleanup = timedelta(days=7)
        #the schedule database reset
        self.stats_reset = timedelta(days=1)
        #delay of subscribtion time in ms. reducing this value will cause server lag.
        self.sub_time = 50
        self.hmi_sub = 10
        asyncio.run(self.opc_server())

    async def count_node(self, name_space,node_id,data_value):
        node = self.server.get_node(ua.NodeId(node_id, name_space)) 
        current_value = await node.read_value()
        new_value = current_value + data_value
        asyncio.create_task(self.simple_write_to_opc(name_space, node_id, new_value))
        if node_id == 10006:
            qty_in_node_id = self.server.get_node(ua.NodeId(10004, 2)) 
            qty_in_value = await qty_in_node_id.read_value()
            total_yield = self.yield_calculation(new_value, qty_in_value)
            asyncio.create_task(self.simple_write_to_opc(2, 10012, total_yield))
 
    def yield_calculation(self,new_value,div_value):
        total_yield = (new_value/div_value)*100
        total_yield = round(total_yield, 2)
        return total_yield

    async def plc_tcp_socket_request(self,start_device,number_of_device,ipaddress,mode):
        ipaddress = ipaddress.split(':')
        reader, writer = await asyncio.open_connection(ipaddress[0], ipaddress[1])
        if mode == 'read':
            encapsulate = bytes(f"RDS {start_device} {number_of_device}\r\n","utf-8")
        elif mode == 'write':
            encapsulate = bytes(f"WR {start_device} {number_of_device}\r\n",'utf-8')
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
            current_relay_list = await self.plc_tcp_socket_request(lead_device,device_size,ip_address,'read')
            i=0
            for key,value in io_dict.items():
                value[5]=current_relay_list[i]
                asyncio.create_task(self.simple_write_to_opc(value[1],key,value[5]))
                i+=1

    async def simple_write_to_opc(self, namespace, node_id, data_value):
        node_id=self.server.get_node(ua.NodeId(node_id, namespace))
        self.source_time = datetime.utcnow()
        if isinstance(data_value,int):
            data_value = ua.DataValue(ua.Variant(data_value, ua.VariantType.Int64),SourceTimestamp=self.source_time, ServerTimestamp=self.source_time)
        elif isinstance(data_value,float):
            data_value = ua.DataValue(ua.Variant(data_value, ua.VariantType.Float),SourceTimestamp=self.source_time, ServerTimestamp=self.source_time)
        elif isinstance(data_value,str):
            data_value = ua.DataValue(ua.Variant(data_value, ua.VariantType.String),SourceTimestamp=self.source_time, ServerTimestamp=self.source_time)
        await self.server.write_attribute_value(node_id.nodeid, data_value)

    async def history_database_cleaner(self,database_file,table_name):
        conn = sqlite3.connect(self.file_path.joinpath(database_file))
        crsr = conn.cursor()
        crsr.execute(f"DELETE FROM '{table_name}';")
        conn.commit()
        conn.close()  

    async def initialization_nodes(self, dictionary):
        node_dict={}
        node_dict.clear()
        for nodes in dictionary:
            var = self.server.get_node(ua.NodeId(nodes, 2))
            var_name = await var.read_display_name()
            parent_node = await var.get_parent()
            parent_name = await parent_node.read_display_name()
            device_node = await parent_node.get_parent()
            device_name = await device_node.read_display_name()
            device_ip = self.plc_ip_address[device_name.Text]
            current_value = await var.read_value()          
            node_dict.update({nodes:[device_ip, 2, device_name.Text,parent_name.Text,var_name.Text,current_value]})

        return node_dict

    async def opc_server(self):
        self.database_file = "variable_history.sqlite3"
        self.conn = sqlite3.connect(self.file_path.joinpath(self.database_file))
        #Configure server to use sqlite as history database (default is a simple memory dict)
        self.server.iserver.history_manager.set_storage(HistorySQLite(self.file_path.joinpath(self.database_file)))
        await self.server.init()
        self.server.set_endpoint(f"opc.tcp://{self.endpoint}") 
     
        #load nodes structure from XML file path
        await self.server.import_xml(self.file_path.joinpath("standard_server_structure.xml"))
        await self.server.load_data_type_definitions()

        #load all the nodes inside the XML file into a dictionary variables for easier data handling
        #io_dict standard dictionary: {io_id:[device_ip, variables_ns, device_name, category_name,variable_name,0]}
        io_dict = await self.initialization_nodes(self.io_list)
        alarm_dict = await self.initialization_nodes(self.alarm_list)
        hmi_dict = await self.initialization_nodes(self.hmi_list)

        #create hmi subscription handler and initialize it with current value of plc relay     
        hmi_handler = SubHmiHandler(hmi_dict,self.plc_tcp_socket_request)
        hmi_sub = await self.server.create_subscription(self.hmi_sub, hmi_handler)  
        for key,value in hmi_dict.items():
            hmi_var = self.server.get_node(ua.NodeId(key,value[1]))
            await hmi_var.set_writable()
            await hmi_sub.subscribe_data_change(hmi_var,queuesize=1)
    
        #create subscription for the monitored nodes and fill with last known data in database
        var_handler = SubVarHandler(self.monitored_node,self.count_node,self.simple_write_to_opc)
        var_sub = await self.server.create_subscription(self.sub_time, var_handler) 
        #initiate infos from database
        for key,value in self.monitored_node.items():
            try:
                previous_data = pd.read_sql_query(f"SELECT Value FROM '{value[0]}_{value[1]}' ORDER BY _Id DESC LIMIT 1", self.conn)
                initial_value = previous_data.iloc[0]['Value']
            except:
                initial_value = 0

            asyncio.create_task(self.simple_write_to_opc(value[0], value[1], int(initial_value)))
            monitored_var = self.server.get_node(ua.NodeId(key,value[0]))
            await var_sub.subscribe_data_change(monitored_var,queuesize=1)
            await self.server.historize_node_data_change(monitored_var, period=None, count=0)

        #initiate time from database, no subscription is needed. Only last 100 items rememebered
        for value in self.time_node.values():
            try:
                previous_data = pd.read_sql_query(f"SELECT Value FROM '{value[0]}_{value[1]}' ORDER BY _Id DESC LIMIT 1", self.conn)
                initial_value = previous_data.iloc[0]['Value']
            except:
                initial_value = '0:00:00'
            asyncio.create_task(self.simple_write_to_opc(value[0], value[1], initial_value))
            time_var = self.server.get_node(ua.NodeId(value[1],value[0]))
            await self.server.historize_node_data_change(time_var, period=None, count=100)
        self.conn.close()

        combined_dict = io_dict|alarm_dict

        async with self.server:
            while True:
                await asyncio.sleep(0.1)
                await asyncio.create_task(self.scan_loop_plc(combined_dict))






