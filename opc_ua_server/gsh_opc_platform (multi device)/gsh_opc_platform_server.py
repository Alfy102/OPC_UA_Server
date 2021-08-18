import asyncio
import logging
from PyQt5.QtCore import QObject
import datetime
from asyncua import ua, Server
import os.path
import sys
import sqlite3
sys.path.insert(0, "..")
from asyncua.server.history_sql import HistorySQLite
#from asyncua.crypto.permission_rules import SimpleRoleRuleset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
stop_threads=False
xml_file_path ='C:/Users/aliff/Documents/OPC_UA_Server/opc_ua_server/gsh_opc_platform (multi device)/standard_server_structure2.xml'
plc_ip_address='127.0.0.1:8501;127.0.0.2:8501'
log_file_path = "server_node_history.db"
set_plc_time=False
server_ip='127.0.0.1:4840'
device_hmi_global=[]





class ServerLogHandler(logging.Handler):
    def __init__(self, sql_conn, sql_cursor):
        logging.Handler.__init__(self)
        self.sql_cursor = sql_cursor
        self.sql_conn = sql_conn

    def emit(self, record):
        #log_file_path = "server_node_history.db"
        #log_conn = sqlite3.connect(log_file_path)
        self.log_msg = record.msg
        self.log_msg = self.log_msg.strip()
        print(f"test log  {self.log_msg}")


log_file_path = "server_node_history.db"
logging.basicConfig(filename=log_file_path)
log_conn = sqlite3.connect(log_file_path)
log_cursor = log_conn.cursor()
logdb = ServerLogHandler(log_conn, log_cursor)
logging.getLogger('').addHandler(logdb)
log = logging.getLogger('opc_server_log')
log.setLevel('INFO')


class SubServerHandler(object):
    async def datachange_notification(self, node, val, data):
        await self.index_comm(node,val)
    async def index_comm(self,node,val):
        name = (await node.read_display_name()).Text
        global device_hmi_global
        for i in range(len(device_hmi_global)):
            if node in device_hmi_global[i]:
                ipadd = plc_ip_address.split(";")
                ipaddress = ipadd[i].split(":")
        log.info(f"Device {name} at {ipaddress[0]}:{ipaddress[1]} data changed to {val}")
        await self.hmi_input(name,val,ipaddress)
    async def hmi_input(self,name,val,ipaddress):
        reader, writer = await asyncio.open_connection(ipaddress[0], ipaddress[1])
        encapsulate = bytes(f"WR {name} {val}\r\n",'utf-8')
        writer.write(encapsulate)
        recv_value = await reader.read(50)
        recv_value = recv_value.decode('UTF-8').split()
        writer.close()



