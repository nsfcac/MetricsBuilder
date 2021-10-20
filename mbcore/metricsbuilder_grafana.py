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

sys.path.append('./')

from flask import request, jsonify
from sqlalchemy import create_engine
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
from werkzeug.exceptions import abort

from generate_sql import gene_idrac9_sql, gene_slurm_sql
# from fetch_job_data import fetch_job_data
# from fetch_node_data import fetch_node_data
from generate_timelist import gen_epoch_timelist
from utils import parse_config, init_tsdb_connection, gene_node_id_mapping

app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
AVAILABLE_METIRCS = ['systempowerconsumption', 'totalmemorypower', 
                     'totalcpupower', 'cpuusage', 'memoryusage', 'rpmreading', 
                     'temperaturereading', 'voltagereading','wattsreading', 
                     'cpu_load', 'memory_used']

# Read configuratin file
CONFIG = parse_config('./config.yml')
# Create TimeScaleDB connection
CONNECTION = init_tsdb_connection(CONFIG['timescaledb'])
# SqlAlchemy engine
ENGINE = create_engine(CONNECTION)
AGGREGATE = 'max'


@app.route('/', methods=['GET'])
@cross_origin()
def index():
    print(request.headers, request.get_json(silent=True))
    return 'Good'


@app.route('/search', methods=['POST'])
@cross_origin()
def search():
    # Find available metrics
    print(request.headers, request.get_json(silent=True))
    req = request.get_json(silent=True)

    dtype = req.get('type')

    if dtype == 'table':
        metrics = ['jobs_data']
    else:
        metrics = AVAILABLE_METIRCS
    
    return jsonify(metrics)


@app.route('/query', methods=['POST'])
@cross_origin()
def query():
    results = []
    print(request.headers, request.get_json(silent=True))
    req = request.get_json(silent=True)

    dtype = req.get('type')
    trange = req.get('range')
    targets = req.get('targets')
    # interval = req.get('interval')
    interval = '5 min'

    # start = trange['from']
    # end = trange['to']
    end = datetime.now() - timedelta(minutes=1)
    start = end - timedelta(hours=1)

    metric_list = [target['target'] for target in targets]

    # print(metric_list)

    if dtype == 'table':
        results = []
    else:
        for metric in metric_list:
            df = query_metric_df(metric, start, end, interval, AGGREGATE, ENGINE)
            response = dataframe_to_response(df, metric)
            results.extend(response)
    # print(json.dumps(results, indent=4))
    return jsonify(results)


@app.route('/annotations', methods=['POST'])
@cross_origin()
def annotations():
    print(request.headers, request.get_json(silent=True))
    return


def query_metric_df(metric: str, 
                    start: str, 
                    end: str, 
                    interval: str, 
                    aggregate: str,
                    engine: object):
    """
    Query monitoring data from TSDB and produce dataframe.
    """
    # Nodeid-nodename mapping
    mapping = gene_node_id_mapping(engine)

    # memoryusage from iDRAC9 is not available, we get it from slurm
    if metric in ['memoryusage', 'cpu_load', 'memory_used']:
        sql = gene_slurm_sql(metric, start, end, interval, aggregate)
    else:
        sql = gene_idrac9_sql(metric, start, end, interval, aggregate)

    df = pd.read_sql_query(sql,con=engine)
    
    df['nodeid'] = df['nodeid'].apply(lambda x: mapping[x])
    return df


def dataframe_to_response(df, metric):
    response = []

    if df.empty:
        return response

    if metric in ['memoryusage', 'cpu_load', 'memory_used']:
        grouped_df = df.groupby(['nodeid'])
        for key, item in grouped_df:
            node_name = key
            target = f'{node_name}_{metric}'
            this_df = grouped_df.get_group(key)
            response.append(_series_to_response(this_df, target))
    else:
        grouped_df = df.groupby(['nodeid', 'label'])
        for key, item in grouped_df:
            node_name = key[0]
            target = f'{node_name}_{metric}_{key[1]}'
            this_df = grouped_df.get_group(key)
            response.append(_series_to_response(this_df, target))

    return response


def _series_to_response(df, target):
    if df.empty:
        return {'target': '%s' % (target),
                'datapoints': []}

    timestamps = (df['time'].astype(np.int64)// 10 ** 6).values.tolist()

    values = df['value'].tolist()

    return {'target': '%s' % (target),
            'datapoints': list(zip(values, timestamps))}


if __name__ == '__main__':
    # To test: hugo.hpcc.ttu.edu:5000/metrics_builder
    app.run(host= '0.0.0.0', port=5000, threaded=True, debug=True)
    # print(metrics_builder())

    # end = datetime.now() - timedelta(minutes=1)
    # start = end - timedelta(minutes=10)
    # interval = '5 min'
    # metric = AVAILABLE_METIRCS[0]

    # df = query_metric_df(metric, start, end,interval, AGGREGATE, ENGINE)
    # response = dataframe_to_response(df)
    # print(response)


