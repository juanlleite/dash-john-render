# 🚀 Deploy para Produção - PythonAnywhere

## ✅ Preparação Local

### 1. Atualizar .env.pythonanywhere com PostgreSQL
```bash
DATABASE_URL=postgresql://lacqua_azzurra_db_user:Pzl3jEA1TaInwwbYMh67IEsvjIdUhpfg@dpg-d4snmj7pm1nc73c7dcdg-a.virginia-postgres.render.com/lacqua_azzurra_db
```

### 2. Testar localmente com .env.pythonanywhere
```powershell
# Renomear .env temporariamente
mv .env .env.local

# Copiar .env.pythonanywhere para .env
cp .env.pythonanywhere .env

# Testar
C:/Users/Juan/Documents/john/.venv/Scripts/python.exe app.py

# Se funcionar, reverter
mv .env.local .env
```

---

## 📦 Deploy no PythonAnywhere

### PASSO 1: Acessar Console do PythonAnywhere
1. Acesse: https://www.pythonanywhere.com/
2. Login com sua conta
3. Vá em **"Consoles"** → **"Bash"**

### PASSO 2: Atualizar Código
```bash
cd ~/dashboard
git pull origin main

# OU se não usar Git, fazer upload manual:
# Files → Upload → Selecione os arquivos
```

### PASSO 3: Criar/Atualizar .env
```bash
cd ~/dashboard
nano .env
```

Cole este conteúdo:
```
DATABASE_URL=postgresql://lacqua_azzurra_db_user:Pzl3jEA1TaInwwbYMh67IEsvjIdUhpfg@dpg-d4snmj7pm1nc73c7dcdg-a.virginia-postgres.render.com/lacqua_azzurra_db
DASH_DEBUG=False
HOST=0.0.0.0
PORT=8000
```

Salvar: `CTRL+O` → `ENTER` → `CTRL+X`

### PASSO 4: Instalar Dependências
```bash
cd ~/dashboard
pip install --user -r requirements.txt
```

### PASSO 5: Testar Conexão com Banco
```bash
python3 -c "
from database import db
print('✅ Banco conectado!')
with db.get_session() as session:
    from models import Cliente
    count = session.query(Cliente).count()
    print(f'📊 Total de clientes: {count}')
"
```

### PASSO 6: Configurar Web App

#### 6.1: Criar/Editar WSGI Configuration
1. Vá em **"Web"** → Seu app → **"WSGI configuration file"**
2. Substitua TODO o conteúdo por:

```python
import sys
import os

# Adicionar path do projeto
path = '/home/juanleite/dashboard'
if path not in sys.path:
    sys.path.insert(0, path)

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

# Importar app Dash
from app import app

# PythonAnywhere precisa do servidor Flask subjacente
application = app.server
```

#### 6.2: Configurar Virtual Environment (se tiver)
1. No painel **"Web"**
2. Seção **"Virtualenv"**
3. Digite: `/home/juanleite/.virtualenvs/dashboard`

OU crie um:
```bash
cd ~
python3 -m venv .virtualenvs/dashboard
source .virtualenvs/dashboard/bin/activate
cd ~/dashboard
pip install -r requirements.txt
```

#### 6.3: Configurar Static Files (IMPORTANTE!)
No painel **"Web"** → **"Static files"**:

| URL | Directory |
|-----|-----------|
| /assets/ | /home/juanleite/dashboard/assets/ |

### PASSO 7: Reload do Web App
1. No painel **"Web"**
2. Botão verde **"Reload [seu-usuario].pythonanywhere.com"**
3. Aguarde ~10 segundos

### PASSO 8: Testar
Acesse: `https://juanleite.pythonanywhere.com`

---

## 🔧 Troubleshooting

### Se aparecer erro 500:
```bash
cd ~/dashboard
tail -n 50 /var/log/juanleite.pythonanywhere.com.error.log
```

### Se não conectar no banco:
```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('DATABASE_URL:', os.getenv('DATABASE_URL'))
"
```

### Se assets não carregarem:
Verifique permissões:
```bash
chmod -R 755 ~/dashboard/assets
```

---

## 📊 Banco de Dados - Alterações Aplicadas

### ✅ Mudanças já aplicadas no PostgreSQL Render:

1. **Colunas adicionadas:**
   - `tipo_filtro` (VARCHAR 100)
   - `valor_filtro` (DECIMAL 10,2)

2. **Colunas removidas:**
   - `metodo_cobranca`
   - `auto_pay`

3. **Dados atualizados:**
   - `valor_rota` zerado (693 clientes)
   - Piscineiros normalizados (4 únicos)
   - 292 clientes com piscineiro atribuído
   - 401 clientes "Não atribuído"

**Não é necessário rodar migrations!** O banco PostgreSQL no Render já está atualizado.

---

## 🎯 Checklist Final

- [ ] `.env` criado no PythonAnywhere com DATABASE_URL correto
- [ ] `requirements.txt` instalado
- [ ] Conexão com PostgreSQL testada
- [ ] WSGI configurado corretamente
- [ ] Virtual environment configurado (opcional)
- [ ] Static files mapeados
- [ ] Web app recarregado
- [ ] Site acessível
- [ ] Login funciona
- [ ] Dados aparecem corretamente
- [ ] Salvamento funciona
- [ ] KPIs corretos (Faturamento, Clientes Ativos, Manutenções)

---

## 📝 Informações do Banco (Render)

- **Host:** dpg-d4snmj7pm1nc73c7dcdg-a.virginia-postgres.render.com
- **Database:** lacqua_azzurra_db
- **User:** lacqua_azzurra_db_user
- **Total de clientes:** 693
- **Piscineiros:** Drask Silva, Lucca, Pedro Santos, Vini Penner

---

## 🚨 Importante!

1. **Nunca commite `.env` no Git!** (já está no .gitignore)
2. O banco PostgreSQL está no Render e é compartilhado entre local e produção
3. Mudanças no banco afetam TODOS os ambientes
4. Faça backup antes de mudanças críticas
5. Porta no PythonAnywhere: use 8000 (não 8050 ou 8051)

---

## 📞 Suporte

Se precisar de ajuda:
1. Verifique logs: `/var/log/[usuario].pythonanywhere.com.error.log`
2. Console PythonAnywhere para testar comandos
3. Fórum PythonAnywhere: https://www.pythonanywhere.com/forums/
