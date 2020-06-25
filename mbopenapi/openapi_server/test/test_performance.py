import sys
sys.path.append('../../')

import connexion
import six
import json
import base64
import time
import zlib
import logging
from influxdb import InfluxDBClient

import multiprocessing
from itertools import repeat

from openapi_server import util

from openapi_server.controllers.gen_timestamp import gen_timestamp
from openapi_server.controllers.gen_timestamp import gen_epoch_timestamp
from openapi_server.controllers.query_db import query_process_data
from openapi_server.controllers.query_db import query_job_data


influxdb = {
    'host': 'localhost',
    'port': '8086',
    'database': 'updated_schema'
}

start = '2020-02-14T12:00-05:00'
end_list = ['2020-02-14T18:00-05:00', '2020-02-15T00:00-05:00', 
       '2020-02-15T06:00-05:00', '2020-02-15T12:00-05:00',
       '2020-02-15T18:00-05:00', '2020-02-16T00:00-05:00',
       '2020-02-16T06:00-05:00']
timerange = ['6h', '12h', '18h', '24h', '30h', '36h', '42h']
interval_list = ['5m', '10m', '30m', '1h', '2h']
value = 'max'
compress = True

ZIPJSON_KEY = 'base64(zip(o))'


def get_metrics(influxdb, start, end, interval, value, compress):
    client = InfluxDBClient(host = influxdb['host'], 
                            port = influxdb['port'], 
                            database = influxdb['database'])
    cpu_count = multiprocessing.cpu_count()

    results = []
    node_data = {}
    job_data = {}
    all_jobs_list = []

    query_start = time.time()

    start = util.deserialize_datetime(start)
    end = util.deserialize_datetime(end)

    node_list = parse_host()

    # Time string used in query_data
    st_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
    et_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')

    unified_metrics = {
        "time_stamp": None,
        "nodes_info": None,
        "jobs_info": None
    }

    # Get time stamp
    time_list = gen_timestamp(start, end, interval)
    epoch_time_list = gen_epoch_timestamp(start, end, interval)

    # unified_metrics.time_stamp = epoch_time_list
    if compress:
        unified_metrics['time_stamp'] = json_zip(epoch_time_list)
    else:
        unified_metrics['time_stamp'] = epoch_time_list

    # Get all nodes detail
    query_process_data_args = zip(
        node_list, repeat(client), repeat(st_str),
        repeat(et_str), repeat(interval),
        repeat(value), repeat(time_list))

    with multiprocessing.Pool(processes=cpu_count) as pool:
        results = pool.starmap(query_process_data, query_process_data_args)

    # Attach data to node ip addr
    for index, node in enumerate(node_list):
        if results[index]:
            node_data[node] = {
                "memory_usage": results[index]["memory_usage"],
                "cpu_usage": results[index]["cpu_usage"],
                "power_usage": results[index]["power_usage"],
                "fan_speed": results[index]["fan_speed"],
                "cpu_inl_temp": results[index]["cpu_inl_temp"],
                "job_id": results[index]["job_list"]
            }
            if results[index]["job_set"]:
                all_jobs_list.extend(results[index]["job_set"])

    if compress:
        unified_metrics['nodes_info'] = json_zip(node_data)
    else:
        unified_metrics['nodes_info'] = node_data

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
                pro_nodelist = process_nodelist(node_list)
            else:
                node_list = None

            job_data[job] = {
                "start_time": results[index]["StartTime"],
                "submit_time": results[index]["SubmitTime"],
                "finish_time": finish_time,
                "job_name": results[index]["JobName"],
                "user_name": results[index]["User"],
                "node_list": pro_nodelist,
                "total_nodes": results[index]["TotalNodes"],
                "cpu_cores": results[index]["CPUCores"],
                "job_array": job_array
            }
    if compress:
        unified_metrics['jobs_info'] = json_zip(job_data)
    else:
        unified_metrics['jobs_info'] = job_data
    
    total_elapsed = float("{0:.2f}".format(time.time() - query_start))
    # In seconds
    # time_range = int(end.timestamp()) - int(start.timestamp())

    return total_elapsed


def json_zip(j):
    j = {
        ZIPJSON_KEY: base64.b64encode(
            zlib.compress(
                json.dumps(j).encode('utf-8')
            )
        ).decode('ascii')
    }
    return j


def process_nodelist(nodelist: str) -> list:
    try:
        nodelist_arr = nodelist[1:-1].split(", ")
        process_nodelist = [node[1:-1].split("-")[0] for node in nodelist_arr]
        return process_nodelist
    except:
        logging.error(f"Failed to process NodeList of node")
        return None


def runtest():
    result = {}
    for interval in interval_list:
        result.update({
            interval: {}
        })
        for index, end in enumerate(end_list): 
            time_range_name = timerange[index]
            value_list = []
            for i in range(0,10):
                total_elapsed = get_metrics(influxdb, start, end, interval, value, compress)
                value_list.append(total_elapsed)
            result[interval].update({
                time_range_name: value_list
            })
    
    with open("performance_prev.json", "a+") as performance_log:
        json.dump(result, performance_log)
    return


def parse_host() -> list:
    """
    Read hostlist file, extract IP addresses, 
    and return an IP addr list of monitored hosts
    """
    hostIp_list = []
    try:
        with open("./hostlist", 'r') as infile:
            data = infile.read()
            list_str = data[1:-1]
            list_arr = list_str.split(', ')
            for item in list_arr:
                hostName = item[1:-1]
                hostIp = hostName.split(":")[0]
                hostIp_list.append(hostIp)
    except Exception as err:
        print(err)
    return hostIp_list


if __name__ == '__main__':
    runtest()