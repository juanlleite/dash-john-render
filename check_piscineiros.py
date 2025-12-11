"""Verificar piscineiros no banco"""
from database import db
from models import Cliente
from sqlalchemy import func

with db.get_session() as s:
    result = s.query(Cliente.piscineiro, func.count(Cliente.id)).filter(
        Cliente.piscineiro.isnot(None),
        Cliente.piscineiro != "",
        Cliente.piscineiro != "Não atribuído"
    ).group_by(Cliente.piscineiro).all()
    
    print("\n📊 Piscineiros no banco:")
    if result:
        for piscineiro, count in result:
            print(f"  ✓ {piscineiro}: {count} clientes")
    else:
        print("  ❌ Nenhum piscineiro encontrado!")
    
    # Verificar total de clientes
    total = s.query(Cliente).count()
    print(f"\n📈 Total de clientes: {total}")
    
    # Verificar clientes sem piscineiro
    sem_piscineiro = s.query(Cliente).filter(
        (Cliente.piscineiro.is_(None)) |
        (Cliente.piscineiro == "") |
        (Cliente.piscineiro == "Não atribuído")
    ).count()
    print(f"  ⚠️ Clientes sem piscineiro: {sem_piscineiro}")
