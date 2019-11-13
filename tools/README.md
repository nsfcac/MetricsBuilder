# Convertor
Convert historical data to a newly defined data structure
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
BMC metrics are saved in `measurement`("bmc); host IP address("10.101.1.1", for example) is saved in `tags`; metrics are saved as a structured string in `filed`.

#### tags
```
<Host IP address>
```
#### field
__CPU_Temperature__: `<CPU1 Temp>|<CPU2 Temp>`
__Inlet_Temperature__: `<Inlet Temp>`
__CPU_Usage__:`<CPU Usage>` 
__Memory_Usage__:`<Memory Usage>`
__Fan_Speed__:`<Fan_1>|<Fan_2>|<Fan_3>|<Fan_4>`
__Node_Power_Usage__:`<Power Usage>`


### UGE metrics structure
UGE metrics are saved `measurement`("uge"); job ID("753696", for example) is saved in `tag`; job information is saved as a structured string in `field`.

#### tags
```
<Job ID>
```

#### field
```
<User Name>|<Submit Time>|<Start Time>|<Finish Time>
```

