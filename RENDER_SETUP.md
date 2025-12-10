# 🚀 Guia Completo de Setup - Render + PostgreSQL

## 📋 Índice
1. [Criar Banco de Dados PostgreSQL](#1-criar-banco-de-dados-postgresql)
2. [Configurar Web Service](#2-configurar-web-service)
3. [Migrar Dados](#3-migrar-dados)
4. [Configurar Backup Automático](#4-configurar-backup-automático)
5. [Verificar Deploy](#5-verificar-deploy)

---

## 1️⃣ Criar Banco de Dados PostgreSQL

### Passo 1.1: Acessar Dashboard do Render
1. Acesse https://dashboard.render.com
2. Clique em **"New +"** no topo direito
3. Selecione **"PostgreSQL"**

### Passo 1.2: Configurar PostgreSQL
```
Name: lacqua-azzurra-db
Database: lacqua_db
User: (será gerado automaticamente)
Region: Oregon (US West) - ou mais próximo do Brasil
PostgreSQL Version: 16
```

### Passo 1.3: Plano Gratuito
- **Instance Type:** Free
- ✅ Free tier inclui:
  - 256 MB RAM
  - 1 GB de armazenamento
  - 90 dias grátis (auto-renova)
- Clique em **"Create Database"**

### Passo 1.4: Aguardar Provisionamento
- Status: **Creating** → **Available** (1-2 minutos)
- ✅ Quando aparecer "Available", está pronto

### Passo 1.5: Copiar Credenciais
No dashboard do banco, copie:
- **Internal Database URL** (formato: `postgres://...`)
- **External Database URL** (para acesso local)

⚠️ **IMPORTANTE:** Guarde essas URLs em local seguro!

---

## 2️⃣ Configurar Web Service

### Passo 2.1: Acessar seu Web Service
1. No Render Dashboard, clique no seu Web Service existente
2. Vá em **"Environment"** no menu lateral

### Passo 2.2: Adicionar Variável de Ambiente
Clique em **"Add Environment Variable"**

```
Key: DATABASE_URL
Value: [cole a Internal Database URL copiada no passo 1.5]
```

⚠️ **CRÍTICO:** 
- Use a **Internal Database URL** (não a External)
- Formato: `postgres://user:password@dpg-xxxxx/dbname`
- Se começar com `postgres://`, o código vai converter automaticamente para `postgresql://`

### Passo 2.3: Adicionar Outras Variáveis (Opcional)
```
Key: BACKUP_ENABLED
Value: True

Key: DEBUG
Value: False
```

### Passo 2.4: Salvar e Fazer Deploy
- Clique em **"Save Changes"**
- O Render vai fazer **redeploy automático**
- Aguarde 2-3 minutos

---

## 3️⃣ Migrar Dados para PostgreSQL

### Opção A: Migração Local + Push

#### Passo 3.1: Configurar Localmente
No seu computador, crie arquivo `.env`:
```bash
# Copie o .env.example
copy .env.example .env
```

Edite o `.env` e adicione:
```
DATABASE_URL=postgresql://user:password@host/dbname
```
⚠️ Use a **External Database URL** (com acesso público)

#### Passo 3.2: Instalar Dependências
```powershell
# Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1

# Instalar novas dependências
pip install -r requirements.txt
```

#### Passo 3.3: Executar Migração
```powershell
# Migrar dados do CSV para PostgreSQL
python migrate_to_postgres.py
```

✅ **Output esperado:**
```
🔄 MIGRAÇÃO DE DADOS: CSV/JSON → PostgreSQL
✅ CSV carregado: 50 registros
📝 Migrados: 50 clientes...
✅ Migração concluída!
```

#### Passo 3.4: Verificar Dados
```powershell
# Testar conexão
python database.py
```

### Opção B: Migração Direta no Render

#### Passo 3.1: Upload do CSV
1. No Render Dashboard, vá no Web Service
2. **Shell** (menu lateral)
3. Upload do CSV:
```bash
# No shell do Render
ls -la
# Verificar se o CSV está presente
```

#### Passo 3.2: Executar Migração
```bash
python migrate_to_postgres.py
```

---

## 4️⃣ Configurar Backup Automático

### Opção A: Backup Manual (Render Dashboard)
1. Vá no PostgreSQL Database no Render
2. **Backups** (menu lateral)
3. Clique em **"Create Backup"**
4. Backups são mantidos por **7 dias** (plano gratuito)

### Opção B: Backup Automático com Script

#### Passo 4.1: Configurar Cron Job (Render)
Crie arquivo `render_cron.yaml`:
```yaml
services:
  - type: cron
    name: lacqua-backup
    env: python
    schedule: "0 3 * * *"  # Todo dia às 3h AM
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python backup_db.py"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: lacqua-azzurra-db
          property: connectionString
```

#### Passo 4.2: Backup Local
No seu computador:
```powershell
# Criar backup
python backup_db.py

# Listar backups
python backup_db.py list

# Restaurar backup
python backup_db.py restore backups/backup_20241210_120000.sql
```

---

## 5️⃣ Verificar Deploy

### Passo 5.1: Checar Logs do Render
1. No Web Service, vá em **"Logs"**
2. Procure por:
```
✅ Banco de dados configurado
✅ Tabelas criadas/verificadas com sucesso
📊 Total de clientes no banco: 50
Dash is running on http://0.0.0.0:10000/
```

### Passo 5.2: Acessar Dashboard
1. Clique no link do seu app (formato: `https://seu-app.onrender.com`)
2. Verifique se os dados aparecem na tabela
3. Teste:
   - ✅ Filtros (status, piscineiro, mês)
   - ✅ Criar novo cliente
   - ✅ Editar cliente existente
   - ✅ Exportar CSV

### Passo 5.3: Verificar Banco de Dados
No Render Dashboard do PostgreSQL:
1. **"Connect"** (menu lateral)
2. Copie o comando `psql`
3. No seu terminal local:
```bash
psql postgres://user:password@host/dbname
```

SQL para verificar:
```sql
-- Contar clientes
SELECT COUNT(*) FROM clientes;

-- Ver últimos 10 clientes
SELECT id, nome, status, piscineiro, valor_rota 
FROM clientes 
ORDER BY criado_em DESC 
LIMIT 10;

-- Ver auditoria
SELECT * FROM auditoria ORDER BY timestamp DESC LIMIT 10;
```

---

## 🔧 Troubleshooting

### Erro: "relation 'clientes' does not exist"
**Solução:** Executar migração
```bash
python migrate_to_postgres.py
```

### Erro: "could not connect to server"
**Solução:** Verificar DATABASE_URL
- Deve começar com `postgresql://` ou `postgres://`
- Verificar se a URL está correta nas variáveis de ambiente

### Erro: "permission denied for schema public"
**Solução:** Recriar banco de dados no Render

### App não carrega dados
**Solução:**
1. Verificar logs: **Logs** no Render Dashboard
2. Verificar se DATABASE_URL está configurada
3. Executar migração novamente

### Dados não persistem após edição
**Solução:**
1. Verificar conexão com banco
2. Checar logs de erro
3. Verificar se `data_processor.py` foi atualizado para versão PostgreSQL

---

## 📊 Monitoramento

### Métricas do Banco (Render Dashboard)
- **PostgreSQL > Metrics:**
  - Connections
  - Storage Usage
  - CPU/RAM Usage

### Alertas
Configure alertas no Render:
1. PostgreSQL > **Settings**
2. **Notifications**
3. Adicionar email para:
   - Storage 80%
   - Connection limit
   - Database errors

---

## 🎯 Checklist Final

Antes de usar em produção:

- [ ] PostgreSQL criado e **Available**
- [ ] DATABASE_URL configurada no Web Service
- [ ] Migração executada com sucesso
- [ ] Dashboard carrega dados corretamente
- [ ] CRUD funciona (Create, Read, Update)
- [ ] Filtros funcionam
- [ ] Exportar CSV funciona
- [ ] Logs sem erros
- [ ] Backup configurado (manual ou automático)
- [ ] .env não está commitado no Git

---

## 🆘 Suporte

### Links Úteis
- **Render Docs:** https://render.com/docs
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/

### Comandos Rápidos

```powershell
# Desenvolvimento local
python database.py          # Testar conexão
python migrate_to_postgres.py  # Migrar dados
python backup_db.py         # Criar backup
python app.py              # Rodar localmente

# Produção (Render)
# Logs: Dashboard > Web Service > Logs
# Shell: Dashboard > Web Service > Shell
# Database: Dashboard > PostgreSQL > Connect
```

---

## 🎉 Pronto!

Seu dashboard agora está rodando com PostgreSQL no Render:
- ✅ Banco de dados persistente
- ✅ Backup automático (90 dias grátis)
- ✅ Escalonável (se precisar)
- ✅ 100% gratuito

**URL do seu app:** `https://seu-app.onrender.com`

Qualquer problema, consulte este guia ou os logs do Render!
