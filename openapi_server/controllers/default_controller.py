import connexion
import six

from openapi_server.models.available_metrics import AvailableMetrics  # noqa: E501
from openapi_server.models.inline_response_default import InlineResponseDefault  # noqa: E501
from openapi_server.models.queue_status import QueueStatus  # noqa: E501
from openapi_server.models.request_metrics import RequestMetrics  # noqa: E501
from openapi_server.models.web_response_metrics import WebResponseMetrics  # noqa: E501
from openapi_server import util

from metrics_builder import slurm_queue, mbweb, mbweb_utils, mbgrafana, api_utils
from metrics_builder import logger
log = logger.get_logger(__name__)


def metricsbuilder(partition, 
                   start=None, 
                   end=None, 
                   interval=None, 
                   aggregation=None, 
                   nodelist=None, 
                   metrics=None, 
                   compression=None):  # noqa: E501
    """Query Metrics for Web Applications

    Execute queries for metrics, job information, etc. # noqa: E501

    :param partition: The target partition of the HPC cluster
    :type partition: str
    :param start: Start time of the time range
    :type start: str
    :param end: End time of the time range
    :type end: str
    :param interval: Time interval for aggregating the metrics.
    :type interval: str
    :param aggregation: Aggregation function.
    :type aggregation: str
    :param nodelist: Target nodes in the cluster.
    :type nodelist: str
    :param metrics: Selected Metrics.
    :type metrics: List[str]
    :param compression: Return compressed data.
    :type compression: bool

    :rtype: WebResponseMetrics
    """
    start = util.deserialize_datetime(start)
    end = util.deserialize_datetime(end)
    # print(f"controller: {start}")

    nodelist = nodelist
    try:
        metrics = mbweb.metricsbuilder(partition, 
                                       start, 
                                       end, 
                                       interval, 
                                       aggregation, 
                                       nodelist, 
                                       metrics, 
                                       compression)
        nodes_info = metrics['nodes_info']
        jobs_info = metrics['jobs_info']
        time_stamp = metrics['time_stamp']
        
        if compression:
            nodes_info = mbweb_utils.json_zip(nodes_info)
            jobs_info = mbweb_utils.json_zip(jobs_info)

        response = WebResponseMetrics(nodes_info = nodes_info, 
                                      jobs_info = jobs_info,
                                      time_stamp = time_stamp)
    except Exception as e:
        log.error(f"Error of MetricsBuilder for web : {e}")
        response = InlineResponseDefault(name='Query metrics error',
                                         message=str(e))
    return response


def query():  # noqa: E501
    """Query Metrics for Grafana Plugins

    Execute queries for metrics, job information, etc. # noqa: E501

    :param request_metrics: 
    :type request_metrics: dict | bytes

    :rtype: List[object]
    """
    if connexion.request.is_json:
        # request_metrics = RequestMetrics.from_dict(connexion.request.get_json())  # noqa: E501
        request_metrics = connexion.request.get_json()
        return mbgrafana.metricsbuilder(request_metrics)


def queue():  # noqa: E501
    """Get Queue Status of Slurm

     # noqa: E501


    :rtype: QueueStatus
    """
    try:
        queue = slurm_queue.get_queue()
        response = QueueStatus(timestamp=queue['timestamp'], 
                               queue_status=queue['queue_status'])
    except Exception as e:
        response = InlineResponseDefault(name='Get queue info error',
                                         message=e)
    return response


def search(partition=None):  # noqa: E501
    """Get Available Metric Names for Grafana Plugins

    Return available metrics of iDRAC and Slurm # noqa: E501

    :param partition: Target partition of the HPC cluster
    :type partition: str

    :rtype: AvailableMetrics
    """
    return mbgrafana.search(partition)