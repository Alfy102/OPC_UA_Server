import os
from asyncua import Client
import asyncio
from queue import Queue
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import logging
logger = logging.getLogger('EVENT.CLIENT')
logger_alarm = logging.getLogger('ALARM.SERVER')
xml_file_path ='C:/Users/aliff/Documents/OPC_UA_Server/opc_ua_server/gsh_opc_platform (multi device)/standard_server_structure2.xml'

class SubAlarmHandler(object):
    async def datachange_notification(self, node, val, data):
        if val !=0:
            logger_alarm.info(f"Alarm Trigger at {node},with alarm code {val}")
            #to create event trigger on alarm subscription
        elif val ==0:
            logger_alarm.info(f"Alarm reset at {node}")

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """
    def datachange_notification(self, node, val, data):
        print("New data change event", node, val)

    def event_notification(self, event):
        print("New event", event)


def start_client(input_q,proc_id):
    asyncio.run(client())

async def client():
    """
    Create node subscription for Alarm Trigger
    """
    #alarm_handler = SubAlarmHandler()
    #alarm_sub = await server.create_subscription(20, alarm_handler)
    #[await alarm_sub.subscribe_data_change(device_alarm_group[i][k],queuesize=1) for k in range(len(device_alarm_group[i])) for i in range(len(device_group))]
    url = "opc.tcp://127.0.0.1:4840/gshopcua/server"
    await asyncio.sleep(5)
    logger.info("Connecting to server")
    async with Client(url=url) as client:
        logger.info('Children of root are: %r', await client.nodes.root.get_children())
        idx = await client.get_namespace_index(uri="Keyence_PLC_Server")
        main_folder = await client.nodes.objects.get_child(f"{idx}:Device")
        main_devices = await main_folder.get_children()
        while True:
            await asyncio.sleep(5)
            print(struct_children)

