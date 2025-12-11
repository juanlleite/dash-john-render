# ⚡ DEPLOY RÁPIDO - PYTHONANYWHERE VIA GITHUB

## 🎯 Método mais rápido: **10 minutos total**

---

## 📋 PRÉ-REQUISITOS

✅ Conta PythonAnywhere criada (FREE ou paga)
✅ Código no GitHub: `juanlleite/dash-john-render`
✅ Python 3.9+ disponível no PythonAnywhere

---

## 🚀 PASSO A PASSO

### **PASSO 1: Console Bash (30 segundos)**

1. No PythonAnywhere, clique em **"Consoles"** (menu superior)
2. Clique em **"Bash"** (console verde)
3. Aguarde terminal abrir

---

### **PASSO 2: Clonar Repositório (1 minuto)**

No console Bash, execute:

```bash
# Clonar repositório do GitHub
git clone https://github.com/juanlleite/dash-john-render.git dashboard

# Entrar na pasta
cd dashboard

# Verificar arquivos
ls -la

# Deve ver: app.py, models.py, database.py, etc.
```

---

### **PASSO 3: Configurar Ambiente (1 minuto)**

```bash
# Copiar template do .env
cp .env.pythonanywhere .env

# Editar .env (ajustar username se necessário)
nano .env
```

**No nano:**
- Verifique se o path está correto: `/home/[SEU_USERNAME]/dashboard/lacqua_azzurra.db`
- Se seu username não é `juanleite`, mude para o correto
- **Salvar:** `Ctrl+O`, `Enter`, `Ctrl+X`

**Ou deixe como está se for usar o default:**
```env
DATABASE_URL=sqlite:////home/juanleite/dashboard/lacqua_azzurra.db
```

---

### **PASSO 4: Instalar Dependências (5 minutos)**

```bash
# Instalar todas as bibliotecas
pip install --user -r requirements.txt
```

⏳ **Aguarde 3-5 minutos** - vai instalar dash, pandas, sqlalchemy, etc.

**Verificar instalação:**
```bash
pip list | grep -E "dash|pandas|SQLAlchemy"
```

Deve mostrar:
```
dash                        3.3.0
pandas                      2.3.3
SQLAlchemy                  2.0.36
```

---

### **PASSO 5: Migrar Dados (2 minutos)**

```bash
# Confirmar que está na pasta certa
pwd
# Deve mostrar: /home/[seu_username]/dashboard

# Executar migração CSV → SQLite
python migrate_to_postgres.py
```

Quando perguntar:
```
Deseja continuar com a migração? (s/n):
```
**Digite:** `s` + Enter

Aguarde:
```
✅ Migração do CSV concluída:
• Migrados: 693
• Pulados: 14 (duplicatas)
```

**Verificar:**
```bash
# Contar clientes no banco
python -c "from database import db; from models import Cliente; \
with db.get_session() as s: print(f'Total: {s.query(Cliente).count()}')"
```

Deve mostrar: `Total: 693` ✅

---

### **PASSO 6: Criar Web App (3 minutos)**

#### 6.1 - Criar aplicação

1. Clique em **"Web"** (menu superior)
2. Clique **"Add a new web app"**
3. Seu domínio: `[seu_username].pythonanywhere.com` → **"Next"**
4. Framework: **"Flask"**
5. Python version: **"Python 3.10"** (ou mais recente)
6. Path: aceite o padrão → **"Next"**
7. Aguarde criação (~30 segundos)

#### 6.2 - Configurar Source Code

Na página **Web**, seção **"Code"**:

**Source code:** (clique no ícone de lápis)
```
/home/juanleite/dashboard
```
(Mude `juanleite` para SEU username)

Clique ✓ para salvar

#### 6.3 - Configurar WSGI

Ainda na seção **"Code"**:

1. Clique no link azul: **"WSGI configuration file"**
   - `/var/www/[seu_username]_pythonanywhere_com_wsgi.py`

2. **APAGUE TODO O CONTEÚDO** do arquivo

3. **Cole este código:**

```python
import sys
import os

# MUDE 'juanleite' para SEU username!
project_home = '/home/juanleite/dashboard'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

from app import app
application = app.server
```

4. **Ajuste o username** se necessário (linha 4)
5. Clique **"Save"** (botão verde no topo)
6. Feche a aba do editor

---

### **PASSO 7: Reload e Testar (1 minuto)**

#### 7.1 - Reload da aplicação

1. Volte para a aba **"Web"**
2. No topo da página, botão verde:
   ```
   🔄 Reload [seu_username].pythonanywhere.com
   ```
