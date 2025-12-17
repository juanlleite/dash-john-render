#!/bin/bash
# Script de Deploy Rápido - PythonAnywhere
# Execute no console Bash do PythonAnywhere

echo "🚀 Iniciando deploy do dashboard L'Acqua Azzurra..."
echo ""

# 1. Navegar para o diretório
cd ~/dashboard || { echo "❌ Diretório ~/dashboard não encontrado!"; exit 1; }
echo "✅ Diretório encontrado"

# 2. Fazer backup do .env atual (se existir)
if [ -f .env ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup do .env criado"
fi

# 3. Criar/atualizar .env
cat > .env << 'EOF'
DATABASE_URL=postgresql://lacqua_azzurra_db_user:Pzl3jEA1TaInwwbYMh67IEsvjIdUhpfg@dpg-d4snmj7pm1nc73c7dcdg-a.virginia-postgres.render.com/lacqua_azzurra_db
DASH_DEBUG=False
HOST=0.0.0.0
PORT=8000
EOF
echo "✅ Arquivo .env criado"

# 4. Instalar/atualizar dependências
echo ""
echo "📦 Instalando dependências..."
pip install --user -r requirements.txt --quiet
echo "✅ Dependências instaladas"

# 5. Testar conexão com banco
echo ""
echo "🔌 Testando conexão com banco..."
python3 << 'PYEOF'
try:
    from database import db
    from models import Cliente
    print("✅ Banco conectado!")
    with db.get_session() as session:
        count = session.query(Cliente).count()
        print(f"📊 Total de clientes: {count}")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    exit(1)
PYEOF

# 6. Verificar arquivos críticos
echo ""
echo "📁 Verificando arquivos..."
FILES=("app.py" "database.py" "models.py" "data_processor_postgres.py" "assets/styles.css")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file NÃO ENCONTRADO!"
    fi
done

# 7. Configurar permissões
chmod -R 755 assets/
echo "✅ Permissões configuradas"

echo ""
echo "========================================="
echo "✅ Deploy concluído!"
echo "========================================="
echo ""
echo "📝 Próximos passos:"
echo "1. Vá em Web → Reload seu app"
echo "2. Acesse: https://juanleite.pythonanywhere.com"
echo "3. Se houver erro, verifique logs:"
echo "   tail -n 50 /var/log/juanleite.pythonanywhere.com.error.log"
echo ""
