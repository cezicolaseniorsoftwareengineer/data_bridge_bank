import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

print("Verificando conexão com PostgreSQL e criando banco de dados DataBridge se necessário...")

# Conexão com o banco de dados padrão "postgres"
try:
    # Primeiro, tentar se conectar ao banco padrão postgres
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="640064"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Verificar se o banco DataBridge já existe
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'DataBridge'")
    exists = cursor.fetchone()
    
    if not exists:
        print("Criando banco de dados 'DataBridge'...")
        cursor.execute("CREATE DATABASE \"DataBridge\"")
        print("Banco de dados 'DataBridge' criado com sucesso!")
    else:
        print("Banco de dados 'DataBridge' já existe.")
    
    # Fechar a conexão com o banco postgres
    cursor.close()
    conn.close()
    
    # Agora, testar a conexão com o banco DataBridge
    print("Testando conexão com o banco 'DataBridge'...")
    conn = psycopg2.connect(
        host="localhost",
        database="DataBridge",
        user="postgres",
        password="640064"
    )
    cursor = conn.cursor()
    
    # Executar uma consulta simples para testar
    cursor.execute("SELECT version()")
    version = cursor.fetchone()
    print(f"Conexão bem-sucedida! Versão do PostgreSQL: {version[0]}")
    
    # Fechar a conexão
    cursor.close()
    conn.close()
    
    print("\nSistema pronto para ser inicializado!")
    print("Execute os seguintes comandos para iniciar a aplicação:")
    print("1. cd databridge")
    print("2. python run_api_debug.py")
    
except Exception as e:
    print(f"\nERRO: {str(e)}")
    print("\nVerifique se:")
    print("1. O PostgreSQL está instalado e em execução")
    print("2. O usuário 'postgres' existe e a senha '640064' está correta")
    print("3. Você tem permissões para criar bancos de dados")
    
    print("\nPara instalar o PostgreSQL e criar o banco de dados:")
    print("1. Baixe e instale o PostgreSQL: https://www.postgresql.org/download/")
    print("2. Durante a instalação, defina a senha do usuário 'postgres' como '640064'")
    print("3. Após a instalação, abra o pgAdmin e crie um banco de dados chamado 'DataBridge'")