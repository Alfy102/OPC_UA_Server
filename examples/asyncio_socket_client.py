import asyncio
from asyncio.tasks import create_task

async def tcp_echo_client2(message):
    reader, writer = await asyncio.open_connection('192.168.0.15', 8501)
    #reader, writer = await asyncio.open_connection('127.0.0.2', 8888)

    print(f'Send: {message!r}')
    encapsulate = bytes(message,'utf-8')
    writer.write(encapsulate)


    data = await reader.readuntil(separator=b'\n')
    test = data.decode('UTF-8').split()
    #data = data.decode('UTF-8').split()
    print(f'Received: {data}')

async def main():
    while True:
        await asyncio.sleep(1)
        #task=asyncio.create_task(tcp_echo_client1("RDS R500 7\r\n"))
        task=asyncio.create_task(tcp_echo_client2("RDS R100 10\r\n"))
        #await task

asyncio.run(main())