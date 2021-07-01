def gene_idrac9_sql(metric: str, 
                    start: str, 
                    end: str, 
                    interval: str, 
                    aggregate: str) -> str:
    """
    Generate SQL for querying iDRAC9 metrics
    interval should be like '5 minutes' or '5 min'
    start and end should be in this format "2021-03-21 17:00:00-05"
    """
    sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) AS time, \
        nodeid, fqdd AS label, {aggregate}(value) AS value \
        FROM idrac9.{metric} \
        WHERE timestamp >= '{start}' \
        AND timestamp < '{end}' \
        GROUP BY time, nodeid, label \
        ORDER BY time;"
    return sql


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
            AND timestamp < '{end}' \
            GROUP BY time, nodeid \
            ORDER BY time;"
    else:
        metric = 'memoryusage'
        sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) AS time, \
            nodeid, {aggregate}(value) AS value\
            FROM slurm.{metric} \
            WHERE timestamp >= '{start}' \
            AND timestamp < '{end}' \
            GROUP BY time, nodeid \
            ORDER BY time;"
    return sql


def gene_metric_sqls(metrics: list,
                     start: str, 
                     end: str, 
                     interval: str, 
                     aggregate: str) -> list:
    """
    Generate sqls bASed on metrics
    """
    node_sqls = []
    return node_sqls