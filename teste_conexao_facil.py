import psycopg2
import time

# Exibir mensagem de boas-vindas
print("\n" + "="*50)
print("TESTE SIMPLES DE CONEXAO COM POSTGRESQL")
print("Data-Bridge-Bank")
print("="*50 + "\n")

print("Tentando conectar ao PostgreSQL...")
print("Database: DataBridge")
print("Usuario: postgres")
print("Senha: 640064\n")

# Pausa para visualizar as mensagens
time.sleep(1)

try:
    # Conectar ao PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        database="DataBridge",
        user="postgres",
        password="640064"
    )
    
    print("CONEXAO BEM-SUCEDIDA!\n")
    time.sleep(1)
    
    # Criar um cursor
    cursor = conn.cursor()
    
    # PASSO 1: Verificar a versao do PostgreSQL
    print("PASSO 1: Verificando versao do PostgreSQL...")
    cursor.execute("SELECT version();")
    versao = cursor.fetchone()[0]
    print(f"Versao: {versao}\n")
    time.sleep(1)
    
    # PASSO 2: Criar tabela de teste
    print("PASSO 2: Criando tabela de teste...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes_teste (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100),
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    print("Tabela 'clientes_teste' criada com sucesso!\n")
    time.sleep(1)
    
    # PASSO 3: Inserir um registro
    print("PASSO 3: Inserindo cliente de teste...")
    cursor.execute("""
    INSERT INTO clientes_teste (nome, email) 
    VALUES ('Cliente Teste', 'teste@databridge.com')
    RETURNING id;
    """)
    id_inserido = cursor.fetchone()[0]
    conn.commit()
    print(f"Cliente inserido com ID: {id_inserido}\n")
    time.sleep(1)
    
    # PASSO 4: Recuperar registros
    print("PASSO 4: Recuperando clientes da tabela...")
    cursor.execute("SELECT id, nome, email, data_cadastro FROM clientes_teste;")
    clientes = cursor.fetchall()
    
    print("\nLista de Clientes:")
    print("-" * 70)
    print(f"{'ID':<5} | {'NOME':<20} | {'EMAIL':<25} | {'DATA CADASTRO'}")
    print("-" * 70)
    
    for cliente in clientes:
        print(f"{cliente[0]:<5} | {cliente[1]:<20} | {cliente[2]:<25} | {cliente[3]}")
    
    print("-" * 70)
    print(f"Total de clientes: {len(clientes)}\n")
    
    # Fechar cursor e conexao
    cursor.close()
    conn.close()
    
    print("="*50)
    print("TESTE CONCLUIDO COM SUCESSO!")
    print("Sua conexao com o PostgreSQL esta funcionando corretamente.")
    print("="*50)
    
except Exception as e:
    print(f"ERRO: {e}")
    print("\nVerifique:")
    print("1. O PostgreSQL esta instalado e rodando?")
    print("2. O banco 'DataBridge' foi criado?")
    print("3. A senha '640064' esta correta?")
    print("4. A porta do PostgreSQL (5432) esta acessivel?")
    
    print("\nPara criar o banco 'DataBridge' no pgAdmin:")
    print("1. Abra o pgAdmin")
    print("2. Digite a senha do pgAdmin (640064)")
    print("3. Expanda 'Servers' e conecte ao PostgreSQL")
    print("4. Clique com botao direito em 'Databases'")
    print("5. Selecione 'Create' > 'Database...'")
    print("6. Digite 'DataBridge' e clique em 'Save'")

# Manter janela aberta
input("\nPressione ENTER para sair...")