import psycopg2

print("\n" + "-"*50)
print("TESTE CONEXAO POSTGRESQL - CODIGO ASCII PURO")
print("-"*50)

print("\nTentando conectar ao PostgreSQL...")
print("Host: localhost")
print("Database: DataBridge")
print("User: postgres")
print("Password: 640064")
print("Port: 5432")

try:
    # Conexao simples
    conn = psycopg2.connect(
        host="localhost",
        database="DataBridge", 
        user="postgres",
        password="640064"
    )
    
    print("\nSUCESSO! Conectado ao PostgreSQL.")
    
    # Consulta simples
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"Versao PostgreSQL: {version[0]}")
    
    # Fechar conexao
    cursor.close()
    conn.close()
    print("Conexao fechada.")
    
except Exception as e:
    print(f"\nERRO: {str(e)}")
    print("\nVerifique:")
    print("1. PostgreSQL esta rodando?")
    print("2. Banco 'DataBridge' existe?")
    print("3. Usuario/senha corretos?")
    print("4. Porta 5432 acessivel?")

print("\n" + "-"*50)
input("Pressione ENTER para sair...")