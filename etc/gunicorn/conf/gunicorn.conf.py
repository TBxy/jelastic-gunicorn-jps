import json
import multiprocessing
import os

#workers_per_core_str = os.getenv("WORKERS_PER_CORE", "2")
#max_workers_str = os.getenv("MAX_WORKERS")
#use_max_workers = None
#if max_workers_str:
#    use_max_workers = int(max_workers_str)
#web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)

host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
#port = "8000"
bind_env = os.getenv("BIND", None)
use_loglevel = os.getenv("LOG_LEVEL", "info")
if bind_env:
    use_bind = bind_env
else:
    use_bind = f"{host}:{port}"

# workers_per_core = float(workers_per_core_str)
# default_web_concurrency = workers_per_core * cores + 1
# if web_concurrency_str:
#     web_concurrency = int(web_concurrency_str)
#     assert web_concurrency > 0
# else:
#     web_concurrency = max(int(default_web_concurrency), 2)
#     if use_max_workers:
#         web_concurrency = min(web_concurrency, use_max_workers)

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
if not workers: # auto
    cores = multiprocessing.cpu_count()
    workers = cores*2+1
threads = None
if worker_class == "gthread":
    threads = int(os.getenv("THREADS", "1"))
preload_app = os.getenv("PRELOAD_APP", "0")).lower() in ["1","y","yes","true","on"]
bind = use_bind
errorlog = use_errorlog
worker_tmp_dir = "/dev/shm"
accesslog = use_accesslog
graceful_timeout = int(graceful_timeout_str)
timeout = int(timeout_str)
keepalive = int(keepalive_str)
worker_class = os.getenv("WORKER_CLASS", "2")


# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "threads": threads,
    "worker_class": worker_class,
    "bind": bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "preload_app": preload_app,
    "keepalive": keepalive,
    "errorlog": errorlog,
    "accesslog": accesslog,
    # Additional, non-gunicorn variables
    #"workers_per_core": workers_per_core,
    #"use_max_workers": use_max_workers,
    "host": host,
    "port": port,
}
print(json.dumps(log_data))