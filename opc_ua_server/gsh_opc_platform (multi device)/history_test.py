import asyncio
import sys
# sys.path.insert(0, "..")
import logging
from asyncua import Client, Node, ua
from datetime import datetime
#logging.basicConfig(level=logging.INFO)
#_logger = logging.getLogger('asyncua')


async def main():
    url = 'opc.tcp://localhost:4840/gshopcua/server'
    # url = 'opc.tcp://commsvr.com:51234/UA/CAS_UA_Server'
    async with Client(url=url) as client:
        var = client.get_node(ua.NodeId(2167, 2))
        test = await var.get_parent()
        print(await test.read_browse_name())
       

if __name__ == '__main__':
    asyncio.run(main())