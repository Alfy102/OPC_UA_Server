import asyncio
import sys
# sys.path.insert(0, "..")
import logging
from asyncua import Client, Node, ua

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')


async def main():
    url = "opc.tcp://172.26.192.1:12345"
    # url = 'opc.tcp://commsvr.com:51234/UA/CAS_UA_Server'
    async with Client(url=url) as client:
        #uri = "Parameters"
        #namespace = await client.get_namespace_index(uri)
        while True:
            await asyncio.sleep(0.5)
            Relay1 = client.get_node("ns=2;i=2")
            Relay2 = client.get_node("ns=2;i=3")
            Relay3 = client.get_node("ns=2;i=4")
            await Relay1.write_value(True)
            await Relay2.write_value(True)
            await Relay3.write_value(True)
        


if __name__ == '__main__':
    asyncio.run(main())