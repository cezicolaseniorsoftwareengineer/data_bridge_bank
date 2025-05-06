"""
Script especializado para iniciar o DataBridge conectado ao PostgreSQL na AWS
"""
import os
import sys
import asyncio
import time
import subprocess
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("databridge-aws")

# Diretórios e caminhos
BASE_DIR = Path(__file__).parent
DATABRIDGE_DIR = BASE_DIR / "databridge"
APP_DIR = DATABRIDGE_DIR / "app"

def print_banner():
    """Exibe um banner informativo sobre a aplicação"""
    banner = """
    ========================================================
        DATABRIDGE BANK - CONEXÃO AWS PostgreSQL
    ========================================================
        🔐 Banco de dados: PostgreSQL (AWS RDS)
        🌐 Região: us-east-2b
        🔧 Host: databridge.c9iuaaiqs1xc.us-east-2.rds.amazonaws.com
    ========================================================
    """
    print(banner)

async def setup_database():
    """Inicializa o banco de dados na AWS"""
    logger.info("Inicializando banco de dados PostgreSQL na AWS...")
    try:
        # Definir variáveis de ambiente para conexão AWS
        os.environ["POSTGRES_SERVER"] = "databridge.c9iuaaiqs1xc.us-east-2.rds.amazonaws.com"
        os.environ["POSTGRES_USER"] = "postgres"
        os.environ["POSTGRES_PASSWORD"] = "data640064"
        os.environ["POSTGRES_DB"] = "databridge"
        os.environ["ENVIRONMENT"] = "production"
        
        # Importar e executar a criação do banco
        sys.path.insert(0, str(DATABRIDGE_DIR))
        from app.models.database import create_db_and_tables
        await create_db_and_tables()
        logger.info("✅ Banco de dados PostgreSQL AWS inicializado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco de dados: {str(e)}")
        return False

def start_api_server():
    """Inicia o servidor da API"""
    logger.info("Iniciando servidor DataBridge API conectado ao PostgreSQL AWS...")
    try:
        # Navegar para o diretório da aplicação
        os.chdir(DATABRIDGE_DIR)
        
        # Iniciar o servidor uvicorn
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar inicialização do servidor
        time.sleep(2)
        
        if process.poll() is None:  # Se o processo ainda estiver rodando
            logger.info("✅ Servidor DataBridge API iniciado com sucesso!")
            logger.info("🌐 API disponível em: http://localhost:8000")
            logger.info("📚 Documentação Swagger: http://localhost:8000/api/docs")
            logger.info("🔍 Verificação de saúde: http://localhost:8000/api/health")
            
            # Executar o processo em primeiro plano
            while True:
                output = process.stdout.readline()
                if output:
                    print(output.strip())
                
                error = process.stderr.readline()
                if error:
                    print(f"ERRO: {error.strip()}")
                
                if process.poll() is not None:
                    break
                
                time.sleep(0.1)
                
            return True
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ Erro ao iniciar servidor: {stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {str(e)}")
        return False

async def main():
    """Função principal para iniciar a aplicação"""
    print_banner()
    
    # Inicializar banco de dados
    db_success = await setup_database()
    if not db_success:
        logger.warning("⚠️ Continuando mesmo com problemas no banco de dados...")
    
    # Iniciar servidor API
    start_api_server()

if __name__ == "__main__":
    asyncio.run(main())