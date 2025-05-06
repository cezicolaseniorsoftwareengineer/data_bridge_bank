import os
import sys
import subprocess

print("=== DataBridge PostgreSQL Connection Tester ===")
print("Este script verifica a conexão com o PostgreSQL para o projeto DataBridge")
print("Data: 1 de maio de 2025")
print("===============================================")

# Verificar se temos psycopg2 instalado
try:
    import psycopg2
    print("✅ psycopg2 está instalado!")
except ImportError:
    print("❌ psycopg2 não está instalado. Instalando agora...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    print("✅ psycopg2 instalado com sucesso!")

print("\nTestando conexão com PostgreSQL...")
print("Parâmetros de conexão:")
print("- Host: localhost")
print("- Banco de dados: DataBridge")
print("- Usuário: postgres")
print("- Senha: 640064")

try:
    # Informações de conexão
    conn = psycopg2.connect(
        host="localhost",
        database="DataBridge",
        user="postgres",
        password="640064"
    )
    
    print("\n✅ CONEXÃO BEM-SUCEDIDA!")
    
    # Criar um cursor para executar operações SQL
    cursor = conn.cursor()
    
    # Executar consulta para testar a conexão
    cursor.execute("SELECT version();")
    
    # Recuperar o resultado
    versao_db = cursor.fetchone()
    print(f"✅ Versão do PostgreSQL: {versao_db[0]}")
    
    # Criar uma tabela simples para teste
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teste_conexao (
        id SERIAL PRIMARY KEY,
        mensagem TEXT NOT NULL,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Commit para salvar as alterações
    conn.commit()
    print("✅ Tabela 'teste_conexao' criada com sucesso!")
    
    # Inserir um registro na tabela
    cursor.execute(
        "INSERT INTO teste_conexao (mensagem) VALUES (%s) RETURNING id",
        ("Teste de conexão realizado com sucesso!",)
    )
    
    # Obter o ID do registro inserido
    id_inserido = cursor.fetchone()[0]
    conn.commit()
    
    print(f"✅ Registro inserido com ID: {id_inserido}")
    
    # Consultar todos os registros da tabela
    cursor.execute("SELECT COUNT(*) FROM teste_conexao")
    total_registros = cursor.fetchone()[0]
    print(f"✅ Total de registros na tabela: {total_registros}")
    
    print("\n===============================================")
    print("🎉 TESTE COMPLETO: A conexão com o PostgreSQL está funcionando corretamente!")
    print("Sua aplicação DataBridge está pronta para usar o PostgreSQL.")
    print("===============================================")
    
    # Fechar conexão
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERRO DE CONEXÃO: {e}")
    print("\nVerifique os seguintes pontos:")
    print("1. O PostgreSQL está instalado e em execução?")
    print("2. Existe um banco de dados chamado 'DataBridge'?")
    print("3. O usuário 'postgres' existe e a senha '640064' está correta?")
    print("4. O PostgreSQL está rodando na porta padrão (5432)?")
    
    # Orientações para criar o banco de dados
    print("\n🔍 Para criar o banco de dados 'DataBridge':")
    print("1. Abra o pgAdmin")
    print("2. Clique com o botão direito em 'Databases'")
    print("3. Selecione 'Create' > 'Database...'")
    print("4. Digite 'DataBridge' no campo 'Database' e clique em 'Save'")

input("\nPressione ENTER para sair...")