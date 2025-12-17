#!/usr/bin/env python3
"""
Script para sincronizar piscineiros do PostgreSQL para SQLite
"""

import sqlite3
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Cliente

def sync_piscineiros_from_postgres():
    """Copia piscineiros do PostgreSQL para SQLite"""
    
    # Configuração
    SQLITE_PATH = '/home/juanleite/dashboard/lacqua_azzurra.db' if os.path.exists('/home/juanleite') else 'lacqua_azzurra.db'
    POSTGRES_URL = 'postgresql://lacqua_azzurra_db_user:Pzl3jEA1TaInwwbYMh67IEsvjIdUhpfg@dpg-d4snmj7pm1nc73c7dcdg-a.virginia-postgres.render.com/lacqua_azzurra_db?sslmode=require'
    
    print("🔄 Sincronizando piscineiros PostgreSQL → SQLite...")
    print(f"📁 SQLite: {SQLITE_PATH}")
    print(f"🐘 PostgreSQL: Render")
    
    try:
        # Conectar PostgreSQL
        print("\n1️⃣ Conectando ao PostgreSQL...")
        pg_engine = create_engine(POSTGRES_URL)
        PGSession = sessionmaker(bind=pg_engine)
        pg_session = PGSession()
        
        # Buscar todos os clientes do PostgreSQL
        print("2️⃣ Buscando clientes do PostgreSQL...")
        pg_clientes = pg_session.query(Cliente.nome, Cliente.piscineiro).all()
        print(f"   ✅ {len(pg_clientes)} clientes encontrados")
        
        # Conectar SQLite
        print("\n3️⃣ Atualizando SQLite...")
        sqlite_conn = sqlite3.connect(SQLITE_PATH)
        sqlite_cursor = sqlite_conn.cursor()
        
        updated = 0
        not_found = 0
        
        for nome, piscineiro in pg_clientes:
            # Verificar se cliente existe no SQLite
            sqlite_cursor.execute("SELECT id FROM clientes WHERE nome = ?", (nome,))
            result = sqlite_cursor.fetchone()
            
            if result:
                # Atualizar piscineiro
                piscineiro_value = piscineiro if piscineiro else 'Não atribuído'
                sqlite_cursor.execute("""
                    UPDATE clientes 
                    SET piscineiro = ? 
                    WHERE nome = ?
                """, (piscineiro_value, nome))
                updated += 1
                if updated <= 10:  # Mostrar primeiros 10
                    print(f"   ✅ {nome} → {piscineiro_value}")
            else:
                not_found += 1
        
        if updated > 10:
            print(f"   ... e mais {updated - 10} clientes atualizados")
        
        # Commit
        sqlite_conn.commit()
        
        # Estatísticas
        print(f"\n📊 Estatísticas:")
        print(f"   Atualizados: {updated}")
        print(f"   Não encontrados no SQLite: {not_found}")
        
        # Distribuição final
        print("\n4️⃣ Distribuição de piscineiros no SQLite:")
        sqlite_cursor.execute("""
            SELECT piscineiro, COUNT(*) as total 
            FROM clientes 
            WHERE piscineiro IS NOT NULL AND piscineiro != 'Não atribuído'
            GROUP BY piscineiro 
            ORDER BY total DESC
        """)
        distribuicao = sqlite_cursor.fetchall()
        for piscineiro, total in distribuicao:
            print(f"   🏊 {piscineiro}: {total} clientes")
        
        # Fechar conexões
        sqlite_conn.close()
        pg_session.close()
        
        print("\n✅ Sincronização concluída!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print("🔄 SINCRONIZAR PISCINEIROS")
    print(f"{'='*60}\n")
    
    success = sync_piscineiros_from_postgres()
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 CONCLUÍDO!")
        print(f"{'='*60}")
        print("\n⚠️ Faça reload do web app no PythonAnywhere!")
