# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.available_metrics import AvailableMetrics  # noqa: E501
from openapi_server.models.inline_response_default import InlineResponseDefault  # noqa: E501
from openapi_server.models.queue_status import QueueStatus  # noqa: E501
from openapi_server.models.request_metrics import RequestMetrics  # noqa: E501
from openapi_server.models.web_response_metrics import WebResponseMetrics  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_metricsbuilder(self):
        """Test case for metricsbuilder

        Query Metrics for Web Applications
        """
        query_string = [('start', '2022-04-16T10:00-05:00'),
                        ('end', '2022-04-16T12:00-05:00'),
                        ('interval', '5m'),
                        ('aggregation', 'max'),
                        ('nodelist', '10.101.23.[1-60],10.101.24.[1-60],10.101.25.[1-60],10.101.26.[1-60]'),
                        ('metrics', ["System Power-iDRAC","CPU Power-iDRAC","Memory Power-iDRAC","NodeJobs Correlation-Slurm","Jobs Info-Slurm"]),
                        ('compression', True)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v2/metricsbuilder/{partition}'.format(partition='nocona'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_query(self):
        """Test case for query

        Query Metrics for Grafana Plugins
        """
        request_metrics = {
  "app" : "app",
  "maxDataPoints" : 1.4658129805029452,
  "panelId" : 5.962133916683182,
  "timezone" : "timezone",
  "scopedVars" : {
    "__interval" : {
      "text" : "text",
      "value" : "value"
    },
    "startTime" : 5.637376656633329,
    "__interval_ms" : {
      "text" : "text",
      "value" : "value"
    }
  },
  "range" : {
    "from" : "from",
    "to" : "to"
  },
  "aggregation" : "min",
  "targets" : [ {
    "jobs" : [ "jobs", "jobs" ],
    "refId" : "refId",
    "type" : "metrics",
    "users" : [ "users", "users" ],
    "required" : true
  }, {
    "jobs" : [ "jobs", "jobs" ],
    "refId" : "refId",
    "type" : "metrics",
    "users" : [ "users", "users" ],
    "required" : true
  } ],
  "intervalMs" : 6.027456183070403,
  "nodes" : [ "nodes", "nodes" ],
  "partition" : "nocona",
  "timeInfo" : "timeInfo",
  "dashboardId" : 0.8008281904610115,
  "requestId" : "requestId",
  "rangeRaw" : {
    "from" : "from",
    "to" : "to"
  },
  "interval" : "interval"
}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/v2/query',
            method='POST',
            headers=headers,
            data=json.dumps(request_metrics),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_queue(self):
        """Test case for queue

        Get Queue Status of Slurm
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v2/queue',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search(self):
        """Test case for search

        Get Available Metric Names for Grafana Plugins
        """
        query_string = [('partition', 'nocona')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v2/search',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
