import logging
import multiprocessing
import asyncio
import sys
sys.path.append('../')

# from openapi_server.NodeAsyncioRequests import NodeAsyncioRequests
from NodeAsyncioRequests import NodeAsyncioRequests


def query_nodedata(node: str, influx_cfg: dict, measurements: dict, 
                   start: str, end: str, interval: str, value: str, ) -> list:
    """
    Spread query across cores
    """
    node_data = []
    try:
        # Generate sqls
        sqls = generate_sqls(node, measurements, start, end, interval, value)

        # Query data
        loop  = asyncio.get_event_loop()
        node_data = query_influx(influx_cfg, sqls, loop)

    except Exception as err:
        logging.error(f"query_nodedata error: {err}")
    return node_data


def query_influx(influx_cfg: dict, sqls: list, loop) -> list:
    """
    Use NodeAsyncioRequests to query urls
    """
    data = []
    try:
        request = NodeAsyncioRequests(influx_cfg['host'], influx_cfg['port'], influx_cfg['database'], loop)
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