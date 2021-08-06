import PySimpleGUI as sg
from asyncua.common import node
import machine_library as PLC
import logo_data as lg

from asyncua import Client, Node
import asyncio

def IO_sample(group):
    if group==0:
        io_list=['EMO 1','EMO 2','Vertical Corr Cylinder 2 Up','Vertical Corr Cylinder 2 Down','Spare','Incoming Air Pressure On','Front Left Door Switch','Front Right Door Switch',
                    'Rear Left Door Switch','Rear Right Door Switch','Degate Stopper Up RS 1','Degate Stopper Down RS 1','Degate Pusher Up RS','Degate Pusher Down RS',
                    'Degate Pusher Fwd RS','Degate Pusher Rvs RS']
    elif group==1:
        io_list=['Lead Frame Present At Entrance', 'Lead Frame Present At Degate', 'Friction 1 Ext RS', 'Degate Stopper Up RS 2', 'Friction 2 Ext RS', 'Degate Stopper Down RS 2', 
                    'Clamper 1 Ext RS', 'Clamper 1 Rvs RS', 'Clamper 2 Ext RS', 'Clamper 2 Rvs RS', 'Degate Fwd RS', 'Degate Rvs RS', 'Degate Up RS', 'Degate Dwn RS', 'Linear Track Full Sensor 2', 
                    'Linear Track in Position Sensor 2']
    elif group==2:
        io_list=['Walking Beam Ext 1 RS','Walking Beam Rvs 1 RS','Walking Beam Ext 2 RS','Walking Beam Rvs 2 RS','Walking Beam Ext 3 RS','Walking Beam Rvs 3 RS','Walking Beam Ext 4 RS', 
        'Walking Beam Rvs 4 RS','WB Part Present Sensor 1','WB Part Present Sensor 2','WB Part Present Sensor 3','WB Part Present Sensor 4','WB Part Present Sensor 5','WB Part Present Sensor 6', 
        'Horizontal Correction Cyl Up','Horizontal Correction Cyl Down']
    elif group==3:
        io_list=['Spare', 'Trim Dieset Misfeed sensor', 'Spare', 'Form Dieset Misfeed Sensor', 'Linear Track Full Sensor 1', 'Linear Track in Position Sensor 1', 
        'Linear Track UP/Down Ext RS', 'Linear Track UP/Down Rvs RS', 'Reject Y Cyl Ext RS', 'Reject Y Cyl Rvs RS', 'Reject Z Cyl Up RS', 'Reject Z Cyl Down RS', 'Horizontal Corr Part Present', 
        'Vertical Corr Part Present', 'Vertical Corr Cyl Up 1', 'Vertical Corr Cyl Down 1']
    elif group==4:
        io_list=['Reject Vacuum On','Reject Vacuum Off','Horrizontal Corr Cyl','Vertical Corr Cyl 1','Vertical Corr Cyl 2','All Door Lock','Spare','Spare','Spare','Degate Stopper Up/Down', 
        'Spare','Degate Pusher Up/Down','Spare','Degate Pusher Fwd','Degate Pusher Rvs','Press 1 Relay']
    elif group==5:
        io_list=['Friction 1 Cyl Ext/Rvs','Spare','Friction 1 Motor On','Friction 2 Cyl Ext/Rvs','Spare','Friction 2 Motor On','Clamper 1 Cyl Ext','Clamper 1 Cyl Rvs','Clamper 2 Cyl Ext', 
        'Clamper 2 Cyl Rvs','Degate Cyl FWD','Degate Cyl RVS','Degate Cyl Up/Down','Spare','Degate Brush Motor On','Press 2 Relay']
    elif group==6:
        io_list=['WB 1 Cyl Ext','WB 1 Cyl Rvs','WB 2 Cyl Ext','WB 2 Cyl Rvs','WB 3 Cyl Ext','WB 3 Cyl Rvs','WB 4 Cyl Ext','WB 4 Cyl Rvs','Linear Track Cyl Up/Down','Spare','Reject Y Cyl Ext', 
        'Reject Y Cyl Rvs','Reject Z Cyl Ext','Reject Z Cyl Rvs','Stepper Enable Relay','VFD Output']
    elif group==7:
        io_list=['WB 1 Cyl Ext','WB 1 Cyl Rvs','WB 2 Cyl Ext','WB 2 Cyl Rvs','WB 3 Cyl Ext','WB 3 Cyl Rvs','WB 4 Cyl Ext','WB 4 Cyl Rvs','Linear Track Cyl Up/Down','Spare','Reject Y Cyl Ext', 
        'Reject Y Cyl Rvs','Reject Z Cyl Ext','Reject Z Cyl Rvs','Stepper Enable Relay','VFD Output']
    return io_list

