import connexion

from openapi_server import encoder
from flask_cors import CORS
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain("/password/SSL_Certificate/influx_ttu_edu_cert.cer", "/password/SSL_Certificate/server.key")


def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'MetricsBuilder API'},
                pythonic_params=True)
    # Talisman(app.app)
    CORS(app.app)
    
    app.run(port=8080, ssl_context=context)
    # app.run()


if __name__ == '__main__':
    main()
