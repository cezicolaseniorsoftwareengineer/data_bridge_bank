"""
Script para criar o banco de dados 'databridge' no PostgreSQL AWS RDS
"""
import os
import sys
import psycopg2
from cloud_config import POSTGRES_CLOUD

def criar_banco_databridge():
    print("Conectando ao banco de dados PostgreSQL padrão na AWS...")

    try:
        conn = psycopg2.connect(
            host=POSTGRES_CLOUD["host"],
            user=POSTGRES_CLOUD["user"],
            password=POSTGRES_CLOUD["password"],
            database="postgres"
        )
        conn.autocommit = True
        print("✓ Conectado ao banco padrão 'postgres'")
    except Exception as e:
        print(f"✗ Erro ao conectar ao banco padrão: {e}")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'databridge'")
    banco_existe = cursor.fetchone()

    if not banco_existe:
        print("Criando banco de dados 'databridge'...")
        try:
            cursor.execute("CREATE DATABASE databridge")
            print("✓ Banco de dados 'databridge' criado com sucesso!")
        except Exception as e:
            print(f"✗ Erro ao criar banco de dados: {e}")
    else:
        print("✓ Banco de dados 'databridge' já existe")

    cursor.close()
    conn.close()
    print("Conexão fechada")

if __name__ == "__main__":
    criar_banco_databridge()