3. Clique no botão
4. Aguarde ~10 segundos (barra de progresso)

#### 7.2 - Acessar dashboard

Clique no link:
```
https://[seu_username].pythonanywhere.com
```

✅ **VERIFICAR:**
- [ ] Página carrega (sem erro 500)
- [ ] 3 KPIs aparecem (Faturamento, Clientes, Manutenções)
- [ ] Tabela mostra 693 clientes
- [ ] Filtros funcionam (Status, Piscineiro, Mês)
- [ ] Busca por nome funciona
- [ ] Botão "Editar" abre modal
- [ ] Botão "Novo Cliente" funciona
- [ ] "Exportar CSV" faz download
- [ ] SSL ativo (cadeado 🔒 no navegador)

---

## 🎉 PRONTO!

Seu dashboard está rodando em:
```
https://[seu_username].pythonanywhere.com
```

**Recursos FREE:**
- ✅ 100.000 hits/dia
- ✅ 512MB RAM
- ✅ 1GB disk space
- ✅ SSL/HTTPS grátis
- ✅ Sempre ativo (não hiberna)
- ✅ 693 clientes no SQLite

---

## 🔄 ATUALIZAR CÓDIGO (10 segundos)

Quando fizer mudanças no código local e subir no GitHub:

```bash
# No Console Bash do PythonAnywhere
cd dashboard
git pull origin main
```

Depois: **Web** → **Reload** 🔄

---

## 🆘 TROUBLESHOOTING

### ❌ Erro 500: "Something went wrong"

**Ver logs:**
1. **Web** → role até **"Log files"**
2. Clique: **"Error log"**
3. Veja últimas linhas do erro

**Causas comuns:**
- Path errado no WSGI (username incorreto)
- .env com path errado (falta barra ou username errado)
- Dependência não instalada

**Solução:**
```bash
# Verificar .env
cat .env

# Reinstalar dependências
pip install --user -r requirements.txt --force-reinstall
```

### ❌ Tabela vazia

**Solução:**
```bash
cd ~/dashboard
rm lacqua_azzurra.db
python migrate_to_postgres.py  # Digite 's'
```
Depois: **Web** → **Reload**

### ❌ "OperationalError: unable to open database"

**Causa:** Path errado no .env (falta barras)

**Solução:**
```bash
nano .env
# Mudar para:
# DATABASE_URL=sqlite:////home/[username]/dashboard/lacqua_azzurra.db
# (4 barras após sqlite:)
```

---

## 📊 ESTRUTURA NO SERVIDOR

```
/home/[seu_username]/
└── dashboard/
    ├── app.py
    ├── models.py
    ├── database.py
    ├── data_processor_postgres.py
    ├── migrate_to_postgres.py
    ├── requirements.txt
    ├── .env
    ├── lacqua_azzurra.db (693 clientes)
    ├── L'Acqua Azzurra Pools Customer report.csv
    ├── assets/
    │   └── styles.css
    └── [outros arquivos]
```

---

## 💰 CUSTO

**R$ 0,00/mês** (plano Beginner FREE)

**Upgrade futuro (opcional):**
- Hacker: $5/mês (100k hits/dia, domínio próprio)
- Web Dev: $12/mês (2 web apps)

---

## 🎯 CHECKLIST FINAL

- [ ] Repositório clonado via Git
- [ ] Arquivo .env criado com path correto
- [ ] Dependências instaladas (requirements.txt)
- [ ] Migração executada (693 clientes)
- [ ] Web App criada (Flask + Python 3.10)
- [ ] Source code configurado
- [ ] WSGI configurado (username correto)
- [ ] App reloaded
- [ ] Dashboard acessível via HTTPS
- [ ] CRUD funcionando (criar, editar, deletar)
- [ ] Filtros e busca operacionais
- [ ] Export CSV funcional

---

## 📞 AJUDA

**Erro persiste?**
1. Copie o erro do **Error log**
2. Envie junto com qual passo você está
3. Inclua seu username do PythonAnywhere

**Tudo funcionou?** 🎉
- Pode pedir reembolso da Hostinger (R$ 12 economizados)
- Use o FREE enquanto funcionar bem
- Upgrade só se precisar de mais recursos

---

## 🚀 EXTRAS (OPCIONAL)

Depois que funcionar:

1. **Domínio próprio**: Upgrade Hacker + configurar DNS
2. **Backup automático**: Scheduled task para backup diário
3. **Monitoramento**: Web → Statistics (CPU usage)
4. **Analytics**: Adicionar Google Analytics no app.py

**Por enquanto: aproveite o FREE! 😎**
