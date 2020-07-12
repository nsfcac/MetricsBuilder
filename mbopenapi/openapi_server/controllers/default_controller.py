import connexion
import six
from influxdb import InfluxDBClient

from openapi_server.models.error_message import ErrorMessage  # noqa: E501
from openapi_server.models.unified_metrics import UnifiedMetrics  # noqa: E501
from openapi_server import util
from openapi_server.mb_utils import parse_config, parse_nodelist

from openapi_server.controllers.generate_timelist import gen_timelist, gen_epoch_timelist


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
    influx_host = config['influxdb']['host']
    influx_port = config['influxdb']['port']

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

        # Initialize influxdb client
        client = InfluxDBClient(host=influx_host, port=influx_port, database=dbname)

        # Time strings used in query influxdb
        st_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
        et_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Generate time list
        time_list = gen_timelist(start, end, interval)
        epoch_time_list = gen_epoch_timelist(start, end, interval)

        # Get nodes data

        # Get jobs data

        # Aggregate time list, nodes and jobs data

    return 
