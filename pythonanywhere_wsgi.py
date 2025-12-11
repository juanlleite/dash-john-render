"""
WSGI configuration for PythonAnywhere
Este arquivo deve ser copiado para /var/www/[seu_usuario]_pythonanywhere_com_wsgi.py
"""
import sys
import os

# ===== CONFIGURAÇÃO DO PATH =====
# IMPORTANTE: Ajuste o username para o SEU usuário do PythonAnywhere
project_home = '/home/juanleite/dashboard'  # Mude 'juanleite' para seu username

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ===== CARREGAR VARIÁVEIS DE AMBIENTE =====
from dotenv import load_dotenv
dotenv_path = os.path.join(project_home, '.env')
load_dotenv(dotenv_path)

# ===== IMPORTAR APLICAÇÃO DASH =====
from app import app

# PythonAnywhere precisa de uma variável chamada "application"
application = app.server

# ===== LOG DE INICIALIZAÇÃO (DEBUG) =====
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.info("✅ WSGI PythonAnywhere iniciado!")
logging.info(f"📂 Project home: {project_home}")
logging.info(f"🐍 Python version: {sys.version}")