async def update_window(window,io_type,io_color,data,ivn):
    if data==1: window[f'button_{io_type}_{ivn}'].update(button_color = io_color) 
    else: window[f'button_{io_type}_{ivn}'].update(button_color = "Black on Grey")

async def read_opc_2(input_nodes,window,ivn,io_type,io_color):
    data = await input_nodes.read_value()
    asyncio.create_task(update_window(window,io_type,io_color,data,ivn))

async def read_opc(input_nodes,window,ivn,io_type):
    #print(input_nodes)
    if io_type=='input': io_color="Black on lime"
    elif io_type=='output': io_color="Black on red"
    asyncio.gather(*(read_opc_2(input_nodes[i],window,ivn[i],io_type,io_color) for i in range(len(input_nodes))))

#-------------------------------Main Thread--------------------------------------------
def IO_layout_list(set,starting_number,io_type,input_button_color,output_button_color):
    if io_type=='input':
        io_color=input_button_color
        disabled_button=True
    elif io_type=='output':
        io_color=output_button_color
        disabled_button=False
    IO_layout=[]
    for i in range(0,16):
        input_name=IO_sample(set)[i]
        IO_layout += [[sg.Button(f'R{(i+starting_number):003}',disabled=disabled_button,disabled_button_color="Black on Grey",font=(None,12,'bold'),button_color=io_color,border_width=0,key=f'button_{io_type}_R{(i+starting_number):03}',pad=(1,7)),
        sg.Text(input_name, text_color='black',font=(None,12,'bold'), justification='left',size=(35,1),background_color='Snow')]]
    return IO_layout 
def main_page_button(event,window,side_menu_layout):
    for i in range(1,len(side_menu_layout)):
        window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
        window[f'main_page_{i}'].update(visible=False) #change all page to false visible
    window[event].update(button_color=('white',35195))
    number=event.split("_")
    window[f'main_page_'+number[2]].update(visible=True)
def io_page_button(event,window):
    y=event.split("_")
    for i in range(1,5):
        #window[f'input_{i}'].update(button_color=('white',23375)) #change button color to default for other button
        window[y[0]+f'_page_{i}'].update(visible=False) #change all page to false visisble
        print(y[0]+f'_page_{i}')
    
    x = (int(y[1])*2)-1
    window[y[0]+'_page_'+y[1]].update(visible=True)
    window[y[0]+'_page_'+str(x)].update(visible=True)
