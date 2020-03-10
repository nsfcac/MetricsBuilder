#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from influxdb import InfluxDBClient

from parse_config import parse_host
from query_db import get_fst_time

config = {
    'host': 'localhost',
    'port': '8086',
    'database': 'hpcc_monitoring_db'
}

def main():

    # Initialization
    client = InfluxDBClient(**config)
    result = client.query("SELECT first('CPU1 Temp') FROM 'CPU_Temperature' WHERE host='10.101.1.1'")
    print(result)

    # Get host list
    # hostlist = parse_host()
    

    # Get first timestamp
    return


if __name__ == "__main__":
    main()