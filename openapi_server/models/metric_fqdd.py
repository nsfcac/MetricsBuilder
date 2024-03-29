# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.metric_fqdd_children import MetricFqddChildren
from openapi_server import util

from openapi_server.models.metric_fqdd_children import MetricFqddChildren  # noqa: E501

class MetricFqdd(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, name=None, children=None):  # noqa: E501
        """MetricFqdd - a model defined in OpenAPI

        :param name: The name of this MetricFqdd.  # noqa: E501
        :type name: str
        :param children: The children of this MetricFqdd.  # noqa: E501
        :type children: MetricFqddChildren
        """
        self.openapi_types = {
            'name': str,
            'children': MetricFqddChildren
        }

        self.attribute_map = {
            'name': 'name',
            'children': 'children'
        }

        self._name = name
        self._children = children

    @classmethod
    def from_dict(cls, dikt) -> 'MetricFqdd':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The MetricFqdd of this MetricFqdd.  # noqa: E501
        :rtype: MetricFqdd
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self):
        """Gets the name of this MetricFqdd.


        :return: The name of this MetricFqdd.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this MetricFqdd.


        :param name: The name of this MetricFqdd.
        :type name: str
        """

        self._name = name

    @property
    def children(self):
        """Gets the children of this MetricFqdd.


        :return: The children of this MetricFqdd.
        :rtype: MetricFqddChildren
        """
        return self._children

    @children.setter
    def children(self, children):
        """Sets the children of this MetricFqdd.


        :param children: The children of this MetricFqdd.
        :type children: MetricFqddChildren
        """

        self._children = children
