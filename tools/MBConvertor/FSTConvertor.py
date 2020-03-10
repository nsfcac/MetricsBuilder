#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from DBcm import QueryInfluxdb
from parse_config import parse_host
from query_db import get_phase_time

read_config = {
    'host': 'localhost',
    'port': '8086',
    'database': 'hpcc_monitoring_db'
}

write_config = {
    'host': 'localhost',
    'port': '8086',
    'database': 'updated_schema'
}

def main():

    # Initialization
    read_client = QueryInfluxdb(read_config)
    write_client = QueryInfluxdb(write_config)
    
    phase_time = get_phase_time(read_client)
    print(phase_time)

    # Get host list
    # hostlist = parse_host()
    # Get first timestamp
    return


if __name__ == "__main__":
    main()