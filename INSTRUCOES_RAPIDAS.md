# 🚀 INSTRUÇÕES RÁPIDAS - Dashboard L'Acqua Azzurra Pools

## ⚡ Iniciar o Dashboard

### Opção 1: Comando Simples
```bash
python app.py
```

### Opção 2: Comando Completo
```bash
C:/Users/Juan/Documents/john/.venv/Scripts/python.exe app.py
```

## 🌐 Acessar o Dashboard

Após iniciar, abra seu navegador e acesse:
```
http://127.0.0.1:8050
```

## 🛑 Parar o Dashboard

Pressione `CTRL + C` no terminal onde o dashboard está rodando.

## 📋 Funcionalidades Rápidas

### 1️⃣ Visualizar KPIs
- **Faturamento Mensal**: Topo da página, primeiro card
- **Clientes Ativos**: Topo da página, segundo card  
- **Manutenções Futuras**: Topo da página, terceiro card

### 2️⃣ Filtrar Dados
Use os 3 dropdowns na seção "Filtros de Busca":
- **Status**: Filtra por tipo de cliente (Active, Inactive, Lead)
- **Piscineiro**: Filtra por técnico (Lucca, Pedro Santos, Drask Silva, Vini Penner)
- **Mês**: Filtra por mês (Janeiro a Dezembro)

### 3️⃣ Editar Informações de Clientes
1. Vá até "Lista de Clientes"
2. Selecione um cliente no dropdown
3. Preencha os campos que aparecem:
   - **Última Troca**: ex: 15/11/2024
   - **Próxima Troca**: ex: 15/12/2024
4. Clique em "💾 Salvar Alterações"
5. ✅ Confirmação aparecerá em verde!

### 4️⃣ Atualizar Dados
Clique no botão "🔄 Atualizar Dados" para recarregar os dados do CSV.

## 📊 Gráficos Disponíveis

1. **Faturamento por Piscineiro** (Barras)
   - Mostra quanto cada técnico gera de receita

2. **Distribuição de Clientes por Status** (Pizza)
   - Mostra quantidade de clientes por categoria

## 🔍 Tabela de Clientes

### Recursos da Tabela:
- ✅ **Ordenação**: Clique nos cabeçalhos para ordenar
- ✅ **Busca**: Digite no campo de filtro
- ✅ **Paginação**: 20 clientes por página
- ✅ **Seleção**: Clique em uma linha para selecionar

### Colunas Exibidas:
1. Nome
2. Status
3. Piscineiro
4. Valor da Rota
5. Método Pagamento
6. Última Troca
7. Próxima Troca
8. Telefone
9. Email

## 💾 Onde os Dados São Salvos?

- **Dados Originais**: `L'Acqua Azzurra Pools Customer report-171125135257 - Sheet.csv` (NÃO é modificado)
- **Edições Manuais**: `data_storage.json` (criado automaticamente)

## ⚠️ Dicas Importantes

1. ✅ Sempre use formato de data: DD/MM/AAAA
2. ✅ As edições são salvas permanentemente
3. ✅ Você pode editar quantos clientes quiser
4. ✅ Para resetar edições, delete o arquivo `data_storage.json`

## 🎨 Características do Design

- 🎨 Tema: Azul Água (cores da piscina)
- ✨ Animações suaves
- 📱 Responsivo (funciona em celular, tablet e desktop)
- 🖱️ Interativo (hover effects, sombras)
- 🔝 Profissional e elegante

## 📞 Problemas Comuns

### Dashboard não abre
- ✅ Verifique se rodou o comando `python app.py`
- ✅ Espere alguns segundos após iniciar
- ✅ Confirme que não há outro programa usando a porta 8050

### Erro ao salvar dados
- ✅ Verifique se tem permissão de escrita na pasta
- ✅ Certifique-se que preencheu os campos corretamente

### Dados não aparecem
- ✅ Verifique se o arquivo CSV está na mesma pasta
- ✅ Clique no botão "Atualizar Dados"

---

**🏊 Desenvolvido para L'Acqua Azzurra Pools**  
**✨ Dashboard Profissional e Elegante**
