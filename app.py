"""
Painel L'Acqua Azzurra - Dashboard Profissional
Dashboard interativo para gerenciamento de clientes e manutenções de piscinas
"""

import os
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context, no_update, ALL
import dash_bootstrap_components as dbc
from data_processor import PoolDataProcessor
import pandas as pd

# Inicializar o app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    title="Painel L'Acqua Azzurra"
)

# Expor o servidor Flask para WSGI (Gunicorn, Render, etc.)
server = app.server

# Inicializar processador de dados
CSV_PATH = "L'Acqua Azzurra Pools Customer report-171125135257 - Sheet.csv"
data_processor = PoolDataProcessor(CSV_PATH)

# Opções para selects
STATUS_OPTIONS = [{"label": s, "value": s} for s in data_processor.get_statuses()]

tech_names = data_processor.get_technicians()
TECH_EDIT_OPTIONS = ([{"label": "Sem Piscineiro", "value": "Não atribuído"}] +
                     [{"label": f"🏊 {t}", "value": t} for t in tech_names])
TECH_FILTER_OPTIONS = ([{"label": "Todos os Piscineiros", "value": "Todos"},
                        {"label": "Sem Piscineiro", "value": "Não atribuído"}] +
                       [{"label": f"🏊 {t}", "value": t} for t in tech_names])
CHARGE_METHOD_OPTIONS = [{"label": m, "value": m} for m in sorted(data_processor.df['Charge Method'].dropna().unique())]

