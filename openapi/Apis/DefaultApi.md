# DefaultApi

All URIs are relative to *http://localhost:5001/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**metricsbuilder**](DefaultApi.md#metricsbuilder) | **GET** /metricsbuilder/{partition} | Query Metrics for Web Applications
[**query**](DefaultApi.md#query) | **POST** /query | Query Metrics for Grafana Plugins
[**queue**](DefaultApi.md#queue) | **GET** /queue | Get Queue Status of Slurm
[**search**](DefaultApi.md#search) | **GET** /search | Get Available Metric Names for Grafana Plugins


<a name="metricsbuilder"></a>
# **metricsbuilder**
> WebResponseMetrics metricsbuilder(partition, start, end, interval, aggregation, nodelist, metrics, compression)

Query Metrics for Web Applications

    Execute queries for metrics, job information, etc.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **partition** | **String**| The target partition of the HPC cluster | [default to nocona] [enum: nocona, quanah]
 **start** | **Date**| Start time of the time range | [optional] [default to null]
 **end** | **Date**| End time of the time range | [optional] [default to null]
 **interval** | **String**| Time interval for aggregating the metrics. | [optional] [default to 5m]
 **aggregation** | **String**| Aggregation function. | [optional] [default to max] [enum: min, max, mean, median]
 **nodelist** | **String**| Target nodes in the cluster. | [optional] [default to 10.101.23.[1-60],10.101.24.[1-60],10.101.25.[1-60],10.101.26.[1-60]]
 **metrics** | [**List**](../Models/String.md)| Selected Metrics. | [optional] [default to [&quot;System Power-iDRAC&quot;,&quot;CPU Power-iDRAC&quot;,&quot;Memory Power-iDRAC&quot;,&quot;NodeJobs Correlation-Slurm&quot;,&quot;Jobs Info-Slurm&quot;]] [enum: System Power-iDRAC, CPU Power-iDRAC, Memory Power-iDRAC, Fan Sensor-iDRAC, Temperature Sensor-iDRAC, CPU Usage-iDRAC, Memory Usage-Slurm, NodeJobs Correlation-Slurm, Jobs Info-Slurm]
 **compression** | **Boolean**| Return compressed data. | [optional] [default to true] [enum: true, false]

### Return type

[**WebResponseMetrics**](../Models/WebResponseMetrics.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="query"></a>
# **query**
> List query(RequestMetrics)

Query Metrics for Grafana Plugins

    Execute queries for metrics, job information, etc.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **RequestMetrics** | [**RequestMetrics**](../Models/RequestMetrics.md)|  |

### Return type

**List**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="queue"></a>
# **queue**
> QueueStatus queue()

Get Queue Status of Slurm

### Parameters
This endpoint does not need any parameter.

### Return type

[**QueueStatus**](../Models/QueueStatus.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="search"></a>
# **search**
> AvailableMetrics search(partition)

Get Available Metric Names for Grafana Plugins

    Return available metrics of iDRAC and Slurm

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **partition** | **String**| Target partition of the HPC cluster | [optional] [default to nocona] [enum: quanah, nocona]

### Return type

[**AvailableMetrics**](../Models/AvailableMetrics.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

