# MetricsBuilder #

As depcited in the figure,  Metrics Builder acts as a middleware between the consumers (i.e. analytic clients or tools) and the producers (i.e. the databases). Its main workflow is as follows. First, it receives requests from consumers. The request includes time range, time interval and data type information. The time range represents the window of time for the data that consumers want to access. Time intervals and data types are used to aggregate and downsample time series data. Second, Metrics Builder generates the appropriate InfluxDB query strings based on the information specified by the consumer and then sends queries to InfluxDB and waits for responses. Third, Metrics Builder then processes data returned from InfluxDB, builds the data in JSON format, and sends them to the consumer.

![Architecture](https://github.com/nsfcac/MetricsBuilder/blob/master/tools/architecture-1.png?raw=true)