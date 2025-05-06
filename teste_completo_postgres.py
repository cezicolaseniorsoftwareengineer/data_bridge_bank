"""
Teste completo de conexão com PostgreSQL
Verifica se o serviço está rodando, testa a conexão e executa consultas básicas
"""
import os
import sys
import subprocess
import time
import socket
import psycopg2
from datetime import datetime
from pathlib import Path

def verificar_servico_postgres():
    """Verifica se o serviço do PostgreSQL está rodando no Windows"""
    print("\n=== VERIFICANDO SERVIÇO DO POSTGRESQL ===")
    
    # Nome do serviço PostgreSQL na sua máquina
    service_name = "postgresql-x64-17"
    
    try:
        stdout = subprocess.check_output(f"sc query {service_name}", shell=True, text=True)
        if "RUNNING" in stdout:
            print(f"✅ Serviço PostgreSQL ({service_name}) está ATIVO")
            return True
        else:
            print(f"❌ Serviço PostgreSQL ({service_name}) NÃO está ativo")
            print(f"Status atual: {stdout.strip() if stdout else 'Desconhecido'}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao verificar serviço PostgreSQL: {e}")
        
        # Tentar encontrar o serviço correto do PostgreSQL
        try:
            stdout = subprocess.check_output("sc query state= all | findstr /i postgres", shell=True, text=True)
            if stdout:
                print(f"📌 Serviços PostgreSQL encontrados:")
                print(stdout)
            else:
                print("❌ Nenhum serviço PostgreSQL encontrado no sistema")
        except subprocess.CalledProcessError:
            print("❌ Falha ao procurar serviços PostgreSQL")
        
        return False

def verificar_porta_postgres():
    """Verifica se a porta 5432 (PostgreSQL) está aberta"""
    print("\n=== VERIFICANDO PORTA DO POSTGRESQL ===")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            resultado = s.connect_ex(('localhost', 5432))
            if resultado == 0:
                print("✅ Porta 5432 está ABERTA - PostgreSQL está acessível")
                return True
            else:
                print("❌ Porta 5432 está FECHADA - PostgreSQL não está acessível")
                return False
    except Exception as e:
        print(f"❌ Erro ao verificar porta: {e}")
        return False

def testar_conexao_postgres():
    """Testa a conexão com o PostgreSQL"""
    print("\n=== TESTANDO CONEXÃO COM POSTGRESQL ===")
    
    try:
        # Tentar conexão com configurações padrão
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",  # Banco de dados padrão
            user="postgres",
            password="postgres"
        )
        
        # Verificar versão do PostgreSQL
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        versao = cursor.fetchone()[0]
        print(f"✅ Conexão com PostgreSQL estabelecida com sucesso!")
        print(f"📌 Versão do PostgreSQL: {versao}")
        
        # Verificar bancos de dados disponíveis
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        bancos = cursor.fetchall()
        print(f"\n📌 Bancos de dados disponíveis:")
        for banco in bancos:
            print(f"   - {banco[0]}")
        
        # Verificar se o banco 'databridge' existe
        databridge_existe = 'databridge' in [banco[0] for banco in bancos]
        if databridge_existe:
            print("✅ Banco de dados 'databridge' encontrado")
        else:
            print("❓ Banco de dados 'databridge' não encontrado")
        
        cursor.close()
        conn.close()
        return True, databridge_existe
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        return False, False

def testar_banco_databridge():
    """Testa o banco de dados databridge especificamente"""
    print("\n=== TESTANDO BANCO DE DADOS DATABRIDGE ===")
    
    try:
        # Conectar ao banco databridge
        conn = psycopg2.connect(
            host="localhost",
            database="databridge",
            user="postgres",
            password="postgres"
        )
        
        # Criar uma tabela de teste se não existir
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS teste_conexao (
            id SERIAL PRIMARY KEY,
            mensagem TEXT,
            data_teste TIMESTAMP
        )
        """)
        conn.commit()
        
        # Inserir um registro de teste
        cursor.execute(
            "INSERT INTO teste_conexao (mensagem, data_teste) VALUES (%s, %s) RETURNING id",
            (f"Teste realizado por {os.getlogin()}", datetime.now())
        )
        id_inserido = cursor.fetchone()[0]
        conn.commit()
        
        print(f"✅ Teste de escrita no banco 'databridge' realizado com sucesso (ID: {id_inserido})")
        
        # Ler o registro inserido
        cursor.execute("SELECT * FROM teste_conexao WHERE id = %s", (id_inserido,))
        registro = cursor.fetchone()
        print(f"✅ Teste de leitura no banco 'databridge' realizado com sucesso")
        print(f"📌 Registro lido: {registro}")
        
        # Verificar tabelas existentes
        cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        """)
        tabelas = cursor.fetchall()
        
        print(f"\n📌 Tabelas existentes no banco 'databridge':")
        if tabelas:
            for tabela in tabelas:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela[0]}")
                contagem = cursor.fetchone()[0]
                print(f"   - {tabela[0]} ({contagem} registros)")
        else:
            print("   Nenhuma tabela encontrada além da tabela de teste")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"❌ Erro ao testar banco 'databridge': {e}")
        return False

def criar_banco_databridge():
    """Cria o banco de dados databridge se não existir"""
    print("\n=== CRIANDO BANCO DE DADOS DATABRIDGE ===")
    
    try:
        # Conectar ao postgres (banco padrão)
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="postgres"
        )
        conn.autocommit = True  # Necessário para comandos como CREATE DATABASE
        
        # Verificar se o banco databridge já existe
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'databridge'")
        existe = cursor.fetchone()
        
        if not existe:
            print("📌 Criando banco de dados 'databridge'...")
            cursor.execute("CREATE DATABASE databridge")
            print("✅ Banco de dados 'databridge' criado com sucesso!")
        else:
            print("📌 Banco de dados 'databridge' já existe")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao criar banco 'databridge': {e}")
        return False