# ===== LAYOUT DO DASHBOARD =====
app.layout = dbc.Container([
    # Header com logo e botão Novo Cliente
    html.Div([
        dbc.Row([
            dbc.Col([
                html.H1("Painel L'Acqua Azzurra", className="header-title"),
                html.P("Gestão Operacional e Financeira", className="header-subtitle")
            ], width=8),
            dbc.Col([
                html.Div([
                    dbc.Button(
                        [html.I(className="fas fa-download me-2"), "Exportar CSV"],
                        id="btn-export",
                        color="secondary",
                        className="btn-export me-2"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-calendar-plus me-2"), "Novo Cliente"],
                        id="btn-novo-cliente",
                        color="primary",
                        className="btn-novo-cliente"
                    )
                ], className="d-flex justify-content-end align-items-center")
            ], width=4, className="d-flex justify-content-end align-items-center")
        ])
    ], className="main-header mb-4"),
    
    # KPIs em destaque
    dcc.Loading(
        id="loading-kpis",
        type="default",
        children=dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-dollar-sign", style={"fontSize": "24px", "color": "#10b981"})
                    ], className="kpi-icon-container"),
                    html.Div([
                        html.P("Faturamento Mensal", className="kpi-label"),
                        html.H3(id="kpi-revenue", className="kpi-number"),
                        html.P([
                            html.Span("Ativo", className="badge-ativo me-2"),
                            "Baseado na rota atual"
                        ], className="kpi-description")
                    ], style={"flex": "1"})
                ], className="kpi-content")
            ], md=4, className="kpi-card"),

            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-users", style={"fontSize": "24px", "color": "#3b82f6"})
                    ], className="kpi-icon-container"),
                    html.Div([
                        html.P("Clientes Ativos", className="kpi-label"),
                        html.H3(id="kpi-active-customers", className="kpi-number"),
                        html.P("Contratos vigentes", className="kpi-description")
                    ], style={"flex": "1"})
                ], className="kpi-content")
            ], md=4, className="kpi-card"),

            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-calendar-check", style={"fontSize": "24px", "color": "#8b5cf6"})
                    ], className="kpi-icon-container"),
                    html.Div([
                        html.P("Manutenções Futuras", className="kpi-label"),
                        html.H3(id="kpi-future-maintenance", className="kpi-number"),
                        html.P("Agendadas no sistema", className="kpi-description")
                    ], style={"flex": "1"})
                ], className="kpi-content")
            ], md=4, className="kpi-card")
        ], className="mb-4")
    ),
    
    # Barra de busca e filtro
    dbc.Row([
        dbc.Col([
            html.Div([
                html.I(className="fas fa-search search-icon-input"),
                dbc.Input(
                    id="search-input",
                    type="text",
                    placeholder="Buscar cliente...",
                    style={'paddingLeft': '2.5rem'}
                )
            ], style={'position': 'relative'})
        ], md=4),
        dbc.Col([
            dcc.Dropdown(
                id="status-filter",
                options=[{"label": "Todos os Status", "value": "Todos"}] + STATUS_OPTIONS,
                value="Todos",
                clearable=False,
                searchable=False,
                className="status-dropdown",
                placeholder="Status"
            )
        ], md=3),
        dbc.Col([
            dcc.Dropdown(
                id="tech-filter",
                options=TECH_FILTER_OPTIONS,
                value="Todos",
                clearable=False,
                searchable=False,
                className="tech-dropdown",
                placeholder="Piscineiro"
            )
        ], md=3),
        dbc.Col([
            dcc.Dropdown(
                id="month-filter",
                options=[
                    {"label": "Todos os Meses", "value": "Todos"},
                    {"label": "Jan (01) - Janeiro", "value": "1"},
                    {"label": "Fev (02) - Fevereiro", "value": "2"},
                    {"label": "Mar (03) - Março", "value": "3"},
                    {"label": "Abr (04) - Abril", "value": "4"},
                    {"label": "Mai (05) - Maio", "value": "5"},
                    {"label": "Jun (06) - Junho", "value": "6"},
                    {"label": "Jul (07) - Julho", "value": "7"},
                    {"label": "Ago (08) - Agosto", "value": "8"},
                    {"label": "Set (09) - Setembro", "value": "9"},
                    {"label": "Out (10) - Outubro", "value": "10"},
                    {"label": "Nov (11) - Novembro", "value": "11"},
                    {"label": "Dez (12) - Dezembro", "value": "12"}
                ],
                value="Todos",
                clearable=False,
                searchable=False,
                placeholder="Mês",
                className="month-dropdown"
            )
        ], md=2)
    ], className="mb-3"),
    # Tabela de Clientes com botões de ação
    dcc.Loading(
        id="loading-table",
        type="default",
        children=html.Div([
            html.Div(id="table-with-actions", children=[
                dash_table.DataTable(
                    id="customers-table",
                    columns=[],
                    data=[],
                    markdown_options={'html': True},
                    selected_rows=[],
                    row_selectable='single',
                    style_table={
                        'overflowX': 'auto',
                        'minWidth': '100%'
                    },
                style_header={
                    'backgroundColor': '#f8fafc',
                    'color': '#475569',
                    'fontWeight': '600',
                    'textAlign': 'left',
                    'padding': '18px 20px',
                    'fontSize': '12px',
                    'textTransform': 'uppercase',
                    'letterSpacing': '0.05em',
                    'borderBottom': '1px solid #e2e8f0',
                    'borderTop': 'none'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '16px 18px',
                    'fontSize': '14px',
                    'fontFamily': 'Inter, sans-serif',
                    'borderBottom': '1px solid #f1f5f9',
                    'backgroundColor': 'white',
                    'color': '#334155',
                    'height': 'auto',
                    'whiteSpace': 'normal'
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'CLIENTE'}, 'minWidth': '220px', 'maxWidth': '260px'},
                    {'if': {'column_id': 'STATUS'}, 'minWidth': '140px', 'maxWidth': '160px', 'textAlign': 'center'},
                    {'if': {'column_id': 'PISCINEIRO'}, 'minWidth': '150px', 'maxWidth': '170px'},
                    {'if': {'column_id': 'VALOR'}, 'minWidth': '110px', 'maxWidth': '120px', 'textAlign': 'center'},
                    {'if': {'column_id': 'MÉTODO'}, 'minWidth': '150px', 'maxWidth': '170px'},
                    {'if': {'column_id': 'AUTO PAY'}, 'minWidth': '120px', 'maxWidth': '130px', 'textAlign': 'center'},
                    {'if': {'column_id': 'ÚLTIMA TROCA'}, 'minWidth': '130px', 'maxWidth': '140px'},
                    {'if': {'column_id': 'PRÓXIMA TROCA'}, 'minWidth': '130px', 'maxWidth': '140px'}
                ],
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{STATUS} contains "Ativo"',
                            'column_id': ['CLIENTE', 'PISCINEIRO', 'ÚLTIMA TROCA', 'PRÓXIMA TROCA', 'VALOR', 'MÉTODO', 'AUTO PAY']
                        },
                        'backgroundColor': '#f0fdf4',
                    },
                    {
                        'if': {
                            'filter_query': '{STATUS} contains "Inativo"',
                            'column_id': ['CLIENTE', 'PISCINEIRO', 'ÚLTIMA TROCA', 'PRÓXIMA TROCA', 'VALOR', 'MÉTODO', 'AUTO PAY']
                        },
                        'backgroundColor': '#fef2f2',
                    },
                    {
                        'if': {
                            'filter_query': '{STATUS} contains "Lead"',
                            'column_id': ['CLIENTE', 'PISCINEIRO', 'ÚLTIMA TROCA', 'PRÓXIMA TROCA', 'VALOR', 'MÉTODO', 'AUTO PAY']
                        },
                        'backgroundColor': '#fffbeb',
                    },
                ],
                style_data={
                    'border': 'none',
                    'borderBottom': '1px solid #f1f5f9'
                },
                style_as_list_view=True,
                page_size=12,
                page_action="native",
                sort_action="native",
                sort_mode="multi"
            ),
            html.Div(id="action-buttons-container")
            ])
        ], className="table-container")
    ),
    
    # Modal para edição/criação
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="modal-title")),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Nome do Cliente", className="form-label"),
                    dbc.Input(id="edit-name", type="text", placeholder="Nome")
                ], md=12)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Status", className="form-label"),
                    dcc.Dropdown(id="edit-status", options=STATUS_OPTIONS, placeholder="Status")
                ], md=6),
                dbc.Col([
                    html.Label("Piscineiro", className="form-label"),
                    dcc.Dropdown(id="edit-tech", options=TECH_EDIT_OPTIONS, placeholder="Piscineiro")
                ], md=6)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Valor da Rota", className="form-label"),
                    dbc.Input(id="edit-route-price", type="number", min=0, step=10, placeholder="0")
                ], md=6),
                dbc.Col([
                    html.Label("Método de Cobrança", className="form-label"),
                    dcc.Dropdown(id="edit-charge-method", options=CHARGE_METHOD_OPTIONS, placeholder="Método")
                ], md=6)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Cobrança Automática", className="form-label"),
                    dbc.Checklist(
                        options=[{"label": " Ativar Auto Pay", "value": "yes"}],
                        value=[],
                        id="edit-auto-pay",
                        switch=True
                    )
                ], md=12)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Última Troca (Filtro)", className="form-label"),
                    dcc.DatePickerSingle(
                        id="edit-ultima-troca",
                        placeholder="Selecione a data",
                        display_format="DD/MM/YYYY",
                        first_day_of_week=1,
                        className="custom-datepicker",
                        style={'width': '100%'}
                    )
                ], md=6),
                dbc.Col([
                    html.Label("Próxima Troca (Filtro)", className="form-label"),
                    dcc.DatePickerSingle(
                        id="edit-proxima-troca",
                        placeholder="Selecione a data",
                        display_format="DD/MM/YYYY",
                        first_day_of_week=1,
                        className="custom-datepicker",
                        style={'width': '100%'}
                    )
                ], md=6)
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancelar", id="btn-cancel", className="me-2", color="secondary"),
            dbc.Button("Salvar", id="save-button", color="primary")
        ])
    ], id="modal-edit", is_open=False, size="lg"),
    
    # Stores
    dcc.Store(id="selected-customer-store"),
    dcc.Store(id="edit-mode-store"),
    dcc.Download(id="export-download"),
    html.Div(id="save-feedback")
    
], fluid=True, className="main-container")


