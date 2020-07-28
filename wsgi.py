import sys
import site

site.addsitedir('/var/www/MetricsBuilder/env/lib/python3.6/site-packages')

sys.path.append('/var/www/MetricsBuilder')

from openapi_server.__main__ import app as application
