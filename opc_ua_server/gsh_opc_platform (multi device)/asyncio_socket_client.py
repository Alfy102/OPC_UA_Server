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
    print(test)

async def main():
    #await tcp_echo_client("WR R102 1\r\n")
    #await tcp_echo_client("WR R102 0\r\n")
    await tcp_echo_client("WR MR2000 0\r\n")
    await tcp_echo_client("WR MR2001 0\r\n")
    await tcp_echo_client("WR MR2002 0\r\n")
    await tcp_echo_client("WR MR2003 0\r\n")
    await tcp_echo_client("WR MR2004 0\r\n")
    """while True:
        await asyncio.sleep(random.randrange(10,100)/100)
    #    #print("ON")
        await tcp_echo_client("WR R100 1\r\n")
        await tcp_echo_client("WR R101 1\r\n")
        await tcp_echo_client("WR R102 1\r\n")
        await tcp_echo_client("WR R103 1\r\n")
        await tcp_echo_client("WR R104 1\r\n")
        await tcp_echo_client("WR R105 1\r\n")
        await tcp_echo_client("WR R106 1\r\n")
        await asyncio.sleep(random.randrange(10,100)/100)
        await tcp_echo_client("WR R100 0\r\n")
        await tcp_echo_client("WR R101 0\r\n")
        await tcp_echo_client("WR R102 0\r\n")
        await tcp_echo_client("WR R103 0\r\n")
        await tcp_echo_client("WR R104 0\r\n")
        await tcp_echo_client("WR R105 0\r\n")
        await tcp_echo_client("WR R106 0\r\n")"""
        

        

       #print("OFF")


asyncio.run(main())