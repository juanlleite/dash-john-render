"""
Configuração e gerenciamento do banco de dados
Suporta: MySQL (Hostinger), PostgreSQL (Render), SQLite (local)
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import contextmanager
from models import Base, Cliente, Auditoria
import logging

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Classe para gerenciar conexões e sessões do banco de dados"""
    
    def __init__(self, database_url=None):
        """
        Inicializa a conexão com o banco de dados
        
        Args:
            database_url: URL de conexão PostgreSQL (se None, usa variável de ambiente)
        """
        # Obter URL do banco de dados
        if database_url is None:
            database_url = os.getenv('DATABASE_URL')
        
        # Fallback para SQLite local em desenvolvimento
        if not database_url:
            database_url = 'sqlite:///local_database.db'
            logger.warning("DATABASE_URL não definida. Usando SQLite local para desenvolvimento.")
        
        # Fix para Render/Heroku (postgres:// → postgresql://)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        self.database_url = database_url
        self.is_sqlite = database_url.startswith('sqlite')
        self.is_mysql = database_url.startswith('mysql')
        self.is_postgresql = database_url.startswith('postgresql')
        
        # Configurar engine baseado no tipo de banco
        engine_kwargs = {
            'echo': False,  # True para debug SQL
            'pool_pre_ping': True,  # Verifica conexões antes de usar
            'pool_recycle': 3600,  # Reciclar conexões a cada 1 hora
        }
        
        if self.is_mysql:
            # Configuração para MySQL (Hostinger)
            engine_kwargs['poolclass'] = QueuePool
            engine_kwargs['pool_size'] = 5
            engine_kwargs['max_overflow'] = 10
            engine_kwargs['pool_timeout'] = 30
            engine_kwargs['connect_args'] = {
                'connect_timeout': 10,
                'charset': 'utf8mb4'
            }
        elif self.is_postgresql:
            # Configuração para PostgreSQL (Render/outras plataformas)
            engine_kwargs['poolclass'] = NullPool  # Sem pool - abre/fecha imediatamente
            engine_kwargs['connect_args'] = {
                'connect_timeout': 10
            }
        # SQLite não precisa de configurações especiais
        
        self.engine = create_engine(database_url, **engine_kwargs)
        
        # Criar sessão factory
        self.SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        )
        
        logger.info(f"✅ Banco de dados configurado: {self._mask_url(database_url)}")
    
    def _mask_url(self, url):
        """Mascara senha na URL para logs"""
        if '@' in url:
            protocol, rest = url.split('://', 1)
            if '@' in rest:
                credentials, host = rest.split('@', 1)
                if ':' in credentials:
                    user, _ = credentials.split(':', 1)
                    return f"{protocol}://{user}:***@{host}"
        return url
    
    def create_all_tables(self):
        """Cria todas as tabelas no banco de dados"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Tabelas criadas/verificadas com sucesso")
            
            # Verificar se há dados
            with self.get_session() as session:
                count = session.query(Cliente).count()
                logger.info(f"📊 Total de clientes no banco: {count}")
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            raise
    
    def drop_all_tables(self):
        """Remove todas as tabelas (CUIDADO!)"""
        logger.warning("⚠️ Removendo todas as tabelas do banco de dados...")
        Base.metadata.drop_all(bind=self.engine)
        logger.info("✅ Tabelas removidas")
    
    @contextmanager
    def get_session(self):
        """
        Context manager para sessões do banco de dados
        
        Usage:
            with db.get_session() as session:
                clientes = session.query(Cliente).all()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erro na sessão do banco: {e}")
            raise
        finally:
            session.close()
    
    def close(self):
        """Fecha todas as conexões"""
        self.SessionLocal.remove()
        self.engine.dispose()
        logger.info("🔒 Conexões do banco de dados fechadas")


# Instância global do banco de dados
db = Database()


def init_db():
    """Inicializa o banco de dados (criar tabelas)"""
    db.create_all_tables()


def get_db_session():
    """Retorna uma nova sessão do banco de dados"""
    return db.get_session()


if __name__ == '__main__':
    # Teste de conexão
    print("🧪 Testando conexão com banco de dados...\n")
    
    # Criar tabelas
    init_db()
    
    # Testar inserção
    with db.get_session() as session:
        # Verificar se já existe cliente de teste
        teste = session.query(Cliente).filter_by(nome='Cliente Teste').first()
        
        if not teste:
            print("📝 Criando cliente de teste...")
            cliente_teste = Cliente(
                nome='Cliente Teste',
                status='Ativo',
                piscineiro='João Silva',
                valor_rota=150.00,
                auto_pay=True
            )
            session.add(cliente_teste)
            session.commit()
            print(f"✅ Cliente criado: {cliente_teste}")
        else:
            print(f"✅ Cliente de teste já existe: {teste}")
        
        # Contar total de clientes
        total = session.query(Cliente).count()
        print(f"\n📊 Total de clientes: {total}")
    
    print("\n✅ Teste concluído com sucesso!")
