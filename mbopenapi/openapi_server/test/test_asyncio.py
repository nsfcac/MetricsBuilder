import json
import sys
sys.path.append('../')

from influxdb import InfluxDBClient
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

measurements = {
  "measurements": {
    "Power": [
      "NodePower"
    ],
    "FanSensor": [
      "FAN_1",
      "FAN_2",
      "FAN_3",
      "FAN_4"
    ],
    "TempSensor": [
      "CPU1 Temp",
      "CPU2 Temp",
      "Inlet Temp"
    ],
    "CPUUsage": [
      "UGE"
    ],
    "MemUsage": [
      "UGE"
    ]
  }
}

# SELECT max(Value) from TempSensor where NodeId ='10.101.1.1' and time >= 1594537200000000000 and time < 1594544400000000000 group by time(5m) fill(null)

nodes = parse_nodelist(nodelist_cfg)
sqls = []

# meas = list(measurements.keys())
host = 'localhost'
port = '8086'
db = 'hpcc_metrics_phase2'

# mea = "FanSensor"
for node in nodes:
    for mea, labels in measurements.items():
        for label in labels:
            sql = "SELECT max(Value) FROM " + mea + " WHERE Label='" + label + "' and NodeId='" + node + "' AND time >= 1594537200000000000 AND time < 1594544400000000000 GROUP BY time(5m) fill(null)" 
            sqls.append(sql)


print(json.dumps(sqls, indent=4))

# # Sequencial
# client = InfluxDBClient(host=host, port=port, database=db)


# resp = []
# for sql in sqls:
#     result = list(client.query(sql).get_points())
#     resp.append(result)

# # Asyncio
# request = AsyncioRequests(host, port, db, mea)
# resp = request.bulk_fetch(sqls, nodes)


# print(json.dumps(resp, indent=4))


# for mea in meas:
#     sqls = []
#     for node in nodes:
#         sql = "SELECT max(Value) FROM " + mea + " WHERE NodeId='" + node + "' AND time >= 1594537200000000000 AND time < 1594544400000000000 GROUP BY time(5m) fill(null)" 
#         sqls.append(sql)

#     request = AsyncioRequests(host, port, db, mea)
#     resp = request.bulk_fetch(sqls, nodes)

# print(json.dumps(resp, indent=4))