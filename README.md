## Introduction
MetricsBuilder is a tool that provides a uniform API for analytic clients like [HiperJobViz](https://idatavisualizationlab.github.io/HPCC/HiperJobViz/index.html); it builds aggregated data and returns dataframe CSV files back to clients. 

Currently, it is designed specifically for the data collected in The Quanah Cluster in [High Performance Comoputing Center](http://www.depts.ttu.edu/hpcc/) in Texas Tech University.
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

To fetch processed data from influxDB based on time range, time interval and data type:
```
$python3 MetricsBuilder.py -s 2019-04-20T00:00:00Z -e 2019-04-26T23:59:59Z -i 5m -t MEAN -o 
```

The output files will be saved in folder "CSV". 

`JobDetail_2019-04-20T00:00:00Z_2019-04-26T23:59:59Z_5m.csv` contains jobs information about `submit time`, `start time` and `user name`.

`HostDetail_2019-04-20T00:00:00Z_2019-04-26T23:59:59Z_5m.csv` contains hosts information for each timestamp, these information includes `CPU Temperature`, `Inlet Temperature`, `CPU Usage`, `Memory Usage`, `Fan Speed`, and `Node Power Usage`.

## Dataframe samples
#### Job details dataframe

|     JobID    |          startTime           |           submitTime         |    user    |
|--------------|------------------------------|------------------------------|------------|
|    755371    | Sat Apr 20 21:40:19 CDT 2019 | Sat Apr 20 21:39:12 CDT 2019 |  akitazum  |
|    753687    | Thu Apr 18 05:02:59 CDT 2019 | Thu Apr 16 23:37:34 CDT 2019 |  rafiisla  |
|    753696    | Thu Apr 18 07:41:54 CDT 2019 | Wed Apr 17 08:12:49 CDT 2019 |  jieyao    |

#### Host details dataframe

|      TimeStamp       | 10.101.4.10-Jobs | 10.101.4.10-Fan_Speed | 10.101.4.10-CPU_Usage |
|----------------------|------------------|-----------------------|-----------------------|
| 2019-04-20T15:20:00Z |     [754619]     |         9275.0        |          0.5          |
| 2019-04-20T15:25:00Z |     [754619]     |         9286.67       |          0.49         |
| 2019-04-20T15:30:00Z |     [754619]     |         9310.0        |          0.49         |

## Files/folders
#### hostlist 
a file contains IP addresses of all monitored nodes
#### CSV
Where generated CSV files are saved
#### influxDB
Where samples of influxDB points are saved
#### BMC
Where samples of BMC metrics are saved
#### UGE
Where samples of UGE metrics are saved