# -*- coding: utf-8 -*-
"""
This module is the MetricsBuilder core, it interacts with TimeScaleDB and 
provide data points to data analytics

Jie Li (jie.li@ttu.edu)
"""
import sys
import json
import flask
import hostlist
import itertools
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy as db

sys.path.append('./')

from flask import request, jsonify
from flask_cors import CORS, cross_origin
# from datetime import datetime, dt.timedelta
from werkzeug.exceptions import abort

from generate_sql import gene_idrac9_sql, gene_slurm_sql, gene_slurm_jobs_sql, gene_node_jobs_sql
# from fetch_job_data import fetch_job_data
# from fetch_node_data import fetch_node_data
from generate_timelist import gen_epoch_timelist
from utils import parse_config, init_tsdb_connection, gene_node_id_mapping

app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
AVAILABLE_METIRCS = ['systempowerconsumption', 'totalmemorypower', 
                     'totalcpupower', 'cpuusage', 'memoryusage', 'rpmreading', 
                     'temperaturereading', 'voltagereading','wattsreading', 
                     'cpu_load', 'memory_used']

# Read configuratin file
CONFIG = parse_config('./config.yml')
AGGREGATE = 'max'

# SqlAlchemy connection
ENGINE = db.create_engine(init_tsdb_connection(CONFIG['timescaledb']))
METADATA = db.MetaData()
CONNECTION = ENGINE.connect()

# Node id - node name mapping
NODE_ID_MAPPING = gene_node_id_mapping(con=ENGINE)


@app.route('/', methods=['GET'])
@cross_origin()
def index():
    print(request.headers, request.get_json(silent=True))
    return 'Good'


@app.route('/search', methods=['POST'])
@cross_origin()
def search():
    # Get Available metrics (including fqdd)
    avail_metrics = get_avail_metrics(CONNECTION, METADATA, ENGINE) 
    # avail_metrics = get_avail_metrics_flat(CONNECTION, METADATA, ENGINE)
    return jsonify(avail_metrics)


@app.route('/query', methods=['POST'])
@cross_origin()
def query():
    results = []
    # print(request.headers, request.get_json(silent=True))
    req = request.get_json(silent=True)

    # print(json.dumps(req))
    # Request details
    time_range = req.get('range')
    interval = req.get('interval')
    targets = req.get('targets')

    # Extract time range (from, to), metrics
    time_from = time_range.get('from')
    time_to = time_range.get('to')

    # TO DO: add partition info and aggregation function in the targets
    partition = 'nocona'
    aggregation = 'max'

    for target in targets:
        req_metric = target.get('metric', '')
        req_type = target.get('type', '')
        nodes = target.get('nodes', '')
        if req_metric and req_type == 'metrics' and len(req_metric.split(' | ')) == 3:
            partition = req_metric.split(' | ')[0]
            metric = req_metric.split(' | ')[1]
            fqdd = req_metric.split(' | ')[2]
            metrics = query_filter_metrics(metric, 
                                           fqdd,
                                           nodes,
                                           NODE_ID_MAPPING, 
                                           time_from,
                                           time_to,
                                           interval,
                                           aggregation,
                                           partition)
            results.append(metrics)
        if req_type == 'jobs':
            users = target.get('users', '')
            if not users:
                users = get_avail_users(time_from, time_to, partition)
            jobs = query_filter_jobs(users,
                                     time_from,
                                     time_to,
                                     partition)
            results.append(jobs)
        if req_type == 'node_core':
            node_core = query_node_core(time_from, time_to, interval)
            results.append(node_core)
    # print(results)
    return jsonify(results)


def query_filter_metrics(metric: str,
                         fqdd: str,
                         nodes: list,
                         NODE_ID_MAPPING,
                         time_from: str,
                         time_to: str,
                         interval: str,
                         aggregation: str = 'max',
                         partition: str = 'nocona') -> list:

    if partition in ['nocona', 'matador', 'quanah']:
        sql = gene_idrac9_sql(metric,
                              fqdd,
                              partition, 
                              time_from, 
                              time_to, 
                              interval, 
                              aggregation)
    else:
        # Slurm metrics
        sql = gene_slurm_sql(metric, 
                             time_from, 
                             time_to, 
                             interval, 
                             aggregation)

    df = pd.read_sql_query(sql,con=ENGINE)

    # Filter nodes
    # fi_df = df[df['nodeid'].isin(nodes)].copy()
    fi_df = df

    # print(nodes)
    # print(fi_df)

    # Add label in slurm metrics
    if partition == 'slurm':
        fi_df['label'] = metric

    # Convert node id to node name
    fi_df['nodeid'] = fi_df['nodeid'].apply(lambda x: NODE_ID_MAPPING[x])
    fi_df['label'] = fi_df['label'].apply(lambda x: f'{metric}|{x}')

    # Pivot the table
    df_p = fi_df.pivot(index='time', columns=['nodeid', 'label'], values='value')
    
    # Flatten the table
    df_p.columns = [ '|'.join([str(c) for c in c_list]) for c_list in df_p.columns.values ]
    
    # print(df_p)
    metrics = metrics_df_to_response(df_p)

    # print(metrics)
    return metrics


