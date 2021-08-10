import asyncio
import logging
import os.path
from PyQt5.QtCore import QObject, QThread
from asyncua.ua.uatypes import DateTime
from asyncua import ua, Server
import sys
from PyQt5.uic import loadUi
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 


hmi_input_list=[]
hmi_data_list=[]
hmi_flag = False
xml_file_path ='C:/Users/aliff/Documents/OPC_UA_Server/opc_plc_server.xml'
#plc_ip_address='192.168.0.11:8501'
plc_ip_address='127.0.0.1:8888'
set_plc_time=False
server_ip='192.168.0.15:4840'
class SubServerHandler(object):
    
    def datachange_notification(self, node, val, data):
        global hmi_flag
        hmi_flag = True
        index = hmi_input_list.index(node)
        hmi_data_list[index] = val

class opc_server_worker(QObject):
    def start_opc_server(self):
        logging.basicConfig(level=logging.INFO)
        asyncio.run(self.opc_server())

    async def plc_tcp_socket(self,start_device,number_of_devices,reader,writer):
        encapsulate = bytes(f"RDS {start_device} {number_of_devices}\r",'utf-8')
        writer.write(encapsulate)
        recv_value = await reader.read(2048)

        recv_value = recv_value.decode('UTF-8').split()
        return recv_value

    async def hmi_input_status(self,input_variable_names,data_value,reader,writer):
        global hmi_flag
        encapsulate = bytes(f"WR {input_variable_names} {data_value}\r",'utf-8')
        writer.write(encapsulate)
        recv_value = await reader.read(50)
        recv_value = recv_value.decode('UTF-8').split()
        hmi_flag = False

    async def plc_source_time(self,reader,writer):
        recv_timestamp = await self.plc_tcp_socket("CM700",6,reader, writer)
        print(recv_timestamp)
        recv_timestamp = str(recv_timestamp[0][-2:])+","+str(recv_timestamp[1][-2:])+","+str(recv_timestamp[2][-2:])+","+str(recv_timestamp[3][-2:])+","+str(recv_timestamp[4][-2:])+","+str(recv_timestamp[5][-2:])
        recv_timestamp = DateTime.strptime(recv_timestamp,"%y,%m,%d,%H,%M,%S")
        #recv_timestamp = DateTime.utcnow()
        return recv_timestamp

    async def set_plc_time(self,reader,writer, time):
        year = str(time.year)[-2:]
        month =f"{time.month:02}"
        day =f"{time.day:02}"
        hour =f"{time.hour:02}"
        minute =f"{time.minute:02}"
        second =f"{time.second:02}"
        day_number = DateTime.now().strftime('%w')
        encapsulate = bytes(f"WRT {year} {month} {day} {hour} {minute} {second} {day_number}\r",'utf-8')
        writer.write(encapsulate)
        recv_value = await reader.read(50)

    #module to read and write to OPC nodes
    async def rw_opc(self,nodes_id,data_list,source_time,server):
        print(data_list)
        if isinstance(nodes_id,list):
            for i in range(len(nodes_id)):
                data_value = ua.DataValue((int(data_list[i])),SourceTimestamp=DateTime.utcnow(), ServerTimestamp=DateTime.utcnow())
                asyncio.create_task(server.write_attribute_value(nodes_id[i].nodeid, data_value))

        else:
            data_value = ua.DataValue((int(data_list)),SourceTimestamp=DateTime.utcnow(), ServerTimestamp=DateTime.utcnow())
            asyncio.create_task(server.write_attribute_value(nodes_id.nodeid, data_value))

    async def plc_to_opc(self,i, dv, current_list,source_time,nodes_id,server):
        if dv[i]!=current_list[i]:
            dv[i]=current_list[i]
            asyncio.create_task(self.rw_opc(nodes_id[i],dv[i],source_time,server))
        return dv

    async def scan_loop_plc(self,reader,writer,start_address,number_of_devices,nodes_id,read_device,source_time,server):
        current_relay_list = await self.plc_tcp_socket(start_address,number_of_devices,reader,writer)
        read_device = asyncio.gather(*(self.plc_to_opc(i, read_device, current_relay_list,source_time, nodes_id,server) for i in range(len(read_device))))


    """
    To create a modular tcp to plc function
    """

    async def tcp_socket(self,plc_address):
        ipaddressport = plc_address.split(":")
        reader, writer = await asyncio.open_connection(ipaddressport[0], ipaddressport[1])
        source_time = await self.plc_source_time(reader,writer)







    async def opc_server(self):#-------------------------------------------------------------------------------------------------PLC OPC Server starts here
        _logger = logging.getLogger('server_log')
        server = Server()
        await server.init()
        _logger.info("Initializing Server")
        endpoint = server_ip
        server.set_endpoint(f"opc.tcp://{endpoint}" )

        _logger.info(f"Establisihing Server at {endpoint}")
        try:
            _logger.info("loading server structure from file")
            list_nodes = await server.import_xml(xml_file_path)
        except FileNotFoundError as e:
            _logger.info("File not found")

        """
        #plc_ip_address = "192.168.0.11"
        _logger.info("Connecting to PLC at " + plc_ip_address)
        address_port = plc_ip_address.split(":")
        try:
            plc_reader, plc_writer = await asyncio.open_connection(address_port[0], address_port[1])
        except WindowsError as e:
            _logger.info("No Connection to PLC\nExiting with Code 1")
            sys.exit(1)
        """
        await server.load_data_type_definitions()
        #_logger.info("Connected to PLC")
        #check for plc connection
        _logger.info("Initializing Nodes")
