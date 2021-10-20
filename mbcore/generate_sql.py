from datetime import datetime


def gene_idrac9_sql(metric: str,
                    fqdd: str,
                    partition: str,
                    time_from: str, 
                    time_to: str, 
                    interval: str, 
                    aggregation: str) -> str:
    """
    Generate SQL for querying iDRAC9 metrics
    interval should be like '5 minutes' or '5 min'
    start and end should be in this format "2021-03-21 17:00:00-05"
    """
    if partition == 'nocona':
        schema = 'idrac9'
    if partition == 'matador':
        schema = 'idrac9_gpu'

    sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) AS time, \
        nodeid, fqdd AS label, {aggregation}(value) AS value \
        FROM {schema}.{metric} \
        WHERE timestamp >= '{time_from}' \
        AND timestamp < '{time_to}' \
        AND fqdd = '{fqdd}' \
        GROUP BY time, nodeid, label \
        ORDER BY time;"
    # print(sql)
    return sql


def gene_slurm_jobs_sql(time_from: str,
                        time_to: str,
                        partition: str = 'nocona') -> str:
    """
    Generate SQL for querying slurm jobs
    """
    utc_from = datetime.strptime(time_from, '%Y-%m-%dT%H:%M:%S.%fZ')
    epoch_from = int((utc_from - datetime(1970, 1, 1)).total_seconds())
    utc_to = datetime.strptime(time_to, '%Y-%m-%dT%H:%M:%S.%fZ')
    epoch_to = int((utc_to - datetime(1970, 1, 1)).total_seconds())

    sql = f"SELECT * FROM slurm.jobs \
            WHERE partition = '{partition}' \
            AND start_time < {epoch_to} \
            AND end_time > {epoch_from};"
    return sql


# For metrics collected from slurm
def gene_slurm_sql(metric: str, 
                   start: str, 
                   end: str, 
                   interval: str, 
                   aggregate: str) -> str:
    """
    Generate SQL for querying slurm metrics
    """
    sql = ""
    if metric == 'node_jobs':
        sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) AS time, \
            nodeid, jsonb_agg(jobs) AS jobs, jsonb_agg(cpus) AS cpus \
            FROM slurm.{metric} \
            WHERE timestamp >= '{start}' \
            AND timestamp <= '{end}' \
            GROUP BY time, nodeid \
            ORDER BY time;"
    else:
        sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) AS time, \
            nodeid, {aggregate}(value) AS value\
            FROM slurm.{metric} \
            WHERE timestamp >= '{start}' \
            AND timestamp <= '{end}' \
            GROUP BY time, nodeid \
            ORDER BY time;"
    return sql


def gene_metric_sqls(metrics: list,
                     start: str, 
                     end: str, 
                     interval: str, 
                     aggregate: str) -> list:
    """
    Generate sqls based on metrics
    """
    node_sqls = []
    return node_sqls