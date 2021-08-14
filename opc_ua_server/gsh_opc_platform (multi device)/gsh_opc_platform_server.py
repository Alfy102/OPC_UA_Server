import asyncio
import logging
from PyQt5.QtCore import QObject
from asyncua.ua.uatypes import DateTime
from asyncua import ua, Server
import os.path
from asyncua.crypto.permission_rules import SimpleRoleRuleset

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
stop_threads=False
xml_file_path ='C:/Users/aliff/Documents/OPC_UA_Server/opc_ua_server/gsh_opc_platform (multi device)/standard_server_structure2.xml'
plc_ip_address='127.0.0.1:8501;127.0.0.2:8501'
set_plc_time=False
server_ip='127.0.0.1:4840'


device_hmi_global=[]

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
        logging.basicConfig(level=logging.INFO)
        asyncio.run(self.opc_server())


    def stop_opc_server(self):
        global stop_threads
        stop_threads=True
    """
    To create a modular tcp to plc function
    """
    async def rw_opc(self,zipped_data,server,source_time):
        data_value = ua.DataValue((int(zipped_data[1])),SourceTimestamp=source_time, ServerTimestamp=DateTime.utcnow())
        await server.write_attribute_value(zipped_data[0].nodeid, data_value)

    async def plc_source_time(self):
        #recv_timestamp = await self.plc_tcp_socket_init(("CM700",6))
        #print(recv_timestamp)
        #recv_timestamp = str(recv_timestamp[0][-2:])+","+str(recv_timestamp[1][-2:])+","+str(recv_timestamp[2][-2:])+","+str(recv_timestamp[3][-2:])+","+str(recv_timestamp[4][-2:])+","+str(recv_timestamp[5][-2:])
        #recv_timestamp = DateTime.strptime(recv_timestamp,"%y,%m,%d,%H,%M,%S")
        recv_timestamp = DateTime.utcnow()
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
        await writer.drain()
        writer.close()
        return recv_value

    async def scan_loop_plc(self,start_device,zipped_data,server,ipaddress,tcp_rw):
        source_time = await self.plc_source_time()
        current_relay_list = [await self.plc_tcp_socket_init(start_device[i],ipaddress) for i in range(len(start_device))]
        [await self.plc_to_opc(current_relay_list[i], source_time, zipped_data[i],server) for i in range(len(current_relay_list))]
        
    async def plc_to_opc(self,current_list,source_time,nodes_id,server):
        [await self.rw_opc([nodes_id[i][0],current_list[i]],server,source_time) for i in range(len(current_list)) if current_list[i] != (await nodes_id[i][0].read_value())]

    async def hmi_init(self,server,hmi_node,ipaddress):
        source_time = await self.plc_source_time()
        for i in range(len(hmi_node)):
            return_data = await self.plc_tcp_socket_init([(await hmi_node[i].read_display_name()).Text,'1'],ipaddress)
            await self.rw_opc([hmi_node[i],return_data[0]],server, source_time)

    async def init_server(self,server,logger,device_group,ipaddress):
        start_device=[]
        data_list=[]
        zipped_data=[]
        device_group = [x for x in device_group if x]
        for i in range(len(device_group)):
            start_device.append(((device_name := await device_group[i][0].read_display_name()).Text,len(device_group[i])))
            data_list.append(await self.plc_tcp_socket_init(start_device[i],ipaddress))
            zipped_data.append(list(zip(device_group[i],data_list[i])))
            logger.info(f"Successfully load {device_name}")
        nodes_data_list = list(zipped_data)
        for k in range(len(nodes_data_list)):
            source_time = await self.plc_source_time()
            asyncio.gather(*(self.rw_opc(nodes_data_list[k][i],server,source_time) for i in range(len(nodes_data_list[k]))))
        return start_device,zipped_data

    async def opc_server(self):
        _logger = logging.getLogger('server_log')
        server = Server()
        await server.init()
        _logger.info("Initializing Server")
        endpoint = server_ip
        server.set_endpoint(f"opc.tcp://{endpoint}/freeopcua/server/" )
        server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt],permission_ruleset=SimpleRoleRuleset())
        await server.load_certificate("gsh_private_certificate.der")
        await server.load_private_key("gsh_private_key.pem")
        _logger.info(f"Establisihing Server at {endpoint}")
        try:
            _logger.info("loading server structure from file")
            list_nodes = await server.import_xml(xml_file_path)
        except FileNotFoundError as e:
            _logger.info("Server Structure File not found")

        await server.load_data_type_definitions()
        hardware_ip = plc_ip_address.split(";")
        ipaddress=[hardware_ip[i].split(":") for i in range(len(hardware_ip))]
        """
        Initializing read only nodes and hmi nodes
        """
        _logger.info("Initializing Nodes from XML File")
        device_group=[]
        device_hmi_group=[]
        root_obj = await server.nodes.root.get_child(["0:Objects", "2:Device"])
        root_obj_children = await root_obj.get_children()
        for i in range(len(root_obj_children)): #loop based on how many plc is connected
            category = await root_obj_children[i].get_children()
            category_group = []
            for k in range(len(category)):
                category_name = (await category[k].read_display_name()).Text
                test = await category[k].get_children()
                hmi_group=[]
                if category_name not in 'hmi':
                    data_group=[(test[l]) for l in range(len(test))]
                else:
                    for l in range(len(test)):
                        await test[l].set_writable(True)
                        hmi_group.append(test[l])
                category_group.append(data_group)
                device_hmi_group.append(hmi_group)
            device_group.append(category_group)    
        device_hmi_group = [x for x in device_hmi_group if x]
        _logger.info("Done Initializing Nodes from XML")
        global device_hmi_global
        device_hmi_global = device_hmi_group

        """
        Init node subscription for HMI       
        """
        _logger.info("Initializing Nodes for HMI Subscription")
        #for i in range(len(device_hmi_group)):
        init_hmi = [await self.hmi_init(server,device_hmi_group[i],ipaddress[i]) for i in range(len(device_hmi_group))]
        """
        Create node subscription for HMI       
        """
        hmi_handler = SubServerHandler()
        hmi_sub = await server.create_subscription(20, hmi_handler)
        sub = [await hmi_sub.subscribe_data_change(device_hmi_group[i][k],queuesize=1) for k in range(len(device_hmi_group[i])) for i in range(len(device_hmi_group))]
        _logger.info("Done Initializing Nodes for HMI Subscription")
        """
        Device group consist of read only data nodes that is contained in category list 
        that is contained device group list *triple layer. This allows the server to accomate 
        more than one PLC. The same is applied to device hmi group.
        """
        
        async with server:
            start_device=[0 for x in range(len(device_group))]
            zipped_data=[0 for x in range(len(device_group))]
            tcp_rw=[0 for x in range(len(device_group))]
            _logger.info('Initializing server!')
            for i in range(len(device_group)):
                start_device[i],zipped_data[i]=await asyncio.create_task(self.init_server(server,_logger,device_group[i],ipaddress[i]))
                rdr, wrtr = await asyncio.open_connection(ipaddress[i][0], ipaddress[i][1])
                tcp_rw[i] = [rdr , wrtr]
            _logger.info('Starting server!')
            while stop_threads==False:
                await asyncio.sleep(0.1)
                tasks = [await asyncio.create_task(self.scan_loop_plc(start_device[i],zipped_data[i],server,ipaddress[i],tcp_rw[i])) for i in range(len(device_group))]

        
        _logger.info('Server Has Stopped!')


