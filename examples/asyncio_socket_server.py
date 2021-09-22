import asyncio
import random

async def handle_echo(reader, writer):
    data = await reader.readuntil(separator=b'\n')
    message = data.decode('UTF-8').split()
    process_1 = message
    range_number = int(process_1[2])
    str1= " "
    recv_value=[]
    for i in range(range_number):
        recv_value.append(str(random.randint(0,1)))
    recv_value2=str1.join(recv_value)

    encapsulate = bytes(f"{recv_value2}\r\n",'utf-8')
    writer.write(encapsulate)


async def main():
    server = await asyncio.start_server(handle_echo, '127.0.0.1', 8501)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
            await server.serve_forever()

asyncio.run(main())