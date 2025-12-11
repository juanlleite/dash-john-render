"""
Atualizar piscineiros dos clientes existentes baseado no CSV
"""
import pandas as pd
from database import db
from models import Cliente
from decimal import Decimal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar CSV
logger.info("📂 Carregando CSV...")
df = pd.read_csv("L'Acqua Azzurra Pools Customer report-171125135257 - Sheet.csv")

# Normalizar nomes de piscineiros
def normalize_tech(tech_name):
    """Normaliza nome do piscineiro"""
    if not tech_name or pd.isna(tech_name) or str(tech_name).strip() == '':
        return 'Não atribuído'
    
    tech_name = str(tech_name).strip()
    
    # Remover pontos finais
    if tech_name.endswith('.'):
        tech_name = tech_name[:-1].strip()
    
    return tech_name

# Mapear dados do CSV
clientes_csv = {}
for _, row in df.iterrows():
    nome = str(row['Name']).strip()
    piscineiro = normalize_tech(row.get('Route Tech', ''))
    clientes_csv[nome] = piscineiro

logger.info(f"✅ {len(clientes_csv)} clientes no CSV")

# Contar piscineiros únicos
piscineiros_unicos = set(v for v in clientes_csv.values() if v != 'Não atribuído')
logger.info(f"👥 {len(piscineiros_unicos)} piscineiros únicos: {', '.join(sorted(piscineiros_unicos))}")

# Atualizar banco
logger.info("\n🔄 Atualizando piscineiros no banco...")
updated = 0
not_found = 0
already_set = 0

with db.get_session() as session:
    for nome, piscineiro in clientes_csv.items():
        cliente = session.query(Cliente).filter_by(nome=nome).first()
        
        if not cliente:
            not_found += 1
            continue
        
        # Verificar se já está correto
        if cliente.piscineiro == piscineiro:
            already_set += 1
            continue
        
        # Atualizar
        old_value = cliente.piscineiro
        cliente.piscineiro = piscineiro
        updated += 1
        
        if updated <= 10:  # Mostrar primeiros 10
            logger.info(f"  ✓ {nome}: '{old_value}' → '{piscineiro}'")
    
    session.commit()

logger.info(f"\n✅ Atualização concluída:")
logger.info(f"  📝 Atualizados: {updated}")
logger.info(f"  ✓ Já corretos: {already_set}")
logger.info(f"  ❌ Não encontrados: {not_found}")

# Verificar resultado
logger.info("\n🔍 Verificando resultado...")
with db.get_session() as session:
    from sqlalchemy import func
    
    result = session.query(Cliente.piscineiro, func.count(Cliente.id)).filter(
        Cliente.piscineiro.isnot(None),
        Cliente.piscineiro != "",
        Cliente.piscineiro != "Não atribuído"
    ).group_by(Cliente.piscineiro).all()
    
    logger.info("\n📊 Piscineiros no banco agora:")
    if result:
        for piscineiro, count in result:
            logger.info(f"  ✓ {piscineiro}: {count} clientes")
    else:
        logger.info("  ❌ Nenhum piscineiro encontrado!")

print("\n🎉 Processo finalizado!")
