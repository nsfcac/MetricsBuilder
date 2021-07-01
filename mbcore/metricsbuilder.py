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
import itertools
import pandas as pd

sys.path.append('./')

from sqlalchemy import create_engine 
from utils import parse_config, init_tsdb_connection, gene_host_id_mapping


def main():
    # Read configuratin file
    config = parse_config('./config.yml')

    # Create TimeScaleDB connection
    connection = init_tsdb_connection(config['timescaledb'])

    # SqlAlchemy engine
    engine = create_engine(connection)

    sql = "SELECT time_bucket_gapfill('5 min', timestamp) as time, nodeid, jsonb_agg(jobs) as jobs, jsonb_agg(cpus) as cpus from slurm.node_jobs WHERE timestamp BETWEEN '2021-06-22 06:00:00-05' AND '2021-06-22 07:00:00-05' group by time, nodeid order by time;"


    node_jobs_df = pd.read_sql_query(sql,con=engine)
    node_jobs = process_node_jobs_df(node_jobs_df)
    print(json.dumps(node_jobs, indent=2))
    # # df = pd.read_sql_query(sql,con=engine)
    # metric = 'cpuusage'
    # start = '2021-06-17 06:00:00-05'
    # end = '2021-06-17 08:00:00-05'
    # interval = '5 min'
    # aggregate = 'max'
    # sql = gene_idrac9_sql(metric, start, end, interval, aggregate)


def gene_idrac9_sql(metric: str, start: str, end: str, 
                    interval: str, aggregate: str) -> dict:
    """
    Generate SQL for querying iDRAC9 metrics
    interval should be like '5 minutes' or '5 min'
    start and end should be in this format "2021-03-21 17:00:00-05"
    """
    sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) as time, nodeid, fqdd as label, {aggregate}(value) as value from idrac9.{metric} WHERE timestamp >= '{start}' AND timestamp < '{end}' GROUP BY time, nodeid, label ORDER BY time;"
    return sql


def gene_slurm_sql(metric: str, start: str, end: str, 
                    interval: str, aggregate: str) -> dict:
    """
    Generate SQL for querying slurm metrics
    """
    sql = ""
    if metric == 'node_jobs':
        sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) as time, nodeid, jsonb_agg(jobs) as jobs, jsonb_agg(cpus) as cpus from slurm.{metric} WHERE timestamp >= '{start}' AND timestamp < '{end}' GROUP BY time, nodeid ORDER BY time;"
    else:
        metric = 'memoryusage'
        sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) as time, nodeid, {aggregate}(value) from slurm.{metric} WHERE timestamp >= '{start}' AND timestamp < '{end}' GROUP BY time, nodeid ORDER BY time;"
    return sql


def process_node_jobs_df(node_jobs_df):
    nodes_info = {}
    node_jobs_df['time'] = node_jobs_df['time'].apply(lambda x: int(x.timestamp()))
    node_jobs_df['fl_jobs'] = node_jobs_df.apply(lambda df_row: flatten_array(df_row, 'jobs'), axis = 1)
    node_jobs_df['fl_cpus'] = node_jobs_df.apply(lambda df_row: flatten_array(df_row, 'cpus'), axis = 1)
    node_jobs_df.drop(columns = ['jobs', 'cpus'], inplace = True)
    node_jobs_df.rename(columns={'fl_jobs': 'jobs', 'fl_cpus': 'cpus'}, inplace = True)

    grouped_df = node_jobs_df.groupby(['nodeid'])[['time', 'jobs', 'cpus']]
    for key, item in grouped_df:
        # print(grouped_df.get_group(key), "\n\n")
        # # print(key)
        # print(f'{key} - Time')
        # print(grouped_df.get_group(key)['time'].tolist())
        # print('jobs')
        jobs = grouped_df.get_group(key)['jobs'].tolist()
        # print('cpus')
        cpus = grouped_df.get_group(key)['cpus'].tolist()
        nodes_info.update({
            key:{
            'jobs': jobs,
            'cpus': cpus
            }
        })
    # print(json.dumps(out, indent=4, default=str))
    # print(node_jobs_df.groupby('nodeid').apply(lambda x: x.to_json(orient='records')))
    # .apply(lambda n_j_df: convert_df_json(n_j_df))
    return nodes_info


def convert_df_json(n_j_df):
    columns = n_j_df.columns
    for column in columns:
        n_j_df[column].tolist()
    return


def flatten_array(df_row, column: str):
    jobs = []
    cpus = []
    job_id_array = df_row['jobs']
    cpus_array = df_row['cpus']
    try:
        if job_id_array:
            # Flatten array
            fl_job_id_array = [item for sublist in job_id_array for item in sublist]
            fl_cpus_array = [item for sublist in cpus_array for item in sublist]

            # Only keep unique jobs
            for i, job in enumerate(fl_job_id_array):
                if job not in jobs:
                    jobs.append(job)
                    cpus.append(fl_cpus_array[i])
    except:
        # print(f"{df_row['time']} - {df_row['nodeid']}")
        pass
    if column == 'jobs':
        return jobs
    else:
        return cpus


def gene_node_sqls(nodes: list, metrics: dict, host_id_map: dict, 
                    start: str, end: str, interval: str, aggregate: str) -> list:
    """
    Generate node-sqls
    """
    node_sqls = []
    for node in nodes:
        host_id = host_id_map[node]
        sqls = {}
        idrac9_sqls = []
        slurm_sqls = []

        for metric in metrics['idrac9']:
            sql = gene_idrac9_sql(host_id, metric, start, end, 
                                  interval, aggregate)
            idrac9_sqls.append(sql)

        for metric in metrics['slurm']:
            sql = gene_slurm_sql(host_id, metric, start, end, 
                                 interval, aggregate)
            slurm_sqls.append(sql)

        sqls = {'idrac9': idrac9_sqls, 'slurm': slurm_sqls}
        each = {'node': node, 'metrics': metrics, 'sqls': sqls}
        node_sqls.append(each)
    return node_sqls


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

