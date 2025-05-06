"""
Lista todos os bancos de dados PostgreSQL existentes no servidor.
"""
import psycopg2

# Configurações de conexão
DB_HOST = "localhost"
DB_USER = "postgres"  # Usuário padrão do PostgreSQL
DB_PASSWORD = "640064"  # Senha fornecida pelo usuário
DB_PORT = 5432  # Porta padrão do PostgreSQL

def list_databases():
    """Lista todos os bancos de dados no servidor PostgreSQL."""
    print("\n===== Lista de Bancos de Dados PostgreSQL =====")
    
    try:
        # Conectar ao PostgreSQL (usando o banco postgres padrão)
        conn = psycopg2.connect(
            host=DB_HOST,
            database="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        conn.set_session(autocommit=True)
        
        # Criar um cursor para executar consultas
        cursor = conn.cursor()
        
        # Consultar lista de todos os bancos de dados
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
        databases = cursor.fetchall()
        
        # Mostrar resultados
        print("\nBancos de dados existentes:")
        print("-" * 40)
        for db in databases:
            if db[0] == "DataBridge":
                print(f"* {db[0]} (ENCONTRADO!)")
            else:
                print(f"  {db[0]}")
        print("-" * 40)
        
        # Verificar especificamente o banco DataBridge
        cursor.execute("SELECT count(*) FROM pg_database WHERE datname = 'DataBridge';")
        exists = cursor.fetchone()[0]
        if exists:
            print("\n✓ O banco de dados 'DataBridge' EXISTE no servidor.")
            
            # Tentar se conectar ao banco DataBridge para verificar permissões
            try:
                test_conn = psycopg2.connect(
                    host=DB_HOST,
                    database="DataBridge",
                    user=DB_USER,
                    password=DB_PASSWORD,
                    port=DB_PORT
                )
                print("✓ Você TEM permissões para acessar o banco de dados 'DataBridge'.")
                test_conn.close()
            except Exception as e:
                print(f"✗ Você NÃO TEM permissões para acessar o banco 'DataBridge'. Erro: {e}")
        else:
            print("\n✗ O banco de dados 'DataBridge' NÃO existe no servidor.")
        
        # Fechar conexão
        cursor.close()
        conn.close()
        print("\nVerificação concluída.")
        
    except Exception as e:
        print(f"\nErro ao conectar ou consultar o PostgreSQL: {e}")

if __name__ == "__main__":
    # Verificar se psycopg2 está instalado
    try:
        import psycopg2
    except ImportError:
        print("O módulo psycopg2 não está instalado. Instalando...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        print("psycopg2-binary instalado com sucesso!")
    
    # Listar os bancos de dados
    list_databases()