"""
Script de Migração: Adicionar colunas tipo_filtro e valor_filtro
Remove colunas metodo_cobranca e auto_pay
Zera valor_rota (não usado mais)
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///lacqua_azzurra.db')

def migrate_schema():
    """Atualiza estrutura do banco de dados"""
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        
        with engine.connect() as conn:
            logger.info("🔧 Iniciando migração do schema...")
            
            # Detectar tipo de banco
            is_sqlite = 'sqlite' in DATABASE_URL.lower()
            
            if is_sqlite:
                logger.info("📦 Banco SQLite detectado")
                
                # SQLite não suporta DROP COLUMN diretamente
                # Precisamos recriar a tabela
                
                # 1. Criar tabela temporária com nova estrutura
                conn.execute(text("""
                    CREATE TABLE clientes_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome VARCHAR(255) NOT NULL UNIQUE,
                        status VARCHAR(50) NOT NULL DEFAULT 'Ativo',
                        piscineiro VARCHAR(100) DEFAULT 'Não atribuído',
                        valor_rota DECIMAL(10, 2) DEFAULT 0.00,
                        tipo_filtro VARCHAR(100),
                        valor_filtro DECIMAL(10, 2) DEFAULT 0.00,
                        ultima_troca DATE,
                        proxima_troca DATE,
                        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
                logger.info("✅ Tabela clientes_new criada")
                
                # 2. Copiar dados da tabela antiga (zerando valor_rota)
                conn.execute(text("""
                    INSERT INTO clientes_new 
                        (id, nome, status, piscineiro, valor_rota, tipo_filtro, valor_filtro, 
                         ultima_troca, proxima_troca, criado_em, atualizado_em)
                    SELECT 
                        id, nome, status, piscineiro, 0.00, NULL, 0.00,
                        ultima_troca, proxima_troca, criado_em, atualizado_em
                    FROM clientes
                """))
                conn.commit()
                logger.info("✅ Dados copiados (valor_rota zerado)")
                
                # 3. Dropar tabela antiga
                conn.execute(text("DROP TABLE clientes"))
                conn.commit()
                logger.info("✅ Tabela antiga removida")
                
                # 4. Renomear nova tabela
                conn.execute(text("ALTER TABLE clientes_new RENAME TO clientes"))
                conn.commit()
                logger.info("✅ Tabela renomeada")
                
                # 5. Recriar índices
                conn.execute(text("CREATE INDEX idx_clientes_nome ON clientes(nome)"))
                conn.execute(text("CREATE INDEX idx_clientes_status ON clientes(status)"))
                conn.execute(text("CREATE INDEX idx_clientes_piscineiro ON clientes(piscineiro)"))
                conn.execute(text("CREATE INDEX idx_clientes_proxima_troca ON clientes(proxima_troca)"))
                conn.execute(text("CREATE INDEX idx_status_piscineiro ON clientes(status, piscineiro)"))
                conn.execute(text("CREATE INDEX idx_proxima_troca_status ON clientes(proxima_troca, status)"))
                conn.commit()
                logger.info("✅ Índices recriados")
                
            else:
                # PostgreSQL/MySQL - suportam ALTER TABLE diretamente
                logger.info("🐘 Banco PostgreSQL/MySQL detectado")
                
                # Adicionar novas colunas
                try:
                    conn.execute(text("ALTER TABLE clientes ADD COLUMN tipo_filtro VARCHAR(100)"))
                    conn.commit()
                    logger.info("✅ Coluna tipo_filtro adicionada")
                except Exception as e:
                    logger.warning(f"⚠️ tipo_filtro já existe ou erro: {e}")
                    conn.rollback()
                
                try:
                    conn.execute(text("ALTER TABLE clientes ADD COLUMN valor_filtro DECIMAL(10, 2) DEFAULT 0.00"))
                    conn.commit()
                    logger.info("✅ Coluna valor_filtro adicionada")
                except Exception as e:
                    logger.warning(f"⚠️ valor_filtro já existe ou erro: {e}")
                    conn.rollback()
                
                # Zerar valor_rota
                conn.execute(text("UPDATE clientes SET valor_rota = 0.00"))
                conn.commit()
                logger.info("✅ Coluna valor_rota zerada")
                
                # Remover colunas antigas
                try:
                    conn.execute(text("ALTER TABLE clientes DROP COLUMN metodo_cobranca"))
                    conn.commit()
                    logger.info("✅ Coluna metodo_cobranca removida")
                except Exception as e:
                    logger.warning(f"⚠️ metodo_cobranca já removida ou erro: {e}")
                    conn.rollback()
                
                try:
                    conn.execute(text("ALTER TABLE clientes DROP COLUMN auto_pay"))
                    conn.commit()
                    logger.info("✅ Coluna auto_pay removida")
                except Exception as e:
                    logger.warning(f"⚠️ auto_pay já removida ou erro: {e}")
                    conn.rollback()
            
            # Verificar resultado
            result = conn.execute(text("SELECT COUNT(*) FROM clientes"))
            total = result.scalar()
            
            logger.info("\n" + "="*60)
            logger.info(f"✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            logger.info(f"📊 Total de clientes: {total}")
            logger.info("="*60 + "\n")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro na migração: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("🔄 MIGRAÇÃO DE SCHEMA - L'Acqua Azzurra")
    print("="*60)
    print("\n📝 Alterações:")
    print("  ✓ Adicionar: tipo_filtro (VARCHAR 100)")
    print("  ✓ Adicionar: valor_filtro (DECIMAL 10,2)")
    print("  ✓ Remover: metodo_cobranca")
    print("  ✓ Remover: auto_pay")
    print("  ✓ Zerar: valor_rota\n")
    
    # Aceitar -y como argumento para auto-confirmar
    if "-y" in sys.argv or "--yes" in sys.argv:
        resposta = 's'
    else:
        resposta = input("⚠️  Deseja continuar? (s/n): ").strip().lower()
    
    if resposta == 's':
        sucesso = migrate_schema()
        
        if sucesso:
            print("\n✅ Migração concluída! O banco está atualizado.")
            print("💡 Lembre-se de atualizar o código do app.py para usar os novos campos.\n")
        else:
            print("\n❌ Migração falhou. Verifique os logs acima.\n")
    else:
        print("\n⏸️  Migração cancelada.\n")
