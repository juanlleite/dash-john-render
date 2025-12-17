"""
WSGI Configuration File para PythonAnywhere
L'Acqua Azzurra Dashboard

INSTRUÇÕES:
1. No PythonAnywhere, vá em: Web → WSGI configuration file
2. Substitua TODO o conteúdo por este arquivo
3. Ajuste o path '/home/juanleite/dashboard' se necessário
4. Salve e recarregue o web app
"""

import sys
import os

# ========================================
# CONFIGURAÇÃO DO PATH
# ========================================
# IMPORTANTE: Ajuste 'juanleite' para seu username!
path = '/home/juanleite/dashboard'

if path not in sys.path:
    sys.path.insert(0, path)

# ========================================
# CARREGAR VARIÁVEIS DE AMBIENTE
# ========================================
from dotenv import load_dotenv
env_path = os.path.join(path, '.env')
load_dotenv(env_path)

# Verificar se .env foi carregado
if not os.path.exists(env_path):
    print(f"⚠️ AVISO: Arquivo .env não encontrado em {env_path}")
    print("⚠️ Crie o arquivo .env com DATABASE_URL!")

# ========================================
# IMPORTAR APLICAÇÃO DASH
# ========================================
try:
    from app import app
    
    # PythonAnywhere precisa do servidor Flask subjacente
    application = app.server
    
    print("✅ Aplicação Dash carregada com sucesso!")
    
except Exception as e:
    print(f"❌ Erro ao carregar aplicação: {e}")
    import traceback
    traceback.print_exc()
    
    # Criar aplicação dummy para evitar erro 500
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"""
        <h1>Erro ao Carregar Dashboard</h1>
        <p>Erro: {str(e)}</p>
        <p>Verifique os logs em /var/log/</p>
        <pre>{traceback.format_exc()}</pre>
        """, 500

# ========================================
# LOGGING PARA DEBUG
# ========================================
print(f"📂 Path do projeto: {path}")
print(f"📂 .env path: {env_path}")
print(f"🔌 DATABASE_URL carregado: {'Sim' if os.getenv('DATABASE_URL') else 'Não'}")
