# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server import util


class UnifiedMetricsNodesInfoMetrics(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, memory_usage=None, cpu_usage=None, power_usage=None, fan_speed=None, cpu_inl_temp=None):  # noqa: E501
        """UnifiedMetricsNodesInfoMetrics - a model defined in OpenAPI

        :param memory_usage: The memory_usage of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :type memory_usage: List[float]
        :param cpu_usage: The cpu_usage of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :type cpu_usage: List[float]
        :param power_usage: The power_usage of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :type power_usage: List[float]
        :param fan_speed: The fan_speed of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :type fan_speed: List[List[int]]
        :param cpu_inl_temp: The cpu_inl_temp of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :type cpu_inl_temp: List[List[float]]
        """
        self.openapi_types = {
            'memory_usage': List[float],
            'cpu_usage': List[float],
            'power_usage': List[float],
            'fan_speed': List[List[int]],
            'cpu_inl_temp': List[List[float]]
        }

        self.attribute_map = {
            'memory_usage': 'memory_usage',
            'cpu_usage': 'cpu_usage',
            'power_usage': 'power_usage',
            'fan_speed': 'fan_speed',
            'cpu_inl_temp': 'cpu_inl_temp'
        }

        self._memory_usage = memory_usage
        self._cpu_usage = cpu_usage
        self._power_usage = power_usage
        self._fan_speed = fan_speed
        self._cpu_inl_temp = cpu_inl_temp

    @classmethod
    def from_dict(cls, dikt) -> 'UnifiedMetricsNodesInfoMetrics':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The UnifiedMetrics_nodes_info_metrics of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :rtype: UnifiedMetricsNodesInfoMetrics
        """
        return util.deserialize_model(dikt, cls)

    @property
    def memory_usage(self):
        """Gets the memory_usage of this UnifiedMetricsNodesInfoMetrics.


        :return: The memory_usage of this UnifiedMetricsNodesInfoMetrics.
        :rtype: List[float]
        """
        return self._memory_usage

    @memory_usage.setter
    def memory_usage(self, memory_usage):
        """Sets the memory_usage of this UnifiedMetricsNodesInfoMetrics.


        :param memory_usage: The memory_usage of this UnifiedMetricsNodesInfoMetrics.
        :type memory_usage: List[float]
        """
        if memory_usage is None:
            raise ValueError("Invalid value for `memory_usage`, must not be `None`")  # noqa: E501

        self._memory_usage = memory_usage

    @property
    def cpu_usage(self):
        """Gets the cpu_usage of this UnifiedMetricsNodesInfoMetrics.


        :return: The cpu_usage of this UnifiedMetricsNodesInfoMetrics.
        :rtype: List[float]
        """
        return self._cpu_usage

    @cpu_usage.setter
    def cpu_usage(self, cpu_usage):
        """Sets the cpu_usage of this UnifiedMetricsNodesInfoMetrics.


        :param cpu_usage: The cpu_usage of this UnifiedMetricsNodesInfoMetrics.
        :type cpu_usage: List[float]
        """
        if cpu_usage is None:
            raise ValueError("Invalid value for `cpu_usage`, must not be `None`")  # noqa: E501

        self._cpu_usage = cpu_usage

    @property
    def power_usage(self):
        """Gets the power_usage of this UnifiedMetricsNodesInfoMetrics.


        :return: The power_usage of this UnifiedMetricsNodesInfoMetrics.
        :rtype: List[float]
        """
        return self._power_usage

    @power_usage.setter
    def power_usage(self, power_usage):
        """Sets the power_usage of this UnifiedMetricsNodesInfoMetrics.


        :param power_usage: The power_usage of this UnifiedMetricsNodesInfoMetrics.
        :type power_usage: List[float]
        """
        if power_usage is None:
            raise ValueError("Invalid value for `power_usage`, must not be `None`")  # noqa: E501

        self._power_usage = power_usage

    @property
    def fan_speed(self):
        """Gets the fan_speed of this UnifiedMetricsNodesInfoMetrics.


        :return: The fan_speed of this UnifiedMetricsNodesInfoMetrics.
        :rtype: List[List[int]]
        """
        return self._fan_speed

    @fan_speed.setter
    def fan_speed(self, fan_speed):
        """Sets the fan_speed of this UnifiedMetricsNodesInfoMetrics.


        :param fan_speed: The fan_speed of this UnifiedMetricsNodesInfoMetrics.
        :type fan_speed: List[List[int]]
        """
        if fan_speed is None:
            raise ValueError("Invalid value for `fan_speed`, must not be `None`")  # noqa: E501

        self._fan_speed = fan_speed

    @property
    def cpu_inl_temp(self):
        """Gets the cpu_inl_temp of this UnifiedMetricsNodesInfoMetrics.


        :return: The cpu_inl_temp of this UnifiedMetricsNodesInfoMetrics.
        :rtype: List[List[float]]
        """
        return self._cpu_inl_temp

    @cpu_inl_temp.setter
    def cpu_inl_temp(self, cpu_inl_temp):
        """Sets the cpu_inl_temp of this UnifiedMetricsNodesInfoMetrics.


        :param cpu_inl_temp: The cpu_inl_temp of this UnifiedMetricsNodesInfoMetrics.
        :type cpu_inl_temp: List[List[float]]
        """
        if cpu_inl_temp is None:
            raise ValueError("Invalid value for `cpu_inl_temp`, must not be `None`")  # noqa: E501

        self._cpu_inl_temp = cpu_inl_temp