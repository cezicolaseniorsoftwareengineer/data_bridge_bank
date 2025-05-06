"""
Configurações para bancos de dados em nuvem
Este arquivo centraliza as configurações de conexão para os bancos na nuvem
"""

# PostgreSQL na nuvem (AWS RDS)
POSTGRES_CLOUD = {
    "uri": "postgres://postgres:data640064@databridge.c9iuaaiqs1xc.us-east-2.rds.amazonaws.com/databridge",
    "user": "postgres",  # Usuário principal configurado na AWS
    "password": "data640064",  # Senha atualizada do RDS
    "host": "databridge.c9iuaaiqs1xc.us-east-2.rds.amazonaws.com",  # Endpoint RDS
    "database": "databridge"  # Banco de dados específico para a aplicação
}

# MongoDB na nuvem (MongoDB Atlas ou DocumentDB)
MONGODB_CLOUD = {
    "uri": "mongodb+srv://usuario:senha@cluster.mongodb.net/databridge",
    "database": "databridge"
}

# Configuração para Apache Kafka (se necessário)
KAFKA_CLOUD = {
    "bootstrap_servers": "seu-kafka-cluster:9092",
    "username": "username",
    "password": "password",
    "use_ssl": True
}

# Variáveis de ambiente para Vercel/Netlify/AWS
def get_cloud_env_vars():
    """Retorna as variáveis de ambiente para configurar na nuvem"""
    return {
        "POSTGRES_SERVER": POSTGRES_CLOUD["host"],
        "POSTGRES_USER": POSTGRES_CLOUD["user"],
        "POSTGRES_PASSWORD": POSTGRES_CLOUD["password"],
        "POSTGRES_DB": POSTGRES_CLOUD["database"],
        "MONGODB_URI": MONGODB_CLOUD["uri"],
        "MONGODB_DB": MONGODB_CLOUD["database"],
        "SECRET_KEY": "sua_chave_secreta_para_jwt",
        "ENVIRONMENT": "production"
    }

def imprimir_instrucoes_deploy():
    """Imprime instruções para configurar o deploy"""
    print("\n=== CONFIGURAÇÕES PARA DEPLOY ===\n")
    
    print("1. VARIÁVEIS DE AMBIENTE PARA AWS:")
    for key, value in get_cloud_env_vars().items():
        masked_value = value
        if "PASSWORD" in key or "KEY" in key:
            masked_value = "****" 
        print(f"   {key}: {masked_value}")
    
    print("\n2. INSTRUÇÕES PARA TESTAR CONEXÃO COM RDS:")
    print("   Execute: python testar_pg_cloud.py")
    print("   Para criar as tabelas básicas: python testar_pg_cloud.py --create-tables")
    
    print("\n3. INSTRUÇÕES PARA INICIAR APLICAÇÃO COM RDS:")
    print("   Defina a variável de ambiente DATABRIDGE_DB_MODE=postgres")
    print("   Execute: python iniciar_databridge_completo.py")

if __name__ == "__main__":
    imprimir_instrucoes_deploy()
    print("\nIMPORTANTE: Este arquivo contém informações sensíveis.")
    print("Não o compartilhe ou comite em repositórios públicos!")