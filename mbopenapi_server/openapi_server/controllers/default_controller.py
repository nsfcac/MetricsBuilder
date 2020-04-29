import connexion
import six
import json, base64
import time
import zlib
from influxdb import InfluxDBClient 

import multiprocessing
from itertools import repeat

from openapi_server.models.error_message import ErrorMessage  # noqa: E501
from openapi_server.models.unified_metrics import UnifiedMetrics  # noqa: E501
from openapi_server import util

from openapi_server.controllers.parse_config import parse_conf, parse_host
from openapi_server.controllers.gen_timestamp import gen_timestamp, gen_epoch_timestamp
from openapi_server.controllers.DBcm import QueryInfluxdb
from openapi_server.controllers.query_db import query_process_data, query_job_data

ZIPJSON_KEY = 'base64(zip(o))'

def get_unified_metric(start, end, interval, value, compress):  # noqa: E501
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
    node_list = parse_host()
    influx = QueryInfluxdb(config["influxdb"])
    cpu_count = multiprocessing.cpu_count()

    node_data = {}
    job_data = {}
    all_jobs_list = []

    start = util.deserialize_datetime(start)
    end = util.deserialize_datetime(end)

    # Time string used in query_data
    st_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
    et_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')

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
        epoch_time_list = gen_epoch_timestamp(start, end, interval)

        # unified_metrics.time_stamp = epoch_time_list
        if compress:
            unified_metrics.time_stamp = json_zip(epoch_time_list)
        else:
            unified_metrics.time_stamp = epoch_time_list
        
        # Get all nodes detail
        query_process_data_args = zip(node_list, repeat(influx), 
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

        if compress:
            unified_metrics.nodes_info = json_zip(node_data)
        else:
            unified_metrics.nodes_info = node_data
        

        # Get all jobs ID
        all_jobs_id = list(set(all_jobs_list))

        query_job_data_args = zip(repeat(influx), all_jobs_id)

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
    
        if compress:
            unified_metrics.jobs_info = json_zip(job_data)
        else:
            unified_metrics.jobs_info = job_data

        total_elapsed = float("{0:.2f}".format(time.time() - query_start)) 
        # In seconds
        time_range = int(end.timestamp()) - int(start.timestamp())

        with open("requests.log", "a+") as requests_log:
            print(f"{time_range}|{interval}|{value}|{total_elapsed}", file = requests_log)

    return unified_metrics

def json_zip(j):

    j = {
        ZIPJSON_KEY: base64.b64encode(
            zlib.compress(
                json.dumps(j).encode('utf-8')
            )
        ).decode('ascii')
    }

    return j