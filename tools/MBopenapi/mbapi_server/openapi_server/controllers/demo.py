import connexion
import six
import time
import json

from parse_config import parse_conf, parse_host
from gen_timestamp import gen_timestamp, gen_epoch_timestamp
from DBcm import QueryInfluxdb
from query_db import query_data

def get_metrics(start, end, interval, value):  # noqa: E501

    # Initialization 
    config = parse_conf()
    node_list = parse_host()
    influx = QueryInfluxdb(config["influxdb"])

    # Time string used in query_data
    start_str = start
    end_str = end

    print(f"Start time str: {start_str}; End time str: {end_str}")

    # Check Sanity
    if start > end:
        print("Start time should no larger than end time")
    else:

        query_start = time.time()
        # Get time stamp
        # time_list = gen_timestamp(start, end, interval)

        # Query Nodes and Jobs info
        all_data = query_data(node_list, influx, start_str, end_str, interval, value)

        query_elapsed = float("{0:.2f}".format(time.time() - query_start))

        print(query_elapsed)
        print(json.dumps(all_data, indent=4))

        # process_start = time.time()
        # # Process Nodes and Jobs info
        # unified_metrics.JobsInfo = process_job_data(all_data["job_data"])
        # unified_metrics.NodesInfo = process_node_data(node_list, all_data["node_data"], time_list, value)

        # process_elapsed = float("{0:.2f}".format(time.time() - process_start)) 
        # total_elapsed = float("{0:.2f}".format(query_elapsed + process_elapsed))
        # # In seconds
        # time_range = int(end.timestamp()) - int(start.timestamp())

        # with open("requests.log", "a+") as requests_log:
        #     print(f"{time_range}:{interval}:{value}:{query_elapsed}:{process_elapsed}:{total_elapsed}", file = requests_log)

    # return unified_metrics


if __name__ == "__main__":
    start = "2020-02-12T00:00:00Z"
    end = "2020-02-12T00:10:00Z"
    interval = "5m"
    value = "max"
    get_metrics(start, end, interval, value)