def metrics_df_to_response(df)-> dict:
    # Convert index to column
    df.reset_index(inplace=True)

    # Convert datetime to epoch time
    # df['time'] = df['time'].astype('int64')// 1e9
    df['time'] = df['time'].apply(lambda x: int(x.timestamp() * 1000))

    columns = [{'text': 'time', 'type': 'time'}]
    columns_raw = list(df.columns)
    for column in columns_raw[1:]:
        c_text = f"{column.split('|')[1]}-{column.split('|')[2]}"
        c_type = 'number'
        c_label = f"| {column.split('|')[0]}"
        column_info = {'text': c_text, 'type': c_type, 'label': c_label}
        columns.append(column_info)
    
    rows = df.values.tolist()
    response = {'columns': columns, 'rows': rows}
    return response


def query_filter_jobs(users: list,
                      time_from: str,
                      time_to: str,
                      partition: str = 'nocona') -> list:
    sql = gene_slurm_jobs_sql(time_from, time_to, partition)
    df = pd.read_sql_query(sql,con=ENGINE)
    jobs = jobs_df_to_response(df)
    return jobs


def query_node_core(time_from: str,
                    time_to: str,
                    interval: str) -> list:
    sql = gene_node_jobs_sql(time_from, time_to, interval)
    df = pd.read_sql_query(sql,con=ENGINE)
    # print(df)
    node_jobs = node_jobs_df_to_response(df)
    return node_jobs


def jobs_df_to_response(df)-> dict:
    columns = []
    selected_columns = ['job_id', 'name', 'user_id', 'user_name', 'nodes', 
                        'node_count', 'cpus', 'start_time', 'end_time']
    selected_df = df[selected_columns].copy()

    # convert ['cpu-1-1', 'cpu-1-2'] -> '{cpu-1-1, cpu-1-1}'
    selected_df['nodes'] = selected_df['nodes'].apply(lambda x: '{' + ', '.join(x) + '}')
    # selected_df['start_time'] = selected_df['start_time'].apply(lambda x: x * 1000)
    # selected_df['end_time'] = selected_df['end_time'].apply(lambda x: x * 1000)
    
    columns_raw = list(selected_df.columns)
    for column in columns_raw:
        if column in ['job_id', 'user_id', 'cpus', 'start_time', 'end_time']:
            c_type = 'number'
        else:
            c_type = 'string'

        column_info = {'text': column, 'type': c_type}
        columns.append(column_info)
    
    rows = selected_df.values.tolist()
    response = {'columns': columns, 'rows': rows}
    return response


def node_jobs_df_to_response(df)-> dict:
    df['time'] = df['time'].apply(lambda x: int(x.timestamp() * 1000))

    df['nodeid'] = df['nodeid'].apply(lambda x: NODE_ID_MAPPING[x])
    df['fl_jobs'] = df.apply(
        lambda df_row: flatten_array(df_row, 'jobs'), axis = 1)
    df['fl_cpus'] = df.apply(
        lambda df_row: flatten_array(df_row, 'cpus'), axis = 1)
    df.drop(columns = ['jobs', 'cpus'], inplace = True)
    df.rename(columns={'fl_jobs': 'jobs', 'fl_cpus': 'cpus'}, inplace = True)
    
    columns = [{'text': 'time', 'type': 'time'}]
    columns_raw = list(df.columns)
    for column in columns_raw[1:]:
        column_info = {'text': column, 'type': 'string'}
        columns.append(column_info)
    
    rows = df.values.tolist()
    response = {'columns': columns, 'rows': rows}
    return response


def flatten_array(df_row, column: str) -> str:
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
                    jobs.append(str(job))
                    cpus.append(str(fl_cpus_array[i]))
    except:
        # print(f"{df_row['time']} - {df_row['nodeid']}")
        pass
    if column == 'jobs':
        str_jobs = '{' + (', ').join(jobs) + '}'
        return str_jobs
    else:
        str_cpus = '{' + (', ').join(cpus) + '}'
        return str_cpus


