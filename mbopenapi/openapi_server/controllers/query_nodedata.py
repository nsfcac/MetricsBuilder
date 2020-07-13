import logging
import multiprocessing
import sys
sys.path.append('../')

from AsyncioRequests import AsyncioRequests


def query_nodedata(influx_cfg: dict, node_list: list, measurements: dict, 
                  start: str, end: str, interval: str, value: str, cores) -> list:
    """
    Spread query across cores
    """
    node_data = []
    try:
        # Generate sqls
        all_sqls = generate_sqls(node_list, measurements, start, end, interval, value)

        # Partition
        sqls_group = partition(all_sqls, cores)

        query_influx_args = []
        for i in range(cores):
            sqls = sqls_group[i]
            query_influx_args.append((influx_cfg, sqls))

        # Parallel query influxdb
        with multiprocessing.Pool() as pool:
            data = pool.starmap(query_influx, query_influx_args)

        # Flatten the returned data
        node_data = [item for sublist in data for item in sublist]

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


def generate_sqls(node_list: list, measurements: dict, 
                  start: str, end: str, interval: str, value: str) -> list:
    """
    Generate sqls from accroding to the user-specified parameters
    """
    sqls = []
    try:
        for node in node_list:
            for measurement, labels in measurements.items():
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