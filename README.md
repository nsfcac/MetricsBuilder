## Introduction
MetricsBuilder is a tool that provides a uniform API for analytic clients like [HiperJobViz](https://idatavisualizationlab.github.io/HPCC/HiperJobViz/index.html); it builds aggregated data and returns a dataframe CSV file back to clients. 

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

To create a csv file based on time range, time interval and data type:
```
$python3 MetricsBuilder.py -s 2019-04-20T00:00:00Z -e 2019-04-26T23:59:59Z -i 5m -t MEAN -o 
```

The output file will be saved in folder "CSV", named with "2019-04-20T00:00:00Z_2019-04-27T00:00:00Z_5m.csv"

## Files/folders
#### hostlist
A file contains IP addresses of all the monitored nodes
#### CSV
A folder where generated CSV files are saved
#### influxDB
A folder where samples of influxDB points are saved
#### BMC
A folder where samples of BMC metrics are saved
#### UGE
A folder where samples of UGE metrics are saved