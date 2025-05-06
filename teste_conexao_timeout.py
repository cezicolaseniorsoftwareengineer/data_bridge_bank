"""
Script direto para testar conexão PostgreSQL com timeout estendido
"""
import psycopg2
import sys
import time

# Configuração da conexão
host = "databridge.c9iuaaiqs1xc.us-east-2.rds.amazonaws.com"
user = "postgres"
password = "data640064"
database = "postgres"
timeout = 30  # timeout aumentado para 30 segundos

print(f"\nTestando conexão PostgreSQL na AWS...")
print(f"Host: {host}")
print(f"Banco: {database}")
print(f"Timeout: {timeout} segundos")
print("Aguarde...")

try:
    start_time = time.time()
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        connect_timeout=timeout
    )
    
    end_time = time.time()
    print(f"\n✓ CONEXÃO BEM-SUCEDIDA em {end_time - start_time:.2f} segundos!")
    
    # Informações básicas da conexão
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✓ Versão do PostgreSQL: {version}")
    
    # Informações sobre bancos existentes
    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    databases = cursor.fetchall()
    print(f"\n✓ Bancos disponíveis no servidor:")
    for db in databases:
        print(f"  - {db[0]}")
    
    cursor.close()
    conn.close()
    print("\nA conexão está funcionando corretamente.")
    
except Exception as e:
    end_time = time.time()
    print(f"\n✗ FALHA NA CONEXÃO após {end_time - start_time:.2f} segundos")
    print(f"✗ Erro: {e}")
    print("\nVerifique:")
    print("1. O status da instância RDS no console AWS (deve estar 'Available')")
    print("2. As configurações de grupo de segurança (deve permitir seu IP na porta 5432)")
    print("3. Configurações de rede da AWS (ACLs, sub-redes, etc)")
    print("4. Sua conexão com a internet")
    sys.exit(1)

print("\nImportante: Se a conexão funcionou, você pode continuar com:")
print("1. Criação do banco databridge: python criar_banco_databridge.py")
print("2. Testes da aplicação com o banco na nuvem: python iniciar_databridge_completo.py")