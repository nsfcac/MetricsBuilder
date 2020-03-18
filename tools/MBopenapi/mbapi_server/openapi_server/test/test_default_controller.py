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

    def test_get_metrics(self):
        """Test case for get_metrics

        
        """
        query_string = [('start', 2020-02-14T12:00Z),
                        ('end', 2020-02-15T12:00Z),
                        ('interval', 5m),
                        ('value', max)]
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
