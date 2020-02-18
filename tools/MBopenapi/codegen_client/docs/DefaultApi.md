# openapi_client.DefaultApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_unified_metric**](DefaultApi.md#get_unified_metric) | **GET** /v1/metrics | 


# **get_unified_metric**
> UnifiedMetrics get_unified_metric(start, end, interval, value)



Get **unified metrics** based on speficied start time, end time, time interval and value type. The **start** and **end** time should follow date-time Notation as defined by [RFC 3339, section 5.6](https://tools.ietf.org/html/rfc3339#section-5.6), e.g. `2020-02-12T14:00:00Z`; the time **interval** should follow **duration literals**, which specify a length of time; the **value** type should only be `min`, `max`, `mean`, or `median`.  A duration literal is an integer literal followed immediately (with no spaces) by a duration unit, the units include `s`(second), `m`(minute), `h`(hour), `d`(day), `w`(week). 

### Example

```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Enter a context with an instance of the API client
with openapi_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    start = '2020-02-14T12:00Z' # datetime | start time of time range of the monitoring metrics
end = '2020-02-15T12:00Z' # datetime | end time of time range of the monitoring metrics
interval = '5m' # str | time interval for aggregating the monitoring metrics
value = 'max' # str | value type of the monitoring metrics

    try:
        api_response = api_instance.get_unified_metric(start, end, interval, value)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_unified_metric: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start** | **datetime**| start time of time range of the monitoring metrics | 
 **end** | **datetime**| end time of time range of the monitoring metrics | 
 **interval** | **str**| time interval for aggregating the monitoring metrics | 
 **value** | **str**| value type of the monitoring metrics | 

### Return type

[**UnifiedMetrics**](UnifiedMetrics.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Get unified metrics successfully |  -  |
**0** | Unexpected error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

