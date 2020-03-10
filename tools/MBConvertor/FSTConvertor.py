#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from DBcm import QueryInfluxdb
from parse_config import parse_host
from query_db import get_phase_time

config = {
    'host': 'localhost',
    'port': '8086',
    'database': 'hpcc_monitoring_db'
}

def main():

    # Initialization
    client = QueryInfluxdb(config)
    phase_time = get_phase_time(client)
    print(phase_time)

    # Get host list
    # hostlist = parse_host()
    

    # Get first timestamp
    return


if __name__ == "__main__":
    main()