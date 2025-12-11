"""
Models do Banco de Dados - L'Acqua Azzurra
Tabelas: clientes, auditoria
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, DateTime, ForeignKey, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Cliente(Base):
    """Tabela principal de clientes e manutenções de piscinas"""
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False, unique=True, index=True)
    status = Column(String(50), nullable=False, default='Ativo', index=True)
    piscineiro = Column(String(100), default='Não atribuído', index=True)
    valor_rota = Column(Numeric(10, 2), default=0.00)  # SERÁ ZERADO - agora é valor_filtro
    tipo_filtro = Column(String(100))  # NOVO: Marca e modelo do filtro (ex: Hayward C750)
    valor_filtro = Column(Numeric(10, 2), default=0.00)  # NOVO: Valor do filtro
    ultima_troca = Column(Date)
    proxima_troca = Column(Date, index=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Índices compostos para queries comuns
    __table_args__ = (
        Index('idx_status_piscineiro', 'status', 'piscineiro'),
        Index('idx_proxima_troca_status', 'proxima_troca', 'status'),
    )
    
    def __repr__(self):
        return f"<Cliente(id={self.id}, nome='{self.nome}', status='{self.status}')>"
    
    def to_dict(self):
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'status': self.status,
            'piscineiro': self.piscineiro,
            'valor_rota': float(self.valor_rota) if self.valor_rota else 0.00,
            'tipo_filtro': self.tipo_filtro,
            'valor_filtro': float(self.valor_filtro) if self.valor_filtro else 0.00,
            'ultima_troca': self.ultima_troca.strftime('%d/%m/%Y') if self.ultima_troca else None,
            'proxima_troca': self.proxima_troca.strftime('%d/%m/%Y') if self.proxima_troca else None,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }


class Auditoria(Base):
    """Tabela de auditoria para rastrear todas as alterações"""
    __tablename__ = 'auditoria'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id', ondelete='SET NULL'), index=True)
    nome_cliente = Column(String(255))  # Guardar nome para histórico
    acao = Column(String(50), nullable=False)  # 'create', 'update', 'delete'
    campo_alterado = Column(String(100))
    valor_anterior = Column(Text)
    valor_novo = Column(Text)
    usuario = Column(String(100), default='Sistema')
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<Auditoria(id={self.id}, acao='{self.acao}', cliente='{self.nome_cliente}')>"
    
    def to_dict(self):
        """Converte objeto para dicionário"""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'nome_cliente': self.nome_cliente,
            'acao': self.acao,
            'campo_alterado': self.campo_alterado,
            'valor_anterior': self.valor_anterior,
            'valor_novo': self.valor_novo,
            'usuario': self.usuario,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