def get_avail_metrics(connection: object, 
                      metadata: object,
                      engine: object) -> list:
    """
    Get available metrics from metrics_definition
    """
    result = []
    metrics_definition = db.Table('metrics_definition', 
                                   metadata, 
                                   autoload=True, 
                                   autoload_with=engine)
    avail_metrics_fqdd_tree = {
            'name': 'password',
            'children': []
    }

    partitions = ['nocona', 'matador']

    for partition in partitions:
        avail_metrics_fqdd = []
        if partition == 'nocona':
            # CPU nodes
            query = db.select([metrics_definition.c.metric_id, 
                            metrics_definition.c.fqdd_cpu]).\
                            where(metrics_definition.c.valid_cpu==True)
        else:
            # Matador GPU nodes
            query = db.select([metrics_definition.c.metric_id, 
                            metrics_definition.c.fqdd_gpu]).\
                            where(metrics_definition.c.valid_gpu==True)

        result_proxy = connection.execute(query)
        result = result_proxy.fetchall()

        if result:
            for i in result:
                metric = i[0]
                children = []
                for fqdd in i[1]:
                    child = {
                        'name': fqdd, 'value': f'{partition} | {metric} | {fqdd}'
                    }
                    children.append(child)
                avail_metrics_fqdd.append({
                    'name': metric, 'children': children
                })
        
        child_dict = {
            'name': partition,
            'children': avail_metrics_fqdd
        }

        avail_metrics_fqdd_tree['children'].append(child_dict)
    
    # Manually add metrics info of quanah
    quanah_child_dict = {
        'name': 'quanah',
        'children': [
            {
                'name': 'rpmreading',
                'children': [
                    {
                        'name': 'FAN_1', 'value': 'quanah | rpmreading | FAN_1'
                    },
                    {
                        'name': 'FAN_2', 'value': 'quanah | rpmreading | FAN_2'
                    },
                    {
                        'name': 'FAN_3', 'value': 'quanah | rpmreading | FAN_3'
                    },
                    {
                        'name': 'FAN_4', 'value': 'quanah | rpmreading | FAN_4'
                    }
                ]
            },
            {
                'name': 'systempowerconsumption',
                'children': [
                    {
                        'name': 'System Power Control', 'value': 'quanah | systempowerconsumption | System Power Control'
                    },
                ]
            },
            {
                'name': 'temperaturereading',
                'children': [
                    {
                        'name': 'CPU1 Temp', 'value': 'quanah | temperaturereading | CPU1 Temp'
                    },
                    {
                        'name': 'CPU2 Temp', 'value': 'quanah | temperaturereading | CPU2 Temp'
                    },
                    {
                        'name': 'Inlet Temp', 'value': 'quanah | temperaturereading | Inlet Temp'
                    },
                ]
            },
        ]
    }
    avail_metrics_fqdd_tree['children'].append(quanah_child_dict)

    # Manually add metrics info of slurm
    slurm_child_dict = {
        'name': 'slurm',
        'children': [
            {
                'name': 'memoryusage',
                'children': [
                    {
                        'name': 'Memory Usage', 'value': 'slurm | memoryusage | Memory Usage'
                    }
                ]
            },
            {
                'name': 'memory_used',
                'children': [
                    {
                        'name': 'Memory Used', 'value': 'slurm | memory_used | Memory Used'
                    },
                ]
            },
            {
                'name': 'cpu_load',
                'children': [
                    {
                        'name': 'CPU Load', 'value': 'slurm | cpu_load | CPU Load'
                    }
                ]
            },
        ]
    }
    avail_metrics_fqdd_tree['children'].append(slurm_child_dict)
    # print(avail_metrics_fqdd_tree)
    return avail_metrics_fqdd_tree


def get_avail_users(time_from: str, time_to: str, partitions: list) -> list:
    all_users = []
    for partition in partitions:
        sql = gene_slurm_jobs_sql(time_from, time_to, partition)
        df = pd.read_sql_query(sql,con=ENGINE)
        users = df['user_name'].unique()
        all_users.extend(users)
    # Remove duplicated users
    all_users = list(set(all_users))
    return all_users



if __name__ == '__main__':
    # To test: hugo.hpcc.ttu.edu:5000/metrics_builder
    app.run(host= '0.0.0.0', port=5000, threaded=True, debug=True)
    # print(metrics_builder())

    # users = ['99362', '98275', '97401']
    # query_filter_jobs(users, time_from, time_to, partition)
    # get_avail_users()

    # df = pd.read_csv('./df_sample.csv', index_col=0, parse_dates=True)
    # df_to_response(df)

    # partition = 'nocona'
    # get_avail_metrics_flat(CONNECTION, METADATA, ENGINE, partition)


