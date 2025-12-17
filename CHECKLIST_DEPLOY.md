# ✅ CHECKLIST DE DEPLOY - PythonAnywhere

## 📋 PRÉ-DEPLOY (Local)

- [ ] Código testado localmente (porta 8051)
- [ ] Salvamento funciona corretamente
- [ ] KPIs atualizando (Faturamento, Clientes, Manutenções)
- [ ] Filtros sem "Carregando..."
- [ ] Todos os arquivos commitados no Git (se usar)

---

## 🚀 DEPLOY PASSO A PASSO

### PASSO 1: Console PythonAnywhere
- [ ] Acessar https://www.pythonanywhere.com/
- [ ] Login com sua conta
- [ ] Abrir "Consoles" → "Bash"

### PASSO 2: Upload de Arquivos
Escolha UMA opção:

**OPÇÃO A - Git (recomendado):**
```bash
cd ~/dashboard
git pull origin main
```

**OPÇÃO B - Upload Manual:**
- [ ] Files → Upload → Selecione TODOS os arquivos alterados:
  - [ ] app.py
  - [ ] data_processor_postgres.py
  - [ ] database.py
  - [ ] models.py
  - [ ] requirements.txt
  - [ ] assets/styles.css
  - [ ] .env (criar manualmente)

### PASSO 3: Criar arquivo .env
```bash
cd ~/dashboard
nano .env
```

**Cole este conteúdo:**
```
DATABASE_URL=postgresql://lacqua_azzurra_db_user:Pzl3jEA1TaInwwbYMh67IEsvjIdUhpfg@dpg-d4snmj7pm1nc73c7dcdg-a.virginia-postgres.render.com/lacqua_azzurra_db
DASH_DEBUG=False
HOST=0.0.0.0
PORT=8000
```

- [ ] Colar conteúdo
- [ ] Salvar: `CTRL+O` → `ENTER`
- [ ] Sair: `CTRL+X`

### PASSO 4: Instalar Dependências
```bash
cd ~/dashboard
pip install --user -r requirements.txt
```

**Aguarde instalação (~2-3 minutos)**

- [ ] Instalação concluída sem erros

### PASSO 5: Testar Conexão
```bash
python3 -c "from database import db; from models import Cliente; print('✅ Banco conectado!'); session = db.get_session().__enter__(); print(f'📊 Clientes: {session.query(Cliente).count()}')"
```

**Resultado esperado:**
```
✅ Banco conectado!
📊 Clientes: 693
```

- [ ] Teste passou (mostrou 693 clientes)

### PASSO 6: Configurar WSGI
- [ ] Ir em "Web" no menu PythonAnywhere
- [ ] Clicar no link "WSGI configuration file"
- [ ] **DELETAR TODO** o conteúdo atual
- [ ] Abrir arquivo `wsgi_pythonanywhere.py` localmente
- [ ] Copiar TODO o conteúdo
- [ ] Colar no editor do PythonAnywhere
- [ ] Trocar `juanleite` pelo seu username (se diferente)
- [ ] Salvar

### PASSO 7: Configurar Virtual Environment (Opcional)
Se você criou um virtualenv:

- [ ] Na página "Web", seção "Virtualenv"
- [ ] Digitar: `/home/juanleite/.virtualenvs/dashboard`

OU criar novo:
```bash
python3 -m venv ~/.virtualenvs/dashboard
source ~/.virtualenvs/dashboard/bin/activate
cd ~/dashboard
pip install -r requirements.txt
```

### PASSO 8: Static Files
Na página "Web" → "Static files":

- [ ] Clicar em "Add a new static file mapping"
- [ ] URL: `/assets/`
- [ ] Directory: `/home/juanleite/dashboard/assets/`
- [ ] Clicar em ✓ (check verde)

### PASSO 9: Reload
- [ ] Na página "Web"
- [ ] Botão verde **"Reload juanleite.pythonanywhere.com"**
- [ ] Aguardar ~10 segundos

### PASSO 10: Testar Produção
- [ ] Abrir nova aba: `https://juanleite.pythonanywhere.com`
- [ ] Página carrega sem erro 500
- [ ] KPIs aparecem com valores corretos
- [ ] Tabela mostra clientes
- [ ] Filtros funcionam (não mostram "Carregando...")
- [ ] Clicar em "Editar" abre modal
- [ ] Salvar alteração funciona
- [ ] Modal fecha automaticamente
- [ ] Dados atualizados aparecem na tabela

---

## 🐛 TROUBLESHOOTING

### Se aparecer erro 500:
```bash
tail -n 100 /var/log/juanleite.pythonanywhere.com.error.log
```

**Erros comuns:**
- ❌ `.env` não existe → Criar arquivo .env no passo 3
- ❌ `DATABASE_URL` vazio → Verificar conteúdo do .env
- ❌ `ModuleNotFoundError` → Instalar requirements.txt
- ❌ `/assets/` não carrega → Configurar static files (passo 8)

### Se não conectar no banco:
```bash
cd ~/dashboard
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DATABASE_URL'))"
```

Deve mostrar: `postgresql://lacqua_azzurra_db_user:...`

### Se assets não carregarem:
```bash
chmod -R 755 ~/dashboard/assets
ls -la ~/dashboard/assets
```

### Verificar logs em tempo real:
```bash
tail -f /var/log/juanleite.pythonanywhere.com.error.log
```

---

## 📊 VALIDAÇÃO FINAL

### Funcionalidades Críticas:
- [ ] Login funciona
- [ ] Dashboard carrega em < 5 segundos
- [ ] Faturamento Mensal: **$215.00** (ou valor atualizado)
- [ ] Clientes Ativos: **304**
- [ ] Manutenções Futuras: **2** (ou mais)
- [ ] Filtro Status mostra: Todos, Ativo, Lead, etc.
- [ ] Filtro Piscineiro mostra: Todos, Drask Silva, Lucca, Pedro Santos, Vini Penner
- [ ] Editar cliente: modal abre em < 1 segundo
- [ ] Salvar: fecha modal em < 2 segundos
- [ ] Valores salvos aparecem sem F5
- [ ] Exportar CSV funciona

---

## 🎉 DEPLOY COMPLETO!

Se todos os checkboxes acima estão marcados, seu deploy foi um sucesso! 🚀

**URL de Produção:** https://juanleite.pythonanywhere.com

---

## 📝 NOTAS IMPORTANTES

1. **Banco Compartilhado:** PostgreSQL Render é usado tanto em DEV quanto PROD
2. **Mudanças de Dados:** Afetam ambiente local E produção
3. **Backups:** Considere fazer backup manual periódico
4. **Logs:** Sempre verifique logs se algo der errado
5. **Cache:** Limpe cache do navegador (CTRL+SHIFT+R) se mudanças não aparecerem

---

## 🔄 PRÓXIMOS DEPLOYS

Para deploys futuros (mais rápidos):

```bash
cd ~/dashboard
git pull  # ou upload manual
pip install --user -r requirements.txt  # só se mudou requirements
# Ir em Web → Reload
```

---

## 📞 CONTATOS ÚTEIS

- Fórum PythonAnywhere: https://www.pythonanywhere.com/forums/
- Render Status: https://render.com/status
- Documentação Dash: https://dash.plotly.com/

---

**Última atualização:** 17/12/2025
**Versão do Dashboard:** v3.3.0
