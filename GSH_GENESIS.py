import PySimpleGUI as sg
import machine_library as PLC
import logo_data as lg

title_font=(None,19,'bold')
heading_font=(None,13,'bold')
subtitle_font=(None,13)
button_font=(None,9)
zero_pad=(0,0)

main_page_color='Snow'
output_page_color=main_page_color
input_page_color=main_page_color
#written by Mohd Aliff

POLL_FREQUENCY = 200 #update frequency
#-------------------------------------------------------------------top_info_bar_layout------------------------------------------------------------------
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

#---------------------------------------------------------Main_page_layout-------------------------------------------------------------------------
#consist of module page, IO list page, Lot information page, Log page and settings page.
def IO_layout_list(set,starting_number,io_type):
    if io_type=='input':
        io_color=input_page_color
    elif io_type=='output':
        io_color=output_page_color
    IO_layout=[]
    for i in range(0,16):
        input_name=f'R{(i+starting_number):003} | '+PLC.IO_sample(set)[i]
        IO_layout += [[sg.Button('',image_data=lg.logo('toggle_off'),mouseover_colors=io_color,button_color=io_color,image_subsample=3,border_width=0,key=f'button_R{(i+starting_number):03}',pad=(5,7)),
        sg.Text(input_name, text_color='black',font=(None,12), justification='left',size=(35,1),background_color=io_color)]]
    return IO_layout 

input_layout_1=[[sg.Column(IO_layout_list(0,0,'input'),background_color=input_page_color),
                sg.Column(IO_layout_list(1,100,'input'),background_color=input_page_color)]]

input_layout_2=[[sg.Column(IO_layout_list(2,200,'input'),background_color=input_page_color),
                sg.Column(IO_layout_list(3,300,'input'),background_color=input_page_color)]]
input_layout=[[sg.Text('Input List',font=title_font,text_color='ForestGreen',background_color=main_page_color)],[
                sg.Column(input_layout_1,justification='center',background_color=input_page_color,size=(800,750),visible=True,key='input_page_1',pad=(0,0)),
                sg.Column(input_layout_2,justification='center',background_color=input_page_color,size=(800,750),visible=False,key='input_page_2',pad=(0,0))],
                [sg.B('Page 1',key='input_1'),sg.B('Page 2',key='input_2')]]


output_layout_1=[[sg.Column(IO_layout_list(4,500,'output'),background_color=output_page_color),
                sg.Column(IO_layout_list(5,600,'output'),background_color=output_page_color)]]
output_layout_2=[[sg.Column(IO_layout_list(6,700,'output'),background_color=output_page_color)]]
output_layout=[[sg.Text('Output List',font=title_font,text_color='DarkRed',background_color=main_page_color)],
                [sg.Column(output_layout_1,justification='center',background_color=output_page_color,size=(800,750),visible=True,key='output_page_1',pad=(0,0)),
                sg.Column(output_layout_2,justification='center',background_color=output_page_color,size=(800,750),visible=False,key='output_page_2',pad=(0,0))],
                [sg.B('Page 1',key='output_1'),sg.B('Page 2',key='output_2')]]





module_page=[[sg.T('Module')]]
io_list_page=[[sg.Column(input_layout,background_color=main_page_color),sg.VerticalSeparator(color='light grey'),sg.Column(output_layout,background_color=main_page_color,pad=(7,5))]]
lot_information_page=[[sg.T('Lot Information')]]
log_page=[[sg.T('Log')]]
settings_page=[[sg.T('Settings')]]





Main_Page=[[
            sg.Column(module_page,visible=True,key='main_page_1'),
            sg.Column(io_list_page,visible=False,background_color=main_page_color,key='main_page_2'),
            sg.Column(lot_information_page,visible=False,key='main_page_3'),
            sg.Column(log_page,visible=False,key='main_page_4'),
            sg.Column(settings_page,visible=False,key='main_page_5')]
            ]



#----------------------------------------------------------------------side_menu_layout---------------------------------------------------------------------
side_menu_layout=[
                [sg.Image(data=lg.logo('company_logo'),background_color='white',size=(104,60),pad=(5,(0,4)))],
                [sg.B('IO MODULE',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',35195),key='main_button_1')],
                [sg.B('IO LIST',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_2')],
                [sg.B('LOT OEE',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_3')],
                [sg.B('LOG',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_4')],
                [sg.B('SETTINGS',font=heading_font,border_width=1,size=(12,2),pad=(0,0),button_color=('white',23375),key='main_button_5')]                
                ]



#Without title bar - looks better
window_layout =[
                [sg.Column(info_bar_layout,vertical_alignment='top',background_color='white',pad=(0,0),expand_x=True)],
                [sg.Column(side_menu_layout,justification='left',size=(120,180),background_color='DarkTurquoise',expand_y=True,pad=(0,0)),
                sg.Column(Main_Page,pad=(0,0),background_color=main_page_color,size=(1800,850),expand_x=True,expand_y=True),]
                ]

window = sg.Window('GSH Genesis', window_layout, background_color='white', no_titlebar=False, location=(0,0), size=(1920,1080), keep_on_top=False, resizable=True).Finalize()
window.Maximize()

#---------------------------------------------governs main page----------------------------------------------------------------------
def main_page_button(event):
    for i in range(1,6):
        window[f'main_button_{i}'].update(button_color=('white',23375)) #change button color to default for other button
        window[f'main_page_{i}'].update(visible=False) #change all page to false visible
    window[event].update(button_color=('white',35195))
    window[f'main_page_'+event[-1]].update(visible=True)



#---------------------------------------------governs io page----------------------------------------------------------------------
def io_page_button(event):
    y=event.split("_")
    for i in range(1,3):
        window[f'input_{i}'].update(button_color=('white',23375)) #change button color to default for other button
        window[y[0]+f'_page_{i}'].update(visible=False) #change all page to false visisble
    window[event].update(button_color=('white',35195))
    window[y[0]+'_page_'+y[1]].update(visible=True)
    

#------------------------------------------------------------------------------------------------------------------------------------
while True:
    
    event, values = window.read(timeout=POLL_FREQUENCY)
    print(event, values)
    

    if event in (None,'Exit'):
        break

    if PLC.machine_UPH()>0:
        
        window['UPH_Status'].update(PLC.machine_UPH())
        window['UPH_Sprint_Status'].update(PLC.machine_UPH())
        window.refresh()

    if event == 'main_button_1': main_page_button(event)
    elif event == 'main_button_2': main_page_button(event)
    elif event == 'main_button_3': main_page_button(event)
    elif event == 'main_button_4': main_page_button(event)
    elif event == 'main_button_5': main_page_button(event)

    if event == 'input_1': io_page_button(event)
    elif event == 'input_2': io_page_button(event)

    if event == 'output_1': io_page_button(event)
    elif event == 'output_2': io_page_button(event)
    if event == 'button_R000':
        window[event].update(image_data=lg.logo('toggle_on'),image_subsample=3)
        



window.close()



