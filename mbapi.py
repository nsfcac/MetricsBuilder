#!/usr/bin/env python3
import os
import connexion

from openapi_server import encoder


def main():
    abs_file_path = os.path.abspath(os.path.dirname(__file__))
    openapi_path = os.path.join(abs_file_path, "./openapi")
    app = connexion.App(__name__, specification_dir=openapi_path)
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('specification.yaml',
                arguments={'title': 'MetricsBuilder API'},
                pythonic_params=True)

    app.run(port=8080)


if __name__ == '__main__':
    main()
