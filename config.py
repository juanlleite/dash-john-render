# Configurações do Dashboard L'Acqua Azzurra Pools

# Caminho do arquivo CSV
CSV_PATH = "L'Acqua Azzurra Pools Customer report-171125135257 - Sheet.csv"

# Configurações do servidor
HOST = "127.0.0.1"
PORT = 8050
DEBUG = True

# Configurações de paginação
PAGE_SIZE = 20

# Configurações de cores (tema azul água)
COLORS = {
    "primary": "#0077be",
    "primary_dark": "#005a8d",
    "primary_light": "#4da6d6",
    "secondary": "#00b4d8",
    "accent": "#90e0ef",
    "success": "#06d6a0",
    "warning": "#ffd166",
    "danger": "#ef476f",
}

# Colunas para exibição na tabela
DISPLAY_COLUMNS = [
    "Name",
    "Status",
    "Route Tech",
    "Route Price",
    "Charge Method",
    "Ultima Troca",
    "Proxima Troca",
    "Billing Phone",
    "Billing Email"
]

# Mapeamento de nomes de colunas (EN -> PT)
COLUMN_NAMES_PT = {
    "Name": "Nome",
    "Status": "Status",
    "Route Tech": "Piscineiro",
    "Route Price": "Valor da Rota",
    "Charge Method": "Método Pagamento",
    "Ultima Troca": "Última Troca",
    "Proxima Troca": "Próxima Troca",
    "Billing Phone": "Telefone",
    "Billing Email": "Email"
}

# Piscineiros (técnicos)
TECHNICIANS = [
    "Lucca .",
    "Pedro Santos",
    "Drask Silva",
    "Vini Penner"
]

# Status possíveis
STATUS_OPTIONS = [
    "Active (routed)",
    "Inactive",
    "Lead",
    "Active (no route)"
]

# Meses do ano
MONTHS = {
    "01": "Janeiro",
    "02": "Fevereiro",
    "03": "Março",
    "04": "Abril",
    "05": "Maio",
    "06": "Junho",
    "07": "Julho",
    "08": "Agosto",
    "09": "Setembro",
    "10": "Outubro",
    "11": "Novembro",
    "12": "Dezembro"
}

# Arquivo de armazenamento de dados extras
DATA_STORAGE_FILE = "data_storage.json"

# Formato de data
DATE_FORMAT = "DD/MM/YYYY"

# Título do dashboard
DASHBOARD_TITLE = "L'Acqua Azzurra Pools Dashboard"
DASHBOARD_SUBTITLE = "Sistema de Gerenciamento de Clientes e Manutenções"

# Mensagens de feedback
MESSAGES = {
    "save_success": "✅ Dados salvos com sucesso para {customer}!",
    "save_error": "❌ Erro ao salvar dados. Tente novamente.",
    "no_customer_selected": "⚠️ Selecione um cliente primeiro.",
    "loading": "⏳ Carregando dados...",
    "no_data": "📭 Nenhum dado encontrado com os filtros selecionados."
}