# ===== CALLBACKS =====

# Atualizar KPIs, tabela e botões de ação
@app.callback(
    [Output("kpi-revenue", "children"),
     Output("kpi-active-customers", "children"),
     Output("kpi-future-maintenance", "children"),
     Output("customers-table", "data"),
     Output("customers-table", "columns"),
     Output("action-buttons-container", "children")],
    [Input("status-filter", "value"),
     Input("tech-filter", "value"),
     Input("month-filter", "value"),
     Input("search-input", "value"),
     Input("save-button", "n_clicks")]
)
def update_dashboard(status_filter, tech_filter, month_filter, search_text, save_clicks):
    # Recarregar dados
    data_processor.load_extra_data()
    data_processor.load_data()
    
    # KPIs
    monthly_revenue = data_processor.get_monthly_revenue()
    active_customers = data_processor.get_active_customers_count()
    future_maintenance = data_processor.get_future_maintenance_count()
    
    # Filtrar dados
    filtered_df = data_processor.get_filtered_data(status_filter, tech_filter, month_filter)
    
    # Busca por texto
    if search_text and search_text.strip():
        filtered_df = filtered_df[
            filtered_df['Name'].str.contains(search_text, case=False, na=False)
        ]
    
    # Preparar dados para tabela
    table_df = filtered_df[['Name', 'Status', 'Route Tech', 'Route Price', 'Charge Method', 'Auto Charge', 'Ultima Troca', 'Proxima Troca']].copy()

    # Adicionar dados extras
    table_df['Ultima Troca'] = ''
    table_df['Proxima Troca'] = ''
    
    for idx, row in table_df.iterrows():
        customer_name = row['Name']
        table_df.at[idx, 'Ultima Troca'] = data_processor.get_customer_extra_data(customer_name, "Ultima Troca")
        table_df.at[idx, 'Proxima Troca'] = data_processor.get_customer_extra_data(customer_name, "Proxima Troca")
    
    # Guardar valores brutos para uso no modal (já com dados extras aplicados)
    table_df['STATUS_RAW'] = table_df['Status']
    table_df['PISCINEIRO_RAW'] = table_df['Route Tech']
    table_df['VALOR_RAW'] = table_df['Route Price']
    table_df['METODO_RAW'] = table_df['Charge Method']
    table_df['AUTO_RAW'] = table_df['Auto Charge']
    table_df['ULTIMA_RAW'] = table_df['Ultima Troca']
    table_df['PROXIMA_RAW'] = table_df['Proxima Troca']
    
    # Renomear colunas
    table_df = table_df.rename(columns={
        'Name': 'CLIENTE',
        'Status': 'STATUS',
        'Route Tech': 'PISCINEIRO',
        'Route Price': 'VALOR',
        'Charge Method': 'MÉTODO',
        'Auto Charge': 'AUTO PAY',
        'Ultima Troca': 'ÚLTIMA TROCA',
        'Proxima Troca': 'PRÓXIMA TROCA'
    })
    
    # Formatar status com badges HTML
    def format_status(status):
        if 'Active (routed)' in str(status):
            return '<span class="badge-status badge-ativo">✓ Ativo</span>'
        elif 'Active (no route)' in str(status):
            return '<span class="badge-status badge-ativo-sem-rota">○ Ativo (sem rota)</span>'
        elif 'Inactive' in str(status):
            return '<span class="badge-status badge-inativo">✕ Inativo</span>'
        elif 'Lead' in str(status):
            return '<span class="badge-status badge-lead">⚬ Lead</span>'
        return str(status)
    
    table_df['STATUS'] = table_df['STATUS'].apply(format_status)
    
    # Formatar valor
    table_df['VALOR'] = table_df['VALOR'].apply(
        lambda x: f'<span class="valor-mensal">${x:.0f}</span>' if pd.notna(x) and x > 0 else '<span class="valor-na">—</span>'
    )
    
    # Formatar Método
    table_df['MÉTODO'] = table_df['MÉTODO'].apply(
        lambda x: '<span class="metodo-badge">📅 ' + str(x) + '</span>' if pd.notna(x) and str(x) != '' else '<span class="metodo-na">—</span>'
    )
    
    # Formatar Auto Pay com badges visuais
    def format_auto_pay(value):
        if pd.notna(value) and str(value).lower() in ['yes', 'sim', 'y']:
            return '<span class="badge-autopay badge-yes">✓ SIM</span>'
        else:
            return '<span class="badge-autopay badge-no">✕ NÃO</span>'
    
    table_df['AUTO PAY'] = table_df['AUTO PAY'].apply(format_auto_pay)
    
    # Preencher valores vazios
    table_df['PISCINEIRO'] = table_df['PISCINEIRO'].fillna('—')
    table_df['ÚLTIMA TROCA'] = table_df['ÚLTIMA TROCA'].apply(lambda x: x if x else 'Não agendado')
    table_df['PRÓXIMA TROCA'] = table_df['PRÓXIMA TROCA'].apply(lambda x: x if x else 'Não agendado')
    
    # Preparar dados da tabela (sem coluna de ações)
    table_data = table_df.to_dict('records')
    table_columns = [
        ({"name": col, "id": col, "presentation": "markdown"} 
         if col in ['STATUS', 'VALOR', 'MÉTODO', 'AUTO PAY'] 
         else {"name": col, "id": col})
        for col in table_df.columns if not col.endswith('_RAW')
    ]
    
    # Criar botões de ação para cada linha
    action_buttons = html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-edit me-2"), "Editar"],
                    id={"type": "edit-btn", "index": idx},
                    color="primary",
                    size="sm",
                    className="action-btn-edit",
                    n_clicks=0
                )
            ], width="auto")
        ], className="mb-2", justify="start")
        for idx, row in enumerate(table_data)
    ], className="action-buttons-wrapper")
    
    return (
        f"${monthly_revenue:,.2f}",
        f"{active_customers}",
        f"{future_maintenance}",
        table_data,
        table_columns,
        action_buttons
    )


