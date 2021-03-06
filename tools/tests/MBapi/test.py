from query_db import query_info
from time_stamp import time_stamp
from configure import parse_host
from process_data import process_node_data, process_job_data

from DBcm import QueryInfluxdb


config = {'host': '10.10.1.4',
          'port': 8086,
          'database': 'hpcc_monitoring_db',}

# node_list = ['10.101.5.5']
node_list = parse_host()
start = '2020-02-12T14:00:00Z'
end = '2020-02-12T15:00:00Z'
interval = '10m'
value = 'max'

time_list = time_stamp(start, end, interval)

influx = QueryInfluxdb(config)

# query_result = query_in_parallel(node_list, config, start, end, interval, value)
# node_data = query_node_info(node_list, influx, start, end, interval, value)
# node_data = query_result[0]

all_data = query_info(node_list, influx, start, end, interval, value)

result = process_node_data(node_list, all_data["node_data"], time_list, value)

print(result)