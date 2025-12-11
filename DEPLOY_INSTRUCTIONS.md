# 🚀 Instruções de Deploy - Atualização Maio 2025

## 📋 Resumo das Alterações

### ✅ Bugs Corrigidos
1. **Datas não salvavam**: Corrigido mapeamento de campos `Ultima Troca` e `Proxima Troca`
2. **Piscineiros não apareciam**: Melhorado `get_technicians()` com filtros e logs

### 🔄 Mudanças na Estrutura
**Colunas Removidas:**
- ❌ `metodo_cobranca` (Método de Cobrança)
- ❌ `auto_pay` (Cobrança Automática)

**Colunas Adicionadas:**
- ✅ `tipo_filtro` (Tipo de Filtro) - VARCHAR(100)
- ✅ `valor_filtro` (Valor do Filtro) - DECIMAL(10,2)

**Outras Mudanças:**
- `valor_rota` foi zerado (não é mais usado)
- Clientes com `status='Inactive'` agora são **filtrados automaticamente** da visualização

### 🎨 UI Atualizada
**Nova estrutura da tabela:**
- Cliente
- Status  
- Piscineiro
- Última Troca
- Próxima Troca
- Tipo Filtro (novo dropdown organizado por marca)
- Valor Filtro (novo campo numérico)

**Dropdown Tipo de Filtro:**
- **Hayward**: C750, C900, C1100, C1200, C1750, C100s, C150s, C200s
- **Pentair**: Cc100, Cc150, Cc200
- **Jandy**: Cs100, Cs150, Cs200, Cs250
- **Outros**: Campo de busca livre

---

## 🔧 Passos para Deploy no PythonAnywhere

### 1️⃣ Fazer Backup do Banco (IMPORTANTE!)

```bash
# Conectar via SSH ou abrir console Bash no PythonAnywhere
cd ~/dashboard

# Fazer backup do banco de dados
cp lacqua_azzurra.db lacqua_azzurra.db.backup.$(date +%Y%m%d_%H%M%S)
```

### 2️⃣ Atualizar Código do Repositório

```bash
cd ~/dashboard

# Puxar atualizações do GitHub
git pull origin main
```

**Saída esperada:**
```
remote: Enumerating objects...
From https://github.com/juanlleite/dash-john-render
 * branch            main       -> FETCH_HEAD
Updating 0371cb7..4b86672
Fast-forward
 app.py                      | 198 +++++++++++++++--------
 data_processor_postgres.py  |  89 ++++++----
 models.py                   |  11 +-
 migrate_schema_filtros.py   | 176 +++++++++++++++++++
 ...
```

### 3️⃣ Executar Migração do Banco de Dados

```bash
# Ativar ambiente virtual
source ~/.virtualenvs/dashboard-env/bin/activate

# Executar script de migração
python migrate_schema_filtros.py -y
```

**Saída esperada:**
```
============================================================
🔄 MIGRAÇÃO DE SCHEMA - L'Acqua Azzurra
============================================================

📝 Alterações:
  ✓ Adicionar: tipo_filtro (VARCHAR 100)
  ✓ Adicionar: valor_filtro (DECIMAL 10,2)
  ✓ Remover: metodo_cobranca
  ✓ Remover: auto_pay
  ✓ Zerar: valor_rota

INFO:__main__:🔧 Iniciando migração do schema...
INFO:__main__:📦 Banco SQLite detectado
INFO:__main__:✅ Tabela clientes_new criada
INFO:__main__:✅ Dados copiados (valor_rota zerado)
INFO:__main__:✅ Tabela antiga removida
INFO:__main__:✅ Tabela renomeada
INFO:__main__:✅ Índices recriados

============================================================
✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!
📊 Total de clientes: 693
============================================================
```

### 4️⃣ Verificar Integridade do Banco

```bash
# Verificar estrutura da tabela
sqlite3 lacqua_azzurra.db "PRAGMA table_info(clientes);"
```

**Saída esperada (deve ter `tipo_filtro` e `valor_filtro`, NÃO deve ter `metodo_cobranca` nem `auto_pay`):**
```
0|id|INTEGER|0||1
1|nome|VARCHAR(255)|1||0
2|status|VARCHAR(50)|1|'Ativo'|0
3|piscineiro|VARCHAR(100)|0|'Não atribuído'|0
4|valor_rota|DECIMAL(10, 2)|0|0.00|0
5|tipo_filtro|VARCHAR(100)|0||0
6|valor_filtro|DECIMAL(10, 2)|0|0.00|0
7|ultima_troca|DATE|0||0
8|proxima_troca|DATE|0||0
9|criado_em|TIMESTAMP|0|CURRENT_TIMESTAMP|0
10|atualizado_em|TIMESTAMP|0|CURRENT_TIMESTAMP|0
```

### 5️⃣ Recarregar Aplicação Web

1. Ir para **Web** no menu do PythonAnywhere
2. Encontrar `juanleite.pythonanywhere.com`
3. Clicar no botão verde **"Reload"** (🔄)
4. Aguardar mensagem "juanleite.pythonanywhere.com has been reloaded"