def iniciar_servico_postgres():
    """Tenta iniciar o serviço do PostgreSQL se estiver parado"""
    print("\n=== INICIANDO SERVIÇO DO POSTGRESQL ===")
    
    try:
        # Nome específico do serviço PostgreSQL na sua máquina
        service_name = "postgresql-x64-17"
        
        # Confirmar nome do serviço examinando os resultados da pesquisa anterior
        stdout = subprocess.check_output("sc query state= all | findstr /i postgres", shell=True, text=True)
        if stdout:
            for line in stdout.split("\n"):
                if "SERVICE_NAME" in line and "postgres" in line.lower():
                    found_name = line.split(":")[1].strip()
                    if found_name:
                        service_name = found_name
                        break
        
        print(f"📌 Tentando iniciar o serviço '{service_name}'...")
        
        # Tentar iniciar o serviço
        subprocess.check_call(f"sc start {service_name}", shell=True)
        
        # Aguardar um pouco
        print("📌 Aguardando o serviço iniciar (5 segundos)...")
        time.sleep(5)
        
        # Verificar se o serviço está rodando
        stdout = subprocess.check_output(f"sc query {service_name}", shell=True, text=True)
        if "RUNNING" in stdout:
            print(f"✅ Serviço '{service_name}' iniciado com sucesso!")
            return True
        else:
            print(f"❌ Não foi possível iniciar o serviço '{service_name}'")
            print(f"Status atual: {stdout}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar o serviço PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def gerar_relatorio_final(resultados):
    """Gera um relatório resumido dos testes realizados"""
    print("\n" + "="*60)
    print(" "*20 + "RELATÓRIO FINAL" + " "*20)
    print("="*60)
    
    # Contar resultados positivos
    testes_ok = sum(1 for resultado in resultados.values() if resultado is True)
    total_testes = len(resultados)
    
    # Resumo geral
    print(f"\n📊 Resumo: {testes_ok}/{total_testes} testes bem-sucedidos")
    
    # Status individual de cada teste
    for teste, resultado in resultados.items():
        status = "✅" if resultado else "❌"
        print(f"{status} {teste}")
    
    # Diagnóstico
    if resultados["servico_postgres"] is False:
        print("\n⚠️ DIAGNÓSTICO: O serviço PostgreSQL não está rodando")
        print("   Solução: Inicie o serviço manualmente através do painel de 'Serviços' do Windows")
        print("   ou execute o script 'iniciar_sistema_completo.py' como administrador")
    elif resultados["porta_postgres"] is False:
        print("\n⚠️ DIAGNÓSTICO: O serviço PostgreSQL está rodando mas a porta 5432 não está acessível")
        print("   Solução: Verifique se outro programa está usando a porta 5432")
        print("   ou verifique configurações de firewall")
    elif resultados["conexao_postgres"] is False:
        print("\n⚠️ DIAGNÓSTICO: A porta está aberta mas não foi possível conectar ao PostgreSQL")
        print("   Solução: Verifique as credenciais (usuário/senha) ou se o PostgreSQL")
        print("   está configurado para aceitar conexões TCP/IP (arquivo pg_hba.conf)")
    elif resultados["banco_databridge"] is False:
        print("\n⚠️ DIAGNÓSTICO: Conexão com PostgreSQL OK, mas o banco databridge tem problemas")
        print("   Solução: Verifique se o banco 'databridge' existe ou tente criá-lo novamente")
    else:
        print("\n✅ DIAGNÓSTICO: O banco de dados PostgreSQL está funcionando perfeitamente!")
        print("   Todos os testes foram concluídos com sucesso.")
    
    # Data e hora do teste
    print(f"\nTeste realizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*60)

def main():
    """Função principal que executa todos os testes"""
    print("\n" + "="*60)
    print(" "*15 + "TESTE DE BANCO DE DADOS POSTGRESQL" + " "*15)
    print("="*60)
    
    # Armazenar resultados dos testes
    resultados = {}
    
    # 1. Verificar se o serviço está rodando
    resultados["servico_postgres"] = verificar_servico_postgres()
    
    # 2. Se o serviço não estiver rodando, tentar iniciá-lo
    if not resultados["servico_postgres"]:
        resultados["servico_postgres"] = iniciar_servico_postgres()
    
    # 3. Verificar se a porta está aberta (apenas se o serviço estiver rodando)
    if resultados["servico_postgres"]:
        resultados["porta_postgres"] = verificar_porta_postgres()
    else:
        resultados["porta_postgres"] = False
    
    # 4. Testar conexão com PostgreSQL (apenas se a porta estiver aberta)
    if resultados["porta_postgres"]:
        conexao_ok, databridge_existe = testar_conexao_postgres()
        resultados["conexao_postgres"] = conexao_ok
    else:
        resultados["conexao_postgres"] = False
        databridge_existe = False
    
    # 5. Criar o banco databridge se não existir (apenas se a conexão estiver OK)
    if resultados["conexao_postgres"] and not databridge_existe:
        criar_banco_databridge()
    
    # 6. Testar banco databridge específico (apenas se a conexão com PostgreSQL estiver OK)
    if resultados["conexao_postgres"]:
        resultados["banco_databridge"] = testar_banco_databridge()
    else:
        resultados["banco_databridge"] = False
    
    # 7. Gerar relatório final
    gerar_relatorio_final(resultados)
    
    # Retornar código de saída com base no sucesso dos testes
    return 0 if all(resultados.values()) else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Teste interrompido pelo usuário")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Erro durante a execução dos testes: {e}")
        sys.exit(3)