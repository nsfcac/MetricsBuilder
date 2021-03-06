## Introduction
MetricsBuilder is a tool that provides a uniform API for analytic clients like [HiperJobViz](https://idatavisualizationlab.github.io/HPCC/HiperJobViz/index.html); it builds aggregated data and returns dataframe CSV files back to clients. 

Currently, it is designed specifically for the data collected in the Quanah Cluster in [High Performance Comoputing Center](http://www.depts.ttu.edu/hpcc/) in Texas Tech University.
## MetricsBuilder command line parameters
```
$python3 MetricsBuilder.py --help
Options:
    --version, -v       Show version number                             [boolean]
    --startTime, -s     Specify start time of monitoring data           [string]
    --endTime, -e       Specify end time of monitoring data             [string]
    --interval, -i      Specify time interval of monitoring data        [string]
    --dataType, -t      Specify value type, MAX, MIN, MEAN              [string]
    --outfile, -o       Generate a dataframe CSV file for each requests [boolean]
    --help, -h          Show help                                       [boolean]
```

To fetch data from influxDB based on time range, time interval and data type:
```
$python3 MetricsBuilder.py -s 2019-04-20T00:00:00Z -e 2019-04-26T23:59:59Z -i 5m -t MEAN -o 
```

The output files will be saved in folder "CSV". 

`JobDetail_2019-04-20T00:00:00Z_2019-04-26T23:59:59Z_5m.csv` contains jobs information about `submit time`, `start time` and `user name`.

`HostDetail_2019-04-20T00:00:00Z_2019-04-26T23:59:59Z_5m.csv` contains hosts information of each timestamp, these information includes `CPU Temperature`, `Inlet Temperature`, `CPU Usage`, `Memory Usage`, `Fan Speed`, and `Node Power Usage`.

## Dataframe samples
#### Job details dataframe

|     JobID    |          startTime           |           submitTime         |    user    |
|--------------|------------------------------|------------------------------|------------|
|    755371    | Sat Apr 20 21:40:19 CDT 2019 | Sat Apr 20 21:39:12 CDT 2019 |  akitazum  |
|    753687    | Thu Apr 18 05:02:59 CDT 2019 | Thu Apr 16 23:37:34 CDT 2019 |  rafiisla  |
|    753696    | Thu Apr 18 07:41:54 CDT 2019 | Wed Apr 17 08:12:49 CDT 2019 |  jieyao    |

#### Host details dataframe

|      TimeStamp       | 10.101.4.10-Jobs | 10.101.4.10-CPU_Usage | 10.101.4.10-Memory_Usage |
|----------------------|------------------|-----------------------|--------------------------|
| 2019-04-20T15:20:00Z |     [754619]     |         0.5           |          134.49          |
| 2019-04-20T15:25:00Z |     [754619]     |         0.49          |          135.64          |
| 2019-04-20T15:30:00Z |     [754619]     |         0.49          |          137.38          |
| 2019-04-20T15:35:00Z |     [754634]     |         0.68          |          160.99          |

## Files/folders
__hostlist__ : a file contains IP addresses of all monitored nodes

__CSV__: generated CSV files

__influxDB__: samples of influxDB points

__BMC__: samples of BMC metrics

__UGE__: samples of UGE metrics

__tools__: data structure convertor, profiling tools etc.

## Tools
#### Convertor
This tool is developed to convert historical data to a newly defined structure, which is used to compare efficiency of differenty database designs.