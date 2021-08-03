import asyncio
from asyncio.tasks import create_task

async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection('192.168.0.11', 8501)

    print(f'Send: {message!r}')
    encapsulate = bytes(message,'utf-8')
    writer.write(encapsulate)


    data = await reader.read(100000)
    data = data.decode('UTF-8').split()
    print(f'Received: {data}')

    print('Close the connection')
    writer.close()




async def main():
    task=asyncio.create_task(tcp_echo_client("WR R015 1\r\n"))
    await task

asyncio.run(main())