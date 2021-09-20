import asyncio
from collections import Counter
from asyncua import ua, Server
from asyncua.common import node
from datetime import timedelta, datetime
from asyncua.server.history_sql import HistorySQLite
from asyncua.ua.uatypes import String
import pandas as pd
import sqlite3
from io_layout_map import monitored_node
#io_dict standard dictionary: {variables_id:[variables_ns, device_name, category_name,variable_name,0]}
#hmi_signal standard: (namespace, nnode_id, data_value)


class SubHmiHandler(object):
    def __init__(self,hmi_dictionary,plc_ip_address,plc_tcp_socket_request):
        self.hmi_structure = hmi_dictionary
        self.ip_address = plc_ip_address
        self.plc_send = plc_tcp_socket_request
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        from_hmi_struct = self.hmi_structure[node_identifier]
        ip_address = self.ip_address[from_hmi_struct[1]]
        await self.plc_send((from_hmi_struct[3],1,val),ip_address,'write')

class SubVarHandler(object):
    def __init__(self,monitored_dict,count):
        self.monitored_node = monitored_dict
        self.count_node=count
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        if val >0:
            value = self.monitored_node[node_identifier]
            await self.count_node((value[0], value[1], val)) #(namespace, node id, amount)

class OpcServerThread(object):
    def __init__(self,plc_address,current_file_path,endpoint,parent=None,**kwargs):
        self.device_structure={}
        self.plc_ip_address=plc_address
        self.file_path = current_file_path
        self.server = Server()
        self.endpoint = endpoint
        #node dictionary pointing which node will connect to which node
        #{R100:Total quantity in, R101: Total Passed, R102: Total Failed, R103: Total Quantity Out}
        self.monitored_node = monitored_node
        #the scheduled database full cleanup
        self.time_cleanup = timedelta(days=7)
        #the schedule database reset
        self.stats_reset = timedelta(days=1)
        #delay of subscribtion time in ms. reducing this value will cause server lag.
        self.sub_time = 50
        self.hmi_sub = 10
        asyncio.run(self.opc_server())


    async def count_node(self, data):
        node_id= self.server.get_node(ua.NodeId(data[1], data[0])) 
        current_value = await node_id.read_value()
        new_value = current_value + data[2]
        asyncio.create_task(self.simple_write_to_opc((data[0], data[1], new_value)))
        if data[1] == 10006:
            qty_in_node_id = self.server.get_node(ua.NodeId(10004, 2)) 
            qty_in_value = await qty_in_node_id.read_value()
            total_yield = self.yield_calculation(new_value, qty_in_value)
            asyncio.create_task(self.simple_write_to_opc((2, 10012, total_yield)))
 
    def yield_calculation(self,new_value,div_value):
        total_yield = (new_value/div_value)*100
        total_yield = round(total_yield, 2)
        return total_yield
    async def plc_tcp_socket_request(self,start_device,ipaddress,mode):
        ipaddress = ipaddress.split(':')
        reader, writer = await asyncio.open_connection(ipaddress[0], ipaddress[1])
        if mode == 'read':
            encapsulate = bytes(f"RDS {start_device[0]} {start_device[1]}\r\n","utf-8")
        elif mode == 'write':
            encapsulate = bytes(f"WRS {start_device[0]} {start_device[1]} {start_device[2]}\r\n",'utf-8')
        writer.write(encapsulate)
        await writer.drain()
        recv_value = await reader.readuntil(separator=b'\r\n') 
        recv_value = recv_value.decode("UTF-8").split()
        recv_value = [int(recv_value[i]) for i in range(len(recv_value))]
        writer.close()
        return recv_value

    async def scan_loop_plc(self,coil_cat_dict_list,device_coil_list,ip_list):
        for key,values in  coil_cat_dict_list.items():
            current_relay_list = await self.plc_tcp_socket_request(values,ip_list,'read')
            cat_filter = dict(filter(lambda elem: key in elem[1],device_coil_list.items()))
            cat_filter_keys = list(cat_filter.keys())
            asyncio.ensure_future(self.write_to_opc(current_relay_list,cat_filter,cat_filter_keys))

    async def write_to_opc(self,current_relay_list,cat_filter_items,cat_filter_keys):    
        for i in range(len(current_relay_list)):
            from_filter = cat_filter_items[cat_filter_keys[i]]
            from_filter[4]=current_relay_list[i]
            node_id=self.server.get_node(ua.NodeId(cat_filter_keys[i], 2))
            self.source_time = datetime.now()
            data_value = ua.DataValue(ua.Variant(current_relay_list[i], ua.VariantType.Int64),SourceTimestamp=self.source_time, ServerTimestamp=self.source_time)
            await self.server.write_attribute_value(node_id.nodeid, data_value)

    async def simple_write_to_opc(self, data):
        #hmi_signal = (namespace, node_id, data_value)
        node_id=self.server.get_node(ua.NodeId(data[1], data[0]))
        self.source_time = datetime.now()
        value = data[2]
        if isinstance(value,int):
            data_value = ua.DataValue(ua.Variant(value, ua.VariantType.Int64),SourceTimestamp=self.source_time, ServerTimestamp=self.source_time)
        elif isinstance(value,float):
            data_value = ua.DataValue(ua.Variant(value, ua.VariantType.Float),SourceTimestamp=self.source_time, ServerTimestamp=self.source_time)
        elif isinstance(value,str):
            data_value = ua.DataValue(ua.Variant(value, ua.VariantType.String),SourceTimestamp=self.source_time, ServerTimestamp=self.source_time)
        
        await self.server.write_attribute_value(node_id.nodeid, data_value)

    async def is_connected(self,ipaddress):
        try:
            r, w = await asyncio.open_connection(ipaddress[0], ipaddress[1])
            w.close()
            return True
        except:
            #self.server_logger_signal.emit(('log',"Device Not Connected\n Closing application in 10 seconds"))
            await asyncio.sleep(10)
            #self.exit_signal.emit()
        return False

    async def history_database_cleaner(self,database_file,table_name):
        conn = sqlite3.connect(self.file_path.joinpath(database_file))
        crsr = conn.cursor()
        crsr.execute(f"DELETE FROM '{table_name}';")
        conn.commit()
        conn.close()  

    async def opc_server(self):
        self.database_file = "variable_history.sqlite3"
        self.conn = sqlite3.connect(self.file_path.joinpath(self.database_file))
        #Configure server to use sqlite as history database (default is a simple memory dict)
        self.server.iserver.history_manager.set_storage(HistorySQLite(self.file_path.joinpath(self.database_file)))
        await self.server.init()
        self.server.set_endpoint(f"opc.tcp://{self.endpoint}") 
        #self.server_logger_signal.emit(('log',f"Creating Server at Endpoint: opc.tcp://{self.endpoint}"))       
        #load nodes structure from XML file path
        await self.server.import_xml(self.file_path.joinpath("standard_server_structure.xml"))
        await self.server.load_data_type_definitions()

        #load all the nodes inside the XML file into a dictionary variables for easier data handling
        root_obj = await self.server.nodes.root.get_child(["0:Objects", "2:Device"])
        connected_devices = await root_obj.get_children()
        for devices in connected_devices:
            device_name = (await devices.read_display_name()).Text
            device_category = await devices.get_children()
            for category in device_category:
                category_name = (await category.read_display_name()).Text
                variables = await category.get_children()
                for variables in variables:
                    #print(variables)
                    variables_id = variables.nodeid.Identifier
                    variables_ns = variables.nodeid.NamespaceIndex
                    variable_name = (await variables.read_display_name()).Text
                    self.device_structure.update({variables_id:[variables_ns, device_name, category_name,variable_name,0]})

        #check for connected device based on the nodes structure inside the loaded XML file
        for ip_address in self.plc_ip_address.values():
            await self.is_connected(ip_address.split(':'))
            await asyncio.sleep(0.5)
            #self.server_logger_signal.emit(('log',"Device Connected"))

        #create hmi subscription handler and initialize it with current value of plc relay
        hmi_dict = dict(filter(lambda elem: elem[1][2]=='hmi',self.device_structure.items()))
        hmi_handler = SubHmiHandler(hmi_dict,self.plc_ip_address,self.plc_tcp_socket_request)
        hmi_sub = await self.server.create_subscription(self.hmi_sub, hmi_handler)  
        for key in hmi_dict.keys():
            hmi_var = self.server.get_node(ua.NodeId(key,hmi_dict[key][0]))
            await hmi_var.set_writable()
            await hmi_sub.subscribe_data_change(hmi_var,queuesize=1)
        #self.server_logger_signal.emit(('log',"Subscribed to HMI Inputs!"))
        
        io_dict = dict(filter(lambda elem: (elem[1][2]!='hmi') ,self.device_structure.items()))

        #create subscription for the monitored nodes and fill with last known data in database
        var_handler = SubVarHandler(self.monitored_node,self.count_node)
        var_sub = await self.server.create_subscription(self.sub_time, var_handler) 

        for key,value in self.monitored_node.items():
            previous_data = pd.read_sql_query(f"SELECT Value, SourceTimestamp FROM '{value[0]}_{value[1]}' ORDER BY _Id DESC LIMIT 1", self.conn)
            initial_value = previous_data.iloc[0]['Value']
            await self.simple_write_to_opc((value[0], value[1], int(initial_value)))
            monitored_var = self.server.get_node(ua.NodeId(key,value[0]))
            await var_sub.subscribe_data_change(monitored_var,queuesize=1)

        #create historizing database for server variables
        server_var_obj = await self.server.nodes.root.get_child(["0:Objects", "2:server_variables"])
        server_var_list = await server_var_obj.get_children()
        for node in server_var_list:
            await self.server.historize_node_data_change(node, period=None, count=0)
            
        #delete the record create from initializing the historizing nodes
        self.conn.close()

        #self.server_signal.emit("Starting server!")
        ip_list = list(self.plc_ip_address.values())
        device_coil_list = [dict(filter(lambda elem: key in elem[1],io_dict.items())) for key in self.plc_ip_address.keys()] #get list of keys in io_dict
        coil_cat_dict_list=[]
        for i in range(len(ip_list)):
            value_list = list(device_coil_list[i].values())
            coil_cat_list = [value_list[i][2] for i in range(len(value_list))]
            coil_cat_dict= dict(Counter(coil_cat_list))
            for key in coil_cat_dict.keys():
                test = dict(filter(lambda elem: key in elem[1],io_dict.items()))
                value = list(test.values())[0]
                coil_cat_dict.update({key:(value[3],coil_cat_dict[key])})
            coil_cat_dict_list.append(coil_cat_dict)
        async with self.server:
            self.server_start_time = datetime.now()
            while True:
                await asyncio.sleep(2)
                for k in range(len(ip_list)):
                    await asyncio.create_task(self.scan_loop_plc(coil_cat_dict_list[k],device_coil_list[k],ip_list[k]))




        

