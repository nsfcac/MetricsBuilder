# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.unified_metrics_jobs_info_details import UnifiedMetricsJobsInfoDetails
from openapi_server import util

from openapi_server.models.unified_metrics_jobs_info_details import UnifiedMetricsJobsInfoDetails  # noqa: E501

class UnifiedMetricsJobsInfo(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, details=None):  # noqa: E501
        """UnifiedMetricsJobsInfo - a model defined in OpenAPI

        :param id: The id of this UnifiedMetricsJobsInfo.  # noqa: E501
        :type id: str
        :param details: The details of this UnifiedMetricsJobsInfo.  # noqa: E501
        :type details: UnifiedMetricsJobsInfoDetails
        """
        self.openapi_types = {
            'id': str,
            'details': UnifiedMetricsJobsInfoDetails
        }

        self.attribute_map = {
            'id': 'id',
            'details': 'details'
        }

        self._id = id
        self._details = details

    @classmethod
    def from_dict(cls, dikt) -> 'UnifiedMetricsJobsInfo':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The UnifiedMetrics_jobs_info of this UnifiedMetricsJobsInfo.  # noqa: E501
        :rtype: UnifiedMetricsJobsInfo
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this UnifiedMetricsJobsInfo.


        :return: The id of this UnifiedMetricsJobsInfo.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this UnifiedMetricsJobsInfo.


        :param id: The id of this UnifiedMetricsJobsInfo.
        :type id: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def details(self):
        """Gets the details of this UnifiedMetricsJobsInfo.


        :return: The details of this UnifiedMetricsJobsInfo.
        :rtype: UnifiedMetricsJobsInfoDetails
        """
        return self._details

    @details.setter
    def details(self, details):
        """Sets the details of this UnifiedMetricsJobsInfo.


        :param details: The details of this UnifiedMetricsJobsInfo.
        :type details: UnifiedMetricsJobsInfoDetails
        """
        if details is None:
            raise ValueError("Invalid value for `details`, must not be `None`")  # noqa: E501

        self._details = details
