# 🚀 Deploy no Render - Dashboard L'Acqua Azzurra

## Guia Completo de Deployment

### 📋 Pré-requisitos

- Conta no [Render](https://render.com)
- Repositório no GitHub: `https://github.com/juanlleite/dash-john-render.git`
- Arquivos de produção configurados (✅ já prontos neste projeto)

### 🎯 Passo a Passo

#### 1. **Preparar o Repositório**

O projeto já está configurado com todos os arquivos necessários:

- ✅ `requirements.txt` - Dependências Python
- ✅ `Procfile` - Comando de inicialização
- ✅ `render.yaml` - Configuração automática do Render
- ✅ `.gitignore` - Arquivos ignorados
- ✅ `app.py` - Servidor Flask exposto via `server = app.server`

#### 2. **Fazer Push para o GitHub**

```bash
git add .
git commit -m "Estrutura de produção configurada para Render"
git push origin main
```

#### 3. **Criar Web Service no Render**

**Opção A: Deploy Automático (Recomendado)**

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub: `juanlleite/dash-john-render`
4. O Render detectará automaticamente o `render.yaml`
5. Clique em **"Apply"** - tudo será configurado automaticamente!

**Opção B: Configuração Manual**

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório: `juanlleite/dash-john-render`
4. Configure:
   - **Name**: `dashboard-lacqua-azzurra`
   - **Region**: Oregon (Free)
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: 
     ```
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```
     gunicorn app:server --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
     ```
   - **Plan**: Free

5. Adicione **Environment Variables**:
   - `DASH_DEBUG` = `false`
   - `DASH_DEV_TOOLS_HOT_RELOAD` = `false`
   - `PYTHON_VERSION` = `3.13.5`

6. Clique em **"Create Web Service"**

#### 4. **Aguardar o Deploy**

- O Render irá:
  1. Clonar seu repositório
  2. Instalar dependências (`requirements.txt`)
  3. Executar o comando de start com Gunicorn
  4. Gerar uma URL pública (ex: `https://dashboard-lacqua-azzurra.onrender.com`)

⏱️ Primeiro deploy: ~2-5 minutos

#### 5. **Acessar o Dashboard**

Após o deploy bem-sucedido, acesse a URL fornecida pelo Render:

```
https://seu-app.onrender.com
```

### 🔧 Configurações Importantes

#### Variáveis de Ambiente no Render

No painel do Render, em **Environment**, adicione:

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `DASH_DEBUG` | `false` | Desativa debug em produção |
| `DASH_DEV_TOOLS_HOT_RELOAD` | `false` | Desativa hot reload |
| `PORT` | *(automático)* | Render define automaticamente |

#### Persistência de Dados

⚠️ **IMPORTANTE**: O Render Free Tier não garante persistência de disco!

**Soluções**:
1. **Curto prazo**: Os dados em `data_storage.json` e CSV funcionarão, mas podem ser perdidos em reinicializações
2. **Longo prazo** (recomendado):
   - Migrar para banco de dados PostgreSQL (Render oferece free tier)
   - Usar serviço de storage (AWS S3, Cloudinary, etc.)
   - Configurar backups automáticos

### 📊 Monitoramento

No painel do Render você pode:

- Ver logs em tempo real
- Monitorar uso de recursos
- Configurar alertas
- Ver histórico de deploys
- Reiniciar serviço manualmente

### 🔄 Atualizações Automáticas

Qualquer push para a branch `main` irá:
1. Trigger automático de novo deploy
2. Rebuild da aplicação
3. Deploy sem downtime

### 🆓 Limitações do Plano Free

- **750 horas/mês** de runtime
- **Inatividade**: App dorme após 15min sem uso
- **Cold Start**: ~30s para acordar
- **Disco**: Não persistente (dados podem ser perdidos)

💡 **Dica**: Para manter o app acordado, use serviços como [UptimeRobot](https://uptimerobot.com) para fazer ping a cada 10 minutos.

### 🚨 Troubleshooting

#### App não inicia

```bash
# Verificar logs no Render Dashboard
# Procurar por erros de dependências ou imports
```

**Soluções comuns**:
- Verificar se `requirements.txt` está completo
- Confirmar que `server = app.server` existe em `app.py`
- Checar se arquivos CSV/JSON existem no repositório

#### Erro de módulo não encontrado

```bash
# Adicionar módulo faltante ao requirements.txt
pip freeze | grep nome-do-modulo >> requirements.txt
git add requirements.txt
git commit -m "Adiciona dependência faltante"
git push
```

#### App muito lento

- Upgrade para plano pago (mais workers)
- Otimizar queries de dados
- Implementar cache com Redis

### 📝 Comandos Úteis Localmente

```bash
# Testar localmente em modo produção
DASH_DEBUG=false gunicorn app:server --bind 0.0.0.0:8050

# Instalar dependências de produção
pip install -r requirements.txt

# Verificar sintaxe Python
python -m py_compile app.py data_processor.py

# Rodar testes (se houver)
pytest tests/
```

### 🔒 Segurança

Para adicionar autenticação:

1. Instale `dash-auth`:
   ```bash
   pip install dash-auth
   ```

2. Configure em `app.py`:
   ```python
   import dash_auth
   
   VALID_USERNAME_PASSWORD_PAIRS = {
       'admin': 'senha-segura'
   }
   
   auth = dash_auth.BasicAuth(
       app,
       VALID_USERNAME_PASSWORD_PAIRS
   )
   ```

3. Adicione credenciais via Environment Variables no Render

### 📚 Recursos Adicionais

- [Documentação Render](https://render.com/docs)
- [Guia Dash Deployment](https://dash.plotly.com/deployment)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)
- [Suporte Render](https://community.render.com)

### ✅ Checklist Final

- [ ] Push de todos os arquivos para GitHub
- [ ] Criar Web Service no Render
- [ ] Configurar variáveis de ambiente
- [ ] Aguardar deploy completar
- [ ] Testar URL pública
- [ ] Configurar monitoramento (opcional)
- [ ] Configurar uptime monitor (opcional)
- [ ] Planejar migração de dados para BD (recomendado)

---

**🎉 Pronto! Seu dashboard está em produção!**

Acesse: `https://seu-app.onrender.com`
