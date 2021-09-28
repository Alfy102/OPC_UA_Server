from datetime import timedelta
from asyncua.ua.uatypes import flatten_and_get_shape


node_structure = {
10000:{ 'name': 'barcode_fail_count',
        'label_point':['barcode_fail_count_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True, 'rw': 'rw', 'initial_value': 0},
        'monitored_node': 10106},

10001:{ 'name': 'barcode_pass_count',
        'label_point':['barcode_pass_count_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 10107},

10002:{ 'name': 'total_quantity_in',
        'label_point':['total_quantity_in_label','label_75'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 10108},

10003:{ 'name': 'total_quantity_out',
        'label_point':['total_quantity_out_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 10109},

10004:{ 'name': 'total_pass',
        'label_point':['total_passed_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 10110},

10005:{ 'name': 'total_fail',
        'label_point':['total_failed_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 10111},

10006:{ 'name': 'soft_jam',
        'label_point':['soft_jam_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 10112},

10007:{ 'name': 'hard_jam',
        'label_point':['hard_jam_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 10113},

10008:{ 'name': 'mtbf',
        'label_point':['mtbf_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10009:{ 'name': 'mtba',
        'label_point':['mtba_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10010:{ 'name': 'error_count',
        'label_point':['error_count_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt32', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': 10114},

10011:{ 'name': 'total_yield',
        'label_point':['total_yield_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'Float', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0.0},
        'monitored_node': None},

10012:{ 'name': 'operation_time',
        'label_point':['operation_time_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'time_variables', 'history': True,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': 10106},

10013:{ 'name': 'down_time',
        'label_point':['down_time_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'time_variables', 'history': True,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': 10107},

10014:{ 'name': 'idling_time',
        'label_point':['idling_time_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'time_variables', 'history': True,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': 10108},

10015:{ 'name': 'maintenance_time',
        'label_point':['maintenance_time_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'String', 'category': 'time_variables', 'history': True,'rw': 'rw', 'initial_value': '0:00:00.0'},
        'monitored_node': 10109},

10016:{ 'name': 'production_uph',
        'label_point':['production_uph_label'],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'server_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10017:{ 'name': 'uph_0',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10018:{ 'name': 'uph_1',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10019:{ 'name': 'uph_2',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10020:{ 'name': 'uph_3',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10021:{ 'name': 'uph_4',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10022:{ 'name': 'uph_5',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10023:{ 'name': 'uph_6',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10024:{ 'name': 'uph_7',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10025:{ 'name': 'uph_8',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10026:{ 'name': 'uph_9',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10027:{ 'name': 'uph_10',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10028:{ 'name': 'uph_11',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10029:{ 'name': 'uph_12',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10030:{ 'name': 'uph_13',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10031:{ 'name': 'uph_14',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10032:{ 'name': 'uph_15',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10033:{ 'name': 'uph_16',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10034:{ 'name': 'uph_17',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10035:{ 'name': 'uph_18',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10036:{ 'name': 'uph_19',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10037:{ 'name': 'uph_20',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10038:{ 'name': 'uph_21',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10039:{ 'name': 'uph_22',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},

10040:{ 'name': 'uph_23',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'uph_variables', 'history': True,'rw': 'rw', 'initial_value': 0},
        'monitored_node': None},


10100:{ 'name': 'DM3000',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'alarm','rw': 'r', 'history': False, 'initial_value': 0}},

10101:{ 'name': 'DM3001',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'alarm','rw': 'r', 'history': False, 'initial_value': 0}},

10102:{ 'name': 'DM3002',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'alarm','rw': 'r', 'history': False, 'initial_value': 0}},

10103:{ 'name': 'DM3003',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'alarm','rw': 'r', 'history': False, 'initial_value': 0}},

10104:{ 'name': 'DM3004',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'alarm','rw': 'r', 'history': False, 'initial_value': 0}},

10105:{ 'name': 'DM3005',
        'label_point':[],
        'node_property':{'device': 'PLC1', 'data_type': 'UInt16', 'category': 'alarm','rw': 'r', 'history': False, 'initial_value': 0}},

10106:{ 'name': 'R100',
        'label_point':['label_x0000','io_module_label_x0000'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10107:{ 'name': 'R101',
        'label_point':['label_x0001','io_module_label_x0001'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10108:{ 'name': 'R102',
        'label_point':['label_x0002','io_module_label_x0002'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10109:{ 'name': 'R103',
        'label_point':['label_x0003','io_module_label_x0003'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10110:{ 'name': 'R104',
        'label_point':['label_x0004','io_module_label_x0004'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10111:{ 'name': 'R105',
        'label_point':['label_x0005','io_module_label_x0005'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10112:{ 'name': 'R106',
        'label_point':['label_x0006','io_module_label_x0006'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10113:{ 'name': 'R107',
        'label_point':['label_x0007','io_module_label_x0007'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10114:{ 'name': 'R108',
        'label_point':['label_x0008','io_module_label_x0008'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10115:{ 'name': 'R109',
        'label_point':['label_x0009','io_module_label_x0009'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10116:{ 'name': 'R110',
        'label_point':['label_x0010','io_module_label_x0010'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10117:{ 'name': 'R111',
        'label_point':['label_x0011','io_module_label_x0011'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10118:{ 'name': 'R112',
        'label_point':['label_x0012','io_module_label_x0012'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10119:{ 'name': 'R113',
        'label_point':['label_x0013','io_module_label_x0013'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10120:{ 'name': 'R114',
        'label_point':['label_x0014','io_module_label_x0014'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10121:{ 'name': 'R115',
        'label_point':['label_x0015','io_module_label_x0015'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10122:{ 'name': 'R200',
        'label_point':['label_x0100','io_module_label_x0100','main_motor_label_x0100'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10123:{ 'name': 'R201',
        'label_point':['label_x0101','io_module_label_x0101','main_motor_label_x0101'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10124:{ 'name': 'R202',
        'label_point':['label_x0102','io_module_label_x0102','main_motor_label_x0102'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10125:{ 'name': 'R203',
        'label_point':['label_x0103','io_module_label_x0103','main_motor_label_x0103'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10126:{ 'name': 'R204',
        'label_point':['label_x0104','io_module_label_x0104'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10127:{ 'name': 'R205',
        'label_point':['label_x0105','io_module_label_x0105'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10128:{ 'name': 'R206',
        'label_point':['label_x0106','io_module_label_x0106'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10129:{ 'name': 'R207',
        'label_point':['label_x0107','io_module_label_x0107'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10130:{ 'name': 'R208',
        'label_point':['label_x0108','io_module_label_x0108'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10131:{ 'name': 'R209',
        'label_point':['label_x0109','io_module_label_x0109'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10132:{ 'name': 'R210',
        'label_point':['label_x0110','io_module_label_x0110'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10133:{ 'name': 'R211',
        'label_point':['label_x0111','io_module_label_x0111'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10134:{ 'name': 'R212',
        'label_point':['label_x0112','main_motor_label_x0112'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10135:{ 'name': 'R213',
        'label_point':['label_x0113','main_motor_label_x0113'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10136:{ 'name': 'R214',
        'label_point':['label_x0114','main_motor_label_x0114'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10137:{ 'name': 'R215',
        'label_point':['label_x0115','main_motor_label_x0115'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10138:{ 'name': 'R300',
        'label_point':['label_x0200'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10139:{ 'name': 'R301',
        'label_point':['label_x0201'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10140:{ 'name': 'R302',
        'label_point':['label_x0202'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10141:{ 'name': 'R303',
        'label_point':['label_x0203'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10142:{ 'name': 'R304',
        'label_point':['label_x0204'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10143:{ 'name': 'R305',
        'label_point':['label_x0205'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10144:{ 'name': 'R306',
        'label_point':['label_x0206'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10145:{ 'name': 'R307',
        'label_point':['label_x0207'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10146:{ 'name': 'R308',
        'label_point':['label_x0208'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10147:{ 'name': 'R309',
        'label_point':['label_x0209'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10148:{ 'name': 'R310',
        'label_point':['label_x0210'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10149:{ 'name': 'R311',
        'label_point':['label_x0211'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10150:{ 'name': 'R312',
        'label_point':['label_x0212'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10151:{ 'name': 'R313',
        'label_point':['label_x0213'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10152:{ 'name': 'R314',
        'label_point':['label_x0214'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10153:{ 'name': 'R315',
        'label_point':['label_x0215'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10154:{ 'name': 'R400',
        'label_point':['label_x0300'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10155:{ 'name': 'R401',
        'label_point':['label_x0301'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10156:{ 'name': 'R402',
        'label_point':['label_x0302'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10157:{ 'name': 'R403',
        'label_point':['label_x0303'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10158:{ 'name': 'R404',
        'label_point':['label_x0304'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10159:{ 'name': 'R405',
        'label_point':['label_x0305'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10160:{ 'name': 'R406',
        'label_point':['label_x0306'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10161:{ 'name': 'R407',
        'label_point':['label_x0307'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10162:{ 'name': 'R408',
        'label_point':['label_x0308'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10163:{ 'name': 'R409',
        'label_point':['label_x0309'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10164:{ 'name': 'R410',
        'label_point':['label_x0310'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10165:{ 'name': 'R411',
        'label_point':['label_x0311'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10166:{ 'name': 'R412',
        'label_point':['label_x0312'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10167:{ 'name': 'R413',
        'label_point':['label_x0313'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10168:{ 'name': 'R414',
        'label_point':['label_x0314'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10169:{ 'name': 'R415',
        'label_point':['label_x0315'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10170:{ 'name': 'R500',
        'label_point':['label_y6000','io_module_label_y6000'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10171:{ 'name': 'R501',
        'label_point':['label_y6001','io_module_label_y6001'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10172:{ 'name': 'R502',
        'label_point':['label_y6002','io_module_label_y6002'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10173:{ 'name': 'R503',
        'label_point':['label_y6003','io_module_label_y6003'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10174:{ 'name': 'R504',
        'label_point':['label_y6004','io_module_label_y6004'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10175:{ 'name': 'R505',
        'label_point':['label_y6005','io_module_label_y6005'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10176:{ 'name': 'R506',
        'label_point':['label_y6006','io_module_label_y6006'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10177:{ 'name': 'R507',
        'label_point':['label_y6007','io_module_label_y6007'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10178:{ 'name': 'R508',
        'label_point':['label_y6008','io_module_label_y6008'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False},},

10179:{ 'name': 'R509',
        'label_point':['label_y6009','io_module_label_y6009'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10180:{ 'name': 'R510',
        'label_point':['label_y6010','io_module_label_y6010'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False},},

10181:{ 'name': 'R511',
        'label_point':['label_y6011','io_module_label_y6011'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10182:{ 'name': 'R512',
        'label_point':['label_y6012','io_module_label_y6012'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10183:{ 'name': 'R513',
        'label_point':['label_y6013','io_module_label_y6013'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10184:{ 'name': 'R514',
        'label_point':['label_y6014','io_module_label_y6014'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}, 'history': False},

10185:{ 'name': 'R515',
        'label_point':['label_y6015','io_module_label_y6015'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10186:{ 'name': 'R600',
        'label_point':['label_y6100','io_module_label_y6100'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10187:{ 'name': 'R601',
        'label_point':['label_y6101','io_module_label_y6101'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10188:{ 'name': 'R602',
        'label_point':['label_y6102','io_module_label_y6102'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10189:{ 'name': 'R603',
        'label_point':['label_y6103','io_module_label_y6103'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10190:{ 'name': 'R604',
        'label_point':['label_y6104','io_module_label_y6104'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10191:{ 'name': 'R605',
        'label_point':['label_y6105','io_module_label_y6105'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10192:{ 'name': 'R606',
        'label_point':['label_y6106','io_module_label_y6106'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10193:{ 'name': 'R607',
        'label_point':['label_y6107','io_module_label_y6107'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10194:{ 'name': 'R608',
        'label_point':['label_y6108','io_module_label_y6108'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False},},

10195:{ 'name': 'R609',
        'label_point':['label_y6109','io_module_label_y6109'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10196:{ 'name': 'R610',
        'label_point':['label_y6110','io_module_label_y6110'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10197:{ 'name': 'R611',
        'label_point':['label_y6111','io_module_label_y6111'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10198:{ 'name': 'R612',
        'label_point':['label_y6112','io_module_label_y6112'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10199:{ 'name': 'R613',
        'label_point':['label_y6113','io_module_label_y6113'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10200:{ 'name': 'R614',
        'label_point':['label_y6114','main_motor_label_y6114'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False},},

10201:{ 'name': 'R615',
        'label_point':['label_y6115','main_motor_label_y6115'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10202:{ 'name': 'R700',
        'label_point':['label_y6200','main_motor_label_y6200'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10203:{ 'name': 'R701',
        'label_point':['label_y6201','main_motor_label_y6201'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10204:{ 'name': 'R702',
        'label_point':['label_y6202'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10205:{ 'name': 'R703',
        'label_point':['label_y6203'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10206:{ 'name': 'R704',
        'label_point':['label_y6204'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10207:{ 'name': 'R705',
        'label_point':['label_y6205'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10208:{ 'name': 'R706',
        'label_point':['label_y6206'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10209:{ 'name': 'R707',
        'label_point':['label_y6207'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10210:{ 'name': 'R708',
        'label_point':['label_y6208'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10211:{ 'name': 'R709',
        'label_point':['label_y6209'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10212:{ 'name': 'R710',
        'label_point':['label_y6210'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10213:{ 'name': 'R711',
        'label_point':['label_y6211'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10214:{ 'name': 'R712',
        'label_point':['label_y6212'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10215:{ 'name': 'R713',
        'label_point':['label_y6213'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10216:{ 'name': 'R714',
        'label_point':['label_y6214'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

10217:{ 'name': 'R715',
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'relay','rw': 'r', 'history': False, 'initial_value': False}},

13000:{ 'name': 'MR1000',
        'label_point':['label_y6000','io_module_label_y6000'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13001:{ 'name': 'MR1001',
        'label_point':['label_y6001','io_module_label_y6001'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13002:{ 'name': 'MR1002',
        'label_point':['label_y6002','io_module_label_y6002'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13003:{ 'name': 'MR1003',
        'label_point':['label_y6003','io_module_label_y6003'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13004:{ 'name': 'MR1004',
        'label_point':['label_y6004','io_module_label_y6004'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13005:{ 'name': 'MR1005',
        'label_point':['label_y6005','io_module_label_y6005'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13006:{ 'name': 'MR1006',
        'label_point':['label_y6006','io_module_label_y6006'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13007:{ 'name': 'MR1007',
        'label_point':['label_y6007','io_module_label_y6007'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13008:{ 'name': 'MR1008',
        'label_point':['label_y6008','io_module_label_y6008'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13009:{ 'name': 'MR1009',
        'label_point':['label_y6009','io_module_label_y6009'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13010:{ 'name': 'MR1010',
        'label_point':['label_y6010','io_module_label_y6010'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13011:{ 'name': 'MR1011',
        'label_point':['label_y6011','io_module_label_y6011'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13012:{ 'name': 'MR1012',
        'label_point':['label_y6012','io_module_label_y6012'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13013:{ 'name': 'MR1013',
        'label_point':['label_y6013','io_module_label_y6013'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13014:{ 'name': 'MR1014',
        'label_point':['label_y6014','io_module_label_y6014'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13015:{ 'name': 'MR1015',
        'label_point':['label_y6015','io_module_label_y6015'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13016:{ 'name': 'MR1100',
        'label_point':['label_y6100','io_module_label_y6100'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13017:{ 'name': 'MR1101',
        'label_point':['label_y6101','io_module_label_y6101'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13018:{ 'name': 'MR1102',
        'label_point':['label_y6102','io_module_label_y6102'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13019:{ 'name': 'MR1103',
        'label_point':['label_y6103','io_module_label_y6103'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13020:{ 'name': 'MR1104',
        'label_point':['label_y6104','io_module_label_y6104'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13021:{ 'name': 'MR1105',
        'label_point':['label_y6105','io_module_label_y6105'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13022:{ 'name': 'MR1106',
        'label_point':['label_y6106','io_module_label_y6106'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13023:{ 'name': 'MR1107',
        'label_point':['label_y6107','io_module_label_y6107'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13024:{ 'name': 'MR1108',
        'label_point':['label_y6108','io_module_label_y6108'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13025:{ 'name': 'MR1109',
        'label_point':['label_y6109','io_module_label_y6109'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13026:{ 'name': 'MR1110',
        'label_point':['label_y6110','io_module_label_y6110'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13027:{ 'name': 'MR1111',
        'label_point':['label_y6111','io_module_label_y6111'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13028:{ 'name': 'MR1112',
        'label_point':['label_y6112','io_module_label_y6112'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13029:{ 'name': 'MR1113',
        'label_point':['label_y6113','io_module_label_y6113'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13030:{ 'name': 'MR1114',
        'label_point':['label_y6114','main_motor_label_y6114'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13032:{ 'name': 'MR1115',
        'label_point':['label_y6115','main_motor_label_y6115'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13033:{ 'name': 'MR1200',
        'label_point':['label_y6200','main_motor_label_y6200'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13034:{ 'name': 'MR1201',
        'label_point':['label_y6201','main_motor_label_y6201'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13035:{ 'name': 'MR1202',
        'label_point':['label_y6202'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13036:{ 'name': 'MR1203',
        'label_point':['label_y6203'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13037:{ 'name': 'MR1204',
        'label_point':['label_y6204'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13038:{ 'name': 'MR1205',
        'label_point':['label_y6205'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13039:{ 'name': 'MR1206',
        'label_point':['label_y6206'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False},},

13040:{ 'name': 'MR1207',
        'label_point':['label_y6207'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13041:{ 'name': 'MR1208',
        'label_point':['label_y6208'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13042:{ 'name': 'MR1209',
        'label_point':['label_y6209'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13043:{ 'name': 'MR1210',
        'label_point':['label_y6210'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13044:{ 'name': 'MR1211',
        'label_point':['label_y6211'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13045:{ 'name': 'MR1212',
        'label_point':['label_y6212'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13046:{ 'name': 'MR1213',
        'label_point':['label_y6213'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13047:{ 'name': 'MR1214',
        'label_point':['label_y6214'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

13048:{ 'name': 'MR1215',
        'label_point':['label_y6215'],
        'node_property':{'device': 'PLC1', 'data_type': 'Boolean', 'category': 'hmi','rw': 'rw', 'history': False, 'initial_value': False}},

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


}

