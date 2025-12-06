"""
Módulo para processamento de dados do dashboard L'Acqua Azzurra Pools
"""
import pandas as pd
import json
import re
from datetime import datetime
from pathlib import Path

class PoolDataProcessor:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.data_storage_path = Path("data_storage.json")
        self.df = None
        self.extra_data = {}
        self.extra_customers = []
        # Carrega dados extras antes para anexar clientes novos ao DataFrame
        self.load_extra_data()
        self.load_data()
    
    def load_data(self):
        """Carrega dados do CSV e anexa clientes criados pelo usuário"""
        self.df = pd.read_csv(self.csv_path, encoding='utf-8')
        
        # Adicionar colunas extras se não existirem
        for col in ['Ultima Troca', 'Proxima Troca', 'Auto Charge']:
            if col not in self.df.columns:
                self.df[col] = ''
        
        # Limpar e padronizar dados
        self.df['Name'] = self.df['Name'].fillna('Desconhecido')
        self.df['Status'] = self.df['Status'].fillna('Desconhecido')
        self.df['Route Price'] = pd.to_numeric(self.df['Route Price'], errors='coerce').fillna(0)
        self.df['Route Tech'] = self.df['Route Tech'].fillna('Não atribuído').apply(self._normalize_tech)
        self.df['Charge Method'] = self.df['Charge Method'].fillna('N/A')
        self.df['Auto Charge'] = self.df['Auto Charge'].fillna('No')
        
        # Anexar clientes criados pelo usuário
        self._apply_extra_customers()

        # Garantir normalização final após anexar extras
        self.df['Route Tech'] = self.df['Route Tech'].apply(self._normalize_tech)
        
    def load_extra_data(self):
        """Carrega dados extras do arquivo JSON"""
        if self.data_storage_path.exists():
            with open(self.data_storage_path, 'r', encoding='utf-8') as f:
                self.extra_data = json.load(f)
        else:
            self.extra_data = {}
        # Clientes adicionados pelo usuário
        self.extra_customers = self.extra_data.get("_new_customers", [])
        # Log de auditoria
        self.extra_data.setdefault("_audit_log", [])
    
    def save_extra_data(self):
        """Salva dados extras no arquivo JSON"""
        # Persistir lista de clientes novos
        self.extra_data["_new_customers"] = self.extra_customers
        with open(self.data_storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.extra_data, f, ensure_ascii=False, indent=2)
    
    def update_customer_data(self, customer_name, field, value):
        """Atualiza dados de um cliente específico"""
        if customer_name not in self.extra_data:
            self.extra_data[customer_name] = {}

        if field == 'Route Tech':
            value = self._normalize_tech(value)
        
        self.extra_data[customer_name][field] = value
        self.save_extra_data()
        
        # Atualizar no DataFrame também
        if field in self.df.columns:
            self.df.loc[self.df['Name'] == customer_name, field] = value
    
    def get_customer_extra_data(self, customer_name, field):
        """Obtém dados extras de um cliente"""
        if customer_name in self.extra_data:
            return self.extra_data[customer_name].get(field, '')
        return ''
    
    def get_filtered_data(self, status_filter=None, tech_filter=None, month_filter=None):
        """Filtra dados baseado em critérios"""
        df_filtered = self.df.copy()
        
        # Aplicar filtros
        if status_filter and status_filter != 'Todos':
            df_filtered = df_filtered[df_filtered['Status'] == status_filter]
        
        if tech_filter and tech_filter != 'Todos':
            df_filtered = df_filtered[df_filtered['Route Tech'] == tech_filter]
        
        # Mesclar com dados extras
        for idx, row in df_filtered.iterrows():
            customer_name = row['Name']
            if customer_name in self.extra_data:
                for field, value in self.extra_data[customer_name].items():
                    if field == 'Route Tech':
                        value = self._normalize_tech(value)
                    if field in df_filtered.columns:
                        df_filtered.at[idx, field] = value

        # Filtrar por mês em Última ou Próxima Troca
        if month_filter and month_filter != 'Todos':
            month_filter = int(month_filter)
            def has_month(row):
                dates = [row.get('Ultima Troca', ''), row.get('Proxima Troca', '')]
                for d in dates:
                    parsed = self._parse_date(d)
                    if parsed and parsed.month == month_filter:
                        return True
                return False
            df_filtered = df_filtered[df_filtered.apply(has_month, axis=1)]
        
        return df_filtered
    
    def get_monthly_revenue(self):
        """Calcula faturamento mensal"""
        active_customers = self.df[self.df['Status'].str.contains('Active', na=False)]
        return active_customers['Route Price'].sum()
    
    def get_active_customers_count(self):
        """Conta clientes ativos"""
        return len(self.df[self.df['Status'].str.contains('Active', na=False)])
    
    def get_future_maintenance_count(self):
        """Conta manutenções futuras"""
        # Contar clientes com próxima data de troca definida
        count = 0
        for customer_name in self.extra_data:
            if 'Proxima Troca' in self.extra_data[customer_name]:
                proxima = self.extra_data[customer_name]['Proxima Troca']
                if proxima and proxima.strip():
                    count += 1
        
        # Também verificar coluna do DataFrame
        df_count = len(self.df[self.df['Proxima Troca'].notna() & (self.df['Proxima Troca'] != '')])
        
        return max(count, df_count)
    
    def get_technicians(self):
        """Retorna lista de técnicos/piscineiros"""
        tech_set = set()
        for raw in self.df['Route Tech']:
            if pd.isna(raw) or not raw:
                continue
            for part in re.split(r',\s*', str(raw)):
                norm = self._normalize_tech(part)
                if norm and norm.lower() not in ['não atribuído', 'nao atribuido']:
                    tech_set.add(norm)
        return sorted(tech_set)

    def name_exists(self, name: str) -> bool:
        if not name:
            return False
        return not self.df[self.df['Name'].str.lower() == name.lower()].empty

    def log_action(self, action: str, name: str, changes: dict):
        entry = {
            "action": action,
            "name": name,
            "changes": changes,
            "timestamp": datetime.now().isoformat()
        }
        log = self.extra_data.get("_audit_log", [])
        log.append(entry)
        self.extra_data["_audit_log"] = log
        self.save_extra_data()
    
    def get_statuses(self):
        """Retorna lista de status"""
        statuses = self.df['Status'].unique()
        return sorted([s for s in statuses if s and pd.notna(s)])
    
    def get_revenue_by_tech(self):
        """Calcula faturamento por técnico"""
        active_df = self.df[self.df['Status'].str.contains('Active', na=False)]
        revenue_by_tech = active_df.groupby('Route Tech')['Route Price'].sum().reset_index()
        revenue_by_tech.columns = ['Técnico', 'Faturamento']
        return revenue_by_tech
    
    def get_customers_by_status(self):
        """Conta clientes por status"""
        status_counts = self.df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Quantidade']
        return status_counts

    def add_customer(self, record: dict):
        """Adiciona um novo cliente criado pelo usuário"""
        defaults = {
            'Name': 'Novo Cliente',
            'Status': 'Lead',
            'Route Tech': 'Não atribuído',
            'Route Price': 0,
            'Charge Method': 'Advance',
            'Auto Charge': 'No',
            'Ultima Troca': '',
            'Proxima Troca': '',
        }
        new_record = {**defaults, **record}
        new_record['Route Tech'] = self._normalize_tech(new_record.get('Route Tech'))
        self.extra_customers.append(new_record)
        self.save_extra_data()
        # Adicionar ao DataFrame em memória
        self.df = pd.concat([self.df, pd.DataFrame([new_record])], ignore_index=True)

    def rename_customer(self, old_name: str, new_name: str):
        """Renomeia um cliente, ajustando df e dados extras"""
        if not old_name or not new_name or old_name == new_name:
            return
        # Atualizar DataFrame
        self.df.loc[self.df['Name'] == old_name, 'Name'] = new_name
        # Mover dados extras
        if old_name in self.extra_data:
            self.extra_data[new_name] = self.extra_data.pop(old_name)
        # Atualizar lista de clientes novos se existir
        for item in self.extra_customers:
            if item.get('Name') == old_name:
                item['Name'] = new_name
        self.save_extra_data()

    def _normalize_tech(self, name):
        """Normaliza nome de piscineiro removendo pontos, espaços extras e sinônimos de não atribuído"""
        if name is None or (isinstance(name, float) and pd.isna(name)):
            return 'Não atribuído'
        cleaned = str(name).strip()
        cleaned = re.sub(r'\.+$', '', cleaned)  # remove pontos no final
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        lowered = cleaned.lower()
        if lowered in ['nao atribuido', 'não atribuído', 'sem piscineiro', 'sem piscinero', 'none', 'n/a', '']:
            return 'Não atribuído'
        return cleaned.title()

    @staticmethod
    def _parse_date(date_str):
        """Tenta parsear datas em formatos comuns"""
        if not date_str or not isinstance(date_str, str):
            return None
        date_str = date_str.strip()
        if not date_str:
            return None
        formats = ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def _apply_extra_customers(self):
        """Anexa clientes criados pelo usuário ao DataFrame"""
        if self.extra_customers:
            extra_df = pd.DataFrame(self.extra_customers)
            for col in ['Ultima Troca', 'Proxima Troca', 'Auto Charge', 'Charge Method', 'Route Tech', 'Route Price', 'Status', 'Name']:
                if col not in extra_df.columns:
                    extra_df[col] = ''
            self.df = pd.concat([self.df, extra_df], ignore_index=True)
    
    def get_display_dataframe(self, filtered_df):
        """Retorna DataFrame formatado para exibição"""
        display_cols = ['Name', 'Status', 'Route Tech', 'Route Price', 'Charge Method', 
                       'Ultima Troca', 'Proxima Troca', 'Billing Phone', 'Billing Email']
        
        # Verificar quais colunas existem
        existing_cols = [col for col in display_cols if col in filtered_df.columns]
        
        df_display = filtered_df[existing_cols].copy()
        
        # Renomear colunas para português
        column_mapping = {
            'Name': 'Nome',
            'Status': 'Status',
            'Route Tech': 'Piscineiro',
            'Route Price': 'Valor da Rota',
            'Charge Method': 'Método Pagamento',
            'Ultima Troca': 'Última Troca',
            'Proxima Troca': 'Próxima Troca',
            'Billing Phone': 'Telefone',
            'Billing Email': 'Email'
        }
        
        df_display = df_display.rename(columns=column_mapping)
        
        # Formatar valor
        if 'Valor da Rota' in df_display.columns:
            df_display['Valor da Rota'] = df_display['Valor da Rota'].apply(
                lambda x: f'${x:.2f}' if pd.notna(x) and x > 0 else '$0.00'
            )
        
        return df_display
