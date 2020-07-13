import logging
import multiprocessing
import sys
sys.path.append('../')

from itertools import repeat

from AsyncioRequests import AsyncioRequests


def query_nodedata(influx_cfg: dict, node_list: list, measurements: dict, 
                  start: str, end: str, interval: str, value: str) -> list:
    """
    Spread query across cores
    """
    node_data = []
    try:
        # Generate sqls
        sqls = generate_sqls(node_list, measurements, start, end, interval, value)

        # Parallel query influxdb
        query_influx_args = zip(repeat(influx_cfg), sqls)
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
        logging.error(f"query_nodedata : fetch_influx error : {err}")
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
        logging.error(f"Cannot generate sql strings: {err}")

    return sqls