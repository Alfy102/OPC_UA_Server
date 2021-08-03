import asyncio
import logging
import itertools
import re
from asyncua.common.subscription import SubHandler
from asyncua.server.internal_server import InternalServer
from asyncua.ua.uaprotocol_auto import DataChangeNotification
from asyncua.ua.uatypes import DataValue, DateTime, Int64
from asyncua import server, ua, Server

import PySimpleGUI as sg
import machine_library as PLC
import logo_data as lg


class SubscriptionHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    """
    async def plc_tcp_socket2(self,register_name):
        reader, writer = await asyncio.open_connection("192.168.0.11", 8501)
        encapsulate = bytes(f"RDS {register_name}\r",'utf-8')
        writer.write(encapsulate)
        recv_value = reader.read(2048)
        print(recv_value)

    async def datachange_notification(self, node_id, data_value,data):
        #print("Python: New data change event", node_id, data_value)
        identifier = re.findall(r"[\w']+", str(node_id))
        identifier = int(identifier[3])-2
        for i in range(len(list_of_devices)):
            if identifier > list_of_devices[i][1]:
                identifier=identifier-list_of_devices[i][1]

            elif identifier < list_of_devices[i][1]:
                device= re.split('(\d+)', list_of_devices[i][0])
                device_number=identifier+int(device[1])
                register_name = device[0]+str(device_number)
                await SubscriptionHandler().plc_tcp_socket2(register_name)
                break

        
        
        #print(identifier)


#module to send socket command to PLC
async def plc_tcp_socket(start_device,number_of_devices,reader,writer):
    encapsulate = bytes(f"RDS {start_device} {number_of_devices}\r",'utf-8')
    writer.write(encapsulate)
    recv_value = await reader.read(2048)
    recv_value = recv_value.decode('UTF-8').split()
    return recv_value


async def plc_source_time(reader,writer):
    recv_timestamp = await plc_tcp_socket("CM700",6,reader, writer)
    recv_timestamp = str(recv_timestamp[0][-2:])+","+str(recv_timestamp[1][-2:])+","+str(recv_timestamp[2][-2:])+","+str(recv_timestamp[3][-2:])+","+str(recv_timestamp[4][-2:])+","+str(recv_timestamp[5][-2:])
    recv_timestamp = DateTime.strptime(recv_timestamp,"%y,%m,%d,%H,%M,%S")
    return recv_timestamp

async def set_plc_time(reader,writer, time):
    year = str(time.year)[-2:]
    month =f"{time.month:02}"
    day =f"{time.day:02}"
    hour =f"{time.hour:02}"
    minute =f"{time.minute:02}"
    second =f"{time.second:02}"
    day_number = DateTime.now().strftime('%w')
    encapsulate = bytes(f"WRT {year} {month} {day} {hour} {minute} {second} {day_number}\r",'utf-8')
    writer.write(encapsulate)
    recv_value = await reader.read(100)

#module to read and write to OPC nodes
async def rw_opc(nodes_id,data_list,source_time,server):
    if isinstance(nodes_id,list):# and len(data_list[0])==1:
        for i in range(len(nodes_id)):
            data_value = ua.DataValue((int(data_list[i])),SourceTimestamp=source_time, ServerTimestamp=DateTime.utcnow())
            asyncio.create_task(server.write_attribute_value(nodes_id[i].nodeid, data_value))#,attr=ua.AttributeIds.Value)

    else:
        data_value = ua.DataValue((int(data_list)),SourceTimestamp=source_time, ServerTimestamp=DateTime.utcnow())
        asyncio.create_task(server.write_attribute_value(nodes_id.nodeid, data_value))#attr=ua.AttributeIds.Value)

async def nodes_init(Param,addspace,start_device,devices_qty):
    start_device = re.split('(\d+)', start_device)
    start_address=int(start_device[1])
    if start_device[0]=="R":
        Relay_node_name_list=list(itertools.chain(*[[(f"{start_device[0]}{start_address+i+(j*100):05}") for i in range(16)] for j in range(0,(devices_qty//16)+1)]))
    else:
        Relay_node_name_list=list([(f"{start_device[0]}{start_address+i:05}") for i in range(devices_qty)])
    Relay_nodes=[]
    for l in range(devices_qty):
        Relay_nodes.append(await Param.add_variable(addspace, Relay_node_name_list[l], 0, varianttype=ua.VariantType.Int64))
        #await Relay_nodes[l].set_writable()
           
    return Relay_nodes

async def plc_to_opc(i, dv, current_list,source_time,nodes_id,server):
    if dv[i]!=current_list[i]:
        dv[i]=current_list[i]
        asyncio.create_task(rw_opc(nodes_id[i],dv[i],source_time,server))
    return dv

async def scan_loop_plc(reader,writer,start_address,number_of_devices,device_nodes,read_device,source_time,server):
    current_relay_list = await plc_tcp_socket(start_address,number_of_devices,reader,writer)
    read_device = asyncio.gather(*(plc_to_opc(i, read_device, current_relay_list,source_time, device_nodes,server) for i in range(len(read_device))))

async def IO_layout_list(set,starting_number,io_type,input_button_color,output_button_color):
    if io_type=='input':
        io_color=input_button_color
    elif io_type=='output':
        io_color=output_button_color
    IO_layout=[]
    for i in range(0,16):
        input_name=PLC.IO_sample(set)[i]
        IO_layout += [[sg.Button(f'R{(i+starting_number):003}',button_color=io_color,border_width=0,key=f'button_R{(i+starting_number):03}',pad=(5,7)),
        sg.Text(input_name, text_color='black',font=(None,12), justification='left',size=(35,1),background_color='Snow')]]
    return IO_layout 

    
async def main():
    title_font=(None,19,'bold')
    heading_font=(None,13,'bold')
    subtitle_font=(None,13)
    button_font=(None,9)
    zero_pad=(0,0)

    main_page_color='Snow'
    output_page_color=main_page_color
    input_page_color=main_page_color
    output_button_color="DarkRed on Red"
    input_button_color="Lime on Green"
    #written by Mohd Aliff

    POLL_FREQUENCY = 200 #update frequency
    
    #-------------------------------------------------------------------scheme layout------------------------------------------------------------------------
    machine_status_layout=[
                        [sg.T('MACHINE STATUS\n N/A',text_color='black',background_color='light grey',font=title_font,pad=(0,(8,2)),size=(15,2),justification='center',key='Machine_Status')],
                        [sg.T('MACHINE MODE\n N/A',text_color='black',background_color='light grey',font=title_font,pad=(0,2),size=(15,2),justification='center',key='Machine_Mode')],
                        ]


    UPH_layout_1=[[sg.T('Production UPH',text_color='black',background_color='WhiteSmoke',font=heading_font,pad=(0,(2,0)),size=(15,1),justification='center')],
        [sg.T('N/A',text_color='black',background_color='WhiteSmoke',font=subtitle_font,pad=(0,(0,2)),size=(17,2),justification='center',key='UPH_Status')]]
    UPH_layout_2=[[sg.T('Sprint UPH',text_color='black',background_color='WhiteSmoke',font=heading_font,pad=(0,(2,0)),size=(15,1),justification='center')],
        [sg.T('N/A',text_color='black',background_color='WhiteSmoke',font=subtitle_font,pad=(0,(0,2)),size=(17,2),justification='center',key='UPH_Sprint_Status')]]
    UPH_status_layout=[[sg.Column(UPH_layout_1,background_color='WhiteSmoke')],[sg.Column(UPH_layout_2,background_color='WhiteSmoke')]]
    recipe_layout=[
                    [sg.Text('Recipe',text_color='black',background_color='white', font=(heading_font),size=(20,1),justification='left')],
                    [sg.Text('PDIP CUTTING',text_color='black',background_color='white', font=subtitle_font,size=(20,2),justification='left',key='recipe_text')]
                    ]
    alarm_button=[[sg.Button('SHOW ALL', font=button_font, size=(9,1), button_color = ('black','grey'))]] #link to show all alarm log message
    alarm_status_layout=[
                        [sg.Text('Alarm',text_color='black',background_color='white', font=(heading_font),size=(160,1),justification='left')],
                        [sg.Text('',text_color='red',background_color='white', font=(None,20),size=(100,2),justification='left',key='alarm_text')],
                        [sg.Column(alarm_button, justification='left',background_color='white')]
                        ]
    connection_text_layout=[[sg.Text('Test Connection')]] #to be updated
    connection_status=[[sg.Frame('Connection Status',connection_text_layout, title_color='black',background_color='white',border_width=0,font=heading_font)]]
    info_bar_layout=[[sg.Column(machine_status_layout,background_color='white',element_justification='left', size=(230,150),pad=(0,0)),
                    sg.VerticalSeparator(color='light grey'),
                    sg.Column(recipe_layout,background_color='white',element_justification='center',size=(200,150),pad=(0,0)),
                    sg.VerticalSeparator(color='light grey'),
                    sg.Column(alarm_status_layout,background_color='white',element_justification='center',size=(1010,150),pad=(0,0)),
                    sg.VerticalSeparator(color='light grey'),
                    sg.Column(connection_status,element_justification='center',size=(250,150),background_color='white',pad=(0,0)),
                    sg.VerticalSeparator(color='light grey'),
                    sg.Column(UPH_status_layout,background_color='white',element_justification='right', size=(230,150),pad=(0,0))],
                        []]
    input_layout_1=[[sg.Column(await IO_layout_list(0,100,'input',input_button_color,output_button_color),background_color=input_page_color),
                    sg.Column(await IO_layout_list(1,200,'input',input_button_color,output_button_color),background_color=input_page_color)]]
    input_layout_2=[[sg.Column(await IO_layout_list(2,300,'input',input_button_color,output_button_color),background_color=input_page_color),
                    sg.Column(await IO_layout_list(3,400,'input',input_button_color,output_button_color),background_color=input_page_color)]]
    input_layout=[[sg.Text('Input List',font=title_font,text_color='ForestGreen',background_color=main_page_color)],[
                    sg.Column(input_layout_1,justification='center',background_color=input_page_color,size=(800,750),visible=True,key='input_page_1',pad=(0,0)),
                    sg.Column(input_layout_2,justification='center',background_color=input_page_color,size=(800,750),visible=False,key='input_page_2',pad=(0,0))],
                    [sg.B('Page 1',key='input_1'),sg.B('Page 2',key='input_2')]]
    output_layout_1=[[sg.Column(await IO_layout_list(4,500,'output',input_button_color,output_button_color),background_color=output_page_color),
                    sg.Column(await IO_layout_list(5,600,'output',input_button_color,output_button_color),background_color=output_page_color)]]
    output_layout_2=[[sg.Column(await IO_layout_list(6,700,'output',input_button_color,output_button_color),background_color=output_page_color)]]
    output_layout=[[sg.Text('Output List',font=title_font,text_color='DarkRed',background_color=main_page_color)],
                    [sg.Column(output_layout_1,justification='center',background_color=output_page_color,size=(800,750),visible=True,key='output_page_1',pad=(0,0)),
                    sg.Column(output_layout_2,justification='center',background_color=output_page_color,size=(800,750),visible=False,key='output_page_2',pad=(0,0))],
                    [sg.B('Page 1',key='output_1'),sg.B('Page 2',key='output_2')]]
    main_page=[[sg.T('MAIN PAGE')]]
    lot_entry_page=[[sg.T('Lot Entry')]]
    lot_information_page=[[sg.T('Lot Information')]]
    log_page=[[sg.T('Log')],[sg.Button("Start Server",key="opc_start"),sg.Button("Stop Server")]]
    io_list_page=[[sg.Column(input_layout,background_color=main_page_color),sg.VerticalSeparator(color='light grey'),sg.Column(output_layout,background_color=main_page_color,pad=(7,5))]]
    io_module_page=[[sg.T('IO MODULE')]]
    main_motor_page=[[sg.T('MAIN MOTOR')]]
    station_page=[[sg.T('STATION')]]
    misc_page=[[sg.T('MISC')]]
    vision_page=[[sg.T('VISION')]]
    recipe_page=[[sg.T('RECIPE')]]
    tower_light_page=[[sg.T('TOWER LIGHT')]]
    life_cycle_page=[[sg.T('LIFE CYCLE')]]
    user_area_page=[[sg.T('USER AREA')]]
    settings_page=[[sg.T('Settings')]]
    #----------------------------------------------------------------------PAGE_LAYOUT---------------------------------------------------------------------
    Main_Page=[[
                sg.Column(main_page,visible=True,key='main_page_1'),
                sg.Column(lot_entry_page,visible=False,key='main_page_2'),
                sg.Column(lot_information_page,visible=False,key='main_page_3'),
                sg.Column(log_page,visible=False,key='main_page_4'),
                sg.Column(io_list_page,visible=False,background_color=main_page_color,key='main_page_5'),
                sg.Column(io_module_page,visible=False,key='main_page_6'),
                sg.Column(main_motor_page,visible=False,key='main_page_7'),
                sg.Column(station_page,visible=False,key='main_page_8'),
                sg.Column(misc_page,visible=False,key='main_page_9'),
                sg.Column(vision_page,visible=False,key='main_page_10'),
                sg.Column(recipe_page,visible=False,key='main_page_11'),
                sg.Column(tower_light_page,visible=False,key='main_page_12'),
                sg.Column(life_cycle_page,visible=False,key='main_page_13'),
                sg.Column(user_area_page,visible=False,key='main_page_14'),
                sg.Column(settings_page,visible=False,key='main_page_15')]
                ]
    #----------------------------------------------------------------------side_menu_layout---------------------------------------------------------------------
    side_menu_layout=[
                    [sg.Image(data=lg.logo('company_logo'),background_color='white',size=(104,60),pad=(5,(0,4)))],
                    [sg.B('MAIN',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',35195),key='main_button_1')],
                    [sg.B('LOT ENTRY',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_2')],
                    [sg.B('LOT INFO',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_3')],
                    [sg.B('EVENT LOG',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_4')],
                    [sg.B('IO LIST',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_5')],
                    [sg.B('IO MODULES',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_6')],
                    [sg.B('MAIN MOTOR',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_7')],
                    [sg.B('STATION',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_8')],
                    [sg.B('VISION',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_9')],
                    [sg.B('USERS',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_10')],                
                    [sg.B('RECIPE',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_11')],
                    [sg.B('TOWER LIGHT',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_12')],
                    [sg.B('LIFE CYCLE',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_13')],
                    [sg.B('USER AREA',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_14')],
                    [sg.B('USER SETTINGS',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_15')]

                    ]
    #-------------------------------------------------------------------top_info_bar_layout------------------------------------------------------------------
    window_layout =[
                    [sg.Column(info_bar_layout,vertical_alignment='top',background_color='white',pad=(0,0),expand_x=True)],
                    [sg.Column(side_menu_layout,justification='left',size=(120,180),background_color='DarkTurquoise',expand_y=True,pad=(0,0)),
                    sg.Column(Main_Page,pad=(0,0),background_color=main_page_color,size=(1800,850),expand_x=True,expand_y=True),]
                    ]
    _logger = logging.getLogger('server_log')
    server = Server()
    await server.init()

    #open server at local host ip address
    url = "opc.tcp://localhost:4840" 
    server.set_endpoint(url)
    list_of_devices=[("R100",32),("DM1000",32),("R400",16)]
    name = "OPC_PLC_SERVER"
    addspace = await server.register_namespace(name) #idx
    Param = await server.nodes.objects.add_object(addspace, 'PLC1')
    plc_reader, plc_writer = await asyncio.open_connection("192.168.0.11", 8501)
    #initializing opc nodes value with current relay value in PLC
    source_time = await plc_source_time(plc_reader,plc_writer)
    device_nodes=[]
    read_device=[]
    for i in range(len(list_of_devices)): 
        device_nodes.append(await nodes_init(Param,addspace,list_of_devices[i][0],list_of_devices[i][1]))
        read_device.append(await plc_tcp_socket(list_of_devices[i][0],list_of_devices[i][1],plc_reader,plc_writer))
        await rw_opc(device_nodes[i],read_device[i],source_time,server)

    _logger.info('Set PLC time!')
    await  set_plc_time(plc_reader,plc_writer,DateTime.utcnow())
    
    _logger.info('Starting server!')
    window = sg.Window('GSH Genesis', window_layout, background_color='white', no_titlebar=False, location=(0,0), size=(1920,1080), keep_on_top=False, resizable=True, finalize=True)
    window.Maximize()
    async with server:

        while True:
            event, values = window.read(timeout=POLL_FREQUENCY)
            #wait asyncio.sleep(2)
            for i in range(len(list_of_devices)):
                    source_time = await plc_source_time(plc_reader,plc_writer)
                    await asyncio.create_task(scan_loop_plc(plc_reader,plc_writer,list_of_devices[i][0],list_of_devices[i][1],device_nodes[i],read_device[i],source_time,server))

            if event in (None,'Exit'):
                break

            if PLC.machine_UPH()>0:
                window['UPH_Status'].update(PLC.machine_UPH())
                window['UPH_Sprint_Status'].update(PLC.machine_UPH())
                window.refresh()

            if event == 'main_button_1':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)
            elif event == 'main_button_2':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)
            elif event == 'main_button_3':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)            
            elif event == 'main_button_4':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)            
            elif event == 'main_button_5':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)            
            elif event == 'main_button_6':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)           
            elif event == 'main_button_7':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)            
            elif event == 'main_button_8':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)            
            elif event == 'main_button_9':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)            
            elif event == 'main_button_10':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)            
            elif event == 'main_button_11':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)            
            elif event == 'main_button_12':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)            
            elif event == 'main_button_13':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)            
            elif event == 'main_button_14':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)            
            elif event == 'main_button_15':# await main_page_button(event,side_menu_layout)
                for i in range(1,len(side_menu_layout)):    
                    window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[f'main_page_{i}'].update(visible=False) #change all page to false visible
                window[event].update(button_color=('white',35195))
                number=event.split("_")
                window[f'main_page_'+number[2]].update(visible=True)
            

            if event == 'input_1': #io_page_button(event,window)
                y=event.split("_")
                for i in range(1,3):
                    window[f'input_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[y[0]+f'_page_{i}'].update(visible=False) #change all page to false visisble
                window[event].update(button_color=('white',35195))
                window[y[0]+'_page_'+y[1]].update(visible=True) 

            elif event == 'input_2': #io_page_button(event,window)
                y=event.split("_")
                for i in range(1,3):
                    window[f'input_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[y[0]+f'_page_{i}'].update(visible=False) #change all page to false visisble
                window[event].update(button_color=('white',35195))
                window[y[0]+'_page_'+y[1]].update(visible=True)


            if event == 'output_1': #io_page_button(event,window)
                y=event.split("_")
                for i in range(1,3):
                    window[f'input_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[y[0]+f'_page_{i}'].update(visible=False) #change all page to false visisble
                window[event].update(button_color=('white',35195))
                window[y[0]+'_page_'+y[1]].update(visible=True)
            elif event == 'output_2': #io_page_button(event,window)
                y=event.split("_")
                for i in range(1,3):
                    window[f'input_{i}'].update(button_color=('white',23375)) #change button color to default for other button
                    window[y[0]+f'_page_{i}'].update(visible=False) #change all page to false visisble
                window[event].update(button_color=('white',35195))
                window[y[0]+'_page_'+y[1]].update(visible=True)
            if event == 'button_R000':
                window[event].update(image_data=lg.logo('toggle_on'),image_subsample=3)
    window.close()



if __name__ == '__main__':
    asyncio.run(main())


