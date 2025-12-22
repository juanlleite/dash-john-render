"""
Painel L'Acqua Azzurra - Dashboard Profissional
Dashboard interativo para gerenciamento de clientes e manutenções de piscinas
VERSÃO PostgreSQL
"""

import os
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context, no_update, ALL
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

# Carregar variáveis de ambiente (.env)
load_dotenv()

# Importar módulos do banco de dados
from database import init_db
from data_processor_postgres import PoolDataProcessor
import pandas as pd

# Inicializar banco de dados
init_db()

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

# Inicializar processador de dados (PostgreSQL)
data_processor = PoolDataProcessor()
# NÃO carregar dados na inicialização - lazy loading para economizar memória

# Opções para selects (cache)
_cached_options = {}

def clear_cached_options():
    """Limpa o cache de opções para forçar reload"""
    global _cached_options
    _cached_options = {}

def get_status_options(force_reload=False):
    """Lazy loading de opções de status"""
    if force_reload or 'status' not in _cached_options:
        _cached_options['status'] = [{"label": s, "value": s} for s in data_processor.get_statuses()]
    return _cached_options['status']

def get_tech_options(force_reload=False):
    """Lazy loading de opções de técnicos"""
    if force_reload or 'tech' not in _cached_options:
        tech_names = data_processor.get_technicians()
        print(f"🔍 DEBUG: Piscineiros encontrados: {tech_names}")  # DEBUG
        _cached_options['tech'] = {
            'edit': ([{"label": "Sem Piscineiro", "value": "Não atribuído"}] +
                    [{"label": f"🏊 {t}", "value": t} for t in tech_names]),
            'filter': ([{"label": "Todos os Piscineiros", "value": "Todos"},
                       {"label": "Sem Piscineiro", "value": "Não atribuído"}] +
                      [{"label": f"🏊 {t}", "value": t} for t in tech_names])
        }
    return _cached_options['tech']

