import asyncio
from asyncua import ua

async def plc_tcp_socket_read(ip_address:str, port_number:str,start_device:str,number_of_device:int):
    """send a tcp socket request to Keyence PLC to read the data according the address number

    Args:
        ip_address (string): PLC IP Address
        port_number (string): PLC Port Number
        start_device (string): start address that wants to read
        number_of_device (int): n many address to read after the start address

    Returns:
        list: return a list of int with n size
    """
    reader, writer = await asyncio.open_connection(ip_address, port_number)
    encapsulate = bytes(f"RDS {start_device} {number_of_device}\r\n","utf-8")
    writer.write(encapsulate)
    await writer.drain()
    recv_value = await reader.readuntil(separator=b'\r\n') 
    recv_value = recv_value.decode("UTF-8").split()
    recv_value = [int(recv_value[i]) for i in range(len(recv_value))]
    writer.close()
    return recv_value

async def plc_tcp_socket_write(ip_address:str, port_number:str,start_device:str,data_value:int):
    """send a tcp socket request to Keyence PLC to write data to an address.

    Args:
        ip_address (string): PLC IP Address
        port_number (string): PLC Port Number
        start_device (string): address
        data_value (int): the desired data to be written to the PLC address

    Returns:
        list: if write is successfull, return OK. Else, return PLC Error code.
    """
    reader, writer = await asyncio.open_connection(ip_address, port_number)
    message = f"WR {start_device} {int(data_value)}\r\n"
    encapsulate = bytes(message,'utf-8')
    writer.write(encapsulate)
    await writer.drain()
    recv_value = await reader.readuntil(separator=b'\r\n') 
    recv_value = recv_value.decode("UTF-8").split()
    recv_value = [int(recv_value[i]) for i in range(len(recv_value))]
    writer.close()
    return recv_value

def ua_variant_data_type(data_type: str, data_value: any):
    """create a UA Variant object

    Args:
        data_type (string): UInt16,UInt32,UInt64,String,Boolean,Float
        data_value (any): data to be wrapped inside the UA Variant Object

    Returns:
        ua object: ua object to used when writing to client
    """
    if data_type == 'UInt16':
        ua_var = ua.Variant(int(data_value), ua.VariantType.UInt16)
    elif data_type == 'UInt32':
        ua_var = ua.Variant(int(data_value), ua.VariantType.UInt32)
    elif data_type == 'UInt64':    
        ua_var = ua.Variant(int(data_value), ua.VariantType.UInt64)
    elif data_type == 'String':
        ua_var = ua.Variant(str(data_value), ua.VariantType.String)
    elif data_type == 'Boolean':
        ua_var = ua.Variant(bool(data_value), ua.VariantType.Boolean)
    elif data_type == 'Float':
        ua_var = ua.Variant(float(data_value), ua.VariantType.Float)
        
    return ua_var


def data_type_conversion(data_type, data_value):
    """convert data types, to safeguard I/O operation

    Args:
        data_type (string): [description]
        data_value (any): [description]

    Returns:
        [type]: [description]
    """
    if data_type == 'UInt16':
        data_value = int(data_value)
    elif data_type == 'UInt32':
        data_value = int(data_value)
    elif data_type == 'UInt64':    
        data_value = int(data_value)
    elif data_type == 'String':
        data_value = str(data_value)
    elif data_type == 'Boolean':
        data_value = bool(data_value)
    elif data_type == 'Float':
        data_value = float(data_value)
    return data_value

