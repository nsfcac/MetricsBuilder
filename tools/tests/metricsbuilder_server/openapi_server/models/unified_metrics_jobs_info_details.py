# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server import util


class UnifiedMetricsJobsInfoDetails(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, user_name=None, submit_time=None, start_time=None, finish_time=None, array_job=None):  # noqa: E501
        """UnifiedMetricsJobsInfoDetails - a model defined in OpenAPI

        :param user_name: The user_name of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :type user_name: str
        :param submit_time: The submit_time of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :type submit_time: int
        :param start_time: The start_time of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :type start_time: object
        :param finish_time: The finish_time of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :type finish_time: object
        :param array_job: The array_job of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :type array_job: bool
        """
        self.openapi_types = {
            'user_name': str,
            'submit_time': int,
            'start_time': object,
            'finish_time': object,
            'array_job': bool
        }

        self.attribute_map = {
            'user_name': 'user_name',
            'submit_time': 'submit_time',
            'start_time': 'start_time',
            'finish_time': 'finish_time',
            'array_job': 'array_job'
        }

        self._user_name = user_name
        self._submit_time = submit_time
        self._start_time = start_time
        self._finish_time = finish_time
        self._array_job = array_job

    @classmethod
    def from_dict(cls, dikt) -> 'UnifiedMetricsJobsInfoDetails':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The UnifiedMetrics_jobs_info_details of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :rtype: UnifiedMetricsJobsInfoDetails
        """
        return util.deserialize_model(dikt, cls)

    @property
    def user_name(self):
        """Gets the user_name of this UnifiedMetricsJobsInfoDetails.


        :return: The user_name of this UnifiedMetricsJobsInfoDetails.
        :rtype: str
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        """Sets the user_name of this UnifiedMetricsJobsInfoDetails.


        :param user_name: The user_name of this UnifiedMetricsJobsInfoDetails.
        :type user_name: str
        """
        if user_name is None:
            raise ValueError("Invalid value for `user_name`, must not be `None`")  # noqa: E501

        self._user_name = user_name

    @property
    def submit_time(self):
        """Gets the submit_time of this UnifiedMetricsJobsInfoDetails.


        :return: The submit_time of this UnifiedMetricsJobsInfoDetails.
        :rtype: int
        """
        return self._submit_time

    @submit_time.setter
    def submit_time(self, submit_time):
        """Sets the submit_time of this UnifiedMetricsJobsInfoDetails.


        :param submit_time: The submit_time of this UnifiedMetricsJobsInfoDetails.
        :type submit_time: int
        """
        if submit_time is None:
            raise ValueError("Invalid value for `submit_time`, must not be `None`")  # noqa: E501

        self._submit_time = submit_time

    @property
    def start_time(self):
        """Gets the start_time of this UnifiedMetricsJobsInfoDetails.


        :return: The start_time of this UnifiedMetricsJobsInfoDetails.
        :rtype: object
        """
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        """Sets the start_time of this UnifiedMetricsJobsInfoDetails.


        :param start_time: The start_time of this UnifiedMetricsJobsInfoDetails.
        :type start_time: object
        """
        if start_time is None:
            raise ValueError("Invalid value for `start_time`, must not be `None`")  # noqa: E501

        self._start_time = start_time

    @property
    def finish_time(self):
        """Gets the finish_time of this UnifiedMetricsJobsInfoDetails.


        :return: The finish_time of this UnifiedMetricsJobsInfoDetails.
        :rtype: object
        """
        return self._finish_time

    @finish_time.setter
    def finish_time(self, finish_time):
        """Sets the finish_time of this UnifiedMetricsJobsInfoDetails.


        :param finish_time: The finish_time of this UnifiedMetricsJobsInfoDetails.
        :type finish_time: object
        """
        if finish_time is None:
            raise ValueError("Invalid value for `finish_time`, must not be `None`")  # noqa: E501

        self._finish_time = finish_time

    @property
    def array_job(self):
        """Gets the array_job of this UnifiedMetricsJobsInfoDetails.


        :return: The array_job of this UnifiedMetricsJobsInfoDetails.
        :rtype: bool
        """
        return self._array_job

    @array_job.setter
    def array_job(self, array_job):
        """Sets the array_job of this UnifiedMetricsJobsInfoDetails.


        :param array_job: The array_job of this UnifiedMetricsJobsInfoDetails.
        :type array_job: bool
        """
        if array_job is None:
            raise ValueError("Invalid value for `array_job`, must not be `None`")  # noqa: E501

        self._array_job = array_job
