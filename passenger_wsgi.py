"""
Passenger WSGI para Hostinger cPanel
Este arquivo é usado pelo Passenger (servidor web da Hostinger) para iniciar a aplicação Dash
"""
import sys
import os

# ===== CONFIGURAÇÃO DO VIRTUALENV =====
# IMPORTANTE: Substitua 'SEU_CPANEL_USER' e 'dashboard' pelo seu usuário e pasta corretos!
# Exemplo: /home/u123456/virtualenv/dashboard/3.9/bin/python3
INTERP = os.path.join(
    os.environ['HOME'],
    'virtualenv',
    'dashboard',  # Nome da pasta onde você fez upload dos arquivos
    '3.9',  # Versão do Python que você escolheu no cPanel
    'bin',
    'python3'
)

# Verificar se estamos usando o interpretador correto
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# ===== ADICIONAR PASTA DO PROJETO AO PATH =====
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

# ===== CARREGAR VARIÁVEIS DE AMBIENTE =====
from dotenv import load_dotenv
load_dotenv(os.path.join(current_dir, '.env'))

# ===== IMPORTAR APLICAÇÃO DASH =====
from app import server as application

# ===== CONFIGURAÇÃO ADICIONAL (OPCIONAL) =====
# Configurar logging para debug
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log de inicialização
logging.info("✅ Passenger WSGI iniciado com sucesso!")
logging.info(f"📂 Diretório: {current_dir}")
logging.info(f"🐍 Python: {sys.version}")
