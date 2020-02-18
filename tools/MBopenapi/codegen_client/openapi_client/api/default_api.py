# coding: utf-8

"""
    MetricsBuilder API

    An API for accessing High Performance Computing(HPC) system monitoring metrics.  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Contact: jie.li@ttu.edu
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from openapi_client.api_client import ApiClient
from openapi_client.exceptions import (
    ApiTypeError,
    ApiValueError
)


class DefaultApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def get_unified_metric(self, start, end, interval, value, **kwargs):  # noqa: E501
        """get_unified_metric  # noqa: E501

        Get **unified metrics** based on speficied start time, end time, time interval and value type. The **start** and **end** time should follow date-time Notation as defined by [RFC 3339, section 5.6](https://tools.ietf.org/html/rfc3339#section-5.6), e.g. `2020-02-12T14:00:00Z`; the time **interval** should follow **duration literals**, which specify a length of time; the **value** type should only be `min`, `max`, `mean`, or `median`.  A duration literal is an integer literal followed immediately (with no spaces) by a duration unit, the units include `s`(second), `m`(minute), `h`(hour), `d`(day), `w`(week).   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_unified_metric(start, end, interval, value, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param datetime start: start time of time range of the monitoring metrics (required)
        :param datetime end: end time of time range of the monitoring metrics (required)
        :param str interval: time interval for aggregating the monitoring metrics (required)
        :param str value: value type of the monitoring metrics (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: UnifiedMetrics
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.get_unified_metric_with_http_info(start, end, interval, value, **kwargs)  # noqa: E501

    def get_unified_metric_with_http_info(self, start, end, interval, value, **kwargs):  # noqa: E501
        """get_unified_metric  # noqa: E501

        Get **unified metrics** based on speficied start time, end time, time interval and value type. The **start** and **end** time should follow date-time Notation as defined by [RFC 3339, section 5.6](https://tools.ietf.org/html/rfc3339#section-5.6), e.g. `2020-02-12T14:00:00Z`; the time **interval** should follow **duration literals**, which specify a length of time; the **value** type should only be `min`, `max`, `mean`, or `median`.  A duration literal is an integer literal followed immediately (with no spaces) by a duration unit, the units include `s`(second), `m`(minute), `h`(hour), `d`(day), `w`(week).   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_unified_metric_with_http_info(start, end, interval, value, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param datetime start: start time of time range of the monitoring metrics (required)
        :param datetime end: end time of time range of the monitoring metrics (required)
        :param str interval: time interval for aggregating the monitoring metrics (required)
        :param str value: value type of the monitoring metrics (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(UnifiedMetrics, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = ['start', 'end', 'interval', 'value']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_unified_metric" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'start' is set
        if self.api_client.client_side_validation and ('start' not in local_var_params or  # noqa: E501
                                                        local_var_params['start'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `start` when calling `get_unified_metric`")  # noqa: E501
        # verify the required parameter 'end' is set
        if self.api_client.client_side_validation and ('end' not in local_var_params or  # noqa: E501
                                                        local_var_params['end'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `end` when calling `get_unified_metric`")  # noqa: E501
        # verify the required parameter 'interval' is set
        if self.api_client.client_side_validation and ('interval' not in local_var_params or  # noqa: E501
                                                        local_var_params['interval'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `interval` when calling `get_unified_metric`")  # noqa: E501
        # verify the required parameter 'value' is set
        if self.api_client.client_side_validation and ('value' not in local_var_params or  # noqa: E501
                                                        local_var_params['value'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `value` when calling `get_unified_metric`")  # noqa: E501

        if self.api_client.client_side_validation and 'interval' in local_var_params and not re.search(r'^[1-9][0-9]*[s, m, h, d, w]$', local_var_params['interval']):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `interval` when calling `get_unified_metric`, must conform to the pattern `/^[1-9][0-9]*[s, m, h, d, w]$/`")  # noqa: E501
        collection_formats = {}

        path_params = {}

        query_params = []
        if 'start' in local_var_params and local_var_params['start'] is not None:  # noqa: E501
            query_params.append(('start', local_var_params['start']))  # noqa: E501
        if 'end' in local_var_params and local_var_params['end'] is not None:  # noqa: E501
            query_params.append(('end', local_var_params['end']))  # noqa: E501
        if 'interval' in local_var_params and local_var_params['interval'] is not None:  # noqa: E501
            query_params.append(('interval', local_var_params['interval']))  # noqa: E501
        if 'value' in local_var_params and local_var_params['value'] is not None:  # noqa: E501
            query_params.append(('value', local_var_params['value']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/v1/metrics', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='UnifiedMetrics',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)
