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
import zlib
import base64

import metrics_builder.api_utils as api_utils


def gene_targets(connection: str, idrac_schema: str, metrics: list):
    targets = []
    
    metric_fqdd = api_utils.get_metric_fqdd_mapping(connection, idrac_schema)
    # Conver all keys into lowercase
    metric_fqdd = {k.lower(): v for k, v in metric_fqdd.items()}

    for metric in metrics:
        target = const_target(metric, idrac_schema, metric_fqdd)
        targets.extend(target)

    return targets


def const_target(metric: str, idrac_schema: str, metric_fqdd: dict):
    target = []
    metric_name = metric.split('-')[0]
    metric_source = metric.split('-')[1]

    idrac_mapping_table = {
        'System Power': 'systempowerconsumption',
        'CPU Power': 'totalcpupower',
        'Memory Power': 'totalmemorypower',
        'Fan Sensor': 'rpmreading',
        'Temperature Sensor': 'temperaturereading',
        'CPU Usage': 'cpuusage',
    }

    slurm_mapping_table = {
        'Memory Usage': 'memoryusage'
    }

    if metric_source == 'iDRAC':
        mm_name = idrac_mapping_table.get(metric_name, '')
        if mm_name:
            fqdd = metric_fqdd.get(mm_name, '')
            if fqdd:
                for f in fqdd:
                    metric_str = f"{idrac_schema} | {mm_name} | {f}"
                    target.append({
                        "metric": metric_str,
                        "type": "metrics",
                        # "nodes": nodeidlist,
                    })
    else:
        mm_name = slurm_mapping_table.get(metric_name, '')
        if mm_name:
            metric_str = f"slurm | {mm_name} | {mm_name}"
            target.append({
                "metric": metric_str,
                "type": "metrics",
                # "nodes": nodeidlist,
            })
        else:
            if metric_name == 'NodeJobs Correlation':
                target.append({
                    "type": "node_core",
                    # "nodes": nodeidlist,
                })
            elif metric_name == 'Jobs Info':
                target.append({
                    "type": "jobs",
                    # "nodes": nodeidlist,
                })
            else:
                pass
            
    return target


def json_zip(j):
    ZIPJSON_KEY = 'base64(zip(o))'
    j = {
        ZIPJSON_KEY: base64.b64encode(
            zlib.compress(
                json.dumps(j).encode('utf-8')
            )
        ).decode('ascii')
    }
    return j