#----------------------------------------------------------------------------------------------
        """
        Initializing read only nodes and hmi nodes
        """
        device_group=[]
        device_hmi_group=[]
        root_obj = await server.nodes.root.get_child(["0:Objects", "2:Device"])
        root_obj_children = await root_obj.get_children()
        for i in range(len(root_obj_children)): #loop based on how many plc is connected
            #print((await root_obj_children[i].read_display_name()).Text)
            category = await root_obj_children[i].get_children()
            category_group = []
            for k in range(len(category)):
                category_name = (await category[k].read_display_name()).Text
                test = await category[k].get_children()
                data_group=[]
                hmi_group=[]
                if category_name not in 'hmi':
                    for l in range(len(test)):
                        #data_group.append((await test[l].read_display_name()).Text)
                        data_group.append(test[l])
                else:
                    for l in range(len(test)):
                        #hmi_group.append((await test[l].read_display_name()).Text)
                        await test[l].set_writable(True)
                        hmi_group.append(test[l])
                category_group.append(data_group)
                device_hmi_group.append(hmi_group)
            device_group.append(category_group)
        
        #print(device_group)
        device_hmi_group = [x for x in device_hmi_group if x]
        #print(device_hmi_group)
        """
        Device group consist of read only data nodes that is contained in category list 
        that is contained device group list *triple layer. This allows the server to accomate 
        more than one PLC. The same is applied to device hmi group.
        """
