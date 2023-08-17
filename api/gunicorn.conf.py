import multiprocessing

import uvloop  # type: ignore

uvloop.install()  # type: ignore


wsgi_app = "api.app:app"
bind = "0.0.0.0:14000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 20000
keepalive = 5
