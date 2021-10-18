import asyncio
from datetime import datetime
from io_layout_map import socket_server_dictionary
import collections



class socket(object):
    def __init__(self):
        self.io_dict = collections.OrderedDict(sorted(socket_server_dictionary.items()))
        asyncio.run(self.main())


    async def handle_echo(self,reader, writer):
        current_time = datetime.now()
        self.io_dict[173]=('CM700',f"{current_time.year:05}")
        self.io_dict[174]=('CM701',f"{current_time.month:05}")
        self.io_dict[175]=('CM702',f"{current_time.day:05}")
        self.io_dict[176]=('CM703',f"{current_time.hour:05}")
        self.io_dict[177]=('CM704',f"{current_time.minute:05}")
        self.io_dict[178]=('CM705',f"{current_time.second:05}")
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
                start_time = datetime.now()
                self.io_dict[179]=('DM1000',f"{start_time.year:05}")
                self.io_dict[180]=('DM1001',f"{start_time.month:05}")
                self.io_dict[181]=('DM1002',f"{start_time.day:05}")
                self.io_dict[182]=('DM1003',f"{start_time.hour:05}")
                self.io_dict[183]=('DM1004',f"{start_time.minute:05}")
                self.io_dict[184]=('DM1005',f"{start_time.second:05}")
                await server.serve_forever()


if __name__ == '__main__':
    socket()