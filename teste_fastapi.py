"""
Script simples para testar a inicialização da aplicação FastAPI com modo de depuração
"""
import logging

# Configurar logging para mostrar informações detalhadas
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

import uvicorn
from fastapi import FastAPI

# Criar uma aplicação FastAPI mínima
app = FastAPI(title="Teste de API")

@app.get("/")
async def root():
    return {"message": "API de teste funcionando!"}

@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "message": "Servidor funcionando corretamente"}

# Executar a aplicação com modo de depuração
if __name__ == "__main__":
    print("\nIniciando servidor FastAPI simples na porta 8000...")
    print("Acesse http://localhost:8000 ou http://127.0.0.1:8000\n")
    
    try:
        uvicorn.run(
            "teste_fastapi:app", 
            host="0.0.0.0",  # Binds em todos os endereços
            port=8000,
            log_level="debug"
        )
    except Exception as e:
        print(f"\nERRO ao iniciar o servidor: {e}")
        print("\nTente com o endereço localhost:")
        
        try:
            uvicorn.run(
                "teste_fastapi:app", 
                host="localhost",  # Tenta apenas com localhost
                port=8000,
                log_level="debug"
            )
        except Exception as e2:
            print(f"\nERRO ao iniciar com localhost: {e2}")
            print("\nTente com o endereço 127.0.0.1:")
            
            try:
                uvicorn.run(
                    "teste_fastapi:app", 
                    host="127.0.0.1",  # Tenta com IP de loopback
                    port=8000,
                    log_level="debug"
                )
            except Exception as e3:
                print(f"\nERRO ao iniciar com 127.0.0.1: {e3}")
                print("\nPor favor, verifique sua configuração de rede e firewall.")