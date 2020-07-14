import logging
import multiprocessing
from itertools import repeat
import asyncio

from openapi_server.NodeAsyncioRequests import NodeAsyncioRequests
from openapi_server.controllers.process_nodedata import process_nodedata
# import sys
# sys.path.append('../')
# from NodeAsyncioRequests import NodeAsyncioRequests
# from controllers.process_nodedata import process_nodedata


def query_nodedata(node_list: str, influx_cfg: dict, measurements: dict, 
                   start: str, end: str, interval: str, value: str, time_list: list) -> list:
    """
    Spread query across cores
    """
    node_data = []
    try:
        cores= multiprocessing.cpu_count()

        node_group = partition(node_list, cores)

        with multiprocessing.Pool() as pool:
            # Generate sqls
            generate_sqls_args = zip(node_group, repeat(measurements), repeat(start),
                                 repeat(end), repeat(interval), repeat(value))
            sqls_group = pool.starmap(generate_sqls, generate_sqls_args)

            # Parallel query data
            query_influx_args = zip(repeat(influx_cfg), sqls_group)
            node_data = pool.starmap(query_influx, query_influx_args)

            # # Process data
            # process_nodedata_args = zip(node_data, repeat(time_list))
            # processd_nodedata = pool.starmap(process_nodedata, process_nodedata_args)

    except Exception as err:
        logging.error(f"query_nodedata error: {err}")
    return node_data


def query_influx(influx_cfg: dict, sqls: list) -> list:
    """
    Use NodeAsyncioRequests to query urls
    """
    data = []
    try:
        request = NodeAsyncioRequests(influx_cfg['host'], influx_cfg['port'], 
                                      influx_cfg['database'])
        data = request.bulk_fetch(sqls)

    except Exception as err:
        logging.error(f"query_nodedata : query_influx : {err}")
    return data


def generate_sqls(node_list:list, measurements: dict, 
                  start: str, end: str, interval: str, value: str) -> list:
    """
    Generate sqls from accroding to the user-specified parameters
    """
    sqls = []
    try:
        for node in node_list:
            for measurement, labels in measurements.items():
                if measurement == "NodeJobs":
                    for label in labels:
                        sql = "SELECT DISTINCT(Value) FROM " + measurement \
                            + " WHERE Label='" + label + "' AND NodeId='" + node \
                            + "' AND time >= '" + start + "' AND time < '" + end \
                            + "' GROUP BY *, time(" + interval + ") SLIMIT 1"
                        sqls.append(sql)
                else:
                    for label in labels:
                        sql = "SELECT " + value + "(Value) FROM " + measurement \
                            + " WHERE Label='" + label + "' AND NodeId='" + node \
                            + "' AND time >= '" + start + "' AND time < '" + end \
                            + "' GROUP BY time(" + interval + ") fill(null)"
                        sqls.append(sql)
    except Exception as err:
        logging.error(f"query_nodedata : generate_sqls: cannot generate sql strings: {err}")

    return sqls


def partition(arr:list, cores: int) -> list:
    """
    Partition urls/nodes into several groups based on # of cores
    """
    groups = []
    try:
        arr_len = len(arr)
        arr_per_core = arr_len // cores
        arr_surplus = arr_len % cores

        increment = 1
        for i in range(cores):
            if(arr_surplus != 0 and i == (cores-1)):
                groups.append(arr[i * arr_per_core:])
            else:
                groups.append(arr[i * arr_per_core : increment * arr_per_core])
                increment += 1
    except Exception as err:
        logging.error(f"query_nodedata : partition : {err}")
    return groups