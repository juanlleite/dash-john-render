"""
Atualizar piscineiros em LOTE (muito mais rápido)
"""
import pandas as pd
from database import db
from models import Cliente
from sqlalchemy import update
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar CSV
logger.info("📂 Carregando CSV...")
df = pd.read_csv("L'Acqua Azzurra Pools Customer report-171125135257 - Sheet.csv")

# Normalizar nomes de piscineiros
def normalize_tech(tech_name):
    if not tech_name or pd.isna(tech_name) or str(tech_name).strip() == '':
        return 'Não atribuído'
    tech_name = str(tech_name).strip()
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

# Piscineiros únicos
piscineiros_unicos = set(v for v in clientes_csv.values() if v != 'Não atribuído')
logger.info(f"👥 {len(piscineiros_unicos)} piscineiros únicos: {', '.join(sorted(piscineiros_unicos))}")

# Atualizar em lotes usando SQL direto
logger.info("\n🔄 Atualizando piscineiros (modo lote)...")

with db.get_session() as session:
    updated = 0
    
    # Agrupar por piscineiro para fazer UPDATE em lote
    for piscineiro, nomes_grupo in {}.items():
        pass  # Placeholder
    
    # Fazer update individual mas com commit único
    for nome, piscineiro in clientes_csv.items():
        try:
            result = session.execute(
                update(Cliente)
                .where(Cliente.nome == nome)
                .values(piscineiro=piscineiro)
            )
            if result.rowcount > 0:
                updated += 1
                if updated % 50 == 0:
                    logger.info(f"  ⏳ Processados: {updated}/{len(clientes_csv)}")
        except Exception as e:
            logger.error(f"  ❌ Erro em '{nome}': {e}")
    
    session.commit()
    logger.info(f"\n✅ Total atualizado: {updated}")

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
