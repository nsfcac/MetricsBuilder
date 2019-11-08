# Introduction
MetricsBuilder is a tool that provides a uniform API for analytic tools like HiperViz; it builds aggregated data and returns a csv dataframe back to analytic tools. 
Currently, it is designed specifically for the data collected in The Quanah Cluster in Texas Tech University.
# MetricsBuilder command line parameters
```
$python3 MetricsBuilder.py --help
Options:
    --version           Show version number                             [boolean]
    --startTime, -s     Specify start time of monitoring data           [string]
    --endTime, -e       Specify end time of monitoring data             [string]
    --interval, -i      Specify time interval of monitoring data        [string]
    --valueType, -v     Specify value type, MAX, MIN, MEAN              [string]
    --outfile, -i       Generate a dataframe CSV file for each requests [boolean]
    --help, -h          Show help                                       [boolean]
```