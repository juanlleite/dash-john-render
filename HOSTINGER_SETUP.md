# 🚀 GUIA COMPLETO - DEPLOY NA HOSTINGER

## ✅ PRÉ-REQUISITOS
- ✅ Plano Premium Hostinger contratado
- ✅ Acesso ao cPanel
- ✅ Arquivos do projeto no computador

---

## 📋 PARTE 1: CONFIGURAR BANCO DE DADOS MYSQL (10 min)

### 1.1 - Acessar cPanel
1. Acesse: https://hpanel.hostinger.com
2. Login com suas credenciais
3. Clique em **"Painel de controle"** → **"cPanel avançado"**

### 1.2 - Criar Banco de Dados MySQL
1. No cPanel, procure por **"MySQL Databases"** ou **"Bancos de dados MySQL"**

2. **Criar Banco:**
   - Em "Create New Database"
   - Nome: `lacqua_azzurra`
   - Clique **"Create Database"**

3. **Criar Usuário:**
   - Em "MySQL Users" → "Add New User"
   - Username: `lacqua_user`
   - Password: **[CRIE UMA SENHA FORTE E ANOTE!]**
   - Clique **"Create User"**

4. **Adicionar Usuário ao Banco:**
   - Em "Add User to Database"
   - User: selecione `lacqua_user`
   - Database: selecione `lacqua_azzurra`
   - Clique **"Add"**
   - Marque **"ALL PRIVILEGES"**
   - Clique **"Make Changes"**

5. **ANOTAR CREDENCIAIS:**
   ```
   Database Name: [cpanel_user]_lacqua_azzurra
   Username: [cpanel_user]_lacqua_user
   Password: [sua senha forte]
   Host: localhost
   ```
   
   Exemplo real:
   ```
   Database Name: u123456_lacqua_azzurra
   Username: u123456_lacqua_user
   Password: MinhaSenha123!@#
   Host: localhost
   ```

---

## 📋 PARTE 2: PREPARAR ARQUIVOS LOCALMENTE (5 min)

### 2.1 - Criar arquivo `.env`

Na pasta do projeto local (`C:\Users\Juan\Documents\john`), crie o arquivo `.env`:

```env
# SUBSTITUIR pelos seus dados reais do MySQL!
DATABASE_URL=mysql+pymysql://[cpanel_user]_lacqua_user:[SUA_SENHA]@localhost/[cpanel_user]_lacqua_azzurra

# Exemplo real (SUBSTITUA com suas credenciais):
# DATABASE_URL=mysql+pymysql://u123456_lacqua_user:MinhaSenha123!@#@localhost/u123456_lacqua_azzurra
```

⚠️ **IMPORTANTE:** Use o formato exato: `mysql+pymysql://usuario:senha@localhost/banco`

### 2.2 - Instalar PyMySQL localmente (teste opcional)

```powershell
pip install PyMySQL cryptography
```

---

## 📋 PARTE 3: FAZER UPLOAD DOS ARQUIVOS (10 min)

### 3.1 - Arquivos para enviar

**✅ ENVIAR estes arquivos:**
```
app.py
models.py
database.py
data_processor_postgres.py
migrate_to_postgres.py
passenger_wsgi.py
requirements.txt
.env
gunicorn_config.py
L'Acqua Azzurra Pools Customer report-171125135257 - Sheet.csv
assets/
  ├── styles.css
  └── [outros arquivos da pasta assets]
```

**❌ NÃO enviar:**
```
.git/
.gitignore
__pycache__/
.venv/
*.pyc
*.db
README*.md
render.yaml
Procfile
backup_db.py
```

### 3.2 - Upload via File Manager (RECOMENDADO)

1. No cPanel, clique em **"File Manager"**
2. Navegue até `public_html/`
3. Crie uma pasta chamada `dashboard`:
   - Clique **"+ Folder"**
   - Nome: `dashboard`
   - Clique **"Create New Folder"**
4. Entre na pasta `dashboard`
5. Clique **"Upload"** (botão no topo)
6. Arraste TODOS os arquivos listados acima
7. Aguarde upload completo (pode demorar 2-3 minutos)

