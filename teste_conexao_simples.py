import psycopg2
import time

print("\n" + "="*60)
print(" "*15 + "TESTE DE CONEXAO POSTGRESQL" + " "*15)
print("="*60)

print("\nTestando conexao com PostgreSQL...")
print("Host: localhost")
print("Banco: DataBridge")
print("Usuario: postgres")
print("Senha: 640064")
print("Porta: 5432 (padrao)")

time.sleep(1)  # Pequena pausa para visualizar as mensagens

try:
    # Tentar conexao simples
    conn = psycopg2.connect(
        host="localhost",
        database="DataBridge", 
        user="postgres",
        password="640064",
        # A porta padrao 5432 sera usada automaticamente
    )
    
    print("\n>>> CONEXAO BEM SUCEDIDA! <<<")
    print("Foi possivel conectar ao PostgreSQL com as credenciais fornecidas.")
    
    # Testar a execucao de uma consulta simples
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"\nVersao do PostgreSQL: {version[0]}")
    
    cursor.close()
    conn.close()
    print("\nConexao fechada com sucesso.")
    
except Exception as e:
    print(f"\n>>> ERRO DE CONEXAO: {e}")
    print("\nVerifique se:")
    print("1. O servico do PostgreSQL esta em execucao")
    print("   - No Windows, verifique os Servicos (services.msc)")
    print("   - Procure por 'postgresql' ou 'postgres'")
    print("2. O banco de dados 'DataBridge' realmente existe")
    print("   - Abra o pgAdmin, conecte ao servidor, e verifique se 'DataBridge' aparece na lista de bancos")
    print("3. O usuario 'postgres' existe e a senha '640064' esta correta")
    print("4. O PostgreSQL esta aceitando conexoes no localhost:5432")
    print("   - Verifique o arquivo pg_hba.conf para regras de autenticacao")
    print("   - Verifique se nao ha firewall bloqueando a porta 5432")

print("\n" + "="*60)
input("Pressione ENTER para sair...")