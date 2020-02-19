from query_db import query_node_info

config = {'host': 'localhost',
          'port': 8086,
          'database': 'hpcc_monitoring_db',}

node_list = ['10.101.5.5']
start = '2020-02-12T14:00:00Z'
end = '2020-02-12T15:00:00Z'
interval = '10m'
value = 'max'

result = query_node_info(node_list, config, start, end, interval, value)

print(result)