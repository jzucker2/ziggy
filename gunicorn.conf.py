import multiprocessing
import os

# Server socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
backlog = int(os.getenv("GUNICORN_BACKLOG", "2048"))

# Worker processes
workers = int(
    os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)
)
worker_class = os.getenv(
    "GUNICORN_WORKER_CLASS", "uvicorn.workers.UvicornWorker"
)
worker_connections = int(os.getenv("GUNICORN_WORKER_CONNECTIONS", "1000"))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "50"))

# Timeout settings
timeout = int(os.getenv("GUNICORN_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "2"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))

# Logging
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info").lower()
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")  # "-" means stdout
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")  # "-" means stderr
access_log_format = os.getenv(
    "GUNICORN_ACCESS_LOG_FORMAT",
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s',
)

# Process naming
proc_name = os.getenv("GUNICORN_PROC_NAME", "ziggy")

# Server mechanics
daemon = os.getenv("GUNICORN_DAEMON", "false").lower() == "true"
pidfile = os.getenv("GUNICORN_PIDFILE", None)
user = os.getenv("GUNICORN_USER", None)
group = os.getenv("GUNICORN_GROUP", None)
tmp_upload_dir = os.getenv("GUNICORN_TMP_UPLOAD_DIR", None)

# SSL (if needed)
keyfile = os.getenv("GUNICORN_KEYFILE", None)
certfile = os.getenv("GUNICORN_CERTFILE", None)

# Security
limit_request_line = int(os.getenv("GUNICORN_LIMIT_REQUEST_LINE", "4094"))
limit_request_fields = int(os.getenv("GUNICORN_LIMIT_REQUEST_FIELDS", "100"))
limit_request_field_size = int(
    os.getenv("GUNICORN_LIMIT_REQUEST_FIELD_SIZE", "8190")
)

# Preload app for better performance
preload_app = os.getenv("GUNICORN_PRELOAD_APP", "true").lower() == "true"


# Worker lifecycle hooks
def on_starting(server):
    """Called just after the server is started."""
    server.log.info("🚀 Starting Ziggy with Gunicorn")


def on_reload(server):
    """Called to reload the server."""
    server.log.info("🔄 Reloading Ziggy server")


def when_ready(server):
    """Called just after the server is started and workers are spawned."""
    server.log.info(f"✅ Ziggy ready with {server.cfg.workers} workers")


def worker_int(worker):
    """Called just after a worker has been initialized."""
    worker.log.info("👷 Worker initialized")


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("🔧 Pre-fork worker setup")


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"👷 Worker {worker.pid} forked")


def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("🔧 Worker application initialized")


def worker_abort(worker):
    """Called when a worker received SIGABRT signal."""
    worker.log.info("⚠️ Worker received SIGABRT")


def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("🔄 Pre-exec master process")


def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("🛑 Gunicorn server shutting down")