---

## 📋 PARTE 4: CONFIGURAR PYTHON NO cPANEL (10 min)

### 4.1 - Criar Aplicação Python

1. No cPanel, procure por **"Setup Python App"** ou **"Python"**
2. Clique em **"Create Application"**
3. Configure:

```
Python Version: 3.9 (ou a mais recente disponível: 3.10, 3.11)
Application Root: dashboard
Application URL: / (ou escolha /dashboard se preferir)
Application startup file: passenger_wsgi.py
Application Entry point: application
```

4. Clique **"Create"**
5. Aguarde criação (30-60 segundos)

### 4.2 - Instalar Dependências

1. Após criar, você verá um botão **"Enter to the virtual environment"**
2. Clique nele - abrirá um terminal
3. No terminal, execute:

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

⏳ **Aguarde 3-5 minutos** para instalação completa

4. Verificar instalação:
```bash
pip list | grep -E "dash|sqlalchemy|pymysql"
```

Deve mostrar:
```
dash                        2.18.2
dash-bootstrap-components   1.6.0
SQLAlchemy                  2.0.36
PyMySQL                     1.1.1
```

---

## 📋 PARTE 5: AJUSTAR passenger_wsgi.py (3 min)

### 5.1 - Editar passenger_wsgi.py

1. No **File Manager**, navegue até `public_html/dashboard/`
2. Clique com botão direito em `passenger_wsgi.py`
3. Selecione **"Edit"**
4. Encontre a linha:
   ```python
   INTERP = os.path.join(
       os.environ['HOME'],
       'virtualenv',
       'dashboard',  # Nome da pasta
       '3.9',  # Versão do Python
   ```

5. **AJUSTE se necessário:**
   - Se sua pasta não é `dashboard`, altere
   - Se escolheu Python 3.10, mude `'3.9'` para `'3.10'`

6. Clique **"Save Changes"**

---

## 📋 PARTE 6: MIGRAR DADOS PARA MYSQL (5 min)

### 6.1 - Executar migração

1. No terminal do virtualenv (ainda aberto do passo 4.2):

```bash
# Confirmar que .env está correto
cat .env

# Executar migração
python migrate_to_postgres.py
```

2. Quando perguntar:
   ```
   Deseja continuar com a migração? (s/n):
   ```
   Digite: `s` e pressione Enter

3. Aguarde a migração:
   ```
   ✅ Migração do CSV concluída:
   • Migrados: 693
   • Pulados: 14 (duplicatas)
   ```

### 6.2 - Verificar migração

```bash
# Verificar dados no banco
python -c "from database import db; from models import Cliente; \
with db.get_session() as s: print(f'Total clientes: {s.query(Cliente).count()}')"
```

Deve mostrar: `Total clientes: 693`

---

## 📋 PARTE 7: RESTART E TESTE (2 min)

### 7.1 - Restart da aplicação

1. Volte para **"Setup Python App"** no cPanel
2. Encontre sua aplicação `dashboard`
3. Clique no ícone **⟳ Restart** (ao lado direito)
4. Aguarde ~30 segundos

### 7.2 - Testar no navegador

1. Acesse: `https://seudominio.com/` (ou `https://seudominio.com/dashboard`)

2. ✅ **VERIFICAR:**
   - [ ] Página carrega sem erro 500
   - [ ] KPIs aparecem:
     - Faturamento Mensal
     - Clientes Ativos
     - Manutenções Futuras
   - [ ] Tabela mostra clientes
   - [ ] Filtros funcionam (Status, Piscineiro, Mês)
   - [ ] Busca por nome funciona
   - [ ] Botão "Editar" abre modal
   - [ ] Botão "Novo Cliente" abre modal
   - [ ] "Exportar CSV" funciona

---

## 🆘 TROUBLESHOOTING

### ❌ Erro: "Internal Server Error" (500)

**Solução 1: Verificar logs**
```bash
# No terminal virtualenv
tail -50 ~/logs/[nome_app]_error.log
```

