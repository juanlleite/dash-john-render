"""
Módulo para processamento de dados do dashboard L'Acqua Azzurra Pools
VERSÃO PostgreSQL - Substitui CSV/JSON por banco de dados
"""
import pandas as pd
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func, or_, and_, extract
from database import db
from models import Cliente, Auditoria
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PoolDataProcessor:
    """Processador de dados com PostgreSQL como backend"""
    
    def __init__(self, csv_path=None):
        """
        Inicializa o processador de dados
        
        Args:
            csv_path: Caminho do CSV (mantido para compatibilidade, mas não usado)
        """
        self.csv_path = csv_path  # Mantido para compatibilidade
        self.df = None
        logger.info("✅ PoolDataProcessor inicializado (modo PostgreSQL)")
    
    def load_data(self):
        """Carrega dados do PostgreSQL para DataFrame"""
        try:
            with db.get_session() as session:
                # Carregar todos os clientes
                clientes = session.query(Cliente).all()
                
                # Converter para lista de dicionários
                data = []
                for cliente in clientes:
                    data.append({
                        'Name': cliente.nome,
                        'Status': cliente.status,
                        'Route Tech': cliente.piscineiro or 'Não atribuído',
                        'Route Price': float(cliente.valor_rota) if cliente.valor_rota else 0.00,
                        'Tipo Filtro': cliente.tipo_filtro or '',
                        'Valor Filtro': float(cliente.valor_filtro) if cliente.valor_filtro else 0.00,
                        'Ultima Troca': cliente.ultima_troca.strftime('%d/%m/%Y') if cliente.ultima_troca else '',
                        'Proxima Troca': cliente.proxima_troca.strftime('%d/%m/%Y') if cliente.proxima_troca else '',
                        'ID': cliente.id  # ID do banco para referência
                    })
                
                # Criar DataFrame
                self.df = pd.DataFrame(data)
                
                logger.info(f"✅ Dados carregados: {len(self.df)} clientes")
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados: {e}")
            # Fallback para DataFrame vazio
            self.df = pd.DataFrame(columns=[
                'Name', 'Status', 'Route Tech', 'Route Price', 
                'Tipo Filtro', 'Valor Filtro', 'Ultima Troca', 'Proxima Troca', 'ID'
            ])
    
    def load_extra_data(self):
        """Carrega dados do PostgreSQL se ainda não carregados"""
        if self.df is None or self.df.empty:
            self.load_data()
    
    def save_extra_data(self):
        """Compatibilidade - não usado mais (dados estão no PostgreSQL)"""
        pass
    
    def _normalize_tech(self, tech_name):
        """Normaliza nome do piscineiro"""
        if not tech_name or pd.isna(tech_name) or str(tech_name).strip() == '':
            return 'Não atribuído'
        
        tech_name = str(tech_name).strip()
        
        # Dicionário de normalização
        normalization = {
            'joao': 'João Silva',
            'joão': 'João Silva',
            'joao silva': 'João Silva',
            'joão silva': 'João Silva',
            'maria': 'Maria Santos',
            'maria santos': 'Maria Santos',
            'pedro': 'Pedro Oliveira',
            'pedro oliveira': 'Pedro Oliveira',
            'ana': 'Ana Costa',
            'ana costa': 'Ana Costa',
        }
        
        tech_lower = tech_name.lower()
        return normalization.get(tech_lower, tech_name)
    
    def _parse_date(self, date_str):
        """Converte string DD/MM/YYYY para objeto date"""
        if not date_str or pd.isna(date_str):
            return None
        
        if isinstance(date_str, date):
            return date_str
        
        if isinstance(date_str, str):
            try:
                return datetime.strptime(date_str, '%d/%m/%Y').date()
            except ValueError:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return None
        return None
    
    def update_customer_data(self, customer_name, field, value):
        """
        Atualiza dados de um cliente específico no PostgreSQL
        
        Args:
            customer_name: Nome do cliente
            field: Campo a ser atualizado
            value: Novo valor
        """
        try:
            with db.get_session() as session:
                cliente = session.query(Cliente).filter_by(nome=customer_name).first()
                
                if not cliente:
                    logger.warning(f"Cliente '{customer_name}' não encontrado")
                    return False
                
                # Mapear campos do DataFrame para modelo
                field_mapping = {
                    'Status': 'status',
                    'Route Tech': 'piscineiro',
                    'Route Price': 'valor_rota',
                    'Tipo Filtro': 'tipo_filtro',
                    'Valor Filtro': 'valor_filtro',
                    'Ultima Troca': 'ultima_troca',
                    'Proxima Troca': 'proxima_troca',
                    'Last Changed': 'ultima_troca',  # Compatibilidade
                    'Next Change': 'proxima_troca'   # Compatibilidade
                }
                
                db_field = field_mapping.get(field, field.lower().replace(' ', '_'))
                old_value = getattr(cliente, db_field, None)
                
                # Processar valor baseado no campo
                if field == 'Route Tech':
                    value = self._normalize_tech(value)
                elif field in ['Route Price', 'Valor Filtro']:
                    value = Decimal(str(value)) if value else Decimal('0.00')
                elif field in ['Last Changed', 'Next Change', 'Ultima Troca', 'Proxima Troca']:
                    value = self._parse_date(value)
                
                # Atualizar campo
                setattr(cliente, db_field, value)
                
                # Registrar auditoria
                self.log_action(
                    'update',
                    cliente_id=cliente.id,
                    nome_cliente=cliente.nome,
                    campo=db_field,
                    valor_anterior=str(old_value),
                    valor_novo=str(value)
                )
                
                session.commit()
                logger.info(f"✅ Cliente '{customer_name}' atualizado: {field} = {value}")
                
                # NÃO recarregar DataFrame aqui - será feito depois de todos os updates
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar cliente: {e}")
            return False
    
    def update_customer_batch(self, customer_name, updates):
        """
        Atualiza múltiplos campos de um cliente em uma única transação
        MUITO MAIS RÁPIDO que update_customer_data múltiplas vezes
        
        Args:
            customer_name: Nome do cliente
            updates: Dict com {campo: valor}
        """
        try:
            with db.get_session() as session:
                cliente = session.query(Cliente).filter_by(nome=customer_name).first()
                
                if not cliente:
                    logger.warning(f"Cliente '{customer_name}' não encontrado")
                    return False
                
                cliente_id = cliente.id
                logger.info(f"✓ Cliente encontrado: ID={cliente_id}")
                
                # Mapear campos
                field_mapping = {
                    'Status': 'status',
                    'Route Tech': 'piscineiro',
                    'Route Price': 'valor_rota',
                    'Tipo Filtro': 'tipo_filtro',
                    'Valor Filtro': 'valor_filtro',
                    'Ultima Troca': 'ultima_troca',
                    'Proxima Troca': 'proxima_troca'
                }
                
                # Coletar valores antigos ANTES de modificar
                old_values = {}
                for field in updates.keys():
                    db_field = field_mapping.get(field, field.lower().replace(' ', '_'))
                    old_values[db_field] = getattr(cliente, db_field, None)
                
                # Aplicar todas as atualizações
                for field, value in updates.items():
                    db_field = field_mapping.get(field, field.lower().replace(' ', '_'))
                    old_value = old_values[db_field]
                    
                    # Processar valor
                    if field == 'Route Tech':
                        value = self._normalize_tech(value)
                    elif field in ['Route Price', 'Valor Filtro']:
                        value = Decimal(str(value)) if value else Decimal('0.00')
                    elif field in ['Ultima Troca', 'Proxima Troca']:
                        value = self._parse_date(value)
                    
                    # Atualizar
                    setattr(cliente, db_field, value)
                
                # Commit ANTES de log para não perder a sessão
                session.commit()
                logger.info(f"✅ Cliente '{customer_name}' atualizado (batch): {len(updates)} campos - COMMIT EXECUTADO")
                
                # Atualizar DataFrame em memória para evitar reload completo
                if self.df is not None:
                    mask = self.df['Name'] == customer_name
                    if mask.any():
                        for field, value in updates.items():
                            if field in self.df.columns:
                                self.df.loc[mask, field] = value
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar cliente (batch): {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def get_customer_extra_data(self, customer_name, field):
        """Obtém dados de um cliente (compatibilidade)"""
        try:
            with db.get_session() as session:
                cliente = session.query(Cliente).filter_by(nome=customer_name).first()
                
                if not cliente:
                    return ''
                
                field_mapping = {
                    'Status': cliente.status,
                    'Route Tech': cliente.piscineiro,
                    'Route Price': float(cliente.valor_rota) if cliente.valor_rota else 0.00,
                    'Tipo Filtro': cliente.tipo_filtro or '',
                    'Valor Filtro': float(cliente.valor_filtro) if cliente.valor_filtro else 0.00,
                    'Last Changed': cliente.ultima_troca.strftime('%d/%m/%Y') if cliente.ultima_troca else '',
                    'Next Change': cliente.proxima_troca.strftime('%d/%m/%Y') if cliente.proxima_troca else '',
                    'Ultima Troca': cliente.ultima_troca.strftime('%d/%m/%Y') if cliente.ultima_troca else '',
                    'Proxima Troca': cliente.proxima_troca.strftime('%d/%m/%Y') if cliente.proxima_troca else ''
                }
                
                return field_mapping.get(field, '')
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter dados do cliente: {e}")
            return ''
    
    def get_filtered_data(self, status_filter=None, tech_filter=None, month_filter=None):
        """Filtra dados baseado em critérios"""
        # Recarregar dados do banco
        self.load_data()
        
        df_filtered = self.df.copy()
        
        # SEMPRE excluir clientes inativos da visualização
        df_filtered = df_filtered[df_filtered['Status'] != 'Inactive']
        
        # Aplicar filtros
        if status_filter and status_filter != 'Todos':
            df_filtered = df_filtered[df_filtered['Status'] == status_filter]
        
        if tech_filter and tech_filter != 'Todos':
            df_filtered = df_filtered[df_filtered['Route Tech'] == tech_filter]
        
        if month_filter and month_filter != 'Todos':
            # Filtrar por mês da próxima troca
            def filter_by_month(date_str):
                if not date_str:
                    return False
                try:
                    dt = datetime.strptime(date_str, '%d/%m/%Y')
                    return dt.strftime('%m/%Y') == month_filter
                except:
                    return False
            
            df_filtered = df_filtered[df_filtered['Proxima Troca'].apply(filter_by_month)]
        
        return df_filtered
    
    def get_statuses(self):
        """Retorna lista de status únicos"""
        try:
            with db.get_session() as session:
                statuses = session.query(Cliente.status).distinct().all()
                return sorted([s[0] for s in statuses if s[0]])
        except:
            return ['Ativo', 'Ativo sem Rota', 'Inativo', 'Lead']
    
    def get_technicians(self):
        """Retorna lista de piscineiros únicos (filtrando múltiplos piscineiros separados por vírgula)"""
        try:
            with db.get_session() as session:
                techs = session.query(Cliente.piscineiro).distinct().filter(
                    Cliente.piscineiro.isnot(None),
                    Cliente.piscineiro != '',
                    Cliente.piscineiro != 'Não atribuído'
                ).all()
                
                # Extrair piscineiros individuais (casos com vírgula)
                tech_set = set()
                for t in techs:
                    if t[0]:
                        # Se contém vírgula, separar e adicionar individualmente
                        if ',' in t[0]:
                            for name in t[0].split(','):
                                # Normalizar: strip espaços, remover pontos, strip novamente
                                normalized = name.strip().rstrip('.').strip()
                                if normalized:
                                    tech_set.add(normalized)
                        else:
                            # Normalizar: strip espaços, remover pontos, strip novamente
                            normalized = t[0].strip().rstrip('.').strip()
                            if normalized:
                                tech_set.add(normalized)
                
                tech_list = sorted(list(tech_set))
                logger.info(f"✅ Piscineiros encontrados: {tech_list}")
                return tech_list
        except Exception as e:
            logger.error(f"❌ Erro ao buscar piscineiros: {e}")
            return []
    
    def get_available_months(self):
        """Retorna lista de meses disponíveis (baseado em Next Change)"""
        try:
            with db.get_session() as session:
                # Buscar todas as datas de próxima troca
                dates = session.query(Cliente.proxima_troca).filter(
                    Cliente.proxima_troca.isnot(None)
                ).distinct().all()
                
                months = set()
                for date_tuple in dates:
                    if date_tuple[0]:
                        months.add(date_tuple[0].strftime('%m/%Y'))
                
                return sorted(list(months))
        except:
            return []
    
    def name_exists(self, name, exclude_id=None):
        """Verifica se um nome de cliente já existe"""
        try:
            with db.get_session() as session:
                query = session.query(Cliente).filter_by(nome=name)
                
                if exclude_id:
                    query = query.filter(Cliente.id != exclude_id)
                
                return query.first() is not None
        except:
            return False
    
    def add_customer(self, customer_data):
        """
        Adiciona um novo cliente ao banco de dados
        
        Args:
            customer_data: Dicionário com dados do cliente
        
        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            with db.get_session() as session:
                # Verificar se nome já existe
                if self.name_exists(customer_data.get('Name', '')):
                    logger.warning(f"Cliente '{customer_data.get('Name')}' já existe")
                    return False
                
                # Criar novo cliente
                cliente = Cliente(
                    nome=customer_data.get('Name', ''),
                    status=customer_data.get('Status', 'Ativo'),
                    piscineiro=self._normalize_tech(customer_data.get('Route Tech')),
                    valor_rota=Decimal(str(customer_data.get('Route Price', 0))),
                    tipo_filtro=customer_data.get('Tipo Filtro'),
                    valor_filtro=Decimal(str(customer_data.get('Valor Filtro', 0))),
                    ultima_troca=self._parse_date(customer_data.get('Ultima Troca')),
                    proxima_troca=self._parse_date(customer_data.get('Proxima Troca'))
                )
                
                session.add(cliente)
                session.commit()
                
                # Registrar auditoria
                self.log_action('create', cliente_id=cliente.id, nome_cliente=cliente.nome)
                
                logger.info(f"✅ Cliente '{cliente.nome}' adicionado com sucesso")
                
                # Recarregar DataFrame
                self.load_data()
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar cliente: {e}")
            return False
    
    def log_action(self, action, cliente_id=None, nome_cliente=None, campo=None, valor_anterior=None, valor_novo=None):
        """Registra ação na tabela de auditoria"""
        try:
            with db.get_session() as session:
                auditoria = Auditoria(
                    cliente_id=cliente_id,
                    nome_cliente=nome_cliente,
                    acao=action,
                    campo_alterado=campo,
                    valor_anterior=valor_anterior,
                    valor_novo=valor_novo,
                    usuario='Sistema'
                )
                
                session.add(auditoria)
                session.commit()
                
        except Exception as e:
            logger.error(f"❌ Erro ao registrar auditoria: {e}")
    
    def get_monthly_revenue(self):
        """Calcula faturamento mensal total baseado em clientes ativos e valor do filtro"""
        try:
            with db.get_session() as session:
                # Somar valor_filtro de todos os clientes ativos (valor_rota foi zerado)
                total = session.query(func.sum(Cliente.valor_filtro)).filter(
                    or_(
                        Cliente.status == 'Ativo',
                        Cliente.status == 'Active (routed)'
                    )
                ).scalar()
                
                return float(total) if total else 0.00
                
        except Exception as e:
            logger.error(f"❌ Erro ao calcular faturamento mensal: {e}")
            return 0.00
    
    def get_active_customers_count(self):
        """Conta total de clientes ativos"""
        try:
            with db.get_session() as session:
                count = session.query(Cliente).filter(
                    or_(
                        Cliente.status == 'Ativo',
                        Cliente.status == 'Active (routed)'
                    )
                ).count()
                
                return count
                
        except Exception as e:
            logger.error(f"❌ Erro ao contar clientes ativos: {e}")
            return 0
    
    def get_future_maintenance_count(self):
        """Conta manutenções futuras (clientes com próxima troca agendada)"""
        try:
            with db.get_session() as session:
                from datetime import date
                
                count = session.query(Cliente).filter(
                    Cliente.proxima_troca.isnot(None),
                    Cliente.proxima_troca >= date.today()
                ).count()
                
                return count
                
        except Exception as e:
            logger.error(f"❌ Erro ao contar manutenções futuras: {e}")
            return 0
    
    def rename_customer(self, old_name, new_name):
        """Renomeia um cliente"""
        try:
            with db.get_session() as session:
                cliente = session.query(Cliente).filter_by(nome=old_name).first()
                
                if not cliente:
                    logger.warning(f"Cliente '{old_name}' não encontrado para renomear")
                    return False
                
                # Verificar se novo nome já existe
                if self.name_exists(new_name):
                    logger.warning(f"Nome '{new_name}' já existe")
                    return False
                
                old_value = cliente.nome
                cliente.nome = new_name
                
                # Registrar auditoria
                self.log_action(
                    'update',
                    cliente_id=cliente.id,
                    nome_cliente=new_name,
                    campo='nome',
                    valor_anterior=old_value,
                    valor_novo=new_name
                )
                
                session.commit()
                logger.info(f"✅ Cliente renomeado: '{old_name}' → '{new_name}'")
                
                # Recarregar DataFrame
                self.load_data()
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao renomear cliente: {e}")
            return False
