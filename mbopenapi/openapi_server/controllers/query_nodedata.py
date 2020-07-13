import logging


def generate_sqls(influx_cfg: dict, node_list: list, measurements: dict, 
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
        logging.error(f"Error : Cannot generate sql strings: {err}")

    return sqls

def query_nodedata(influx_cfg: dict, sqls: list) -> dict:
    """
    Query node data
    """
    return


def fetch()