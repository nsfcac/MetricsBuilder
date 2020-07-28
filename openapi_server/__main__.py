import connexion
from openapi_server import encoder
from flask_cors import CORS
import ssl


context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain("/home/username/SSL_Certificate/influx_ttu_edu_cert.cer", "/home/username/SSL_Certificate/server.key")

app = connexion.App(__name__, specification_dir='./openapi/', server='gevent')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'MetricsBuilder API'},
            pythonic_params=True)
CORS(app.app)


if __name__ == '__main__':
    app.run(port=8080, ssl_context=context)


# Jul 28 02:47:19 influx control.sh[26221]: File "/usr/lib64/python3.6/ssl.py", line 365, in wrap_socket
# Jul 28 02:47:19 influx control.sh[26221]: _context=self, _session=session)
# Jul 28 02:47:19 influx control.sh[26221]: File "/usr/lib64/python3.6/ssl.py", line 773, in __init__
# Jul 28 02:47:19 influx control.sh[26221]: self.do_handshake()
# Jul 28 02:47:19 influx control.sh[26221]: File "/usr/lib64/python3.6/ssl.py", line 1033, in do_handshake
# Jul 28 02:47:19 influx control.sh[26221]: self._sslobj.do_handshake()
# Jul 28 02:47:19 influx control.sh[26221]: File "/usr/lib64/python3.6/ssl.py", line 645, in do_handshake
# Jul 28 02:47:19 influx control.sh[26221]: self._sslobj.do_handshake()
# Jul 28 02:47:19 influx control.sh[26221]: ssl.SSLError: [SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:877)
# Jul 28 02:47:19 influx control.sh[26221]: 2020-07-28T07:47:19Z <Greenlet at 0x7f4388a05b48: _handle_and_close_when_done(<bound method StreamServer.wrap_socket_and_handle , <bound me

# gunicorn --certfile='/home/username/SSL_Certificate/influx_ttu_edu_cert.cer' --keyfile='/home/username/SSL_Certificate/server.key' -b 0.0.0.0:8080 'openapi_server.__main__:app' --limit-request-line 0
