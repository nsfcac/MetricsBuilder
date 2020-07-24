# MetricsBuilder #

### Overview

<p align="center">
<img src="./tools/mechanism.png" alt="mechanism" width="600" />
</p>

Metrics Builder acts as a middleware between the consumers (i.e. analytic clients or tools) and the producers (i.e. the databases). As depcited in the figure, its main workflow is as follows. 

1. It receives requests from consumers. The request includes `time range`, `time interval`, `data type` information, if the returned data is `compressed` or not. User can also specify the target `nodes` and `metrics` interested in (This function is still under optimized, you may find it under the **filter** branch). The time range represents the window of time for the data that consumers want to access. Time intervals and data types are used to aggregate and downsample time series data. 
2. Metrics Builder compare the specified nodes with the nodelist of the cluster being monitored and then generates the appropriate InfluxDB query strings based on valid nodes and the information specified by the consumer, and then sends queries to InfluxDB and waits for responses. 
3. Metrics Builder then processes data returned from InfluxDB, builds the data in JSON format. It decides whether the JSON data need to be compressed or not. The compression option is set to True by default, which significantly reduces the transmission time.

