# 🎨 GUIA DE PERSONALIZAÇÃO - Dashboard L'Acqua Azzurra Pools

## 🎨 Como Mudar as Cores do Dashboard

### Arquivo: `assets/styles.css`

Localize a seção de variáveis (linhas 9-20):

```css
:root {
    --primary-color: #0077be;        /* Azul principal */
    --primary-dark: #005a8d;         /* Azul escuro */
    --primary-light: #4da6d6;        /* Azul claro */
    --secondary-color: #00b4d8;      /* Azul secundário */
    --accent-color: #90e0ef;         /* Azul accent */
    --success-color: #06d6a0;        /* Verde sucesso */
    --warning-color: #ffd166;        /* Amarelo aviso */
    --danger-color: #ef476f;         /* Vermelho perigo */
}
```

### Exemplo: Mudar para tema verde

```css
:root {
    --primary-color: #10b981;        /* Verde principal */
    --primary-dark: #059669;         /* Verde escuro */
    --primary-light: #34d399;        /* Verde claro */
    --secondary-color: #14b8a6;      /* Verde água */
    --accent-color: #5eead4;         /* Verde accent */
}
```

---

## 📝 Como Adicionar Novos Campos Editáveis

### 1. Atualizar `app.py` (adicionar campo no formulário)

Localize a seção de edição (linha ~175) e adicione:

```python
dbc.Col([
    html.Label("Novo Campo:", className="edit-form-label"),
    dcc.Input(
        id="edit-novo-campo",
        type="text",
        placeholder="Digite aqui...",
        className="form-control edit-form-input"
    )
], md=4),
```

### 2. Atualizar callback de salvamento

Adicione o novo campo no callback `save_customer_data`:

```python
@app.callback(
    Output("save-feedback", "children"),
    [Input("save-button", "n_clicks")],
    [State("customer-select", "value"),
     State("edit-ultima-troca", "value"),
     State("edit-proxima-troca", "value"),
     State("edit-novo-campo", "value")]  # NOVO
)
def save_customer_data(n_clicks, customer_name, ultima_troca, 
                       proxima_troca, novo_campo):  # NOVO
    # ... código existente ...
    if novo_campo:
        data_processor.update_customer_data(customer_name, "Novo Campo", novo_campo)
```

### 3. Adicionar à tabela (opcional)

Em `data_processor.py`, método `get_display_dataframe`, adicione:

```python
display_cols = ['Name', 'Status', ..., 'Novo Campo']
```

---

## 📊 Como Adicionar Novos Gráficos

### Exemplo: Gráfico de Linha (Evolução Mensal)

Em `app.py`, adicione na seção de gráficos:

```python
dbc.Col([
    html.Div([
        html.H5("📈 Evolução Mensal", className="chart-title"),
        dcc.Graph(id="monthly-evolution-chart")
    ], className="chart-card fade-in")
], md=12)
```

Crie o callback para popular o gráfico:

```python
@app.callback(
    Output("monthly-evolution-chart", "figure"),
    [Input("refresh-button", "n_clicks")]
)
def update_monthly_chart(n_clicks):
    # Seus dados aqui
    fig = px.line(df, x="mes", y="faturamento", title="")
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Poppins, sans-serif")
    )
    return fig
```

---

## 🔍 Como Adicionar Novos Filtros

### Em `app.py`, seção de filtros:

```python
dbc.Col([
    html.Label("Novo Filtro:", className="edit-form-label"),
    dcc.Dropdown(
        id="novo-filtro",
        options=[
            {"label": "Opção 1", "value": "opt1"},
            {"label": "Opção 2", "value": "opt2"}
        ],
        value="opt1",
        clearable=False,
        className="mb-3"
    )
], md=3)
```

### Atualizar callback principal:

```python
@app.callback(
    [...],
    [Input("status-filter", "value"),
     Input("tech-filter", "value"),
     Input("month-filter", "value"),
     Input("novo-filtro", "value")]  # NOVO
)
def update_dashboard(status_filter, tech_filter, month_filter, novo_filtro):
    # Aplicar novo filtro
    if novo_filtro != "todos":
        filtered_df = filtered_df[filtered_df['Coluna'] == novo_filtro]
```

---

## 📱 Como Ajustar Layout Responsivo

### Em `assets/styles.css`, adicione media queries:

```css
/* Para tablets */
@media (max-width: 992px) {
    .kpi-container {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Para celulares */
@media (max-width: 576px) {
    .dashboard-title {
        font-size: 1.5rem;
    }
    
    .kpi-value {
        font-size: 1.8rem;
    }
}
```

---

## 🔔 Como Adicionar Notificações

### Exemplo: Alerta de Manutenção Próxima

Em `app.py`, adicione um componente de alerta:

```python
# No layout
html.Div(id="alert-notifications", className="mb-3")

# Callback
@app.callback(
    Output("alert-notifications", "children"),
    [Input("refresh-button", "n_clicks")]
)
def check_notifications(n_clicks):
    # Lógica para verificar manutenções próximas
    upcoming = data_processor.get_upcoming_maintenance(days=7)
    
    if upcoming > 0:
        return dbc.Alert(
            f"⚠️ {upcoming} manutenções agendadas para os próximos 7 dias!",
            color="warning",
            dismissable=True
        )
    return ""
```

---

## 🎯 Como Mudar Configurações do Servidor

### Em `config.py`:

```python
# Mudar porta
PORT = 8080  # ao invés de 8050

# Mudar host (para aceitar conexões externas)
HOST = "0.0.0.0"

# Desativar debug em produção
DEBUG = False
```

### Em `app.py`:

```python
app.run(debug=False, host="0.0.0.0", port=8080)
```

---

## 📊 Como Exportar Dados

### Adicionar botão de exportação:

```python
# No layout
dbc.Button("📥 Exportar CSV", id="export-button", color="info")

# Callback
@app.callback(
    Output("download-data", "data"),
    [Input("export-button", "n_clicks")],
    prevent_initial_call=True
)
def export_data(n_clicks):
    return dcc.send_data_frame(filtered_df.to_csv, "clientes.csv")
```

---

## 🔐 Como Adicionar Autenticação

### Instalar Dash Auth:

```bash
pip install dash-auth
```

### Em `app.py`:

```python
import dash_auth

# Usuários e senhas
VALID_USERS = {
    'admin': 'senha123',
    'usuario': 'senha456'
}

auth = dash_auth.BasicAuth(
    app,
    VALID_USERS
)
```

---

## 🎨 Como Mudar a Fonte

### Em `assets/styles.css`:

```css
/* Importar nova fonte */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

/* Aplicar */
body {
    font-family: 'Montserrat', sans-serif;
}
```

---

## 📧 Como Adicionar Envio de Email

### Instalar biblioteca:

```bash
pip install yagmail
```

### Criar função de envio:

```python
import yagmail

def send_email(to, subject, body):
    yag = yagmail.SMTP('seu_email@gmail.com', 'sua_senha')
    yag.send(to=to, subject=subject, contents=body)
```

---

## 💡 DICAS EXTRAS

1. **Backup Automático**: Configure cron job para backup do JSON
2. **Logs**: Use `logging` para registrar ações importantes
3. **Validação**: Adicione validação de datas e campos obrigatórios
4. **Temas**: Crie múltiplos arquivos CSS para diferentes temas
5. **Performance**: Use caching para dados que não mudam frequentemente

---

**🎨 Personalize à vontade!**  
**💪 O código está organizado e pronto para evoluir!**
