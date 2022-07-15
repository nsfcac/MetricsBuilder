MBAPI=$(PWD)/gunicorn.conf.py mbapi:app
GUNICORN=$(PWD)/env/bin/gunicorn

ps_mbapi=`ps aux | grep "$(GUNICORN) -c ${MBAPI}" | grep -v 'grep' > /dev/null`

startmbapi:
	@-if $(ps_mbapi); then \
		echo "MetricsBuilder API Service is already up and running!"; \
	else \
		echo "Start MetricsBuilder API service..."; \
		. ./env/bin/activate; \
		$(GUNICORN) -c ${MBAPI} 2> /dev/null &\
	fi

stopmbapi:
	@-if $(ps_mbapi); then \
		echo "Stop MetricsBuilder API service..."; \
		pkill -f "$(GUNICORN) -c ${MBAPI}"; \
	else \
		echo "MetricsBuilder API service is already stopped!"; \
	fi