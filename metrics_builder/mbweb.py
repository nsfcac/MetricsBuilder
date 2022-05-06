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
import hostlist

from metrics_builder import utils, api_utils, mbweb_utils

def metricsbuilder(partition, 
                   start=None, 
                   end=None, 
                   interval=None, 
                   aggregation=None, 
                   nodelist=None, 
                   metrics=None, 
                   compress=None):
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    # TSDB Connection
    connection = utils.init_tsdb_connection(partition)

    # Node id - node name mapping
    ID_NODE_MAPPING = api_utils.get_id_node_mapping(connection)
    NODE_ID_MAPPING = {v : k for k, v in ID_NODE_MAPPING.items()}
    
    # Expand nodelist
    nodelist = hostlist.expand_hostlist(nodelist)
    # Convert ipaddress to hostname
    nodelist = [mbweb_utils.ip_hostname(node) for node in nodelist]
    
    # Convert nodelist to nodeidlist
    nodeidlist = [NODE_ID_MAPPING[n] for n in nodelist]

    # generate targets
    targets = mbweb_utils.gene_targets(connection, metrics, nodeidlist)

    start = start.strftime(DATETIME_FORMAT)
    end = end.strftime(DATETIME_FORMAT)

    request = {
        "range": {
            "from": start,
            "to": end
        },
        "interval": interval,
        "aggregation": aggregation,
        "targets": targets,
    }

    results = api_utils.query_tsdb_parallel(request, ID_NODE_MAPPING, connection)
    time_stamp = api_utils.gen_epoch_timelist(start, end, interval)
    
    results.update({
        'time_stamp': time_stamp
    })
    return results