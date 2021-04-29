# -*- coding: utf-8 -*-
"""
This module is the MetricsBuilder core, it interacts with TimeScaleDB and 
provide data points to data analytics

Jie Li (jie.li@ttu.edu)
"""
import sys
import json
import aiopg
import asyncio
import hostlist
import psycopg2

sys.path.append('./')
from utils import parse_config, init_tsdb_dsn, init_tsdb_connection, gene_host_id_mapping

def main():
    # Read configuratin file
    config = parse_config('./config.yml')
    # Create TimeScaleDB connection
    connection = init_tsdb_connection(config['timescaledb'])
    dsn = init_tsdb_dsn(config['timescaledb'])

    host_id_map = {}
    with psycopg2.connect(connection) as conn:
        # Get hostname-id mapping
        host_id_map = gene_host_id_mapping(conn)

    job_id = 680540
    metrics = {
        'idrac9': ['systempowerconsumption', 'totalcpupower', 'totalmemorypower', 'cpuusage', 'rpmreading'],
        'slurm':['node_jobs', 'memoryusage']
    }
    start = '2021-03-25 15:00:00-05'
    end = '2021-03-25 20:00:00-05'
    interval = '5 min'
    aggregate = 'max'

    metrics_sqls = gene_metrics_sqls(metrics, host_id_map, 
                             start, end, interval, aggregate)
    
    # print(json.dumps(node_sqls, indent=4))

    loop = asyncio.get_event_loop()
    metrics = loop.run_until_complete(async_query_tsdb(metrics_sqls, dsn))

    with open('./data/mb_optimize.json', 'w') as jsonfile:
        json.dump(metrics, jsonfile, indent=4, default=str)

    # # Aggregate node_jobs
    # for i, each_record in enumerate(node_metrics):
    #     if 'node_jobs' in each_record:
    #         agg_node_jobs = aggregate_node_jobs(each_record['node_jobs'])
    #         node_metrics[i]['node_jobs'] = agg_node_jobs

    # dataset = gene_dataset(node_metrics)
    # print(json.dumps(dataset, indent=4, default=str))


def gene_idrac9_sql(metric: str, start: str, end: str, 
                    interval: str, aggregate: str) -> dict:
    """
    Generate SQL for querying iDRAC9 metrics
    interval should be like '5 minutes' or '5 min'
    start and end should be in this format "2021-03-21 17:00:00-05"
    SELECT time_bucket_gapfill('5 minutes', timestamp) as time, nodeid , fqdd as label, max(value) from idrac9.cpuusage WHERE timestamp >= '2021-04-28 17:00:00-05' AND timestamp < '2021-04-28 18:00:00-05' GROUP BY time, nodeid, label ORDER BY time;
    """
    sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) as time, nodeid, fqdd as label, {aggregate}(value) from idrac9.{metric} WHERE timestamp >= '{start}' AND timestamp < '{end}' GROUP BY time, nodeid, label ORDER BY time;"
    return sql


def gene_slurm_sql(metric: str, start: str, end: str, 
                   interval: str, aggregate: str) -> dict:
    """
    Generate SQL for querying slurm metrics
    SELECT time_bucket_gapfill('5 minutes', timestamp) as time, nodeid, array_agg(jobs) as jobs, array_agg(cpus) as cpus from slurm.node_jobs WHERE timestamp >= '2021-04-28 17:00:00-05' AND timestamp < '2021-04-28 18:00:00-05' GROUP BY time, nodeid, jobs, cpus ORDER BY time;
    SELECT time_bucket_gapfill('5 minutes', timestamp) as time, nodeid, max(value) from slurm.memoryusage WHERE timestamp >= '2021-04-28 17:00:00-05' AND timestamp < '2021-04-28 18:00:00-05' GROUP BY time, nodeid ORDER BY time;
    """
    sql = ""
    if metric == 'node_jobs':
        sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) as time, nodeid, array_agg(jobs) as jobs, array_agg(cpus) as cpus from slurm.{metric} WHERE timestamp >= '{start}' AND timestamp < '{end}' GROUP BY time, nodeid, jobs, cpus ORDER BY time;"
    else:
        metric = 'memoryusage'
        sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) as time, nodeid, {aggregate}(value) from slurm.{metric} WHERE timestamp >= '{start}' AND timestamp < '{end}' GROUP BY time, nodeid ORDER BY time;"
    return sql


