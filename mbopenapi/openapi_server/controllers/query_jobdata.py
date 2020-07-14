import logging
import multiprocessing
import sys
sys.path.append('../')

from openapi_server.JobAsyncioRequests import JobAsyncioRequests
# from JobAsyncioRequests import JobAsyncioRequests


def query_jobdata(job_ids: list, influx_cfg: dict) -> list:
    """
    Spread query across cores
    """
    job_data = []
    try:
        # Generate sqls
        sqls = generate_sqls(job_ids)

        # Query data
        job_data = query_influx(influx_cfg, sqls)

    except Exception as err:
        logging.error(f"query_jobdata error: {err}")
    return job_data


def query_influx(influx_cfg: dict, sqls: list) -> list:
    """
    Use JobAsyncioRequests to query urls
    """
    data = []
    try:
        request = JobAsyncioRequests(influx_cfg['host'], influx_cfg['port'], influx_cfg['database'])
        data = request.bulk_fetch(sqls)
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