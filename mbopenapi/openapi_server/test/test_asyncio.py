import json
import sys
sys.path.append('../')

from AsyncioRequests import AsyncioRequests
from mb_utils import parse_nodelist

nodelist_cfg = [
    "10.101.1/1-60",
    "10.101.2/1-60",
    "10.101.3/1-56",
    "10.101.4/1-48",
    "10.101.5/1-24",
    "10.101.6/1-20",
    "10.101.7/1-3,5-60",
    "10.101.8/1-60",
    "10.101.9/1-60",
    "10.101.10/25-44"
]

# SELECT max(Value) from TempSensor where NodeId ='10.101.1.1' and time >= 1594537200000000000 and time < 1594544400000000000 group by time(5m) fill(null)

nodes = parse_nodelist(nodelist_cfg)
sqls = []

meas = 'TempSensor'
host = 'localhost'
port = '8086'
db = 'hpcc_metrics_phase2'

for node in nodes:
    sql = "SELECT max(Value) FROM " + meas + " WHERE NodeId='" + node + "' AND time >= 1594537200000000000 AND time < 1594544400000000000 GROUP BY time(5m) fill(null)" 
    sqls.append(sql)

request = AsyncioRequests(host, port, db, meas)

resp = request.bulk_fetch(sqls, nodes)
print(json.dumps(resp, indent=4))