STATUS_OPTIONS = []  # Inicializar vazio, será preenchido no primeiro uso
TECH_EDIT_OPTIONS = []  # Lazy loading
TECH_FILTER_OPTIONS = []  # Lazy loading
CHARGE_METHOD_OPTIONS = [
    {"label": "Cash", "value": "Cash"},
    {"label": "Check", "value": "Check"},
    {"label": "Credit Card", "value": "Credit Card"},
    {"label": "N/A", "value": "N/A"}
]

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
                options=[{"label": "Todos os Status", "value": "Todos"}],
                value="Todos",
                clearable=False,
                searchable=False,
                className="status-dropdown",
                placeholder="Status"
            )
        ], md=2),
        dbc.Col([
            dcc.Dropdown(
                id="tech-filter",
                options=[{"label": "Todos os Piscineiros", "value": "Todos"}],
                value="Todos",
                clearable=False,
                searchable=False,
                className="tech-dropdown",
                placeholder="Piscineiro"
            )
        ], md=2),
        dbc.Col([
            dcc.Dropdown(
                id="last-change-filter",
                options=[
                    {"label": "📅 Última Troca: Todos", "value": "Todos"},
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
                placeholder="Última Troca",
                className="month-dropdown"
            )
        ], md=2),
        dbc.Col([
            dcc.Dropdown(
                id="next-change-filter",
                options=[
                    {"label": "📆 Próxima Troca: Todos", "value": "Todos"},
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
                placeholder="Próxima Troca",
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
                    {'if': {'column_id': 'CLIENTE'}, 'minWidth': '200px', 'maxWidth': '240px'},
                    {'if': {'column_id': 'STATUS'}, 'minWidth': '130px', 'maxWidth': '150px', 'textAlign': 'center'},
                    {'if': {'column_id': 'PISCINEIRO'}, 'minWidth': '140px', 'maxWidth': '160px'},
                    {'if': {'column_id': 'ÚLTIMA TROCA'}, 'minWidth': '120px', 'maxWidth': '130px'},
                    {'if': {'column_id': 'PRÓXIMA TROCA'}, 'minWidth': '120px', 'maxWidth': '130px'},
                    {'if': {'column_id': 'TIPO FILTRO'}, 'minWidth': '120px', 'maxWidth': '140px'},
                    {'if': {'column_id': 'VALOR FILTRO'}, 'minWidth': '100px', 'maxWidth': '110px', 'textAlign': 'center'}
                ],
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{STATUS} contains "Ativo"',
                            'column_id': ['CLIENTE', 'PISCINEIRO', 'ÚLTIMA TROCA', 'PRÓXIMA TROCA', 'TIPO FILTRO', 'VALOR FILTRO']
                        },
                        'backgroundColor': '#f0fdf4',
                    },
                    {
                        'if': {
                            'filter_query': '{STATUS} contains "Inativo"',
                            'column_id': ['CLIENTE', 'PISCINEIRO', 'ÚLTIMA TROCA', 'PRÓXIMA TROCA', 'TIPO FILTRO', 'VALOR FILTRO']
                        },
                        'backgroundColor': '#fef2f2',
                    },
                    {
                        'if': {
                            'filter_query': '{STATUS} contains "Lead"',
                            'column_id': ['CLIENTE', 'PISCINEIRO', 'ÚLTIMA TROCA', 'PRÓXIMA TROCA', 'TIPO FILTRO', 'VALOR FILTRO']
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
                page_current=0,
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
                    dbc.Input(
                        id="edit-name", 
                        type="text", 
                        placeholder="Nome",
                        style={'fontSize': '15px', 'height': '46px'}
                    )
                ], md=12)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Status", className="form-label"),
                    dcc.Dropdown(
                        id="edit-status", 
                        options=[], 
                        placeholder="Carregando...",
                        style={'fontSize': '15px'}
                    )
                ], md=6),
                dbc.Col([
                    html.Label("Piscineiro", className="form-label"),
                    dcc.Dropdown(
                        id="edit-tech", 
                        options=[], 
                        placeholder="Carregando...",
                        style={'fontSize': '15px'}
                    )
                ], md=6)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Tipo de Filtro", className="form-label"),
                    dcc.Dropdown(
                        id="edit-tipo-filtro",
                        options=[
                            {"label": "━━━━━━ HAYWARD ━━━━━━", "value": "", "disabled": True},
                            {"label": "  Hayward C750", "value": "Hayward C750"},
                            {"label": "  Hayward C900", "value": "Hayward C900"},
                            {"label": "  Hayward C1100", "value": "Hayward C1100"},
                            {"label": "  Hayward C1200", "value": "Hayward C1200"},
                            {"label": "  Hayward C1750", "value": "Hayward C1750"},
                            {"label": "  Hayward C100s", "value": "Hayward C100s"},
                            {"label": "  Hayward C150s", "value": "Hayward C150s"},
                            {"label": "  Hayward C200s", "value": "Hayward C200s"},
                            {"label": "━━━━━━ PENTAIR ━━━━━━", "value": "", "disabled": True},
                            {"label": "  Pentair Cc100", "value": "Pentair Cc100"},
                            {"label": "  Pentair Cc150", "value": "Pentair Cc150"},
                            {"label": "  Pentair Cc200", "value": "Pentair Cc200"},
                            {"label": "━━━━━━ JANDY ━━━━━━", "value": "", "disabled": True},
                            {"label": "  Jandy Cs100", "value": "Jandy Cs100"},
                            {"label": "  Jandy Cs150", "value": "Jandy Cs150"},
                            {"label": "  Jandy Cs200", "value": "Jandy Cs200"},
                            {"label": "  Jandy Cs250", "value": "Jandy Cs250"},
                            {"label": "━━━━━━ OUTROS ━━━━━━", "value": "", "disabled": True}
                        ],
                        placeholder="Selecione ou digite",
                        searchable=True,
                        clearable=True,
                        style={'fontSize': '15px'}
                    )
                ], md=6),
                dbc.Col([
                    html.Label("Valor do Filtro (R$)", className="form-label"),
                    dbc.Input(
                        id="edit-valor-filtro", 
                        type="number", 
                        min=0, 
                        step=0.01, 
                        placeholder="0.00",
                        style={'fontSize': '15px', 'height': '46px'}
                    )
                ], md=6)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Última Troca (Filtro)", className="form-label"),
                    dbc.Input(
                        id="edit-ultima-troca",
                        type="date",
                        placeholder="dd / mm / aaaa",
                        className="date-input-custom"
                    )
                ], md=6),
                dbc.Col([
                    html.Label("Próxima Troca (Filtro)", className="form-label"),
                    dbc.Input(
                        id="edit-proxima-troca",
                        type="date",
                        placeholder="dd / mm / aaaa",
                        className="date-input-custom"
                    )
                ], md=6)
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancelar", id="btn-cancel", className="me-2", color="secondary"),
            dbc.Button("Salvar", id="save-button", color="primary")
        ])
    ], id="modal-edit", is_open=False, size="xl"),
    
    # Stores
    dcc.Store(id="selected-customer-store"),
    dcc.Store(id="edit-mode-store"),
    dcc.Store(id="refresh-trigger", data=0),
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
     Output("action-buttons-container", "children"),
     Output("status-filter", "options"),
     Output("tech-filter", "options"),
     Output("edit-status", "options"),
     Output("edit-tech", "options")],
    [Input("status-filter", "value"),
     Input("tech-filter", "value"),
     Input("last-change-filter", "value"),
     Input("next-change-filter", "value"),
     Input("search-input", "value"),
     Input("refresh-trigger", "data"),
     Input("customers-table", "page_current"),
     Input("customers-table", "page_size"),
     Input("customers-table", "sort_by")]
)
def update_dashboard(status_filter, tech_filter, last_change_month, next_change_month, search_text, refresh_trigger, page_current, page_size, sort_by):
    # Garantir que dados estejam carregados
    data_processor.load_extra_data()
    
    # Popular opções dos dropdowns (forçar reload se refresh_trigger mudou)
    force_reload = refresh_trigger and refresh_trigger > 0
    status_opts = get_status_options(force_reload=force_reload)
    tech_opts = get_tech_options(force_reload=force_reload)
    status_filter_opts = [{"label": "Todos os Status", "value": "Todos"}] + status_opts
    tech_filter_opts = tech_opts['filter']
    tech_edit_opts = tech_opts['edit']
    
    # KPIs
    monthly_revenue = data_processor.get_monthly_revenue()
    active_customers = data_processor.get_active_customers_count()
    future_maintenance = data_processor.get_future_maintenance_count()
    
    # Filtrar dados
    filtered_df = data_processor.get_filtered_data(
        status_filter, 
        tech_filter, 
        last_change_month=last_change_month, 
        next_change_month=next_change_month
    )
    
    # Busca por texto
    if search_text and search_text.strip():
        filtered_df = filtered_df[
            filtered_df['Name'].str.contains(search_text, case=False, na=False)
        ]
    
    # Preparar dados para tabela (NOVA ESTRUTURA: sem Método/Auto Pay, com Tipo/Valor Filtro)
    table_df = filtered_df[['Name', 'Status', 'Route Tech', 'Ultima Troca', 'Proxima Troca', 'Tipo Filtro', 'Valor Filtro']].copy()

    # Guardar valores brutos para uso no modal
    table_df['STATUS_RAW'] = table_df['Status']
    table_df['PISCINEIRO_RAW'] = table_df['Route Tech']
    table_df['TIPO_FILTRO_RAW'] = table_df['Tipo Filtro']
    table_df['VALOR_FILTRO_RAW'] = table_df['Valor Filtro']
    table_df['ULTIMA_RAW'] = table_df['Ultima Troca']
    table_df['PROXIMA_RAW'] = table_df['Proxima Troca']
    
    # Renomear colunas
    table_df = table_df.rename(columns={
        'Name': 'CLIENTE',
        'Status': 'STATUS',
        'Route Tech': 'PISCINEIRO',
        'Ultima Troca': 'ÚLTIMA TROCA',
        'Proxima Troca': 'PRÓXIMA TROCA',
        'Tipo Filtro': 'TIPO FILTRO',
        'Valor Filtro': 'VALOR FILTRO'
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
    
    # Formatar valor do filtro
    table_df['VALOR FILTRO'] = table_df['VALOR FILTRO'].apply(
        lambda x: f'<span class="valor-mensal">R$ {x:.2f}</span>' if pd.notna(x) and x > 0 else '<span class="valor-na">—</span>'
    )
    
    # Formatar tipo de filtro
    table_df['TIPO FILTRO'] = table_df['TIPO FILTRO'].apply(
        lambda x: '<span class="metodo-badge">🔷 ' + str(x) + '</span>' if pd.notna(x) and str(x) != '' else '<span class="metodo-na">—</span>'
    )
    
    # Preencher valores vazios
    table_df['PISCINEIRO'] = table_df['PISCINEIRO'].fillna('—')
    table_df['ÚLTIMA TROCA'] = table_df['ÚLTIMA TROCA'].apply(lambda x: x if x else 'Não agendado')
    table_df['PRÓXIMA TROCA'] = table_df['PRÓXIMA TROCA'].apply(lambda x: x if x else 'Não agendado')
    
    # Adicionar índice oculto para rastreamento
    table_df['INDEX_HIDDEN'] = range(len(table_df))
    
    # Preparar dados da tabela
    table_data = table_df.to_dict('records')
    table_columns = [
        ({"name": col, "id": col, "presentation": "markdown"} 
         if col in ['STATUS', 'VALOR FILTRO', 'TIPO FILTRO'] 
         else {"name": col, "id": col})
        for col in table_df.columns if not col.endswith('_RAW') and col != 'INDEX_HIDDEN'
    ]
    
    # Calcular linhas da página atual
    if page_current is None:
        page_current = 0
    if page_size is None:
        page_size = 12
    
    start_idx = page_current * page_size
    end_idx = min(start_idx + page_size, len(table_data))
    
    # Criar botões de ação apenas para as linhas visíveis na página atual
    # Garantir que criamos exatamente page_size botões ou menos na última página
    num_buttons = min(page_size, len(table_data) - start_idx)
    visible_rows = table_data[start_idx:end_idx]
    
    action_buttons = html.Div([
        html.Div([
            dbc.Button(
                [html.I(className="fas fa-edit me-2"), "Editar"],
                id={"type": "edit-btn", "index": row['INDEX_HIDDEN']},
                color="primary",
                size="sm",
                className="action-btn-edit"
            )
        ], className="action-btn-row")
        for row in visible_rows
    ], className="action-buttons-wrapper", id="action-buttons-list")
    
    return (
        f"${monthly_revenue:,.2f}",
        f"{active_customers}",
        f"{future_maintenance}",
        table_data,
        table_columns,
        action_buttons,
        status_filter_opts,  # status-filter options
        tech_filter_opts,    # tech-filter options
        status_opts,         # edit-status options
        tech_edit_opts       # edit-tech options
    )


# Exportar CSV do resultado filtrado
@app.callback(
    Output("export-download", "data"),
    [Input("btn-export", "n_clicks")],
    [State("status-filter", "value"),
     State("tech-filter", "value"),
     State("last-change-filter", "value"),
     State("next-change-filter", "value"),
     State("search-input", "value")]
)
def export_csv(n_clicks, status_filter, tech_filter, last_change_month, next_change_month, search_text):
    if not n_clicks:
        return no_update

    data_processor.load_extra_data()
    data_processor.load_data()
    filtered_df = data_processor.get_filtered_data(
        status_filter, 
        tech_filter, 
        last_change_month=last_change_month, 
        next_change_month=next_change_month
    )

    if search_text and search_text.strip():
        filtered_df = filtered_df[
            filtered_df['Name'].str.contains(search_text, case=False, na=False)
        ]

    export_cols = ['Name', 'Status', 'Route Tech', 'Tipo Filtro', 'Valor Filtro', 'Ultima Troca', 'Proxima Troca']
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
     Output("edit-tipo-filtro", "value"),
     Output("edit-valor-filtro", "value"),
     Output("edit-ultima-troca", "value"),
     Output("edit-proxima-troca", "value")],
    [Input({"type": "edit-btn", "index": ALL}, "n_clicks"),
     Input("btn-novo-cliente", "n_clicks"),
     Input("btn-cancel", "n_clicks"),
     Input("refresh-trigger", "data")],
    [State("customers-table", "data"),
     State("modal-edit", "is_open"),
     State("selected-customer-store", "data"),
     State("edit-mode-store", "data")],
    prevent_initial_call=True
)
def toggle_modal(edit_btn_clicks, btn_new, btn_cancel, refresh_trigger, table_data, is_open, selected_customer, edit_mode):
    ctx = callback_context
    if not ctx.triggered:
        return no_update
    
    trigger_id = ctx.triggered[0]["prop_id"]
    trigger_value = ctx.triggered[0]["value"]
    
    # Se o valor do trigger é None ou 0, ignorar (não foi realmente clicado)
    if trigger_value is None or trigger_value == 0:
        return no_update
    
    # Fechar modal após salvar (refresh-trigger incrementou)
    if "refresh-trigger" in trigger_id and refresh_trigger and refresh_trigger > 0:
        return (False, None, None, "", "", None, None, None, None, None, None)
    
    # Fechar modal (cancelar)
    if "btn-cancel" in trigger_id:
        return (False, None, None, "", "", None, None, None, None, None, None)

    # Novo cliente
    if "btn-novo-cliente" in trigger_id:
        return (
            True,
            None,
            "create",
            "Novo Cliente",
            "",
            None,  # Status - será populado pelo dropdown
            "Não atribuído",
            None,  # Tipo filtro
            0.00,  # Valor filtro
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
                row.get("TIPO_FILTRO_RAW"),
                row.get("VALOR_FILTRO_RAW", 0.00),
                ultima_date,
                proxima_date
            )

    # Manter estado atual se nenhuma ação específica
    return no_update


