# MBConvertor
Convert historical data according to the schema and save them into "processed_metrics" database.
## Schema
### BMC metrics 
Measurement of BMC metrics is followed by Redfish entry point name, e.g. *CPU1_Temp* is get from`/redfish/v1/Chassis/System.Embedded.1/Thermal`, thus *CPU1_Temp* will be saved into measurement `Thermal`. Tag keys of BMC metrics are constrained to __Label__ and __NodeId__; By indexing these two tags, we can get the only reading value, which is saved into field key __Reading__.

Dummy data points in `Thermal` measurement:
```
measurement: Thermal         
time: 1583792296             
tags: 
    Label: "CPU1Temp"
    NodeId: "101.10.1.1"
fields:
    Reading: 46.00

measurement: Thermal         
time: 1583792296             
tags: 
    Label: "FAN_1"
    NodeId: "101.10.1.1"
fields:
    Reading: 4500
```

Dummy data points in "Power" measurement:
```
measurement: Power           
time: 1583792296             
tags: 
    Label: "NodePower"
    NodeId: "101.10.1.1"
fields:
    Reading: 277
```
### UGE metrics 
Resource usage (CPU usage and Memory usage) related metrics from UGE are saved into measurement `UGE`; Tag key and field key names follow the BMC metrics, in which only __Label__, __NodeId__ and __Reading__ are kept. 

Dummy data points in `UGE` measurement:
```
measurement: UGE
time: 1583792296             
tags: 
    Label: "CPUUsage"
    NodeId: "101.10.1.1"
fields:
    Reading: 0.5

measurement: UGE            
time: 1583792296             
tags: 
    Label: "MemUsage"
    NodeId: "101.10.1.1"
fields:
    Reading: 0.5
```

Node-Jobs relationship is saved in `NodeJobs` measurement. Tag key is __NodeId__, from which we can get the corresponding field value that is a list of job IDs. Job ID follows the name rule of UGE, if it is an array job, job_id + "." + task_id to represent the job ID.

Dummy data points in `NodeJobs` measurement:
```
measurement: NodeJobs
time: 1583792296             
tags: 
    NodeId: "101.10.1.1"
fields:
    JobList:
        - 123456
        - 123457.1
        - 123457.2
```

Job details are saved in `JobsInfo` measurement. Tag key is __JobId__, from which we can get the corresponding job details that are saved into fields. The data point in this measurement is inserted only when a new job is submitted.

Dummy data points in `JobsInfo` measurement:
```
measurement: JobsInfo
time: 1583792296              
tags: 
    JobId: 123456
    Queue: "quanah"
fields:
    StartTime: 1583792200   
    SubmitTime: 1583792200  
    TotalNodes: 4
    NodeList: "101.10.1.1"
    CPUCores: 10
    JobName: "efg"
    User: "abc"
```

