#!/usr/bin/env python3
import os
import connexion

from openapi_server import encoder
from flask_cors import CORS


abs_file_path = os.path.abspath(os.path.dirname(__file__))
openapi_path = os.path.join(abs_file_path, "./openapi_server/openapi")
app = connexion.App(__name__, specification_dir=openapi_path)
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'MetricsBuilder API'},
            pythonic_params=True)
CORS(app.app)
crt = os.environ['FLASKCRT']
key = os.environ['FLASKKEY']

if __name__ == '__main__':
  app.run(port=5000, ssl_context=(crt, key))
