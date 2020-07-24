#! /bin/bash

readonly sourceFile="/home/username/TestMB/MetricsBuilder/env/bin/activate"

source ${sourceFile}

python3 -m openapi_server

# if [ $# == 0 ]
#   then
#     echo "Please specify a argument: 0 to start MetricsBuilderAPI, other value to stop MetricsBuilderAPI."
#     exit 0
# fi

# if [ $1 == 0 ]
# then
#     # activate
#     echo "Start MetricsBuilderAPI ..."
#     cd /home/username/TestMB/MetricsBuilder/mbopenapi/
#     nohup python3 -m openapi_server >> running.log &
# else
#     echo "Stop MetricsBuilderAPI ..."
#     kill -9 `ps -ef | grep openapi_server | grep -v grep | awk '{print $2}'`
# fi
