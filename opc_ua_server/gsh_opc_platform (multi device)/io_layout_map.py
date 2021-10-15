from datetime import timedelta
from asyncua.ua.uatypes import flatten_and_get_shape


node_structure = {

#---------------------------------------------------------------------------------
#lot counting and yield variables
#---------------------------------------------------------------------------------
10000:{ 'name': 'lot_barcode_fail_count',
        'label_point':['barcode_fail_count_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True, 'rw': 'rw', 'initial_value': 0},
        'monitored_node': 11000},

10001:{ 'name': 'lot_barcode_pass_count',
        'label_point':['barcode_pass_count_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 11001},

10002:{ 'name': 'lot_total_quantity_in',
        'label_point':['total_quantity_in_label','label_75'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 11002},

10003:{ 'name': 'lot_total_quantity_out',
        'label_point':['total_quantity_out_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 11003},

10004:{ 'name': 'lot_total_pass',
        'label_point':['total_passed_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 11004},

10005:{ 'name': 'lot_total_fail',
        'label_point':['total_failed_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 11005},

10006:{ 'name': 'lot_soft_jam',
        'label_point':['soft_jam_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10007:{ 'name': 'lot_hard_jam',
        'label_point':['hard_jam_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10008:{ 'name': 'lot_mtbf',
        'label_point':['mtbf_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10009:{ 'name': 'lot_mtba',
        'label_point':['mtba_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10010:{ 'name': 'lot_error_count',
        'label_point':['error_count_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 11010},

10011:{ 'name': 'lot_total_yield',
        'label_point':['total_yield_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'Float', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0.0},
        'monitored_node': None},

#---------------------------------------------------------------------------------
#Shift count and yield variables
#---------------------------------------------------------------------------------
10020:{ 'name': 'shift_total_quantity_in',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'shift_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 11002},

10021:{ 'name': 'shift_total_quantity_out',
        'label_point':['shift_total_qty_out_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'shift_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 11003},

10022:{ 'name': 'shift_total_pass',
        'label_point':['shift_total_passed_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'shift_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 11004},

10023:{ 'name': 'shift_total_fail',
        'label_point':['shift_total_fail_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'shift_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 11005},

10024:{ 'name': 'shift_soft_jam',
        'label_point':['shift_soft_jam_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'shift_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10025:{ 'name': 'shift_hard_jam',
        'label_point':['shift_hard_jam_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'shift_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10026:{ 'name': 'shift_mtbf',
        'label_point':['shift_mtbf_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'shift_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10027:{ 'name': 'shift_mtba',
        'label_point':['shift_mtba_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'shift_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10028:{ 'name': 'shift_total_yield',
        'label_point':['shift_total_yield_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'Float', 'category': 'shift_variables', 'history': True,'rw': 'rw', 'initial_value': 0.0},
        'monitored_node': None},

#---------------------------------------------------------------------------------
#minute interval UPH
#---------------------------------------------------------------------------------

10030:{ 'name': 'production_uph',
        'label_point':['production_uph_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},



#---------------------------------------------------------------------------------
#Lot and shift time variables
#---------------------------------------------------------------------------------

10040:{ 'name': 'shift_uptime',
        'label_point':['shift_uptime_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'shift_time_variables', 'history': False,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': None},

10041:{ 'name': 'shift_operation_time',
        'label_point':['shift_operation_time_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'shift_time_variables', 'history': True,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': 10070}, #refers to device_mode

10042:{ 'name': 'shift_down_time',
        'label_point':['shift_down_time_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'shift_time_variables', 'history': True,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': 10071}, #refers to device_mode

10043:{ 'name': 'shift_idling_time',
        'label_point':['shift_idling_time_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'shift_time_variables', 'history': True,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': 10072}, #refers to device_mode
 
10044:{ 'name': 'lot_uptime',
        'label_point':['lot_uptime_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'shift_time_variables', 'history': False,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': None},

10045:{ 'name': 'lot_operation_time',
        'label_point':['lot_operation_time_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'time_variables', 'history': True,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': 10070}, #refers to device_mode

10046:{ 'name': 'lot_down_time',
        'label_point':['lot_down_time_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'time_variables', 'history': True,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': 10071}, #refers to device_mode

10047:{ 'name': 'lot_idling_time',
        'label_point':['lot_idling_time_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'time_variables', 'history': True,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': 10072}, #refers to device_mode
 
10048:{ 'name': 'lot_maintenance_time',
        'label_point':['lot_maintenance_time_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'time_variables', 'history': True,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': 10073}, #refers to device_mode

#---------------------------------------------------------------------------------
#Lot ID Information (from client)
#---------------------------------------------------------------------------------
10050:{ 'name': 'lot_id',
        'label_point':['lot_id_input'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'lot_input', 'history': True,'rw': 'rw', 'initial_value': ''},
        'monitored_node': None},
10051:{ 'name': 'operator_id',
        'label_point':['operator_id_input'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'lot_input', 'history': True,'rw': 'rw', 'initial_value': ''},
        'monitored_node': None},
10052:{ 'name': 'package_name',
        'label_point':['package_name_input'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'lot_input', 'history': True,'rw': 'rw', 'initial_value': ''},
        'monitored_node': None},
10053:{ 'name': 'device_id',
        'label_point':['device_id_input'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'lot_input', 'history': True,'rw': 'rw', 'initial_value': ''},
        'monitored_node': None},
10054:{ 'name': 'lot_start_time',
        'label_point':['lot_start_date_time'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'lot_input', 'history': True,'rw': 'rw', 'initial_value': ''},
        'monitored_node': None},
10055:{ 'name': 'shift_start_time',
        'label_point':['shift_start_date_time'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'lot_input', 'history': True,'rw': 'rw', 'initial_value': ''},
        'monitored_node': None},
#---------------------------------------------------------------------------------
#PLC Clock
#---------------------------------------------------------------------------------

10060:{ 'name': 'CM700', #year
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'plc_clock','rw': 'r', 'history': False, 'initial_value': 0}},

10061:{ 'name': 'CM701', #month
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'plc_clock','rw': 'r', 'history': False, 'initial_value': 0}},

10062:{ 'name': 'CM702', #day
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'plc_clock','rw': 'r', 'history': False, 'initial_value': 0}},

10063:{ 'name': 'CM703', #hour
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'plc_clock','rw': 'r', 'history': False, 'initial_value': 0}},

10064:{ 'name': 'CM704', #minute
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'plc_clock','rw': 'r', 'history': False, 'initial_value': 0}},

10065:{ 'name': 'CM705', #second
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'plc_clock','rw': 'r', 'history': False, 'initial_value': 0}},


#---------------------------------------------------------------------------------
#Device Mode
#---------------------------------------------------------------------------------

10070:{ 'name': 'MR2000', #operation_mode (auto_mode) machine running
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'device_mode', 'history': False,'rw': 'r', 'initial_value': False}},

10071:{ 'name': 'MR2001', #stand_by_mode / down_mode (not entering auto) machine stop
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'device_mode', 'history': False,'rw': 'r', 'initial_value': False}},

10072:{ 'name': 'MR2002', #idling_mode / starving_mode (auto_mode) no maetrial
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'device_mode', 'history': False,'rw': 'r', 'initial_value': False}},

10073:{ 'name': 'MR2003', #maintenance_mode (machine_stop) machine stop
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'device_mode', 'history': False,'rw': 'r', 'initial_value': False}},

10074:{ 'name': 'MR2004', #machine_ready_to_initialize machine stop
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'device_mode', 'history': False,'rw': 'r', 'initial_value': False}},

10075:{ 'name': 'MR2005', #machine_ready_to_run machine stop
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'device_mode', 'history': False,'rw': 'r', 'initial_value': False}},


#---------------------------------------------------------------------------------
#light_tower settings
#---------------------------------------------------------------------------------
10080:{ 'name': 'machine_running',  
        'label_point':['check_box_0','check_box_1','check_box_2','check_box_3','check_box_4','check_box_5'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'light_tower_setting', 'history': True,'rw': 'rw', 'initial_value': 0}},

10081:{ 'name': 'machine_stop',  
        'label_point':['check_box_10','check_box_11','check_box_12','check_box_13','check_box_14','check_box_15'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'light_tower_setting', 'history': True,'rw': 'rw', 'initial_value': 0}},

10082:{ 'name': 'machine_alarm',  
        'label_point':['check_box_20','check_box_21','check_box_22','check_box_23','check_box_24','check_box_25'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'light_tower_setting', 'history': True,'rw': 'rw', 'initial_value': 0}},

10083:{ 'name': 'no_material',  
        'label_point':['check_box_30','check_box_31','check_box_32','check_box_33','check_box_34','check_box_35'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'light_tower_setting', 'history': True,'rw': 'rw', 'initial_value': 0}},

10084:{ 'name': 'door_bypass',  
        'label_point':['check_box_40','check_box_41','check_box_42','check_box_43','check_box_44','check_box_45'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'light_tower_setting', 'history': True,'rw': 'rw', 'initial_value': 0}},

#---------------------------------------------------------------------------------
#----------user access level restrictions
#---------------------------------------------------------------------------------
10090:{ 'name': 'level_1',
        'label_point':['check_box_1','check_box_2','check_box_3','check_box_4','check_box_5','check_box_6','check_box_7','check_box_8','check_box_9','check_box_10','check_box_11','check_box_12','check_box_13','check_box_14','check_box_15','check_box_16','check_box_17','check_box_18','check_box_19','check_box_20','check_box_21','check_box_22','check_box_23','check_box_24'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'user_access', 'history': True,'rw': 'rw', 'initial_value': 'FF0000'}},


10091:{ 'name': 'level_2',
        'label_point':['check_box_1','check_box_2','check_box_3','check_box_4','check_box_5','check_box_6','check_box_7','check_box_8','check_box_9','check_box_10','check_box_11','check_box_12','check_box_13','check_box_14','check_box_15','check_box_16','check_box_17','check_box_18','check_box_19','check_box_20','check_box_21','check_box_22','check_box_23','check_box_24'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'user_access', 'history': True,'rw': 'rw', 'initial_value': 'FFA800'}},


10092:{ 'name': 'level_3',
        'label_point':['check_box_1','check_box_2','check_box_3','check_box_4','check_box_5','check_box_6','check_box_7','check_box_8','check_box_9','check_box_10','check_box_11','check_box_12','check_box_13','check_box_14','check_box_15','check_box_16','check_box_17','check_box_18','check_box_19','check_box_20','check_box_21','check_box_22','check_box_23','check_box_24'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'user_access', 'history': True,'rw': 'rw', 'initial_value': 'FFFFFF'}},

10093:{ 'name': 'level_1',
        'label_point':[],
        'username':'user_1',
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'user_info', 'history': True,'rw': 'rw', 'initial_value': 'user_1'},
        'monitored_node': 10090},

10094:{ 'name': 'level_2',
        'label_point':[],
        'username':'user_2',
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'user_info', 'history': True,'rw': 'rw', 'initial_value': 'user_2'},
        'monitored_node': 10091},

10095:{ 'name': 'level_3',
        'label_point':[],
        'username':'user_3',
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'user_info', 'history': True,'rw': 'rw', 'initial_value': 'user_3'},
        'monitored_node': 10092},



#---------------------------------------------------------------------------------
#UPH in 24 hours
#---------------------------------------------------------------------------------

10200:{ 'name': 'uph_00_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10201:{ 'name': 'uph_00_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10202:{ 'name': 'uph_01_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10203:{ 'name': 'uph_01_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10204:{ 'name': 'uph_02_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10205:{ 'name': 'uph_02_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10206:{ 'name': 'uph_03_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10207:{ 'name': 'uph_03_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10208:{ 'name': 'uph_04_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10209:{ 'name': 'uph_04_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10210:{ 'name': 'uph_05_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10211:{ 'name': 'uph_05_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10212:{ 'name': 'uph_06_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10213:{ 'name': 'uph_06_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10214:{ 'name': 'uph_07_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10215:{ 'name': 'uph_07_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10216:{ 'name': 'uph_08_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10217:{ 'name': 'uph_08_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10218:{ 'name': 'uph_09_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10220:{ 'name': 'uph_09_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10221:{ 'name': 'uph_10_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10222:{ 'name': 'uph_10_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10223:{ 'name': 'uph_11_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10224:{ 'name': 'uph_11_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10225:{ 'name': 'uph_12_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10226:{ 'name': 'uph_12_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10227:{ 'name': 'uph_13_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10228:{ 'name': 'uph_13_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10229:{ 'name': 'uph_14_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10230:{ 'name': 'uph_14_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10231:{ 'name': 'uph_15_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10232:{ 'name': 'uph_15_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10233:{ 'name': 'uph_16_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10234:{ 'name': 'uph_16_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10235:{ 'name': 'uph_17_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10236:{ 'name': 'uph_17_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10237:{ 'name': 'uph_18_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10238:{ 'name': 'uph_18_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10239:{ 'name': 'uph_19_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10240:{ 'name': 'uph_19_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10241:{ 'name': 'uph_20_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10242:{ 'name': 'uph_20_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10243:{ 'name': 'uph_21_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10244:{ 'name': 'uph_21_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10245:{ 'name': 'uph_22_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10246:{ 'name': 'uph_22_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10247:{ 'name': 'uph_23_00',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10248:{ 'name': 'uph_23_30',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': False},
        'monitored_node': None},



#---------------------------------------------------------------------------------
#Single series relay list
#---------------------------------------------------------------------------------


10300:{ 'name': 'DM3000',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'alarm','rw': 'r', 'history': False, 'initial_value': 0}},

10301:{ 'name': 'DM3001',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'alarm','rw': 'r', 'history': False, 'initial_value': 0}},

10302:{ 'name': 'DM3002',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'alarm','rw': 'r', 'history': False, 'initial_value': 0}},

10303:{ 'name': 'DM3003',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'alarm','rw': 'r', 'history': False, 'initial_value': 0}},

10304:{ 'name': 'DM3004',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'alarm','rw': 'r', 'history': False, 'initial_value': 0}},

10305:{ 'name': 'DM3005',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'alarm','rw': 'r', 'history': False, 'initial_value': 0}},

11000:{ 'name': 'R100',
        'label_point':['label_x0000','io_module_label_x0000'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11001:{ 'name': 'R101',
        'label_point':['label_x0001','io_module_label_x0001'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11002:{ 'name': 'R102',
        'label_point':['label_x0002','io_module_label_x0002'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11003:{ 'name': 'R103',
        'label_point':['label_x0003','io_module_label_x0003'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11004:{ 'name': 'R104',
        'label_point':['label_x0004','io_module_label_x0004'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11005:{ 'name': 'R105',
        'label_point':['label_x0005','io_module_label_x0005'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11006:{ 'name': 'R106',
        'label_point':['label_x0006','io_module_label_x0006'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11007:{ 'name': 'R107',
        'label_point':['label_x0007','io_module_label_x0007'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11008:{ 'name': 'R108',
        'label_point':['label_x0008','io_module_label_x0008'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11009:{ 'name': 'R109',
        'label_point':['label_x0009','io_module_label_x0009'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11010:{ 'name': 'R110',
        'label_point':['label_x0010','io_module_label_x0010'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11011:{ 'name': 'R111',
        'label_point':['label_x0011','io_module_label_x0011'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11012:{ 'name': 'R112',
        'label_point':['label_x0012','io_module_label_x0012'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11013:{ 'name': 'R113',
        'label_point':['label_x0013','io_module_label_x0013'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11014:{ 'name': 'R114',
        'label_point':['label_x0014','io_module_label_x0014'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11015:{ 'name': 'R115',
        'label_point':['label_x0015','io_module_label_x0015'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11016:{ 'name': 'R200',
        'label_point':['label_x0100','io_module_label_x0100','main_motor_label_x0100'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11017:{ 'name': 'R201',
        'label_point':['label_x0101','io_module_label_x0101','main_motor_label_x0101'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11018:{ 'name': 'R202',
        'label_point':['label_x0102','io_module_label_x0102','main_motor_label_x0102'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11019:{ 'name': 'R203',
        'label_point':['label_x0103','io_module_label_x0103','main_motor_label_x0103'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11020:{ 'name': 'R204',
        'label_point':['label_x0104','io_module_label_x0104'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11021:{ 'name': 'R205',
        'label_point':['label_x0105','io_module_label_x0105'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11022:{ 'name': 'R206',
        'label_point':['label_x0106','io_module_label_x0106'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11023:{ 'name': 'R207',
        'label_point':['label_x0107','io_module_label_x0107'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11024:{ 'name': 'R208',
        'label_point':['label_x0108','io_module_label_x0108'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11025:{ 'name': 'R209',
        'label_point':['label_x0109','io_module_label_x0109'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11026:{ 'name': 'R210',
        'label_point':['label_x0110','io_module_label_x0110'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11027:{ 'name': 'R211',
        'label_point':['label_x0111','io_module_label_x0111'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11028:{ 'name': 'R212',
        'label_point':['label_x0112','main_motor_label_x0112'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11029:{ 'name': 'R213',
        'label_point':['label_x0113','main_motor_label_x0113'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11030:{ 'name': 'R214',
        'label_point':['label_x0114','main_motor_label_x0114'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11031:{ 'name': 'R215',
        'label_point':['label_x0115','main_motor_label_x0115'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11032:{ 'name': 'R300',
        'label_point':['label_x0200'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11033:{ 'name': 'R301',
        'label_point':['label_x0201'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11034:{ 'name': 'R302',
        'label_point':['label_x0202'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11035:{ 'name': 'R303',
        'label_point':['label_x0203'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11036:{ 'name': 'R304',
        'label_point':['label_x0204'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11037:{ 'name': 'R305',
        'label_point':['label_x0205'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11038:{ 'name': 'R306',
        'label_point':['label_x0206'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11039:{ 'name': 'R307',
        'label_point':['label_x0207'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11040:{ 'name': 'R308',
        'label_point':['label_x0208'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11041:{ 'name': 'R309',
        'label_point':['label_x0209'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11042:{ 'name': 'R310',
        'label_point':['label_x0210'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11043:{ 'name': 'R311',
        'label_point':['label_x0211'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11044:{ 'name': 'R312',
        'label_point':['label_x0212'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11045:{ 'name': 'R313',
        'label_point':['label_x0213'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11046:{ 'name': 'R314',
        'label_point':['label_x0214'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11047:{ 'name': 'R315',
        'label_point':['label_x0215'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11048:{ 'name': 'R400',
        'label_point':['label_x0300'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11049:{ 'name': 'R401',
        'label_point':['label_x0301'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11050:{ 'name': 'R402',
        'label_point':['label_x0302'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11051:{ 'name': 'R403',
        'label_point':['label_x0303'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11052:{ 'name': 'R404',
        'label_point':['label_x0304'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11053:{ 'name': 'R405',
        'label_point':['label_x0305'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11054:{ 'name': 'R406',
        'label_point':['label_x0306'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11055:{ 'name': 'R407',
        'label_point':['label_x0307'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11056:{ 'name': 'R408',
        'label_point':['label_x0308'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11057:{ 'name': 'R409',
        'label_point':['label_x0309'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11058:{ 'name': 'R410',
        'label_point':['label_x0310'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11059:{ 'name': 'R411',
        'label_point':['label_x0311'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11060:{ 'name': 'R412',
        'label_point':['label_x0312'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11061:{ 'name': 'R413',
        'label_point':['label_x0313'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11062:{ 'name': 'R414',
        'label_point':['label_x0314'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11063:{ 'name': 'R415',
        'label_point':['label_x0315'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11064:{ 'name': 'R500',
        'label_point':['label_y6000','io_module_label_y6000'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11065:{ 'name': 'R501',
        'label_point':['label_y6001','io_module_label_y6001'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11066:{ 'name': 'R502',
        'label_point':['label_y6002','io_module_label_y6002'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11067:{ 'name': 'R503',
        'label_point':['label_y6003','io_module_label_y6003'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11068:{ 'name': 'R504',
        'label_point':['label_y6004','io_module_label_y6004'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11069:{ 'name': 'R505',
        'label_point':['label_y6005','io_module_label_y6005'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11070:{ 'name': 'R506',
        'label_point':['label_y6006','io_module_label_y6006'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11071:{ 'name': 'R507',
        'label_point':['label_y6007','io_module_label_y6007'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11072:{ 'name': 'R508',
        'label_point':['label_y6008','io_module_label_y6008'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False},},

11073:{ 'name': 'R509',
        'label_point':['label_y6009','io_module_label_y6009'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11074:{ 'name': 'R510',
        'label_point':['label_y6010','io_module_label_y6010'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False},},

11075:{ 'name': 'R511',
        'label_point':['label_y6011','io_module_label_y6011'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11076:{ 'name': 'R512',
        'label_point':['label_y6012','io_module_label_y6012'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11077:{ 'name': 'R513',
        'label_point':['label_y6013','io_module_label_y6013'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11078:{ 'name': 'R514',
        'label_point':['label_y6014','io_module_label_y6014'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}, 'history': False},

11079:{ 'name': 'R515',
        'label_point':['label_y6015','io_module_label_y6015'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11080:{ 'name': 'R600',
        'label_point':['label_y6100','io_module_label_y6100'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11081:{ 'name': 'R601',
        'label_point':['label_y6101','io_module_label_y6101'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11082:{ 'name': 'R602',
        'label_point':['label_y6102','io_module_label_y6102'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11083:{ 'name': 'R603',
        'label_point':['label_y6103','io_module_label_y6103'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11084:{ 'name': 'R604',
        'label_point':['label_y6104','io_module_label_y6104'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11085:{ 'name': 'R605',
        'label_point':['label_y6105','io_module_label_y6105'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11086:{ 'name': 'R606',
        'label_point':['label_y6106','io_module_label_y6106'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11087:{ 'name': 'R607',
        'label_point':['label_y6107','io_module_label_y6107'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11088:{ 'name': 'R608',
        'label_point':['label_y6108','io_module_label_y6108'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False},},

11089:{ 'name': 'R609',
        'label_point':['label_y6109','io_module_label_y6109'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11090:{ 'name': 'R610',
        'label_point':['label_y6110','io_module_label_y6110'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11091:{ 'name': 'R611',
        'label_point':['label_y6111','io_module_label_y6111'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11092:{ 'name': 'R612',
        'label_point':['label_y6112','io_module_label_y6112'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11093:{ 'name': 'R613',
        'label_point':['label_y6113','io_module_label_y6113'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11094:{ 'name': 'R614',
        'label_point':['label_y6114','main_motor_label_y6114'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False},},

11095:{ 'name': 'R615',
        'label_point':['label_y6115','main_motor_label_y6115'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11096:{ 'name': 'R700',
        'label_point':['label_y6200','main_motor_label_y6200'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11097:{ 'name': 'R701',
        'label_point':['label_y6201','main_motor_label_y6201'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11098:{ 'name': 'R702',
        'label_point':['label_y6202'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11099:{ 'name': 'R703',
        'label_point':['label_y6203'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11100:{ 'name': 'R704',
        'label_point':['label_y6204'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11101:{ 'name': 'R705',
        'label_point':['label_y6205'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11102:{ 'name': 'R706',
        'label_point':['label_y6206'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11103:{ 'name': 'R707',
        'label_point':['label_y6207'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11104:{ 'name': 'R708',
        'label_point':['label_y6208'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11105:{ 'name': 'R709',
        'label_point':['label_y6209'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11106:{ 'name': 'R710',
        'label_point':['label_y6210'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11107:{ 'name': 'R711',
        'label_point':['label_y6211'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11108:{ 'name': 'R712',
        'label_point':['label_y6212'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11109:{ 'name': 'R713', 
        'label_point':['label_y6213'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11110:{ 'name': 'R714', 
        'label_point':['label_y6214'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

11111:{ 'name': 'R715', 
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},



#---------------------------------------------------------------------------------
#--------Motor properties
#---------------------------------------------------------------------------------

11200:{ 'name': 'CM1000', #Motor 1 memory 1 
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},

11201:{ 'name': 'CM1001', #Motor 1 memory 2
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},

11202:{ 'name': 'CM1002', #Motor 1 memory 3 
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},

11203:{ 'name': 'CM1003', #Motor 1 memory 4
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},

11204:{ 'name': 'CM1004', #Motor 1 memory 5
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},

11205:{ 'name': 'CM1005', #Motor 1 memory 6
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},

11206:{ 'name': 'CM1006', #Motor 1 memory 7
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},

11207:{ 'name': 'CM1007', #Motor 1 memory 8
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},

11208:{ 'name': 'CM1008', #Motor 1 memory 9
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},

11208:{ 'name': 'CM1008', #Motor 1 memory 10
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},


11208:{ 'name': 'CM1008', #Motor memory 2
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},


11208:{ 'name': 'CM1008', #Motor memory 2
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},


11208:{ 'name': 'CM1008', #Motor memory 2
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},


11208:{ 'name': 'CM1008', #Motor memory 2
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},


11208:{ 'name': 'CM1008', #Motor memory 2
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},


11208:{ 'name': 'CM1008', #Motor memory 2
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'data_memory','rw': 'r', 'history': False, 'initial_value': 0}},






#---------------------------------------------------------------------------------
#Input for hmi
#---------------------------------------------------------------------------------

13000:{ 'name': 'MR1000',
        'label_point':['label_y6000','io_module_label_y6000'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13001:{ 'name': 'MR1001',
        'label_point':['label_y6001','io_module_label_y6001'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13002:{ 'name': 'MR1002',
        'label_point':['label_y6002','io_module_label_y6002'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13003:{ 'name': 'MR1003',
        'label_point':['label_y6003','io_module_label_y6003'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13004:{ 'name': 'MR1004',
        'label_point':['label_y6004','io_module_label_y6004'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13005:{ 'name': 'MR1005',
        'label_point':['label_y6005','io_module_label_y6005'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13006:{ 'name': 'MR1006',
        'label_point':['label_y6006','io_module_label_y6006'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13007:{ 'name': 'MR1007',
        'label_point':['label_y6007','io_module_label_y6007'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13008:{ 'name': 'MR1008',
        'label_point':['label_y6008','io_module_label_y6008'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13009:{ 'name': 'MR1009',
        'label_point':['label_y6009','io_module_label_y6009'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13010:{ 'name': 'MR1010',
        'label_point':['label_y6010','io_module_label_y6010'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13011:{ 'name': 'MR1011',
        'label_point':['label_y6011','io_module_label_y6011'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13012:{ 'name': 'MR1012',
        'label_point':['label_y6012','io_module_label_y6012'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13013:{ 'name': 'MR1013',
        'label_point':['label_y6013','io_module_label_y6013'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13014:{ 'name': 'MR1014',
        'label_point':['label_y6014','io_module_label_y6014'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13015:{ 'name': 'MR1015',
        'label_point':['label_y6015','io_module_label_y6015'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13016:{ 'name': 'MR1100',
        'label_point':['label_y6100','io_module_label_y6100'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13017:{ 'name': 'MR1101',
        'label_point':['label_y6101','io_module_label_y6101'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13018:{ 'name': 'MR1102',
        'label_point':['label_y6102','io_module_label_y6102'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13019:{ 'name': 'MR1103',
        'label_point':['label_y6103','io_module_label_y6103'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13020:{ 'name': 'MR1104',
        'label_point':['label_y6104','io_module_label_y6104'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13021:{ 'name': 'MR1105',
        'label_point':['label_y6105','io_module_label_y6105'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13022:{ 'name': 'MR1106',
        'label_point':['label_y6106','io_module_label_y6106'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13023:{ 'name': 'MR1107',
        'label_point':['label_y6107','io_module_label_y6107'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13024:{ 'name': 'MR1108',
        'label_point':['label_y6108','io_module_label_y6108'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13025:{ 'name': 'MR1109',
        'label_point':['label_y6109','io_module_label_y6109'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13026:{ 'name': 'MR1110',
        'label_point':['label_y6110','io_module_label_y6110'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13027:{ 'name': 'MR1111',
        'label_point':['label_y6111','io_module_label_y6111'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13028:{ 'name': 'MR1112',
        'label_point':['label_y6112','io_module_label_y6112'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13029:{ 'name': 'MR1113',
        'label_point':['label_y6113','io_module_label_y6113'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13030:{ 'name': 'MR1114',
        'label_point':['label_y6114','main_motor_label_y6114'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13032:{ 'name': 'MR1115',
        'label_point':['label_y6115','main_motor_label_y6115'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13033:{ 'name': 'MR1200',
        'label_point':['label_y6200','main_motor_label_y6200'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13034:{ 'name': 'MR1201',
        'label_point':['label_y6201','main_motor_label_y6201'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13035:{ 'name': 'MR1202',
        'label_point':['label_y6202'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13036:{ 'name': 'MR1203',
        'label_point':['label_y6203'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13037:{ 'name': 'MR1204',
        'label_point':['label_y6204'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13038:{ 'name': 'MR1205',
        'label_point':['label_y6205'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13039:{ 'name': 'MR1206',
        'label_point':['label_y6206'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False},},

13040:{ 'name': 'MR1207',
        'label_point':['label_y6207'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13041:{ 'name': 'MR1208',
        'label_point':['label_y6208'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13042:{ 'name': 'MR1209',
        'label_point':['label_y6209'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13043:{ 'name': 'MR1210',
        'label_point':['label_y6210'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13044:{ 'name': 'MR1211',
        'label_point':['label_y6211'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13045:{ 'name': 'MR1212',
        'label_point':['label_y6212'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13046:{ 'name': 'MR1213',
        'label_point':['label_y6213'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13047:{ 'name': 'MR1214',
        'label_point':['label_y6214'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},

13048:{ 'name': 'MR1215',
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'client_input_1','rw': 'rw', 'history': False, 'initial_value': False}},


}


alarm_list={
        1000:['Alarm 1',0,1],	
        1001:['Alarm 2',0,1],	
        1002:['Alarm 3',0,1],	
        1003:['Alarm 4',0,1],	
        1004:['Alarm 5',0,1],	
        1005:['Alarm 6',0,1],	
        1006:['Alarm 7',0,1],	
        1007:['Alarm 8',0,1],	
        1008:['Alarm 9',0,1],	
        1009:['Alarm 10',0,1],	
        1010:['Alarm 11',0,1],	
        1011:['Alarm 12',0,1],	
        1012:['Alarm 13',0,1],	
        1013:['Alarm 14',0,1],	
        1014:['Alarm 15',0,1],	
        1015:['Alarm 16',0,1],	
        1016:['Alarm 17',0,1],	
        1017:['Alarm 18',0,1],	
        1018:['Alarm 19',0,1],	
        1019:['Alarm 20',0,1],	
        1020:['Alarm 21',0,1],	
        1021:['Alarm 22',0,1],	
        1022:['Alarm 23',0,1],	
        1023:['Alarm 24',0,1],
}

socket_server_dictionary={
1:('R100',0),
2:('R101',0),
3:('R102',0),
4:('R103',0),
5:('R104',0),
6:('R105',0),
7:('R106',0),
8:('R107',0),
9:('R108',0),
10:('R109',0),
11:('R110',0),
12:('R111',0),
13:('R112',0),
14:('R113',0),
15:('R114',0),
16:('R115',0),
17:('R200',0),
18:('R201',0),
19:('R202',0),
20:('R203',0),
21:('R204',0),
22:('R205',0),
23:('R206',0),
24:('R207',0),
25:('R208',0),
26:('R209',0),
27:('R210',0),
28:('R211',0),
29:('R212',0),
30:('R213',0),
31:('R214',0),
32:('R215',0),
33:('R300',0),
34:('R301',0),
35:('R302',0),
36:('R303',0),
37:('R304',0),
38:('R305',0),
39:('R306',0),
40:('R307',0),
41:('R308',0),
42:('R309',0),
43:('R310',0),
44:('R311',0),
45:('R312',0),
46:('R313',0),
47:('R314',0),
48:('R315',0),
49:('R400',0),
50:('R401',0),
51:('R402',0),
52:('R403',0),
53:('R404',0),
54:('R405',0),
55:('R406',0),
56:('R407',0),
57:('R408',0),
58:('R409',0),
59:('R410',0),
60:('R411',0),
61:('R412',0),
62:('R413',0),
63:('R414',0),
64:('R415',0),
65:('R500',0),
66:('R501',0),
67:('R502',0),
68:('R503',0),
69:('R504',0),
70:('R505',0),
71:('R506',0),
72:('R507',0),
73:('R508',0),
74:('R509',0),
75:('R510',0),
76:('R511',0),
77:('R512',0),
78:('R513',0),
79:('R514',0),
80:('R515',0),
81:('R600',0),
82:('R601',0),
83:('R602',0),
84:('R603',0),
85:('R604',0),
86:('R605',0),
87:('R606',0),
88:('R607',0),
89:('R608',0),
90:('R609',0),
91:('R610',0),
92:('R611',0),
93:('R612',0),
94:('R613',0),
95:('R614',0),
96:('R615',0),
97:('R700',0),
98:('R701',0),
99:('R702',0),
100:('R703',0),
101:('R704',0),
102:('R705',0),
103:('R706',0),
104:('R707',0),
105:('R708',0),
106:('R709',0),
107:('R710',0),
108:('R711',0),
109:('R712',0),
110:('R713',0),
111:('R714',0),
112:('R715',0),
113:('DM3000',1234),
114:('DM3001',1235),
115:('DM3002',1236),
116:('DM3003',1237),
117:('DM3004',1238),
118:('DM3005',1239),
119:('MR1000',0),
120:('MR1001',0),
121:('MR1002',0),
122:('MR1003',0),
123:('MR1004',0),
124:('MR1005',0),
125:('MR1006',0),
126:('MR1007',0),
127:('MR1008',0),
128:('MR1009',0),
129:('MR1010',0),
130:('MR1011',0),
131:('MR1012',0),
132:('MR1013',0),
133:('MR1014',0),
134:('MR1015',0),
135:('MR1100',0),
136:('MR1101',0),
137:('MR1102',0),
138:('MR1103',0),
139:('MR1104',0),
140:('MR1105',0),
141:('MR1106',0),
142:('MR1107',0),
143:('MR1108',0),
144:('MR1109',0),
145:('MR1110',0),
146:('MR1111',0),
147:('MR1112',0),
148:('MR1113',0),
149:('MR1114',0),
150:('MR1115',0),
151:('MR1200',0),
152:('MR1201',0),
153:('MR1202',0),
154:('MR1203',0),
155:('MR1204',0),
156:('MR1205',0),
157:('MR1206',0),
158:('MR1207',0),
159:('MR1208',0),
160:('MR1209',0),
161:('MR1210',0),
162:('MR1211',0),
163:('MR1212',0),
164:('MR1213',0),
165:('MR1214',0),
166:('MR1215',0),
167:('MR2000',0),
168:('MR2001',0),
169:('MR2002',0),
170:('MR2003',0),
170:('MR2004',0),
170:('MR2005',0),
171:('CM700',0),
172:('CM701',0),
173:('CM702',0),
174:('CM703',0),
175:('CM704',0),
176:('CM705',0),
177:('DM1000',0),
178:('DM1001',0),
179:('DM1002',0),
180:('DM1003',0),
181:('DM1004',0),
182:('DM1005',0),
}

time_series_axis = [
            "00:00",
            "00:30",
            "01:00",
            "01:30",
            "02:00",
            "02:30",
            "03:00",
            "03:30",
            "04:00",
            "04:30",
            "05:00",
            "05:30",
            "06:00",
            "06:30",
            "07:00",
            "07:30",
            "08:00",
            "08:30",
            "09:00",
            "09:30",
            "10:00",
            "10:30",
            "11:00",
            "11:30",
            "12:00",
            "12:30",
            "13:00",
            "13:30",
            "14:00",
            "14:30",
            "15:00",
            "15:30",
            "16:00",
            "16:30",
            "17:00",
            "17:30",
            "18:00",
            "18:30",
            "19:00",
            "19:30",
            "20:00",
            "20:30",
            "21:00",
            "21:30",
            "22:00",
            "22:30",
            "23:00",
            "23:30",         
           ]