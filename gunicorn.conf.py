# gunicorn.conf.py

import multiprocessing
import os

from dotenv import load_dotenv

load_dotenv()

bind = f"0.0.0.0:{os.getenv('PORT', '8363')}"

workers = int(os.getenv("WORKERS", multiprocessing.cpu_count()))
worker_class = "uvicorn.workers.UvicornWorker"

graceful_timeout = 30
timeout = 120

preload_app = False

accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").split()[0].lower()

pidfile = "/tmp/gunicorn.pid"
daemon = False


def on_starting(server):
    print("🚀 Gunicorn master starting...")


def on_reload(server):
    print("♻️  Graceful reload triggered - starting new workers...")


def worker_int(worker):
    print(f"  Worker {worker.pid} received INT signal, finishing requests...")


def worker_exit(server, worker):
    print(f"  Worker {worker.pid} exited")


def post_fork(server, worker):
    print(f"  Worker {worker.pid} spawned")
