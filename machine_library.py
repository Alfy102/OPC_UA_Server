import random
def machine_status_check(x):
    #x=0 #to be change to refer to machine server
    if x==1:
        status='ERROR'
        bg_color='red'
        text_color='white'
        alarm=machine_alarm()
    else:
        status='OPERATIONAL'
        bg_color='light grey'
        text_color='black'
        alarm=' '
    return [status, bg_color, text_color,alarm];

def machine_mode_check(x):
    x=1#x=0 #to be change to refer to machine server
    if x==1:
        status='ERROR'
        bg_color='red'
        text_color='white'
    else:
        status='RUNNING'
        bg_color='light grey'
        text_color='black'
    return [status, bg_color, text_color];

def machine_UPH():
    numbers = list(range(10000, 50000))
    random.shuffle(numbers)
    for random_number in numbers[:1]:
        UPH_speed=random_number
        return UPH_speed

def machine_alarm():
    #x=0 #to be change to refer to machine server
    alarm_message='1718: DEGATE STOPPER#2 DOWN FAIL CHK X2105'
    return alarm_message

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
    return io_list