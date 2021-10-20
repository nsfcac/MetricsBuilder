
import sys
import pandas as pd
from multiprocessing import Pool

sys.path.append('./')

from generate_sql import gene_idrac9_sql, gene_slurm_sql
from utils import parse_config, init_tsdb_connection, gene_node_id_mapping
from process_df import process_node_jobs_df, process_idrac9_df, process_slurm_df


def fetch_node_data(metrics: list, 
                    start: str, 
                    end: str, 
                    interval: str, 
                    aggregate: str, 
                    engine: object) -> dict:
    """
    Get nodes info, including the data of node-jobs correlation and specified
    metrics
    """
    nodes_data = {}
    node_jobs = {}
    metrics_data = []

    # Nodeid-nodename mapping
    mapping = gene_node_id_mapping(engine)

    # Node-jobs-cpus correlation
    node_jobs_sql = gene_slurm_sql('node_jobs', 
                                   start, 
                                   end, 
                                   interval, 
                                   aggregate)
                                   
    node_jobs_df = pd.read_sql_query(node_jobs_sql,con=engine)
    node_jobs = process_node_jobs_df(node_jobs_df, mapping)

    # Use multiprocessing
    # process_num = len(metrics)
    # with Pool(process_num) as p:
    #     p.map()

    for metric in metrics:
        metric_data = query_metric(metric, start, end, interval, 
                                   aggregate,engine, mapping)
        metrics_data.append(metric_data)
    
    # Aggregate all metrics and store the result in nodes_data
    for node in metrics_data[0].keys():
        try:
            nodes_data[node] = metrics_data[0][node]
            for metric_data in metrics_data[1:]:
                nodes_data[node].update(metric_data[node])
            nodes_data[node].update(node_jobs[node])
        except Exception as err:
            pass
    
    return nodes_data


def query_metric(metric: str, 
                 start: str, 
                 end: str, 
                 interval: str, 
                 aggregate: str,
                 engine: object,
                 mapping: dict) -> dict:
    """
    Query monitoring data from TSDB and produce dict format data.
    """
    # memoryusage from iDRAC9 is not available, we get it from slurm
    if metric in ['memoryusage', 'cpu_load', 'memory_used']:
        sql = gene_slurm_sql(metric, start, end, interval, aggregate)
    else:
        sql = gene_idrac9_sql(metric, start, end, interval, aggregate)

    df = pd.read_sql_query(sql,con=engine)

    if metric in ['memoryusage', 'cpu_load', 'memory_used']:
        metric_info = process_slurm_df(metric, df, mapping)
    else:
        metric_info = process_idrac9_df(metric, df, mapping)
    
    return metric_info
