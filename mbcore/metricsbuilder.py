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
import pandas as pd

sys.path.append('./')

from sqlalchemy import create_engine
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta

from fetch_job_data import fetch_job_data
from fetch_node_data import fetch_node_data
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

@app.route('/metrics_builder')
@cross_origin()
def metrics_builder():
    aggregated_data = {}
    nodes_data = {}
    jobs_data = {}

    # Read configuratin file
    config = parse_config('./config.yml')
    # Create TimeScaleDB connection
    connection = init_tsdb_connection(config['timescaledb'])
    # SqlAlchemy engine
    engine = create_engine(connection)

    now = datetime.now() - timedelta(minutes=1)
    prev = now - timedelta(hours=1)

    start = prev.strftime(DATETIME_FORMAT)
    end = now.strftime(DATETIME_FORMAT)

    # start = '2021-06-28T13:00:00'
    # end = '2021-06-28T14:00:00'

    interval = '5 min'
    aggregate = 'max'

    metrics = AVAILABLE_METIRCS

    nodes_data =  fetch_node_data(metrics, start, end, interval, aggregate,engine)
    jobs_data = fetch_job_data(start, end)
    time_stamp = gen_epoch_timelist(start, end, interval)

    aggregated_data.update({
        'nodes_data': nodes_data,
        'jobs_data': jobs_data,
        'time_stamp': time_stamp
    })

    return aggregated_data


if __name__ == '__main__':
    # To test: hugo.hpcc.ttu.edu:5000/metrics_builder
    app.run(host= '0.0.0.0', port=5000, threaded=True, debug=True)
    # print(metrics_builder())