# Exportar CSV do resultado filtrado
@app.callback(
    Output("export-download", "data"),
    [Input("btn-export", "n_clicks")],
    [State("status-filter", "value"),
     State("tech-filter", "value"),
     State("month-filter", "value"),
     State("search-input", "value")]
)
def export_csv(n_clicks, status_filter, tech_filter, month_filter, search_text):
    if not n_clicks:
        return no_update

    data_processor.load_extra_data()
    data_processor.load_data()
    filtered_df = data_processor.get_filtered_data(status_filter, tech_filter, month_filter)

    if search_text and search_text.strip():
        filtered_df = filtered_df[
            filtered_df['Name'].str.contains(search_text, case=False, na=False)
        ]

    export_cols = ['Name', 'Status', 'Route Tech', 'Route Price', 'Charge Method', 'Auto Charge', 'Ultima Troca', 'Proxima Troca']
    existing_cols = [c for c in export_cols if c in filtered_df.columns]
    df_export = filtered_df[existing_cols].copy()

    return dcc.send_data_frame(df_export.to_csv, "clientes_filtrados.csv", index=False)


# Abrir modal para editar ou criar cliente
@app.callback(
    [Output("modal-edit", "is_open"),
     Output("selected-customer-store", "data"),
     Output("edit-mode-store", "data"),
     Output("modal-title", "children"),
     Output("edit-name", "value"),
     Output("edit-status", "value"),
     Output("edit-tech", "value"),
     Output("edit-route-price", "value"),
     Output("edit-charge-method", "value"),
     Output("edit-auto-pay", "value"),
     Output("edit-ultima-troca", "date"),
     Output("edit-proxima-troca", "date")],
    [Input({"type": "edit-btn", "index": ALL}, "n_clicks"),
     Input("btn-novo-cliente", "n_clicks"),
     Input("btn-cancel", "n_clicks"),
     Input("save-button", "n_clicks")],
    [State("customers-table", "data"),
     State("modal-edit", "is_open"),
     State("selected-customer-store", "data"),
     State("edit-mode-store", "data")],
    prevent_initial_call=True
)
def toggle_modal(edit_btn_clicks, btn_new, btn_cancel, btn_save, table_data, is_open, selected_customer, edit_mode):
    ctx = callback_context
    if not ctx.triggered:
        return no_update
    
    trigger_id = ctx.triggered[0]["prop_id"]

    # Fechar modal
    if "btn-cancel" in trigger_id or "save-button" in trigger_id:
        return False, None, None, "", "", None, None, None, None, [], None, None

    # Novo cliente
    if "btn-novo-cliente" in trigger_id:
        return (
            True,
            None,
            "create",
            "Novo Cliente",
            "",
            STATUS_OPTIONS[0]['value'] if STATUS_OPTIONS else None,
            "Não atribuído",
            0,
            CHARGE_METHOD_OPTIONS[0]['value'] if CHARGE_METHOD_OPTIONS else None,
            [],
            None,
            None
        )

    # Editar cliente existente (botão pattern matching)
    if "edit-btn" in trigger_id:
        import json
        trigger_dict = json.loads(trigger_id.split(".")[0])
        row_idx = trigger_dict.get("index")
        
        if row_idx is not None and row_idx < len(table_data):
            row = table_data[row_idx]
            auto_raw = str(row.get("AUTO_RAW", "")).lower()
            auto_val = ["yes"] if auto_raw in ["yes", "sim", "y"] else []
            
            # Converter datas DD/MM/YYYY para YYYY-MM-DD (formato do DatePicker)
            def convert_date_to_iso(date_str):
                if not date_str or date_str == "Não agendado":
                    return None
                try:
                    from datetime import datetime
                    dt = datetime.strptime(date_str, "%d/%m/%Y")
                    return dt.strftime("%Y-%m-%d")
                except:
                    return None
            
            ultima_date = convert_date_to_iso(row.get("ULTIMA_RAW", ""))
            proxima_date = convert_date_to_iso(row.get("PROXIMA_RAW", ""))
            
            return (
                True,
                row.get("CLIENTE"),
                "edit",
                f"Editar Cliente",
                row.get("CLIENTE", ""),
                row.get("STATUS_RAW"),
                row.get("PISCINEIRO_RAW"),
                row.get("VALOR_RAW"),
                row.get("METODO_RAW"),
                auto_val,
                ultima_date,
                proxima_date
            )

    # Manter estado atual se nenhuma ação específica
    return no_update


