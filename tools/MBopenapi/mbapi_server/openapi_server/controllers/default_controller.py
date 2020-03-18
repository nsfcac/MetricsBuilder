import connexion
import six
import time
import json

from openapi_server.models.error_message import ErrorMessage  # noqa: E501
from openapi_server.models.unified_metrics import UnifiedMetrics  # noqa: E501
from openapi_server import util

from openapi_server.controllers.parse_config import parse_conf, parse_host
from openapi_server.controllers.gen_timestamp import gen_timestamp, gen_epoch_timestamp
from openapi_server.controllers.DBcm import QueryInfluxdb
from openapi_server.controllers.query_db import query_data
from openapi_server.controllers.process_data import process_node_data

def get_metrics(start, end, interval, value):  # noqa: E501
    """get_metrics

    Get **unified metrics** based on speficied start time, end time, time interval and value type. The **start** and **end** time should follow date-time Notation as defined by [RFC 3339, section 5.6](https://tools.ietf.org/html/rfc3339#section-5.6), e.g. &#x60;2020-02-12T14:00:00Z&#x60;; the time **interval** should follow **duration literals**, which specify a length of time; the **value** type should only be &#x60;min&#x60;, &#x60;max&#x60;, &#x60;mean&#x60;, or &#x60;median&#x60;. A duration literal is an integer literal followed immediately (with no spaces) by a duration unit, the units include &#x60;s&#x60;(second), &#x60;m&#x60;(minute), &#x60;h&#x60;(hour), &#x60;d&#x60;(day), &#x60;w&#x60;(week). # noqa: E501

    :param start: start time of time range of the monitoring metrics
    :type start: str
    :param end: end time of time range of the monitoring metrics
    :type end: str
    :param interval: time interval for aggregating the monitoring metrics
    :type interval: str
    :param value: value type of the monitoring metrics
    :type value: str

    :rtype: UnifiedMetrics
    """
    # Initialization 
    config = parse_conf()
    node_list = parse_host()
    influx = QueryInfluxdb(config["influxdb"])

    # Time string used in query_data
    start_str = start
    end_str = end

    print(f"Start time str: {start_str}; End time str: {end_str}")

    start = util.deserialize_datetime(start)
    end = util.deserialize_datetime(end)

    # print(f"Start time: {start}; End time: {end}")

    # Check Sanity
    if start > end:
        return ErrorMessage(
            error_code = '400 INVALID_PARAMETERS',
            error_message = 'Start time should no larger than end time'
        )
    else:
        unified_metrics = UnifiedMetrics()

        query_start = time.time()
        # Get time stamp
        time_list = gen_timestamp(start, end, interval)
        # Epoch time in seconds
        epoch_time_list = gen_epoch_timestamp(start, end, interval)
        unified_metrics.TimeStamp = epoch_time_list

        # print(epoch_time_list)

        # Query Nodes and Jobs info
        all_data = query_data(node_list, influx, start_str, end_str, interval, value)

        query_elapsed = float("{0:.2f}".format(time.time() - query_start))

        print(query_elapsed)
        print(json.dumps(all_data, indent=4))

        process_start = time.time()
        # Process Nodes and Jobs info
        unified_metrics.JobsInfo = all_data["job_data"]
        unified_metrics.NodesInfo = process_node_data(node_list, all_data["node_data"], time_list, value)

        process_elapsed = float("{0:.2f}".format(time.time() - process_start)) 
        total_elapsed = float("{0:.2f}".format(query_elapsed + process_elapsed))
        # In seconds
        time_range = int(end.timestamp()) - int(start.timestamp())

        with open("requests.log", "a+") as requests_log:
            print(f"{time_range}:{interval}:{value}:{query_elapsed}:{process_elapsed}:{total_elapsed}", file = requests_log)

    return unified_metrics