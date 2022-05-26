# Documentation for MetricsBuilder API

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *http://localhost:5001/v2*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*DefaultApi* | [**metricsbuilder**](Apis/DefaultApi.md#metricsbuilder) | **GET** /metricsbuilder/{partition} | Query Metrics for Web Applications
*DefaultApi* | [**query**](Apis/DefaultApi.md#query) | **POST** /query | Query Metrics for Grafana Plugins
*DefaultApi* | [**queue**](Apis/DefaultApi.md#queue) | **GET** /queue | Get Queue Status of Slurm
*DefaultApi* | [**search**](Apis/DefaultApi.md#search) | **GET** /search | Get Available Metric Names for Grafana Plugins


<a name="documentation-for-models"></a>
## Documentation for Models

 - [AvailableMetrics](./Models/AvailableMetrics.md)
 - [Interval](./Models/Interval.md)
 - [MetricFqdd](./Models/MetricFqdd.md)
 - [MetricFqdd_children](./Models/MetricFqdd_children.md)
 - [MetricSource](./Models/MetricSource.md)
 - [QueueStatus](./Models/QueueStatus.md)
 - [RequestMetrics](./Models/RequestMetrics.md)
 - [RequestMetrics_scopedVars](./Models/RequestMetrics_scopedVars.md)
 - [RequestMetrics_targets](./Models/RequestMetrics_targets.md)
 - [SlurmData](./Models/SlurmData.md)
 - [TimeRange](./Models/TimeRange.md)
 - [WebResponseMetrics](./Models/WebResponseMetrics.md)
 - [inline_response_default](./Models/inline_response_default.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

All endpoints do not require authorization.
