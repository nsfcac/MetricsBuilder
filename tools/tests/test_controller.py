import connexion
import six
import json
import time
from influxdb import InfluxDBClient
import logging

import multiprocessing
from itertools import repeat
from dateutil.parser import parse

from parse_config import parse_conf, parse_host
from gen_timestamp import gen_timestamp, gen_epoch_timestamp
# from DBcm import QueryInfluxdb
from query_db import query_process_data, query_job_data

logging.basicConfig(
    level=logging.ERROR,
    filename='test_metricsbuilder.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z'
)


def get_unified_metric(start, end, interval, value):  # noqa: E501
    """get_unified_metric

    Get **unified metrics** based on speficied start time, end time, time interval and value type. The **start** and **end** time should follow date-time Notation as defined by [RFC 3339, section 5.6](https://tools.ietf.org/html/rfc3339#section-5.6), e.g. &#x60;2020-02-12T14:00:00Z&#x60;; the time **interval** should follow **duration literals**, which specify a length of time; the **value** type should only be &#x60;min&#x60;, &#x60;max&#x60;, &#x60;mean&#x60;, or &#x60;median&#x60;.  A duration literal is an integer literal followed immediately (with no spaces) by a duration unit, the units include &#x60;s&#x60;(second), &#x60;m&#x60;(minute), &#x60;h&#x60;(hour), &#x60;d&#x60;(day), &#x60;w&#x60;(week).  # noqa: E501

    :param start: start time of time range of the monitoring metrics
    :type start: str
    :param end: end time of time range of the monitoring metrics
    :type end: str
    :param interval: time interval for aggregating the monitoring metrics
    :type interval: str
    :param value: value type of the monitoring metrics
    :type value: str
    :param compress: return compressed data
    :type compress: bool

    :rtype: UnifiedMetrics
    """
     # Initialization 
    config = parse_conf()
    # node_list = parse_host()
    node_list = ["10.101.1.1"]
    host = config["influxdb"]["host"]
    port = config["influxdb"]["port"]

    start = parse(start)
    end = parse(end)

    # When we changed the database, April 28, 2020 11:40:00 AM GMT-05:00 DST
    switch_time = 1588092000
    start_epoch = int(start.timestamp())
    end_epoch = int(end.timestamp())

    if start_epoch >= switch_time:
        dbname = config["influxdb"]["db_monster"]
    elif end_epoch <= switch_time:
        dbname = config["influxdb"]["database"]
    else:
        print("""
        Due to we switched database on April 28, 2020 11:40:00 AM GMT-05:00 DST, 
        currently we do not support requesting data with time range falls on this time point
        """)
        return

    client = InfluxDBClient(host=host, port=port, database=dbname)

    cpu_count = multiprocessing.cpu_count()

    unified_metrics = {}
    node_data = {}
    job_data = {}
    all_jobs_list = []
    

    # Time string used in query_data
    st_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
    et_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')

    # query_start = time.time()

    # Get time stamp
    time_list = gen_timestamp(start, end, interval)

    # print("time_list: ", end = " ")
    # print(len(time_list))
    # print(json.dumps(time_list, indent=4))
    epoch_time_list = gen_epoch_timestamp(start, end, interval)

    
    # Query nodes data

    # Get all nodes detail
    query_process_data_args = zip(node_list, repeat(client), 
                            repeat(st_str), repeat(et_str), 
                            repeat(interval), repeat(value), repeat(time_list))

    with multiprocessing.Pool(processes=cpu_count) as pool:
        results = pool.starmap(query_process_data, query_process_data_args)

    # Attach data to node ip addr
    for index, node in enumerate(node_list):
        node_data[node] = {
            "memory_usage": results[index]["memory_usage"],
            "cpu_usage": results[index]["cpu_usage"],
            "power_usage": results[index]["power_usage"],
            "fan_speed": results[index]["fan_speed"],
            "cpu_inl_temp": results[index]["cpu_inl_temp"],
            "job_id": results[index]["job_list"]
        }
        try:
            all_jobs_list.extend(results[index]["job_set"])
        except Exception as err:
            print(err)

    print(json.dumps(node_data, indent=4))
    # Get all jobs ID
    all_jobs_id = list(set(all_jobs_list))

    query_job_data_args = zip(repeat(client), all_jobs_id)

    # Get all jobs detail
    with multiprocessing.Pool(processes=cpu_count) as pool:
        results = pool.starmap(query_job_data, query_job_data_args)

    for index, job in enumerate(all_jobs_id):
        if results[index]:
            job_array = False
            if "." in results[index]["JobId"]:
                job_array = True
            
            if "FinishTime" in results[index]:
                finish_time = results[index]["FinishTime"]
            else:
                finish_time = None

            if "NodeList" in results[index]:
                node_list = results[index]["NodeList"]
            else:
                node_list = None

            job_data[job] = {
                "start_time": results[index]["StartTime"],
                "submit_time": results[index]["SubmitTime"],
                "finish_time": finish_time,
                "job_name": results[index]["JobName"],
                "user_name": results[index]["User"],
                "node_list": node_list,
                "total_nodes": results[index]["TotalNodes"],
                "cpu_cores": results[index]["CPUCores"],
                "job_array": job_array
            }
        else:
            print("No Result")

    print(json.dumps(job_data, indent=4))

    # total_elapsed = float("{0:.2f}".format(time.time() - query_start)) 
    # # In seconds
    # time_range = int(end.timestamp()) - int(start.timestamp())

    unified_metrics = {
        "node_data": node_data,
        "job_data": job_data,
        "time_list": epoch_time_list
    }

    # print(json.dumps(unified_metrics, indent=4))
    return

start = "2020-04-29T00:00:00Z-05:00"
end = "2020-04-29T12:00:00Z-05:00"
interval = "1h"
value = "max"

get_unified_metric(start, end, interval, value)