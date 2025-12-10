"""
Script de Migração: CSV/JSON → PostgreSQL
Importa todos os dados existentes para o banco de dados
"""
import sys
import os
from datetime import datetime
from decimal import Decimal
import pandas as pd
import json

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db, init_db
from models import Cliente, Auditoria


def parse_date(date_str):
    """Converte string DD/MM/YYYY para objeto date"""
    if not date_str or pd.isna(date_str):
        return None
    
    if isinstance(date_str, str):
        try:
            return datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return None
    return None


def normalize_technician(tech_name):
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


def migrate_from_csv(csv_path):
    """Migra dados do CSV original para PostgreSQL"""
    print(f"\n📂 Lendo CSV: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"✅ CSV carregado: {len(df)} registros")
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return 0
    
    # Mapear colunas do CSV
    column_mapping = {
        'Name': 'nome',
        'Status': 'status',
        'Technician': 'piscineiro',
        'Route Price': 'valor_rota',
        'Charge Method': 'metodo_cobranca',
        'Auto-Pay': 'auto_pay',
        'Last Changed': 'ultima_troca',
        'Next Change': 'proxima_troca'
    }
    
    migrated = 0
    skipped = 0
    
    with db.get_session() as session:
        for idx, row in df.iterrows():
            try:
                # Verificar se cliente já existe
                nome = str(row.get('Name', '')).strip()
                if not nome:
                    print(f"⚠️ Linha {idx+1}: Nome vazio, pulando...")
                    skipped += 1
                    continue
                
                existing = session.query(Cliente).filter_by(nome=nome).first()
                if existing:
                    print(f"⚠️ Cliente '{nome}' já existe, pulando...")
                    skipped += 1
                    continue
                
                # Processar campos
                status = str(row.get('Status', 'Ativo')).strip()
                piscineiro = normalize_technician(row.get('Technician'))
                
                # Valor da rota
                valor_rota = row.get('Route Price', 0)
                if pd.isna(valor_rota):
                    valor_rota = 0
                valor_rota = Decimal(str(valor_rota))
                
                # Auto-pay
                auto_pay_value = row.get('Auto-Pay', 'No')
                auto_pay = str(auto_pay_value).strip().lower() in ['yes', 'sim', 'true', '1']
                
                # Datas
                ultima_troca = parse_date(row.get('Last Changed'))
                proxima_troca = parse_date(row.get('Next Change'))
                
                # Criar cliente
                cliente = Cliente(
                    nome=nome,
                    status=status,
                    piscineiro=piscineiro,
                    valor_rota=valor_rota,
                    metodo_cobranca=str(row.get('Charge Method', '')).strip() or None,
                    auto_pay=auto_pay,
                    ultima_troca=ultima_troca,
                    proxima_troca=proxima_troca
                )
                
                session.add(cliente)
                session.flush()  # Flush individual para detectar duplicatas
                migrated += 1
                
                if migrated % 10 == 0:
                    print(f"  📝 Migrados: {migrated} clientes...")
                    session.commit()  # Commit parcial a cada 10 registros
                
            except Exception as e:
                print(f"⚠️ Erro na linha {idx+1} ({nome}): {str(e)[:100]}")
                session.rollback()  # Rollback apenas deste registro
                skipped += 1
                continue
        
        # Commit final
        try:
            session.commit()
        except:
            session.rollback()
    
    print(f"\n✅ Migração do CSV concluída:")
    print(f"   • Migrados: {migrated}")
    print(f"   • Pulados: {skipped}")
    
    return migrated


def migrate_from_json(json_path):
    """Migra dados extras do JSON (novos clientes, auditoria)"""
    if not os.path.exists(json_path):
        print(f"⚠️ Arquivo {json_path} não encontrado, pulando...")
        return 0
    
    print(f"\n📂 Lendo JSON: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler JSON: {e}")
        return 0
    
    migrated = 0
    
    with db.get_session() as session:
        # Migrar novos clientes
        new_customers = data.get('_new_customers', [])
        print(f"📊 Novos clientes no JSON: {len(new_customers)}")
        
        for customer_data in new_customers:
            try:
                nome = customer_data.get('Name', '').strip()
                if not nome:
                    continue
                
                # Verificar se já existe
                existing = session.query(Cliente).filter_by(nome=nome).first()
                if existing:
                    continue
                
                cliente = Cliente(
                    nome=nome,
                    status=customer_data.get('Status', 'Ativo'),
                    piscineiro=normalize_technician(customer_data.get('Technician')),
                    valor_rota=Decimal(str(customer_data.get('Route Price', 0))),
                    metodo_cobranca=customer_data.get('Charge Method'),
                    auto_pay=customer_data.get('Auto-Pay', 'No').lower() in ['yes', 'sim'],
                    ultima_troca=parse_date(customer_data.get('Last Changed')),
                    proxima_troca=parse_date(customer_data.get('Next Change'))
                )
                
                session.add(cliente)
                migrated += 1
                
            except Exception as e:
                print(f"❌ Erro ao migrar cliente do JSON: {e}")
                continue
        
        session.commit()
    
    print(f"✅ Migrados {migrated} novos clientes do JSON")
    
    return migrated


def main():
    """Executa a migração completa"""
    print("\n" + "="*60)
    print("🔄 MIGRAÇÃO DE DADOS: CSV/JSON → PostgreSQL")
    print("="*60)
    
    # Inicializar banco de dados
    print("\n🗄️ Inicializando banco de dados...")
    init_db()
    
    # Verificar estado atual
    with db.get_session() as session:
        current_count = session.query(Cliente).count()
        print(f"📊 Clientes atuais no banco: {current_count}")
    
    if current_count > 0:
        response = input("\n⚠️ Já existem dados no banco. Continuar? (s/N): ")
        if response.lower() != 's':
            print("❌ Migração cancelada.")
            return
    
    # Migrar do CSV
    csv_path = "L'Acqua Azzurra Pools Customer report-171125135257 - Sheet.csv"
    total_migrated = migrate_from_csv(csv_path)
    
    # Migrar do JSON
    json_path = "data_storage.json"
    total_migrated += migrate_from_json(json_path)
    
    # Relatório final
    print("\n" + "="*60)
    print("✅ MIGRAÇÃO CONCLUÍDA")
    print("="*60)
    
    with db.get_session() as session:
        total_clientes = session.query(Cliente).count()
        total_auditoria = session.query(Auditoria).count()
        
        print(f"\n📊 Estatísticas finais:")
        print(f"   • Total de clientes: {total_clientes}")
        print(f"   • Registros de auditoria: {total_auditoria}")
        print(f"   • Novos registros migrados: {total_migrated}")
        
        # Estatísticas por status
        print(f"\n📈 Por status:")
        statuses = session.query(Cliente.status, session.query(Cliente).filter_by(status=Cliente.status).count()).\
            group_by(Cliente.status).all()
        
        from sqlalchemy import func
        status_counts = session.query(
            Cliente.status,
            func.count(Cliente.id)
        ).group_by(Cliente.status).all()
        
        for status, count in status_counts:
            print(f"   • {status}: {count}")
    
    print("\n✅ Migração concluída com sucesso!\n")


if __name__ == '__main__':
    main()
