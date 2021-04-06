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
    metrics = ['systempowerconsumption', 'totalcpupower', 'totalmemorypower', 'cpuusage']
    start = '2021-03-25 15:00:00-05'
    end = '2021-03-26 05:00:00-05'
    interval = '5 min'
    aggregate = 'max'
    nodelist = 'cpu-23-[16-28,34-38,45-54,56-60],cpu-24-[1,5-6,16-19,38-41],cpu-25-[4-8,11-15,50-54,56-60]'
    nodes = hostlist.expand_hostlist(nodelist)

    node_sqls = gene_node_sqls(nodes, metrics, host_id_map, 
                               start, end, interval, aggregate)
    
    # print(json.dumps(node_sqls, indent=4))

    loop = asyncio.get_event_loop()
    node_metrics = loop.run_until_complete(async_query_tsdb(node_sqls, dsn))
    print(json.dumps(node_metrics, indent=4, default=str))


def gene_idrac9_sql(host_id: int, metric: str, start: str, end: str, 
                    interval: str, aggregate: str) -> dict:
    """
    Generate SQL for querying iDRAC9 metrics
    interval should be like '5 minutes' or '5 min'
    start and end should be in this format "2021-03-21 17:00:00-05"
    """
    sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) as time, fqdd as label, {aggregate}(value) from idrac9.{metric} WHERE nodeid = {host_id} AND timestamp >= '{start}' AND timestamp <= '{end}' GROUP BY time, label ORDER BY time;"
    return sql


def gene_node_sqls(nodes: list, metrics: list, host_id_map: dict, 
                    start: str, end: str, interval: str, aggregate: str) -> list:
    """
    Generate node-sqls
    """
    node_sqls = []
    for node in nodes:
        host_id = host_id_map[node]
        sqls = []
        for metric in metrics:
            sql = gene_idrac9_sql(host_id, metric, start, end, 
                                  interval, aggregate)
            sqls.append(sql)
        each = {'node': node, 'metrics': metrics, 'sqls': sqls}
        node_sqls.append(each)
    return node_sqls


async def async_query_tsdb(node_sqls: list, dsn: str) -> list:
    """
    node_sqls = [{'node': 'cpu-1-1', 'sqls':[]}]
    """
    tasks = []
    async with aiopg.create_pool(dsn) as pool:
        for each in node_sqls:
            node = each['node']
            metrics = each['metrics']
            for i, sql in enumerate(each['sqls']):
                tasks.append(async_execute(node, metrics[i], sql, pool))
        return await asyncio.gather(*tasks) 


async def async_execute(node: str, metric: str, sql: str, pool: object) -> dict:
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql)
                resp = await cur.fetchall()
                return {'node': node, metric: resp}
    except Exception as err:
        print(f"{node} : {err}")

# def query_tsdb(conn: object, host: str, sql: str) -> list
#     """
#     Query TimeScaleDB, return host metrics in a list of tuples
#     """
#     cur = conn.cursor()
#     cur.execute(sql)
#     metrics = cur.fetchall()
#     return {host: metrics}


# metrics = {}
# time_list = []
# label_value = {}
# for(time, label, value) in cur.fetchall():
#         if time not in time_list:
#             time_list.append(time)
#         if label not in label_value:
#             label_value.update(
#                 label:[value]
#             )
#         else:
#             label_value[label].append(value)
    
#     metrics.update(
#         "time": time_list,
#         "values" : label_value
#     )


if __name__ == '__main__':
    main()

