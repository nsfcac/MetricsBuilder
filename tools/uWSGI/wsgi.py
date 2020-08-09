import sys

sys.path.append('/home/username/MetricsBuilder')

import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS)
context.load_cert_chain("/home/username/SSL_Certificate/influx_ttu_edu_cert.cer", "/home/username/SSL_Certificate/server.key")

from openapi_server.__main__ import app as application

if __name__ == "__main__":
    application.run(port=8080, ssl_context=context)
