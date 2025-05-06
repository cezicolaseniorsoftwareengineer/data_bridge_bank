import psycopg2
import time

print("\n" + "="*60)
print(" "*15 + "TESTE DE CONEXÃO POSTGRESQL" + " "*15)
print("="*60)

print("\nTestando conexão com PostgreSQL...")
print("Host: localhost")
print("Banco: DataBridge")
print("Usuário: postgres")
print("Senha: 640064")
print("Porta: 5432 (padrão)")

time.sleep(1)  # Pequena pausa para visualizar as mensagens

try:
    # Tentar conexão simples
    conn = psycopg2.connect(
        host="localhost",
        database="DataBridge", 
        user="postgres",
        password="640064",
        # A porta padrão 5432 será usada automaticamente
    )
    
    print("\n✅ CONEXÃO BEM SUCEDIDA!")
    print("Foi possível conectar ao PostgreSQL com as credenciais fornecidas.")
    
    # Testar a execução de uma consulta simples
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"\nVersão do PostgreSQL: {version[0]}")
    
    cursor.close()
    conn.close()
    print("\nConexão fechada com sucesso.")
    
except Exception as e:
    print(f"\n❌ ERRO DE CONEXÃO: {e}")
    print("\nVerifique se:")
    print("1. O serviço do PostgreSQL está em execução")
    print("   - No Windows, verifique os Serviços (services.msc)")
    print("   - Procure por 'postgresql' ou 'postgres'")
    print("2. O banco de dados 'DataBridge' realmente existe")
    print("   - Abra o pgAdmin, conecte ao servidor, e verifique se 'DataBridge' aparece na lista de bancos")
    print("3. O usuário 'postgres' existe e a senha '640064' está correta")
    print("4. O PostgreSQL está aceitando conexões no localhost:5432")
    print("   - Verifique o arquivo pg_hba.conf para regras de autenticação")
    print("   - Verifique se não há firewall bloqueando a porta 5432")

print("\n" + "="*60)
input("Pressione ENTER para sair...")