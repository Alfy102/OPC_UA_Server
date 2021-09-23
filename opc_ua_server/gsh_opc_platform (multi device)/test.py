from io_layout_map import node_structure
import time


tic = time.perf_counter()
#test_string = dict((key, item) for key,item in node_structure.items())


category_list = {key:value for key,value in node_structure.items() if value['node_property']['category']=='hmi'}
toc = time.perf_counter()
print(f'{toc - tic:.10f}')
print(bool(1))
