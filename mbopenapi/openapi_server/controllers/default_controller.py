import connexion
import six
import multiprocessing
from itertools import repeat

from openapi_server.models.error_message import ErrorMessage  # noqa: E501
from openapi_server.models.unified_metrics import UnifiedMetrics  # noqa: E501
from openapi_server import util
from openapi_server.mb_utils import parse_config, parse_nodelist

from openapi_server.controllers.generate_timelist import gen_timelist, gen_epoch_timelist
from openapi_server.controllers.query_nodedata import query_nodedata
from openapi_server.controllers.query_jobdata import query_jobdata
from openapi_server.controllers.process_nodedata import process_nodedata
from openapi_server.controllers.process_jobdata import generate_jobset, process_jobdata


def get_unified_metric(start, end, interval, value, compress):  # noqa: E501
    """get_unified_metric

    Get **unified metrics** based on speficied start time, end time, time interval and value type. The **start** and **end** time should follow date-time Notation as defined by [RFC 3339, section 5.6](https://tools.ietf.org/html/rfc3339#section-5.6), e.g. &#x60;2020-02-12T14:00:00Z&#x60;; the time **interval** should follow **duration literals**, which specify a length of time; the **value** type should only be &#x60;min&#x60;, &#x60;max&#x60;, &#x60;mean&#x60;, or &#x60;median&#x60;.  A duration literal is an integer literal followed immediately (with no spaces) by a duration unit, the units include &#x60;s&#x60;(second), &#x60;m&#x60;(minute), &#x60;h&#x60;(hour), &#x60;d&#x60;(day), &#x60;w&#x60;(week).  Use compress to specify returned data is compressed or not. If query large range of time with small interval, it would reduce significant transfering time using compressed data. For Json data compression and de-compression, please refer to [this](https://medium.com/@busybus/zipjson-3ed15f8ea85d).  One thing to be noticed, due to we switched database on April 28, 2020 11:40:00 AM GMT-05:00 DST, currently we do not support requesting data with time range falls on this time point.  # noqa: E501

    :param start: start time of time range of the monitoring metrics
    :type start: str
    :param end: end time of time range of the monitoring metrics
    :type end: str
    :param interval: time interval for aggregating the monitoring metrics
    :type interval: str
    :param value: value type of the monitoring metrics
    :type value: str
    :param compress: return compressed data
    :type compress: bool

    :rtype: UnifiedMetrics
    """
    config_path = 'openapi_server/controllers/config.yml'
    start = util.deserialize_datetime(start)
    end = util.deserialize_datetime(end)

    # Parse configuration, get target node list
    config = parse_config('config_path')
    node_list = parse_nodelist(config['nodelist'])
    measurements = config["measurements"]
    influx_cfg = config['influxdb']

    # Switch database according to the time we switched the database
    switch_time = 1594537200
    start_epoch = int(start.timestamp())
    end_epoch = int(end.timestamp())

    # Check sanity
    if start_epoch >= switch_time:
        dbname = config["influxdb"]["phase2"]
    elif end_epoch <= switch_time:
        dbname = config["influxdb"]["phase1"]
    else:
        return ErrorMessage(
            error_code='400 INVALID_PARAMETERS',
            error_message='Due to we switched database on July 12, 2020 \
                02:00:00 AM GMT-05:00 DST, currently we do not support \
                    requesting data with time range falls on this time point.'
        )

    if start > end:
        return ErrorMessage(
            error_code='400 INVALID_PARAMETERS',
            error_message='Start time should no larger than end time'
        )
    else:
        # Initialize returned metrics
        unified_metrics = UnifiedMetrics()
        node_data = {}
        job_data = {}

        # # Configure influxdb client
        influx_cfg.update({
            "database": dbname
        })

        # Time strings used in query influxdb
        st_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
        et_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Generate time list
        time_list = gen_timelist(start, end, interval)
        epoch_time_list = gen_epoch_timelist(start, end, interval)

        # Get nodes data
        query_nodedata_args = zip(node_list, repeat(influx_cfg), 
                                  repeat(measurements), 
                                  repeat(st_str), repeat(et_str), 
                                  repeat(interval), repeat(value))
        
        with multiprocessing.Pool() as pool:
            # Query data
            nodedata = pool.starmap(query_nodedata, query_nodedata_args)

            # Process data
            process_nodedata_args = zip(nodedata, repeat(epoch_time_list))
            processed_nodedata = pool.starmap(process_nodedata, process_nodedata_args)

            # Get all job set
            all_jobset = pool.map(generate_jobset, process_nodedata)

        # Generate dict for each node data
        for data in processed_nodedata:
            for key, value in data.items():
                node_data.update({
                    key: value
                })

        # Get jobs data
        flatten_jobset = list(set([item for sublist in all_jobset for item in sublist]))
        # Request jobs information according to the job set
        all_jobdata = query_jobdata(flatten_jobset, influx_cfg)

        # Process job data
        with multiprocessing.Pool() as pool:
            processed_jobdata = pool.map(process_jobdata, all_jobdata)

        for data in processed_jobdata:
            for key, value in data.items():
                job_data.update({
                    key: value
                })
        # Aggregate time list, nodes and jobs data

    return 
