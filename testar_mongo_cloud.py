"""
Script para testar a conexão com MongoDB na nuvem (MongoDB Atlas)
Execute este script para verificar se a conexão está funcionando corretamente.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
import sys

# Substitua com a string de conexão do seu MongoDB Atlas
MONGO_URI = "mongodb+srv://usuario:senha@cluster.mongodb.net/databridge"

async def testar_conexao_async():
    """Testa a conexão assíncrona com MongoDB Atlas (como no código da aplicação)"""
    print("Testando conexão assíncrona com MongoDB Atlas...")
    try:
        # Conectar com Motor (cliente assíncrono)
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Obter informações do servidor para verificar conexão
        server_info = await client.admin.command("serverStatus")
        
        print("✓ Conexão assíncrona bem-sucedida!")
        print(f"MongoDB versão: {server_info.get('version', 'desconhecida')}")
        return True
    except Exception as e:
        print(f"✗ Erro na conexão assíncrona: {e}")
        return False

def testar_conexao_sync():
    """Testa a conexão síncrona com MongoDB Atlas (mais simples para diagnóstico)"""
    print("\nTestando conexão síncrona com MongoDB Atlas...")
    try:
        # Conectar com PyMongo (cliente síncrono)
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Ping para verificar conexão
        client.admin.command('ping')
        
        # Obter informações do servidor
        server_info = client.server_info()
        
        print("✓ Conexão síncrona bem-sucedida!")
        print(f"MongoDB versão: {server_info.get('version', 'desconhecida')}")
        return True
    except Exception as e:
        print(f"✗ Erro na conexão síncrona: {e}")
        return False

async def criar_colecoes():
    """Cria as coleções básicas no MongoDB Atlas"""
    if not await testar_conexao_async():
        return False
    
    print("\nCriando coleções no MongoDB...")
    try:
        # Conexão
        client = AsyncIOMotorClient(MONGO_URI)
        db = client.databridge
        
        # Criar coleções para logs e eventos
        await db.create_collection("logs")
        await db.create_collection("events")
        
        # Inserir um documento de exemplo em cada coleção
        await db.logs.insert_one({
            "level": "INFO",
            "message": "Sistema inicializado",
            "timestamp": pymongo.datetime.datetime.utcnow()
        })
        
        await db.events.insert_one({
            "type": "SYSTEM_START",
            "description": "Inicialização do sistema DataBridge",
            "timestamp": pymongo.datetime.datetime.utcnow()
        })
        
        # Verificar documentos
        log_count = await db.logs.count_documents({})
        event_count = await db.events.count_documents({})
        
        print(f"✓ Coleções criadas com sucesso!")
        print(f"  - Logs: {log_count} documento(s)")
        print(f"  - Events: {event_count} documento(s)")
        return True
    except Exception as e:
        print(f"✗ Erro ao criar coleções: {e}")
        return False

async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--create-collections":
        await criar_colecoes()
    else:
        await testar_conexao_async()
        testar_conexao_sync()
        print("\nPara criar as coleções básicas, execute:")
        print("python testar_mongo_cloud.py --create-collections")

if __name__ == "__main__":
    asyncio.run(main())