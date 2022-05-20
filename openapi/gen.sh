#!/bin/bash
echo "Backup default_controller..."
cp ../openapi_server/controllers/default_controller.py ../metrics_builder/shared/

echo "Generate openapi_server from openapi.ymal..."
npx @openapitools/openapi-generator-cli generate -i openapi.yaml -g python-flask -o ../openapi_tmp/

echo "Remove the previous openapi_server folder..."
rm -r ../openapi_server

echo "Update the openapi_server folder..."
mv ../openapi_tmp/openapi_server ../

rm ../openapi_server/__main__.py

cp ../metrics_builder/shared/default_controller.py ../openapi_server/controllers

echo "Clean the temporary folder..."
rm -r ../openapi_tmp