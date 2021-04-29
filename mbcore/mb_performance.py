# -*- coding: utf-8 -*-
"""
This module is to test the MetricsBuilder performance 

Jie Li (jie.li@ttu.edu)
"""
import sys
import json
import time
import aiopg
import asyncio
import hostlist
import psycopg2

sys.path.append('./')

from utils import parse_config, init_tsdb_dsn, init_tsdb_connection, gene_host_id_mapping
from mb_optimize import gene_idrac9_sql, gene_metrics_sqls, async_query_tsdb, async_execute


def main():
    # Read configuratin file
    config = parse_config('./config.yml')
    # Create TimeScaleDB connection
    connection = init_tsdb_connection(config['timescaledb'])
    dsn = init_tsdb_dsn(config['timescaledb'])

    host_id_map = {}
    with psycopg2.connect(connection) as conn:
        # Get hostname-id mapping
        host_id_map = gene_host_id_mapping(conn)
    
    metrics = {
        'idrac9': ['cpuusage'],
        # 'totalcpupower', 'totalmemorypower', 'cpuusage', 'systempowerconsumption', 'temperaturereading', 'rpmreading'
        'slurm':[],
        # 'slurm':['node_jobs', 'memoryusage']
    }

    # systempowerconsumption: 1
    # rpmreading: 8
    # temperaturereading: 21
    # NIC.Embedded.1-1-1, NIC.Integrated.1-1-1, 
    # iDRAC.Embedded.1#InletTemp, 
    # iDRAC.Embedded.1#CPU1Temp, 
    # iDRAC.Embedded.1#CPU2Temp, 
    # DIMM.Socket.A1, DIMM.Socket.A2, DIMM.Socket.A3, DIMM.Socket.A4, 
    # DIMM.Socket.A5, DIMM.Socket.A6, DIMM.Socket.A7, DIMM.Socket.A8
    # DIMM.Socket.B1, DIMM.Socket.B2, DIMM.Socket.B3, DIMM.Socket.B4
    # DIMM.Socket.B5, DIMM.Socket.B6, DIMM.Socket.B7, DIMM.Socket.B8

    start = '2021-03-22 00:00:00-05'
    end = ['2021-03-22 06:00:00-05', '2021-03-22 12:00:00-05', 
           '2021-03-22 18:00:00-05', '2021-03-23 00:00:00-05',
           '2021-03-23 06:00:00-05', '2021-03-23 12:00:00-05',
           '2021-03-23 18:00:00-05', '2021-03-22 00:05:00-05']

    interval = '5 min'
    aggregate = 'max'

    # nodelist_1 = 'cpu-23-[1-60]'
    # nodelist_2 = 'cpu-23-[1-60],cpu-24-[1-60]'
    # nodelist_3 = 'cpu-23-[1-60],cpu-24-[1-60],cpu-25-[1-60]'
    # nodelist_4 = 'cpu-23-[1-60],cpu-24-[1-60],cpu-25-[1-60],cpu-26-[1-60]'

    # nodes_1 = hostlist.expand_hostlist(nodelist_1)
    # nodes_2 = hostlist.expand_hostlist(nodelist_2)
    # nodes_3 = hostlist.expand_hostlist(nodelist_3)
    # nodes_4 = hostlist.expand_hostlist(nodelist_4)

    # nodelist = [nodes_1, nodes_2, nodes_3, nodes_4]

    # total_elasped = {
    #     "range_0": [],
    #     "range_1": [],
    #     "range_2": [],
    #     "range_3": [],
    #     "range_4": [],
    #     "range_5": [],
    #     "range_6": []
    # }

    total_elasped = []
    # for i, nodes in enumerate(nodelist):
    for j in range(7):
        metrics_sqls = gene_metrics_sqls(metrics, host_id_map, 
                                      start, end[j], interval, aggregate)

        time_elapsed = test_time(metrics_sqls, dsn)

        total_elasped.append(time_elapsed)
            
            # index = f"range_{j}"
            # total_elasped[index].append(time_elapsed)
    performance = {metrics['idrac9'][0]: total_elasped}

    with open('./data/performance_optimize.json', 'a') as f:
        json.dump(performance, f)
    # print(node_metrics)
    # print(total_elapsed)

def test_time(metrics_sqls, dsn) -> float:
    query_start = time.time()

    loop = asyncio.get_event_loop()
    node_metrics = loop.run_until_complete(async_query_tsdb(metrics_sqls, dsn))

    time_elapsed = float("{0:.2f}".format(time.time() - query_start))

    return time_elapsed

if __name__ == '__main__':
    main()