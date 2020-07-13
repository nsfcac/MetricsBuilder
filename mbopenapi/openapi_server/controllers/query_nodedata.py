import logging
import multiprocessing
import sys
sys.path.append('../')

from AsyncioRequests import AsyncioRequests


def query_nodedata(node: str, influx_cfg: dict, measurements: dict, 
                   start: str, end: str, interval: str, value: str) -> list:
    """
    Spread query across cores
    """
    node_data = []
    try:
        # Generate sqls
        sqls = generate_sqls(node, measurements, start, end, interval, value)

        # Query data
        node_data = query_influx(influx_cfg, sqls)

    except Exception as err:
        logging.error(f"query_nodedata error: {err}")
    return node_data


def query_influx(influx_cfg: dict, sqls: list) -> list:
    """
    Use AsyncioRequests to query urls
    """
    data = []
    try:
        request = AsyncioRequests(influx_cfg['host'], influx_cfg['port'], influx_cfg['database'])
        data = request.bulk_fetch(sqls)
    except Exception as err:
        logging.error(f"query_nodedata : query_influx : {err}")
    return data


def generate_sqls(node:str, measurements: dict, 
                  start: str, end: str, interval: str, value: str) -> list:
    """
    Generate sqls from accroding to the user-specified parameters
    """
    sqls = []
    try:
        for measurement, labels in measurements.items():
            if measurement == "NodeJobs":
                for label in labels:
                    sql = "SELECT DISTINCT(Value) FROM " + measurement + \
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
    Partition sqls into several groups based on # of cores
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
        logging.error(f"query_nodedata : partition error : {err}")
    return groups