### 6️⃣ Testar a Aplicação

**Testes obrigatórios:**

1. **Acessar Dashboard:**
   - https://juanleite.pythonanywhere.com
   - https://www.dashboard-lacqua-azzurra.com

2. **Verificar Piscineiros:**
   - Dropdown "Piscineiro" deve mostrar nomes dos técnicos
   - Tabela deve exibir nomes dos piscineiros

3. **Verificar Datas:**
   - Editar um cliente
   - Preencher "Última Troca" e "Próxima Troca"
   - Salvar
   - Verificar se datas aparecem na tabela

4. **Testar Novos Campos:**
   - Editar um cliente
   - Selecionar "Tipo de Filtro" (ex: Hayward C750)
   - Preencher "Valor do Filtro" (ex: 250.00)
   - Salvar
   - Verificar se aparecem na tabela

5. **Verificar Filtros:**
   - Clientes inativos NÃO devem aparecer na tabela
   - Total de clientes deve ser ~467 (693 - 226 inativos)

6. **Verificar Colunas:**
   - Tabela NÃO deve ter "MÉTODO" nem "AUTO PAY"
   - Tabela deve ter "TIPO FILTRO" e "VALOR FILTRO"

---

## 🆘 Troubleshooting

### ❌ Erro: "no such column: metodo_cobranca"
**Causa:** Migração não foi executada
**Solução:** Executar passo 3 novamente

### ❌ Erro: "UNIQUE constraint failed"
**Causa:** Tabela pode estar corrompida
**Solução:**
```bash
# Restaurar backup
cd ~/dashboard
cp lacqua_azzurra.db.backup.YYYYMMDD_HHMMSS lacqua_azzurra.db

# Executar migração novamente
python migrate_schema_filtros.py -y
```

### ❌ Piscineiros ainda não aparecem
**Solução:**
```bash
# Verificar dados no banco
sqlite3 lacqua_azzurra.db "SELECT DISTINCT piscineiro FROM clientes WHERE piscineiro IS NOT NULL AND piscineiro != '' AND piscineiro != 'Não atribuído' LIMIT 10;"

# Se vazio, verificar dados brutos
sqlite3 lacqua_azzurra.db "SELECT piscineiro, COUNT(*) as total FROM clientes GROUP BY piscineiro;"
```

### ❌ Erro 500 após reload
**Solução:**
1. Verificar logs de erro: **Web → Log files → Error log**
2. Procurar por erros de importação ou sintaxe
3. Se encontrar erro em `app.py`, reverter para commit anterior:
```bash
cd ~/dashboard
git reset --hard 0371cb7  # Commit anterior
# Reload web app
```

---

## 📊 Validação Final

Execute o seguinte comando para validar dados:

```bash
sqlite3 lacqua_azzurra.db << 'EOF'
SELECT 
    COUNT(*) as total_clientes,
    SUM(CASE WHEN status = 'Inactive' THEN 1 ELSE 0 END) as inativos,
    SUM(CASE WHEN tipo_filtro IS NOT NULL THEN 1 ELSE 0 END) as com_tipo_filtro,
    SUM(CASE WHEN valor_filtro > 0 THEN 1 ELSE 0 END) as com_valor_filtro,
    SUM(CASE WHEN valor_rota > 0 THEN 1 ELSE 0 END) as valor_rota_nao_zerado
FROM clientes;
EOF
```

**Resultado esperado:**
- `total_clientes`: 693
- `inativos`: ~226
- `com_tipo_filtro`: 0 (ainda não preenchido)
- `com_valor_filtro`: 0 (ainda não preenchido)
- `valor_rota_nao_zerado`: 0 (deve ser zero)

---

## ✅ Checklist de Deploy

- [ ] Backup do banco criado
- [ ] Código atualizado via `git pull`
- [ ] Migração executada com sucesso
- [ ] Estrutura da tabela verificada
- [ ] Web app recarregado
- [ ] Dashboard acessível (ambos URLs)
- [ ] Piscineiros aparecem nos dropdowns
- [ ] Datas salvam e aparecem na tabela
- [ ] Novos campos (Tipo/Valor Filtro) funcionam
- [ ] Clientes inativos filtrados
- [ ] Colunas antigas (Método/Auto Pay) removidas

---

## 📞 Suporte

Se algo der errado:
1. Verificar logs de erro no PythonAnywhere
2. Restaurar backup: `cp lacqua_azzurra.db.backup.XXXXX lacqua_azzurra.db`
3. Reverter código: `git reset --hard 0371cb7`
4. Reload web app

**Commit atual:**
- Hash: `4b86672`
- Mensagem: "Refatorar schema: remover Metodo/AutoPay, adicionar TipoFiltro/ValorFiltro, corrigir bugs datas/piscineiros, filtrar inativos"

**Commit anterior (rollback):**
- Hash: `0371cb7`
