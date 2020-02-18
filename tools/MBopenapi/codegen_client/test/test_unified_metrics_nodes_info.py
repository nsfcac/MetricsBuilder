# coding: utf-8

"""
    MetricsBuilder API

    An API for accessing High Performance Computing(HPC) system monitoring metrics.  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Contact: jie.li@ttu.edu
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import openapi_client
from openapi_client.models.unified_metrics_nodes_info import UnifiedMetricsNodesInfo  # noqa: E501
from openapi_client.rest import ApiException

class TestUnifiedMetricsNodesInfo(unittest.TestCase):
    """UnifiedMetricsNodesInfo unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test UnifiedMetricsNodesInfo
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = openapi_client.models.unified_metrics_nodes_info.UnifiedMetricsNodesInfo()  # noqa: E501
        if include_optional :
            return UnifiedMetricsNodesInfo(
                id = '0', 
                metrics = openapi_client.models.unified_metrics_nodes_info_metrics.UnifiedMetrics_nodes_info_metrics(
                    memory_usage = [
                        1.337
                        ], 
                    cpu_usage = [
                        1.337
                        ], 
                    power_usage = [
                        1.337
                        ], 
                    fan_speed = [
                        [
                            56
                            ]
                        ], 
                    cpu_int_temp = [
                        [
                            1.337
                            ]
                        ], )
            )
        else :
            return UnifiedMetricsNodesInfo(
                id = '0',
                metrics = openapi_client.models.unified_metrics_nodes_info_metrics.UnifiedMetrics_nodes_info_metrics(
                    memory_usage = [
                        1.337
                        ], 
                    cpu_usage = [
                        1.337
                        ], 
                    power_usage = [
                        1.337
                        ], 
                    fan_speed = [
                        [
                            56
                            ]
                        ], 
                    cpu_int_temp = [
                        [
                            1.337
                            ]
                        ], ),
        )

    def testUnifiedMetricsNodesInfo(self):
        """Test UnifiedMetricsNodesInfo"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
