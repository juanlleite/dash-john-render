#!/usr/bin/env python3
"""
Script para popular piscineiros DIRETAMENTE no SQLite
Sem depender do PostgreSQL
"""

import sqlite3
import os

# Piscineiros conhecidos do sistema
PISCINEIROS = ['Drask Silva', 'Lucca', 'Pedro Santos', 'Vini Penner']

def populate_piscineiros_simple(db_path):
    """Popula piscineiros distribuindo igualmente entre os clientes"""
    
    print("🔄 Populando piscineiros no SQLite...")
    print(f"📁 Banco: {db_path}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Buscar todos os clientes sem piscineiro
        cursor.execute("""
            SELECT nome FROM clientes 
            WHERE piscineiro IS NULL OR piscineiro = '' OR piscineiro = 'Não atribuído'
            ORDER BY nome
        """)
        clientes = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Clientes sem piscineiro: {len(clientes)}")
        print(f"🏊 Piscineiros disponíveis: {', '.join(PISCINEIROS)}\n")
        
        # 2. Distribuir igualmente
        total_piscineiros = len(PISCINEIROS)
        updated = 0
        
        for i, nome in enumerate(clientes):
            # Distribuir em round-robin
            piscineiro = PISCINEIROS[i % total_piscineiros]
            
            cursor.execute("""
                UPDATE clientes 
                SET piscineiro = ? 
                WHERE nome = ?
            """, (piscineiro, nome))
            
            updated += 1
            if updated <= 10:  # Mostrar primeiros 10
                print(f"   ✅ {nome} → {piscineiro}")
        
        if updated > 10:
            print(f"   ... e mais {updated - 10} clientes atualizados")
        
        # Commit
        conn.commit()
        
        # 3. Estatísticas finais
        print(f"\n📊 Distribuição final:")
        cursor.execute("""
            SELECT piscineiro, COUNT(*) as total 
            FROM clientes 
            GROUP BY piscineiro 
            ORDER BY total DESC
        """)
        for piscineiro, count in cursor.fetchall():
            print(f"   🏊 {piscineiro}: {count} clientes")
        
        # 4. Verificar piscineiros únicos
        print(f"\n🎯 Piscineiros no sistema:")
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
        
        print(f"\n✅ Total atualizado: {updated} clientes")
        print(f"✅ {len(piscineiros)} piscineiros ativos")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        conn.close()
        return False

if __name__ == "__main__":
    DB_PATH = '/home/juanleite/dashboard/lacqua_azzurra.db' if os.path.exists('/home/juanleite') else 'lacqua_azzurra.db'
    
    print(f"\n{'='*60}")
    print("🏊 POPULAR PISCINEIROS DIRETAMENTE")
    print(f"{'='*60}\n")
    
    success = populate_piscineiros_simple(DB_PATH)
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 CONCLUÍDO!")
        print(f"{'='*60}")
        print("\n⚠️ Faça RELOAD do web app no PythonAnywhere!")
