"""
MIT License

Copyright (c) 2022 Texas Tech University

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
This file is part of MetricsBuilderAPI.

Author:
    Jie Li, jie.li@ttu.edu
"""
from datetime import datetime


def generate_slurm_sql(metric: str, 
                       start: str, 
                       end: str, 
                       interval: str, 
                       aggregate: str):
    """generate_slurm_sql Generate Slurm Sql

    Generate sql for querying slurm metrics

    Args:
        metric (str): metric name
        start (str): start of time range
        end (str): end of time range
        interval (str): aggregation interval
        aggregate (str): aggregation function

    Returns:
        string: sql string
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


def generate_idrac_sql(metric: str, 
                       fqdd: str,
                       start: str, 
                       end: str, 
                       interval: str, 
                       aggregate: str,
                       schema: str = 'idrac'):
    """generate_idrac_sql Generate iDRAC Sql

    Generate sql for querying idrac metrics

    Args:
        metric (str): metric name
        fqdd (str): Fully Qualified Device Descriptor
        start (str): start of time range
        end (str): end of time range
        interval (str): aggregation interval
        aggregate (str): aggregation function
    
    Returns:
        string: sql string
    """
    sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) AS time, \
        nodeid, fqdd AS label, {aggregate}(value) AS value \
        FROM {schema}.{metric} \
        WHERE timestamp >= '{start}' \
        AND timestamp < '{end}' \
        AND fqdd = '{fqdd}' \
        GROUP BY time, nodeid, label \
        ORDER BY time;"
    return sql


def generate_slurm_jobs_sql(start: str,end: str):
    """generate_slurm_jobs_sql Generate Slurm Jobs Sql

    Generate Sql for querying slurm jobs info

    Args:
        start (str): start time
        end (str): end time

    Returns:
        string: sql string
    """
    utc_from = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
    epoch_from = int((utc_from - datetime(1970, 1, 1)).total_seconds())
    utc_to = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ')
    epoch_to = int((utc_to - datetime(1970, 1, 1)).total_seconds())

    sql = f"SELECT * FROM slurm.jobs \
            WHERE start_time < {epoch_to} \
            AND end_time > {epoch_from};"
    return sql


def generate_node_jobs_sql(start: str, end: str, interval: str):
    """gene_node_jobs_sql Generate Node-Jobs Sql

    Generate SQL for querying node-jobs correlation

    Args:
        start (str): start time
        end (str): end time
        interval (str): interval for aggragation

    Returns:
        string: sql string
    """
    sql = f"SELECT time_bucket_gapfill('{interval}', timestamp) AS time, \
            nodeid, jsonb_agg(jobs) AS jobs, jsonb_agg(cpus) AS cpus \
            FROM slurm.node_jobs \
            WHERE timestamp >= '{start}' \
            AND timestamp <= '{end}' \
            GROUP BY time, nodeid \
            ORDER BY time;"
    return sql