# Salvar alterações (feedback apenas; fechamento do modal é feito pelo callback de toggle)
# Salvar alterações (feedback apenas; fechamento do modal é feito pelo callback de toggle)
@app.callback(
    Output("save-feedback", "children"),
    [Input("save-button", "n_clicks")],
    [State("selected-customer-store", "data"),
     State("edit-mode-store", "data"),
     State("edit-name", "value"),
     State("edit-status", "value"),
     State("edit-tech", "value"),
     State("edit-route-price", "value"),
     State("edit-charge-method", "value"),
     State("edit-auto-pay", "value"),
     State("edit-ultima-troca", "date"),
     State("edit-proxima-troca", "date")]
)
def save_customer_data(n_clicks, customer_name, edit_mode, name, status, tech, route_price, charge_method, auto_pay, ultima_troca, proxima_troca):
    if not n_clicks:
        return ""

    def error_toast(msg):
        return dbc.Toast(
            msg,
            header="Erro",
            icon="danger",
            duration=3500,
            is_open=True,
            style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999}
        )

    name = (name or "").strip()
    if not name:
        return error_toast("Informe o nome do cliente." )

    status = status or 'Lead'
    tech = tech or 'Não atribuído'
    charge_method = charge_method or 'Advance'

    try:
        route_price = float(route_price) if route_price not in [None, "", " "] else 0
    except ValueError:
        return error_toast("Valor da rota inválido.")
    if route_price < 0:
        return error_toast("Valor da rota não pode ser negativo.")

    # Converter datas do formato ISO (YYYY-MM-DD) para DD/MM/YYYY
    def convert_iso_to_br(date_str):
        if not date_str:
            return ''
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str)
            return dt.strftime("%d/%m/%Y")
        except:
            return ''

    ultima_valid = convert_iso_to_br(ultima_troca)
    proxima_valid = convert_iso_to_br(proxima_troca)

    auto_value = 'Yes' if auto_pay and 'yes' in auto_pay else 'No'

    # Recarregar dados para checar duplicidade
    data_processor.load_extra_data()
    data_processor.load_data()

    if edit_mode == "create" or not customer_name:
        if data_processor.name_exists(name):
            return error_toast("Já existe um cliente com esse nome.")
        data_processor.add_customer({
            'Name': name,
            'Status': status,
            'Route Tech': tech,
            'Route Price': route_price,
            'Charge Method': charge_method,
            'Auto Charge': auto_value,
            'Ultima Troca': ultima_valid,
            'Proxima Troca': proxima_valid
        })
        data_processor.log_action("create", name, {
            'Status': status,
            'Route Tech': tech,
            'Route Price': route_price,
            'Charge Method': charge_method,
            'Auto Charge': auto_value,
            'Ultima Troca': ultima_valid,
            'Proxima Troca': proxima_valid
        })
    else:
        # Renomear se necessário
        if name != customer_name and data_processor.name_exists(name):
            return error_toast("Já existe um cliente com esse nome.")
        if name != customer_name:
            data_processor.rename_customer(customer_name, name)
            customer_name = name
        # Atualizar campos
        data_processor.update_customer_data(customer_name, "Status", status)
        data_processor.update_customer_data(customer_name, "Route Tech", tech)
        data_processor.update_customer_data(customer_name, "Route Price", route_price)
        data_processor.update_customer_data(customer_name, "Charge Method", charge_method)
        data_processor.update_customer_data(customer_name, "Auto Charge", auto_value)
        data_processor.update_customer_data(customer_name, "Ultima Troca", ultima_valid)
        data_processor.update_customer_data(customer_name, "Proxima Troca", proxima_valid)
        data_processor.log_action("update", customer_name, {
            'Status': status,
            'Route Tech': tech,
            'Route Price': route_price,
            'Charge Method': charge_method,
            'Auto Charge': auto_value,
            'Ultima Troca': ultima_valid,
            'Proxima Troca': proxima_valid
        })

    toast = dbc.Toast(
        "Dados salvos com sucesso!",
        header="Sucesso",
        icon="success",
        duration=2500,
        is_open=True,
        style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999}
    )

    return toast


if __name__ == "__main__":
    # Configurações de ambiente
    DEBUG = os.getenv("DASH_DEBUG", "True").lower() == "true"
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8050))
    
    print("\n" + "="*60)
    print("🏊 Painel L'Acqua Azzurra")
    print("="*60)
    print(f"\n✨ Iniciando servidor do dashboard...")
    print(f"📍 Acesse: http://{HOST}:{PORT}")
    print(f"🔧 Modo Debug: {DEBUG}")
    print("\n💡 Pressione CTRL+C para encerrar\n")
    print("="*60 + "\n")
    
    app.run(debug=DEBUG, host=HOST, port=PORT)
