#!/usr/bin/env python3
"""
Script de migração para atualizar banco SQLite do PythonAnywhere
com a nova estrutura (tipo_filtro, valor_filtro)
"""

import os
import sqlite3
from datetime import datetime

def migrate_database(db_path):
    """Aplica todas as migrações necessárias"""
    
    print("🔄 Iniciando migração do banco de dados...")
    print(f"📁 Banco: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Verificar e adicionar coluna tipo_filtro
        print("\n1️⃣ Verificando coluna tipo_filtro...")
        cursor.execute("PRAGMA table_info(clientes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tipo_filtro' not in columns:
            print("   ➕ Adicionando coluna tipo_filtro...")
            cursor.execute("ALTER TABLE clientes ADD COLUMN tipo_filtro VARCHAR(100)")
            print("   ✅ Coluna tipo_filtro adicionada")
        else:
            print("   ✅ Coluna tipo_filtro já existe")
        
        # 2. Verificar e adicionar coluna valor_filtro
        print("\n2️⃣ Verificando coluna valor_filtro...")
        if 'valor_filtro' not in columns:
            print("   ➕ Adicionando coluna valor_filtro...")
            cursor.execute("ALTER TABLE clientes ADD COLUMN valor_filtro DECIMAL(10,2)")
            print("   ✅ Coluna valor_filtro adicionada")
        else:
            print("   ✅ Coluna valor_filtro já existe")
        
        # 3. Migrar dados de metodo_cobranca para tipo_filtro (se existir)
        print("\n3️⃣ Migrando dados metodo_cobranca → tipo_filtro...")
        if 'metodo_cobranca' in columns:
            cursor.execute("""
                UPDATE clientes 
                SET tipo_filtro = metodo_cobranca 
                WHERE metodo_cobranca IS NOT NULL 
                AND (tipo_filtro IS NULL OR tipo_filtro = '')
            """)
            migrated = cursor.rowcount
            print(f"   ✅ {migrated} registros migrados")
        else:
            print("   ℹ️ Coluna metodo_cobranca não existe (já foi removida)")
        
        # 4. Zerar valor_rota (preparação para novo sistema)
        print("\n4️⃣ Zerando valor_rota...")
        cursor.execute("UPDATE clientes SET valor_rota = 0 WHERE valor_rota IS NOT NULL")
        print(f"   ✅ {cursor.rowcount} registros atualizados")
        
        # 5. Normalizar piscineiros (remover espaços extras)
        print("\n5️⃣ Normalizando piscineiros...")
        cursor.execute("""
            UPDATE clientes 
            SET piscineiro = TRIM(piscineiro)
            WHERE piscineiro IS NOT NULL AND piscineiro != TRIM(piscineiro)
        """)
        print(f"   ✅ {cursor.rowcount} registros normalizados")
        
        # 6. Atualizar clientes sem piscineiro
        print("\n6️⃣ Atualizando clientes sem piscineiro...")
        cursor.execute("""
            UPDATE clientes 
            SET piscineiro = 'Não atribuído'
            WHERE piscineiro IS NULL OR piscineiro = '' OR piscineiro = 'None'
        """)
        print(f"   ✅ {cursor.rowcount} clientes atualizados para 'Não atribuído'")
        
        # 7. Estatísticas finais
        print("\n📊 Estatísticas do banco atualizado:")
        
        cursor.execute("SELECT COUNT(*) FROM clientes")
        total = cursor.fetchone()[0]
        print(f"   Total de clientes: {total}")
        
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE tipo_filtro IS NOT NULL AND tipo_filtro != ''")
        com_filtro = cursor.fetchone()[0]
        print(f"   Clientes com tipo_filtro: {com_filtro}")
        
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE valor_filtro IS NOT NULL AND valor_filtro > 0")
        com_valor = cursor.fetchone()[0]
        print(f"   Clientes com valor_filtro: {com_valor}")
        
        cursor.execute("SELECT piscineiro, COUNT(*) FROM clientes GROUP BY piscineiro ORDER BY COUNT(*) DESC")
        piscineiros = cursor.fetchall()
        print(f"\n   Distribuição de piscineiros:")
        for p, count in piscineiros:
            print(f"      {p}: {count} clientes")
        
        # Commit das mudanças
        conn.commit()
        
        print("\n✅ Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante migração: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def backup_database(db_path):
    """Cria backup do banco antes da migração"""
    if not os.path.exists(db_path):
        print(f"⚠️ Banco de dados não encontrado: {db_path}")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    print(f"💾 Criando backup: {backup_path}")
    
    import shutil
    shutil.copy2(db_path, backup_path)
    
    print(f"✅ Backup criado com sucesso!")
    return backup_path

if __name__ == "__main__":
    # Detectar ambiente
    if os.path.exists('/home/juanleite'):
        # PythonAnywhere
        DB_PATH = '/home/juanleite/dashboard/lacqua_azzurra.db'
        print("🌐 Ambiente: PythonAnywhere")
    else:
        # Local
        DB_PATH = 'lacqua_azzurra.db'
        print("💻 Ambiente: Local")
    
    print(f"\n{'='*60}")
    print("🚀 MIGRAÇÃO DO BANCO DE DADOS SQLITE")
    print(f"{'='*60}\n")
    
    # Criar backup
    backup_path = backup_database(DB_PATH)
    
    if backup_path:
        print(f"\n⚠️ IMPORTANTE: Backup criado em {backup_path}")
        print("   Em caso de problema, você pode restaurá-lo.\n")
    
    # Executar migração
    success = migrate_database(DB_PATH)
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 MIGRAÇÃO CONCLUÍDA!")
        print(f"{'='*60}")
        print("\n📝 Próximos passos:")
        print("   1. Atualize o arquivo .env com:")
        print(f"      DATABASE_URL=sqlite:///{DB_PATH}")
        print("   2. Reinicie a aplicação")
        print("   3. Teste o dashboard")
    else:
        print(f"\n{'='*60}")
        print("❌ MIGRAÇÃO FALHOU")
        print(f"{'='*60}")
        if backup_path:
            print(f"\n💾 Para restaurar o backup:")
            print(f"   mv {backup_path} {DB_PATH}")
