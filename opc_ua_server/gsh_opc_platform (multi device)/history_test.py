import asyncio
import sys
# sys.path.insert(0, "..")
import logging
from asyncua import Client, Node, ua
from datetime import datetime
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')


async def main():
    url = 'opc.tcp://localhost:4840/gshopcua/server'
    # url = 'opc.tcp://commsvr.com:51234/UA/CAS_UA_Server'
    async with Client(url=url) as client:
        data = 1
        source_time = datetime.utcnow()
        var = client.get_node(ua.NodeId(2048, 2))
        data_value = ua.DataValue(ua.Variant(data, ua.VariantType.Int64),SourceTimestamp=source_time, ServerTimestamp=source_time)
        await var.write_value(data_value)
       

if __name__ == '__main__':
    asyncio.run(main())