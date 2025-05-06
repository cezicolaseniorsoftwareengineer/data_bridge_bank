"""
Script para testar a conexão com PostgreSQL em nuvem (AWS RDS)
Execute este script para verificar se a conexão está funcionando corretamente.
"""
import psycopg2
import sys
from cloud_config import POSTGRES_CLOUD

# Use a configuração do arquivo cloud_config.py
CLOUD_PG_URI = POSTGRES_CLOUD["uri"]

def testar_conexao_cloud():
    print("Testando conexão com PostgreSQL em nuvem (AWS RDS)...")
    try:
        # Conectar ao banco em nuvem
        conn = psycopg2.connect(CLOUD_PG_URI)
        
        # Executar uma consulta simples
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        # Fechar conexão
        cursor.close()
        conn.close()
        
        print("✓ Conexão bem-sucedida!")
        print(f"Versão do PostgreSQL: {version[0]}")
        return True
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        return False

def criar_tabelas_basicas():
    """Cria as tabelas básicas necessárias no banco em nuvem"""
    if not testar_conexao_cloud():
        return False
    
    print("\nCriando tabelas básicas no AWS RDS...")
    try:
        conn = psycopg2.connect(CLOUD_PG_URI)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Criar tabela de uploads
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_uploads (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            file_type VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP NULL,
            error_message TEXT NULL
        );
        """)
        
        # Criar tabela de registros
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_records (
            id SERIAL PRIMARY KEY,
            file_id INTEGER REFERENCES file_uploads(id),
            record_type VARCHAR(50) NOT NULL,
            content JSONB NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Criar tabela de clientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Criar alguns dados de exemplo
        cursor.execute("""
        INSERT INTO clients (name, status)
        VALUES 
            ('Banco Nacional', 'active'),
            ('Seguros Confiança', 'active'),
            ('Investimentos Futuro', 'inactive')
        ON CONFLICT DO NOTHING;
        """)
        
        cursor.execute("""
        INSERT INTO file_uploads (filename, file_type, status)
        VALUES 
            ('exemplo1.csv', 'csv', 'processed'),
            ('exemplo2.json', 'json', 'processed'),
            ('dados.xml', 'xml', 'failed')
        ON CONFLICT DO NOTHING;
        """)
        
        cursor.close()
        conn.close()
        print("✓ Tabelas criadas com sucesso!")
        return True
    except Exception as e:
        print(f"✗ Erro ao criar tabelas: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-tables":
        criar_tabelas_basicas()
    else:
        testar_conexao_cloud()
        print("\nPara criar as tabelas básicas, execute:")
        print("python testar_pg_cloud.py --create-tables")