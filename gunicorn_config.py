"""
Configuração do Gunicorn otimizada para Render Free Tier (256MB RAM)
"""
import multiprocessing
import os

# Configurações de Worker
workers = 1  # Apenas 1 worker para economizar memória (Render Free Tier tem 256MB)
worker_class = "sync"  # Worker síncrono (usa menos memória que async)
threads = 2  # 2 threads por worker (suficiente para 1-2 usuários simultâneos)

# Timeouts
timeout = 120  # 120 segundos (2 minutos) antes de matar worker travado
graceful_timeout = 30  # 30 segundos para finalizar requests em andamento
keepalive = 5  # Manter conexões por 5 segundos

# Gestão de Memória
max_requests = 100  # Reiniciar worker após 100 requests (previne memory leaks)
max_requests_jitter = 20  # Adiciona aleatoriedade (80-120 requests)

# Bind
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"

# Logging
loglevel = "info"
accesslog = "-"  # Log para stdout
errorlog = "-"   # Erros para stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Preload (carrega app antes de criar workers - economiza memória)
preload_app = True

# Worker connections (não relevante para sync worker)
worker_connections = 50

# Configurações adicionais para economizar memória
def post_fork(server, worker):
    """Hook executado após fork de cada worker"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Hook executado antes do fork"""
    pass

def pre_exec(server):
    """Hook executado antes do exec"""
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """Hook quando o servidor está pronto"""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Hook quando worker recebe SIGINT"""
    worker.log.info("worker received INT or QUIT signal")

def worker_abort(worker):
    """Hook quando worker é abortado"""
    worker.log.info("worker received SIGABRT signal")
