"""
Script para testar conexão com PostgreSQL na AWS RDS
Versão detalhada com diagnóstico de erros
"""
import psycopg2
import socket
import sys
import time

# Dados de conexão
HOST = "databridge.c9iuaaiqs1xc.us-east-2.rds.amazonaws.com"
USER = "dbadmin"  # Substitua pelo usuário correto
PASSWORD = "SuaSenhaAqui"  # Substitua pela senha correta
DATABASE = "databridge"
PORT = 5432

print(f"\n{'='*60}")
print(f"TESTE DE CONEXÃO COM AWS RDS")
print(f"{'='*60}")
print(f"Host: {HOST}")
print(f"Usuário: {USER}")
print(f"Banco: {DATABASE}")
print(f"Porta: {PORT}")

# Testar se o host responde a ping
print(f"\n1. Verificando conectividade básica com o host...")
try:
    # Testar conexão TCP direta
    start_time = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((HOST, PORT))
    end_time = time.time()
    
    if result == 0:
        print(f"   ✓ Host acessível na porta {PORT} (tempo: {end_time - start_time:.2f}s)")
    else:
        print(f"   ✗ Não foi possível conectar ao host na porta {PORT}")
        print(f"   Código de erro: {result}")
        print("\nPossíveis causas:")
        print("1. O Grupo de Segurança da instância RDS não permite conexões da sua rede")
        print("2. A instância RDS não está configurada como 'Publicly Accessible'")
        print("3. A instância RDS pode estar em manutenção ou inativa")
        print("4. Há um firewall local ou de rede bloqueando a conexão")
    sock.close()
except Exception as e:
    print(f"   ✗ Erro ao verificar conectividade: {e}")

# Tentar conexão PostgreSQL completa
print("\n2. Tentando conexão PostgreSQL...")
try:
    start_time = time.time()
    conn = psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        port=PORT
    )
    end_time = time.time()
    
    # Verificar versão do PostgreSQL
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    
    print(f"   ✓ Conexão PostgreSQL bem-sucedida (tempo: {end_time - start_time:.2f}s)")
    print(f"   ✓ Versão do PostgreSQL: {version}")
    
    # Verificar permissões
    cursor.execute("SELECT current_user;")
    user = cursor.fetchone()[0]
    print(f"   ✓ Conectado como usuário: {user}")
    
    # Verificar bancos existentes
    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
    databases = cursor.fetchall()
    print(f"   ✓ Bancos de dados disponíveis:")
    for db in databases:
        print(f"      - {db[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ✗ Erro ao conectar ao PostgreSQL: {e}")
    print("\nVerifique se:")
    print("1. O usuário e senha estão corretos")
    print("2. O banco de dados 'databridge' existe no servidor")
    print("3. O usuário tem permissões para acessar o banco de dados")
    print("4. As configurações de rede permitem a conexão")

print(f"\n{'='*60}")
print("Lembre-se de verificar no console AWS RDS:")
print("1. Se a instância está em estado 'Available'")
print("2. Se 'Publicly Accessible' está definido como 'Yes'")
print("3. Se o Security Group permite tráfego na porta 5432 do seu IP")