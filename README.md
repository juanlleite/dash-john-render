# 🏊 L'Acqua Azzurra Pools - Dashboard Profissional

Dashboard interativo e elegante para gerenciamento de clientes e manutenções de piscinas, desenvolvido com Dash, Plotly, Bootstrap e CSS customizado.

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![Dash](https://img.shields.io/badge/Dash-Latest-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Características Principais

### 📊 KPIs em Destaque
- **💰 Faturamento Mensal**: Visualização em tempo real do faturamento total
- **👥 Clientes Ativos**: Contagem de clientes com serviço ativo
- **🔧 Manutenções Futuras**: Número de manutenções agendadas

### 🎯 Funcionalidades

#### 1. **Filtros Avançados**
- Filtro por **Status** (Active, Inactive, Lead)
- Filtro por **Piscineiro** (4 técnicos disponíveis: Lucca, Pedro Santos, Drask Silva, Vini Penner)
- Filtro por **Mês** (para visualização de manutenções futuras)

#### 2. **Visualização de Dados**
- Tabela interativa com todos os clientes
- Colunas: Nome, Status, Piscineiro, Valor da Rota, Método de Pagamento, Última Troca, Próxima Troca, Telefone, Email
- Ordenação e busca nativa
- Paginação automática

#### 3. **Gráficos Profissionais**
- **Gráfico de Barras**: Faturamento por Piscineiro
- **Gráfico de Pizza**: Distribuição de clientes por status
- Design elegante com paleta de cores azul água

#### 4. **Sistema de Edição**
- Seleção de cliente via dropdown
- Edição de campos:
  - Última Troca (data)
  - Próxima Troca (data)
- Salvamento persistente em arquivo JSON
- Feedback visual de sucesso

#### 5. **Design Elegante**
- Interface moderna e profissional
- Tema azul água (cores da marca)
- Animações suaves
- Responsivo (desktop, tablet, mobile)
- Scrollbar customizada
- Cards com sombras e gradientes

## 🚀 Como Usar

### Pré-requisitos
- Python 3.7+
- pip (gerenciador de pacotes Python)

### Instalação

1. **Clone ou acesse a pasta do projeto:**
```bash
cd "c:\Users\Juan\Documents\john"
```

2. **O ambiente virtual já está configurado!** Os pacotes necessários já foram instalados:
   - dash
   - plotly
   - pandas
   - dash-bootstrap-components
   - openpyxl

### Executar o Dashboard

```bash
C:/Users/Juan/Documents/john/.venv/Scripts/python.exe app.py
```

Ou simplesmente:
```bash
python app.py
```

O dashboard estará disponível em: **http://127.0.0.1:8050**

## 📁 Estrutura do Projeto

```
john/
├── app.py                          # Aplicação principal do dashboard
├── data_processor.py               # Processamento e manipulação de dados
├── data_storage.json               # Armazenamento de dados editados (criado automaticamente)
├── L'Acqua Azzurra Pools Customer report-171125135257 - Sheet.csv
├── assets/
│   └── styles.css                  # Estilos customizados
├── .venv/                          # Ambiente virtual Python
└── README.md                       # Este arquivo
```

## 🎨 Paleta de Cores

- **Primária**: #0077be (Azul água)
- **Primária Escura**: #005a8d
- **Primária Clara**: #4da6d6
- **Secundária**: #00b4d8
- **Accent**: #90e0ef
- **Sucesso**: #06d6a0
- **Aviso**: #ffd166
- **Perigo**: #ef476f

## 📝 Como Editar Informações de Clientes

1. Acesse o dashboard
2. Na seção "Lista de Clientes", use o dropdown para selecionar um cliente
3. O formulário de edição aparecerá automaticamente
4. Preencha os campos desejados:
   - **Última Troca**: Data da última manutenção (formato: DD/MM/AAAA)
   - **Próxima Troca**: Data agendada para próxima manutenção (formato: DD/MM/AAAA)
5. Clique em "💾 Salvar Alterações"
6. As informações serão salvas permanentemente no arquivo `data_storage.json`

## 🔄 Atualização de Dados

- Clique no botão "🔄 Atualizar Dados" para recarregar os dados do CSV
- As edições manuais são preservadas no arquivo JSON
- Os filtros são aplicados automaticamente após atualização

## 📊 Dados Exibidos

### Informações de Clientes
- **Nome**: Nome completo do cliente
- **Status**: Active (routed), Inactive, Lead, etc.
- **Piscineiro**: Técnico responsável (Lucca, Pedro Santos, Drask Silva, Vini Penner)
- **Valor da Rota**: Preço do serviço mensal
- **Método de Pagamento**: Advance, Arrears, etc.
- **Última Troca**: Data da última manutenção (editável)
- **Próxima Troca**: Data da próxima manutenção (editável)
- **Telefone**: Número de contato
- **Email**: Email de contato

### Piscineiros Disponíveis
1. **Lucca .**
2. **Pedro Santos**
3. **Drask Silva**
4. **Vini Penner**

## 🛠️ Tecnologias Utilizadas

- **Python 3.13**: Linguagem de programação
- **Dash**: Framework para dashboards interativos
- **Plotly**: Biblioteca de visualização de dados
- **Pandas**: Manipulação e análise de dados
- **Bootstrap**: Framework CSS responsivo
- **CSS3**: Estilização customizada

## 💡 Dicas de Uso

1. **Filtros**: Use os filtros combinados para análises específicas
2. **Tabela**: Clique nos cabeçalhos para ordenar os dados
3. **Busca**: Use a busca nativa da tabela para encontrar clientes rapidamente
4. **Edição**: As edições são salvas automaticamente e persistem entre sessões
5. **Gráficos**: Passe o mouse sobre os gráficos para ver detalhes

## 🔒 Segurança dos Dados

- Os dados originais do CSV **não são modificados**
- As edições são salvas em um arquivo JSON separado (`data_storage.json`)
- É possível excluir o arquivo JSON para resetar todas as edições

## 🐛 Resolução de Problemas

### O dashboard não inicia
- Verifique se todos os pacotes estão instalados
- Confirme que está usando o Python correto do ambiente virtual

### Dados não aparecem
- Verifique se o arquivo CSV está na mesma pasta que `app.py`
- Confirme o nome do arquivo CSV no código

### Edições não são salvas
- Verifique as permissões de escrita na pasta
- Confirme que o arquivo `data_storage.json` pode ser criado

## 📞 Suporte

Para dúvidas ou sugestões sobre o dashboard, consulte a documentação ou entre em contato.

## 📄 Licença

Este projeto foi desenvolvido para uso interno da L'Acqua Azzurra Pools.

---

**Desenvolvido com ❤️ para L'Acqua Azzurra Pools** 🏊‍♂️
