# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server import util


class InlineResponseDefault(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, name=None, message=None):  # noqa: E501
        """InlineResponseDefault - a model defined in OpenAPI

        :param name: The name of this InlineResponseDefault.  # noqa: E501
        :type name: str
        :param message: The message of this InlineResponseDefault.  # noqa: E501
        :type message: str
        """
        self.openapi_types = {
            'name': str,
            'message': str
        }

        self.attribute_map = {
            'name': 'name',
            'message': 'message'
        }

        self._name = name
        self._message = message

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponseDefault':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_default of this InlineResponseDefault.  # noqa: E501
        :rtype: InlineResponseDefault
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self):
        """Gets the name of this InlineResponseDefault.


        :return: The name of this InlineResponseDefault.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this InlineResponseDefault.


        :param name: The name of this InlineResponseDefault.
        :type name: str
        """

        self._name = name

    @property
    def message(self):
        """Gets the message of this InlineResponseDefault.


        :return: The message of this InlineResponseDefault.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this InlineResponseDefault.


        :param message: The message of this InlineResponseDefault.
        :type message: str
        """

        self._message = message
