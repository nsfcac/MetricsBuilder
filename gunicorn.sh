#! /bin/bash

readonly sourceFile="/home/username/MetricsBuilder/env/bin/activate"

source ${sourceFile}

gunicorn --certfile='/home/username/SSL_Certificate/influx_ttu_edu_cert.cer' --keyfile='/home/username/SSL_Certificate/server.key' --workers=5 --timeout 120 -b 0.0.0.0:8090 'openapi_server.__main__:app' --log-file error_logs.log --log-level error --name MetricsBuilderAPI