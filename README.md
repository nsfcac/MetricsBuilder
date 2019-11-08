## Introduction
MetricsBuilder is a tool that provides a uniform API for analytic clients like [HiperJobViz](https://idatavisualizationlab.github.io/HPCC/HiperJobViz/index.html); it builds aggregated data and returns a dataframe CSV file back to clients. 

Currently, it is designed specifically for the data collected in The Quanah Cluster in [High Performance Comoputing Center](http://www.depts.ttu.edu/hpcc/) in Texas Tech University.
## MetricsBuilder command line parameters
```
$python3 MetricsBuilder.py --help
Options:
    --version, -V       Show version number                             [boolean]
    --startTime, -S     Specify start time of monitoring data           [string]
    --endTime, -E       Specify end time of monitoring data             [string]
    --interval, -I      Specify time interval of monitoring data        [string]
    --dataType, -D      Specify value type, MAX, MIN, MEAN              [string]
    --outfile, -O       Generate a dataframe CSV file for each requests [boolean]
    --help, -H          Show help                                       [boolean]
```

To create a csv file based on the time range, time interval and data type:
```
$python3 MetricsBuilder3.py -S 2019-04-20T00:00:00Z -E 2019-04-26T23:59:59Z -I 5m -D MEAN -O 
```

The output file will be saved in folder "csv", named with "2019-04-20T00:00:00Z_2019-04-27T00:00:00Z_5m.csv"

## Files/folders description
#### hostlist
A file contains IP addresses of all the monitored nodes
#### csv
A folder where generated csv files are saved
#### influxDB
A folder where samples of influxDB points are saved
#### BMC
A folder where samples of BMC metrics are saved
#### UGE
A folder where samples of UGE metrics are saved

## To do list
1. Evaluate efficiency of different database design

    *Build a tool that converts historical data to newly designed data structure
2. Configuration file

    *Users can set up configuration of MetricsBuilder in the configuration file, e.g. parameters for connecting to database, metrics needed by analytic tools etc.
3. Optimize the algorithm of the processing function