def gene_metrics_sqls(metrics: dict, host_id_map: dict, 
              start: str, end: str, interval: str, aggregate: str) -> list:
    """
    Generate node-sqls
    """
    metrics_sqls = {}
    sqls = {}
    idrac9_sqls = []
    slurm_sqls = []
    
    for metric in metrics['idrac9']:
        sql = gene_idrac9_sql(metric, start, end, interval, aggregate)
        idrac9_sqls.append(sql)

    for metric in metrics['slurm']:
        sql = gene_slurm_sql(metric, start, end, interval, aggregate)
        slurm_sqls.append(sql)

    sqls = {'idrac9': idrac9_sqls, 'slurm': slurm_sqls}

    metrics_sqls.update({
        'metrics': metrics,
        'sqls': sqls
    })
    return metrics_sqls


async def async_query_tsdb(metrics_sqls: dict, dsn: str) -> list:
    """
    sqls = {'idrac9': idrac9_sqls, 'slurm': slurm_sqls}
    """
    tasks = []
    async with aiopg.create_pool(dsn) as pool:

        idrac9_metrics = metrics_sqls['metrics']['idrac9']
        idrac9_sqls = metrics_sqls['sqls']['idrac9']
        for i, sql in enumerate(idrac9_sqls):
            tasks.append(async_execute(idrac9_metrics[i], sql, pool))

        slurm_metrics = metrics_sqls['metrics']['slurm']
        slurm_sqls = metrics_sqls['sqls']['slurm']
        for i, sql in enumerate(slurm_sqls):
            tasks.append(async_execute(slurm_metrics[i], sql, pool))
        return await asyncio.gather(*tasks) 


async def async_execute(metric: str, sql: str, pool: object) -> dict:
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql)
                resp = await cur.fetchall()
                return {metric: resp}
    except Exception as err:
        print(f"{metric} : {err}")


def aggregate_node_jobs(node_jobs: list) -> list:
    agg_node_jobs = []
    for record in node_jobs:
        timestamp = record[0]
        jobs_list = record[1]
        cpus_list = record[2]

        if jobs_list:
            jobs_cpus = {}
            for i, jobs in enumerate(jobs_list):
                for j, job in enumerate(jobs):
                    job_id_str = str(job)
                    if job_id_str not in jobs_cpus:
                        jobs_cpus.update({
                            job_id_str: cpus_list[i][j]
                        })
            agg_jobs_list = [int(job) for job in list(jobs_cpus.keys())]
            agg_cpus_list = list(jobs_cpus.values())
        else:
            agg_jobs_list = []
            agg_cpus_list = []
        agg_node_jobs.append([timestamp, agg_jobs_list, agg_cpus_list])

    return agg_node_jobs


def gene_dataset(node_metrics: list) -> dict:
    """
    This is only for generating previous MetricsBuilder-like dataset.
    """
    nodes_info = {}
    time_stamp_dt = [i[0] for i in node_metrics[0]['systempowerconsumption']]
    time_stamp = [int(ts.timestamp()) for ts in time_stamp_dt]
    # all_keys = list(node_metrics[0].keys())
    # all_metrics = all_keys.pop(0)

    for record in node_metrics:
        node = record['node']
        all_keys = list(record.keys())
        metric = all_keys[1]

        if metric == 'node_jobs' or metric == 'memoryusage':
            values = [i[1] for i in record[metric]]
        else:
            values = [i[2] for i in record[metric]]

        if node not in nodes_info:
            nodes_info.update({
                node:{
                    metric: values
                }
            })
        else:
            nodes_info[node].update({
                metric:values
            })

    return {'nodes_info': nodes_info, 'time_stamp': time_stamp}


if __name__ == '__main__':
    main()

