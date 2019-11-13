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
BMC metrics are saved in `measurement`("bmc"); host IP address("10.101.1.1", for example) is saved in `tags`; metrics are saved as a structured string in `filed`.

__tags__: host_IP=`<Host IP address>`

__fields__: CPU_Temperature=`<CPU1 Temp>|<CPU2 Temp>`,Inlet_Temperature=`<Inlet Temp>`,CPU_Usage=`<CPU Usage>`,Memory_Usage=`<Memory Usage>`,Fan_Speed=`<Fan_1>|<Fan_2>|<Fan_3>|<Fan_4>`,Node_Power_Usage=`<Power Usage>`


### UGE metrics structure
UGE metrics are saved `measurement`("uge"); job ID("753696", for example) is saved in `tag`; job information is saved as a structured string in `field`.

__tags__: job_ID=`<Job ID>`

__fields__: Job_Info=`<User Name>|<Submit Time>|<Start Time>|<Finish Time>`

