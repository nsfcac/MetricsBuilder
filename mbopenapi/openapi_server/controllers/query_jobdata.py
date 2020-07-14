import logging
import multiprocessing
from itertools import repeat
import asyncio
import sys
sys.path.append('../')

# from openapi_server.JobAsyncioRequests import JobAsyncioRequests
from JobAsyncioRequests import JobAsyncioRequests
from controllers.process_jobdata import process_jobdata


def query_jobdata(processd_nodedata: list, influx_cfg: dict) -> list:
    """
    Spread query across cores
    """
    processed_jobdata = []
    flatten_jobset = set()
    try:
        cores= multiprocessing.cpu_count()

        with multiprocessing.Pool() as pool:
            all_jobset = pool.map(generate_jobset, processd_nodedata)

        # Get job ids
        for jobset in all_jobset:
            flatten_jobset.update(jobset)

        # job_group = partition(flatten_jobset, cores)

        # with multiprocessing.Pool() as pool:
        #     # Generate sqls
        #     sqls_group = pool.map(generate_sqls, job_group)

        #     # Parallel query  job data
        #     query_influx_args = zip(repeat(influx_cfg), sqls_group)
        #     job_data = pool.starmap(query_influx, query_influx_args)

        #     processed_jobdata = pool.map(process_jobdata, job_data)
            

        

    except Exception as err:
        logging.error(f"query_jobdata error: {err}")
    return list(flatten_jobset)


def query_influx(influx_cfg: dict, sqls: list) -> list:
    """
    Use JobAsyncioRequests to query urls
    """
    data = []
    try:
        loop = asyncio.get_event_loop()

        request = JobAsyncioRequests(influx_cfg['host'], influx_cfg['port'], 
                                     influx_cfg['database'], loop)
        data = request.bulk_fetch(sqls)

        loop.close()
    except Exception as err:
        logging.error(f"query_jobdata : query_influx : {err}")
    return data


def generate_sqls(job_ids: list) -> list:
    """
    Generate sqls from accroding to the job_ids
    """
    sqls = []
    try:
        for job_id in job_ids:
            sql = "SELECT * FROM JobsInfo WHERE JobId='" + job_id + "'"
            sqls.append(sql)
    except Exception as err:
        logging.error(f"query_jobdata : generate_sqls: cannot generate sql strings: {err}")

    return sqls


def partition(arr:list, cores: int) -> list:
    """
    Partition urls/nodes into several groups based on # of cores
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
        logging.error(f"query_jobdata : partition : {err}")
    return groups


def generate_jobset(processed_nodedata: list) -> set:
    """
    Generate job set from 'job_id'
    """
    flatten_jobset = set()
    try:
        for nodedata in processed_nodedata:
            for node, values in nodedata.items():
                job_id = values['job_id']
                flatten = set([item for sublist in job_id for item in sublist])
            flatten_jobset.update(flatten)
    except Exception as err:
        logging.error(f"generate_jobset : {err}")
    return flatten_jobset