async def hmi():#-------------------------------------------------------------------------------------------------------OPC HMI Starts here

    title_font=(None,19,'bold')
    heading_font=(None,13,'bold')
    subtitle_font=(None,13)
    button_font=(None,9)

    main_page_color='Snow'
    output_page_color=main_page_color
    input_page_color=main_page_color
    output_button_color="Black on Grey"
    input_button_color="Black on Grey"


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


    input_layout=[[sg.Text('Input List',font=title_font,text_color='ForestGreen',background_color=main_page_color)],
                    [sg.Column(IO_layout_list(0,100,'input',input_button_color,output_button_color),background_color=input_page_color,visible=True,key='input_page_1'),
                    sg.Column(IO_layout_list(1,200,'input',input_button_color,output_button_color),background_color=input_page_color,visible=True,key='input_page_2')],
                    [sg.Column(IO_layout_list(2,300,'input',input_button_color,output_button_color),background_color=input_page_color,visible=False,key='input_page_3'),
                    sg.Column(IO_layout_list(3,400,'input',input_button_color,output_button_color),background_color=input_page_color,visible=False,key='input_page_4')],
                    [sg.B('Page 1',key='input_1'),sg.B('Page 2',key='input_2')]]

    output_layout=[[sg.Text('Output List',font=title_font,text_color='DarkRed',background_color=main_page_color)],
                    [sg.Column(IO_layout_list(4,500,'output',input_button_color,output_button_color),background_color=output_page_color,visible=True,key='output_page_1'),
                    sg.Column(IO_layout_list(5,600,'output',input_button_color,output_button_color),background_color=output_page_color,visible=True,key='output_page_2')],
                    [sg.Column(IO_layout_list(6,700,'output',input_button_color,output_button_color),background_color=output_page_color,visible=False,key='output_page_3'),
                    sg.Column(IO_layout_list(7,800,'output',input_button_color,output_button_color),background_color=output_page_color,visible=False,key='output_page_4')],
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

    window = sg.Window('GSH Genesis', window_layout, background_color='white', no_titlebar=False, location=(0,0), size=(1920,1080), keep_on_top=False, resizable=True, finalize=True)
    window.Maximize()


    client = Client(url='opc.tcp://localhost:4840/freeopcua/server/')
    async with client:

        obj=[]
        init_value = []
        nodes = []
        io_type=[]
        obj.append(await client.nodes.root.get_child(["0:Objects", "2:plc1_relay_input"])) #obj[0]
        io_type.append("input")
        obj.append(await client.nodes.root.get_child(["0:Objects", "2:plc1_relay_output"])) #obj[1]
        io_type.append("output")
        input_variable_name = []
        for i in range(len(obj)):
            ivn=[]
            nodes.append(await obj[i].get_children())
            for k in range(len(nodes[i])):
                display_name = await nodes[i][k].read_display_name() #get the display name of the variables, will be use to send to plc socket
                ivn.append(display_name.Text)
                init_value.append(await nodes[i][k].read_value())
            input_variable_name.append(ivn)



        input_obj=await client.nodes.root.get_child(["0:Objects", "2:plc1_hmi_input"])
        input_nodes=await input_obj.get_children()
        ovn=[]
        button_states=[]
        for i in range(len(input_nodes)):
            hmi_display_name = await input_nodes[i].read_display_name()
            ovn.append(hmi_display_name.Text)
            button_states.append(0)
        print(ovn)
        
        down = True      
        while True:
            await asyncio.sleep(0.1)
            #print(input_data_list)
            for i in range(len(nodes)):
                try:
                    tasks = await asyncio.create_task(read_opc(nodes[i],window,input_variable_name[i],io_type[i]))
        
                except KeyboardInterrupt as e:
                    tasks.cancel()
                    tasks.exception()
            
            event, values = window.read(timeout=10)
            if event in (None,'Exit'):
                break

            if PLC.machine_UPH()>0:
                window['UPH_Status'].update(PLC.machine_UPH())
                window['UPH_Sprint_Status'].update(PLC.machine_UPH())
                
            for n in range(1,16):
                if event == f'main_button_{n}': main_page_button(event,window,side_menu_layout)

            for m in range(1,3):
                if event == f'input_{m}': io_page_button(event,window)

            for m in range(1,3):
                if event == f'output_{m}': io_page_button(event,window)


            for m in range(len(input_nodes)):
                if event == f'button_output_{ivn[m]}':
                    if button_states[m]==0:
                        await input_nodes[m].write_value(1)
                        button_states[m]=1
                    elif button_states[m]==1:
                        await input_nodes[m].write_value(0)
                        button_states[m]=0
                    


            
            #await asyncio.gather(*(read_opc(nodes[i],window,input_variable_name[i],io_type[i]) for i in range(len(nodes))))


    window.close()
if __name__ == '__main__':
    asyncio.run(hmi())