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
import json

from dateutil.parser import parse

from metrics_builder import utils, api_utils

def metricsbuilder(request: dict):
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
    # Extract basic info for querying the database
    partition = request.get("partition")
    # node is represented as format like cpu-1-1
    nodelist = request.get("nodes")
    
    range = request.get("range")
    if range:
        start = range.get("from")
        end = range.get("to")

    start = parse(start)
    end = parse(end)

    start = start.strftime(DATETIME_FORMAT)
    end = end.strftime(DATETIME_FORMAT)

    request["range"]["from"] = start
    request["range"]["to"] = end
    
    interval = request.get("interval")

    # TSDB Connection
    connection = utils.init_tsdb_connection(partition)

    # # iDRAC schema (the schema where iDRAC metrics are stored)
    # idrac_schema = utils.parse_config()['timescaledb'][f'{partition}_idrac_schema']

    # Node id - node name mapping
    id_node_mapping = api_utils.get_id_host_mapping(connection, nodelist)

    if not id_node_mapping:
        raise Exception("Cannot find id-node mapping in the node metadata table!")

    results = api_utils.query_tsdb_parallel(request, id_node_mapping, connection)
    time_stamp = api_utils.gen_epoch_timelist(start, end, interval)

    results.update({
        'time_stamp': time_stamp
    })

    return results


def search(partition: str):
    # TSDB Connection
    connection = utils.init_tsdb_connection(partition)
    # iDRAC schema (the schema where iDRAC metrics are stored)
    idrac_schema = utils.parse_config()['timescaledb'][f'{partition}_idrac_schema']

    metric_fqdd_mapping = api_utils.get_metric_fqdd_mapping(connection, idrac_schema)
    metric_fqdd_tree = api_utils.get_metric_fqdd_tree(metric_fqdd_mapping, idrac_schema)
    return metric_fqdd_tree