#---------------------------------------------------------------------------------------------


        for i in range(len(plc_obj)):
            #input_device_nodes.append(await plc_obj[i].get_children()) #get children of of the above node. Can use len to determine the number of variables
            display_name = await input_device_nodes[i][0].read_display_name() #get the display name of the variables, will be use to send to plc socket
            start_device.append(display_name.Text)
            read_device.append(await self.plc_tcp_socket(start_device[i],len(input_device_nodes[i]),plc_reader,plc_writer))
            await self.rw_opc(input_device_nodes[i],read_device[i],source_time,server)
        
        #----------------------------------------------HMI subscription-----------------------------------------------
        hmi_handler = SubServerHandler()
        hmi_sub = await server.create_subscription(20, hmi_handler)
        hmi_obj=[]
        input_hmi_nodes = []
        hmi_obj.append(await server.nodes.root.get_child(["0:Objects", "2:plc1_hmi_input"]))
        #obj.append(await client.nodes.root.get_child(["0:Objects", "2:plc1_dm_input"]))
        ivn=[]
        for i in range(len(hmi_obj)):
            
            input_hmi_nodes.append(await hmi_obj[i].get_children())
            for k in range(len(input_hmi_nodes[i])):
                display_name = await input_hmi_nodes[i][k].read_display_name() #get the display name of the variables, will be use to send to plc socket
                ivn.append(display_name.Text)
                await hmi_sub.subscribe_data_change(input_hmi_nodes[i][k],queuesize=1)
                hmi_input_list.append(input_hmi_nodes[i][k])
                hmi_data_list.append(0)
                await input_hmi_nodes[i][k].set_writable(True)
        #-------------------------------------------------------------------------------------------------------------
        _logger.info('Starting server!')
        async with server:

            #######################  


            ##########################

            if set_plc_time==True:
                await self.set_plc_time(plc_reader,plc_writer,DateTime.utcnow())
                _logger.info('Sync PLC time with server')
            while not QThread.currentThread().isInterruptionRequested():
                await asyncio.sleep(0.001)
                for i in range(len(plc_obj)):
                    try:
                        source_time = await self.plc_source_time(plc_reader,plc_writer)
                        tasks = await asyncio.create_task(self.scan_loop_plc(plc_reader,plc_writer,start_device[i],len(read_device[i]),input_device_nodes[i],read_device[i],source_time,server))
                
                    except KeyboardInterrupt as e:
                        _logger.info("Caught keyboard interrupt. Canceling tasks...")
                        tasks.cancel()
                        tasks.exception()
                    if hmi_flag == True:
                        for i in range(len(ivn)):
                            await self.hmi_input_status(ivn[i],hmi_data_list[i], plc_reader,plc_writer)
        _logger.info('Server Stopped!')






























class server_conf(QDialog):
    def __init__(self):
        super(server_conf, self).__init__()
        loadUi('server_conf.ui', self)
        self.setWindowTitle("Configure Server")
        self.pushButton_browse.clicked.connect(self.open_xml)
        self.buttonBox.accepted.connect(self.ok_button)
        self.buttonBox.rejected.connect(self.cancel_button)

    def open_xml(self):
        dlg = QFileDialog()
        fileName = dlg.getOpenFileName(self, 'OpenFile')
        self.lineEdit_3.setText(str(fileName[0]))

    def ok_button(self):
        global plc_ip_address
        global set_plc_time
        global xml_file_path
        global server_ip
        if self.checkBox.isChecked():
            set_plc_time=True
        else:
            set_plc_time=False
        plc_ip_address = self.lineEdit_2.text()
        xml_file_path = self.lineEdit_3.text()
        server_ip = self.lineEdit.text()

    def cancel_button(self):
        self.close()


def main():
    thread = QThread()

    worker = opc_server_worker()
    worker.moveToThread(thread)
    thread.started.connect(worker.start_opc_server)

    
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    tray = QSystemTrayIcon()
    menu = QMenu()
    option1 = QAction("Start Server")
    option2 = QAction("Stop Server")
    option3 = QAction("Configure Server")
    option1.triggered.connect(lambda: tray_start_button(thread))
    option2.triggered.connect(lambda: tray_stop_button(thread))
    option3.triggered.connect(server_conf_dialog)
    menu.addAction(option1)
    menu.addAction(option2)
    menu.addAction(option3)

    # To quit the app
    quit = QAction("Quit")
    quit.triggered.connect(app.quit)
    menu.addAction(quit)
    icon = QIcon("icons8.png")
    tray.setIcon(icon)
    tray.setVisible(True)
    tray.setContextMenu(menu)
    sys.exit(app.exec_())

def tray_start_button(thread):
    thread.start()

def tray_stop_button(thread):
    thread.requestInterruption()
    thread.quit()
def server_conf_dialog():
    server_configuration = server_conf()
    server_configuration.exec_()

if __name__ == '__main__':
    main()