import asyncio
from PyQt5.QtCore import QObject, pyqtSignal
from collections import Counter
from asyncua import ua, Server, uamethod
from asyncua.common import node
from datetime import timedelta, datetime
from asyncua.server.history_sql import HistorySQLite
import pandas as pd
import sqlite3
import time
#io_dict standard dictionary: {variables_id:[variables_ns, device_name, category_name,variable_name,0]}
#hmi_signal standard: (node_id, namespace, data_value)


class SubHmiHandler(object):
    def __init__(self,hmi_dictionary,plc_ip_address,hmi_signal,plc_tcp_socket_request):
        self.hmi_structure = hmi_dictionary
        self.ip_address = plc_ip_address
        self.hmi_signal = hmi_signal
        self.plc_send = plc_tcp_socket_request
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        from_hmi_struct = self.hmi_structure[node_identifier]
        ip_address = self.ip_address[from_hmi_struct[1]]
        self.hmi_signal.emit((from_hmi_struct[1], from_hmi_struct[3], val))
        await self.plc_send((from_hmi_struct[3],1,val),ip_address,'write')

class SubAlarmHandler(object):
    def __init__(self,alarm_signal):
        self.alarm_signal = alarm_signal
        
    async def datachange_notification(self, node, val, data):
        if val >0:
            self.alarm_signal.emit((node.nodeid.Identifier, val))

class SubIoHandler(object):
    def __init__(self,data_signal):
        self.data_signal = data_signal

    async def datachange_notification(self, node, val, data):
        self.data_signal.emit((node.nodeid.Identifier, val))


class SubVarHandler(object):
    def __init__(self,monitored_dict,count):
        self.monitored_node = monitored_dict
        self.count_node=count
    async def datachange_notification(self, node, val, data):
        node_identifier = node.nodeid.Identifier
        if val >0:
            value = self.monitored_node[node_identifier]
            await self.count_node((value[0], value[1], val)) #(namespace, node id, amount)
        

