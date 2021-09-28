import asyncio
import random
from io_layout_map import socket_server_dictionary
import collections



class socket(object):
    def __init__(self):
        self.io_dict = collections.OrderedDict(sorted(socket_server_dictionary.items()))
        asyncio.run(self.main())


    async def handle_echo(self,reader, writer):
        data = await reader.readuntil(separator=b'\n')
        message = data.decode('UTF-8').split()
        data_value = message[2]
        str1= " "
        recv_value = []
        if message[0] == 'RDS':
            for key,value in self.io_dict.items():
                if value[0] == message[1]:
                    start_key = key
            for i in range(start_key,start_key+int(message[2])):
                value = self.io_dict[i][1]
                recv_value.append(str(value))

        elif message[0] == 'WR':
            input_key = message[1]
            
            for key,value in self.io_dict.items():
                if value[0] == input_key:
                    value = (input_key, data_value)
                    self.io_dict.update({key:value})
                    print(key, value)
                    

            
            recv_value.append(str(1))
        recv_value2=str1.join(recv_value)

        encapsulate = bytes(f"{recv_value2}\r\n",'utf-8')
        writer.write(encapsulate)


    async def main(self):
        
        server = await asyncio.start_server(self.handle_echo, '127.0.0.1', 8501)
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')
        async with server:
                await server.serve_forever()

if __name__ == '__main__':
    socket()