**Solução 2: Verificar .env**
- Conferir se DATABASE_URL está correto
- Formato: `mysql+pymysql://usuario:senha@localhost/banco`
- Senha deve estar URL-encoded se tiver caracteres especiais

**Solução 3: Verificar passenger_wsgi.py**
```bash
# Testar manualmente
python passenger_wsgi.py
```

### ❌ Erro: "Can't connect to MySQL server"

**Solução: Corrigir DATABASE_URL**
```env
# Formato correto:
DATABASE_URL=mysql+pymysql://[cpanel_user]_lacqua_user:[senha]@localhost/[cpanel_user]_lacqua_azzurra

# Exemplo:
DATABASE_URL=mysql+pymysql://u123456_lacqua_user:SenhaForte123@localhost/u123456_lacqua_azzurra
```

### ❌ Erro: "Module not found"

**Solução: Reinstalar dependências**
```bash
# Entrar no virtualenv
cd ~/virtualenv/dashboard/3.9/bin
source activate

# Reinstalar
pip install -r ~/public_html/dashboard/requirements.txt
```

### ⚠️ Tabela carrega vazia

**Solução: Rodar migração novamente**
```bash
cd ~/public_html/dashboard
python migrate_to_postgres.py
```

### ⚠️ SSL/HTTPS não funciona

**Solução: Ativar SSL no cPanel**
1. cPanel → **"SSL/TLS Status"**
2. Selecionar seu domínio
3. Clique **"Run AutoSSL"**
4. Aguarde 5-10 minutos

---

## 📊 ESTRUTURA FINAL NO SERVIDOR

```
/home/[cpanel_user]/
├── public_html/
│   └── dashboard/
│       ├── app.py
│       ├── models.py
│       ├── database.py
│       ├── data_processor_postgres.py
│       ├── migrate_to_postgres.py
│       ├── passenger_wsgi.py
│       ├── requirements.txt
│       ├── .env (com DATABASE_URL do MySQL)
│       ├── L'Acqua Azzurra Pools Customer report.csv
│       └── assets/
│           └── styles.css
└── virtualenv/
    └── dashboard/
        └── 3.9/
            └── lib/python3.9/site-packages/
                ├── dash/
                ├── sqlalchemy/
                ├── pymysql/
                └── [outras dependências]
```

---

## ✅ CHECKLIST FINAL

Antes de considerar concluído:

- [ ] MySQL database criado
- [ ] Usuário MySQL criado e com privilégios
- [ ] Arquivo `.env` com DATABASE_URL correto
- [ ] Arquivos enviados via File Manager
- [ ] Python App criada no cPanel (Python 3.9+)
- [ ] requirements.txt instalado (dash, sqlalchemy, pymysql)
- [ ] passenger_wsgi.py ajustado com paths corretos
- [ ] Migração executada (693 clientes no MySQL)
- [ ] App reiniciado
- [ ] Dashboard acessível via HTTPS
- [ ] Todos recursos funcionando (CRUD, filtros, export)
- [ ] SSL ativo (cadeado verde no navegador)

---

## 🎯 RESULTADO FINAL

✅ **Dashboard rodando em:**
```
https://seudominio.com/
```

✅ **Com:**
- 693 clientes no MySQL
- RAM ilimitada (Hostinger Premium)
- Sempre ativo (não hiberna)
- Backup semanal automático
- SSL/HTTPS ativo
- Performance profissional
- Domínio próprio

---

## 💰 CUSTO MENSAL

**R$ 11,99/mês** = Tudo incluído:
- Hosting ilimitado
- MySQL 100 databases
- 100 GB SSD
- SSL grátis
- Domínio grátis (primeiro ano)
- Email profissional
- Backup automático
- Suporte 24/7

---

## 📞 PRECISA DE AJUDA?

Se encontrar qualquer problema:
1. Copie a mensagem de erro completa
2. Verifique os logs: `tail -50 ~/logs/[app]_error.log`
3. Me envie o erro e qual passo você está

**Boa sorte com o deploy! 🚀**
