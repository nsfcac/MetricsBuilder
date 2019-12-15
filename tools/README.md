# FTFinder
Find finish time for each job, it reads HostDetail.csv, analyzes the finish time and writes the results into JobDetail.csv


# MBConvertor
Process historical data and save them into "processed_metrics" database.
## MBConvertor command line parameters
```
$python3 MBConvertor.py --help
Options:
    --version, -v       Show version number                             [boolean]
    --startTime, -s     Specify start time of monitoring data           [string]
    --endTime, -e       Specify end time of monitoring data             [string]
    --interval, -i      Specify time interval of monitoring data        [string]
    --valueType, -t     Specify value type: MAX, MIN, MEAN              [string]
    --help, -h          Show help                                       [boolean]
```
## Data structure
### BMC metrics structure
BMC metrics are saved in `measurement`("hostDetail"); host IP address("10.101.1.1", for example) is saved in `tags`; metrics are saved as a structured string in `fileds`.

__tags__: host_IP=`<Host IP address>`

__fields__: CPU1_Temp=`<CPU1 Temp>`, CPU2_Temp=`<CPU2 Temp>`,Inlet_Temperature=`<Inlet Temp>`,CPU_Usage=`<CPU Usage>`,Memory_Usage=`<Memory Usage>`,Fan_1_Speed=`<Fan_1 Speed>`,Fan_2_Speed=`<Fan_2 Speed>`,Fan_3_Speed=`<Fan_3 Speed>`,Fan_4_Speed=`<Fan_4 Speed>`,Node_Power_Usage=`<Power Usage>`

__timestamp__: timestamp(in Unit Timestamp)



