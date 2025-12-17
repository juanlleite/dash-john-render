#!/usr/bin/env python3
"""
Script para popular piscineiros no banco SQLite de produção
Baseado nos dados do PostgreSQL
"""

import sqlite3
import os

# Mapeamento de piscineiros (baseado no que tínhamos no PostgreSQL)
PISCINEIROS_MAPPING = {
    'Aaron Robichaud CC': 'Drask Silva',
    'Adrienne Williams CC': 'Lucca',
    'Aimara Linn Sage': 'Pedro Santos',
    'Al Bayati': 'Vini Penner',
    'Alan Falcone': 'Drask Silva',
    'Alan Velazquez': 'Lucca',
    'Albert Lee': 'Pedro Santos',
    'Albert Licea': 'Vini Penner',
}

def populate_piscineiros(db_path):
    """Popula piscineiros no banco SQLite"""
    
    print("🔄 Populando piscineiros no banco de dados...")
    print(f"📁 Banco: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Verificar clientes existentes
        print("\n1️⃣ Verificando clientes...")
        cursor.execute("SELECT nome, piscineiro FROM clientes ORDER BY nome")
        clientes = cursor.fetchall()
        print(f"   Total de clientes: {len(clientes)}")
        
        # 2. Atualizar piscineiros conhecidos
        print("\n2️⃣ Atualizando piscineiros conhecidos...")
        updated_count = 0
        for nome, piscineiro_atual in clientes:
            if nome in PISCINEIROS_MAPPING:
                novo_piscineiro = PISCINEIROS_MAPPING[nome]
                cursor.execute("""
                    UPDATE clientes 
                    SET piscineiro = ? 
                    WHERE nome = ?
                """, (novo_piscineiro, nome))
                print(f"   ✅ {nome} → {novo_piscineiro}")
                updated_count += 1
        
        print(f"\n   Total atualizado: {updated_count} clientes")
        
        # 3. Mostrar distribuição
        print("\n3️⃣ Distribuição de piscineiros:")
        cursor.execute("""
            SELECT piscineiro, COUNT(*) as total 
            FROM clientes 
            GROUP BY piscineiro 
            ORDER BY total DESC
        """)
        distribuicao = cursor.fetchall()
        for piscineiro, total in distribuicao:
            print(f"   {piscineiro or 'NULL'}: {total} clientes")
        
        # 4. Listar piscineiros únicos
        print("\n4️⃣ Piscineiros únicos no sistema:")
        cursor.execute("""
            SELECT DISTINCT piscineiro 
            FROM clientes 
            WHERE piscineiro IS NOT NULL 
            AND piscineiro != '' 
            AND piscineiro != 'Não atribuído'
            ORDER BY piscineiro
        """)
        piscineiros = cursor.fetchall()
        for p in piscineiros:
            print(f"   🏊 {p[0]}")
        
        # Commit
        conn.commit()
        
        print("\n✅ Piscineiros populados com sucesso!")
        print(f"\n📊 Total de piscineiros únicos: {len(piscineiros)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    # Detectar ambiente
    if os.path.exists('/home/juanleite'):
        DB_PATH = '/home/juanleite/dashboard/lacqua_azzurra.db'
        print("🌐 Ambiente: PythonAnywhere")
    else:
        DB_PATH = 'lacqua_azzurra.db'
        print("💻 Ambiente: Local")
    
    print(f"\n{'='*60}")
    print("🏊 POPULAR PISCINEIROS")
    print(f"{'='*60}\n")
    
    success = populate_piscineiros(DB_PATH)
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 CONCLUÍDO!")
        print(f"{'='*60}")
        print("\n⚠️ IMPORTANTE: Faça reload do web app no PythonAnywhere!")
