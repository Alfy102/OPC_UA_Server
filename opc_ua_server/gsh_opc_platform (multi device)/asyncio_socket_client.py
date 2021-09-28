import asyncio
from asyncio.tasks import create_task
import random
async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8501)
    encapsulate = bytes(message,'utf-8')
    writer.write(encapsulate)
    data = await reader.readuntil(separator=b'\n')
    test = data.decode('UTF-8').split()
    writer.close()

async def main():
    while True:
        await asyncio.sleep(random.randrange(10,100)/100)
        await tcp_echo_client("WR R103 1\r\n")
        await asyncio.sleep(random.randrange(10,100)/100)
        await tcp_echo_client("WR R103 0\r\n")


asyncio.run(main())