class OpcServerThread(QObject):
    data_signal = pyqtSignal(tuple)
    hmi_signal = pyqtSignal(tuple)
    alarm_signal = pyqtSignal(tuple)
    server_logger_signal = pyqtSignal(str)
    #ui_refresh_signal = pyqtSignal()
    def __init__(self,input_q,current_file_path,endpoint,parent=None,**kwargs):
        super().__init__(parent, **kwargs)
        self.input_queue = input_q
        self.device_structure={}
        self.plc_ip_address={'PLC1':'127.0.0.1:8501'}
        self.file_path = current_file_path
        self.server = Server()
        self.endpoint = endpoint
        self.monitored_node = {2167:(2,10004),2168:(2,10006),2169:(2,10007),2170:(2,10005)}
        #{R100:Total quantity in, R101: Total Passed, R102: Total Failed, R103: Total Quantity Out}
        self.time_cleanup = timedelta(days=7) #the schedule database reset
        self.stats_reset = timedelta(days=1)
        self.sub_time = 50
        self.hmi_sub = 10
    def run(self):
        asyncio.run(self.opc_server())

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

    async def count_node(self, data):
        node_id= self.server.get_node(ua.NodeId(data[1], data[0])) 
        current_value = await node_id.read_value()
        #print(node_id , current_value)
        new_value = current_value + data[2]
        await self.simple_write_to_opc((data[0], data[1], new_value))

    async def simple_write_to_opc(self,hmi_signal):
        #hmi_signal = (namespace, node_id, data_value)
        node_id=self.server.get_node(ua.NodeId(hmi_signal[1], hmi_signal[0]))
        self.source_time = datetime.now()
        data_value = ua.DataValue(ua.Variant(hmi_signal[2], ua.VariantType.Int64),SourceTimestamp=self.source_time, ServerTimestamp=self.source_time)
        await self.server.write_attribute_value(node_id.nodeid, data_value)

    async def is_connected(self,ipaddress):
        try:
            r, w = await asyncio.open_connection(ipaddress[0], ipaddress[1])
            w.close()
            return True
        except:
            pass
        return False

    async def history_database_cleaner(self,database_file,added_time,table_name):
        conn = sqlite3.connect(self.file_path.joinpath(database_file))
        crsr = conn.cursor()
        crsr.execute(f"DELETE FROM '{table_name}' WHERE SourceTimestamp < '{added_time}';")
        conn.commit()
        conn.close()  

    async def opc_server(self):
        self.database_file = "variable_history.sqlite3"
        self.conn = sqlite3.connect(self.file_path.joinpath(self.database_file))
        #Configure server to use sqlite as history database (default is a simple memory dict)
        self.server.iserver.history_manager.set_storage(HistorySQLite(self.file_path.joinpath(self.database_file)))
        await self.server.init()
        self.server.set_endpoint(f"opc.tcp://{self.endpoint}")        
        #load nodes structure from XML file path
        await self.server.import_xml(self.file_path.joinpath("standard_server_structure_3.xml"))
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

        #create hmi subscription handler and initialize it with current value of plc relay
        hmi_dict = dict(filter(lambda elem: elem[1][2]=='hmi',self.device_structure.items()))
        hmi_handler = SubHmiHandler(hmi_dict,self.plc_ip_address,self.hmi_signal,self.plc_tcp_socket_request)
        hmi_sub = await self.server.create_subscription(self.hmi_sub, hmi_handler)  
        for key in hmi_dict.keys():
            hmi_var = self.server.get_node(ua.NodeId(key,hmi_dict[key][0]))
            await hmi_var.set_writable()
            from_hmi_dict = hmi_dict[key]
            hmi_relays = from_hmi_dict[3]
            plc_device = from_hmi_dict[1]
            plc_address = self.plc_ip_address[plc_device]
            hmi_plc_status = (await self.plc_tcp_socket_request((hmi_relays,1),plc_address,'read'))[0]
            data_value = ua.DataValue(ua.Variant(hmi_plc_status, ua.VariantType.Int64))
            await self.server.write_attribute_value(hmi_var.nodeid, data_value)
            await hmi_sub.subscribe_data_change(hmi_var,queuesize=1)
            from_hmi_dict[4] = hmi_plc_status
            hmi_dict.update({key:from_hmi_dict})

        #create alarm subscription handler and pass the self.alarm_signal
        alarm_handler = SubAlarmHandler(self.alarm_signal)
        alarm_sub = await self.server.create_subscription(self.sub_time, alarm_handler) 
        alarm_dict = dict(filter(lambda elem: elem[1][2]== 'alarm' ,self.device_structure.items()))
        for key in alarm_dict.keys():
            alarm_var = self.server.get_node(ua.NodeId(key,alarm_dict[key][0]))
            await alarm_sub.subscribe_data_change(alarm_var,queuesize=1)
        
        
        io_dict = dict(filter(lambda elem: (elem[1][2]!='hmi') and (elem[1][2]!='alarm') ,self.device_structure.items()))
        io_handler = SubIoHandler(self.data_signal)
        io_sub = await self.server.create_subscription(self.sub_time, io_handler) 
        for key in io_dict.keys():
            io_var = self.server.get_node(ua.NodeId(key,io_dict[key][0]))
            await io_sub.subscribe_data_change(io_var,queuesize=1)

        #combined the alarm and io dictionary for main operation
        io_dict=alarm_dict|io_dict

        #create subscription for the monitored nodes and fill with last known data in database
        var_handler = SubVarHandler(self.monitored_node,self.count_node)
        var_sub = await self.server.create_subscription(self.sub_time, var_handler) 
        for key,value in self.monitored_node.items():
            
            try:
                previous_data = pd.read_sql_query(f"SELECT Value FROM '{value[0]}_{value[1]}' ORDER BY _Id DESC LIMIT 1", self.conn)
                pd.read_sql_query(f"DELETE FROM '{value[0]}_{value[1]}' ORDER BY _Id DESC LIMIT 1", self.conn)
                initial_value = previous_data.iloc[0]['Value']
                await self.simple_write_to_opc((value[0], value[1], int(initial_value)))
            except:
                pass
            monitored_var = self.server.get_node(ua.NodeId(key,value[0]))
            await var_sub.subscribe_data_change(monitored_var,queuesize=1)


        #WHERE STRFTIME('%H', SourceTimestamp) > '9'
        #create historizing database for server variables
        server_var_obj = await self.server.nodes.root.get_child(["0:Objects", "2:server_variables"])
        server_var_list = await server_var_obj.get_children()
        for node in server_var_list:
            await self.server.historize_node_data_change(node, period=None, count=0)
        #delete the record create from initializing the historizing nodes
        crsr = self.conn.cursor()
        for key,value in self.monitored_node.items():         
            table_name = f"{value[0]}_{value[1]}"
            crsr.execute(f"DELETE FROM '{table_name}' WHERE _Id = (SELECT MAX(_Id) FROM '{table_name}');")
        self.conn.commit()
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

        i=1
        async with self.server:
            self.server_logger_signal.emit("Server Launched!")
            while True:
                #tic = time.perf_counter()
                current_time = datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
                scheduled_database_cleanup_time = current_time + self.time_cleanup
                stats_reset_time = current_time + self.stats_reset
                await asyncio.sleep(0.2)
                for k in range(len(ip_list)):
                    await asyncio.create_task(self.scan_loop_plc(coil_cat_dict_list[k],device_coil_list[k],ip_list[k]))
                if not self.input_queue.empty():
                    print("Receiving data")
                    hmi_signal = self.input_queue.get()
                    #asyncio.ensure_future(self.simple_write_to_opc(hmi_signal))
                    self.server_logger_signal.emit(hmi_signal)
                if datetime.now()>= scheduled_database_cleanup_time:
                    for value in self.monitored_node.values():
                        table_name = str(f"{value[0]}_{value[1]}")
                        asyncio.create_task(self.history_database_cleaner(self.database_file,scheduled_database_cleanup_time,table_name))
                if datetime.now()>= stats_reset_time:
                    print(datetime.now())
                #toc = time.perf_counter()
                #self.server_logger_signal.emit(f"Loop executed in {toc - tic:0.4f} seconds")

            


        

