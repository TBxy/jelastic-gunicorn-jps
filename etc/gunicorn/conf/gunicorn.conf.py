import json
import multiprocessing
import os
from dotenv import load_dotenv
from pathlib import Path

# take env files from gunicorn env
load_dotenv(dotenv_path=Path('/etc/sysconfig/gunicorn'))

host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
#port = "8000"
bind_env = os.getenv("BIND", None)
use_loglevel = os.getenv("LOG_LEVEL", "info")
if bind_env:
    use_bind = bind_env
else:
    use_bind = f"{host}:{port}"

accesslog_var = os.getenv("ACCESS_LOG", "-")
use_accesslog = accesslog_var or None
errorlog_var = os.getenv("ERROR_LOG", "-")
use_errorlog = errorlog_var or None
graceful_timeout_str = os.getenv("GRACEFUL_TIMEOUT", "120")
timeout_str = os.getenv("TIMEOUT", "120")
keepalive_str = os.getenv("KEEP_ALIVE", "5")

# Gunicorn config variables
loglevel = use_loglevel
workers = int(os.getenv("WORKERS", "2"))
chdir = os.getenv("APP_WORKDIR", ".")
if not workers: # auto
    cores = multiprocessing.cpu_count()
    workers = cores*2+1
preload_app = os.getenv("PRELOAD_APP", "0").lower() in ["1","y","yes","true","on"]
reload = os.getenv("RELOAD_APP", "0").lower() in ["1","y","yes","true","on"]
bind = use_bind
errorlog = use_errorlog
worker_tmp_dir = "/dev/shm" # https://docs.gunicorn.org/en/latest/faq.html#blocking-os-fchmod
accesslog = use_accesslog
graceful_timeout = int(graceful_timeout_str)
timeout = int(timeout_str)
keepalive = int(keepalive_str)
worker_class = os.getenv("WORKER_CLASS", "2")
threads = 0
if worker_class == "gthread":
    threads = int(os.getenv("THREADS", "2"))

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
