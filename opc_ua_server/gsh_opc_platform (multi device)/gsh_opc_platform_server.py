import asyncio
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import datetime
import time
from collections import Counter
from asyncua import ua, Server, uamethod
from asyncua.common import node
import gsh_opc_platform_ui as gsh_ui
from asyncua.server.history_sql import HistorySQLite


#{variables_id:[variables_ns, device_name, category_name,variable_name,0]}
@uamethod
def count(parent, x, y):
    return x + y


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
    def __init__(self,data_signal,io_dictionary):
        self.data_signal = data_signal
        self.io_dictionary = io_dictionary
    async def datachange_notification(self, node, val, data):
        self.data_signal.emit((node.nodeid.Identifier, val))



class OpcServerThread(QObject):
    server_signal = pyqtSignal(str)
    data_signal = pyqtSignal(tuple)
    alarm_signal = pyqtSignal(tuple)
    hmi_signal = pyqtSignal(tuple)
    def __init__(self,input_q,current_file_path,parent=None,**kwargs):
        super().__init__(parent, **kwargs)
        self.input_queue = input_q
        self.device_structure={}
        self.plc_ip_address={'PLC1':'127.0.0.1:8501'}
        self.file_path = current_file_path
        self.server_class = Server()
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

    async def scan_loop_plc(self,server,coil_cat_dict_list,device_coil_list,ip_list):
        source_time = datetime.datetime.now()
        for key,values in  coil_cat_dict_list.items():
            current_relay_list = await self.plc_tcp_socket_request(values,ip_list,'read')
            cat_filter = dict(filter(lambda elem: key in elem[1],device_coil_list.items()))
            cat_filter_keys = list(cat_filter.keys())
            asyncio.ensure_future(self.write_to_opc(server,current_relay_list,cat_filter,cat_filter_keys,source_time))

    async def write_to_opc(self,server,current_relay_list,cat_filter_items,cat_filter_keys,source_time):
        
        for i in range(len(current_relay_list)):
            from_filter = cat_filter_items[cat_filter_keys[i]]
            from_filter[4]=current_relay_list[i]
            node_id=server.get_node(ua.NodeId(cat_filter_keys[i], 2))
            data_value = ua.DataValue(ua.Variant(current_relay_list[i], ua.VariantType.Int64),SourceTimestamp=source_time, ServerTimestamp=source_time)
            await server.write_attribute_value(node_id.nodeid, data_value)



    async def simple_write_to_opc(self,server,hmi_signal):
        node_id=server.get_node(ua.NodeId(hmi_signal[0], 2))
        data_value = ua.DataValue(ua.Variant(hmi_signal[1], ua.VariantType.Int64))
        await server.write_attribute_value(node_id.nodeid, data_value)



    async def is_connected(self,ipaddress):
        try:
            r, w = await asyncio.open_connection(ipaddress[0], ipaddress[1])
            w.close()
            return True
        except:
            pass
        return False

    async def opc_server(self):

        server = self.server_class
        server.iserver.history_manager.set_storage(HistorySQLite(self.file_path.joinpath("my_datavalue_history.sql")))
        await server.init()
        endpoint = "localhost:4840"
        server.set_endpoint(f"opc.tcp://{endpoint}/gshopcua/server" )
        self.server_signal.emit(f"Establishing Server at {endpoint}/gshopcua/server")


        
        #load nodes structure from XML file path
        try:
            self.server_signal.emit("Loading Server Structure from file")
            await server.import_xml(self.file_path.joinpath("standard_server_structure_3.xml"))
        except FileNotFoundError as e:
            self.server_signal.emit("Server Structure File not found")
        await server.load_data_type_definitions()
        self.server_signal.emit("Loading Server Structure to OPC Server!")


        #load all the nodes inside the XML file into a dictionary variables for easier data handling
        root_obj = await server.nodes.root.get_child(["0:Objects", "2:Device"])
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
        self.server_signal.emit("Done Initializing Nodes from XML")
         
        #monitored_node = [2167,2168,2169]
        #for key in monitored_node:
        #    node_target = server.get_node(f"ns=2;i={key}")
        #    await server.historize_node_data_change(node_target, period = None, count = 100)

        #check for connected device based on the nodes structure inside the loaded XML file
        for ip_address in self.plc_ip_address.values():
            self.server_signal.emit(f"Checking for device at {ip_address}")
            device_connection = await self.is_connected(ip_address.split(':'))
            await asyncio.sleep(1)
            if device_connection == True:
                self.server_signal.emit(f"Successfully connected to device at {ip_address}!")

            else:
                self.server_signal.emit(f"Failed to connect to device at {ip_address}. Cannot start Server!")
        self.server_signal.emit("Initializing Nodes for HMI")


        #create hmi subscription handler and initialize it with current value of plc relay
        hmi_dict = dict(filter(lambda elem: elem[1][2]=='hmi',self.device_structure.items()))
        hmi_handler = SubHmiHandler(hmi_dict,self.plc_ip_address,self.hmi_signal,self.plc_tcp_socket_request)
        hmi_sub = await server.create_subscription(1, hmi_handler)  
        for key in hmi_dict.keys():
            hmi_var = server.get_node(f"ns={hmi_dict[key][0]};i={key}")
            await hmi_var.set_writable()
            from_hmi_dict = hmi_dict[key]
            hmi_relays = from_hmi_dict[3]
            plc_device = from_hmi_dict[1]
            plc_address = self.plc_ip_address[plc_device]
            hmi_plc_status = (await self.plc_tcp_socket_request((hmi_relays,1),plc_address,'read'))[0]
            data_value = ua.DataValue(ua.Variant(hmi_plc_status, ua.VariantType.Int64))
            await server.write_attribute_value(hmi_var.nodeid, data_value)
            await hmi_sub.subscribe_data_change(hmi_var,queuesize=1)
            from_hmi_dict[4] = hmi_plc_status
            hmi_dict.update({key:from_hmi_dict})
        

        #create alarm subscription handler and pass the self.alarm_signal
        alarm_handler = SubAlarmHandler(self.alarm_signal)
        alarm_sub = await server.create_subscription(1, alarm_handler) 
        alarm_dict = dict(filter(lambda elem: elem[1][2]== 'alarm' ,self.device_structure.items()))
        for key in alarm_dict.keys():
            alarm_var = server.get_node(f"ns={alarm_dict[key][0]};i={key}")
            await alarm_sub.subscribe_data_change(alarm_var,queuesize=1)


        #create io_dict to remove hmi and alarm from device structure for io operation
        io_dict = dict(filter(lambda elem: (elem[1][2]!='hmi') and (elem[1][2]!='alarm') ,self.device_structure.items()))
        io_handler = SubIoHandler(self.data_signal,io_dict)
        io_sub = await server.create_subscription(1, io_handler) 
        for key in io_dict.keys():
            io_var = server.get_node(f"ns={io_dict[key][0]};i={key}")
            await io_sub.subscribe_data_change(io_var,queuesize=1)

        objects = server.nodes.objects
        self.myobj = await objects.add_object(2, "server_method")
        await self.myobj.add_method(2, "count", count, [ua.VariantType.Int64, ua.VariantType.Int64], [ua.VariantType.Int64])

        #combined the alarm and io dictionary for main operation
        io_dict=alarm_dict|io_dict
        self.server_signal.emit("Starting server!")
        
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

        async with server:

            while i <11:
                while True:
                    tic = time.perf_counter()
                    await asyncio.sleep(0.001)
                    try:
                        for k in range(len(ip_list)):
                            await asyncio.create_task(self.scan_loop_plc(server,coil_cat_dict_list[k],device_coil_list[k],ip_list[k]))

                        if not self.input_queue.empty():
                            hmi_signal = self.input_queue.get()
                            asyncio.ensure_future(self.simple_write_to_opc(server,hmi_signal))
                        toc = time.perf_counter()
                        print(f"Executed loop in {toc - tic:0.4f} seconds")
                    except:
                        self.server_signal.emit(f"Server Exception Occured, Retrying Attempt {i} in 10s!")
                        await asyncio.sleep(10)
                        i+=1
                        break
                    else:
                        if i>1:
                            self.server_signal.emit("Resuming Server Operation!")
                            i=1
                    continue
            self.server_signal.emit("Server Has Stopped!")
            


        

