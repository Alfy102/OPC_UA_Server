import asyncio
import logging
import itertools
import re
import collections
from asyncua.ua.uatypes import DataValue, DateTime
from asyncua import server, ua, Server
from asyncua.common.methods import uamethod




#module to send socket command to PLC
async def plc_tcp_socket(start_device,number_of_devices,reader,writer):
    encapsulate = bytes(f"RDS {start_device} {number_of_devices}\r",'utf-8')
    writer.write(encapsulate)
    recv_value = await reader.read(2048)
    recv_value = recv_value.decode('UTF-8').split()
    return recv_value


async def plc_source_time(reader,writer):
    time_encapsulate = bytes(f"RDS CM700 6\r",'utf-8')
    writer.write(time_encapsulate)
    recv_timestamp = await reader.read(100)
    recv_timestamp = recv_timestamp.decode('UTF-8').split()
    recv_timestamp = str(recv_timestamp[0][-2:])+","+str(recv_timestamp[1][-2:])+","+str(recv_timestamp[2][-2:])+","+str(recv_timestamp[3][-2:])+","+str(recv_timestamp[4][-2:])+","+str(recv_timestamp[5][-2:])
    recv_timestamp = DateTime.strptime(recv_timestamp,"%y,%m,%d,%H,%M,%S")
    return recv_timestamp

async def set_plc_time(reader,writer, time):
    year = str(time.year)[-2:]
    month =f"{time.month:02}"
    day =f"{time.day:02}"
    hour =f"{time.hour:02}"
    minute =f"{time.minute:02}"
    second =f"{time.second:02}"
    day_number = DateTime.now().strftime('%w')
    encapsulate = bytes(f"WRT {year} {month} {day} {hour} {minute} {second} {day_number}\r",'utf-8')
    writer.write(encapsulate)
    recv_value = await reader.read(100)

#module to read and write to OPC nodes
async def rw_opc(nodes_id,data_list,source_time,server):
    if isinstance(nodes_id,list):# and len(data_list[0])==1:
        for i in range(len(nodes_id)):
            data_value = ua.DataValue((int(data_list[i])),SourceTimestamp=source_time, ServerTimestamp=DateTime.utcnow())
            await server.write_attribute_value(nodes_id[i].nodeid, data_value)#,attr=ua.AttributeIds.Value)

    else:
        data_value = ua.DataValue((int(data_list)),SourceTimestamp=source_time, ServerTimestamp=DateTime.utcnow())
        await server.write_attribute_value(nodes_id.nodeid, data_value)#attr=ua.AttributeIds.Value)

async def nodes_init(Param,addspace,start_device,devices_qty):
    start_device = re.split('(\d+)', start_device)
    start_address=int(start_device[1])
    if start_device[0]=="R":
        Relay_node_name_list=list(itertools.chain(*[[(f"{start_device[0]}{start_address+i+(j*100):05}") for i in range(16)] for j in range(0,(devices_qty//16)+1)]))
    else:
        Relay_node_name_list=list([(f"{start_device[0]}{start_address+i:05}") for i in range(devices_qty)])
    Relay_nodes=[]
    for l in range(devices_qty):
        Relay_nodes.append(await Param.add_variable(addspace, Relay_node_name_list[l], 0, varianttype=ua.VariantType.Int64))
        await Relay_nodes[l].set_writable()        
    return Relay_nodes

async def plc_to_opc(i, dv, current_list,source_time,nodes_id,server):
    if dv[i]!=current_list[i]:
        dv[i]=current_list[i]
    asyncio.create_task(rw_opc(nodes_id[i],dv[i],source_time,server))
    return dv

async def scan_loop(reader,writer,start_address,number_of_devices,device_nodes,read_device,source_time,server):
    current_relay_list = await plc_tcp_socket(start_address,number_of_devices,reader,writer)
    read_device = asyncio.gather(*(plc_to_opc(i, read_device, current_relay_list,source_time, device_nodes,server) for i in range(len(read_device))))

async def main():

    list_of_devices=[("R100",32),("DM1000",32),("R400",16)]

    _logger = logging.getLogger('server_log')
    server = Server()
    await server.init()
    #open server at local host ip address
    url = "opc.tcp://localhost:4840" 
    server.set_endpoint(url)

    name = "OPC_PLC_SERVER"
    addspace = await server.register_namespace(name) #idx
    Param = await server.nodes.objects.add_object(addspace, 'PLC1')

    plc_reader, plc_writer = await asyncio.open_connection("192.168.0.11", 8501)

    #initializing opc nodes value with current relay value in PLC
    source_time = await plc_source_time(plc_reader,plc_writer)
    device_nodes=[]
    read_device=[]
    for i in range(len(list_of_devices)): 
        #print(i)
        device_nodes.append(await nodes_init(Param,addspace,list_of_devices[i][0],list_of_devices[i][1]))
        read_device.append(await plc_tcp_socket(list_of_devices[i][0],list_of_devices[i][1],plc_reader,plc_writer))
        await rw_opc(device_nodes[i],read_device[i],source_time,server)
    #dm_nodes = await nodes_init(Param,addspace,start_dm_address,number_of_dm)
    #read_dm=await plc_tcp_socket(start_dm_address,number_of_dm,plc_reader,plc_writer)
    #await rw_opc(dm_nodes,read_dm,dm_source_time,server)
    #dm_source_time = relay_source_time
  
    _logger.info('Set PLC time!')
    await  set_plc_time(plc_reader,plc_writer,DateTime.utcnow())

    _logger.info('Starting server!')
  
    async with server:
        while True:
            #await asyncio.sleep(3)
            #reader,writer,start_address,number_of_devices,device_nodes,read_device,source_time,server
            for i in range(len(list_of_devices)):
                source_time = await plc_source_time(plc_reader,plc_writer)
                await asyncio.create_task(scan_loop(plc_reader,plc_writer,list_of_devices[i][0],list_of_devices[i][1],device_nodes[i],read_device[i],source_time,server))
            #for i in range(len(list_of_devices)):
            #    await scan_loop(plc_reader,plc_writer,list_of_devices[i][0],list_of_devices[i][1],device_nodes[i],read_device[i],source_time,server)
            #current_relay_list = await plc_tcp_socket(start_relay_address,number_of_relay,plc_reader,plc_writer)
            #current_dm_list = await plc_tcp_socket(start_dm_address,number_of_dm,plc_reader,plc_writer)
            #current_source_time = await plc_source_time(plc_reader,plc_writer)
            #read_dm = await asyncio.gather(*(plc_to_opc(i, read_dm, current_dm_list,current_source_time, dm_nodes,server) for i in range(len(read_dm))))
            #read_relay = await asyncio.gather(*(plc_to_opc(i, read_relay, current_relay_list,current_source_time, Relay_nodes,server) for i in range(len(read_relay))))


    
    

if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())