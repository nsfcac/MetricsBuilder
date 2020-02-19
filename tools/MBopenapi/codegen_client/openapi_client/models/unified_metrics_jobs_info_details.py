# coding: utf-8

"""
    MetricsBuilder API

    An API for accessing High Performance Computing(HPC) system monitoring metrics.  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Contact: jie.li@ttu.edu
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from openapi_client.configuration import Configuration


class UnifiedMetricsJobsInfoDetails(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'user_name': 'str',
        'submit_time': 'int',
        'start_time': 'int',
        'finish_time': 'int'
    }

    attribute_map = {
        'user_name': 'user_name',
        'submit_time': 'submit_time',
        'start_time': 'start_time',
        'finish_time': 'finish_time'
    }

    def __init__(self, user_name=None, submit_time=None, start_time=None, finish_time=None, local_vars_configuration=None):  # noqa: E501
        """UnifiedMetricsJobsInfoDetails - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._user_name = None
        self._submit_time = None
        self._start_time = None
        self._finish_time = None
        self.discriminator = None

        self.user_name = user_name
        self.submit_time = submit_time
        self.start_time = start_time
        self.finish_time = finish_time

    @property
    def user_name(self):
        """Gets the user_name of this UnifiedMetricsJobsInfoDetails.  # noqa: E501


        :return: The user_name of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :rtype: str
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        """Sets the user_name of this UnifiedMetricsJobsInfoDetails.


        :param user_name: The user_name of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and user_name is None:  # noqa: E501
            raise ValueError("Invalid value for `user_name`, must not be `None`")  # noqa: E501

        self._user_name = user_name

    @property
    def submit_time(self):
        """Gets the submit_time of this UnifiedMetricsJobsInfoDetails.  # noqa: E501


        :return: The submit_time of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :rtype: int
        """
        return self._submit_time

    @submit_time.setter
    def submit_time(self, submit_time):
        """Sets the submit_time of this UnifiedMetricsJobsInfoDetails.


        :param submit_time: The submit_time of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and submit_time is None:  # noqa: E501
            raise ValueError("Invalid value for `submit_time`, must not be `None`")  # noqa: E501

        self._submit_time = submit_time

    @property
    def start_time(self):
        """Gets the start_time of this UnifiedMetricsJobsInfoDetails.  # noqa: E501


        :return: The start_time of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :rtype: int
        """
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        """Sets the start_time of this UnifiedMetricsJobsInfoDetails.


        :param start_time: The start_time of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and start_time is None:  # noqa: E501
            raise ValueError("Invalid value for `start_time`, must not be `None`")  # noqa: E501

        self._start_time = start_time

    @property
    def finish_time(self):
        """Gets the finish_time of this UnifiedMetricsJobsInfoDetails.  # noqa: E501


        :return: The finish_time of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :rtype: int
        """
        return self._finish_time

    @finish_time.setter
    def finish_time(self, finish_time):
        """Sets the finish_time of this UnifiedMetricsJobsInfoDetails.


        :param finish_time: The finish_time of this UnifiedMetricsJobsInfoDetails.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and finish_time is None:  # noqa: E501
            raise ValueError("Invalid value for `finish_time`, must not be `None`")  # noqa: E501

        self._finish_time = finish_time

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, UnifiedMetricsJobsInfoDetails):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UnifiedMetricsJobsInfoDetails):
            return True

        return self.to_dict() != other.to_dict()