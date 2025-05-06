"""
Teste de conexão com o banco de dados PostgreSQL 'DataBridge'.
Este script verifica se a conexão com o banco PostgreSQL pode ser estabelecida
usando as credenciais fornecidas.
"""
import psycopg2
import sys

# Configurações de conexão
DB_HOST = "localhost"
DB_NAME = "DataBridge"
DB_USER = "postgres"  # Usuário padrão do PostgreSQL
DB_PASSWORD = "640064"  # Senha fornecida pelo usuário
DB_PORT = 5432  # Porta padrão do PostgreSQL

def test_postgresql_connection():
    """Testa a conexão com o banco de dados PostgreSQL."""
    print(f"\n{'='*60}")
    print(f"Testando conexão com o banco de dados PostgreSQL 'DataBridge'")
    print(f"{'='*60}")
    
    try:
        # Tentar estabelecer a conexão
        print(f"Conectando ao PostgreSQL em {DB_HOST}:{DB_PORT}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        
        # Criar um cursor para executar operações no banco de dados
        cursor = conn.cursor()
        
        # Obter informações da versão do PostgreSQL
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"Versão do PostgreSQL: {db_version[0]}")
        
        # Listar as tabelas do banco de dados
        print("\nTabelas disponíveis no banco de dados:")
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        if tables:
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("Não foram encontradas tabelas no esquema 'public'.")
        
        # Fechar a conexão com o banco de dados
        cursor.close()
        conn.close()
        print("\nA conexão com o PostgreSQL foi estabelecida com sucesso!")
        return True
    
    except Exception as e:
        print(f"\nErro ao conectar ao PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    # Tentar importar psycopg2
    try:
        import psycopg2
    except ImportError:
        print("O módulo psycopg2 não está instalado. Instalando...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        print("psycopg2-binary instalado com sucesso!")
    
    # Executar o teste de conexão
    success = test_postgresql_connection()
    
    # Sair com código de status apropriado
    sys.exit(0 if success else 1)