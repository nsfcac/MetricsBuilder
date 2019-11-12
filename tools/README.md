# Convertor
Convert historical data to a newly defined structure
## Convertor command line parameters
```
$python3 Convertor.py --help
Options:
    --version, -v       Show version number                             [boolean]
    --startTime, -s     Specify start time of monitoring data           [string]
    --endTime, -e       Specify end time of monitoring data             [string]
    --database, -d      Specify newly added database name               [string]
    --help, -h          Show help                                       [boolean]
```
## Data structure
### BMC metrics structure 
All BMC metrics are saved in host level. Each host has its own `measurement`("10.101.1.1", for example). Metrics are saved as a structured string in the same `field`. We do not use key-value `tags`.

__field string__
```
<CPU1 Temp>|<CPU2 Temp>|<Inlet Temp>|<CPU Usage>|<Memory Usage>|<FAN1 Speed>|<FAN2 Speed>|<FAN3 Speed>|<FAN4 Speed>|<Power Usage>
```
### UGE metrics structure
UGE metrics are saved in cluster level. We only have one `measurement`("uge"), and use both `tag` and `field`.

__tag string__
```
<Job ID>
```

__field string__
```
<User Name>|<Submit Time>|<Start Time>|<Finish Time>
```

