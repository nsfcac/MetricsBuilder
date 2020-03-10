#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from DBcm import QueryInfluxdb
from parse_config import parse_host
from query_db import get_fst_time

config = {
    'host': '10.10.1.4',
    'port': '8086',
    'database': 'hpcc_monitoring_db'
}

def main(argv):

    # Initialization
    influx = QueryInfluxdb(config)
    data_point = get_fst_time(influx)
    print(data_point)
    
    # Get host list
    # hostlist = parse_host()
    

    # Get first timestamp
    return


if __name__ == "__main__":
    main(sys.argv[1:])