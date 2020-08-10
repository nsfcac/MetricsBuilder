import connexion
from openapi_server import encoder
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
import ssl


context = ssl.SSLContext(ssl.PROTOCOL_TLS)
context.load_cert_chain("/home/username/SSL_Certificate/influx_ttu_edu_cert.cer", "/home/username/SSL_Certificate/server.key")

app = connexion.App(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'MetricsBuilder API'},
            pythonic_params=True)
CORS(app.app)

if __name__ == '__main__':
    http_server = WSGIServer(('localhost', 8080), app, keyfile="/home/username/SSL_Certificate/server.key", 
                              certfile="/home/username/SSL_Certificate/influx_ttu_edu_cert.cer")
    http_server.serve_forever()
    # app.run(port=8080, ssl_context=context)
    # app.run(port=8080)