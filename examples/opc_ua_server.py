import asyncio
import logging
import os.path

from asyncua.ua.uatypes import DataValue, DateTime, Int64
from asyncua import ua, Server
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


async def opc_server():#-------------------------------------------------------------------------------------------------PLC OPC Server starts here
    _logger = logging.getLogger('server_log')
    server = Server()
    await server.init()
    _logger.info("Initializing Server")
    server.set_endpoint("opc.tcp://localhost:4840" )
    await server.import_xml("standard_server_structure.xml")
    await server.load_data_type_definitions()


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
    
    print(len(device_group))
    device_hmi_group = [x for x in device_hmi_group if x]
    print(len(device_hmi_group))
            #category_sub.append(test)
            #for l in range(len(category_sub)):
            #    print((await category_sub[i].read_display_name()).Text)
    #print(category_sub)
        #print(root_obj_children[i])
    #plc_devices = []
    #for i in range(len(devices)):
    #    name = await devices[i].read_display_name()
    #    test.append(name)
    #print(test)
    async with server:
        while True:
            await asyncio.sleep(2)


if __name__ == '__main__':
    asyncio.run(opc_server())

