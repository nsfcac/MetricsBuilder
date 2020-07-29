import sys

sys.path.append('/home/lijie/MetricsBuilder')

from openapi_server.__main__ import app as application

if __name__ == "__main__":
    application.run()
