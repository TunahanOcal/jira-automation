# gunicorn_conf.py
from multiprocessing import cpu_count

bind = "127.0.0.1:2001"

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

