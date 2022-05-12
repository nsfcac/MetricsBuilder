# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.slurm_data import SlurmData
from openapi_server import util

from openapi_server.models.slurm_data import SlurmData  # noqa: E501

class QueueStatus(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, timestamp=None, queue_status=None):  # noqa: E501
        """QueueStatus - a model defined in OpenAPI

        :param timestamp: The timestamp of this QueueStatus.  # noqa: E501
        :type timestamp: float
        :param queue_status: The queue_status of this QueueStatus.  # noqa: E501
        :type queue_status: List[SlurmData]
        """
        self.openapi_types = {
            'timestamp': float,
            'queue_status': List[SlurmData]
        }

        self.attribute_map = {
            'timestamp': 'timestamp',
            'queue_status': 'queue_status'
        }

        self._timestamp = timestamp
        self._queue_status = queue_status

    @classmethod
    def from_dict(cls, dikt) -> 'QueueStatus':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The QueueStatus of this QueueStatus.  # noqa: E501
        :rtype: QueueStatus
        """
        return util.deserialize_model(dikt, cls)

    @property
    def timestamp(self):
        """Gets the timestamp of this QueueStatus.


        :return: The timestamp of this QueueStatus.
        :rtype: float
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this QueueStatus.


        :param timestamp: The timestamp of this QueueStatus.
        :type timestamp: float
        """

        self._timestamp = timestamp

    @property
    def queue_status(self):
        """Gets the queue_status of this QueueStatus.


        :return: The queue_status of this QueueStatus.
        :rtype: List[SlurmData]
        """
        return self._queue_status

    @queue_status.setter
    def queue_status(self, queue_status):
        """Sets the queue_status of this QueueStatus.


        :param queue_status: The queue_status of this QueueStatus.
        :type queue_status: List[SlurmData]
        """

        self._queue_status = queue_status
