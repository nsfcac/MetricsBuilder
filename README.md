# Metrics Builder API

## Overview
Metrics Builder API acts as a middleware between the consumer (i.e. analytic clients or tools) and producers (i.e. the database InfluxDB). It receives requests from consumers and generates the appropriate InfluxDB query strings. Metrics Builder then processes data returned from InfluxDB, builds the data in JSON format, and sends them to the consumer. 

The Metrics Builder service in this implementation is specifically designed for accessing the monitoring data collected from **the Quanah Cluster** at Texas Tech University’s High Performance Computing
Center (HPCC). To test its features, please visite the [Metrics Builder API](https://redfish.hpcc.ttu.edu:8080/ui/). Please DISABLE WEB SECURITY in your browser(e.g chrome) for successifully loading the webpage.

Metrics Builder highly relies on the understanding of the precise database schemas. The schemas we are using can be found in `schema.yml` under the folder, `tools`. Thus Metrics Builder **CANNOT** be used directly in your project. However, it may provide a reference for your customized implementation.

Our experience with the deployment on the Quanah cluster have shown that **well-designed schema** can reduce the amount of data collected without losing informative metrics and uing **high-speed storage**, **concurrent processing**, and **transmitting compressed data** reduce data retrieval time significantly and enable near real-time analysis and visualization. 

Metrics Builder API is a OpenAPI-enabled Flask server that is generated by the [OpenAPI Generator](https://openapi-generator.tech) project.

## OpenAPI specification
YAML file `openapi.yaml` is the OpenAPI specification of this API service. It comprises 5 parts: `openapi`, `info`, `servers`, `components`, and `paths`.

`openapi` specifies the version numberof OpenAPI specification this document uses. `info` is the metadata of the API service. `servers` specifies connectivity information of the API service. 

`components` are a collection of resuable schemas throughout the API service. In this implementation, we use two schemas, `UnifiedMetrics` and `ErrorMessage`. `UnifiedMetrics` includes `nodes_info`, `jobs_info`, and `time_stamp` fields, representing **node-related metrics**, **job-related metrics**, and **epoch time stamps**, respectively.

`paths` are the reources and method supported by the API service. We only have `get` method in the API.

## The server-side stub
OpenAPI generator generates server-side code by:

```
$ openapi-generator generate -i openapi.yaml -g python-flask -o mbopenapi
```

OpenAPI generator uses `openapi.yaml` as the input, prepares server-side stub using the flask framework in Python, saves the generated code in folder, `mbopenapi`. 

## Metrics Builder functions
All functions (except for auto-generated Classes/functions) can be found under directory, `mbopenapi/openapi_server/controllers`
1. **main function**\
Metrics Builder main function is implemented in `default_controller.py`, in which we check sanity of requests, concurrently calls querying and processing functions, and compresses the processed data.
2. **query_db.py**\
Queries node-level and job-level metrics. The functions in this file generate Influx query languages based on the speficied arguments and call InfluxDB python client to fetch data.
3. **process_data.py**\
Processes and agregates the data returned from InfluxDB.
4. **gen_timestamp.py**\
Generates timestamps based on user-speficied arguments.
5. **parse_config.py**\
Parses configuration file, `config.yml`.
6. **config.yml**\
Saves configuration for accessing InfluxDB.
7. **hostlist**\
Saves nodes information of the Quanah cluster.




