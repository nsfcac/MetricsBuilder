import os

bind = '0.0.0.0:5000'
workers = 4
preload_app = True
timeout = 45
loglevel = 'error'
accesslog = './log/mbapi_access.log'
errorlog = './log/mbapi_error.log'
certfile=os.environ['FLASKCRT']
keyfile=os.environ['FLASKKEY']