# Salvar alterações e disparar refresh automático
@app.callback(
    [Output("save-feedback", "children"),
     Output("refresh-trigger", "data")],
    [Input("save-button", "n_clicks")],
    [State("selected-customer-store", "data"),
     State("edit-mode-store", "data"),
     State("edit-name", "value"),
     State("edit-status", "value"),
     State("edit-tech", "value"),
     State("edit-tipo-filtro", "value"),
     State("edit-valor-filtro", "value"),
     State("edit-ultima-troca", "value"),
     State("edit-proxima-troca", "value"),
     State("refresh-trigger", "data")],
    prevent_initial_call=True
)
def save_customer_data(n_clicks, customer_name, edit_mode, name, status, tech, tipo_filtro, valor_filtro, ultima_troca, proxima_troca, refresh_trigger):
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"💾 Salvando: {customer_name}")

    def error_toast(msg):
        return dbc.Toast(
            msg,
            header="Erro",
            icon="danger",
            duration=3500,
            is_open=True,
            style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999}
        ), (refresh_trigger or 0)

    name = (name or "").strip()
    if not name:
        return error_toast("Informe o nome do cliente.")

    status = status or 'Lead'
    tech = tech or 'Não atribuído'
    tipo_filtro = tipo_filtro or ''

    try:
        valor_filtro = float(valor_filtro) if valor_filtro not in [None, "", " "] else 0.00
    except ValueError:
        return error_toast("Valor do filtro inválido.")
    if valor_filtro < 0:
        return error_toast("Valor do filtro não pode ser negativo.")

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

    # Verificar duplicidade sem recarregar todos os dados
    if edit_mode == "create" or not customer_name:
        if data_processor.name_exists(name):
            return error_toast("Já existe um cliente com esse nome.")
        data_processor.add_customer({
            'Name': name,
            'Status': status,
            'Route Tech': tech,
            'Tipo Filtro': tipo_filtro,
            'Valor Filtro': valor_filtro,
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
        
        # Atualizar todos os campos em uma única transação (BATCH UPDATE - MUITO MAIS RÁPIDO)
        updates = {
            "Status": status,
            "Route Tech": tech,
            "Tipo Filtro": tipo_filtro,
            "Valor Filtro": valor_filtro,
            "Ultima Troca": ultima_valid,
            "Proxima Troca": proxima_valid
        }
        
        result = data_processor.update_customer_batch(customer_name, updates)
        logger.info(f"✅ Salvo: {customer_name} ({len(updates)} campos)")

    toast = dbc.Toast(
        "✓ Salvo!",
        header="Sucesso",
        icon="success",
        duration=1500,
        is_open=True,
        style={"position": "fixed", "top": 20, "right": 20, "zIndex": 9999}
    )
    
    # Incrementar trigger para forçar atualização da tabela
    new_trigger = (refresh_trigger or 0) + 1

    return toast, new_trigger


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
