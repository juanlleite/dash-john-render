"""
Script de Backup Automático do PostgreSQL
Gera backups diários do banco de dados
"""
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
BACKUP_DIR = Path("backups")
RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', 30))


def create_backup():
    """Cria um backup do banco de dados PostgreSQL"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        logger.error("❌ DATABASE_URL não definida")
        return False
    
    # Verificar se é PostgreSQL
    if not database_url.startswith(('postgresql://', 'postgres://')):
        logger.warning("⚠️ Backup automático disponível apenas para PostgreSQL")
        return False
    
    # Criar diretório de backups
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # Nome do arquivo de backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f"backup_{timestamp}.sql"
    
    try:
        # Usar pg_dump para criar backup
        logger.info(f"📦 Criando backup: {backup_file}")
        
        # Comando pg_dump
        cmd = f"pg_dump {database_url} > {backup_file}"
        
        # Executar backup
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Verificar tamanho do arquivo
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            logger.info(f"✅ Backup criado com sucesso: {backup_file} ({size_mb:.2f} MB)")
            
            # Limpar backups antigos
            cleanup_old_backups()
            
            return True
        else:
            logger.error(f"❌ Erro ao criar backup: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar backup: {e}")
        return False


def cleanup_old_backups():
    """Remove backups mais antigos que RETENTION_DAYS"""
    try:
        cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
        deleted = 0
        
        for backup_file in BACKUP_DIR.glob("backup_*.sql"):
            # Obter timestamp do arquivo
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            if file_time < cutoff_date:
                backup_file.unlink()
                deleted += 1
                logger.info(f"🗑️ Backup antigo removido: {backup_file.name}")
        
        if deleted > 0:
            logger.info(f"✅ {deleted} backup(s) antigo(s) removido(s)")
        
    except Exception as e:
        logger.error(f"❌ Erro ao limpar backups antigos: {e}")


def list_backups():
    """Lista todos os backups disponíveis"""
    if not BACKUP_DIR.exists():
        logger.info("📂 Nenhum backup encontrado")
        return []
    
    backups = sorted(BACKUP_DIR.glob("backup_*.sql"), reverse=True)
    
    logger.info(f"\n📦 Backups disponíveis ({len(backups)}):")
    for backup in backups:
        size_mb = backup.stat().st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        logger.info(f"   • {backup.name} ({size_mb:.2f} MB) - {mtime.strftime('%d/%m/%Y %H:%M')}")
    
    return backups


def restore_backup(backup_file):
    """
    Restaura um backup do banco de dados
    
    Args:
        backup_file: Path do arquivo de backup
    """
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        logger.error("❌ DATABASE_URL não definida")
        return False
    
    if not backup_file.exists():
        logger.error(f"❌ Arquivo de backup não encontrado: {backup_file}")
        return False
    
    try:
        logger.warning(f"⚠️ ATENÇÃO: Restaurando backup {backup_file.name}")
        logger.warning("⚠️ Isso irá SUBSTITUIR todos os dados atuais!")
        
        # Confirmar ação (comentar em produção)
        # response = input("Continuar? (digite 'SIM' para confirmar): ")
        # if response != 'SIM':
        #     logger.info("❌ Restauração cancelada")
        #     return False
        
        # Comando psql para restaurar
        cmd = f"psql {database_url} < {backup_file}"
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Backup restaurado com sucesso: {backup_file}")
            return True
        else:
            logger.error(f"❌ Erro ao restaurar backup: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao restaurar backup: {e}")
        return False


def main():
    """Executa backup e limpeza"""
    logger.info("\n" + "="*60)
    logger.info("🔄 BACKUP AUTOMÁTICO DO BANCO DE DADOS")
    logger.info("="*60 + "\n")
    
    # Verificar se backup está habilitado
    if os.getenv('BACKUP_ENABLED', 'True').lower() != 'true':
        logger.info("⚠️ Backup desabilitado (BACKUP_ENABLED=False)")
        return
    
    # Criar backup
    create_backup()
    
    # Listar backups
    list_backups()
    
    logger.info("\n✅ Processo de backup concluído\n")


if __name__ == '__main__':
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'list':
            list_backups()
        elif command == 'restore' and len(sys.argv) > 2:
            backup_path = Path(sys.argv[2])
            restore_backup(backup_path)
        else:
            print("Uso:")
            print("  python backup_db.py          - Criar backup")
            print("  python backup_db.py list     - Listar backups")
            print("  python backup_db.py restore <arquivo> - Restaurar backup")
    else:
        main()
