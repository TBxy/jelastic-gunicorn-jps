import json
import multiprocessing
import os
from pathlib import Path
#from dotenv import load_dotenv

# take env files from gunicorn env
#load_dotenv(dotenv_path=Path('/etc/sysconfig/gunicorn'))

host = os.getenv("APP_HOST", "0.0.0.0")
port = os.getenv("APP_PORT", "80")
#port = "8000"
bind_env = os.getenv("APP_BIND", None)
use_loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
if bind_env:
    use_bind = bind_env
else:
    use_bind = f"{host}:{port}"

accesslog_var = os.getenv("GUNICORN_ACCESS_LOG", "/var/log/gunicorn/access_log")
use_accesslog = accesslog_var or None
errorlog_var = os.getenv("GUNICORN_ERROR_LOG", "/var/log/gunicorn/gunicorn.log")
use_errorlog = errorlog_var or None
graceful_timeout_str = os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30")
timeout_str = os.getenv("GUNICORN_TIMEOUT", "30")
keepalive_str = os.getenv("GUNICORN_KEEP_ALIVE", "5")

# Gunicorn config variables
loglevel = use_loglevel
max_workers = int(os.getenv("GUNICORN_WORKERS_MAX", "20"))
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
chdir = os.getenv("APP_WORKDIR", ".")
if workers > max_workers:
    workers = max_workers
preload_app = os.getenv("APP_PRELOAD", "0").lower() in ["1","y","yes","true","on"]
reload = os.getenv("APP_RELOAD", "0").lower() in ["1","y","yes","true","on"]
bind = use_bind
errorlog = use_errorlog
worker_tmp_dir = "/dev/shm" # https://docs.gunicorn.org/en/latest/faq.html#blocking-os-fchmod
accesslog = use_accesslog
graceful_timeout = int(graceful_timeout_str)
timeout = int(timeout_str)
keepalive = int(keepalive_str)
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "2")
threads = 1
if worker_class == "gthread":
    threads = int(os.getenv("THREADS", "2"))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "200"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "20"))

# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "threads": threads,
    "reload": reload,
    "worker_class": worker_class,
    "bind": bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "preload_app": preload_app,
    "keepalive": keepalive,
    "errorlog": errorlog,
    "accesslog": accesslog,
    "host": host,
    "port": port,
}
print(json.dumps(log_data))
