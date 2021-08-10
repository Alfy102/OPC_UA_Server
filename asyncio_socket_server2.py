import asyncio
import random
async def handle_echo(reader, writer):
    data = await reader.read(1000)
    message = data.decode('UTF-8').split()
    #addr = writer.get_extra_info('peername')
    print(message)
    process_1 = message
    if process_1[1] in 'CM700':
        recv_value2 = "00021 00008 00010 00008 00010 00020"
    else:
        range_number = int(process_1[2])
        str1= " "
        recv_value=[]
        for i in range(range_number):
            recv_value.append(str(random.randint(0,1)))
        recv_value2=str1.join(recv_value)

    encapsulate = bytes(f"{recv_value2}\r\n",'utf-8')
    print(encapsulate)
    writer.write(encapsulate)
    #await writer.drain()
    writer.close()



loop = asyncio.get_event_loop() 
coro = asyncio.start_server(handle_echo, '127.0.0.2', 8888, loop=loop) 

server = loop.run_until_complete(coro)
 # Serve requests until Ctrl+C is pressed 

print('Serving on {}'.format(server.sockets[0].getsockname()))
try: 
    loop.run_forever() 
except KeyboardInterrupt: 
    pass 
# Close the server 
server.close() 
loop.run_until_complete(server.wait_closed()) 
loop.close()