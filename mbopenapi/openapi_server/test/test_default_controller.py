# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.error_message import ErrorMessage  # noqa: E501
from openapi_server.models.unified_metrics import UnifiedMetrics  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_get_unified_metric(self):
        """Test case for get_unified_metric

        
        """
        query_string = [('start', 2020-02-14T12:00-05:00),
                        ('end', 2020-02-14T18:00-05:00),
                        ('interval', 5m),
                        ('value', max),
                        ('compress', true)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/v1/metrics',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
