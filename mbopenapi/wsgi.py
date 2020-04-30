from openapi_server.__main__ import main

if __name__ == "__main__":
    app = main()
    app.run()
else:
    gunicorn_app = main()