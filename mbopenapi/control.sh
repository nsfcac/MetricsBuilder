#! /bin/bash
if [ $# == 0 ]
  then
    echo "Please specify a argument: 0 to start MetricsBuilderAPI, other value to stop MetricsBuilderAPI."
    exit 0
fi

if [ $1 == 0 ]
then
    echo "Start MetricsBuilderAPI ..."
    nohup python3.6 -m openapi_server >> running.log &
else
    echo "Stop MetricsBuilderAPI ..."
    kill -9 `ps -ef | grep openapi_server | grep -v grep | awk '{print $2}'`
fi