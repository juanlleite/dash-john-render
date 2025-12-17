#!/usr/bin/env python3
"""
Script de correção para produção - limpa dados incorretos
"""

import os
import sqlite3
from datetime import datetime

def fix_database(db_path):
    """Corrige dados migrados incorretamente"""
    
    print("🔧 Iniciando correção do banco de dados...")
    print(f"📁 Banco: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Limpar tipo_filtro que tem valores de pagamento
        print("\n1️⃣ Limpando tipo_filtro com dados incorretos...")
        cursor.execute("""
            UPDATE clientes 
            SET tipo_filtro = NULL 
            WHERE tipo_filtro IN ('Cash', 'Advance', 'Check', 'nan', 'None', '')
        """)
        print(f"   ✅ {cursor.rowcount} registros limpos")
        
        # 2. Verificar se existe coluna metodo_cobranca ainda
        cursor.execute("PRAGMA table_info(clientes)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"\n📊 Colunas disponíveis: {', '.join(columns)}")
        
        # 3. Limpar valor_filtro zerado
        print("\n2️⃣ Limpando valor_filtro zerado...")
        cursor.execute("""
            UPDATE clientes 
            SET valor_filtro = NULL 
            WHERE valor_filtro = 0 OR valor_filtro IS NULL
        """)
        print(f"   ✅ {cursor.rowcount} registros atualizados")
        
        # 4. Verificar piscineiros existentes
        print("\n3️⃣ Verificando piscineiros...")
        cursor.execute("SELECT piscineiro, COUNT(*) FROM clientes GROUP BY piscineiro")
        piscineiros = cursor.fetchall()
        print(f"   Distribuição atual:")
        for p, count in piscineiros:
            print(f"      {p}: {count} clientes")
        
        # 5. Estatísticas finais
        print("\n📊 Estatísticas após correção:")
        
        cursor.execute("SELECT COUNT(*) FROM clientes")
        total = cursor.fetchone()[0]
        print(f"   Total de clientes: {total}")
        
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE tipo_filtro IS NOT NULL AND tipo_filtro != ''")
        com_filtro = cursor.fetchone()[0]
        print(f"   Clientes com tipo_filtro válido: {com_filtro}")
        
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE valor_filtro IS NOT NULL AND valor_filtro > 0")
        com_valor = cursor.fetchone()[0]
        print(f"   Clientes com valor_filtro: {com_valor}")
        
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE piscineiro != 'Não atribuído'")
        com_piscineiro = cursor.fetchone()[0]
        print(f"   Clientes com piscineiro atribuído: {com_piscineiro}")
        
        # Commit das mudanças
        conn.commit()
        
        print("\n✅ Correção concluída com sucesso!")
        print("\n⚠️ IMPORTANTE: Agora você precisa preencher manualmente:")
        print("   - tipo_filtro: Tipo de filtro da piscina (Jandy, Pentair, etc.)")
        print("   - valor_filtro: Valor do serviço de manutenção")
        print("   - piscineiro: Nome do piscineiro responsável")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante correção: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def backup_database(db_path):
    """Cria backup do banco antes da correção"""
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
    print("🔧 CORREÇÃO DO BANCO DE DADOS")
    print(f"{'='*60}\n")
    
    # Criar backup
    backup_path = backup_database(DB_PATH)
    
    if backup_path:
        print(f"\n⚠️ IMPORTANTE: Backup criado em {backup_path}")
        print("   Em caso de problema, você pode restaurá-lo.\n")
    
    # Executar correção
    success = fix_database(DB_PATH)
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 CORREÇÃO CONCLUÍDA!")
        print(f"{'='*60}")