class opc_server_worker(QObject):
    def start_opc_server(self):
        global stop_threads
        stop_threads = False
        asyncio.run(self.opc_server(log))

    def stop_opc_server(self):
        global stop_threads
        stop_threads=True

    async def rw_opc(self,zipped_data,server,source_time):
        data_value = ua.DataValue(ua.Variant((int(zipped_data[1])), ua.VariantType.Int64),SourceTimestamp=source_time, ServerTimestamp=source_time)
        await server.write_attribute_value(zipped_data[0].nodeid, data_value)

    async def plc_source_time(self,ipaddress):
        recv_timestamp = await self.plc_tcp_socket_init(("CM700",6),ipaddress)
        timestamp = [(f"{i:02}") for i in recv_timestamp]
        timestamp = ''.join(timestamp)
        timestamp = datetime.datetime.strptime(timestamp,"%y%m%d%H%M%S")
        #date_timestamp=
        #print(timestamp)
        #print(recv_timestamp)
        #recv_timestamp = str(recv_timestamp[0][-2:])+","+str(recv_timestamp[1][-2:])+","+str(recv_timestamp[2][-2:])+","+str(recv_timestamp[3][-2:])+","+str(recv_timestamp[4][-2:])+","+str(recv_timestamp[5][-2:])
        #recv_timestamp = DateTime.strptime(recv_timestamp,"%y,%m,%d,%H,%M,%S")
        recv_timestamp = datetime.datetime.now() #place holder time method
        #print(recv_timestamp)
        #print(recv_timestamp)
        return recv_timestamp
    
    async def plc_tcp_socket_init(self,start_device,ipaddress):
        reader, writer = await asyncio.open_connection(ipaddress[0], ipaddress[1])
        encapsulate = bytes(f"RDS {start_device[0]} {start_device[1]}\r\n",'utf-8')
        writer.write(encapsulate)
        await writer.drain()
        recv_value = await reader.readuntil(separator=b'\r\n')
        recv_value = recv_value.decode('UTF-8').split()
        recv_value = [int(recv_value[i]) for i in range(len(recv_value))]
        writer.close()
        return recv_value

    async def scan_loop_plc(self,start_device,zipped_data,server,ipaddress):
        source_time = await self.plc_source_time(ipaddress)
        current_relay_list = [await self.plc_tcp_socket_init(start_device[i],ipaddress) for i in range(len(start_device))]
        [await self.plc_to_opc(current_relay_list[i], source_time, zipped_data[i],server) for i in range(len(current_relay_list))]
        
    async def plc_to_opc(self,current_list,source_time,nodes_id,server):
        [await self.rw_opc([nodes_id[i][0],current_list[i]],server,source_time) for i in range(len(current_list)) if current_list[i] != (await nodes_id[i][0].read_value())]

    async def hmi_init(self,server,hmi_node,ipaddress):
        source_time = await self.plc_source_time(ipaddress)
        for i in range(len(hmi_node)):
            return_data = await self.plc_tcp_socket_init([(await hmi_node[i].read_display_name()).Text,'1'],ipaddress)
            await self.rw_opc([hmi_node[i],return_data[0]],server, source_time)

    async def init_server(self,server,device_group,ipaddress):
        start_device=[]
        data_list=[]
        zipped_data=[]
        device_group = [x for x in device_group if x]
        for i in range(len(device_group)):
            start_device.append(((await device_group[i][0].read_display_name()).Text,len(device_group[i])))
            data_list.append(await self.plc_tcp_socket_init(start_device[i],ipaddress))
            zipped_data.append(list(zip(device_group[i],data_list[i])))
        nodes_data_list = list(zipped_data)
        for k in range(len(nodes_data_list)):
            source_time = await self.plc_source_time(ipaddress)
            asyncio.gather(*(self.rw_opc(nodes_data_list[k][i],server,source_time) for i in range(len(nodes_data_list[k]))))
        return start_device,zipped_data

    async def is_connected(self,ipaddress):
        try:
            r, w = await asyncio.open_connection(ipaddress[0], ipaddress[1])
            w.close()
            return True
        except:
            pass
        return False


    async def opc_server(self,log):
        

        server = Server()
        server.iserver.history_manager.set_storage(HistorySQLite(log_file_path))
        await server.init()
        endpoint = server_ip
        server.set_endpoint(f"opc.tcp://{endpoint}/freeopcua/server/" )
        log.info(f"Establisihing Server at {endpoint}/freeopcua/server/")
        #server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt],permission_ruleset=SimpleRoleRuleset())
        #try:
        #    await server.load_certificate("gsh_private_certificate.der")   
        #except:
        #    log.info("Server Certicate File not found")
        #try:
        #    await server.load_private_key("gsh_private_key.pem")    
        #except:
        #    log.info("Server Key file not found")
        try:
            log.info("loading server structure from file")
            await server.import_xml(xml_file_path)
        except FileNotFoundError as e:
            log.info("Server Structure File not found")

        await server.load_data_type_definitions()
        hardware_ip = plc_ip_address.split(";")
        ipaddress=[hardware_ip[i].split(":") for i in range(len(hardware_ip))]
        """
        Initializing read only nodes and hmi nodes base on server structure xml file hierachy.
        Device <--Get children of this node
            |__PLC1 <-- Loop 1 get children of this node
            |   |__hmi          <--Loop 2 get all children for this node
            |   |__alarm        <--Loop 2 get all children for this node
            |   |__relay_data   <--Loop 2 get all children for this node
            |   |__memory_data  <--Loop 2 get all children for this node
            |
            |__PLC2 <-- Loop 1 get children of this node
                |__hmi          <--Loop 2 get all children for this node
                |__alarm        <--Loop 2 get all children for this node
                |__relay_data   <--Loop 2 get all children for this node
                |__memory_data  <--Loop 2 get all children for this node
        """
        log.info("Loading Server Structure!")
        device_group=[]
        device_hmi_group=[]
        root_obj = await server.nodes.root.get_child(["0:Objects", "2:Device"])
        root_obj_children = await root_obj.get_children()
        for i in range(len(root_obj_children)):
            device_name = (await  root_obj_children[i].read_display_name()).Text
            category = await root_obj_children[i].get_children()
            category_group = []
            for k in range(len(category)):
                category_name = (await category[k].read_display_name()).Text
                log.info(f"Successfully load {device_name}:{category_name}")
                device_nodes = await category[k].get_children()
                hmi_group=[]
                data_group=[]
                if category_name not in 'hmi':
                    for l in range(len(device_nodes)):
                        data_group.append(device_nodes[l]) 
                        await server.historize_node_data_change(device_nodes[l], period=None, count=100)
                else:
                    for l in range(len(device_nodes)):
                        await device_nodes[l].set_writable(True)
                        await server.historize_node_data_change(device_nodes[l], period=None, count=100)
                        hmi_group.append(device_nodes[l])
                category_group.append(data_group)
                device_hmi_group.append(hmi_group)
            device_group.append(category_group)    
        device_hmi_group = [x for x in device_hmi_group if x]
        log.info("Done Initializing Nodes from XML")
        global device_hmi_global
        device_hmi_global = device_hmi_group
        """
        Check for device connection
        """
           
        for i in range(len(root_obj_children)):
                log.info(f'Checking for device {ipaddress[0]}:{ipaddress[1]}')
                device_connection = await self.is_connected(ipaddress[i])
                await asyncio.sleep(3)
                if device_connection == False:
                    log.info(f'Failed to connect to {ipaddress[i][0]}:{ipaddress[i][1]}')
                    raise Exception("No connected device. Recheck Connection")
        #log.info(f'Checking connection with device {ipaddress}')
        """
        Init node subscription for HMI       
        """
        log.info("Initializing Nodes for HMI Subscription")
        init_hmi = [await self.hmi_init(server,device_hmi_group[i],ipaddress[i]) for i in range(len(device_hmi_group))]
        """
        Create node subscription for HMI       
        """
        hmi_handler = SubServerHandler()
        hmi_sub = await server.create_subscription(20, hmi_handler)
        sub = [await hmi_sub.subscribe_data_change(device_hmi_group[i][k],queuesize=1) for k in range(len(device_hmi_group[i])) for i in range(len(device_hmi_group))]
        log.info("Done Initializing Nodes for HMI Subscription")




        """
        Device group consist of read only data nodes that is contained in category list 
        that is contained device group list *triple layer. This allows the server to accomate 
        more than one PLC. The same is applied to device hmi group.
        """
        start_device=[0 for x in range(len(device_group))]
        zipped_data=[0 for x in range(len(device_group))]
        tcp_rw=[0 for x in range(len(device_group))]
        log.info('Initializing server!')
        for i in range(len(device_group)):
            try:
                start_device[i],zipped_data[i]=await asyncio.create_task(self.init_server(server,device_group[i],ipaddress[i]))            
            except:
                log.info('Initializing server failed!')
        log.info('Initializing server complete!')
        log.info('Starting server!')
        log.info('Server Started!')
        i=1
        async with server:
            while i <11:
                while stop_threads==False:
                    await asyncio.sleep(2)
                    try:
                        #log.info(f"Lost Connection to device at {ipaddress[o]}:{ipaddress[1]}")
                        tasks = [await asyncio.create_task(self.scan_loop_plc(start_device[i],zipped_data[i],server,ipaddress[i])) for i in range(len(device_group))]
                    except:
                        log.info(f'Server Exception Occured, Retrying Attempt {i} in 10s!')
                        await asyncio.sleep(10)
                        i+=1
                        break
                    else:
                        if i>1:
                            log.info("Resuming Server Operation!")
                            i=1
                    continue
            raise Exception("Device Connection Problem")
                        #log.info('Server Failed to Start!')
            

        
        


